import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "A Demo Proves An Agent Can Work. Once.",
      ["On the input you happened to type, on a day the model happened to behave. It proves nothing about the input you didn't try, or what happens after next week's prompt change."])

slide(p("slide-02.png"), 2, 6, "Not The Same As A Unit Test", "Code Correctness vs. Behavior Quality",
      ["A unit test asks: does this function do what the code says, with the LLM mocked out.",
       "Eval asks: is the agent's behavior good enough to ship — probabilistic, and the LLM call is exactly the thing being measured."])

slide(p("slide-03.png"), 3, 6, "The Core Idea", "Grade Every Layer, Not Just The Final Answer",
      ["**Tool use**: right tool, right arguments.",
       "**Retrieval**: right documents came back.",
       "**Planning/routing**: right sub-task chosen.",
       "**Final answer**: correct, grounded, well-formed — the only layer a demo shows you."])

slide(p("slide-04.png"), 4, 6, "Why That Matters", "A 100% Final-Answer Score Can Still Be Broken",
      ["Two wrong steps underneath can coincidentally land on a correct-looking answer — grading only the last row is grading a group project by the final presentation alone."])

slide(p("slide-05.png"), 5, 6, "Sample Code", "One Trace, Every Scorer Reads The Same Shape",
      [],
      code="trace = {\n    \"query\": query,\n    \"route\": route,           # \"tool\" | \"retrieval\" | \"direct\"\n    \"tool_call\": tool_call,\n    \"retrieved_docs\": retrieved_docs,\n    \"final_answer\": final_answer,\n}")

slide(p("slide-06.png"), 6, 6, "Takeaway", "Fixed Inputs, Re-Run Every Time Something Changes",
      ["A golden set, not live traffic — the prompt, the model, the retrieval corpus, a dependency version. Live traffic isn't controlled enough to tell you anything about one specific change."],
      closing_q="Could you point to which layer of your agent broke, or only whether the final answer was right?")

print("done: 87")
