import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "Making The Model's Reasoning Visible",
      ["Tool calling decides which tool silently. ReAct writes the reasoning out in plain text first."])

slide(p("slide-02.png"), 2, 6, "The Loop", "Thought, Action, Observation",
      ["The model reasons, requests a tool, gets a real result injected back — then reasons again."],
      diagram=("flow", ["Thought", "Action", "Observation", "Final Answer"]))

slide(p("slide-03.png"), 3, 6, "Load-Bearing Gotcha", "Without stop=[\"Observation:\"], It Hallucinates One",
      ["Nothing stops the model from generating its own fake Observation: line and reasoning off invented results instead of your real tool output."],
      code='litellm.completion(..., stop=["Observation:"])')

slide(p("slide-04.png"), 4, 6, "Security Discipline", "Observations Are Untrusted Data",
      ["A search result can contain adversarial text — \"ignore previous instructions and...\" — embedded in otherwise-legitimate content.",
       "The model reasons about it, never obeys it."])

slide(p("slide-05.png"), 5, 6, "Sample Code", "Regex-Parsing The Action Line",
      ["Your code extracts the tool and argument, calls it, and injects the result as the next turn."],
      code='match = re.search(r"Action:\\s*search\\[(.+?)\\]", text)\nresult = search_web(match.group(1))')

slide(p("slide-06.png"), 6, 6, "Takeaway", "Same Loop As Tool Calling — Different Plan Format",
      ["A structured tool_calls field versus a regex-parsed line of text — the mechanism is identical."],
      closing_q="Have you shipped a ReAct loop that forgot the stop sequence?")

print("done: 43")
