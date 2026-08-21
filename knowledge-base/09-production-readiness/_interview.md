# 09-production-readiness — interview fire round

### testing-agent-code

- **Q: Why not just eval the agent instead of unit-testing individual nodes?**
  A: Eval measures whether the agent's *behavior* is good against a golden dataset — slower, often non-deterministic, and answers a quality question. Unit tests measure whether a specific piece of code does what you intended — fast, deterministic, and catch a broken router or a crashing parser long before an eval run would even notice. See [[eval-driven-development-mindset]] for the eval side.
- **Q: Why does it matter *where* you patch a shared `call_llm` helper?**
  A: `patch`/`monkeypatch` replace a name in a specific module's namespace, not the function's original definition everywhere it's imported. If two callers each did `from llm_helpers import call_llm`, patching `llm_helpers.call_llm` won't affect a caller that already imported its own local reference — you have to patch the name where the code under test looks it up.

### langfuse-tracing

- **Q: Why does a `generation` span need explicit `usage_details`, when a `span` doesn't?**
  A: Cost only computes from token counts. A plain `span` has no token concept; a `generation` span needs `model` and `usage_details` wired from the actual response object, because the SDK's built-in per-model price table can't reliably resolve every provider-prefixed model name.
- **Q: Why compare traced vs. untraced latency instead of just reporting the traced number?**
  A: Every span costs real wall-clock overhead — object creation, attribute recording, eventual flush. On fast operations that overhead can dominate the numbers; report the untraced median as the system's real latency, and the delta as a separate, also-interesting fact about instrumentation cost.

### privacy-and-pii-handling

- **Q: Why redact "before it leaves the process" rather than in the dashboard/storage layer?**
  A: Once PII reaches a log/trace/storage backend, removing it means finding and scrubbing every copy — the dashboard, backups, any downstream consumer. Stripping it in application memory before transmission means it never exists in those places at all.
- **Q: Why is an allowlist safer than a denylist for what gets logged from a shared state object?**
  A: A denylist has to correctly anticipate every PII-shaped field, including ones added later by someone who doesn't know about the redaction rule. An allowlist inverts the failure mode — a newly added field is blocked by default until someone deliberately marks it safe, rather than leaked by default until someone notices.

### retry-fallback-patterns

- **Q: Why doesn't a retry loop fix a malformed response?**
  A: `retry_if_exception_type` only fires on raised exceptions — malformed data is a successful call that returned the wrong shape, not an exception. Retrying it just re-rolls the same bad odds; it has to be checked and handled as a separate case (fallback), not retried.
- **Q: Why exponential backoff instead of a fixed delay between retries?**
  A: A fixed delay across many clients synchronizes into a thundering herd — everyone retries at the same moment and re-overloads the dependency. Waiting longer each attempt (ideally with jitter) protects a struggling dependency instead of piling onto it.

### circuit-breaker-pattern

- **Q: Why exactly one trial call in `half_open`, not a few?**
  A: `half_open` exists to test recovery without guessing — allowing multiple trial calls risks sending a burst of traffic back at a dependency that's still down, defeating the point of the breaker. One call, and any failure re-opens immediately.
- **Q: When does a circuit breaker help that a retry alone doesn't?**
  A: During a *sustained* outage. Retries still pay the full retry budget (multiple attempts with backoff) on every request against a dead dependency — a breaker stops that spend entirely once it opens, protecting both the caller's latency and the dependency from a retry storm while it's down.

### eval-driven-development-mindset

- **Q: Why can a system with a 100% "final answer correct" score still be broken?**
  A: The final-answer score doesn't tell you whether the layers underneath (tool use, retrieval, planning) were actually right — two wrong steps can still coincidentally land on a correct-looking answer, and you won't find out until the layers diverge on a case that doesn't get lucky.
- **Q: Your LLM judge agrees with human labels 87% of the time. Which disagreement direction should worry you more?**
  A: Judge-says-PASS/human-says-FAIL — that's the judge certifying a bad answer as good, which is invisible unless you specifically audit for it. Judge-says-FAIL/human-says-PASS just costs you a false alarm you'll notice.
- **Q: How is eval different from the unit tests in [[testing-agent-code]]?**
  A: Unit tests check code correctness with the LLM call mocked out — deterministic, pass/fail on logic. Eval checks the *quality of the LLM's actual behavior* against a golden set — probabilistic, scored, and the LLM call is exactly the thing being measured.

### deterministic-scorers

- **Q: Why run a deterministic scorer at all if you already have LLM judges?**
  A: LLM-judge scoring is noisy and can be wrong in ways that are hard to detect on its own — a deterministic scorer gives you a cheap, reproducible independent signal. When the two disagree, that disagreement is exactly the case worth reading by hand.
- **Q: Why does `tool_match_score` give no partial credit but `answer_keyword_score` does?**
  A: A tool call with the wrong argument isn't a partially-correct action — it's the wrong call, full stop. A written answer can legitimately capture most of the required information without literally containing every golden keyword, so partial credit reflects that better.

### llm-judges-eval

- **Q: Why run three separate LLM-judge frameworks instead of picking one?**
  A: Each judge is a model with its own blind spots. If all three independently agree an answer is faithful, that's stronger evidence than any single judge's opinion; when they disagree, that's a specific signal to read the transcript by hand rather than trust any one number.
- **Q: You audit a judge and get 87.5% agreement with human labels. Is that framework good enough to ship?**
  A: The number alone doesn't say — you have to look at *which* direction the disagreements ran. Judge-says-PASS/human-says-FAIL is the expensive direction (bad output certified as good, invisible without an audit); judge-says-FAIL/human-says-PASS just costs a false alarm you'll catch immediately.
- **Q: Why does Ragas's `ToolCallAccuracy` sit inside an "LLM judge" library if it's deterministic?**
  A: Because it scores a different signal (tool-call correctness) that happens not to need a model call — pure name+argument comparison — while the library's other metrics (`Faithfulness`, `ContextPrecision`) genuinely need an LLM to judge semantic entailment. It's grouped by product, not by mechanism.

### guardrails-injection-detection

- **Q: Why scan retrieved documents for injection, not just the user's query?**
  A: Anything the agent treats as trusted context — including a document your own retriever returned — is a vector for an attacker who managed to get content into the corpus. A poisoned document is functionally the same attack as a poisoned prompt.
- **Q: A guardrail blocks 23% of legitimate questions and nobody complains. Is it working?**
  A: Not necessarily — false rejections are the guardrail failure mode nobody files a ticket about. You only find out by measuring the false-rejection rate against a golden set with known-good cases, the same discipline used for eval.
- **Q: Why does a schema constraint on `route` count as a guardrail rather than just data validation?**
  A: Because an out-of-schema route is exactly the kind of hallucination that would otherwise reach code expecting one of a fixed set of values — the guardrail's job here is to fail loud (reject the response) rather than let a fabricated value propagate downstream.

### fastapi-fundamentals

- **Q: Why does FastAPI's async support matter more for an agent endpoint than for a typical CRUD API?**
  A: An agent endpoint spends nearly all its wall-clock time waiting on external I/O — an LLM call, a vector search, a tool call — not doing CPU work. `async def` handlers let one worker serve other requests during that wait instead of blocking on it, which a synchronous WSGI framework can't do without more workers/processes.
- **Q: Why does `ChatResponse` deliberately omit fields like `tool_call` and `plan_reasoning` that the trace dict contains?**
  A: A `response_model` isn't just documentation — it filters what actually gets serialized back to the caller. Internal trace fields aren't part of the public API contract, and leaving them in `response_model` would silently promote implementation detail into a stable-looking API surface.

### deployment-packaging

- **Q: Why can't you just share the ngrok URL with teammates once and be done?**
  A: Free-tier ngrok URLs are ephemeral — they change every time the tunnel restarts. Sharing a Postman Collection (which re-points to whatever URL is current) survives restarts; sharing a bare URL doesn't.
- **Q: What's the actual difference between "the demo runs" and "ready to ship," per the course framing?**
  A: A demo proves the agent can produce a right answer once. Ready-to-ship is a documented package — the agent's job and limits, an evaluation report, an operational runbook, and honestly-stated known limitations — that a team can sign off on, not just a working process on someone's laptop.
- **Q: Why validate required env vars at process startup instead of wherever they're first used?**
  A: A config error caught at startup fails loud and immediately, before any traffic is served. The same error caught lazily on first use surfaces as a random user's request failing, possibly hours after deploy — see [[env-secrets-and-config]].

### putting-it-all-together

- **Q: Walk me through what happens between a user's message arriving and a response going back, for a system with RAG, tools, and multi-agent orchestration.**
  A: Intake validates the request at the API boundary; identity comes from the session, never the message text; a planning step routes to tool and/or retrieval; tools execute deterministically while retrieval embeds, searches, and reranks; an orchestration layer coordinates multiple specialized agents and handles any human-in-the-loop step; guardrails check the final answer independent of whether it's *good*; every hop is a traced span under one trace ID; and the API layer returns a filtered response — while eval and reliability protections (retries, circuit breakers, golden-set scoring) sit around the whole path rather than on it.
  A: (See the Core mechanics numbered list above for the full nine-hop breakdown.)
- **Q: Why is the trace dict from the eval notebook the same shape referenced in the tracing and guardrail layers?**
  A: Keeping one trace structure that every layer writes into and every scorer/guardrail reads from is what keeps component boundaries clean — a change to how tool calls are recorded doesn't require updating three separate representations, and it's exactly what makes a request both debuggable (tracing) and gradable (eval) from the same object.

## Harder / real-interview-style

Grounded in 2026 web-researched interview material on LLM observability, eval/guardrails, and resilience patterns (search terms: "LLM observability eval guardrails interview questions production AI agents 2026", "circuit breaker retry pattern interview questions distributed systems production incident"), cross-referenced against [Confident AI's AI agent observability guide](https://www.confident-ai.com/blog/ai-agent-observability) and general microservices resilience-pattern interview coverage, plus this stage's own pages — [[testing-agent-code]], [[langfuse-tracing]], [[privacy-and-pii-handling]], [[retry-fallback-patterns]], [[circuit-breaker-pattern]], [[eval-driven-development-mindset]], [[deterministic-scorers]], [[llm-judges-eval]], [[guardrails-injection-detection]], [[fastapi-fundamentals]], [[deployment-packaging]]. This repo's labs use Langfuse SDK v4 (`get_client()`, `start_as_current_observation`) — treat older `Langfuse()`/decorator-only tutorials as describing a superseded API surface.

### Testing vs. eval boundary

- **Q: A PR passes all unit tests and the CI eval suite shows no regression, but a customer reports the agent gave a policy-violating answer in production the same day. How is this possible, and what does it tell you about your test/eval coverage?**
  A: Unit tests check code correctness with the LLM mocked out, and eval checks quality against a fixed golden set — neither is a live production monitor. The gap is coverage: the golden set didn't contain a case resembling what the customer hit, and no unit test encodes "policy violations are impossible" because that's precisely the LLM-generated behavior unit tests intentionally don't exercise. This is the argument for online eval/production tracing (per [[langfuse-tracing]]) layered on top of offline unit tests and golden-set eval — the golden set catches known failure shapes, but only live tracing plus sampling-based review catches a shape nobody wrote a golden case for yet.

- **Q: You mock `call_llm` in a test and it silently doesn't take effect — the test hits the real API. What's the most likely cause, and why doesn't the mocking library warn you?**
  A: `patch`/`monkeypatch` replace a name in a specific module's namespace, not the function's original definition everywhere it's referenced — if the code under test did `from llm_helpers import call_llm` into its own module namespace, patching `llm_helpers.call_llm` doesn't touch that already-imported local reference. There's no warning because, from the patching library's point of view, it successfully patched exactly the name it was told to — the bug is a mismatch between where the name is *defined* and where the code under test actually *looks it up*, which is a Python import-semantics issue, not a testing-library defect.

### Tracing, cost, and silent failures

- **Q: A team adds Langfuse tracing broadly by wrapping every function with a tracing decorator that `repr()`s its arguments onto the span. Weeks later, a security review finds full customer chat transcripts sitting in the tracing dashboard's default retention. How did this happen, and what's the actual fix?**
  A: A blanket instrumentation decorator has no concept of which arguments are sensitive — it captures everything indiscriminately, and raw chat text (which routinely contains PII, order details, account info) ends up on spans by default with no explicit choice ever made to put it there. Per [[langfuse-tracing]] and [[privacy-and-pii-handling]], the fix is redacting or allowlisting what gets attached to a span *before* it leaves the process — an allowlist of specifically-approved fields, not a denylist of "known bad" ones — because once PII reaches the tracing backend, scrubbing it means finding and removing every copy (dashboard, backups, downstream consumers), not just fixing the code going forward.

- **Q: Your agent's per-call cost dashboard shows a sudden 40% jump with no corresponding traffic increase. Walk through how you'd diagnose it using tracing data alone.**
  A: Start from the `generation` spans specifically, since only those carry `usage_details` and `model` — a cost anomaly usually traces to either a model routing change (calls silently falling back to a pricier model), a prompt-length regression (context growing per call, e.g. a broken compression step per [[context-compression]]), or a retry storm (failed calls being retried more than expected, multiplying billed tokens per logical request). Comparing token counts and model names per trace before and after the jump, rather than just the aggregate dollar figure, is what actually localizes which of those three it is — the dashboard total alone can't distinguish "more expensive calls" from "more calls."

- **Q: Why would you deliberately run a small number of canary queries against a production RAG system on a schedule, even when nothing has changed and no alerts have fired?**
  A: Canary queries exist to catch *silent* failures — a corpus re-index that quietly drops a document class, a retriever regressing on a query type nobody's asked recently, or a refusal-rate creeping up in either direction (over-refusing legitimate queries, or under-refusing ones that should be blocked) — none of which necessarily throws an exception or fails a health check. A system can be "up" by every infrastructure metric while silently answering worse, and a scheduled canary is one of the only ways to detect that class of failure before a customer does, rather than relying on someone noticing a metric drift after the fact.

### Retry, fallback, and circuit-breaker incident scenarios

- **Q: On-call gets paged: a downstream LLM provider is having a partial outage, and your service's latency has spiked to 30x normal even though the error rate is only slightly elevated. Retries are configured with exponential backoff. What's actually happening, and is the retry config itself the bug?**
  A: This is the classic failure mode retries alone don't solve: during a *sustained* outage, every request still pays the full retry budget (several attempts with growing backoff) against a dependency that's mostly failing, so overall latency balloons even though each individual retry is "working as configured." The retry config isn't wrong in isolation — the missing piece is a circuit breaker that stops paying the retry cost entirely once failures cross a threshold, short-circuiting to a fallback (cached response, degraded mode, or a fast fail) instead of exhausting the retry budget on every request during a known-bad window, per [[circuit-breaker-pattern]].

- **Q: Your circuit breaker's `half_open` state sends one trial call to test recovery, and it happens to fail due to an unrelated transient blip — the breaker re-opens and stays open for another full cooldown window even though the dependency was actually fine. Is this a bug, and how would you tune around it?**
  A: This is expected, conservative-by-design behavior, not a bug — `half_open` intentionally sends exactly one trial call rather than several, because allowing a burst of trial traffic risks re-overloading a dependency that might still be struggling, which would defeat the point of the breaker. The tuning lever isn't "send more trial calls" (that reintroduces the risk the single-call design avoids); it's tuning the cooldown duration and, separately, distinguishing transient-blip failures from sustained-outage failures in the trial call's own retry policy — a trial call itself can have a small retry budget before being counted as a breaker-relevant failure.

- **Q: A retry loop is correctly catching exceptions and retrying, but a malformed (successfully returned, schema-invalid) LLM response keeps reaching downstream code unhandled. Why doesn't the retry logic catch this?**
  A: `retry_if_exception_type`-style retry logic only fires on *raised exceptions* — a malformed response is a successful call that returned the wrong shape, not an exception, so the retry decorator never sees it as a failure to retry. Retrying it anyway would just re-roll the same bad odds on a model that's producing malformed output for a structural reason (bad prompt, wrong schema, a model change) — this has to be caught and handled as a distinct fallback/validation case (parse, validate against schema, then decide retry-vs-repair-vs-fail), not folded into the same retry path as network errors.

### Eval, guardrails, and judge-agreement scenarios

- **Q: Your LLM judge reports 96% pass rate on a golden set, matching the previous release. Two weeks later, a support escalation reveals the agent has been giving a subtly wrong answer to a common question the whole time. How did the eval suite miss this?**
  A: Either the golden set never contained a case shaped like the one that failed (coverage gap, not a judge-accuracy problem), or the judge is systematically agreeing with a wrong-but-plausible-sounding answer — i.e. the dangerous disagreement direction, judge-says-PASS on a case a human would mark FAIL. The fix for the first is expanding golden-set coverage from real production traffic, not just hand-authored cases; the fix for the second is periodically auditing judge output against human labels specifically looking for that PASS/FAIL-human-disagrees direction, since it's invisible unless you deliberately look for it — a stable aggregate pass rate over time is not the same claim as "the judge is still accurate."

- **Q: A guardrail that blocks prompt-injection attempts shows zero user complaints in a month. Is that evidence it's working correctly?**
  A: Not by itself — a guardrail's most dangerous failure mode, over-blocking legitimate queries, doesn't generate complaints the way under-blocking does, because a rejected user usually just leaves rather than filing a ticket explaining what they wanted. "Zero complaints" is consistent with either "working well" or "silently rejecting a meaningful fraction of legitimate traffic" — the only way to distinguish them is measuring false-rejection rate against a golden set of known-good queries, the same discipline used for eval scoring, not inferring correctness from an absence of tickets.

- **Q: Why would a production team run a deterministic scorer *and* three separate LLM-judge frameworks (e.g. Ragas, DeepEval, TruLens) on the same eval set, instead of picking the strongest one?**
  A: Each LLM judge is itself a model with its own blind spots and can be systematically wrong in ways that are hard to detect from its own output alone; a deterministic scorer (exact tool-call match, keyword presence) provides a cheap, reproducible independent signal that doesn't share those blind spots. When multiple independent judges agree an answer is faithful, that's meaningfully stronger evidence than any single judge's opinion; when they disagree, that specific disagreement is the highest-value case to read by hand — the point isn't redundancy for its own sake, it's converting "trust one number" into "trust a pattern of agreement, and specifically investigate disagreement."

### FastAPI, deployment, and shipping decisions

- **Q: An agent's FastAPI endpoint works fine under a light load test but falls over under real concurrent traffic — requests start queuing and timing out even though CPU usage looks low. What's the likely cause?**
  A: If the handlers are defined `def` instead of `async def` for I/O-bound work (LLM calls, vector search, tool calls), a synchronous handler blocks its worker for the full duration of each external call, and low CPU usage with high queuing is exactly the signature of I/O-bound blocking rather than CPU exhaustion — the fix is `async def` handlers with `await`ed I/O calls so one worker can serve other requests during the wait, which is specifically why FastAPI's async support matters more for an agent endpoint than for a typical CRUD API doing mostly synchronous DB reads.

- **Q: What's the concrete difference between "the demo works" and being ready to hand this system to another team, and why does an interviewer care about this distinction specifically?**
  A: A demo proves the agent can produce a correct-looking answer once, under conditions the demo-runner controls; "ready to ship" means a documented package — the agent's actual job and stated limits, an evaluation report with real numbers, an operational runbook (what to do when it fails, who's paged), and honestly-stated known limitations — that another team can operate without the original author present. Interviewers ask this because it's the fastest way to distinguish someone who's built a working prototype from someone who's actually operated a system in production and knows what breaks when the original builder isn't in the room.

- **Q: Why validate required environment variables (API keys, DB URLs) at process startup rather than lazily at first use, and what's the actual production cost of getting this wrong?**
  A: A startup check fails loud and immediately, before any traffic is served, so a bad deploy is caught by the deploy process itself. A lazy check surfaces as a specific user's request failing at whatever point that code path first runs — which could be hours after deploy, for a rarely-hit code path, making the failure much harder to correlate back to "we deployed a config error this morning" — see [[env-secrets-and-config]]. The production cost isn't just a slower fix; it's a failure that looks like an intermittent bug rather than what it actually is, a deterministic config error that's only intermittent in *when it's first observed*.
