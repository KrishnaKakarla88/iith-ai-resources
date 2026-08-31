import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "JSON Mode Isn't Validation",
      ["An LLM is trained to sound fluent, not to produce parseable data. Two separate checks close that gap."])

slide(p("slide-02.png"), 2, 6, "Building On", "Detecting A Bad Value Isn't The Hard Part",
      ["JSON mode catches shape, Pydantic catches value — both already validate correctly on their own.",
       "The harder question this page actually answers: what happens the moment validation fails?"])

slide(p("slide-03.png"), 3, 6, "Core Mechanics", "The Repair Loop",
      ["Generate a JSON attempt, validate it, and on failure feed the model its own mistake back.",
       "That's the smallest possible agentic loop: generate, validate, observe the failure, act, repeat."],
      diagram=("flow", ["Generate", "Validate", "Fail?", "Repair"]))

slide(p("slide-04.png"), 4, 6, "What Gets Sent Back", "The Error, Not Another Guess",
      ["The repair prompt carries the ValidationError text, the original input, and the model's failed attempt.",
       "A specific mistake to correct beats asking the same question again with no new information."],
      code="f'Your last response failed validation: {error}\\nPrevious attempt: {raw}'")

slide(p("slide-05.png"), 5, 6, "Discipline", "Cap The Retries, Escalate On Exhaustion",
      ["2-3 attempts is typical — cost, and some inputs are legitimately unparseable no matter how many tries.",
       "Hit the cap and fail loudly to a human. Never let unvalidated data flow through silently."])

slide(p("slide-06.png"), 6, 6, "Takeaway", "Checking Values Is A Separate Job From Checking Shape",
      ["A refund tool call can be syntactically perfect JSON with an amount of -9999999.",
       "Shape validation buys you the first half only."],
      closing_q="Do you validate shape and value as two separate layers, or one?")

print("done: 35")
