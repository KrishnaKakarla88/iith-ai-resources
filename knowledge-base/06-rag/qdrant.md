---
stage: "06-rag"
tools: [qdrant-client, qdrant-cloud]
tags: [rag, vector-database, qdrant]
last_verified: 2026-08-20
verified_against: "qdrant-client 1.18.x (PyPI, current as of 2026-08-20) — not pinned in this repo's pyproject.toml"
---

# Qdrant

Qdrant is the vector database this course uses to store embedded chunks and search them by similarity — the storage and search engine underneath [[dense-retrieval]].

## Prerequisites
- [[embeddings-models]]
- [[chunking]]

## In plain English

Once a chunk of text is turned into an embedding vector ([[embeddings-models]]), it needs somewhere to live that can answer "which of my millions of stored vectors are closest to this new one?" fast. A regular database index (a B-tree, say) isn't built for that question — it's built for exact/range lookups, not "nearest in 3072-dimensional space." Qdrant is purpose-built for exactly that: store vectors plus whatever metadata you want attached to each one, then query by similarity, optionally narrowed by that metadata.

The lab uses Qdrant Cloud (the managed offering) rather than self-hosting, so the mental model is: create a collection once, upsert points into it as documents get ingested, then query it at answer time.

## Core mechanics

| Concept | What it means |
|---|---|
| Collection | A named set of points that all share the same vector dimension and distance metric — created once, up front |
| Point | One stored record: an id, a vector, and a payload — the unit both writes and reads operate on |
| Payload | Arbitrary structured metadata attached to a point (e.g. `{"source": "...", "doc_type": "pdf"}`) — not part of the vector, but filterable |
| Distance metric | How closeness between vectors is scored — `Distance.COSINE` is the course's default, matching Gemini embeddings |
| Payload index | A dedicated index on one payload field, required *before* filtering on that field — Qdrant Cloud's default strict mode outright rejects filters on unindexed fields rather than degrading gracefully |
| Deterministic point id | Assigning ids from a stable hash of source content (e.g. `uuid5(namespace, f"{source}:{chunk_idx}")`) rather than a random `uuid4()` makes re-ingestion idempotent — re-running ingestion upserts the same points instead of duplicating them |

## Sample code

Lab-sourced (Day 2 · Session 2 — `labs/Day2 Session 2 - RAG, Retrieval and Evaluation.ipynb`), collection creation, the required payload index, and a filtered query:

```python
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PayloadSchemaType, Filter, FieldCondition, MatchValue

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

client.create_collection(
    collection_name=COLLECTION,
    vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
)

# required before filtering on doc_type — Qdrant Cloud rejects unindexed-field filters
client.create_payload_index(
    collection_name=COLLECTION,
    field_name="doc_type",
    field_schema=PayloadSchemaType.KEYWORD,
)

hits = client.query_points(
    collection_name=COLLECTION,
    query=query_vector,
    limit=10,
    query_filter=Filter(must=[FieldCondition(key="doc_type", match=MatchValue(value="csv"))]),
)
```

`qdrant-client` is not pinned in this repo's `pyproject.toml` — the notebook installs it ad hoc rather than as a tracked project dependency, unlike `langgraph`/`litellm`/`fastmcp`. Current PyPI release as of this writing is 1.18.x.

## Alternatives

| Store | Where it lives | Boring/simple alternative to Qdrant? |
|---|---|---|
| Qdrant | Self-hosted (Rust, open-source) or Qdrant Cloud (managed) | — |
| [pgvector](https://github.com/pgvector/pgvector) | PostgreSQL extension | **Yes** — the boring option; if you already run Postgres, vectors live alongside the rest of your relational data with ACID guarantees and JOINs, at the cost of falling behind purpose-built engines at very large scale (roughly beyond ~10M vectors) |
| [Pinecone](https://www.pinecone.io/) | Fully managed, serverless, usage-billed (also offers BYOC) | No — same tier of dedicated vector search, but Pinecone hides index internals entirely (no self-hosting, no tunable index parameters) in exchange for zero ops |
| [Weaviate](https://docs.weaviate.io/weaviate) | Open-source; self-hosted (Docker/Kubernetes/embedded) or Weaviate Cloud | No — same tier as Qdrant, with a particular strength in built-in hybrid (vector + keyword) search and multi-tenant deployments as first-class features |

## How this shows up in the capstone

Milestone 4 (production RAG + evaluation baseline) — Qdrant is the vector store behind the policy-RAG agent's retrieval pipeline, holding the embedded, chunked policy corpus; see [[capstone-milestone-map]].

## Interview fire round

- **Q: Why does Qdrant Cloud require a payload index before you can filter on a field?**
  A: Qdrant combines vector search with filtering via a "filterable HNSW index" — payload indexes built before ingestion let the vector index generate filter-aware graph edges up front. Qdrant Cloud's default strict mode blocks filtering on unindexed fields entirely rather than silently degrading performance, so the index has to exist first, not be added as an afterthought.
- **Q: What actually breaks if point ids are assigned with `uuid4()` instead of a deterministic hash?**
  A: Re-running ingestion generates new random ids for the same underlying content every time, so a re-run upserts duplicate points instead of overwriting the originals — the collection silently accumulates duplicates on every re-ingest.

## Production gotchas & best practices

- Lab gotcha: a payload index on `doc_type` must exist *before* Qdrant Cloud will allow filtering on it — this is enforced, not just recommended, per `lab-summaries/Day2-Session2-RAGRetrievalEval.md`'s own gotchas list.
- Lab gotcha (`labs/production-notes.md`): deterministic point ids via `uuid5(NAMESPACE, f"{source}:{chunk_idx}")` make re-ingestion idempotent; random `uuid4()` duplicated every chunk on re-run. Never change the namespace constant once chosen — doing so orphans all prior data (every id derived from it changes, so nothing matches existing points anymore).
- Production practice: payload indexes should be created before data ingestion, not retrofitted — adding one after points already exist forces a full HNSW index rebuild rather than incrementally optimizing, per Qdrant's own documentation.
- Production practice: for hybrid retrieval at scale, Qdrant supports native sparse vectors (since v1.7.0) and a built-in RRF fusion query (`{"rrf": {}}` combining `prefetch` dense + sparse queries) — collapsing [[hybrid-retrieval-rrf]] into one DB-side call instead of two separate retrievers fused in application code.

## Course vs. production

The lab creates one collection per notebook run against Qdrant Cloud's free tier, with a small corpus (under 200 chunks across three documents) and no incremental-update story beyond re-running the whole ingestion cell. Production deployments size collections for real corpus growth, treat payload-index creation and point-id strategy as part of the initial schema design (not something fixed ad hoc mid-notebook), and often push retrieval fusion (RRF) into Qdrant's native hybrid query API rather than fetching two candidate lists and fusing them in application code.

## Related
- **Builds on** — [[embeddings-models]], [[chunking]]
- **Feeds into** — [[dense-retrieval]], [[hybrid-retrieval-rrf]]
- **Contrasts with** — pgvector, Pinecone, Weaviate (see Alternatives above)

## Sources

**Lab sources**
- `lab-summaries/Day2-Session2-RAGRetrievalEval.md` (§ "A3 Embed + index", § "Gotchas")
- `labs/production-notes.md` (§ "RAG Retrieval", § "Qdrant")
- `labs/Day2 Session 2 - RAG, Retrieval and Evaluation.ipynb`

**Web sources**
- [Qdrant — Collections concept docs](https://qdrant.tech/documentation/concepts/collections/) — collections/points/payload structure, distance metrics, accessed 2026-08-20
- [Qdrant — Indexing / payload index docs](https://qdrant.tech/documentation/concepts/indexing/#payload-index) — payload index required before ingestion, Qdrant Cloud strict-mode filter enforcement, accessed 2026-08-20
- [Qdrant — Hybrid Queries docs](https://qdrant.tech/documentation/concepts/hybrid-queries/) — native `rrf`/`dbsf` fusion over dense + sparse prefetch queries, accessed 2026-08-20
- [pgvector (GitHub, pgvector/pgvector)](https://github.com/pgvector/pgvector) — HNSW/IVFFlat index types, distance metrics, Postgres-native positioning, accessed 2026-08-20
- [Pinecone](https://www.pinecone.io/) — fully managed/serverless model, BYOC option, tiered usage-based pricing, accessed 2026-08-20
- [Weaviate docs — overview](https://docs.weaviate.io/weaviate) — open-source status, deployment options (Cloud/Docker/Kubernetes/embedded), built-in hybrid search, accessed 2026-08-20
