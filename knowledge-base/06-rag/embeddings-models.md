---
stage: "06-rag"
tools: [langchain-google-genai, gemini-embedding-001]
tags: [rag, embeddings, gemini]
last_verified: 2026-08-20
verified_against: "lab notebook uses gemini-embedding-001, not pinned in this repo's pyproject.toml"
---

# Embeddings models

An embedding model turns text into a fixed-length vector of numbers such that texts with similar meaning land close together in that vector space — the piece that makes semantic ([[dense-retrieval]]) search possible at all.

## Prerequisites
- [[what-is-an-llm]]
- [[chunking]]

## In plain English

A dense retriever doesn't compare text to text — it compares vectors to vectors. The embedding model is what produces those vectors: feed it a chunk of text, get back a list of floats (its "dimension"). Feed it a query, get back another list of floats in the same space. "Similar meaning" then becomes a geometry question — how close are these two points? — which a vector database like [[qdrant]] can answer very fast over millions of points.

This course deliberately uses a **different provider for embeddings than for chat**: Groq (`llama-3.1-8b-instant`) generates text, Gemini generates embeddings. There's no requirement that these be the same vendor — embedding quality and chat quality are separate capabilities, and a model that's fast/cheap for one isn't necessarily the best or even available for the other. See [[model-selection-cost-latency-tradeoffs]] for the fuller reasoning behind pairing providers this way.

## Core mechanics

| Concept | What it means |
|---|---|
| Dimension | Length of the output vector (e.g. 3072 floats) — fixed per model, must match on both write (indexing) and read (query) sides |
| Distance metric | How "closeness" between two vectors is measured — cosine similarity is the default pairing with most modern embedding models, including Gemini's |
| Matryoshka Representation Learning (MRL) | A training technique (used by `gemini-embedding-001`) that lets the same model's output be truncated to a shorter, still-usable vector — trading some quality for smaller storage/faster search |
| Batching & throttling | Embedding APIs are typically rate-limited (requests/min, requests/day); production and course code alike batch texts and pause between batches to stay under quota |
| Disk cache | Caching embeddings by a hash of their input text (e.g. sha1) avoids re-embedding unchanged chunks on every pipeline re-run — saves both quota and latency |

### The plan-vs-lab discrepancy, resolved

This knowledge base's own plan document initially assumed the embedding model would be `text-embedding-004` at 768 dimensions. **The lab notebook (Day 2 · Session 2) actually uses `gemini-embedding-001`, whose default output is 3072 dimensions** (truncatable to 1536 or 768 via MRL, with Google recommending 3072/1536/768 as the supported cut points). Per the project's own rule — lab/notebook wins over the plan's inline description on API specifics — **`gemini-embedding-001` at 3072-dim is the correct answer for this codebase**, not `text-embedding-004`/768-dim. `text-embedding-004` is an older, separate Gemini embedding model; the two are not interchangeable, and vectors from one cannot be queried against an index built from the other.

If a Qdrant collection is created with `size=768` and later fed 3072-dim vectors (or vice versa), inserts fail outright — the dimension is fixed at collection-creation time (see [[qdrant]]).

## Sample code

Lab-sourced (Day 2 · Session 2 — `labs/Day2 Session 2 - RAG, Retrieval and Evaluation.ipynb`), wrapped with a disk cache and a throttle to survive the free tier (100 req/min, 1000/day):

```python
from langchain_google_genai import GoogleGenerativeAIEmbeddings

embedder = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")

# disk cache: sha1(text) -> embedding, stored under .embcache/
# batches of 90 texts, 60s pause between batches
# exponential backoff (1, 2, 4, 8s) on HTTP 429

def embed_texts(texts: list[str]) -> list[list[float]]:
    cached, to_embed = split_cached(texts)          # lab helper, not shown
    fresh = embedder.embed_documents(to_embed)       # batched + throttled internally
    save_to_cache(to_embed, fresh)
    return merge(cached, fresh)
```

`langchain_google_genai` is not pinned in this repo's `pyproject.toml` — the notebook installs it ad hoc, unlike `litellm`/`langgraph`/`fastmcp` which are tracked project dependencies.

## Alternatives

| Model / provider | Where it lives | Boring/simple alternative? |
|---|---|---|
| `gemini-embedding-001` | Google Gemini API | — |
| OpenAI `text-embedding-3-large`/`-small` | OpenAI API | No — same tier of hosted API embedding, different vendor |
| Cohere Embed v4 | Cohere API | No — same tier, adds native multimodal (image) embedding support |
| Open-weight `sentence-transformers` models (e.g. `all-MiniLM-L6-v2`, BGE, E5 families) | Self-hosted, `huggingface/sentence-transformers` | **Yes** — the boring option; no per-call API cost or rate limit, but you own the hosting/GPU, and quality on niche domains often trails current hosted SOTA models without fine-tuning |

## How this shows up in the capstone

Milestone 4 (production RAG + evaluation baseline) — every chunk in the policy-RAG agent's ingestion pipeline is embedded with this model before indexing into [[qdrant]]; see [[capstone-milestone-map]].

## Interview fire round

- **Q: Why can Groq (chat) and Gemini (embeddings) be different vendors in the same pipeline?**
  A: Embedding and chat generation are separate capabilities with separate cost/latency/quality tradeoffs — nothing requires them to come from the same provider, and picking the strongest/cheapest option per capability is normal, not a workaround.
- **Q: What breaks if you change embedding models after a corpus is already indexed?**
  A: Every existing vector is in the old model's space — mixing old and new vectors in one index makes distances meaningless. The whole corpus has to be re-embedded and the collection rebuilt at the new dimension, not appended to in place.

## Production gotchas & best practices

- Lab gotcha: the free embedding tier caps at 100 requests/min and 1000/day — the notebook's disk cache (sha1-keyed JSON under `.embcache/`) and batch throttle (batches of 90, 60s pause, exponential backoff on 429) exist specifically to survive that quota; delete `.embcache/` to force a fresh re-embed.
- Lab gotcha: dense search on exact identifiers (an SKU, a case number) is only *probabilistic* — a strong embedder handles distinctive ids well in practice, but this depends on embedder quality and record distinctness, not a guarantee; see [[hybrid-retrieval-rrf]] for why exact-identifier domains need BM25 as a backstop, not just a stronger embedder.
- Production practice: pin the exact model name and dimension in config, not just in code that happens to work — a silent provider-side model upgrade can change output dimensions or the underlying vector space entirely.
- Production practice: budget embedding cost per token up front for a corpus of known size before committing to a model/provider — pricing is per input token and scales with corpus size and re-embedding frequency, not a one-time cost.

## Course vs. production

The lab throttles and caches to survive a free-tier quota — a classroom constraint. Production embedding pipelines usually run on a paid tier sized to the actual corpus and re-embedding cadence, and treat model/dimension choice as a versioned, deliberately-changed decision (with a migration plan for re-indexing), not something fixed once at notebook-writing time and left alone.

## Related
- **Builds on** — [[chunking]]
- **Feeds into** — [[dense-retrieval]], [[qdrant]]
- **Contrasts with** — [[bm25-sparse-retrieval]] (no embedding model involved at all)
- **See also** — [[fine-tuning-vs-rag]], [[model-selection-cost-latency-tradeoffs]]

## Sources

**Lab sources**
- `lab-summaries/Day2-Session2-RAGRetrievalEval.md` (§ "A3 Embed + index", § "A5 Exact identifiers: dense vs keyword")
- `labs/Day2 Session 2 - RAG, Retrieval and Evaluation.ipynb`

**Web sources**
- [Google Developers Blog — Gemini Embedding now generally available](https://developers.googleblog.com/gemini-embedding-available-gemini-api/) — `gemini-embedding-001`, default 3072-dim, MRL truncation to 1536/768, accessed 2026-08-20
- [Gemini API — Embeddings docs](https://ai.google.dev/gemini-api/docs/embeddings) — model capabilities, input token limit, accessed 2026-08-20
