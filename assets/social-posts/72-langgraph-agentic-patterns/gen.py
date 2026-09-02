import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 7, "Concept", "\"Until It Is Good\" Is Not A Termination Condition",
      ["ReAct, Planner-Executor, and Reflection are all loops — and every loop in this stack needs an explicit, state-based exit condition plus a hard cap as backstop."])

slide(p("slide-02.png"), 2, 7, "ReAct", "Designed Against Calling The Same Tool Forever",
      ["tools_condition alone can loop forever against a stubborn model — always AND it with a step cap in the conditional edge."],
      code="def capped_tools_condition(state):\n    if state[\"steps\"] >= REACT_STEP_CAP:\n        return \"end\"\n    return tools_condition(state)")

slide(p("slide-03.png"), 3, 7, "Planner-Executor", "One Plan Up Front, One Step Per Visit",
      ["The known trap: a plan goes stale if executing step 2 invalidates step 3's assumptions.",
       "The production fix is replanning — an edge back to the planner after execution, at the cost of one extra model call."])

slide(p("slide-04.png"), 4, 7, "Reflection", "The Critic Shares The Generator's Blind Spots",
      ["Same model, same training — self-critique catches sloppiness, not ignorance.",
       "If a deterministic checker exists for the property you care about, use that as the critic and keep the model only for repair."],
      code="def route_after_critique(state):\n    if state[\"verdict\"] == \"PASS\" or state[\"rounds\"] >= MAX_REFLECT_ROUNDS:\n        return \"end\"\n    return \"revise\"")

slide(p("slide-05.png"), 5, 7, "Why The Critic Sees Less", "Independence Is The Entire Value Of The Separate Node",
      ["The critic sees only the rules and the current draft, never the generator's reasoning — seeing the chain of thought would make it rubber-stamp the draft instead of judging it."])

slide(p("slide-06.png"), 6, 7, "Production Gotcha", "Two Layers Of Loop Termination, Not One",
      ["A state-based guard as the intentional exit, and recursion_limit only as the backstop that turns an undesigned loop into a crash instead of a silent hang."])

slide(p("slide-07.png"), 7, 7, "Takeaway", "Every Named Pattern Is A Specialization Of One Shape",
      ["ReAct is shape 4. Planner-Executor and Reflection are shape 5 variants. Knowing the shape underneath tells you exactly what to cap and where."],
      closing_q="Does your reflection loop have a deterministic checker available, or only a model critiquing itself?")

print("done: 72")
