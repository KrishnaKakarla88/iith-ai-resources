import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "You Can't Just Add Two Incompatible Scores",
      ["A cosine similarity and a BM25 score aren't comparable numbers — hybrid retrieval fuses dense and sparse search without ever touching either raw score."])

slide(p("slide-02.png"), 2, 6, "The Trick", "Fuse By Rank Position, Not By Score",
      ["Reciprocal Rank Fusion throws away raw scores and uses only where a chunk lands in each ranked list.",
       "A chunk ranking well in both dense and sparse search wins big; a chunk only one method surfaced still gets partial credit."],
      diagram=("flow", ["Dense ranks", "Sparse ranks", "RRF sum 1/(c+rank)", "Re-sorted list"]))

slide(p("slide-03.png"), 3, 6, "Core Mechanics", "One Constant, No Tuning",
      ["c (commonly 60) dampens the impact of very top ranks so one method's #1 doesn't automatically dominate the fused result."],
      code="def rrf_fuse(rankings, k=10, c=60):\n    scores = {}\n    for ranking in rankings:\n        for rank, cid in enumerate(ranking, start=1):\n            scores[cid] = scores.get(cid, 0.0) + 1.0 / (c + rank)\n    return sorted(scores, key=scores.get, reverse=True)[:k]")

slide(p("slide-04.png"), 4, 6, "Not A Nice-To-Have", "The Only Guarantee Against Missed Identifiers",
      ["For domains with exact identifiers — SKUs, case numbers — hybrid isn't a tuning improvement, it's the only way to guarantee an exact match isn't missed, since dense search's success there is probabilistic and BM25's isn't."])

slide(p("slide-05.png"), 5, 6, "Production Practice", "c=60 Is A Default, Not A Knob To Tune First",
      ["Treat it as a well-tested constant from the original paper's benchmarking across domains, rather than something to re-tune per corpus before anything else."])

slide(p("slide-06.png"), 6, 6, "Takeaway", "No Score Normalization, No Blend Weight",
      ["That's the entire simplicity story versus a weighted linear combination that has to be re-tuned every time either retriever changes."],
      closing_q="Is your retrieval pipeline blending incompatible scores, or fusing by rank?")

print("done: 54")
