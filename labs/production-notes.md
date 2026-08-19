# ShopSense `src/shopsense/` — Production-Grade Learnings Checklist

Swept every file under `src/shopsense/`, extracting only places where the "obvious" implementation was deviated from because something forced it. Grouped by concern so you can carry it into the new repo as a checklist.

## Retry / Resilience

- **Jittered exponential backoff** (`reliability/retry.py`): fixed-interval retries synchronize into a thundering herd. Fix: `base_delay * 2^(attempt-1) + random.uniform(0,0.1)`, logged per attempt. *Principle:* always jitter; log retries so silent recovery stays observable.
- **Circuit breaker on monotonic clock, scoped per-dependency** (`reliability/circuit_breaker.py`): `time.monotonic()` avoids clock-adjustment bugs; one breaker instance per tool so one bad tool doesn't trip breakers for unrelated ones. `mcp/server.py`'s `reliable()` composes retry *then* circuit-breaker deliberately in that order.
- **Parse the provider's own retry-after signal** (`llm.py`): Groq 429s include "Please try again in 3.86s" — regex-extract and sleep that long instead of guessing a curve.
- **Distinguish transient vs. permanent before retrying** (`rag/indexer.py`): only retries on `"429" in str(exc)`, re-raises everything else immediately.
- **Deliberate pacing beats reactive retry** (`parsing/ticket_parser.py`): flat `time.sleep(2)` between batch records to stay under Groq's free-tier TPM.
- **Graceful loop guard beneath the framework's hard limit** (`graph/workflow.py`, `MAX_SUPERVISOR_VISITS`): forces `"done"` before LangGraph's `recursion_limit` would crash.

## Schema Validation

- **Defensive env-var parsing** (`config.py` `_int_env`): malformed `.env` inline comments broke naive `int(getenv())`; regex-extract the leading integer, fall back to default.
- **`extra="forbid"` on every tool-arg schema** (`models/tool_args.py`): strict Pydantic (`Literal` enums, `Field(gt=0)`) before LLM args touch business logic.
- **Shared extract→validate→repair loop, but keep provider calls local per module** (`parsing/extract_repair.py`): factored control flow out, but left `call_llm` in each caller's namespace because tests `patch()` it by module path — refactor the flow, not the mocked call site.
- **Never trust the LLM to reproduce a verbatim field** (`parsing/ticket_parser.py`): `raw_text` is never asked of the model; injected via `setdefault` after JSON parse.
- **Fail-closed on unparseable judge output** (`guardrails/groundedness.py`): bad JSON from the LLM-judge → `{"grounded": False, "score": 0}`, not a crash or a pass.

## Tool Calling

- **Force-set authorization-critical fields server-side** (`agents/order_agent.py`): `tool_args["customer_ref"]` unconditionally overwritten before validation — never trust an LLM tool-call arg for identity.
- **Enforce deterministic values in code, not just the prompt** (`calculated_refund_by_order` override): the model is told to copy `calculate_refund_amount`'s number, but code force-overwrites `amount_inr` anyway, warning on disagreement.
- **Detect narrated-but-not-executed outcomes**: model would narrate "refund processed" without calling the tool. Fix: regex-detect outcome language + inject a `SystemMessage` forcing it back into the tool loop if no tool ran — paired with an explicit prompt rule, since the prompt alone wasn't reliable.
- **Match provider tool-call errors by message text, not exception class** (`_is_tool_call_generation_error`): exception classes aren't standardized across providers routed through litellm.
- **Convert cross-tenant `PermissionError` into a safe message**, not a leak of the real owner.
- **Regex/keyword extraction is a fallback, never the source of truth** (`request_extractor.py`, `agent_helpers.py`): structured LLM extraction + schema validation is primary.
- **Spell out which enum subset applies per tool** when two tools share a similar but different `Literal` vocabulary (`prompts/order_agent.py`).
- **A tool-execution library's return shape can change across versions with no error, just wrong-looking data**: a real incident — a successful `process_refund` got reported to the customer as failed because the MCP adapter returned the newer content-block-list shape (`[{"type":"text","text":"<json>","id":"..."}]`) instead of the bare dict an `isinstance(result, dict)` check was written against. Fix: normalize once at the MCP-call boundary, not per consumer — an `isinstance` check against one SDK shape is a version pin in disguise.

## RAG Retrieval

- **Lazy `@lru_cache(maxsize=1)` singletons for the cross-encoder/embedder** (`rag/retriever.py`) — reloading from disk per instance was slow.
- **Guard empty-corpus edge case**: `BM25Okapi` raises `ZeroDivisionError` on empty corpus; short-circuit to `[]` first.
- **Reciprocal Rank Fusion instead of score normalization**: dense and BM25 scores are on incompatible scales; fuse by rank position.
- **Deterministic point IDs** (`uuid5(NAMESPACE, f"{source}:{chunk_idx}")`) for idempotent re-ingest — random `uuid4()` duplicated every chunk on re-run. Comment: never change the namespace constant, it orphans all prior data.

## Memory

- **Scope thread/checkpoint identity to the unit of work, not the session**: fresh `thread_id` per turn — reusing one per session leaked finished state into the next turn's routing.
- **Raw uncompressed fallback for exact identifiers**: LLM-compressed summaries drop literal `order_refs`; try raw recent-turns cache first, fall back to compressed summary.
- **Explicit ordering dependency** between context-gathering steps, documented inline — reordering "equivalent-looking" steps silently reintroduced a UX bug.
- **Label recalled memory as untrusted in the prompt**: memory can contain the assistant's own past hallucinations; wrapped in a `SystemMessage` marked "never the source of a new tool argument."
- **Identity only from authenticated session, never from message text** (`memory_bridge.py`) — an old version guessed `customer_ref` from an order ref in free text.
- **Memory-writing functions must run on every turn/every return path** — called out twice in the codebase as a recurring regression ("asks every time" symptom).
- **Purge must clear the in-process cache, not just the persistent store**, or a long-lived process keeps serving stale data.
- **Fail open but log loudly** (`customer_memory.py` `_store`): swallowed exceptions, but now with `exc_info=True`.
- **Document best-effort bulk ops honestly**: no "list all" API in Supermemory, so purge is a best-effort semantic sweep, not guaranteed-complete.
- **Explicit per-tenant namespace on every read/write** (`_ns`) — a single missed call site would leak cross-customer data.

## Guardrails

- **Config-driven thresholds, not hardcoded constants** (`AUTO_REFUND_CAP_INR` was a Python constant; moved to env).
- **Defense in depth: duplicate independent enforcement at multiple layers** — graph-layer `check_refund_cap` mirrors the service-layer check; fabrication check runs on top of ReAct's own reflection.
- **Structurally restrict a guardrail-bypass flag to its one legitimate caller** (`human_approved` only ever set by `refund_execute_node`).
- **Probabilistic injection detection paired with prompt-level "untrusted data" framing**, not a hard block.
- **Auto-expire stalled escalations** as an idempotent side effect of existing read paths, not dedicated worker infra.
- **Document what an eval metric actually measures**: `expected_route` scored against answer content, not structural routing state, since no golden case exercises the real interrupt route — explicitly flagged so it isn't misread later.
- **Hard-block + safe fallback text, not just a flag, once a groundedness guardrail fires**: flagging alone still surfaced a possibly-fabricated answer. Fix: swap in a canned "couldn't find a grounded answer" message; original text is kept only for logs/eval, never shown. Same shape gap the refund flow had before its own human-in-loop step existed — deliberately deferred, not silently inconsistent.

## Auth / Permissions

- **Explicit login gate, never guess identity from free text** (`auth/customer_auth.py`).
- **Explicitly branch credential resolution when introducing a proxy layer** (`llm.py`): litellm's default per-provider env-var resolution sends the wrong token to a LiteLLM proxy.
- **Re-verify authorization at the point of mutation, not just at login** (`order_service._authorize` on every call).
- **Embed the owner in the resource ID for cheap ownership checks** (`thread_id.startswith(f"{customer_ref}:")`).
- **Model the actual actor per endpoint**: reviewer endpoint deliberately skips the customer-ownership check present on `/chat/resume` — documented so it isn't "fixed" into a bug later.

## Concurrency / Idempotency

- **Async resources backed by structured concurrency must stay within one Task** (`_McpToolsCache`): caching an MCP session across `tools()` calls broke because anyio TaskGroups can't cross asyncio Tasks — LangGraph runs each node in its own Task.
- **Unwrap `BaseExceptionGroup` at every catch site near a TaskGroup** (PEP 654 — single exceptions still get wrapped).
- **Split interrupt/resume nodes so no side effect runs before the pause point** — a resumed node re-runs from the top, so pre-interrupt side effects fire twice.
- **Validate state completeness even after human approval**, before executing.
- **Overwrite semantics for control fields, accumulate only the audit log** — accumulating routing fields is "the classic graph-never-terminates bug."
- **Enforce per-node write scopes programmatically** (`@scoped(role)`) — catches cross-node state bugs immediately, not as a downstream symptom.
- **Move idempotency-sensitive bookkeeping out of a re-runnable node**, into an upsert-based side table written from call sites that see the one-time event.
- **WAL mode + short-lived per-call connections** for a side-table shared across sync/async contexts.
- **Validate cross-store consistency before acting on an assumption** — registry row can outlive its checkpoint; check `snapshot.next` before resuming, else 409 + mark resolved.

## Prompt Engineering

- **Stop sequence to block self-generated fake observations** (`stop=["Observation:"]` in the ReAct loop).
- **Replace LLM inference of a conditional rubric with a computed fact** injected as `[FACT]` — the critique LLM kept mis-inferring "escalated."
- **Fail open on a broken quality-improvement pass** (`reflection.py` returns the original draft, verdict `"SKIPPED"`).
- **Ambiguity → ask, don't keep retrying retrieval** — bounds cost and hallucination risk.
- **Frame every piece of external/stored content as untrusted data — applied uniformly**, not just at the "obvious" RAG boundary (retrieved docs, ReAct observations, reflection context, memory recall, even MCP prompt template fields).
- **One top-level tracing span per turn**, entered before any nested async boundary, rather than trusting OTel propagation alone across async hops.
- **A generation span isn't useful without explicit input/output/cost** — token counts alone still hide the prompt/response text and show no $ figure (the SDK's built-in price table doesn't reliably know provider-prefixed model names). Wire `input`/`output` from the actual messages/response, and compute cost explicitly via the LLM library's own cost-per-token helper rather than relying on auto-pricing.
- **A centralized instrumentation fix doesn't reach call sites that bypass the central function**: a fix to one LLM-call wrapper only covers callers that go through it — a second code path that talks to the model directly (e.g. via a different SDK's own `bind_tools()`/`ainvoke()`) needs the same input/output wiring added by hand. Audit for parallel paths before calling an instrumentation fix complete.
- **A generic "wrap the whole function" tracing decorator becomes a PII leak once its argument is a shared, growing state dict**: a blanket `repr(args/kwargs/result)` capture on every graph node put the customer's raw chat message (the state's first field, within the truncation window) on every node span, every turn — discovered as a real, live exposure, not a hypothetical, and initially missed because the decorator was applied as a plain call (`traced_node(name)(fn)`) rather than `@traced_node`, so a decorator-syntax grep found nothing. Fix: an explicit redact-keys allowlist blanks free-text fields before repr; routing/audit fields stay visible.
- **Uniform trace sampling has no concept of "always keep the interesting ones"**: sample-rate config draws per trace (the right granularity) but is a uniform random draw with no override for errors/escalations. Fix: mark flagged/escalated traces with a `level="WARNING"` after the fact so they're filterable regardless of sample rate — it can't rescue a trace already dropped by sampling. If volume forces sampling on a system handling refunds/escalations, cut payload size before cutting trace count.
- **Pay a library's slow first-call cost at startup, not on the first customer request**: an LLM library's ~11s first-import cost and a tracing SDK's first auth round-trip both previously happened lazily inside the first LLM call, showing up as unattributed gap time on whatever request triggered it. Fix: eagerly trigger both in app startup, best-effort — a warm-up failure never blocks startup, the same call still runs and fails the same way on first real use either way.

## Error Handling

- **Central fail-fast validation, called at entry points only — not import time** (`validate_required_env`), because tests import the module transitively without live keys.
- **Observability code must never fail the primary operation** — cost estimation and tracing payloads both defensively wrapped/truncated.
- **Check multiple known response shapes for library version drift** (`LLMUsageCallback.on_llm_end`: `llm_output` vs. `usage_metadata`).
- **Degrade to a uniform "nothing extracted" sentinel rather than raising** (`request_extractor.py`).
- **Pick the fallback branch whose downstream logic is most self-sufficient** (`triage_agent.py` defaults to `"order"`, not `"policy"`, on parse failure).
- **Isolate each scorer's failure in a multi-metric eval harness** so one broken metric doesn't null the whole case.
- **Resolve and cache optional integrations lazily for the process lifetime**, treat `None`/unavailable as normal everywhere downstream, never force-flush on the hot path.

## Technology-Specific Learnings

- **LangGraph**: loop guard beneath `recursion_limit`, thread-ID scoping to checkpointer, interrupt/resume side-effect ordering, state reducer overwrite-vs-accumulate, per-node write scopes, duplicate guardrail enforcement layers, triage fallback branch choice, hard-block+fallback on a failed groundedness guardrail.
- **LangChain**: tool-arg identity injection, forced deterministic refund amount, narrated-but-unexecuted outcome detection, `PermissionError` handling, memory ordering/labeling in prompts, reflection fail-open, `LLMUsageCallback` version-shape drift, direct `bind_tools()`/`ainvoke()` calls bypassing a centralized LLM wrapper's tracing.
- **LiteLLM**: proxy credential branching, retry-after parsing from Groq 429 body, message-substring matching for malformed tool-call errors (exception classes not standardized across providers), slow first-import cost warmed up at startup instead of on the first request.
- **Langfuse**: lazy cache-once client resolution, no force-flush on hot path, one top-level span per turn, sanitized/truncated tracing payloads, explicit input/output/cost wiring on generation spans, redacting free-text state keys before a blanket tracing decorator reprs them, trace-level `level` marking for guardrail/escalation outcomes since uniform sampling has no "always keep" override.
- **FastAPI**: prefix-based ownership check on `thread_id`, deliberate asymmetry between customer-resume and reviewer-decision endpoints, eager dependency warm-up in `lifespan` to avoid unattributed first-request latency.
- **Pydantic**: `extra="forbid"` strict tool-arg schemas, shared extract-validate-repair helper (with a note on why `call_llm` stayed per-module for test-mocking reasons), never asking the LLM to reproduce verbatim fields.
- **Qdrant**: deterministic `uuid5` point IDs for idempotent re-ingest.
- **rank_bm25**: empty-corpus `ZeroDivisionError` guard; RRF fusion to sidestep score-scale mismatch with dense search.
- **Supermemory**: per-tenant namespace tagging, purge must clear in-process cache too, fail-open-but-log-loudly, "no list-all API" documented as best-effort.
- **SQLite (escalation registry)**: WAL mode + per-call sync connections across mixed async/sync contexts, upsert-based idempotent writes, cross-store consistency check against the LangGraph checkpointer.
- **anyio/MCP**: session must stay within one asyncio Task, `BaseExceptionGroup` unwrapping per PEP 654; a tool-adapter library's result shape isn't stable across versions — normalize once at the call boundary, not per consumer.