---
stage: "06-rag"
tags: [rag, evaluation, metrics, golden-set]
last_verified: 2026-08-20
verified_against: "lab notebook implementation, generic metric formulas"
---

# Retrieval eval metrics

Precision@k, recall@k, and MRR are the standard way to measure whether a retrieval pipeline actually surfaces the right evidence — a way to prove a change helped, instead of eyeballing a few examples and hoping.

## Prerequisites
- [[hybrid-retrieval-rrf]]
- [[reranking]]

## In plain English

"This answer looks better" is not evidence — two retrieval pipelines can both produce fluent, confident answers, and only one of them is actually right. The fix is a **golden set**: a fixed collection of real questions where you already know the correct answer *and* which source chunk(s) support it. Run every candidate pipeline against the exact same golden set, and you get numbers you can actually compare — not vibes.

Retrieval eval measures the retriever specifically, in isolation from generation: for a given query, did the retriever's ranked list of chunk ids actually contain the chunk(s) that support the known-correct answer? This isolates retrieval quality from generation quality — a pipeline can retrieve the right chunk and still generate a bad answer from it (a generation problem), or generate a fluent answer that's ungrounded because retrieval never found the right chunk in the first place (a retrieval problem, dressed up as a "hallucination"). Measuring retrieval separately is what tells you which one you're actually looking at.

## Core mechanics

| Metric | Question it answers | Formula (generic, works on any ids) |
|---|---|---|
| Precision@k | Of the top k retrieved, how many are actually relevant? | `\|retrieved[:k] ∩ gold\| / k` |
| Recall@k | Of all relevant chunks that exist, how many did the top k retrieve? | `\|retrieved[:k] ∩ gold\| / \|gold\|` |
| MRR (Mean Reciprocal Rank) | How high up the ranking did the *first* relevant result land, averaged across the whole golden set? | `1 / rank_of_first_relevant_hit`, then averaged across queries |

Precision and recall answer different questions and can move in opposite directions — a retriever that returns 50 candidates can hit high recall (it probably contains the right chunk somewhere) while scoring low precision at k=50 (most of those 50 aren't relevant). MRR specifically rewards getting the *first* relevant hit near the top of the ranking, which matters most when only the top few results actually make it into the generation prompt.

## Sample code

Lab-sourced (Day 2 · Session 2 — `labs/Day2 Session 2 - RAG, Retrieval and Evaluation.ipynb`), generic metric functions plus the golden-set lookup pattern:

```python
def precision_at_k(retrieved: list[str], gold: set[str], k: int) -> float:
    return sum(1 for cid in retrieved[:k] if cid in gold) / k

def recall_at_k(retrieved: list[str], gold: set[str], k: int) -> float:
    return len(set(retrieved[:k]) & gold) / len(gold)

def mrr(retrieved: list[str], gold: set[str]) -> float:
    for i, cid in enumerate(retrieved, start=1):
        if cid in gold:
            return 1.0 / i
    return 0.0

# golden set: {"q": "...", "answer_contains": "<exact string>"}
# gold_chunks() finds the chunk(s) containing that string at scoring time —
# no manual chunk-id bookkeeping needed as the corpus changes
def gold_chunks(answer_contains: str, chunks: list[dict]) -> set[str]:
    return {c["cid"] for c in chunks if answer_contains in c["text"]}
```

The lab compares three pipeline variants against the same 12-question golden set, no LLM calls required (fast, free, deterministic): `v_dense` (naive dense only), `v_fused` (hybrid, no rerank), `v_full` (hybrid + cross-encoder rerank).

## Alternatives

Retrieval eval metrics themselves are standard information-retrieval formulas, not a product with competing vendors — there's no "alternatives table" in the usual sense. The comparable choice is *framework* for running this kind of eval at scale: hand-rolled functions (as in the lab, and the boring/simple default), versus a dedicated RAG eval framework like Ragas/DeepEval/TruLens (covered together in [[llm-judges-eval]]), which adds LLM-judged metrics (faithfulness, answer relevancy) on top of these deterministic retrieval-only ones.

## How this shows up in the capstone

Milestone 4 (production RAG + evaluation baseline) — the golden-set harness (12 questions, `gold_chunks` lookup, precision/recall/MRR across `v_dense`/`v_fused`/`v_full`) is meant to be reused directly to prove future retrieval changes to the policy-RAG agent actually help, not just look different; see [[capstone-milestone-map]].

## Interview fire round

- **Q: Is a hallucinated-sounding RAG answer usually a generation problem or a retrieval problem?**
  A: Usually retrieval — if every claim in the answer traced back to a retrieved chunk, checking that trace would catch the failure immediately. Most "the model made this up" cases are actually "the retriever never surfaced the right chunk," which better retrieval eval catches directly and a bigger/better model often can't fix on its own.
- **Q: Why build a golden set instead of just spot-checking a few example queries after each change?**
  A: A handful of examples can look convincing in either direction by chance, and doesn't detect regressions on the questions you didn't happen to check. A fixed, scored golden set turns "this seems better" into a comparable number (e.g. laptop-policy accuracy 72% → 68%) that catches regressions automatically, even ones no user has reported yet.

## Production gotchas & best practices

- Lab gotcha: chunk-level "gold" evidence is computed by searching for the known answer substring inside chunk text at scoring time (`gold_chunks`), rather than hand-maintaining a chunk-id-to-question mapping — this keeps the golden set valid even as the underlying chunking changes, at the cost of the golden set needing a genuinely unique, exact substring per question.
- Lab gotcha: groundedness scoring via an LLM judge is deliberately kept optional/sampled, not run for every question on every pipeline variant — judging every answer for every variant is hundreds of LLM calls, easily exhausting a free tier; see [[llm-judges-eval]].
- Production practice: log retrieval-eval runs over time (Langfuse `score_trace` per metric, per the lab's own Langfuse SDK v4 usage) so a regression shows up as a number moving, not as a support ticket — see [[langfuse-tracing]].
- Production practice: a golden set needs deliberate coverage of failure-prone categories (acronyms/exact ids, table-based rules, outdated-policy traps), not just easy representative questions — per course material (`presentations/day2.md`, Act 3 "Run the Same Test, Then Compare"), a 60-question set explicitly built this way is what actually separates two competing pipelines.

## Course vs. production

The lab's golden set is 12 questions over a small earthquake-records CSV — enough to demonstrate the harness, not enough to be statistically robust on its own. Production golden sets are typically much larger (the course material's own worked comparison example uses 60 questions across multiple failure-prone categories) and are re-run as a standing regression suite on every retrieval or prompt change, not built once and left static.

## Related
- **Builds on** — [[hybrid-retrieval-rrf]], [[reranking]]
- **Feeds into** — [[llm-judges-eval]]
- **Logged via** — [[langfuse-tracing]]

## Sources

**Lab sources**
- `lab-summaries/Day2-Session2-RAGRetrievalEval.md` (§ "Lab C — Proving It Works (Retrieval Evaluation)")
- `labs/Day2 Session 2 - RAG, Retrieval and Evaluation.ipynb`

**Web sources**
- Manning, Raghavan & Schütze — *Introduction to Information Retrieval* — canonical precision/recall/MRR definitions, cited per course material (`presentations/day2.md`, Act 3)
- Per course material (`presentations/day2.md`, Act 3 "Run the Same Test, Then Compare") — the 60-question worked comparison example, not independently web-verified as course-specific
