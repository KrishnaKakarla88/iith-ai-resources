---
stage: "00-ai-and-llm-basics"
tags: [primer, fine-tuning, rag, decision-framework]
last_verified: 2026-08-21
---

# Fine-tuning vs. RAG

RAG and fine-tuning solve two different problems that both get pitched as "make the model smarter": RAG keeps facts current without retraining anything, fine-tuning changes how the model behaves in general — and reaching for the wrong one is one of the more expensive mistakes a team can make.

## Prerequisites
- [[model-selection-cost-latency-tradeoffs]]
- [[what-is-an-llm]]

## In plain English

It's tempting to treat "the model doesn't know X" and "the model doesn't behave the way I want" as the same problem, solvable the same way. They aren't. RAG (retrieval-augmented generation — the full mechanics live in [[ingestion]] through [[grounded-answers-injection-defense]] in the RAG stage, not repeated here) hands the model a reference to consult at answer time: retrieve the relevant document, put it in context, let the model answer from it. Fine-tuning instead retrains the model's weights on examples of the behavior you want, so that behavior becomes the model's default without needing anything supplied at call time.

The test that decides between them is: **does the thing you're trying to fix change often, or is it a stable pattern you want the model to just do by default?** A return policy that gets revised quarterly, an exchange rate, a row in a database — these are facts that change, and retraining a model every time one of them updates is both slow and wasteful. A consistent output format, a specific tone, a checklist the model should reliably follow across thousands of cases — that's stable behavior, and no amount of retrieval fixes an assistant that keeps getting the *shape* of its answer wrong even when it's looking at the right facts.

The common, costly mistake is fine-tuning on facts that change weekly — baking in something you'll have to retrain again the moment it goes stale, when retrieval would have kept it current for free.

## Core mechanics

| | RAG | Fine-tuning |
|---|---|---|
| What it changes | What the model can *look up* at answer time | How the model *behaves* by default, with no lookup needed |
| Best fit | Facts that change — policies, prices, current records | Stable behavior/style — consistent format, tone, a checklist followed reliably |
| Update cost when the underlying thing changes | Re-ingest/re-index the changed document; no retraining | Retrain (or re-adapt) the model itself |
| Failure mode if misapplied | Stale retrieval if the index isn't refreshed | Wrong tool entirely if what you needed was current facts, not a behavior change — a model can be perfectly fine-tuned and still confidently wrong about something that changed after training |
| What "2026" changed (per course material) | Not the core trade-off itself | Cheap, open-weight adapter techniques made fine-tuning meaningfully more affordable and accessible than a year earlier, per course material (`presentations/day4.md`) citing open-weight models such as Kimi K3, Qwen3.6, GLM, and DeepSeek — reported here as course material, not independently web-verified given how recent these releases are |

**Worked example** (per course material): an internal assistant answers "how much parental leave can I take, and what do I need to submit?" The leave *entitlement* varies by country and gets revised — that's retrieved from the current policy document, not memorized. The required *answer shape* (a plain-English explanation, a checklist, specific escalation wording) is something the assistant should produce consistently across thousands of cases; if prompting alone can't make that reliable, that's the fine-tuning candidate — and a cheaper, capable open-weight model can now make that adaptation affordable enough to be worth testing rather than assumed out of reach. The two aren't mutually exclusive: retrieve the facts that must stay current, fine-tune the repeatable way the model handles them.

## How this shows up in the capstone

The ShopSense policy-RAG agent (Milestone 4) is a direct instance of the "facts that change" side of this framework — Kartway's policy documents are deliberately conflicting and versioned, which is exactly the kind of content retrieval keeps current without retraining; see [[capstone-milestone-map]]. Nothing in the course build calls for fine-tuning a model, which is itself consistent with the framework: the capstone's behavior-consistency needs (tool-call shape, escalation wording) are handled through prompting, schemas, and repair loops (see [[structured-output-repair-loops]]) rather than retraining, since a small, capable instruction-following model plus good context engineering covers it.

## Interview fire round

- **Q: A team wants to "fine-tune the model on our latest pricing" so it always has current prices. Good idea?**
  A: No — pricing changes are exactly the "facts that change" case RAG is built for. Fine-tuning on today's prices bakes in information that goes stale the moment prices change again, requiring another retraining pass; retrieval keeps that current without touching the model at all.
- **Q: When does fine-tuning actually make sense over RAG?**
  A: When the problem is consistent *behavior* — format, tone, a checklist reliably followed — not missing or changing facts, and prompting/context engineering alone haven't made that behavior reliable enough.
- **Q: What changed about this trade-off in 2026, per course material?**
  A: Cheaper, capable open-weight models with more accessible adapter-based fine-tuning shifted the cost side of the calculation — fine-tuning a stable-behavior need became more affordable to test, not that the underlying facts-vs-behavior distinction changed.

## Production gotchas & best practices

- Per course material (`presentations/day4.md`, Act 3): fine-tuning facts that change weekly is called out explicitly as "the most common and costliest mistake" in this decision — a signal that the failure mode is common enough to name directly, not a hypothetical.
- Production practice: RAG and fine-tuning are not mutually exclusive — a system can fine-tune for consistent behavior/format while still retrieving the facts that must stay current, per the worked example above.
- Production practice: before fine-tuning for a behavior problem, verify prompting and context engineering (see [[context-engineering]]) have actually been exhausted first — a behavior inconsistency is sometimes a context problem (the right instruction isn't reliably in the window) rather than a genuine case for retraining.

## Course vs. production

Course material frames this as a 2026-specific shift: cheaper open-weight adapters made fine-tuning viable for teams that previously couldn't justify the cost, turning "RAG vs. fine-tune" into more of a live, worth-testing hybrid decision than a near-automatic default to RAG. This capstone doesn't exercise fine-tuning at all — every ShopSense agent's behavior consistency comes from prompting, schemas, and repair loops rather than retraining, which is itself a legitimate instance of the framework (the behavior need was solvable without paying fine-tuning's cost).

## Related
- **Builds on** — [[model-selection-cost-latency-tradeoffs]]
- **See also** — [[embeddings-models]], [[chunking]] (RAG mechanics this page doesn't re-explain)
- **Related** — [[context-engineering]] (often the cheaper fix to try before fine-tuning)

## Sources

**Course material**
- `presentations/day4.md` (Session 2, Act 3, Question 2 — "What Is the Fine-Tune-vs-RAG Decision Framework?", the HR-policy-assistant worked example; near-future open-weight model names reported per course material, not independently web-verified)

**Web sources**
- No independent web source verifies the specific 2026 open-weight model claims (Kimi K3, Qwen3.6, GLM, DeepSeek) cited in course material as of 2026-08-21 — reported here as "per course material" per this knowledge base's sourcing rules, not as independently confirmed.
