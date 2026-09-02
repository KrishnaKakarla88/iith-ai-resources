import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "A Node Returns A Partial Update, Never The Whole State",
      ["The engine merges just the keys a node touched into the running state using a per-key reducer — not a blind overwrite of everything."])

slide(p("slide-02.png"), 2, 6, "Core Mechanics", "Default Reducer Is \"Last Write Wins\"",
      ["Exactly right for a routing decision. Exactly wrong for a running list of messages — which is why reducers are opt-in per field, via Annotated[type, reducer]."],
      code="class ApprovalState(TypedDict):\n    draft: str                          # overwrite\n    issues: list[str]                   # overwrite — control field\n    issue_log: Annotated[list[str], add]  # accumulate — audit trail\n    revision_count: int                  # overwrite")

slide(p("slide-03.png"), 3, 6, "The Design Pattern", "Control Fields vs. Audit Fields",
      ["A field a router reads to decide what happens next must stay overwrite-only, or it never becomes empty again once anything has failed once.",
       "A separate accumulate field preserves full history for debugging without corrupting the field the router depends on."])

slide(p("slide-04.png"), 4, 6, "The Crash Guard", "Two Nodes, Same Key, No Reducer",
      ["InvalidUpdateError — the engine refuses to silently pick a winner between two conflicting writes in the same superstep."])

slide(p("slide-05.png"), 5, 6, "Production Gotcha", "A TypedDict Is Not Runtime-Validated",
      ["A misspelled key in a node's return value silently creates a dead channel nothing ever reads, rather than raising.",
       "Print or inspect state after every node during development — that's what catches it early."])

slide(p("slide-06.png"), 6, 6, "Takeaway", "Facts The Graph Acts On Are Control Fields",
      ["Everything the graph remembers for a human or a trace is an audit field. Mixing the two is the most common state-design bug."],
      closing_q="Does your router read a field that also silently accumulates history?")

print("done: 67")
