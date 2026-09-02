import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "A Static Edge Carries No Logic Of Its Own",
      ["After node A finishes, always run node B next — same destination, every run, regardless of what state contains."])

slide(p("slide-02.png"), 2, 6, "Two Mandatory Edges", "START And END Aren't Optional",
      ["Every graph needs one edge from the built-in START marker into the first node, and one from the last node into END — a node with no outgoing edge never finishes that branch."])

slide(p("slide-03.png"), 3, 6, "Sample Code", "A Human Already Decided The Step Order",
      ["extract -> validate -> post: only extract touches a model. Every edge here is static."],
      code="builder.add_edge(START, \"extract\")\nbuilder.add_edge(\"extract\", \"validate\")\nbuilder.add_edge(\"validate\", \"post\")\nbuilder.add_edge(\"post\", END)")

slide(p("slide-04.png"), 4, 6, "Static Fan-Out", "Multiple Edges From One Node Run Concurrently",
      ["Legal, finance, and compliance specialists all start from START in the same superstep, then converge on one merge node — no branching logic needed, just parallel static paths."],
      diagram=("flow", ["START", "legal / finance / compliance", "merge", "END"]))

slide(p("slide-05.png"), 5, 6, "The Test", "Can You Enumerate The Paths Right Now?",
      ["If every run visits the same steps in the same order regardless of state, a static edge is the right choice — a conditional edge would just be unused machinery."])

slide(p("slide-06.png"), 6, 6, "Takeaway", "A Graph Of Only Static Edges Is Functionally A Chain",
      ["Durability (checkpointing/resume) and branching are separate reasons to reach for LangGraph — a long fixed sequence can still want one without the other."],
      closing_q="Does your graph have a single conditional edge, or is it a chain wearing graph machinery?")

print("done: 69")
