---
stage: "06-rag"
tags: [rag, retrieval, hybrid, rrf]
last_verified: 2026-08-20
verified_against: "lab notebook implementation, no external RRF library used"
---

# Hybrid retrieval (RRF)

Hybrid retrieval runs dense and sparse search separately, then fuses their two ranked lists into one with Reciprocal Rank Fusion — getting BM25's exact-match guarantee and dense search's semantic recall without hand-tuning a blend weight.

## Prerequisites
- [[dense-retrieval]]
- [[bm25-sparse-retrieval]]
- [[embeddings-models]]

## In plain English

Dense and sparse retrieval fail in complementary ways: dense search is strong on paraphrase and concepts but can miss an exact SKU, case number, or acronym; BM25 is strong on exact terms but blind to synonyms and rephrasing. Running both and picking whichever "looks more relevant" isn't a real strategy — the two methods produce scores on completely different, incompatible scales (a cosine similarity and a BM25 score aren't comparable numbers), so you can't just add them together or pick a max.

Reciprocal Rank Fusion sidesteps that problem entirely by throwing away the raw scores and using only *rank position*. For every ranked list a chunk appears in, it earns `1/(c + rank)` points (rank starting at 1, `c` a constant, commonly 60); a chunk's final score is the sum of that across every list it showed up in, and the results are re-sorted by that sum. A chunk that ranks well in both dense and sparse search wins big; a chunk that only one method surfaced still gets partial credit instead of being discarded.

## Core mechanics

| Concept | What it means |
|---|---|
| Rank, not score | RRF fuses based on *position* in each ranked list, never the raw similarity/BM25 score — this is exactly why it needs no score normalization or blend weight |
| `c` (rank constant) | Dampens the impact of very top ranks so one method's #1 doesn't automatically dominate; 60 is the conventional default from the original paper |
| `pool` | Each individual retriever (dense, BM25) is queried for more candidates than the final `k`, so RRF has enough overlap to actually fuse over |
| Requirement, not optimization | For domains with exact identifiers (SKUs, case numbers, acronyms), hybrid isn't a nice-to-have tuning improvement — it's the only way to guarantee the exact match isn't missed, since dense's success there is probabilistic and BM25's is not |

## Sample code

Lab-sourced (Day 2 · Session 2 — `labs/Day2 Session 2 - RAG, Retrieval and Evaluation.ipynb`):

```python
def rrf_fuse(rankings: list[list[str]], k: int = 10, c: int = 60) -> list[str]:
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, cid in enumerate(ranking, start=1):
            scores[cid] = scores.get(cid, 0.0) + 1.0 / (c + rank)
    ranked = sorted(scores, key=scores.get, reverse=True)
    return ranked[:k]

def hybrid_search(query: str, k: int = 10, pool: int = 10) -> list[str]:
    return rrf_fuse(
        [dense_search(query, pool), bm25_search(query, pool)],
        k=k,
    )
```

This is a from-scratch, ~10-line implementation — the lab does not reach for an external RRF library, since the algorithm is simple enough that hand-rolling it is clearer than adding a dependency.

## Alternatives

| Approach | Where it lives | Boring/simple alternative? |
|---|---|---|
| Hand-rolled RRF (as above) | Plain Python, no dependency | — |
| Qdrant native hybrid query (`Fusion.RRF` in `query_points`) | Built into `qdrant-client`, once sparse vectors are stored alongside dense in the same collection | No — same algorithm, but pushes the fusion into the vector DB instead of application code |
| Weighted linear score combination (min-max normalize both scores, then blend) | Common hand-rolled alternative | No — trades RRF's rank-only simplicity for a blend weight that has to be tuned per corpus and re-tuned when either retriever changes |
| Learned re-ranking model trained to combine both signals | ML-based, heavier | No — solves the same problem with a trained model instead of a fixed formula; higher ceiling, much higher setup cost |

The genuinely "boring" option here is really just RRF itself relative to a weighted blend — it's the simplicity story: no score normalization, no weight to tune, one constant (`c`) that rarely needs changing.

## How this shows up in the capstone

Milestone 4 (production RAG + evaluation baseline) — `hybrid_search` (dense + BM25 fused via RRF) is the policy-RAG agent's default retrieval path, feeding into [[reranking]] before an answer is generated; see [[capstone-milestone-map]].

## Interview fire round

- **Q: Why RRF instead of normalizing and averaging the dense and BM25 scores directly?**
  A: Cosine similarity and a BM25 score live on different, incomparable scales with different distributions — normalizing them well is fiddly and corpus-dependent. RRF avoids the problem entirely by using only rank position, which is directly comparable across any two ranking methods.
- **Q: What did the lab's own evaluation actually show hybrid buying over dense alone?**
  A: With a strong embedder on a clean corpus, dense alone already scored recall@k ≈ 1.0 and MRR ≈ 0.95 — already strong. Hybrid edged MRR to ≈1.0 and, more importantly, made exact recall a *guarantee* via BM25 rather than a probabilistic outcome — the gap would widen with a weaker embedder or colliding identifiers.

## Production gotchas & best practices

- Lab gotcha: fuse by rank, never by raw score — dense and BM25 scores are on incompatible scales, and the lab's own production notes call this out explicitly (`labs/production-notes.md`, § "RAG Retrieval").
- Lab gotcha: reranking barely moves pure exact-token lookups after hybrid fusion — cross-encoder rerankers are a semantic tool, so `hybrid + rerank` scores land close to `hybrid (fused)` alone on identifier-style queries; don't expect reranking to fix what hybrid retrieval already solved.
- Production practice: treat `c=60` as a reasonable, well-tested default rather than a knob to tune per corpus first — the constant mainly affects how much top ranks are dampened, and the original paper's benchmarking already settled on it as a sane default across domains.
- Production practice: when both retrievers are backed by the same vector database (as with Qdrant's native sparse-vector support), pushing RRF fusion into the DB's own hybrid query API avoids a network round trip per retriever and keeps fusion logic in one place.

## Course vs. production

The lab hand-rolls `rrf_fuse` in ~10 lines and calls it directly from Python — appropriate for a notebook where the two retrievers (a BM25 index and a Qdrant dense query) are already both accessible in-process. Production systems at scale often push RRF into the vector database itself (Qdrant's native `Fusion.RRF` hybrid query, once sparse vectors are stored in the same collection as dense ones) rather than fetching two independently-scored candidate lists and fusing them in application code — fewer round trips, and one less place for the two retrievers' candidate pools to drift out of sync.

## Related
- **Builds on** — [[dense-retrieval]], [[bm25-sparse-retrieval]]
- **Feeds into** — [[reranking]], [[grounded-answers-injection-defense]]
- **Evaluated by** — [[retrieval-eval-metrics]]

## Sources

**Lab sources**
- `lab-summaries/Day2-Session2-RAGRetrievalEval.md` (§ "A6 BM25 + hybrid RRF", § "Lab C — Proving It Works")
- `labs/production-notes.md` (§ "RAG Retrieval")
- `labs/Day2 Session 2 - RAG, Retrieval and Evaluation.ipynb`

**Web sources**
- [Cormack, Clarke, Büttcher — Reciprocal Rank Fusion outperforms Condorcet and individual rank learning methods (SIGIR 2009)](https://research.google/pubs/reciprocal-rank-fusion-outperforms-condorcet-and-individual-rank-learning-methods/) — the original RRF paper, `1/(c+rank)` formula, `c=60` convention, accessed 2026-08-20
- [Qdrant — Hybrid Queries docs](https://qdrant.tech/documentation/concepts/hybrid-queries/) — native `Fusion.RRF` support over dense + sparse vectors in one collection, accessed 2026-08-20
