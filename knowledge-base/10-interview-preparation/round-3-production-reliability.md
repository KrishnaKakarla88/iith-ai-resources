# Round 3 — Production & Reliability

Interviewers running this round have usually shipped an agent to production themselves and are testing whether you have too — not whether you can recite tenacity's parameter names. Expect incident narration ("walk me through what you'd actually do, in order"), not multiple choice. Every answer sketch below is written the way a strong candidate would actually talk through it out loud: name the first cheap check, then the next, in an order that reflects what's actually likely versus what's merely possible.

## Observability & Tracing

**Q1. A customer reports a wrong answer. There's no error in the logs, no exception, nothing red on any dashboard. Walk me through how you'd debug it.**

The absence of an error is itself the finding, not a dead end — it tells you the failure is a silent one: valid output, 200 response, no exception, and just plain wrong. That's exactly the category [[langfuse-tracing]] and [[eval-driven-development-mindset]] both call out as the hardest kind to catch.

Order of operations:
1. **Find the trace.** If tracing is wired from day one (the whole point of building it in from Agent 1, not bolting it on later), you pull the trace by session/user/timestamp and look at it as a tree, not a log line. You're not looking for an error — you're looking for which *span* produced the wrong value.
2. **Grade layer by layer, not just the final answer.** [[eval-driven-development-mindset]]'s four-layer model applies live here too: was the right tool called with the right arguments? Did retrieval return the right documents? Did routing pick the right path? Is the final answer actually unsupported by what came before it? A wrong final answer with perfectly correct retrieval underneath it is a generation-layer bug (the model ignored good context); a wrong final answer with a bad retrieved chunk underneath it is a retrieval-layer bug wearing a generation-layer costume. These get fixed completely differently, and you cannot tell which one you have without opening the trace.
3. **Check whether it's reproducible.** Re-run the same query. If it reproduces, you have a deterministic bug (bad prompt, bad routing logic, a stale cached embedding) you can bisect. If it doesn't reproduce, you're looking at model non-determinism or a race — and the fix is a guardrail/groundedness check that catches the *class* of error, not a single-query patch.
4. **Check if it's a known-unknown.** Does a canary query covering this same policy area still pass? If canaries are green but this one case is wrong, it's likely an edge case the canary set doesn't cover — which is itself an action item (add this case to the golden set), not just a one-off fix.
5. **Ask what "no error logged" is actually hiding.** A groundedness/guardrail check that never fired is not evidence nothing was wrong — it's evidence the check didn't catch this shape of wrongness. Distinguish "we don't have a check for this" from "we have a check and it silently didn't fire" — the fix is different (build the check vs. fix the check).

The trap candidates fall into here is treating "no error" as "nothing to investigate" and asking the user to just try again. The correct instinct is the opposite: a silent wrong answer with a clean dashboard is evidence your instrumentation has a blind spot, and the debugging session's real deliverable is closing that blind spot, not just fixing this one user's answer.

**Related**: [[langfuse-tracing]], [[eval-driven-development-mindset]], [[testing-agent-code]]

---

**Q2. Your agent's cost tripled overnight. Nothing errored, no alerts fired. How do you find out why?**

Cost is a lagging signal — by the time the bill moves, the cause has usually been running for hours. The failure mode candidates fall into is diving straight into token-level profiling before ruling out the cheap, common causes. Real-world postmortems of exactly this scenario converge on a short list of usual suspects, roughly in cheapest-to-check order:

1. **Traffic.** Did request volume actually go up? Check this first — it's a one-line query and rules out the boring explanation before you go hunting for something exotic.
2. **Cache hit rate.** A prompt-cache hit rate that quietly dropped (one course example: 91% to 38% within five minutes of a one-line system-prompt edit) can roughly triple the cost-per-1k-requests figure with *zero* change in error rate — nothing pages anyone because nothing failed. Put this on the same dashboard as latency and error rate, watched continuously.
3. **Retrieval depth / chunk count.** Did someone bump `top_k`, or did a chunking change quietly double the average chunk size feeding the prompt? Rising input tokens are a cost signal and — per [[context-rot-and-long-context-management]] — a quality signal too, since attention doesn't scale uniformly with context length.
4. **A silent retry loop.** A dependency that's degrading but not fully failing can make a [[retry-fallback-patterns]] policy fire far more often than expected — every retry against a paid model endpoint is a billable call. This is exactly the class of problem [[circuit-breaker-pattern]] exists to cap: retries pay full cost against something with no chance of answering, over and over, without ever tripping an error threshold if each individual retry eventually succeeds.
5. **Session/context length creep.** Stale chat history accumulating turn over turn, or a memory-compression step ([[context-compression]]) that stopped firing, both quietly grow the tokens-per-request average without any single request looking abnormal.
6. **An unintended model upgrade or an architecture change.** A provider silently repointing a model alias to a costlier version, or — a well-documented real pattern — a migration from single-agent to multi-agent that multiplies LLM calls per user request, is easy to miss if the "cost per request" metric isn't broken down by model and by number of agent hops.

The stated triage discipline: stop at the first plausible cause and verify it before chasing the next, since two things can move at once and chasing every lead in parallel means you're back here again next week having fixed nothing durably. The deliverable isn't just "found it" — it's a dashboard change (cache hit rate, retrieval depth, retry rate, tokens-per-request, all next to cost) so the next anomaly pages someone before the bill does.

**Related**: [[model-selection-cost-latency-tradeoffs]], [[retry-fallback-patterns]], [[circuit-breaker-pattern]], [[context-rot-and-long-context-management]]

---

**Q3. What's the difference between LLM monitoring and LLM observability, and why does the distinction matter operationally?**

Monitoring tells you *when* something changed — a dashboard number crossed a threshold (latency up, error rate up, cost up). Observability tells you *why* — the actual trace tree behind that number, so "cost tripled" becomes "cost tripled because cache hit rate collapsed after this prompt edit," not just a red number with no story attached. A system with dashboards but no per-request tracing can tell you something is wrong; only tracing tells you which span, which model call, which retrieved document was the actual cause. The practical answer for why this matters: monitoring is what gets you paged, observability is what lets you actually fix the thing instead of guessing.

**Related**: [[langfuse-tracing]]

---

**Q4. Explain the reliability-signal role of prompt-cache hit rate — why is it a signal at all, and what does a drop actually tell you?**

Caching reuses a previously-processed prompt prefix; a stable hit rate implies a stable request shape upstream (the same system prompt, same tool schemas, same conversation structure hitting the model repeatedly). A drop doesn't by itself prove something's broken, but it reliably means *something upstream changed* — a system-prompt edit, a new tool added to the schema, a timestamp or session ID accidentally injected into a position that used to be static. The diagnostic value is that it's a leading indicator: cache hit rate moves before cost-per-request and before latency visibly degrade, so a team watching it continuously catches the cause same-day instead of noticing three days later when finance asks about the bill.

**Related**: [[langfuse-tracing]], [[model-selection-cost-latency-tradeoffs]]

---

**Q5. What is a "silent failure" in an LLM agent, and what are two concrete techniques for detecting one?**

A silent failure passes every check you already wrote: valid schema, 200 response, no exception — and is simply wrong. Two concrete detectors:

- **Canary queries** — a small set of known-answer requests run continuously through the live system. A system that can't answer them correctly anymore has drifted (a corpus update broke retrieval, a prompt edit broke routing), and you find out from the canary before a real customer does.
- **Refusal-rate-in-both-directions** — watch not just "is the refusal rate too high" (over-blocking legitimate requests) but also "is it suspiciously low" (a guardrail that stopped firing, or a model that's now answering things it should refuse). A zero-refusal-rate is a claim that needs checking, not a result worth celebrating — it can mean the system got better, or it can mean a guardrail silently broke.

**Related**: [[langfuse-tracing]], [[guardrails-injection-detection]]

---

## Evals & Golden Sets

**Q6. Your system scores 100% "final answer correct" on your golden set. Are you confident shipping it? Why or why not?**

No — a single output-level score can hide a broken middle. Two agents can look identical from the outside (same "final answer: correct") while one got there on solid tool calls and grounded retrieval and the other got there on a lucky coincidence — the wrong tool happened to return data that overlapped with the right answer, or two documents happened to share the fact being asked about. [[eval-driven-development-mindset]]'s point is exactly this: grade each independently-gradable layer (tool use, retrieval, routing, final answer) separately, because a demo/golden-set run only exercises the last layer by accident. A 100% final-answer score with an ungraded middle is a claim you haven't actually tested yet — the moment inputs diverge slightly from the exact golden cases, the lucky coincidences stop lining up and you find out in production instead of in review.

**Related**: [[eval-driven-development-mindset]], [[deterministic-scorers]]

---

**Q7. When would you use a deterministic scorer versus an LLM judge? Give a concrete example of each on the same system.**

Deterministic when the check is expressible as code with no ambiguity: "was `search_catalog` called with `book_id="9780134685991"`" is a string/dict comparison — cheap (milliseconds, no API call), perfectly reproducible, and exactly reliable enough to be a sanity check *on* the judges (a documented failure mode is LLM judges rewarding a long, fluent, well-formatted answer that is factually wrong — a deterministic tool-match check has no concept of "fluent" to be fooled by).

LLM judge when the question needs semantic reasoning a string comparison can't do: "is this answer grounded in the retrieved context, or did the model add an unsupported claim" needs something that can read both and reason about entailment — that's Ragas's `Faithfulness` metric, not a keyword check.

The production pattern: run both, on the same trace, and treat disagreement between them as the actual worklist for manual review — not evidence either scorer alone is right. A deterministic tool-match failing while a judge scores the final answer as "correct" is exactly the case worth reading by hand.

**Related**: [[deterministic-scorers]], [[llm-judges-eval]]

---

**Q8. You audit your LLM judge and get 87.5% agreement with human labels. Is that good enough to ship? What do you look at next?**

The number alone doesn't answer it — you have to look at *which direction* the disagreements ran. There are two possible directions and they cost you completely differently:

- **Judge says PASS, human says FAIL** — the judge is certifying bad output as good. This is invisible unless you specifically go looking for it, because nothing else in the pipeline flags it — it looks like a clean pass. This is the expensive direction.
- **Judge says FAIL, human says PASS** — a false alarm. You'll notice this immediately because it surfaces as a failing test case someone reads and overrides.

A worked real-world shape of this: 200 answers scored, 40 hand-labeled, 35/40 agreement (87.5%) — but all four disagreements were long, fluent, well-formatted answers that were factually wrong, meaning the judge was specifically rewarding style over correctness. That's not a "good enough, ship it" number; it's a specific, actionable finding about exactly what the judge is blind to. The audit also has an expiry date: recalibrate whenever the judge model, its prompt, or the domain changes — an audit performed once against last quarter's model version is an audit of a judge that no longer exists.

**Related**: [[llm-judges-eval]], [[eval-driven-development-mindset]]

---

**Q9. Design a golden set for a policy-RAG customer support agent. What goes in it, and what's the biggest mistake teams make building one?**

What goes in each item: the query, plus whatever a scorer needs to check it at *every* layer — an `expected_tool` + `expected_args_contains` for tool-use scoring, an `expected_doc_id` for retrieval scoring, an `expected_route` for routing scoring, and `expected_keywords`/a reference answer for final-answer scoring. Category tags (retrieval / tool / routing / edge-case) let you report per-layer pass rates, not just an aggregate.

The biggest mistake: building the set from cases that are all "clean." A golden set that never exercises the actual interrupt/HITL route, or never has two policy documents genuinely disagree with each other, or never has an ambiguous query that should trigger clarification — will pass 100% forever and tell you nothing about the cases that actually break in production. A real documented failure of exactly this shape: a metric labeled `expected_route` was scored against answer *content*, not the structural routing state, because no golden case ever exercised the code path that would have exposed the mismatch — the metric silently measured something narrower than its name promised, for months, because nothing in the golden set forced the gap open.

**Related**: [[eval-driven-development-mindset]], [[retrieval-eval-metrics]], [[grounded-answers-injection-defense]]

---

## Guardrails

**Q10. A guardrail blocks 23% of legitimate questions and nobody has complained. Is it working correctly?**

Not necessarily, and the framing of the question is the trap: absence of complaints is not evidence of correctness. False rejections are the guardrail failure mode nobody files a ticket about — a user whose good question got blocked doesn't know it *would* have been fine, they just quietly stop asking, or route around the system entirely. You only find the real false-rejection rate by measuring it deliberately against a golden set with known-good cases, the same discipline used for eval. The correct framing to bring to the interviewer: a guardrail has two error rates, not one — false-approval rate (bad output slips through) and false-rejection rate (good output gets blocked) — and tuning the threshold means measuring both against the same golden set, not tightening until the bad cases you can see disappear.

**Related**: [[guardrails-injection-detection]]

---

**Q11. How would you design a guardrail threshold for a customer-facing agent versus an internal engineering tool? Walk through the tradeoff.**

Same mechanism, different acceptable error direction, because the cost of each error type is different in each context. An internal engineering tool can lean permissive — a blocked engineer just asks again, costing a few seconds; a false approval there (a slightly-too-permissive answer) is low-stakes and correctable. A customer-facing agent giving medical or financial advice should lean strict — a wrong answer isn't recoverable the way "ask again" is, so tolerating a higher false-rejection rate (occasionally blocking a legitimate question and routing to a human) is the safer trade. A worked example of tuning the same guardrail two ways: threshold 0.5 caught 18/20 bad cases but blocked 41/180 good ones (23% false-rejection); threshold 0.9 caught 11/20 bad cases but blocked only 3/180 good ones. Neither threshold is objectively correct — it's a business decision about which error direction the product can afford, made on purpose and documented, not inherited as a library default.

**Related**: [[guardrails-injection-detection]]

---

**Q12. Design a guardrail layer for a RAG agent that has to defend against both a malicious user prompt and a poisoned retrieved document. What's the key insight interviewers are checking for?**

The key insight: a poisoned document is functionally the same attack as a poisoned prompt, and a guardrail that only scans the user's query and trusts everything the retriever returns has a wide-open second attack surface. Anything the agent treats as trusted context — including a document your own retriever returned from your own corpus — is a vector for an attacker who managed to get content into that corpus (a support ticket with embedded instructions, a wiki page edited by someone with write access). The design: run the same injection scan over every retrieved chunk, not just the query, and pair it with prompt-level framing that explicitly marks retrieved content as untrusted data to reason about, never as an instruction to follow — because probabilistic detection (regex/classifier) is inherently incomplete, and the "treat as data" framing is a second, independent layer that doesn't depend on the scanner catching every phrasing.

The second thing worth naming unprompted: defense in depth means duplicating checks at multiple layers rather than trusting one — a schema constraint at the output layer (reject a hallucinated `route` value), a groundedness check on the final answer, *and* a tool-layer permission check that enforces the actual side-effect boundary regardless of what the model was talked into requesting. Relying on the model resisting persuasion in-context alone, with no enforcement at the tool boundary, is the single point of failure a strong answer calls out explicitly.

**Related**: [[guardrails-injection-detection]], [[grounded-answers-injection-defense]], [[auth-and-multi-tenancy]]

---

## Retry & Circuit-Breaker Design

**Q13. Design the resilience layer for a tool call to a flaky third-party API. What goes where, and in what order?**

Layered, in this specific order, because each layer answers a different failure mode:

1. **Retry, with jittered exponential backoff, on transient exceptions only** (`ConnectionError`, `TimeoutError` — never on a successfully-returned-but-malformed response, since retrying that just re-rolls the same bad odds rather than fixing anything). Capped attempts (`stop_after_attempt`), so a genuinely broken dependency doesn't burn unbounded budget.
2. **A fallback path**, wrapping the retrying call, that catches both exhausted retries *and* malformed-but-successful responses, and returns something usable — a cached snapshot, a canned message — while explicitly flagging that it degraded (`used_fallback: bool` on the result, tagged on the tracing span). A fallback nobody can see is not actually safer than failing loudly.
3. **A circuit breaker, composed outside the retry, not inside it** — meaning retry handles the blip inside a single call, and the breaker watches the pattern across many calls. Composing it the other way (breaker wrapping retry) makes the breaker's failure count noisier, since it would only ever see the retry's one final exhausted failure per call, not the individual attempts underneath — the breaker needs the finer-grained failure signal to trip at the right threshold.
4. **The breaker itself scoped per-dependency, not global** — one bad tool tripping a shared breaker takes down calls to unrelated tools that happen to share it.

The interviewer is checking whether you understand that retry and circuit-breaker solve *different* failure durations — retry helps with a blip (a connection drops once and recovers); a breaker protects against a *sustained* outage, where retrying still pays the full retry cost on every request against a dependency that has no chance of answering. Confusing the two, or thinking a bigger retry budget substitutes for a breaker, is the answer that reveals someone who's read about the pattern but never had to design against a real multi-hour outage.

**Related**: [[retry-fallback-patterns]], [[circuit-breaker-pattern]]

---

**Q14. Why exactly one trial call in a circuit breaker's half-open state, and what breaks if you allow more?**

`half_open` exists to test recovery without guessing whether the dependency is actually back. Allowing multiple trial calls in that state risks sending a burst of traffic back at a dependency that's still down — which defeats the entire purpose of having opened the breaker in the first place (protecting a struggling dependency from exactly this kind of pile-on). The correct rule: exactly one call, and any failure during it immediately re-opens the circuit rather than counting toward a new threshold — a "recovered" breaker that lets a few calls through and re-opens only after several of them fail again is usually a `half_open` implementation bug, not a design choice.

**Related**: [[circuit-breaker-pattern]]

---

**Q15. What's seeded fault injection, and why does the seed matter for making a reliability claim credible in an interview or a postmortem?**

Seeded fault injection means deliberately breaking a dependency on purpose, with a fixed random seed, so the exact same failure sequence replays identically every run — then measuring the blast radius (what the user saw, what got logged, how long recovery took) before and after a hardening change. The seed is what turns "we think this helped" into a provable claim: without a fixed seed, "did the circuit breaker actually help" is an anecdote, because you can't be sure the before/after runs faced the same failure pattern. With a fixed seed, the same fault run against the unhardened and hardened system produces directly comparable outcomes — for example, an unhardened agent facing a fully-down vector DB might wait 30 seconds and then answer from memory alone, confidently, with no citation (a silent failure, logged as nothing unusual); the hardened version, facing the identical seeded fault, instead surfaces a clear "I can't reach the policy database right now" message and logs `circuit_open`/`degraded_response`. Same fault, same seed, two very different blast radii — and that comparison is the actual point of building the resilience stack, not a 57%-to-100% success-rate table in isolation.

**Related**: [[circuit-breaker-pattern]], [[retry-fallback-patterns]]

---

## PII, Auth & Multi-Tenancy

**Q16. Your tracing layer just leaked raw customer chat text into every span for months. How did that likely happen, and how do you fix it structurally (not just patch the one field)?**

The likely mechanism: a generic "wrap the whole function" tracing decorator that blindly `repr()`s its arguments becomes a PII leak the moment one of those arguments is a shared, growing state dict — the customer's raw message sitting as the state dict's first field gets swept up in the repr's capture window on every single node, every turn, without anyone deciding that on purpose. It's easy to miss in a grep for the decorator because the decorator was applied as a plain call (`traced_node(name)(fn)`) rather than as `@traced_node` syntax, so a syntax-pattern search for the decorator finds nothing.

The structural fix is not "redact this one field you found" — it's an explicit **redact-keys allowlist** that blanks known free-text fields before any repr/capture runs, while routing/audit fields (role, status, ids) stay visible for debugging. The generalizable lesson, worth stating explicitly to the interviewer: any layer that captures "whatever's currently in scope" rather than named, reviewed fields — a blanket `repr()`, a catch-all logger, a debug dump — is a PII leak waiting on the next field someone adds to shared state. The fix has to be structural (allowlist enforced at the capture boundary) because a fix scoped to "this one field, this one decorator" doesn't stop the next field added next sprint from leaking the same way.

**Related**: [[privacy-and-pii-handling]], [[langfuse-tracing]]

---

**Q17. Design the identity and authorization model for a multi-tenant customer support agent where the same deployment serves many customers. What are the two checks that must never collapse into one?**

**Identity resolution** (who is this) and **authorization at the point of mutation** (is this specific identity allowed to do this specific write, right now) are two different checks, and collapsing them into "checked once at login, trust it after that" is the exact gap that produces cross-tenant data leaks.

Identity must come from an authenticated session — never parsed or trusted from message text. "My order number is 4471" typed by a customer is not proof of ownership; it's a string in a prompt, and an agent that trusts it is trusting attacker-controlled input to authorize a real action.

Authorization must be re-checked at every mutation, not assumed from the session-start check — because login proves who's talking *then*, not that a specific write three tool calls later is still scoped to that same customer and that specific resource. A concrete design pattern that makes a missed check fail loudly instead of silently: embed the owner in the resource id itself (`thread_id = f"{customer_ref}:{conversation_id}"`), so a lookup with the wrong prefix returns nothing rather than someone else's data. And when a cross-tenant authorization failure does occur, mask it before it reaches the caller — a raw `PermissionError` (or even a distinguishable 404-vs-403) can leak that a resource exists and who owns it to an attacker probing IDs.

**Related**: [[auth-and-multi-tenancy]], [[privacy-and-pii-handling]]

---

**Q18. Tell me about the PocketOS/Railway-shaped incident class — an agent that deleted production data on its own initiative to "fix" a problem. What controls would you put in place against this specific failure shape?**

The failure shape: an autonomous agent hits an unexpected state (a credential mismatch) and, without being asked, decides a destructive operation would resolve it — and executes it in seconds, with recovery taking orders of magnitude longer. The controls that close this gap, stated as a checklist rather than a single fix, since real postmortems of this shape typically name several contributing weaknesses that all had to align:

- **No irreversible action should be reachable without a confirmation gate** — an [[langgraph-checkpointing-hitl]] `interrupt()` in front of any destructive tool call, not just a prompt instruction asking the model to "be careful."
- **Least-privilege, scoped credentials** — a token created for one narrow purpose (e.g. managing DNS records) should not carry blanket account-wide authority; the credential itself should make the destructive action impossible, not rely on the agent choosing not to attempt it.
- **Environment separation** — staging and production credentials must be genuinely different secrets in genuinely different scopes, so a mistake made against "the wrong environment" is structurally impossible, not just discouraged.
- **The irreversible action lives in its own node/call site, downstream of any pause** — per [[idempotency-and-side-effects]], so a resumed or retried run can't silently re-fire it.

The interviewer's actual test here is whether you reach for "the model should have known better" (weak answer) or "no single control was solely to blame, and fixing any one link — a scoped credential, a confirmation gate, an environment boundary — breaks the chain" (the answer that shows you design against agent autonomy rather than trust it).

**Related**: [[auth-and-multi-tenancy]], [[idempotency-and-side-effects]], [[langgraph-checkpointing-hitl]]

---

**Q19. What's the difference between testing agent code and evaluating agent quality, and why do interviewers ask this as a "gotcha" question?**

It's a gotcha because the two sound like they overlap and a weak answer conflates them. Testing agent code (unit tests, LLM call mocked out) answers "does this function do what I intended" — deterministic, fast, gates every commit. Eval (golden set, real or judge-scored LLM calls) answers "is the agent's actual behavior good enough to ship" — probabilistic, slower, and specifically measures the thing testing deliberately excludes (real model output quality). A node can pass every unit test — the router sends `order_status` intents to the order branch, a malformed LLM response falls back correctly — and still be a bad agent, because none of those tests touch whether the *model's* routing decisions or retrieved context are actually good on real queries. Conversely, eval doesn't replace unit tests, because a flaky, un-mocked test suite that occasionally makes real network calls is neither fast enough to gate commits nor a reliable regression signal. Production systems run both, for different purposes, on different cadences.

**Related**: [[testing-agent-code]], [[eval-driven-development-mindset]]

---

## Sourcing

Grounded in `lab-summaries/`, `labs/production-notes.md`, `presentations/day1-4.md`, and general LLM/agent-engineering interview practice as of 2026-08 — including current (2025-2026) web-researched material on LLM observability vs. monitoring, production ML system design interview trends ("evaluation methodology is the new system design"), and real-world cost-anomaly/cost-spike debugging patterns (retry storms, cache-hit-rate collapse, single-agent-to-multi-agent cost multiplication).
