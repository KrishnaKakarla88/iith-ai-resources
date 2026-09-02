import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 7, "Concept", "An Agentic Loop Is Just A while Loop Underneath",
      ["Fine for a task that finishes in three turns. It breaks down once a run gets long, needs to branch, or has to survive a crash — not because the model got worse."])

slide(p("slide-02.png"), 2, 7, "Three Structural Gaps", "Nothing To Do With Model Quality",
      ["**Opaque**: one long transcript, no named stages — debugging means reading it back to front.",
       "**Unbounded**: stops when the model decides it's finished — a hope, not a guarantee.",
       "**Not resumable**: state lives in a Python variable in RAM — a crash means restarting from zero."])

slide(p("slide-03.png"), 3, 7, "The Fix", "Node, Edge, State",
      ["Name every stage as a node. Make every transition an explicit edge. Keep the run's current state in one inspectable, saveable object."],
      diagram=("flow", ["Node", "Edge (reads state)", "Node", "Checkpoint"]))

slide(p("slide-04.png"), 4, 7, "The Key Split", "Decide In A Node, Route In An Edge",
      ["A node decides by writing a value to state. The edge only reads it — no model call inside a conditional edge.",
       "That split makes routing logic a pure, testable function, and a runaway loop a design choice you can see and cap."])

slide(p("slide-05.png"), 5, 7, "The Re-Implementation Test", "If You Could Rebuild It By Hand, You Learned The Idea",
      ["State machines, checkpointing, and human-in-the-loop pauses are decades-old distributed-systems concepts — the API is this year's best illustration of them, not the idea itself."])

slide(p("slide-06.png"), 6, 7, "Production Gotcha", "A Misspelled State Key Fails Silently",
      ["A TypedDict state schema isn't runtime-validated field-by-field — printing or streaming state after every node during development catches this immediately, not a framework guarantee."])

slide(p("slide-07.png"), 7, 7, "Takeaway", "A Straight-Line Task Gains Nothing From Being A Graph",
      ["Load → chunk → summarize → return, same steps every run, no branch ever taken — that's unexercised branching code to maintain, not a mindset upgrade."],
      closing_q="Which specific graph feature would you actually use on your current task — or do you just want a chain?")

print("done: 62")
