--- LINKEDIN ---
A regular database index — a B-tree, say — is built for exact or range lookups, not "which of my millions of stored vectors are closest to this one in 3072-dimensional space." Qdrant is purpose-built for exactly that question: store vectors plus arbitrary metadata, then query by similarity, optionally narrowed by that metadata.

A collection is a named set of points sharing one vector dimension and distance metric, created once up front. A point is one record: id, vector, payload. A payload index is required before filtering on that field at all — Qdrant Cloud's default strict mode rejects filters on unindexed fields outright rather than degrading gracefully.

client.create_collection(collection_name=COLLECTION,
    vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE))
client.create_payload_index(collection_name=COLLECTION,
    field_name="doc_type", field_schema=PayloadSchemaType.KEYWORD)

The gotcha that actually bites in production: point ids. Assigning them with uuid4() generates a new random id for the same content on every ingestion run — a re-run upserts duplicates instead of overwriting the originals, and the collection silently accumulates duplicates on every re-ingest. uuid5(namespace, f"{source}:{chunk_idx}") makes re-ingestion idempotent instead. Never change that namespace constant once chosen — every id derived from it changes too, orphaning all prior data.

Build the payload index before ingestion, not after — retrofitting one forces a full HNSW index rebuild instead of incrementally optimizing.

Are your point ids deterministic, or does every re-ingest quietly duplicate your collection?

#AppliedAI #RAG #LLM #VectorSearch

--- INSTAGRAM ---
A B-tree can't tell you what's nearest in 3072 dimensions. Qdrant can. 📍

Collection = shared dimension + metric. Point = id + vector + payload. Payload index required before filtering — no exceptions on Qdrant Cloud.

uuid4() duplicates every re-ingest. uuid5(namespace, source+chunk_idx) makes it idempotent.

Full mechanics + code in the carousel.

#AppliedAI #RAG #LLM #VectorSearch #GenAI

--- VISUAL FORMAT ---
carousel — 6 slides
1. Title — "A B-Tree Can't Answer \"Nearest In 3072 Dimensions\""
2. Core mechanics — collection, point, payload
3. Sample code — the index has to exist first (code)
4. The gotcha — random ids silently duplicate every re-ingest
5. Don't touch this once set — changing the namespace orphans everything
6. Takeaway — build the payload index before ingestion (closing question)
