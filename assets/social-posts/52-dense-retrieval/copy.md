--- LINKEDIN ---
Dense retrieval ranks documents by embedding-vector similarity to a query. That's what makes semantic search possible: a query for "can I return a laptop late?" can retrieve a chunk saying "electronics must be returned within 14 days" — zero shared exact words, same meaning. That strength is also its blind spot.

An embedding captures meaning, and an exact SKU, case number, or acronym often isn't meaningfully different from a similar-looking one in vector space. Whether dense search finds the exact right record for an exact identifier is probabilistic — dependent on embedder quality and how distinct that identifier actually is from its neighbors — not guaranteed.

hits = client.query_points(collection_name=COLLECTION, query=query_vector, limit=k,
    query_filter=Filter(must=[FieldCondition(key="doc_type", match=MatchValue(value=doc_type))]))

A metadata filter like this is an exact, structural constraint. Embedding "only look at CSV files" into the query text instead isn't a guarantee the vector search will respect it — it's just another signal competing with the rest of the query's meaning.

Production practice worth internalizing: retrieving more candidates isn't automatically safer. Every extra chunk in the eventual generation context competes for the model's attention and adds cost/latency. Over-fetch into a pool only when a reranking stage follows — dense search's job in a two-stage pipeline is recall, not final precision.

A recall@k of 1.0 on a small, clean corpus with a strong embedder is a best case, not a guarantee — production corpora are noisier and more likely to have near-duplicate identifiers.

Would your retriever survive two SKUs that differ by one digit?

#AppliedAI #RAG #LLM #VectorSearch

--- INSTAGRAM ---
Dense retrieval is great at meaning. Terrible at exact tokens. 🔍

"Can I return a laptop late?" matches "must be returned within 14 days" — zero shared words, same meaning.

But an exact SKU or case number? Probabilistic, not guaranteed — that's embedder-dependent, not a promise.

Metadata filters are exact. Query text isn't.

Full mechanics + code in the carousel.

#AppliedAI #RAG #LLM #VectorSearch #GenAI

--- VISUAL FORMAT ---
carousel — 6 slides
1. Title — "Good At Meaning, Blind To Exact Tokens"
2. The strength — no shared words required
3. The blind spot — exact identifiers are probabilistic
4. Sample code — metadata filters vs query text (code)
5. Production practice — fetching more isn't automatically safer
6. Takeaway — recall@k=1.0 is a best case (closing question)
