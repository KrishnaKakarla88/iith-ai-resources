# Day 4 · Session 2 — Evaluation, Guardrails & Continuous Improvement

Source: `labs/Day4 Session 2 - Evaluation, Guardrails and Continuous Improvement.ipynb`

System under test: **Campus Library Assistant** — a toy domain, deliberately swappable, chosen only for zero-domain-knowledge accessibility. Everything downstream (scorers, guardrails, Langfuse wiring, FastAPI) is domain-agnostic. Frameworks: Ragas, DeepEval, TruLens (all three as LLM-judges, cross-checked against each other and deterministic scorers), Langfuse (tracing + experiment runner), FastAPI + ngrok (deployable public endpoint). LLM: `gemini-flash-lite-latest` throughout via `google-genai`, rate-limit-safe wrappers.

**Setup gotcha worth remembering**: Ragas 0.4.3 has an upstream bug — imports `ChatVertexAI` from a `langchain_community` path that package deleted (moved to `langchain-google-vertexai`). Fix: register a harmless stub module under that exact import path in `sys.modules` before importing ragas.

## Rate-limit-safe call wrapper
Free-tier Gemini's 15 RPM limit is **shared across every call source** in the notebook (the agent itself + all three judge frameworks) — throttling only the agent isn't enough since each judge framework makes its own HTTP calls. `_pace()` is a shared gate (`_MIN_GAP_SECONDS=4.5`, blocks until that much time passed since the *last* call from *any* source). `_suggested_wait(exc, fallback)` parses Gemini's actual `retryDelay` from the 429 body instead of guessing with a blind exponential backoff (often much shorter than the real quota reset). `call_llm()` and `with_backoff(fn, ...)` (generalized retry for the judge scorer functions, which don't retry on 429 themselves) both use these.

## The system under test — four independently-gradable components
1. **Tools** — `search_catalog`, `check_fine_policy`: deterministic mock functions (no network, reproducible, don't burn quota).
2. **Retrieval** — `TfidfVectorizer` + cosine similarity over a small in-memory policy-snippet corpus (fit once, not per-query — keeps it deterministic and cheap).
3. **Planning** — one LLM call routing to `"tool"`/`"retrieval"`/`"direct"`, forced into JSON via `response_schema` (Gemini's constrained decoding). **Gotcha**: `tool_args` must have named properties, not a bare `{"type":"object"}` — schema-less objects give the constrained decoder no slots to fill and reliably return `{}` regardless of prompt text; the schema, not the prose, governs what constrained decoding can produce. All possible args across both tools are listed as optional fields; the model fills only the relevant ones, and `run_agent` filters down to the callee's actual accepted params before calling.
4. **Final answer** — one LLM call synthesizing a reply from whatever tool/retrieval context was produced.

`run_agent(query)` chains all four into one trace dict — every scorer (deterministic and judge alike) reads from this same structure, keeping component boundaries clean.

## Golden dataset — 20 items, 5 per component
Each item carries whatever a scorer needs: `expected_tool`+`expected_args_contains` (tool_use), `expected_doc_id`+`expected_keywords` (retrieval), `expected_route` (planning), `reference_answer`+`expected_keywords` (final_answer). Domain-owned list — swap tools/corpus/questions for your own project and the rest of the notebook is unchanged.

## Guardrails layer — independent of answer quality
- **Schema check**: `AgentResponse` Pydantic model constrains `route` to a `Literal["tool","retrieval","direct"]` (rejects any hallucinated route), `final_answer` has `min_length`/`max_length`, plus a `field_validator` that catches placeholder answers (`"", "n/a", "todo", "..."`) that would otherwise pass a bare `min_length=1` check.
- **Prompt-injection scan**: one compiled regex (`_INJECTION_RE`) over a list of common jailbreak phrasing families (not exact strings — broad recall on textbook attempts, review against real domain queries before trusting in production). Scanned over **both** the user's query **and every retrieved document** — a poisoned corpus entry is as much an injection vector as a poisoned prompt.
- `guardrail_check(trace)` returns `{passed, flags}` — never silently swallows a problem.

## Deterministic scorers (pure Python, no LLM, milliseconds)
TA note: *LLM-judge scoring is noisy — always pair with at least one deterministic metric.* One per category:
- `tool_match_score`: 1.0 only if right tool **and** every expected arg substring matches (case-insensitive) — no partial credit, any mismatch fails the whole call.
- `retrieval_keyword_hit_score` / `answer_keyword_score`: fraction of golden keywords present in retrieved context / final answer — partial credit allowed.
- `route_match_score`: binary exact match.

## LLM-judge scorers — three independent judges
Rationale: if all three agree an answer is faithful, that's stronger evidence than one judge's opinion; disagreement is a signal to read the transcript by hand rather than trust the number blindly.
- **Ragas**: `Faithfulness` (answer grounded in context) and `ContextPrecisionWithReference` are true LLM judges pointed at Gemini via its OpenAI-compatible endpoint (**must use `AsyncOpenAI`**, not sync `OpenAI` — Ragas's `.ascore()` methods call the async path internally and raise otherwise). `ToolCallAccuracy` is actually **deterministic** (pure name+args comparison, no LLM call) — doubles as a second deterministic check on tool_use. Note: Ragas compares tool args with case-sensitive exact-string equality, so args must be lowercased before comparison to match the golden set's lowercase substrings.
- **DeepEval**: `GEval` builds a custom rubric judge from plain-language criteria (no hand-written judge prompt needed) — used for final-answer correctness against `reference_answer`. Returns `(score, reason)` — the reason is what makes an LLM-judge debuggable instead of a black box.
- **TruLens**: 2.x's app-instrumentation (OTEL `Metric` API) is too heavy for a batch golden-set run, so its feedback-function *providers* are called directly as plain scoring functions — `groundedness_measure_with_cot_reasons` and `context_relevance_with_cot_reasons`, both returning `(score, reasons_dict)` with chain-of-thought reasoning, same spirit as DeepEval's `.reason`.

## Wiring through Langfuse
`langfuse.run_experiment(task=agent_task, evaluators=[component_scorer], data=experiment_data, max_concurrency=1)` — runs the agent on every golden item, dispatches each item to the right mix of deterministic+judge scores for its category (via `component_scorer`), always runs the guardrail check on top regardless of category ("safety isn't quality-conditional"). Every score logged back as a named `Evaluation` — one trace per item, one column per metric in the Langfuse UI.

**Rate budget worked out explicitly**: 2 calls/item for tool_use/planning (agent only), 4/item for retrieval (agent + Ragas context precision + TruLens context relevance), 5/item for final_answer (agent + DeepEval + Ragas faithfulness + TruLens groundedness) = **65 calls total**, all sharing `_pace()`. At 4.5s spacing that's ~5 min best case, but realistically 10-15 min once 429 retries (Gemini's suggested wait is often 30-50s) kick in — the theoretical floor undersells real run time.

**Region gotcha**: Langfuse Cloud EU and US are fully isolated; a project's keys only work against the region it was created in. Signing up doesn't always default to EU — check the URL bar, mismatched `LANGFUSE_HOST` is the #1 cause of a `401`, not a bad key. `auth_check()` fails fast with one clear error instead of a wall of repeated 401s during the run.

**Each judge call individually wrapped in try/except** inside `component_scorer` — under sustained rate limiting a judge can exhaust its retry budget and still fail; without per-call isolation that would raise out of the whole function and discard every score already computed for that item (Python doesn't return partial results on an uncaught exception), including `guardrail_passed`.

**Self-check pattern**: build a per-metric mean table from `result.item_results`, then flag rows where a deterministic score and an LLM judge disagree by >0.4 — those are exactly the rows worth reading by hand. TA note: *tune guardrail thresholds against the golden set, not intuition* — if `guardrail_passed` drags down an otherwise-good category, that's a signal the injection regex is too aggressive for this domain's vocabulary, not that the agent is unsafe.

## Lab B — Package as a FastAPI service
- `/chat` (POST, `ChatRequest{query}` → `ChatResponse{route, final_answer, retrieved_doc_ids}`) wraps `run_agent` + `guardrail_check`; guardrail failures return **HTTP 422 with the actual flags in the body** — rejected requests are visible to the caller, not silently dropped. `ChatResponse` deliberately omits internal trace fields (`tool_call`, `tool_result`, `plan_reasoning`) — not part of the public API contract.
- `/health` — cheap liveness check, no LLM call, never rate-limited.
- **Running uvicorn in a notebook**: `uvicorn.run()` blocks the cell forever, so the server runs in a background daemon thread with its **own fresh event loop**, driven via `loop.run_until_complete(server.serve())` rather than `server.run()` — because `nest_asyncio.apply()` (needed earlier for Ragas' async scorers) patches `asyncio.run()` in a way incompatible with the `loop_factory` argument `server.run()` passes internally.
- **ngrok**: `pyngrok.ngrok.connect(8000, "http")` opens a public tunnel so the same endpoint is reachable from Postman on any machine. Free-tier ngrok URLs change on every tunnel restart — share a Postman Collection, not the URL, so teammates can re-point it later.
- Postman walkthrough: POST to `{public_url}/chat`, raw JSON body `{"query": "..."}`; 200 = clean answer, 422 = guardrail rejection with `flags` explaining why.

## Architecture review write-up template (reusable for Milestone 8)
Sections to fill for the capstone submission: System overview → Components & data flow (table: component / what it does / failure mode if it breaks) → Evaluation results summary (paste the per-metric table, call out any metric below target and what was changed in response — the actual "continuous improvement" part) → Guardrails & safety (what's covered vs. explicitly out of scope — be honest about gaps) → Known limitations (e.g. TF-IDF has no semantic understanding, synonyms miss) → Deployment notes (secrets/env vars, rate-limit handling, logging, rollback plan).

**Capstone tie-in:** Milestone 8. Full pipeline — golden dataset → deterministic scorers → three LLM judges → Langfuse experiment run → guardrails → packaged live public endpoint — is meant to be reused as-is: swap tools/corpus/golden set for the actual ShopSense domain and everything downstream carries over unchanged.
