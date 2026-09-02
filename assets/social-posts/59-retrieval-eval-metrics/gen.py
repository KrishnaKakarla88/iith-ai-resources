import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "\"This Looks Better\" Is Not Evidence",
      ["Two retrieval pipelines can both produce fluent, confident answers — only one is actually right. A golden set turns that into a number."])

slide(p("slide-02.png"), 2, 6, "Three Metrics", "Precision, Recall, MRR",
      ["**Precision@k**: of the top k retrieved, how many are actually relevant?",
       "**Recall@k**: of all relevant chunks that exist, how many did the top k retrieve?",
       "**MRR**: how high up did the first relevant result land, averaged across the set?"])

slide(p("slide-03.png"), 3, 6, "Sample Code", "Formulas That Work On Any Chunk Ids",
      [],
      code="def precision_at_k(retrieved, gold, k):\n    return sum(1 for c in retrieved[:k] if c in gold) / k\n\ndef mrr(retrieved, gold):\n    for i, cid in enumerate(retrieved, start=1):\n        if cid in gold:\n            return 1.0 / i\n    return 0.0")

slide(p("slide-04.png"), 4, 6, "Why Measure The Retriever Separately", "Isolates Retrieval From Generation",
      ["A pipeline can retrieve the right chunk and still generate a bad answer (generation problem), or generate a fluent answer that's ungrounded because retrieval never found the right chunk (a retrieval problem dressed up as \"hallucination\")."])

slide(p("slide-05.png"), 5, 6, "Precision And Recall Disagree", "They Can Move In Opposite Directions",
      ["Fetching 50 candidates can hit high recall (the right chunk is probably in there) while scoring low precision at k=50 (most of those 50 aren't relevant)."])

slide(p("slide-06.png"), 6, 6, "Takeaway", "A Golden Set Catches Regressions Nobody Reported",
      ["A handful of spot-checked examples can look convincing by chance in either direction — a fixed, scored set turns \"seems worse\" into a number that moves."],
      closing_q="Is a hallucinated-looking answer on your system actually a retrieval problem in disguise?")

print("done: 59")
