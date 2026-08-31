import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "Checking Is Easier Than Generating Right",
      ["The same model that produced a flawed draft can often catch its own mistake when asked to check."])

slide(p("slide-02.png"), 2, 6, "What's Different", "Shape vs Goal-Satisfaction",
      ["The repair loop checks shape — valid JSON, right types.",
       "Reflection checks whether the answer actually satisfies the goal given the evidence gathered."])

slide(p("slide-03.png"), 3, 6, "The Loop", "One Critique, One Correction",
      ["A critique call replies APPROVED or REVISE — on REVISE, exactly one more call fixes it.",
       "Capped by design, same reasoning as capping ReAct's iterations."],
      diagram=("flow", ["Draft", "Critique", "Revise?", "Final"]))

slide(p("slide-04.png"), 4, 6, "Sample Code", "One Verdict, One Format",
      ["The critique prompt carries the goal, the evidence, and the draft — nothing more."],
      code='"""Reply with exactly one of:\nAPPROVED\nREVISE: <one sentence on what\'s wrong>"""')

slide(p("slide-05.png"), 5, 6, "Discipline", "Fail Open, Not Fake-Approved",
      ["No key, an outage — skip the critique and return the original draft, labeled SKIPPED.",
       "A broken quality pass should never block the pipeline from answering at all."])

slide(p("slide-06.png"), 6, 6, "Takeaway", "A Model Critiquing Itself Shares Its Own Blind Spots",
      ["Catches arithmetic slips and obvious gaps well — not a substitute for an independent eval on anything higher-stakes than a quality nudge."],
      closing_q="Where would one extra critique call be worth the latency in your pipeline?")

print("done: 44")
