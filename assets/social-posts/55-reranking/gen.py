import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "Fast Enough For Millions, Never That Precise",
      ["Dense and BM25 retrieval score a query against a document without ever letting the two directly interact — a reranker is the second pass that finally lets them."])

slide(p("slide-02.png"), 2, 6, "Bi-Encoder vs. Cross-Encoder", "The Model Never Reads Both Together — Until Now",
      ["**Bi-encoder**: query and document encoded separately, compared by cheap distance math. Fast, scales to a full corpus.",
       "**Cross-encoder**: a (query, document) pair as joint input, one relevance score for that specific pair. Accurate, but can't be precomputed."])

slide(p("slide-03.png"), 3, 6, "Why Two Stages", "Recall At Scale, Then Precision On A Pool",
      ["A cross-encoder scoring an entire corpus per query is far too slow — stage one narrows millions of documents to ~10-50 candidates, only that pool gets the expensive treatment."],
      diagram=("flow", ["Corpus", "Hybrid search (broad)", "Pool of ~10", "Cross-encoder (precise)"]))

slide(p("slide-04.png"), 4, 6, "Sample Code", "One Score Per Candidate Pair",
      ["A small CPU-friendly cross-encoder reranking the hybrid-fused pool."],
      code="from sentence_transformers import CrossEncoder\n\nreranker = CrossEncoder(\"cross-encoder/ms-marco-MiniLM-L-6-v2\")\npairs = [(query, chunk_text_by_id[cid]) for cid in candidate_ids]\nscores = reranker.predict(pairs)")

slide(p("slide-05.png"), 5, 6, "The Honest Finding", "Reranking Barely Moves Exact-Token Lookups",
      ["A cross-encoder judges meaning, not exact-match — it has little to improve once hybrid retrieval already surfaced (or missed) the right chunk on pure token grounds.",
       "Measure with a golden set — don't assume reranking always helps."])

slide(p("slide-06.png"), 6, 6, "Takeaway", "Reranking Latency Scales With Pool Size",
      ["Not corpus size — tune the stage-1 candidate count as the actual latency knob."],
      closing_q="Have you measured whether reranking is earning its latency cost on your corpus?")

print("done: 55")
