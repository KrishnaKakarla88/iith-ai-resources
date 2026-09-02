import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "A Node Is Just A Function — No Base Class, No Decorator",
      ["That plainness is deliberate: because a node is a regular callable, you can unit-test it with a hand-built state dict, no graph, no checkpointer, no model call."])

slide(p("slide-02.png"), 2, 6, "Two Kinds Of Node", "Deterministic vs. The One That Calls A Model",
      ["A rule expressible in code shouldn't be paid for in model variance.",
       "\"Let the model produce, let deterministic code decide\" — an LLM node can produce a new draft, a deterministic node still decides whether it passes."])

slide(p("slide-03.png"), 3, 6, "Sample Code", "Both Callable Directly, No Graph Required",
      [],
      code="def check_document(state):\n    issues = run_policy_checks(state[\"draft\"])\n    return {\"issues\": issues, \"issue_log\": issues}\n\n# unit-testable without a graph, a model, or a checkpointer:\nresult = check_document({\"draft\": \"...\", \"issues\": [], \"issue_log\": [], \"revision_count\": 0})")

slide(p("slide-04.png"), 4, 6, "The Failure Case", "A Failed Model Call Returns None By Design",
      ["Every LLM node needs an explicit fallback — a node that doesn't handle a failed call silently propagates None into state, which then breaks whatever reads that field next."])

slide(p("slide-05.png"), 5, 6, "Production Practice", "Mock The Model Call, Not The Node",
      ["Because nodes are plain functions, keep the LLM-call wrapper at each caller's own module namespace — that's what lets patch() target it per-module even after refactoring shared control flow out."])

slide(p("slide-06.png"), 6, 6, "Takeaway", "Force-Set Identity Fields Inside The Node Itself",
      ["Never trust an upstream LLM tool-call argument for an authorization-critical field — overwrite it unconditionally before it reaches anything downstream."],
      closing_q="Could you unit-test your busiest node right now, with nothing but a dict?")

print("done: 68")
