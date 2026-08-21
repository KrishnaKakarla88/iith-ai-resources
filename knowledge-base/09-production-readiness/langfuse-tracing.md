---
stage: "09-production-readiness"
tools: [langfuse]
tags: [observability, tracing, cost-accounting, pii]
last_verified: 2026-08-20
verified_against: "langfuse 4.14.0 (this repo's lab pin; SDK v4 — get_client()/start_as_current_observation, not v2/v3 decorators)"
---

# Langfuse tracing

Langfuse turns "the agent gave a wrong answer, 14 seconds, no error" into a tree of timed, inspectable spans — one per agent turn or tool call — so a multi-step failure is a lookup instead of a guess.

## Prerequisites
- [[decorators-and-wrappers]]
- [[agentic-loop-fundamentals]]
- [[async-await-for-llm-apps]]

## In plain English

Without tracing, a multi-agent run that produces a wrong answer only shows you the final state — you can't tell which agent produced the bad value or which step ate the latency. A **trace** is one end-to-end run represented as a tree of **spans** (an agent turn, a tool call, an LLM generation), each with a start time, end time, and optional recorded input/output. Open a second span inside code that's already running inside an outer span and it nests automatically — Langfuse follows the Python call stack (built on OpenTelemetry), so you never pass a span object around by hand. That's what turns a flat list of events into a tree: `supervisor.run` containing `retrieval_agent.run` containing `vector_search`/`rerank` as children, exactly the shape you'd want when a user reports "it gave me the wrong shipping date" and the trace shows the reranker returned a low-confidence chunk that the answer agent used anyway.

## Core mechanics

| API | Purpose |
|---|---|
| `get_client()` | Returns the process-wide Langfuse client, configured from `LANGFUSE_PUBLIC_KEY`/`LANGFUSE_SECRET_KEY`/`LANGFUSE_HOST` env vars — v4's entry point, replacing v2/v3's `Langfuse()` direct instantiation patterns |
| `start_as_current_observation(as_type=..., name=...)` | Context manager that opens a span (or generation) and sets it as the active observation; anything opened inside its `with` block nests as a child automatically |
| `as_type="span"` vs `as_type="generation"` | v4 unifies what were separate `start_span()`/`start_generation()` calls behind one API — use `"generation"` for an actual LLM call so Langfuse can record `model`/`usage_details` and estimate cost |
| `span.update(input=..., output=...)` | Attaches input/output data to an already-open observation |
| `generation.update(usage_details={...})` | Records token counts (`input`/`output`/`total`) on a generation span — this is what lets Langfuse's UI compute a cost figure, if the model name matches a known price entry |
| `propagate_attributes(session_id=..., user_id=..., tags=[...])` | Context manager that stamps `session_id`/`user_id`/`tags` onto the current span and every child created inside its scope — v4's replacement for v3's imperative `update_current_trace()` |
| `langfuse.flush()` | Forces buffered spans to send immediately — needed in short-lived scripts/notebooks that would otherwise exit before the background flush fires |

## Sample code

Lab-sourced (Day 4 · Session 1 — `labs/Day4 Session 1 - LangFuse Instrumentation, Failure Injection and Production Hardening.ipynb`), Langfuse 4.14.0 pinned in the notebook install cell. A span decorator that survives failure, and a generation span that records real token usage:

```python
import functools, time
from langfuse import get_client, propagate_attributes

langfuse = get_client()
RUN_EVENTS = []  # {"role": str, "ms": float, "ok": bool} per call — local dashboard, no round-trip to Langfuse needed

def traced(role: str):
    """Wrap a node fn so every call opens a named span, records input/output,
    and appends a timing record to RUN_EVENTS — even when the node raises."""
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(state):
            t0, ok = time.perf_counter(), True
            try:
                with langfuse.start_as_current_observation(as_type="span", name=f"agent:{role}") as span:
                    result = fn(state)
                    span.update(input={"plan": state.get("plan")}, output={"wrote": sorted(result)})
                    return result
            except Exception:
                ok = False
                raise
            finally:
                RUN_EVENTS.append({"role": role, "ms": (time.perf_counter() - t0) * 1000, "ok": ok})
        return wrapper
    return decorator

# tag the whole run, inside a root span so every node nests under it automatically
with langfuse.start_as_current_observation(as_type="span", name="research-team-run"):
    with propagate_attributes(session_id=session_id, user_id=user_id, tags=["day4", "lab-a"]):
        traced_team.invoke(seed, {"recursion_limit": 50})
langfuse.flush()
```

A `generation`-type span, additionally recording model and token usage for cost accounting:

```python
def traced_generation(role: str, model: str):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(state):
            with langfuse.start_as_current_observation(as_type="generation", name=f"agent:{role}", model=model) as gen:
                result = fn(state)
                usage = LAST_USAGE.get(role)   # AIMessage.usage_metadata, keyed by role
                if usage:
                    gen.update(usage_details={
                        "input": usage["input_tokens"],
                        "output": usage["output_tokens"],
                        "total": usage["total_tokens"],
                    })
                return result
        return wrapper
    return decorator
```

`traced()`/`traced_generation()` wrap `NODE_FNS` the same way an [[mcp-fastmcp]]-backed researcher swap wraps one node — a decorator applied at graph-build time, topology unchanged.

### Cost accounting

Cost only exists once real tokens are spent — a fully deterministic node (no LLM call) legitimately has no cost figure, and its dashboard column should read as absent, not zero. Two things have to be true for Langfuse to show a dollar figure at all: (1) a `generation`-type observation, not a plain `span`, and (2) `usage_details` wired from the actual response object (`AIMessage.usage_metadata` for LangChain-routed calls) — Langfuse's built-in price table doesn't reliably resolve every provider-prefixed model name (e.g. `groq/llama-3.1-8b-instant`), so a generation span with only elapsed time and no usage numbers shows latency but no cost. `litellm.token_counter()` (see [[tokens-and-tokenization]]) is the fallback when a provider's response doesn't expose usage metadata at all.

## Alternatives

| Tool | Where it lives | Differentiator |
|---|---|---|
| Langfuse | Open source (MIT), self-hostable; SDK built on OpenTelemetry | Centralized Postgres-backed trace store, prompt/eval/dataset management built in — this repo's pinned choice |
| [OpenTelemetry (GenAI semantic conventions) + structured logs](https://github.com/open-telemetry/semantic-conventions-genai) | Vendor-neutral spec + your own log/trace backend | **The boring alternative** — no hosted UI, but the raw span/attribute shape (`gen_ai.*` conventions) is the substrate Langfuse's own SDK is built on; own your backend, write your own dashboard |
| [LangSmith](https://langfuse.com/resources/engineering/langsmith-alternative) | Proprietary, LangChain-team-run | Deepest auto-instrumentation for LangChain/LangGraph specifically; closed-source, no self-hosting |
| [Helicone](https://www.helicone.ai/blog/the-complete-guide-to-LLM-observability-platforms) | Proxy-based (route calls through its endpoint) | Integrates via a URL/base-path change rather than an SDK; built-in response caching Langfuse doesn't have, but framework-agnostic at the API-call level only (shallower than nested-span tracing) |

## How this shows up in the capstone

Milestone 7 (observability + reliability hardening) — every agent gets `traced()`/`traced_generation()` wrapping from the first agent built, per [[capstone-milestone-map]].

## Interview fire round

- **Q: Why does a `generation` span need explicit `usage_details`, when a `span` doesn't?**
  A: Cost only computes from token counts. A plain `span` has no token concept; a `generation` span needs `model` and `usage_details` wired from the actual response object, because the SDK's built-in per-model price table can't reliably resolve every provider-prefixed model name.
- **Q: Why compare traced vs. untraced latency instead of just reporting the traced number?**
  A: Every span costs real wall-clock overhead — object creation, attribute recording, eventual flush. On fast operations that overhead can dominate the numbers; report the untraced median as the system's real latency, and the delta as a separate, also-interesting fact about instrumentation cost.

## Production gotchas & best practices

- Lab gotcha: nothing shows up in the Langfuse UI and the SDK fails **silently by design** if `LANGFUSE_PUBLIC_KEY`/`SECRET_KEY` are missing — check `auth_check()` first rather than assuming a config problem elsewhere.
- Lab gotcha: spans appear flat instead of nested when a node call happens outside the root span's `with` block — keep `invoke(...)` inside the root span, since nesting follows the Python call stack, not manual span-passing.
- Lab gotcha (`labs/production-notes.md`): a generation span isn't useful without explicit `input`/`output`/`usage_details` — token counts alone hide the actual prompt/response text and show no dollar figure if the model name doesn't match a known price entry. Wire input/output from the real messages/response, don't rely on auto-capture.
- Lab gotcha: a centralized instrumentation fix doesn't reach call sites that bypass the central wrapper — a fix to one LLM-call function only covers callers that go through it; a second code path calling a model directly (e.g. a different SDK's own `bind_tools()`/`ainvoke()`) needs the same input/output wiring added by hand. Audit for parallel LLM-call paths before calling an instrumentation pass complete.
- Lab gotcha: pay a library's slow first-call cost (LLM SDK import, tracing SDK's first auth round-trip) at app startup, not on the first customer request — both previously happened lazily inside the first LLM call and showed up as unattributed gap time on whichever request triggered them; trigger both eagerly and best-effort at startup instead.

### PII in traces

A real, documented incident (`labs/production-notes.md`): a generic "wrap the whole function" tracing decorator that blindly `repr()`s its arguments becomes a PII leak the moment one of those arguments is a shared, growing state dict. In this codebase, a blanket `repr(args/kwargs/result)` capture on every LangGraph node put the customer's raw chat message — the state dict's first field, within the repr's truncation window — onto every node's span, every single turn. It was initially missed because the decorator had been applied as a plain call (`traced_node(name)(fn)`) rather than `@traced_node`, so a grep for decorator syntax found nothing. The fix was an explicit redact-keys allowlist that blanks free-text fields before the repr runs, while routing/audit fields (role, status, ids) stay visible — see [[privacy-and-pii-handling]] for the general pattern this instance of. The lesson generalizes past this one decorator: any tracing layer that captures "whatever's in scope" rather than named, reviewed fields is a PII leak waiting on the next field someone adds to shared state.

### Reliability signals beyond errors and latency (per course material, `presentations/day4.md`)

- **Prompt-cache hit rate** — caching reuses a previously-processed prompt prefix; a stable hit rate implies a stable request shape upstream. A drop (course example: 91% → 38% within five minutes of a one-line system-prompt edit) doesn't by itself mean broken, but it reliably means something upstream changed and is worth investigating — the cost/1k-requests figure in that example roughly tripled with zero change in error rate, so nothing paged anyone. Put cache hit rate on the same dashboard as latency and error rate, watched continuously, not reviewed monthly as a cost line.
- **Context size as a reliability signal, not just a cost line** — attention doesn't scale uniformly with context length (Chroma Research, "Context Rot," 2025 — see [[context-rot-and-long-context-management]]), so a request that quietly grows from ~6K to ~64K input tokens (stale chat history, extra retrieved documents, more tool schemas) degrades answer quality non-uniformly, not just latency/cost. The course's diagnostic move: don't alert on token count alone — correlate rising input tokens with p95 latency, cost per request, and user-correction/escalation rate together, then break the context down by source to find what's actually bloating it.
- **Cost-anomaly triage order** — cost is a lagging signal (by the time the bill moves, the cause has usually been running for hours). When cost doubles and nothing errored, the course's stated investigation order is: rule out traffic first (cheapest check), then check cache hit rate, then retrieval depth/chunk count, then a silent retry loop, then session length — stop at the first plausible cause and you'll be back next week, since two things can move at once.
- **Silent-failure detection** — a silent failure passes every check you wrote: valid output, 200 response, no exception, and wrong. Two course-recommended detectors: **canary queries** with known-correct answers, run continuously (a system that can't answer them has drifted), and watching the **refusal rate in both directions** — too few refusals is as much a warning sign as too many, since a zero error rate is a claim that needs checking, not a result worth celebrating.

## Course vs. production

The lab measures overhead on microsecond-fast deterministic stubs, where span-creation cost can dominate the numbers — a classroom artifact of stub speed, not a real-world tracing cost. In production, tracing overhead is genuinely small relative to network-bound LLM calls, but the redaction discipline the lab surfaces (never repr a raw shared-state dict onto a span) and the sampling discipline from `presentations/day4.md` (keep 100% of errored/refused/over-threshold runs, sample healthy runs down to a few percent, and mark flagged/escalated traces with `level="WARNING"` so they're filterable regardless of sample rate) are both production requirements the lab's single-learner notebook run never has to face at scale.

## Related
- **Builds on** — [[decorators-and-wrappers]], [[agentic-loop-fundamentals]]
- **Feeds into** — [[privacy-and-pii-handling]], [[retry-fallback-patterns]]
- **Contrasts with** — [[testing-agent-code]] (tests correctness offline; tracing observes live behavior)
- **Instruments** — [[langgraph-nodes]] (each node function is a natural span boundary in a graph-based agent)

## Sources

**Lab sources**
- `lab-summaries/Day4-Session1-LangfuseHardening.md` (§ "Lab A — Instrument the research team with LangFuse")
- `labs/Day4 Session 1 - LangFuse Instrumentation, Failure Injection and Production Hardening.ipynb` (cells: `traced()`, `traced_generation()`, `propagate_attributes` usage)
- `labs/production-notes.md` (§ "Prompt Engineering" — tracing/PII/instrumentation entries; § "Technology-Specific Learnings" — Langfuse)

**Web sources**
- [Langfuse — Python v3 → v4 migration guide](https://langfuse.com/docs/observability/sdk/upgrade-path/python-v3-to-v4) — `start_observation()`/`start_as_current_observation()` unification, `as_type` parameter, `propagate_attributes()` replacing `update_current_trace()`, accessed 2026-08-20
- [Langfuse Python SDK on PyPI](https://pypi.org/project/langfuse/) — latest release 4.14.4 (lab pins 4.14.0), Python ≥3.10 required, accessed 2026-08-20
- [OpenTelemetry GenAI semantic conventions](https://github.com/open-telemetry/semantic-conventions-genai) — the span/attribute substrate Langfuse's SDK builds on, accessed 2026-08-20
- [Langfuse — LangSmith alternative comparison](https://langfuse.com/resources/engineering/langsmith-alternative) — self-hosting/open-source vs. proprietary positioning, accessed 2026-08-20
- [Helicone — LLM observability platforms guide](https://www.helicone.ai/blog/the-complete-guide-to-LLM-observability-platforms) — proxy-based integration model, built-in caching, accessed 2026-08-20
- `presentations/day4.md` (Session 1, Act 1-3) — cache-hit-rate-as-reliability-signal, context-rot-as-reliability, cost-anomaly triage order, silent-failure/canary-query detection — cited per course material, not independently web-verified for the specific numeric examples
