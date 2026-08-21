# Round 2: System design

System design is the highest-weighted round in most current AI/LLM agent-engineer loops — some 2026 GenAI interview surveys put roughly 75% of technical-round time on RAG architecture, evals, and multi-agent design specifically. Unlike round 1, there's no single correct answer here; there's a *defensible* one. Each prompt below is open-ended, exactly the way it would actually get asked, followed by a strong-answer sketch: the shape a great answer takes, the tradeoffs it names unprompted, and the follow-up questions a real interviewer would push with next. Rehearse these out loud — talk through your own answer for 3-5 minutes before reading the sketch.

A repeatable framework worth applying to every prompt in this round, roughly in this order: (1) clarify the actual requirements and constraints before designing anything, (2) sketch the end-to-end shape at a high level, (3) go one level deeper on the 1-2 components that are actually hard here, (4) name the failure modes and how the system degrades under each, (5) state what you'd measure to know it's working. Interviewers notice candidates who jump straight to step 3 without doing 1-2 first.

## Prompt 1: Design a policy-RAG customer-support agent

*"Design a system that answers customer questions by retrieving from a set of company policy documents. The documents get updated regularly and sometimes conflict with each other."*

**Strong-answer sketch**

Start by clarifying: how often do policies change, how large is the corpus, does "conflict" mean stale duplicates or genuinely different current policies for different customer segments, and what's the cost of a wrong answer (a refund miscalculation is worse than a wrong store-hours answer). This framing question alone signals more maturity than jumping straight to "I'd use a vector database."

Then the pipeline, in order: ingestion → chunking → embedding → indexing → retrieval → (optional) rerank → grounded generation, mirroring [[ingestion]] through [[grounded-answers-injection-defense]]:

- **Ingestion & chunking** — policy documents chunk by logical section, not fixed character count, so a chunk is a coherent policy statement rather than a mid-sentence fragment; each chunk carries metadata (`policy_id`, `version`, `effective_date`, `region`) so retrieval and generation can reason about *which* version of a conflicting policy applies. See [[chunking]], [[ingestion]].
- **Retrieval** — hybrid, not dense-only: dense catches paraphrased customer questions ("can I send this back") against formally-worded policy text; sparse (BM25) guarantees exact matches on SKUs, policy codes, or specific terms dense search treats only probabilistically. Fuse with RRF rather than a hand-tuned score blend — no normalization needed, one well-tested constant (`c=60`). See [[hybrid-retrieval-rrf]], [[dense-retrieval]], [[bm25-sparse-retrieval]].
- **The conflicting-policy problem specifically** — this is the part of the prompt worth dwelling on, since it's the actual hard problem, not retrieval mechanics. Options to name and compare: (a) always retrieve by most-recent `effective_date` and surface the version explicitly rather than silently picking one; (b) if two policies for the same topic are both currently active for different customer segments (region, tier), retrieve both and let the generation step disambiguate using customer context, rather than have retrieval itself guess; (c) flag genuinely unresolved conflicts (same effective date, contradictory text) to a human rather than let the model pick silently — this is a guardrail decision, not a retrieval one.
- **Grounded generation** — the answer must cite which policy chunk(s) it drew from, and the system prompt must instruct the model to answer *only* from retrieved content, treating it as untrusted data to reason about (never instructions to follow) — the same discipline ReAct applies to tool observations. See [[grounded-answers-injection-defense]], [[react-pattern]].
- **Freshness** — re-ingestion has to be a scheduled or event-triggered pipeline, not a one-time load; a stale index answering from a superseded policy is a worse failure than "I don't know."

**Tradeoffs to mention unprompted**: chunk size (bigger = more context per chunk, worse retrieval precision), whether to rerank (adds latency and cost, pays off most when hybrid alone doesn't disambiguate near-duplicate chunks), and whether reranking is even worth it for exact-identifier queries where hybrid retrieval already nailed it (per this repo's own lab evaluation, reranking barely moved scores once hybrid fusion had already found the right chunk).

**Follow-ups an interviewer would probe with**: "How do you evaluate this beyond eyeballing answers?" (precision@k/recall@k/MRR on a golden set, see [[retrieval-eval-metrics]]) — "What happens if retrieval returns nothing relevant?" (fail closed: say "I don't have a policy on that" rather than let the model free-generate) — "How would you detect a customer trying to get the assistant to ignore its grounding instructions?" ([[guardrails-injection-detection]]).

**Grounded in this repo**: this is exactly ShopSense's Policy RAG agent (Milestone 4) — Kartway's 14 policy documents are *deliberately* conflicting and versioned specifically to force this design decision, not an edge case bolted on afterward. See [[capstone-milestone-map]], [[qdrant]].

## Prompt 2: Design a multi-agent system with a supervisor and specialists

*"Design a customer-support system where different kinds of requests need different handling — some need a database lookup, some need policy interpretation, some need a human escalation."*

**Strong-answer sketch**

First, justify the multi-agent decision itself before designing it — this is the question most candidates skip, and it's the one that separates "knows the mechanics" from "knows when to reach for them." A single agent with three tools bound to it is not automatically worse than three specialist agents; splitting only pays off for a nameable reason: genuine separation of expertise (a fact-checker sharing the writer's full context can be talked into confirming its own fabrication), independently parallelizable sub-tasks, or a critic that must not share the producer's blind spots. See [[workflow-vs-agent-autonomy-spectrum]], [[agent-topologies]].

Given the prompt's actual shape (routing depends on ticket content, order isn't knowable in advance), a **hierarchical supervisor-worker topology** is the right call — a supervisor classifies/routes, specialists (Triage, Policy RAG, Order-Actions, Escalation Reviewer) each own one narrow decision:

- **State design** — one shared state object (LangGraph `TypedDict`/`Annotated` state), but *not* unrestricted shared access. Two scoping decisions matter more than the graph wiring itself: **read scoping** — each specialist gets only its relevant state slice via a `context_for(role, state)` function, not the whole dict, because a specialist that can read another's full context can be persuaded by it; and **write scoping** — a `@scoped(role)` decorator enforcing a per-role allowlist of state keys each node may write, raising before an out-of-scope write ever reaches the graph's reducer. See [[supervisor-worker-teams]], [[langgraph-state]].
- **Routing** — the supervisor node reads current state and a conditional edge dispatches to the next specialist; this loop needs a hard iteration/recursion cap, the same "agentic loop needs a ceiling" discipline as a single agent's tool-call loop, just one level up. See [[langgraph-agentic-patterns]], [[langgraph-conditional-edges]].
- **Escalation as a design-native path, not an afterthought** — the Escalation Reviewer isn't a fallback bolted onto failure; it's a specialist in the roster the supervisor can route to deliberately (a Fact-Checker/Reviewer-style dual-critic shape, potentially), and its verdict should require *both* an objective/deterministic check and an independent LLM-judge check (AND, not OR) if any judgment is safety- or compliance-relevant — a judge alone can be argued around, a structural check alone can't catch a plausible-sounding wrong decision.
- **Checkpointing** — a long-running or multi-turn ticket needs to survive a process restart or a human-in-the-loop pause (a customer needs to confirm something before Order-Actions proceeds); LangGraph's checkpointer persists graph state per-thread so a paused conversation resumes exactly where it left off, distinct from the cross-thread long-term memory store (a common interviewer trap: don't conflate `checkpointer` with `Store`). See [[langgraph-checkpointing-hitl]].
- **Idempotency** — any specialist with a side effect (Order-Actions issuing a refund) needs a deterministic idempotency key so a re-run after an interrupt or checkpoint-resume doesn't double-fire the action. See [[idempotency-and-side-effects]].

**Tradeoffs to mention unprompted**: coordination cost compounds with topology depth — a star topology burns roughly two supersteps per unit of work, so a 5-agent team can eat into a default recursion limit fast; per 2026 industry estimates, independent multi-agent setups run roughly 58% more tokens than a single agent doing the same work, and centralized/hierarchical coordination overhead can run substantially higher — multi-agent only pays for itself when specialization/parallelism/critique genuinely matter, not by default.

**Follow-ups an interviewer would probe with**: "What happens if two specialists need to write the same state key on the same turn?" (write-scope violation, should raise rather than silently overwrite) — "How do you keep one customer's data from leaking into another's session?" ([[auth-and-multi-tenancy]] — identity from the authenticated session only, never parsed from message text, per-tenant namespacing) — "Supervisor or swarm (peer-to-peer handoff, no central router)?" (supervisor is centralized and easy to audit; swarm is more flexible but much harder to debug and reason about — most production deployments in 2026 still favor centralized orchestrator/supervisor shapes).

**Grounded in this repo**: this is exactly Milestone 6-7 — ShopSense's four-agent team (Triage → Policy RAG → Order-Actions → Escalation Reviewer), coordinated as a LangGraph supervisor-worker graph with write-scoping and dual-critic review baked in from the lab's own multi-agent notebook. See [[capstone-milestone-map]], [[supervisor-worker-teams]].

## Prompt 3: How would you add long-term memory to an existing agent?

*"You have a working single-turn support agent with no memory. A customer wants it to remember their preferences and past issues across sessions. How would you add that?"*

**Strong-answer sketch**

Resist the urge to say "add a vector database" as the first sentence — start from the actual taxonomy of what "remember" means, because different kinds of memory need different treatment: **working** (the live conversation buffer, transient, already exists implicitly), **episodic** (what happened and when — a specific past event), **semantic** (a durable, timeless fact), and **procedural** (a reusable how-to). A plain chat history is only episodic memory in a crude, undistilled form — extracting semantic facts and procedural rules is a deliberate write step your application (or the agent itself) has to perform, not something that falls out of a longer buffer. See [[memory-types]].

Design from there:

- **Storage** — a managed memory API (this repo uses Supermemory) or a self-hosted alternative (Postgres + pgvector + your own extraction prompt is the "boring" option worth naming) writes each fact tagged with a per-customer isolation key (`container_tag`) and a `metadata={"type": "episodic"|"semantic"|"procedural"}` tag. Every read and write must be scoped to that key — a single missed call site is a cross-customer data leak, not a cosmetic bug. See [[supermemory]].
- **Write path** — decide *when* something gets written: a fixed post-turn extraction step (application-decided, the lab's approach) or let the agent itself decide what's worth persisting mid-conversation (2026-era "agent-managed memory," e.g. tool-based memory APIs) — the latter shifts judgment to the model, trading a simpler mental model for less predictable coverage.
- **Read path** — memory recall has to work across paraphrase (the customer might ask about "that flight" without saying "flight AI-302"), which is a property of the retrieval mechanism (semantic embedding search), not the memory type itself. Recalled memory should be labeled untrusted in the prompt — it can include the agent's own past hallucinations, so it shouldn't be treated as ground truth for a new tool argument any more than a RAG chunk would be.
- **Consolidation** — uncurated long-term memory accumulates duplicates and staleness over months of real use; production systems run an offline consolidation pass ("Dreaming," per course material) between sessions that merges duplicates and prunes what's gone stale — something a short-lived demo never needs but a real deployment eventually always does. See [[context-compression]].
- **Async write semantics** — a managed memory API's writes are often async (not immediately searchable); code that writes then immediately reads back needs to poll, not assume immediate consistency — a real, not hypothetical, race condition.

**Tradeoffs to mention unprompted**: managed memory API (Supermemory/Mem0/Zep) vs. a hand-rolled Postgres+pgvector table — the managed option buys indexing/search/extraction pipeline maintenance for free at the cost of vendor lock-in and, in this repo's case, no bulk "list all" API (purge is a best-effort semantic sweep, not a guaranteed-complete delete) — a real limitation to flag if the interviewer asks about GDPR-style deletion requirements.

**Follow-ups an interviewer would probe with**: "How do you prevent memory from just becoming a second, unmanaged context-rot problem?" (curate what gets recalled per call the same way you'd curate retrieved RAG chunks — see [[context-engineering]]) — "What if the memory store is down?" (fail open on the write, log loudly, never block the customer-facing turn on a memory outage) — "How would you test that memory recall actually works?" (a paraphrase-robustness test: write a fact, query it back using different wording, assert recall — exactly the lab's own test pattern).

**Grounded in this repo**: Milestone 3 — persistent memory + semantic index, the first ShopSense capability layered onto the single-agent build from M1/M2. See [[capstone-milestone-map]].

## Prompt 4: How would you decide between fine-tuning and RAG for a given problem?

*"A team wants their assistant to be better at [some capability]. How do you decide whether that's a fine-tuning problem or a RAG problem?"*

**Strong-answer sketch**

Lead with the actual test, not a list of pros and cons: **does the thing you're trying to fix change often, or is it a stable pattern you want the model to just do by default?** RAG hands the model a reference to consult at answer time — best fit for facts that change (a policy, a price, a database row). Fine-tuning retrains the model's weights on examples of a behavior — best fit for a stable pattern (a consistent output format, a tone, a checklist reliably followed) that prompting alone hasn't made reliable. See [[fine-tuning-vs-rag]].

Walk through the concrete diagnostic, since "it depends" without a test is a weak answer: ask what specifically is failing. If the model gives outdated or wrong facts, that's a retrieval-freshness problem, and fine-tuning on today's facts would just bake in something that goes stale the moment those facts change again — a named, costly, common mistake. If the model has the right facts in context but keeps getting the *shape* of the answer wrong (inconsistent format, wrong tone, skips a required disclosure) even when prompted carefully, that's the actual fine-tuning-shaped problem — and worth checking prompting/context-engineering has genuinely been exhausted first, since a behavior inconsistency is sometimes a context problem (the instruction isn't reliably present in the window) rather than a real case for retraining.

Note the two aren't mutually exclusive: a system can fine-tune for consistent behavior *and* retrieve the facts that must stay current — retrieve the volatile part, fine-tune the stable part.

**Tradeoffs to mention unprompted**: update cost asymmetry — re-indexing a changed document is cheap and instantaneous-ish; retraining or re-adapting a model is a whole pipeline with its own eval and rollout risk. Cheaper open-weight adapter techniques have made fine-tuning more accessible than a couple of years ago, which shifts the "worth testing" threshold but doesn't change the underlying facts-vs-behavior distinction.

**Follow-ups an interviewer would probe with**: "Give a concrete example where you'd do both." (an HR-policy assistant: retrieve the country-specific leave entitlement that changes; fine-tune — or more cheaply, prompt-engineer first — the consistent explanation/checklist/escalation format) — "How would you know prompting has actually been exhausted before reaching for fine-tuning?" (an eval set showing the behavior fails consistently across representative prompts, not just an anecdotal miss) — "What's the risk of fine-tuning on facts that change?" (staleness the moment the fact changes again, requiring a whole new training pass, versus a RAG re-index that's near-free).

**Grounded in this repo**: ShopSense never fine-tunes anything — Kartway's conflicting, versioned policy documents are the textbook "facts that change" case for Policy RAG (M4), and the capstone's behavior-consistency needs (tool-call shape, escalation wording) are handled through prompting, schemas, and repair loops rather than retraining, which the framework itself predicts is the right call when a smaller lever (context engineering) already covers it. See [[fine-tuning-vs-rag]], [[structured-output-repair-loops]].

---

*Grounded in `lab-summaries/`, `presentations/day1-4.md`, this knowledge base's stage 00-09 pages, ShopSense/Kartway's own architecture ([[capstone-milestone-map]]), and general LLM/RAG/agent-engineering system-design interview practice as of 2026-08.*
