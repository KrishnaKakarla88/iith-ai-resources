# Round 5 — Behavioral & Tradeoffs

This round has no single right answer — interviewers are grading your reasoning process, not whether you land on the "correct" side of RAG-vs-fine-tune. The strong pattern across every answer here: name the actual axis the decision turns on, give a concrete worked number or example, and say what you'd measure to confirm the call rather than assert it from instinct. Behavioral questions in this round are deliberately hybridized with technical judgment — "tell me about a production issue" is really asking "do you understand what breaks in a system like this, and would you have designed against it before it happened."

---

## RAG vs. Fine-Tuning

**Q1. When would you reach for fine-tuning instead of RAG, and what's the single question that decides it?**

The single question: does the thing you're trying to fix *change often*, or is it a *stable pattern* you want the model to just do by default? RAG hands the model a reference to consult at answer time — right for facts that change (a return policy revised quarterly, current prices, a database row). Fine-tuning retrains the model's weights on examples of a behavior — right for something you want baked in as default behavior (a consistent output format, a tone, a checklist reliably followed across thousands of cases) where no amount of retrieval fixes the model getting the *shape* of its answer wrong even when it's looking at the correct facts.

The most common, costliest mistake in practice: fine-tuning on facts that change weekly — pricing, inventory, anything with a shelf life shorter than your retraining cadence. You bake in something that goes stale the moment it changes again, and you're back to retraining, when retrieval would have kept it current for free. A worked example: an HR assistant answering "how much parental leave can I take" — the entitlement varies by country and gets revised, so that's retrieved, not memorized; the required answer *shape* (a checklist, specific escalation wording) is something you want reliably consistent across thousands of cases — that's the fine-tuning candidate, if prompting alone hasn't already made it reliable enough.

**What a strong answer adds unprompted**: these aren't mutually exclusive. A production system can retrieve the facts that must stay current *and* fine-tune for the repeatable way it handles them — the decision isn't "pick one," it's "which mechanism handles which part of the problem."

**Related**: [[fine-tuning-vs-rag]], [[embeddings-models]], [[model-selection-cost-latency-tradeoffs]]

---

**Q2. A team wants to fine-tune a model on this quarter's product catalog so it "always knows current inventory." Good idea? What would you tell them instead?**

No, for the same reason pricing is the canonical wrong-use case: inventory is a fact that changes — daily, possibly hourly — and fine-tuning bakes in a snapshot that's stale before the training run even finishes. The team's actual goal ("the assistant should always answer with current inventory") is better served by retrieval against a live or near-live inventory index, so a stock change shows up on the next query with no retraining involved. What would legitimately be worth fine-tuning here, if anything: the *consistent way* the assistant should phrase an out-of-stock answer, offer substitutes, or escalate — a stable behavioral pattern, not the inventory numbers themselves.

**Related**: [[fine-tuning-vs-rag]]

---

**Q3. Before reaching for fine-tuning to fix an inconsistent agent behavior, what should you check first — and why does that check usually get skipped?**

Check whether prompting and context engineering have actually been exhausted first — a behavior inconsistency is sometimes a context problem (the instruction that would fix it isn't reliably present in the window on every call, or it's present but buried under retrieved chunks and history) rather than a genuine case for retraining. It gets skipped because fine-tuning feels like a more "permanent" fix and prompting feels like something you've "already tried" — but a prompt that works 80% of the time is often a prompt that's competing for attention with too much other context, not a signal the model fundamentally can't do the task. The cheaper, reversible fix (tightening context, restructuring the system prompt, adding a few-shot example) should be ruled out before paying fine-tuning's cost, which is real even with cheap adapter techniques: data curation, training/eval cycles, and a new artifact to version and redeploy every time the behavior needs to change again.

**Related**: [[fine-tuning-vs-rag]], [[context-engineering]]

---

## Retrieval Strategy

**Q4. Dense, sparse, or hybrid retrieval — how do you decide, and what's the failure mode of picking wrong?**

The two base methods fail in complementary, not overlapping, ways: dense (embedding) retrieval is strong on paraphrase and concepts but can miss an exact SKU, case number, or acronym it's never seen phrased that way; BM25/sparse retrieval nails exact terms but is blind to synonyms and rephrasing entirely. If your domain has exact identifiers that must never be missed (order numbers, product codes, legal citations), hybrid isn't a nice-to-have tuning improvement — it's the only way to *guarantee* the exact match isn't missed, since dense's success there is probabilistic (does the embedding space happen to place a paraphrase close enough) and BM25's is deterministic (the token is either in the document or it isn't).

The wrong-pick failure mode in each direction: dense-only on an identifier-heavy corpus silently misses exact matches some fraction of the time with no error — the system just answers confidently from the wrong (or no) document; sparse-only on a corpus full of paraphrase and natural-language variation misses semantically-relevant documents that never share exact wording with the query. Both failures are silent — nothing errors, the system just retrieves badly — which is exactly the kind of thing [[retrieval-eval-metrics]] (recall@k, MRR measured deliberately, not assumed) is supposed to catch before a user does.

**What a strong candidate adds**: how you'd *fuse* the two matters as much as choosing to run both — Reciprocal Rank Fusion (RRF) fuses on rank position, not raw score, specifically because a cosine similarity and a BM25 score live on incompatible scales that can't be meaningfully normalized or averaged together; naively blending the two raw scores is a common mistake that produces a fusion that's more fragile (needs re-tuning per corpus) than RRF's fixed formula.

**Related**: [[dense-retrieval]], [[bm25-sparse-retrieval]], [[hybrid-retrieval-rrf]], [[retrieval-eval-metrics]]

---

**Q5. Your dense retriever already scores recall@k ≈ 1.0 on your eval set. Is adding BM25/hybrid retrieval still worth the engineering cost?**

It depends entirely on what's actually in your corpus and what your eval set covers — a strong dense-alone number on a clean, well-covered eval set doesn't guarantee the same result on the queries you didn't test. Concretely: with a strong embedder on a clean corpus, dense-only retrieval can genuinely already hit recall@k ≈ 1.0 and MRR ≈ 0.95 — hybrid retrieval in that regime buys a smaller, incremental gain (MRR edging toward 1.0) and, more importantly, converts an already-good-but-probabilistic guarantee on exact identifiers into an actual guarantee via BM25. Whether that's worth the added engineering (a second index, a fusion step, more moving parts to keep in sync) depends on the cost of the rare miss: for a general-knowledge assistant, an occasional miss on the long tail might be acceptable; for a system where "produced the wrong order number" is a real operational cost, the guarantee is worth it even at a small measured uplift. The answer an interviewer wants to hear is "it depends, and here's the measurement I'd run to decide," not a reflexive "always add hybrid, it can only help."

**Related**: [[hybrid-retrieval-rrf]], [[retrieval-eval-metrics]]

---

## Framework and Architecture Choices

**Q6. LangChain, LangGraph, or a bare `while` loop — how do you actually decide, and why is this not really a three-way choice?**

It's really a narrower question than the framing suggests: does this specific piece of work run the same steps in the same order every time (a **chain** — plain code, or LCEL if you want composability), or does it need branching, a pause point, resumability after a crash, or multiple cooperating agents (a **graph**)? As of LangChain 1.0, LangChain's own agent runtime (`create_agent`) is built on top of LangGraph — so "LangChain vs. LangGraph" isn't picking between two competing frameworks forever, it's picking the right *layer*: a pre-built tool-calling loop (`create_agent`) when a standard ReAct-shaped loop is all you need, or dropping to raw `StateGraph` when you need node-level control the pre-built loop doesn't expose (custom state fields, non-standard conditional routing, checkpointing wired at a specific pause point).

The bare `while` loop is the genuinely boring alternative underneath both: fine for a single-developer prototype or a task simple enough that you don't need state persistence, but it has no answer for "the process died at minute forty" — there's no saved position to resume from, so a crash means starting over at minute zero. That's the concrete capability a checkpointer buys you, and it's the reason "just use a loop" stops being the right answer the moment durability or human-in-the-loop pausing enters the requirements.

**Strong-answer framing**: name the actual question ("chain vs. graph," not "LangChain vs. LangGraph") — that's usually the tell that a candidate understands the current (post-1.0) relationship between the two rather than repeating outdated framing from a blog post that predates `create_agent`.

**Related**: [[langchain-vs-langgraph]], [[graph-engineering-mindset]], [[langgraph-checkpointing-hitl]]

---

**Q7. When should you deploy a fixed workflow instead of an autonomous agent, and what's the actual signal that a task needs agent autonomy?**

The signal is not "this task involves an LLM" or "this feels complex" — it's whether the next step genuinely depends on something discovered mid-task: a search returns something unexpected, a tool fails and a different one is needed, the right path can't be enumerated ahead of time. If the steps are actually fixed — validate input, look something up, format an answer — a workflow does that job with less cost, lower latency, and a fully enumerable set of execution paths you can test exhaustively, because you wrote every path yourself. Reaching for agent autonomy by default, when the task's steps are actually knowable in advance, is the specific mistake this framing exists to prevent: autonomy is a cost you pay for genuine unpredictability, not a feature you add because agents are more interesting to build.

**Follow-up interviewers ask**: "Is an agent always strictly more capable, since it can also just... follow fixed steps if that's the best path?" — no, and this is the trap: an agent's flexibility means you can only *bound* its paths (iteration caps, tool allowlists, guardrails), never fully enumerate them the way you can a workflow's — so even when an agent happens to behave like a fixed workflow in practice, you've paid for unpredictability you never needed and can't fully test away.

**Related**: [[workflow-vs-agent-autonomy-spectrum]], [[agentic-loop-fundamentals]], [[react-pattern]]

---

**Q8. "Agent = model + harness" — unpack that claim and explain why it matters for a hiring decision about your own experience.**

The claim: the model alone doesn't determine how reliable or capable an "agent" is — the harness around it (the loop structure, the tool executor, retry/circuit-breaker wrapping, permission checks, context/memory management, iteration caps) is what actually determines whether the same model behaves like a careful, bounded actor or a runaway one. The same underlying model dropped into two different harnesses — one with a tight iteration cap, tool allowlist, and guardrail layer; one with none of that — produces very different real-world behavior and risk, even though "the model" hasn't changed at all.

Why it matters for how you talk about your own experience: describing a project as "I built an agent with Groq/Claude" says almost nothing about what you actually did. The harness-level decisions — how you bounded the loop, what you did when a tool call failed, how you decided a step was irreversible enough to need a human pause — are the actual engineering content of the work, and naming them specifically is what distinguishes "I called an LLM API in a loop" from "I designed a reliable system."

**Related**: [[workflow-vs-agent-autonomy-spectrum]], [[agentic-loop-fundamentals]]

---

## Model Selection

**Q9. How do you choose which model to use for a given task — walk through your actual decision process, not just "check a leaderboard."**

"Which model should I use" is the wrong first question — the right one is which model passes your evals at the lowest acceptable cost, latency, and risk for *this specific task*. A frontier model topping a general leaderboard can still be the wrong production pick if it's too slow for a real-time flow, too expensive at your actual request volume, or its provider can't meet a data-residency requirement — none of which a benchmark score captures.

Concretely: cost and latency both scale with tokens, and a longer conversation isn't "a bit more" than a short one — the entire history gets resent and reprocessed on every call, so a 50-turn conversation is the whole transcript, billed and processed again, every single turn. A back-of-envelope worth having ready: `tokens/day = tokens/turn × turns/session × sessions/day`, then `cost/day = (tokens/day / 1M) × price per 1M tokens` — a worked shape of this: 200 tokens/turn × 20 turns × 500 sessions/day ≈ 2M tokens/day, which at $2.50/1M is $5/day for one *untrimmed* flow — small-sounding until multiplied across a real product's traffic.

The second, less obvious point: task/domain leaderboards (tool-use benchmarks, domain-specific evals) matter more than general leaderboards for a specific job — general capability and fit for your actual task are different measurements, and benchmark contamination/saturation make trusting any single number risky without triangulating across a couple of boards.

**Why this repo pairs Groq for chat with a separate provider (Gemini) for embeddings, specifically**: chat/reasoning quality and embedding quality are separate capabilities with entirely separate cost/latency/quality curves — nothing requires the same vendor to be best (or even competitive) at both, and assuming "one vendor for everything" is simpler is a real cost if it means settling for a worse embedding model just to stay in one provider's ecosystem.

**Related**: [[model-selection-cost-latency-tradeoffs]], [[embeddings-models]], [[litellm-as-gateway]]

---

**Q10. "This model is API-compatible with OpenAI's format" — what does that guarantee, and what does it not guarantee? Why does this matter operationally?**

It guarantees the request will *parse* against the compatible endpoint — the JSON shape, field names, and basic contract match closely enough that existing client code doesn't error out. It does not guarantee identical *behavior*: a parameter the original API respects can be silently ignored or reinterpreted by the compatible provider, with no error and no signal in the response that anything was different. This matters operationally because a team that swaps providers assuming "OpenAI-compatible" means "drop-in replacement" can ship a silent regression — a `temperature` or `max_tokens` setting that used to matter quietly stops mattering, and nothing pages anyone because nothing errored. The practical discipline: re-run your eval suite against the new provider before trusting a swap, don't assume compatibility from the API shape alone.

**Related**: [[model-selection-cost-latency-tradeoffs]], [[litellm-as-gateway]]

---

## Behavioral / Production-Judgment Hybrids

**Q11. Tell me about a production reliability issue you'd expect in a system like this, and how you'd have designed against it before it happened.**

A strong answer here doesn't just describe a bug — it walks through the design decision that would have prevented it, framed as something decided up front rather than patched after an incident. One concrete, well-grounded shape to reason through out loud:

*The issue*: an agent with a tool that performs an irreversible action (issuing a refund, deleting a record) gets checkpointed and human-in-the-loop paused before executing it — but the side effect is placed *before* the pause inside the same node. On resume, the graph doesn't restore an in-flight call stack; it replays the entire node function from the top until the pause resolves. The irreversible action fires once on the original run and fires *again* on every resume — a real double-charge, not a hypothetical.

*How you'd have designed against it*: structurally, not defensively — split any node that pauses into two: one node that does nothing but read state and call the pause, and a second, downstream node (reached only after the pause resolves) that contains the actual irreversible action. That split makes the double-fire architecturally impossible rather than something a code reviewer has to remember to check for on every new node. Layer a deterministic idempotency key underneath that as defense in depth — a refund call keyed by `uuid5(order_id, amount, approval_timestamp)` makes even a second accidental call a no-op at the payment provider, rather than relying solely on the graph-level fix holding forever as the codebase grows.

*The generalizable point to make explicit*: the fix is structural, not "remember not to do this" — the same category of bug (a control that depends on developer discipline under deadline pressure rather than being impossible-by-design) shows up across this stack in different clothes: a guardrail bypass flag that isn't scoped to its one legitimate caller, a credential with more scope than the one action it's meant to authorize, a tracing decorator that captures whatever's in scope rather than an explicit allowlist. Naming the *pattern*, not just the one incident, is what separates a candidate who fixed a bug from one who thinks about reliability as a design discipline.

**Related**: [[idempotency-and-side-effects]], [[langgraph-checkpointing-hitl]], [[auth-and-multi-tenancy]]

---

**Q12. Describe a time (real or a system you'd design) where you had to choose between shipping something imperfect and delaying for more testing. How did you decide, specifically for an agentic system where "testing" is unusually hard to make exhaustive?**

The strong framing for an agentic system specifically: the decision isn't "tested vs. untested," it's "which layer have I actually verified, and which am I still trusting on faith." [[testing-agent-code]] and [[eval-driven-development-mindset]] answer genuinely different questions — unit tests prove the code does what you meant (deterministic, fast, gate every commit) while eval against a golden set proves the agent's *behavior* is good enough (probabilistic, slower, never fully exhaustive because you can't enumerate every real user query in advance). A defensible ship decision names which of these you have real coverage on, which you don't, and what the mitigation is for the gap — guardrails that fail loud rather than silently, a human-in-the-loop pause on the highest-blast-radius actions, a fallback path that degrades visibly instead of hiding a failure. The weak version of this answer treats "we tested it" as binary; the strong version treats confidence as layered, names which layer is thin, and describes what catches a miss in that layer in production rather than pretending pre-ship testing alone could have been exhaustive.

**Related**: [[testing-agent-code]], [[eval-driven-development-mindset]], [[guardrails-injection-detection]]

---

**Q13. How would you decide whether a support-agent feature needs a new autonomous sub-agent versus being folded into an existing agent's toolset?**

This is the multi-agent version of the workflow-vs-agent question, and the same discipline applies at one level up: don't add topology complexity (a new agent, a new supervisor route) where a new tool on an existing agent would do. The signal that genuinely justifies a *new agent* rather than a new tool: the new capability needs its own scoped permissions or write-boundary that shouldn't be trusted to the existing agent's context (e.g., an escalation-reviewer role that can override a decision the customer-facing agent made, which should not share write-scope with it), or it needs independent reasoning about a sub-problem complex enough that folding it into the existing agent's prompt would overload that agent's context and routing logic. The failure mode on both sides is real: under-splitting means one agent's prompt and toolset become an unmanageable grab-bag with blurred permission boundaries; over-splitting means unnecessary coordination overhead, more inter-agent state to keep consistent, and more surface area for a permission-boundary bug between roles that didn't need to exist as separate roles at all.

**Related**: [[agent-topologies]], [[supervisor-worker-teams]], [[workflow-vs-agent-autonomy-spectrum]]

---

## Sourcing

Grounded in `lab-summaries/`, `presentations/day1-4.md`, and general LLM/agent-engineering interview practice as of 2026-08 — including current (2025-2026) web-researched framing on RAG-vs-fine-tuning decision frameworks, dense/sparse/hybrid retrieval tradeoffs, and LangChain-vs-LangGraph/workflow-vs-agent architecture-choice questions as they're currently asked in production ML and agentic-AI system-design interviews.
