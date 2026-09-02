import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 7, "Concept", "Every LangGraph Graph Is Built From Five Shapes",
      ["However elaborate a graph looks, it's assembled from a small, recurring set — three workflows, two agents, arranged along the autonomy spectrum."])

slide(p("slide-02.png"), 2, 7, "The Three Workflows", "A Human Enumerated The Paths",
      ["**Single call**: START -> node -> END, one judgment.",
       "**Prompt chain**: fixed steps, the model fills fuzzy content in one of them.",
       "**Router**: one categorical decision, everything downstream fixed per category."])

slide(p("slide-03.png"), 3, 7, "The Two Agents", "The Model Directs Its Own Next Step",
      ["**Single tool-calling loop**: model decides which tool and when to stop — the sequence can't be enumerated in advance.",
       "**Multi-agent fan-out/fan-in**: independent subtasks running concurrently, combined at a merge node."])

slide(p("slide-04.png"), 4, 7, "Sample Code", "The Loop Pattern Every Later Shape Builds On",
      ["A mandatory step cap — an uncapped tool-calling loop is unbounded cost."],
      code="def should_continue(state):\n    if state[\"steps\"] >= MAX_TOOL_STEPS:  # mandatory cap\n        return \"end\"\n    return \"continue\" if last.tool_calls else \"end\"")

slide(p("slide-05.png"), 5, 7, "The Reducer Requirement", "Fan-Out Needs A Reducer, A Chain Doesn't",
      ["In a prompt chain exactly one node writes to any key at a time — overwrite is fine.",
       "In fan-out, multiple nodes write concurrently in the same superstep — without a reducer, that's InvalidUpdateError, not a silent pick-one."])

slide(p("slide-06.png"), 6, 7, "Production Practice", "Default To NO On Multi-Agent",
      ["Even when a problem could technically fan out — a second agent adds a lossy re-serialization boundary at every handoff. Split only for a reason you can name."])

slide(p("slide-07.png"), 7, 7, "Takeaway", "Ask If You Can Enumerate The Valid Paths Right Now",
      ["If yes, it's shapes 1-3, a workflow. If the next action genuinely depends on data you don't have until run time, it's shape 4 or 5, an agent."],
      closing_q="Which of the five shapes does your current graph actually need?")

print("done: 71")
