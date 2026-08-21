---
stage: "06-rag"
tools: [qdrant-client, langchain-google-genai]
tags: [rag, retrieval, dense, vector-search]
last_verified: 2026-08-20
verified_against: "qdrant-client (not pinned in this repo's pyproject.toml — installed ad hoc in the lab notebook)"
---

# Dense retrieval

Dense retrieval ranks documents by embedding-vector similarity to a query — good at "this means roughly the same thing," blind to exact tokens it wasn't trained to treat as distinctive.

## Prerequisites
- [[embeddings-models]]
- [[qdrant]]

## In plain English

"Dense" describes the shape of the vector: every dimension has a (usually non-zero) value, in contrast to a sparse BM25-style representation where almost every dimension is zero. To search, you embed the query with the same model used to embed the corpus ([[embeddings-models]]), then ask the vector database for the stored vectors closest to it — closeness usually measured by cosine similarity.

This is what makes semantic search possible: a query for "can I return a laptop late?" can retrieve a chunk that says "electronics must be returned within 14 days" even though they don't share a single exact word. That strength is also its blind spot — an embedding captures *meaning*, and an exact SKU, case number, or acronym often isn't meaningfully different from a similar-looking one in vector space. Whether dense search finds the exact right record for an exact identifier is probabilistic — dependent on embedder quality and how distinct that identifier actually is from its neighbors — not guaranteed the way [[bm25-sparse-retrieval]] is.

## Core mechanics

| Concept | What it means |
|---|---|
| Embed query | Query text is converted to a vector with the same embedding model used at index time |
| Similarity/distance | Cosine similarity is the standard metric paired with modern embedding models — Qdrant collections declare this at creation time |
| Approximate nearest neighbor (ANN) | Vector DBs don't scan every vector for an exact top-k — they use an index structure (e.g. HNSW) that trades a small amount of accuracy for large speed gains at scale |
| Metadata filter | A `Filter` restricting the search to points matching a payload condition (e.g. `doc_type="csv"`) — requires a payload index to exist first on Qdrant Cloud, see [[qdrant]] |
| `k` / `pool` | How many nearest results to return — often over-fetched into a larger pool for a later reranking or fusion stage rather than requested at the final display size directly |

## Sample code

Lab-sourced (Day 2 · Session 2 — `labs/Day2 Session 2 - RAG, Retrieval and Evaluation.ipynb`), with an optional metadata filter:

```python
from qdrant_client.models import Filter, FieldCondition, MatchValue

def dense_search(query: str, k: int, doc_type: str | None = None) -> list[str]:
    query_vector = embedder.embed_query(query)          # see embeddings-models.md
    flt = None
    if doc_type:
        flt = Filter(must=[FieldCondition(key="doc_type", match=MatchValue(value=doc_type))])
    hits = client.query_points(
        collection_name=COLLECTION,
        query=query_vector,
        limit=k,
        query_filter=flt,
    )
    return [point.id for point in hits.points]
```

`qdrant_client` is not pinned in this repo's `pyproject.toml` — installed ad hoc in the notebook, unlike `langgraph`/`litellm`/`fastmcp`, which are tracked project dependencies. As of this writing the current release on PyPI is `qdrant-client` 1.18.x.

## Alternatives

Dense retrieval as a *technique* isn't tied to one vector database — see [[qdrant]]'s Alternatives table for the store-level comparison (pgvector, Pinecone, Weaviate). At the technique level, the main alternative axis is what dense retrieval is combined with, not what replaces it outright — [[bm25-sparse-retrieval]] (exact-term guarantee) and [[reranking]] (precision on the retrieved pool) are complements, not substitutes.

## How this shows up in the capstone

Milestone 4 (production RAG + evaluation baseline) — dense retrieval is one leg of the policy-RAG agent's hybrid retriever ([[hybrid-retrieval-rrf]]), and the `dense_search` function with a `doc_type` filter is reused directly; see [[capstone-milestone-map]].

## Interview fire round

- **Q: If a SOTA embedder gets recall@k ≈ 1.0 on its own, why bother with hybrid at all?**
  A: That result is specific to a strong embedder and a corpus without near-duplicate/colliding identifiers — the lab's own eval notes the gap would widen with a cheaper embedder or ids that look alike (near-duplicate SKUs, case numbers, acronyms). Hybrid makes the exact-match guarantee independent of embedder quality, rather than betting on it holding in every domain.
- **Q: Why filter on metadata instead of just embedding the filter condition into the query text?**
  A: A metadata filter is an exact, structural constraint (only search `doc_type="csv"`) — embedding "only look at CSV files" into the query text is not a guarantee the vector search will actually respect it, it's just another signal competing with the rest of the query's meaning.

## Production gotchas & best practices

- Lab gotcha: dense search on exact identifiers is probabilistic, not guaranteed — even a strong embedder like `gemini-embedding-001` handling a distinctive id well in one run doesn't generalize to every corpus; per `lab-summaries/Day2-Session2-RAGRetrievalEval.md` this is embedder- and record-distinctness-dependent.
- Lab gotcha: a metadata filter (`doc_type`) requires a payload index to exist on Qdrant Cloud *before* it can be used — filtering on an unindexed field is rejected outright under Qdrant Cloud's default strict mode, see [[qdrant]].
- Production practice: retrieving more candidates ("just fetch 50 instead of 10") is not automatically safer — every extra chunk in the eventual generation context competes for the model's attention and adds cost/latency; tighter, filtered retrieval often beats wider retrieval, per course material (`presentations/day2.md`, Act 2 "Context Dilution in Retrieval").
- Production practice: over-fetch into a pool (`pool` > final `k`) when a reranking stage follows — dense search's job in a two-stage pipeline is recall, not final precision.

## Course vs. production

The lab's honest result — naive dense-only retrieval already hitting recall@k ≈ 1.0 with a strong embedder on a small, clean corpus — is a best case, not a guarantee. Production corpora are larger, noisier, and more likely to contain near-duplicate or colliding identifiers, which is exactly where dense-only retrieval's probabilistic weak spot on exact matches shows up; production RAG pipelines default to hybrid ([[hybrid-retrieval-rrf]]) rather than relying on dense search alone once the corpus stops being small and clean.

## Related
- **Builds on** — [[embeddings-models]]
- **Contrasts with** — [[bm25-sparse-retrieval]]
- **Feeds into** — [[hybrid-retrieval-rrf]], [[reranking]]
- **Runs against** — [[qdrant]]

## Sources

**Lab sources**
- `lab-summaries/Day2-Session2-RAGRetrievalEval.md` (§ "A4 Dense search + metadata filter", § "A5 Exact identifiers: dense vs keyword")
- `labs/Day2 Session 2 - RAG, Retrieval and Evaluation.ipynb`

**Web sources**
- [Qdrant — Filtering docs](https://qdrant.tech/documentation/concepts/filtering/) — payload filter conditions, accessed 2026-08-20
- Per course material (`presentations/day2.md`, Act 2 "Context Dilution in Retrieval") — retrieval-width-vs-attention framing, not independently web-verified as course-specific
