---
stage: "02-python-for-ai-agents"
tools: [functools]
tags: [primer, decorators, resilience, tracing]
last_verified: 2026-08-20
verified_against: "Python 3.13 (this repo's pin: requires-python >=3.13)"
---

# Decorators and wrappers

A decorator wraps a function with extra behavior — logging, retrying, tracing — without changing the function's own code; this is the exact mechanism retry, circuit-breaker, and tracing get bolted onto agent functions throughout this stack.

## Prerequisites
- [[functions-args-kwargs]]

## In plain English

Functions in Python are ordinary objects — they can be passed around, stored in variables, and returned from other functions. A decorator takes advantage of that: it's a function that accepts another function and returns a new function that wraps it — usually running some behavior, calling the original, then running more behavior. `@my_decorator` above a function definition is shorthand for `my_function = my_decorator(my_function)`.

The reason this matters for agent code specifically: retrying a flaky tool call, tripping a circuit breaker after repeated failures, and recording a trace span all need to happen *around* a function call, not inside the function's own logic — and they need to happen the same way for many different functions with different signatures. A decorator lets you write that "around" behavior exactly once and apply it to any function, instead of copy-pasting a try/except-retry block into every tool.

## Core mechanics

| Piece | Role |
|---|---|
| Outer function (`retry_with_backoff(max_retries=3)`) | takes decorator arguments, returns the actual decorator |
| Decorator (returned by the outer function) | takes the target function `fn`, returns `wrapper` |
| `wrapper(*args, **kwargs)` | the function that actually runs at call time — calls `fn(*args, **kwargs)`, wrapped in whatever the decorator adds |
| `@functools.wraps(fn)` on `wrapper` | copies `fn.__name__`/`__doc__`/etc. onto `wrapper` so introspection and debugging still show the original function's identity, not `"wrapper"` |
| Stacking (`@a` then `@b` above a function) | applies bottom-up — `b` wraps the function first, then `a` wraps the result |

Without `functools.wraps`, every decorated function's `__name__` becomes `"wrapper"` and its docstring disappears — harmless for behavior, but it breaks introspection tools, `help()`, and (in this stack specifically) anything that reads a function's identity or docstring for a schema, like FastMCP.

## Sample code

Lab-sourced retry decorator (`lab-summaries/Day1-Session2-ToolCalling.md`, § A6 — "Reliability wrappers"), the outer-function-returns-decorator pattern needed because the decorator itself takes arguments:

```python
import functools, random, time

def retry_with_backoff(max_retries: int = 3, base_delay: float = 0.5):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return fn(*args, **kwargs)
                except Exception:
                    if attempt == max_retries:
                        raise
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 0.1)  # exponential backoff + jitter
                    time.sleep(delay)
        return wrapper
    return decorator

@retry_with_backoff(max_retries=3, base_delay=0.5)
def get_weather(city: str) -> dict:
    ...
```

The tracing span decorator (`lab-summaries/Day4-Session1-LangfuseHardening.md`, § A1 — "`traced(role)` span decorator"), same three-layer shape, wrapping a node function in a `finally` block so a crashing agent still shows up in the trace instead of vanishing:

```python
def traced(role: str):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            with langfuse.start_as_current_observation(as_type="span", name=f"agent:{role}") as span:
                start = time.monotonic()
                ok = True
                try:
                    result = fn(*args, **kwargs)
                    span.update(output=result)
                    return result
                except Exception:
                    ok = False
                    raise
                finally:
                    RUN_EVENTS.append({"role": role, "ms": (time.monotonic() - start) * 1000, "ok": ok})
        return wrapper
    return decorator
```

## How this shows up in the capstone

Every agent function in this build gets wrapped in this exact pattern in layers — `traced(role)` for observability (M7), `retry_with_backoff`/`CircuitBreaker` for resilience (M2/M7) — stacked without touching the underlying function's own logic each time a new cross-cutting concern is added.

## Interview fire round

- **Q: Why does `retry_with_backoff` need three nested function levels instead of one?**
  A: The outer level exists only to accept the decorator's own arguments (`max_retries`, `base_delay`) — `@retry_with_backoff(max_retries=3)` calls `retry_with_backoff(3)` first, which must return the actual decorator function, which in turn returns the wrapper that runs at call time. A parameterless decorator only needs two levels.
- **Q: What breaks if you forget `@functools.wraps(fn)` inside a decorator?**
  A: `wrapper.__name__`, `__doc__`, and other metadata get replaced by the wrapper's own — every decorated function reports as `"wrapper"` under introspection. In this stack that's not cosmetic: FastMCP reads a tool function's name/docstring to build its JSON schema, so an unwrapped decorator on a tool function would silently break the exposed schema.
- **Q: Why is the tracing decorator's record-keeping inside a `finally` block, not just after the successful return?**
  A: A `finally` block runs whether the wrapped call succeeded or raised — a crashing agent still gets logged with `ok=False` instead of vanishing from the trace, which is exactly the failure case you most need visibility into.

## Production gotchas & best practices

- Decorator order matters when stacking retry + circuit breaker: this stack applies retry innermost and the circuit breaker outermost (`make_robust_tool`, `lab-summaries/Day1-Session2-ToolCalling.md`, § A6) so a burst of retried-but-still-failing calls is what trips the breaker — swapping the order changes what "one failure" means to the breaker.
- `functools.wraps` is not optional in production code that introspects functions (docs, schema generation, some test frameworks) — treat a bare `def wrapper(*args, **kwargs):` without it as a bug, not a style nit ([Python 3 functools docs — wraps](https://docs.python.org/3/library/functools.html#functools.wraps), accessed 2026-08-20).
- Async functions need an async-aware decorator (`async def wrapper(*args, **kwargs): return await fn(*args, **kwargs)`) — a sync decorator applied to an `async def` function just wraps the coroutine object without awaiting it, silently returning an un-awaited coroutine instead of a result; `inspect.iscoroutinefunction(fn)` is the standard check for a decorator meant to support both (`lab-summaries/Day3-Session2-MultiAgentProtocols.md`, § A1: `@scoped(role)` "handles async nodes too via `inspect.iscoroutinefunction`").

## Course vs. production

The lab's retry/circuit-breaker decorators are hand-rolled to teach the mechanism; production code more often reaches for a maintained library (`tenacity` for retry — used directly in `lab-summaries/Day4-Session1-LangfuseHardening.md`'s Lab B hardening pass once the hand-rolled version's lesson has landed) rather than hand-writing backoff/jitter math per project. The underlying decorator pattern is identical either way — see [[retry-fallback-patterns]] and [[circuit-breaker-pattern]] for the maintained-library version of this same mechanism.

## Related

- **Builds on** — [[functions-args-kwargs]], [[dunder-methods]]
- **Underlies** — [[retry-fallback-patterns]], [[circuit-breaker-pattern]], [[langfuse-tracing]]

## Sources

**Lab sources**
- `lab-summaries/Day1-Session2-ToolCalling.md` (§ A6 — "Reliability wrappers")
- `lab-summaries/Day4-Session1-LangfuseHardening.md` (§ A1 — "`traced(role)` span decorator")
- `lab-summaries/Day3-Session2-MultiAgentProtocols.md` (§ A1 — `@scoped(role)` async-aware decorator)
- `labs/Day1 Session 2 - Tool calling and Single Agent Patterns.ipynb`
- `labs/Day4 Session 1 - LangFuse Instrumentation, Failure Injection and Production Hardening.ipynb`

**Web sources**
- [Python 3 tutorial — Decorators (via functools)](https://docs.python.org/3/library/functools.html#functools.wraps) — `functools.wraps`, why it matters for introspection, accessed 2026-08-20
- [Real Python — Primer on Python Decorators](https://realpython.com/primer-on-python-decorators/) — parameterized decorators, stacking order, accessed 2026-08-20
