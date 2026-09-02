--- LINKEDIN ---
Semantic search is really a geometry question. An embedding model turns text into a fixed-length vector such that texts with similar meaning land close together in that space — feed it a query, feed it a corpus, and "similar meaning" becomes "how close are these two points."

Dimension is the length of that vector, fixed per model — it has to match on both the write (indexing) and read (query) side. Cosine similarity is the default distance metric paired with most modern embedding models. Matryoshka Representation Learning lets one model's output be truncated to a shorter, still-usable vector, trading quality for smaller storage.

This stack pairs Groq for chat (llama-3.1-8b-instant) with Gemini for embeddings — a deliberate mismatch. Embedding quality and chat quality are separate capabilities; nothing requires the same vendor for both.

from langchain_google_genai import GoogleGenerativeAIEmbeddings
embedder = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
# disk cache: sha1(text) -> embedding, batches of 90, 60s pause

The gotcha: switching embedding models isn't a config change. Every existing vector lives in the old model's space — mixing old and new vectors makes distances meaningless. The whole corpus has to be re-embedded and the collection rebuilt at the new dimension, never appended to in place.

Pin the exact model name and dimension in config, not just code that happens to work today — a silent provider-side upgrade can change the vector space entirely.

Do you know exactly which embedding model and dimension your index was built with?

#AppliedAI #RAG #LLM #AIEngineering

--- INSTAGRAM ---
Semantic search is just geometry. 📐

Embedding model turns text into a vector — similar meaning, close points. Dimension is fixed per model, must match on write and read.

This stack: Groq for chat, Gemini for embeddings — different vendors, different capability.

Switch embedding models later? You're not appending — you're re-embedding the whole corpus.

Full mechanics in the carousel.

#AppliedAI #RAG #LLM #AIEngineering #GenAI

--- VISUAL FORMAT ---
carousel — 6 slides
1. Title — "Semantic Search Is Actually A Geometry Question"
2. Core mechanics — dimension, distance, MRL
3. Chat and embeddings don't have to match — different vendor, different capability
4. Sample code — cache and throttle (code)
5. The gotcha — switching embedding models isn't a config change
6. Takeaway — pin the exact model + dimension (closing question)
