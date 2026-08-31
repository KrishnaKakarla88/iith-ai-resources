import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 5, "Interview Nugget", "\"Make It An Agent, Agents Are Impressive\"",
      ["A real scenario question on pushing back against unwarranted agent autonomy."])

slide(p("slide-02.png"), 2, 5, "The Question", "The Task Is Two Checks And A Branch",
      ["A PM insists on an agent for: refund an order if it's within 30 days and under $50, else escalate.",
       "How do you push back, concretely?"])

slide(p("slide-03.png"), 3, 5, "The Answer", "Name The Steps Back To Them",
      ["Check date, check amount, branch two ways — fully knowable ahead of time.",
       "That's the textbook signature of a workflow, not an agent."],
      code="check_date() -> check_amount() -> branch()  # fixed, enumerable")

slide(p("slide-04.png"), 4, 5, "The Cost", "Agent Autonomy Isn't Free Here",
      ["Unpredictable execution paths, more tokens and latency per decision, a much larger test surface — for zero benefit, since there's no discovery-dependent branching to earn autonomy's keep."])

slide(p("slide-05.png"), 5, 5, "Takeaway", "Ask For A Case The First Two Checks Don't Already Decide",
      ["If the PM can't name one, it's a workflow — not a weaker choice, the correct one."],
      closing_q="Has \"just make it an agent\" ever shown up as a requirement on your team?")

print("done: 45")
