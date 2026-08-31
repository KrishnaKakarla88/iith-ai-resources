import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "Don't Default To Agent",
      ["Every multi-step AI system sits somewhere on a spectrum between two poles."])

slide(p("slide-02.png"), 2, 6, "The Two Poles", "Who Decides The Next Step",
      ["**Workflow**: your code decides the steps and their order in advance, ahead of any run.",
       "**Agent**: the model decides what to do next, call by call, based on what it observes."])

slide(p("slide-03.png"), 3, 6, "The Spectrum", "Most Systems Sit In The Middle",
      ["Each rung spends a little more autonomy than the last — code decides less, the model decides more."],
      diagram=("stack", ["Fixed Workflow", "Workflow With Routing", "Single Tool-Calling Agent", "Multi-Agent Orchestration"]))

slide(p("slide-04.png"), 4, 6, "The Real Signal", "Discovery, Not Difficulty",
      ["Autonomy earns its keep when the next step depends on something discovered mid-task — not because a task \"feels complex\" or \"involves an LLM.\""])

slide(p("slide-05.png"), 5, 6, "Code Contrast", "No Cap vs A Hard Cap",
      ["The workflow version has no loop to bound. The agent version needs MAX_ITERATIONS precisely because the model, not your code, is choosing the path."],
      code="for _ in range(MAX_ITERATIONS):\n    response = model.invoke(messages)  # model picks the next step")

slide(p("slide-06.png"), 6, 6, "Takeaway", "Autonomy Is A Cost You Pay Deliberately",
      ["A fully enumerable workflow gets the same outcome with less cost, lower latency, less to test."],
      closing_q="What's the last task you built as an agent that should've been a workflow?")

print("done: 40")
