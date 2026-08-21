---
stage: "06-rag"
tools: [rank_bm25]
tags: [rag, retrieval, bm25, sparse]
last_verified: 2026-08-20
verified_against: "rank_bm25 (not pinned in this repo's pyproject.toml — installed ad hoc in the lab notebook)"
---

# BM25 / sparse retrieval

BM25 is a keyword-based ranking algorithm that scores documents by exact term overlap with a query — deterministic, cheap, and immune to the ways embedding-based search can miss an exact code or id.

## Prerequisites
- [[ingestion]]

## In plain English

Sparse retrieval means most of the "vector" describing a document is zero — it's really a big table of "does this document contain this word, and how often." BM25 (**B**est **M**atch **25**) scores a query against every document by summing, for each query term the document contains, a weight based on how rare that term is across the corpus (rarer terms count more) and how densely it appears in this particular document (with diminishing returns — ten repeats of the same word don't count ten times as much as one), normalized against document length so long documents don't win purely by being long.

The practical reason this still matters next to a modern embedding model: dense (semantic) search is good at "this means roughly the same thing," but an exact invoice number, SKU, or acronym isn't a *meaning* — it's a token, and dense search's success at matching it is probabilistic, not guaranteed. BM25 either contains the exact token or it doesn't — deterministic, independent of embedding quality.

## Core mechanics

| Concept | What it means |
|---|---|
| Term frequency (TF) | How often a query term appears in a document — with saturation, so repetition has diminishing returns |
| Inverse document frequency (IDF) | Rare terms across the corpus are weighted higher than common ones |
| Document length normalization | Prevents long documents from scoring higher purely by containing more words |
| Tokenization | BM25 implementations (like `rank_bm25`) do **no** text preprocessing themselves — lowercasing, stopword removal, and tokenizing are the caller's responsibility |
| `BM25Okapi` | The classic Okapi BM25 variant — the one used in this course's lab; `rank_bm25` also ships BM25L, BM25+, and BM25-Adpt variants |

BM25 improves on older TF-IDF scoring specifically by adding term-frequency saturation and document-length normalization — the two knobs that keep it from over-rewarding either repetition or sheer document size.

## Sample code

Lab-sourced (Day 2 · Session 2 — `labs/Day2 Session 2 - RAG, Retrieval and Evaluation.ipynb`):

```python
from rank_bm25 import BM25Okapi

# tokenize once at index build time — rank_bm25 does no preprocessing itself
tokenized_corpus = [chunk["text"].lower().split() for chunk in chunks]
bm25 = BM25Okapi(tokenized_corpus)

def bm25_search(query: str, k: int) -> list[str]:
    if not tokenized_corpus:
        return []  # guard: BM25Okapi raises ZeroDivisionError on an empty corpus
    scores = bm25.get_scores(query.lower().split())
    ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
    return [chunks[i]["cid"] for i in ranked[:k]]
```

`rank_bm25` is not pinned in this repo's `pyproject.toml` — installed ad hoc in the notebook rather than tracked as a project dependency, same as `qdrant-client` and `sentence-transformers`.

## Alternatives

| Approach | Where it lives | Boring/simple alternative? |
|---|---|---|
| `rank_bm25` (`BM25Okapi`) | Pure-Python, `dorianbrown/rank_bm25` on GitHub | — |
| Elasticsearch / OpenSearch (built-in BM25 scoring) | Self-hosted or managed search engine | No — same underlying algorithm, but a full search engine rather than an in-process library |
| Qdrant sparse vectors (BM25-style, first-class since v1.7.0) | Same vector DB already used for dense search ([[qdrant]]) | No — heavier setup, but collapses sparse + dense into one store instead of two |
| Plain Python `Counter`-based exact/substring match | Stdlib only, no dependency | **Yes** — the boring option; catches exact-token hits with no ranking sophistication, fine when the corpus is small and matches are truly exact |

## How this shows up in the capstone

Milestone 4 (production RAG + evaluation baseline) — BM25 is the deterministic half of the policy-RAG agent's hybrid retriever, guaranteeing exact-term recall (policy IDs, SKUs) that dense search alone can't promise; see [[capstone-milestone-map]].

## Interview fire round

- **Q: Why does BM25 still matter when embeddings are "good enough" for most queries?**
  A: "Good enough" is still probabilistic for exact identifiers — an embedding model's success at matching an exact SKU or case number depends on embedder quality and how distinct that token is in the corpus. BM25 either contains the exact token or it doesn't, which is a guarantee dense search can't offer.
- **Q: What's the practical failure mode of skipping the empty-corpus guard?**
  A: `BM25Okapi` divides by average document length internally — on an empty corpus that's a division by zero, an unhandled `ZeroDivisionError` that crashes retrieval instead of returning an empty result list.

## Production gotchas & best practices

- Lab gotcha: `BM25Okapi` raises `ZeroDivisionError` on an empty corpus — guard for it explicitly before calling `get_scores`, per `labs/production-notes.md`.
- Lab gotcha: `rank_bm25` does no text preprocessing — lowercasing/stopword removal/stemming are the caller's job; forgetting to apply the *same* tokenization at index time and query time silently degrades match quality.
- Production practice: cache/lazy-load the BM25 index (and any embedder) as a singleton rather than rebuilding it per request — reloading a full corpus index from scratch on every call is slow and unnecessary when the corpus hasn't changed, per `labs/production-notes.md`.
- Production practice: at real scale, an in-process `rank_bm25` index doesn't horizontally scale or persist independently — production systems with large or frequently-updated corpora typically move sparse scoring into Elasticsearch/OpenSearch or a vector DB's native sparse-vector support instead.

## Course vs. production

The lab builds one in-memory `BM25Okapi` index per notebook run over a small demo corpus — fine for a few hundred chunks, rebuilt fresh each time. Production systems with larger, continuously-updated corpora typically move sparse retrieval into a dedicated search engine (Elasticsearch/OpenSearch) or a vector database's native sparse-vector support, so the index persists, updates incrementally, and doesn't have to be rebuilt in-process on every deploy.

## Related
- **Builds on** — [[ingestion]], [[chunking]]
- **Contrasts with** — [[dense-retrieval]]
- **Feeds into** — [[hybrid-retrieval-rrf]]

## Sources

**Lab sources**
- `lab-summaries/Day2-Session2-RAGRetrievalEval.md` (§ "A6 BM25 + hybrid RRF", § "Gotchas")
- `labs/production-notes.md` (§ "RAG Retrieval")
- `labs/Day2 Session 2 - RAG, Retrieval and Evaluation.ipynb`

**Web sources**
- [rank_bm25 (GitHub, dorianbrown/rank_bm25)](https://github.com/dorianbrown/rank_bm25) — `BM25Okapi` API, no built-in preprocessing, accessed 2026-08-20
