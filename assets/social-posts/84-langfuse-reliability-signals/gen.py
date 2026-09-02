import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "A Silent Failure Passes Every Check You Wrote",
      ["Valid output, 200 response, no exception — and wrong. Errors and latency alone won't catch this class of failure."])

slide(p("slide-02.png"), 2, 6, "Signal One", "Prompt-Cache Hit Rate",
      ["A stable hit rate implies a stable request shape upstream.",
       "**Example:** hit rate drops 91% to 38% within five minutes of a one-line system-prompt edit — cost roughly tripled with zero change in error rate. Nothing paged anyone."])

slide(p("slide-03.png"), 3, 6, "Signal Two", "Context Size, Not Just A Cost Line",
      ["Attention doesn't scale uniformly with context length — a request quietly growing from 6K to 64K input tokens degrades answer quality non-uniformly, not just latency and cost.",
       "Correlate rising input tokens with p95 latency and user-correction rate together, not token count alone."])

slide(p("slide-04.png"), 4, 6, "Signal Three", "Cost-Anomaly Triage Order",
      ["Cost is a lagging signal — by the time the bill moves, the cause has usually run for hours.",
       "Rule out traffic first, then cache hit rate, then retrieval depth, then a silent retry loop, then session length. Stop at the first plausible cause and you'll be back next week."])

slide(p("slide-05.png"), 5, 6, "Signal Four", "Canary Queries And The Refusal Rate",
      ["Known-answer requests run continuously — a system that can't answer them has drifted.",
       "Watch refusal rate in both directions: too few refusals is as much a warning sign as too many. A zero error rate is a claim that needs checking, not a result worth celebrating."])

slide(p("slide-06.png"), 6, 6, "Takeaway", "None Of These Show Up As An Error",
      ["They show up as a rate moving on a dashboard nobody was watching — which is exactly why they need to be watched continuously, not reviewed monthly as a cost line."],
      closing_q="Which of these four signals is actually on your dashboard today?")

print("done: 84")
