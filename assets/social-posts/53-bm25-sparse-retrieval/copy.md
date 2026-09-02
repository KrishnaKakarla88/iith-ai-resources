--- LINKEDIN ---
BM25 scores documents by exact term overlap with a query — deterministic, cheap, and immune to the way embedding-based search can miss an exact code. Sparse means most of the "vector" describing a document is zero — it's really a table of "does this document contain this word, and how often."

Term frequency counts how often a query term appears, with saturation — ten repeats of a word don't count ten times as much as one. Inverse document frequency weighs rare terms higher than common ones. Length normalization stops long documents winning purely by containing more words.

from rank_bm25 import BM25Okapi
tokenized_corpus = [chunk["text"].lower().split() for chunk in chunks]
bm25 = BM25Okapi(tokenized_corpus)

rank_bm25 does zero text preprocessing — lowercasing, stopword removal, tokenizing are entirely the caller's job, and applying different tokenization at index time versus query time silently degrades match quality.

The crash gotcha: BM25Okapi divides by average document length internally, so an empty corpus is an unhandled ZeroDivisionError, not an empty result list. Guard for it explicitly.

Why this still matters next to a strong embedder: "good enough" semantic matching on an exact SKU or case number is still probabilistic, dependent on embedder quality and how distinct that token is in the corpus. BM25 either contains the exact token or it doesn't — a guarantee dense search can't offer.

Does your retrieval pipeline have an exact-match guarantee, or is it all probabilistic?

#AppliedAI #RAG #LLM #AIEngineering

--- INSTAGRAM ---
It either contains the word or it doesn't. No probability involved. 🎯

BM25: term frequency (with saturation) + rarity weighting + length normalization. Deterministic, cheap.

bm25 = BM25Okapi(tokenized_corpus)

Zero preprocessing built in — tokenize the same way at index and query time or matches silently degrade.

Full mechanics in the carousel.

#AppliedAI #RAG #LLM #AIEngineering #GenAI

--- VISUAL FORMAT ---
carousel — 6 slides
1. Title — "It Either Contains The Token Or It Doesn't"
2. Core mechanics — rarity, saturation, length
3. Sample code — tokenization is entirely your job (code)
4. The crash gotcha — empty corpus = ZeroDivisionError
5. Why it still matters — "good enough" embeddings are still probabilistic
6. Takeaway — cache the index (closing question)
