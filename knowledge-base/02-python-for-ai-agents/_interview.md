# 02-python-for-ai-agents — interview fire round

### type-hints-basics

- **Q: Does Python enforce type hints at runtime?**
  A: No — CPython ignores them entirely at execution time. Enforcement comes from external tools: static type checkers (mypy, pyright) catch mismatches before running, and libraries like Pydantic add real runtime validation on top of the annotations.
- **Q: Why use `Literal["tool", "retrieval", "direct"]` instead of just `str` for a routing field?**
  A: `str` accepts any string — a hallucinated route like `"unknown"` would pass type-level scrutiny. `Literal` narrows the type to an exact enumerated set, so Pydantic can reject any value outside it at validation time, not downstream when the router tries to act on it.

### pydantic-basics

- **Q: Why not just use a plain dict and check keys manually with `if`/`get()`?**
  A: A dict never fails until code tries to use a missing/wrong-typed field, often far from where the bad data entered — the bug surfaces downstream and is harder to trace. A Pydantic model fails immediately at construction, with a specific error naming the field and reason, right at the boundary where untrusted data enters.
- **Q: What does `extra="forbid"` protect against that a bare type-checked model doesn't?**
  A: Without it, a model silently accepts and ignores any field it doesn't declare — an LLM hallucinating an extra key, or a subtly wrong key name, passes validation unnoticed. `extra="forbid"` turns an unexpected key into a `ValidationError` instead of silent data loss.
- **Q: Why does `min_length=1` alone not catch a placeholder answer like `"..."`?**
  A: `min_length` only checks the field isn't empty — `"..."` has length 3, so it passes. Catching content-level junk (placeholders, empty-but-nonzero-length strings) needs a `field_validator` that inspects the actual value, not just its length.

### decorators-and-wrappers

- **Q: Why does `retry_with_backoff` need three nested function levels instead of one?**
  A: The outer level exists only to accept the decorator's own arguments (`max_retries`, `base_delay`) — `@retry_with_backoff(max_retries=3)` calls `retry_with_backoff(3)` first, which must return the actual decorator function, which in turn returns the wrapper that runs at call time. A parameterless decorator only needs two levels.
- **Q: What breaks if you forget `@functools.wraps(fn)` inside a decorator?**
  A: `wrapper.__name__`, `__doc__`, and other metadata get replaced by the wrapper's own — every decorated function reports as `"wrapper"` under introspection. In this stack that's not cosmetic: FastMCP reads a tool function's name/docstring to build its JSON schema, so an unwrapped decorator on a tool function would silently break the exposed schema.
- **Q: Why is the tracing decorator's record-keeping inside a `finally` block, not just after the successful return?**
  A: A `finally` block runs whether the wrapped call succeeded or raised — a crashing agent still gets logged with `ok=False` instead of vanishing from the trace, which is exactly the failure case you most need visibility into.

### async-await-for-llm-apps

- **Q: What actually happens when you call an `async def` function without `await`ing it?**
  A: You get back a coroutine object, not a result — the function body hasn't run yet. Python usually warns about this ("coroutine was never awaited") but it doesn't raise an error, so the bug can go unnoticed until the missing result causes a failure somewhere downstream.
- **Q: Why does async help with LLM/MCP calls specifically, but not with a CPU-heavy loop?**
  A: Async concurrency works by yielding control at `await` points while waiting on I/O — an LLM API call or MCP subprocess call spends nearly all its time waiting on a response, so the event loop can usefully run other coroutines during that wait. A CPU-bound loop never hits an `await` point to yield at, so async buys it nothing; that needs real parallelism (multiprocessing), not concurrency.
- **Q: Why must an MCP client session stay within one asyncio Task rather than being cached and reused across calls from different Tasks?**
  A: `anyio`'s structured-concurrency `TaskGroup`s (which MCP's stdio transport is built on) are scoped to the Task they were created in — LangGraph runs each node in its own Task, so a session opened in one node's Task and reused in another breaks the TaskGroup's structured-concurrency guarantees (`labs/production-notes.md`, § "Concurrency / Idempotency").

## Harder / real-interview-style

Scenario-based questions on the specific patterns this stack leans on — type hints as a Pydantic prerequisite, decorators as the retry/circuit-breaker/tracing mechanism, and async for concurrent I/O-bound LLM/tool calls. Grounded in current (2025-2026) interview practice for Python/AI-agent roles ([Real Python — Pydantic AI](https://realpython.com/pydantic-ai/), [techinterview.org](https://www.techinterview.org/post/3233474450/python-interview-questions-2025-generators-decorators-async-await-type-hints-dataclasses-concurrency-gil-memory-management/), [DataCamp Python 2026](https://www.datacamp.com/blog/top-python-interview-questions-and-answers)) and this repo's own [[decorators-and-wrappers]], [[pydantic-basics]], [[async-await-for-llm-apps]].

#### Type hints and Pydantic in practice

- **Q: A tool function's parameter is typed `quantity: int`, but an LLM tool call sends `"quantity": "3"` (a string). What actually happens, and where's the failure point if you didn't expect it?**
  A: A bare Python type hint on a plain function does nothing at runtime — CPython never checks it, so `"3"` gets passed straight through and either silently works (if downstream code coincidentally coerces it) or blows up somewhere unrelated to the type mismatch's real cause. If the parameter is instead a Pydantic model field, Pydantic's validation will actually *coerce* `"3"` to `3` for a plain `int` field (lenient mode) — which is convenient but means a validated model doesn't guarantee the *type came in correct*, only that it was coercible; a `strict=True` field or a stricter type (e.g. `Annotated[int, Field(strict=True)]`) is what you want if a string quantity should be a hard failure, not a silent coercion.
- **Q: Why would a tool-calling agent's schema use `Literal["refund", "reship", "escalate"]` instead of an `Enum` for the same field, or vice versa — is there an actual difference that matters here?**
  A: Both restrict the value to an exact set and both validate the same way under Pydantic, but `Literal` values serialize to JSON Schema as a plain `enum` of raw values with less type machinery, while a Python `Enum` gives you a real class you can attach methods/docstrings to and reference programmatically (`Action.REFUND`) elsewhere in the codebase. For a tool schema whose only job is constraining an LLM's output to one of a few strings, `Literal` is usually the leaner choice; `Enum` earns its keep when the values need to carry behavior or be reused as first-class objects elsewhere.
- **Q: A Pydantic model for a tool's arguments validates successfully, but the agent still crashes two lines later trying to use one of the fields. What's a validation gap this points to, and how do you close it?**
  A: Passing type + shape validation (`extra="forbid"`, correct types, required fields present) doesn't guarantee the *values* are sane — a `refund_amount: float` of `-50.0` or an `order_id: str` of `"..."` both pass structural validation while being nonsense. Closing that gap needs a `field_validator` (or `model_validator` for cross-field checks, e.g. "refund_amount must not exceed order total") that inspects actual values, not just types — structural validation and business-rule validation are two separate layers, and skipping the second is exactly the gap that crashes code further downstream instead of failing at the boundary.

#### Decorators as the resilience/observability mechanism

- **Q: You stack `@traced` above `@retry_with_backoff(max_retries=3)` above a tool function. A call fails twice then succeeds on the third attempt. How many trace spans does `@traced` record, and why does the *order* of these two decorators matter?**
  A: Decorator order determines what each one actually wraps — `@traced` above `@retry_with_backoff` means `traced` wraps the *entire retrying process* as one call, so it records one span covering all three attempts (and only sees the final outcome). Reversing the order (`@retry_with_backoff` above `@traced`) would instead retry the *already-traced* function, producing three separate spans, one per attempt. Neither order is "wrong" in the abstract — but if the interview question is "why did our trace show only 1 span for a call we know retried," the answer is decorator order, not a tracing bug.
- **Q: A teammate's custom retry decorator doesn't use `functools.wraps`, and later a FastMCP tool built from that decorated function shows up with the wrong name and no docstring in the exposed schema. Explain the failure chain.**
  A: Without `functools.wraps(fn)`, the decorator's returned `wrapper` function replaces the original function's `__name__`, `__doc__`, and other metadata with its own generic `wrapper`/`None` values, because that's genuinely what got defined and returned. FastMCP builds a tool's JSON schema by introspecting the function object it's given — reading its name and docstring for the tool's `name`/`description` fields — so an unwrapped decorator silently produces a tool schema with `"wrapper"` as the name and no description, exactly the "vague/missing description" failure mode that causes an LLM to never call the tool correctly.
- **Q: Why does the circuit-breaker decorator need to track state (open/closed/half-open, failure count) *outside* the wrapper function's local scope, rather than as local variables inside `wrapper`?**
  A: A closure's local variables inside `wrapper` are recreated fresh on each call in the sense that they don't persist call-to-call unless explicitly captured in an enclosing scope (e.g. as attributes on the decorator object, a `nonlocal`-captured variable in the enclosing decorator function, or a class-based decorator's `self`). A circuit breaker's entire point is remembering failure history *across* calls to decide whether to short-circuit the next one — state that resets every call can never observe "the last N calls failed," so the mechanism requires state living in the enclosing/class scope, not inside the innermost wrapper.

#### Async, concurrency, and where it actually pays off

- **Q: An agent needs to call three independent tools (a weather API, an order lookup, and a policy-RAG query) to answer one user question. Sequentially awaited, it takes 900ms. What's the fastest safe way to speed this up, and what has to be true about the three calls for it to be safe?**
  A: If the three calls are genuinely independent — none needs another's result as input — `asyncio.gather(call_weather(), call_order(), call_rag())` runs them concurrently, so wall-clock time drops toward the *slowest* single call (roughly 300-400ms) instead of the sum. It's only safe if there's no shared mutable state between them (e.g. two calls both mutating the same in-memory cache dict without synchronization) and no ordering dependency — the moment step 2 needs step 1's output, they're no longer parallelizable and reverting to sequential `await` calls is correct, not a missed optimization.
- **Q: A production service starts timing out under load, and profiling shows the event loop is "busy" but each individual LLM call is fast. What's a common root cause specific to async code, and how would you confirm it?**
  A: A likely culprit is a blocking, synchronous call (a non-async `requests.get`, a heavy CPU-bound JSON parse, or worse, an accidental synchronous LLM SDK call inside an `async def`) executing directly on the event loop thread — it blocks *every* coroutine from making progress for its duration, not just its own caller, because async concurrency only works if every task actually yields at `await` points. Confirming it usually means checking for any blocking I/O or CPU-heavy call inside an async function that isn't wrapped in `run_in_executor`/a thread pool, and profiling for a single call stack that "owns" the event loop for an unexpectedly long stretch.
- **Q: Why would adding `asyncio` to a Groq-based agent's tool-calling loop buy noticeably less latency win than adding it to an agent that fans out to 5 independent MCP tool servers?**
  A: Async's benefit scales with how much *genuinely concurrent, independent* I/O-wait there is to overlap. A single agent making one LLM call then waiting on its answer has little to overlap — the call is inherently sequential (you need the model's decision before acting). An agent fanning out to 5 independent tool servers has 5 independent I/O waits that can genuinely run concurrently, so the win is proportional to how much of the total latency is "waiting on parallelizable I/O" versus "waiting on an inherently sequential step" — a distinction worth stating explicitly rather than treating async as a blanket speedup.
