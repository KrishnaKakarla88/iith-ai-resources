import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "One Loop Under Every Agent Pattern",
      ["ReAct and reflection are the same four moves, repeated, wearing different clothes."])

slide(p("slide-02.png"), 2, 6, "The Four Moves", "Perceive, Plan, Act, Observe",
      ["Not an LLM invention — the same shape as an OODA loop or a control-system feedback loop.",
       "What's specific to an agentic loop is who owns step two: plan is handed to the model, not hardcoded."],
      diagram=("flow", ["Perceive", "Plan", "Act", "Observe"]))

slide(p("slide-03.png"), 3, 6, "What Makes It Agentic", "Plan Is Delegated To The Model",
      ["Your code doesn't decide which tool gets called next — the model's output does.",
       "That single delegation is the difference from a plain while loop with an LLM call in it."])

slide(p("slide-04.png"), 4, 6, "Core Mechanics", "The Abstract Shape",
      ["Every concrete instance — tool-calling loop, ReAct — is this shape with a different plan() implementation."],
      code="for i in range(MAX_ITERATIONS):\n    decision = plan(state)          # delegated to the model\n    if decision.is_final: return decision.output\n    result = act(decision)          # your code executes this\n    state = observe(state, result)")

slide(p("slide-05.png"), 5, 6, "Core Mechanics", "State Accumulates Across Iterations",
      ["Each pass sees everything gathered so far — the messages list, or a thought/action/observation trace.",
       "\"Act\" is still always your code's job: the model's output is a request, never an action."])

slide(p("slide-06.png"), 6, 6, "Takeaway", "A Repair Loop Isn't Usually \"Agentic\"",
      ["It has no tool/action step, and its plan is fixed by your code, not chosen by the model — closer to a workflow than an agent."],
      closing_q="Can you point to the exact line where your loop delegates the plan step to the model?")

print("done: 41")
