---
stage: "06-rag"
tools: [sentence-transformers]
tags: [rag, retrieval, reranking, cross-encoder]
last_verified: 2026-08-20
verified_against: "sentence-transformers, cross-encoder/ms-marco-MiniLM-L-6-v2 (not pinned in this repo's pyproject.toml)"
---

# Reranking

Reranking is a second-pass model that re-scores a small pool of already-retrieved candidates for precision — cheap enough to run only there, too slow to run over an entire corpus.

## Prerequisites
- [[hybrid-retrieval-rrf]]

## In plain English

[[dense-retrieval]] and [[bm25-sparse-retrieval]] are both "bi-encoder"-style, or purely lexical — they score a query against a document without ever letting the two directly interact; a query's vector and a document's vector are computed independently, then compared by a cheap distance calculation. That's what makes them fast enough to run over millions of documents. But it also caps their precision: the model never actually reads the query and the document *together*.

A cross-encoder reranker does exactly that — it takes a `(query, document)` pair as joint input and outputs one relevance score for that specific pair, letting the model attend across both texts at once. That's much more accurate, but also far more expensive: you can't precompute anything, since the score only exists for a specific query+document pair, and scoring the whole corpus this way for every query would be far too slow. The answer is a two-stage pipeline: a fast, broad first pass (dense/BM25/hybrid) narrows millions of documents down to a pool of ~10-50 candidates, and only that small pool gets the expensive cross-encoder treatment.

## Core mechanics

| Concept | What it means |
|---|---|
| Bi-encoder | Encodes query and document separately, compares via cheap vector math — what dense retrieval uses; fast, scales to a full corpus |
| Cross-encoder | Encodes a `(query, document)` pair jointly, outputs one relevance score per pair — accurate, but scored one pair at a time |
| Two-stage retrieval | Stage 1 (cheap, broad) optimizes for recall over the whole corpus; stage 2 (reranker) optimizes for precision over a small pool | 
| Pool size | How many stage-1 candidates get reranked — large enough to likely contain the right answer, small enough to stay fast (the lab reranks a fused top-10) |
| Late interaction (ColBERT-style) | A middle ground between bi- and cross-encoders — token-level matching without a cross-encoder's full pairwise cost; not used in this course's lab, mentioned as the more scalable alternative |

## Sample code

Lab-sourced (Day 2 · Session 2 — `labs/Day2 Session 2 - RAG, Retrieval and Evaluation.ipynb`), a small CPU-friendly cross-encoder reranking the hybrid-fused pool:

```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def rerank(query: str, candidate_ids: list[str], k: int) -> list[str]:
    pairs = [(query, chunk_text_by_id[cid]) for cid in candidate_ids]
    scores = reranker.predict(pairs)
    ranked = [cid for cid, _ in sorted(zip(candidate_ids, scores), key=lambda x: x[1], reverse=True)]
    return ranked[:k]

def retrieve(query: str, k: int = 5, pool: int = 10) -> list[str]:
    return rerank(query, hybrid_search(query, k=pool, pool=pool), k=k)
```

`sentence-transformers` is not pinned in this repo's `pyproject.toml` — installed ad hoc in the notebook, same as `qdrant-client` and `rank_bm25`. `cross-encoder/ms-marco-MiniLM-L-6-v2` is trained on the MS MARCO passage-ranking dataset and is small enough to run on CPU at interactive speed.

## Alternatives

| Approach | Where it lives | Boring/simple alternative? |
|---|---|---|
| `sentence-transformers` `CrossEncoder` (self-hosted) | Open-source, `huggingface/sentence-transformers` | — |
| [Cohere Rerank](https://cohere.com/rerank) (hosted API) | Managed API, no local model to run | No — same tier of cross-encoder-style reranking, hosted instead of self-run |
| ColBERT / ColBERTv2 (late interaction) | Open-source, token-level matching | No — different architecture tier, trades some of the cross-encoder's accuracy for much better scalability |
| Skip reranking; take hybrid's fused top-k directly | No extra model at all | **Yes** — the boring option; the lab's own eval shows this barely costs anything on exact-token lookups, since reranking is a semantic tool that doesn't move pure identifier matches |

## How this shows up in the capstone

Milestone 4 (production RAG + evaluation baseline) — the cross-encoder reranker sits between hybrid retrieval and answer generation in the policy-RAG agent (`retrieve()` = hybrid fuse → rerank → top-k), with the golden-set eval proving whether it actually helps; see [[capstone-milestone-map]].

## Interview fire round

- **Q: Why not just run the cross-encoder over the whole corpus and skip the first retrieval stage entirely?**
  A: A cross-encoder scores one `(query, document)` pair at a time with no precomputation possible — running it over an entire corpus for every query is far too slow (quadratic-ish cost per query). The first stage's job is recall at scale; the reranker's job is precision over a small, already-narrowed pool.
- **Q: The lab found reranking barely changed results on exact-identifier queries. Why?**
  A: Cross-encoder rerankers are a semantic relevance tool — they judge how well text *means* what the query means. An exact identifier match or miss isn't primarily a meaning judgment, so reranking has little to improve once hybrid retrieval has already surfaced (or missed) the right chunk on pure token grounds.

## Production gotchas & best practices

- Lab gotcha: reranking doesn't help pure exact-token lookups — it's a semantic tool, and the lab's own eval shows `hybrid+rerank` scoring close to `hybrid (fused)` alone on identifier-style golden questions; don't expect a reranker to fix a retrieval gap that's really a hybrid/BM25 gap.
- Lab gotcha (`labs/production-notes.md`): lazy `@lru_cache(maxsize=1)`-style singleton loading for the cross-encoder (and the embedder) matters — reloading model weights from disk per request/instance is slow and unnecessary when the model doesn't change between calls.
- Production practice: reranking latency scales with pool size, not corpus size — tune the pool (stage-1 candidate count) as the actual latency knob, not the final `k`.
- Production practice: a hosted reranking API (e.g. Cohere Rerank) trades self-hosting/GPU management for per-call cost and network latency — the right tradeoff depends on call volume and whether GPU infrastructure is already available for other parts of the stack.

## Course vs. production

The lab's honest finding — reranking barely moves the needle on a corpus dominated by exact-identifier lookups — is corpus-specific, not a general verdict on reranking. Production corpora with more paraphrase-heavy, ambiguous, or long-document queries (rather than short exact-id lookups) typically see reranking contribute meaningfully more, which is exactly why the lab's own methodology — measure with a golden set rather than assume — is the transferable lesson, not the specific "barely helps" result itself.

## Related
- **Builds on** — [[hybrid-retrieval-rrf]]
- **Feeds into** — [[grounded-answers-injection-defense]]
- **Evaluated by** — [[retrieval-eval-metrics]]

## Sources

**Lab sources**
- `lab-summaries/Day2-Session2-RAGRetrievalEval.md` (§ "B1 Cross-encoder rerank", § "Lab C — Proving It Works", § "Gotchas")
- `labs/production-notes.md` (§ "RAG Retrieval")
- `labs/Day2 Session 2 - RAG, Retrieval and Evaluation.ipynb`

**Web sources**
- [cross-encoder/ms-marco-MiniLM-L6-v2 (Hugging Face model card)](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2) — MS MARCO training data, CPU-friendly throughput, accessed 2026-08-20
- [Sentence Transformers — Cross-Encoder usage docs](https://sbert.net/docs/cross_encoder/usage/usage.html) — `CrossEncoder` API, joint-pair scoring, accessed 2026-08-20
- Per course material (`presentations/day2.md`, Act 2 "What is Reranking? / Two-Stage Pipeline") — bi-encoder vs cross-encoder framing, ColBERT late-interaction mention
