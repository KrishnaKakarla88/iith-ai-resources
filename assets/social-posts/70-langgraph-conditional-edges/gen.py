import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "\"Always Go To B\" Becomes \"Go Wherever This Function Says\"",
      ["A conditional edge routes at runtime by calling a function on current state — and that function must contain no model call."])

slide(p("slide-02.png"), 2, 6, "The Slogan", "Decide In A Node, Route In An Edge",
      ["Whatever fuzzy judgment needs to happen — did the draft pass, which category is this — happens inside a node and gets written to state as a plain value.",
       "The edge that follows just reads that value. Pure state -> str, unit-testable without a graph or a model."])

slide(p("slide-03.png"), 3, 6, "Sample Code", "The Loop-Guarded Router Behind Every Capped Loop",
      [],
      code="def route_after_checks(state):\n    if state[\"issues\"] and state[\"revision_count\"] < MAX_REVISIONS:\n        return \"revise\"\n    return \"approval\"  # clean, or max revisions hit -> escalate, don't loop forever")

slide(p("slide-04.png"), 4, 6, "The Common Bug", "An Unmapped Return Value Fails At Run Time",
      ["If route_fn can return a value not present as a key in path_map, that's a run-time error, not a compile-time one — it can hide until a rare state combination triggers it."])

slide(p("slide-05.png"), 5, 6, "Production Practice", "Validate The Router's Output Before It Reaches The Edge",
      ["An LLM-produced category string is untrusted input to a router exactly like any other tool argument — fall back to a deterministic default rather than letting an unmapped value crash the run."])

slide(p("slide-06.png"), 6, 6, "Takeaway", "A State Guard Is The Real Exit Condition",
      ["LangGraph's recursion_limit is only the crash-instead-of-design backstop — a guard like revision_count < MAX_REVISIONS is what should actually stop the loop."],
      closing_q="If your router returned a value nobody mapped, would your graph crash gracefully or hang?")

print("done: 70")
