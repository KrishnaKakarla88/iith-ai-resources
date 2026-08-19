# Day 4 · Session 1 — LangFuse Instrumentation, Failure Injection, Production Hardening

Source: `labs/Day4 Session 1 - LangFuse Instrumentation, Failure Injection and Production Hardening.ipynb`

Two labs, both **Milestone 7 — "Observability + reliability hardening"**: Lab A = observability half, Lab B = reliability half. Both wrap the Day3-S2 five-agent research team / `search_kb` tool **without changing behavior** — tracing/hardening are additive layers.

## Lab A — Instrument the research team with LangFuse

A **trace** = one end-to-end run as a tree of **spans** (agent turn / tool call / generation), each with start/end time and optional input/output. Without tracing, a multi-agent failure only shows final state; with it, you see which agent produced a bad value and how long each step took.

- **A1 — `traced(role)` span decorator**: wraps a node fn so calling it opens `langfuse.start_as_current_observation(as_type="span", name=f"agent:{role}")`, records input/output on the span, and — in a `finally` block — appends `{"role", "ms", "ok"}` to a local `RUN_EVENTS` list regardless of success/failure (a crashing agent still shows up in the trace instead of vanishing). Local `RUN_EVENTS` is what the in-notebook dashboard (A3) reads from — no need to pull data back out of Langfuse.
- **A1b — nested spans**: opening a second `start_as_current_observation` **inside** code already running inside an outer span (e.g. a `search_kb` span inside `researcher_node`'s span) nests automatically — no span object passed around by hand, it follows the Python call stack (OTel foundation). This is how a trace becomes a tree, not a flat list — mirrors the "One Request, Forty Spans" idea (`retrieval_agent.run` → child spans `vector_search`/`rerank`).
- **A2 — traced team, tagged per run**: wrap every entry in `NODE_FNS`, rebuild the graph (topology unchanged — same one-node-swap pattern as Day3-S2's MCP researcher swap). Run the whole `team.invoke(...)` **inside** a root span so every child nests automatically. Tag with `session_id`/`user_id` via `langfuse.propagate_attributes(session_id=..., user_id=..., tags=[...])` — lets you filter one learner's/user's run in the UI, auto-attaches to every child span. Self-check proves tracing changed **nothing** about behavior (same plan/draft/status as the untraced run), only what's observable.
- **A3 — per-agent cost/latency dashboard**: `pandas.groupby("role")["ms"].agg(calls="count", total_ms="sum", avg_ms="mean")` over `RUN_EVENTS` — a quick in-notebook view that doesn't depend on the Langfuse UI being reachable. In production, the same shape of query would run against Langfuse's traces/observations API instead of a local list.
- **A4 — traced vs. untraced timing (the TA pitfall, measured)**: every span costs real wall-clock overhead (object creation, attribute recording, eventual flush). On microsecond-fast deterministic stubs that overhead can dominate the numbers. **Never report a traced run's latency as the system's real latency** — measure the delta directly (`statistics.median` over N runs, traced vs untraced) and report the untraced number as real latency.
- **A5 (stretch, separate from A1-4 self-checks) — real LLM calls, cost/token tracking**: swap in `llm_planner_node`/`llm_writer_node` using `ChatLiteLLM`. Two beginner traps: (1) real calls can rate-limit transiently — `call_llm()` wraps `chat_model.invoke()` with `tenacity` retry (`retry_if_exception_type(RateLimitError)`, jittered exponential backoff, `stop_after_attempt(5)`) — the same pattern Lab B formalizes; (2) an LLM doesn't always follow format instructions exactly — if the planner's parse fails silently and nothing bounds planner retries (unlike the writer/reviewer loop's `MAX_REVISIONS`), the graph could loop forever, so `if not plan:` falls back to the deterministic keyword match. `traced_generation(role, model)` opens a `generation`-type span (not plain `span`) — additionally records `model` and `usage_details` (input/output/total tokens, read off `AIMessage.usage_metadata`), which is what lets Langfuse estimate **cost** in its UI (if the model name matches a known price definition). Cost only exists once real tokens are spent — the deterministic team's dashboard legitimately has no cost column.

### Pitfall table (Lab A)
| Symptom | Cause | Fix |
|---|---|---|
| Spans appear flat, not nested | node call happened outside the root span's `with` block | keep `invoke(...)` inside the root span |
| Nothing shows up in Langfuse UI | no `LANGFUSE_PUBLIC_KEY`/`SECRET_KEY` in `.env` | SDK fails silently by design — check `auth_check()` first |
| Reported latency looks worse than production | comparing traced run to an untraced baseline | always benchmark both, report the delta |
| Dashboard misses a role | `traced()` applied to some nodes but not others | wrap every entry in the mapping |

## Lab B — Failure Injection & Production Hardening

Builds a **seeded, deterministic** fault-injection harness around `search_kb`, then hardens it with three standard patterns, measuring before/after success rate with **exact** numbers (self-checks assert exact values because the seed is fixed — reproducible for grading, not "roughly better").

- **Fault harness (provided)**: `FaultConfig(seed, fail_rate, timeout_rate, malformed_rate)`; `make_flaky_search_kb(config)` returns a fresh independently-seeded wrapper (call once per experiment so cells don't share/perturb the same RNG stream) that on each call rolls a seeded random number to decide: raise `ConnectionError`, raise `TimeoutError`, return a malformed record (missing `"text"` key), or call through to the real `search_kb`.
- **B1 — baseline**: call the flaky tool 200 times across 4 topics, tally ok/conn/timeout/malformed. With `BASE_CONFIG = FaultConfig(seed=42, fail_rate=0.2, timeout_rate=0.1, malformed_rate=0.1)`: `success_rate = 0.57`. This is the number every later step must beat.
- **B2 — retries with exponential backoff**: `tenacity.retry(stop=stop_after_attempt(4), wait=wait_exponential(...), retry=retry_if_exception_type((ConnectionError, TimeoutError)), reraise=True)` — retry **only** on the two transient exception types, never on malformed data (retrying bad data just burns the same bad odds again, it's not an exception). Result: success rate 57%→90%; malformed count barely moves (16→20) — proves retries fix transience, not data quality. Rationale for exponential backoff: waiting longer each attempt protects a struggling dependency from a retry storm (Nygard, *Release It!*).
- **B3 — fallback path**: `robust_search_kb` wraps the retrying call — on exhausted retries **or** malformed response, returns a canned `FALLBACK_RECORD` instead of raising, and returns `(records, used_fallback: bool)` so degradation is visible, never silent. Result: success rate → 100% (never raises), 21/200 calls served from fallback. **"A system that silently degrades is worse than one that fails loudly"** — every fallback use should be logged/tagged in production (ties to Lab A's `traced()`).
- **B4 — circuit breaker**: three states — `closed` (normal) → `open` (short-circuits every call immediately, no network attempt, after `failure_threshold` consecutive failures) → `half_open` (exactly **one** trial call after `reset_timeout` elapses, to test recovery without guessing). Any failure in `half_open` re-opens immediately. Pattern originates from Netflix Hystrix / resilience4j — general distributed-systems pattern, not LLM-specific. Demonstrated against a fully-dead dependency (`fail_rate=1.0`): breaker opens after 3 real failures, short-circuits the remaining 7 of 10 calls without ever touching the dead dependency. `failure_threshold`/`reset_timeout` are tuned per dependency in production (too low = blips trip it; too high = keep hammering a dead service).
- **Before/after table**: baseline 57% → +retries 89.5% → +fallback 100% (circuit breaker demonstrated separately since it needs a *sustained* outage that `BASE_CONFIG`'s modest rates don't produce over 200 calls).
- **Stretch goal**: combine with Lab A — wrap `robust_search_kb` with `traced()` so spans record whether a call used retry/fallback/open-breaker, enabling a query like "what fraction of production traffic degraded to fallback this week" straight from trace data.

### Pitfall table (Lab B)
| Symptom | Cause | Fix |
|---|---|---|
| Retries "fix" nothing | malformed responses aren't exceptions, `retry_if_exception_type` never fires | check response shape after the call, handle malformed data separately |
| Retries make latency worse under sustained outage | no circuit breaker — every request pays the full retry budget against a dead dependency | add a breaker in front of the retrying call |
| A "recovered" breaker immediately re-opens | `half_open` treated like `closed` (multiple trial calls allowed) | exactly one trial call in half-open; any failure re-opens |
| Fallback use is invisible in production | fallback returns look identical to real data, no tag | return/log a `used_fallback` flag or trace tag |

## Evaluation section (bridges into Day4-S2)
Three failure modes and where each eval framework's metrics map:
| Failure mode | Ragas | DeepEval | TruLens |
|---|---|---|---|
| Hallucination | `Faithfulness` | `HallucinationMetric` | Groundedness (RAG Triad) |
| Retrieval/extraction misses | `Context Recall` | `ContextualRecallMetric` | Context Relevance (RAG Triad) |
| Tool failures | `Tool call Accuracy`/`Tool Call F1` | `ToolCorrectnessMetric` | not a core focus |

Uses **DeepEval** (`metric.measure(test_case)`, no extra infra) with Groq as judge via `LiteLLMModel(model="groq/...")`.
- **Hallucination**: `HallucinationMetric(threshold=0.3, model=judge)` on an `LLMTestCase(input, actual_output, context=<retrieved KB texts>)` — flags claims not supported by the supplied ground-truth context.
- **Extraction/retrieval recall**: computed directly (`len(retrieved & ground_truth) / len(ground_truth)`) rather than importing Ragas, since Ragas's `context_recall` expects a RAG-shaped reference-answer setup that doesn't match plain extraction — same idea, adapted.
- **Tool correctness**: `ToolCorrectnessMetric` compares `tools_called` (via `ToolCall(name=...)`) against `expected_tools` for a scenario — e.g. did `robust_search_kb` correctly call only `search_kb` on success vs. `search_kb` + `fallback` on forced failure.

**Capstone tie-in:** Milestone 7 — observability (Lab A) + reliability hardening (Lab B) together form the milestone; the evaluation section previews Day4-S2's guardrails/eval work.
