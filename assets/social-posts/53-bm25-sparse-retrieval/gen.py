import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "It Either Contains The Token Or It Doesn't",
      ["BM25 scores documents by exact term overlap with a query — deterministic, cheap, immune to the way embeddings can miss an exact code."])

slide(p("slide-02.png"), 2, 6, "Core Mechanics", "Rarity, Saturation, Length",
      ["**Term frequency**: how often a query term appears — diminishing returns, ten repeats don't count ten times as much.",
       "**Inverse document frequency**: rare terms across the corpus weigh more than common ones.",
       "**Length normalization**: stops long documents winning purely by being long."])

slide(p("slide-03.png"), 3, 6, "Sample Code", "Tokenization Is Entirely Your Job",
      ["rank_bm25 does no preprocessing — forgetting to apply the *same* tokenization at index time and query time silently degrades match quality."],
      code="from rank_bm25 import BM25Okapi\n\ntokenized_corpus = [chunk[\"text\"].lower().split() for chunk in chunks]\nbm25 = BM25Okapi(tokenized_corpus)\nscores = bm25.get_scores(query.lower().split())")

slide(p("slide-04.png"), 4, 6, "The Crash Gotcha", "Empty Corpus = ZeroDivisionError",
      ["BM25Okapi divides by average document length internally — an empty corpus crashes retrieval outright instead of returning an empty result list.",
       "Guard for it explicitly before calling get_scores()."])

slide(p("slide-05.png"), 5, 6, "Why It Still Matters", "\"Good Enough\" Embeddings Are Still Probabilistic",
      ["An embedding model's success at matching an exact SKU or case number depends on embedder quality and how distinct that token is in the corpus.",
       "BM25 offers a guarantee dense search can't."])

slide(p("slide-06.png"), 6, 6, "Takeaway", "Cache The Index, Don't Rebuild It Per Request",
      ["Reloading a full corpus index from scratch on every call is slow and unnecessary when the corpus hasn't changed."],
      closing_q="Does your retrieval pipeline have an exact-match guarantee, or is it all probabilistic?")

print("done: 53")
