import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 5, "Interview Nugget", "A Handoff Summary Loses The \"Why\"",
      ["A real scenario question on why an agent redoes work another agent already ruled out — even with a summary in hand."])

slide(p("slide-02.png"), 2, 5, "The Question", "The Receiving Agent Redoes Rejected Work",
      ["The handoff includes a summary of the conclusion. Why does this happen anyway?"])

slide(p("slide-03.png"), 3, 5, "The Answer", "Conclusions Read As The Important Part — Rejections Don't",
      ["Natural-language summaries favor conclusions because they read as the point.",
       "Assumptions, rejected alternatives, and confidence levels look like supporting detail and get compressed out first — even though that detail is exactly what stops re-deriving the same dead end."])

slide(p("slide-04.png"), 4, 5, "The Fix", "State Carries Facts, Not Vibes",
      ["Not a longer summary. Structure the handoff payload to carry rejected alternatives and confidence as first-class fields, not prose the receiving agent has to infer intent from."])

slide(p("slide-05.png"), 5, 5, "Takeaway", "The Same Discipline As Write-Scoped Fields",
      ["Exactly what supervisor-worker teams already apply to findings and fact_check — structured fields, never freeform narrative standing in for facts."],
      closing_q="Does your handoff payload carry rejected paths, or just the conclusion?")

print("done: 80")
