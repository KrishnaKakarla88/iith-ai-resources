--- LINKEDIN ---
Dense and sparse retrieval fail in complementary ways: dense is strong on paraphrase but can miss an exact SKU; BM25 is strong on exact terms but blind to synonyms. Running both and picking whichever "looks more relevant" isn't a real strategy — a cosine similarity and a BM25 score live on completely different, incomparable scales. You can't add them or take a max.

Reciprocal Rank Fusion sidesteps that entirely by throwing away raw scores and using only rank position. For every ranked list a chunk appears in, it earns 1/(c + rank) points; the final score is the sum across every list it showed up in.

def rrf_fuse(rankings, k=10, c=60):
    scores = {}
    for ranking in rankings:
        for rank, cid in enumerate(ranking, start=1):
            scores[cid] = scores.get(cid, 0.0) + 1.0 / (c + rank)
    return sorted(scores, key=scores.get, reverse=True)[:k]

A chunk ranking well in both dense and sparse search wins big. A chunk only one method surfaced still gets partial credit instead of being discarded.

For domains with exact identifiers, hybrid isn't a nice-to-have tuning improvement — it's the only way to guarantee a match isn't missed, since dense search's success there is probabilistic and BM25's isn't. Treat c=60 as a well-tested default from the original paper's benchmarking, not a knob to tune first.

No score normalization, no blend weight to re-tune every time either retriever changes — that's the entire simplicity case for RRF over a weighted linear combination.

Is your retrieval pipeline blending incompatible scores, or fusing by rank?

#AppliedAI #RAG #LLM #VectorSearch

--- INSTAGRAM ---
You can't add a cosine similarity to a BM25 score. They live on different planets. 🔀

RRF fixes this by fusing on rank position only — 1/(c + rank), summed across every ranked list a chunk shows up in.

def rrf_fuse(rankings, k=10, c=60): ...

No normalization, no blend weight to tune. Just ranks.

Full mechanics in the carousel.

#AppliedAI #RAG #LLM #VectorSearch #GenAI

--- VISUAL FORMAT ---
carousel — 6 slides
1. Title — "You Can't Just Add Two Incompatible Scores"
2. The trick — fuse by rank position (diagram)
3. Core mechanics — one constant, no tuning (code)
4. Not a nice-to-have — the only guarantee against missed identifiers
5. Production practice — c=60 is a default, not a knob to tune first
6. Takeaway — no score normalization, no blend weight (closing question)
