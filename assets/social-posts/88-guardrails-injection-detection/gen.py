import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 7, "Concept", "\"Right\" And \"Safe To Return\" Are Different Questions",
      ["A correct, well-written answer can still leak data it shouldn't. A guardrail can block a perfectly good answer for being phrased suspiciously. Checked separately, on purpose."])

slide(p("slide-02.png"), 2, 7, "Sample Code", "A Hallucinated Route Passes A Naive Schema Check",
      ["A Literal field rejects any route the model invents that isn't in the fixed set — and a placeholder answer like \"n/a\" still technically satisfies min_length=1 without this check."],
      code="class AgentResponse(BaseModel):\n    route: Literal[\"tool\", \"retrieval\", \"direct\"]\n    final_answer: str = Field(min_length=1, max_length=2000)\n\n    @field_validator(\"final_answer\")\n    def reject_placeholder(cls, v):\n        if v.strip().lower() in _PLACEHOLDER_ANSWERS:\n            raise ValueError(\"placeholder, not a real response\")")

slide(p("slide-03.png"), 3, 7, "Two Failure Directions", "Only One Ever Generates A Support Ticket",
      ["**False approval**: something bad gets through — a user complains, you find out.",
       "**False rejection**: a good answer gets blocked — nobody files a ticket for the answer they never received. It just quietly erodes trust."])

slide(p("slide-04.png"), 4, 7, "The Actual Tuning Data", "Neither Threshold Is \"Correct\"",
      ["A worked example: threshold 0.5 caught 18/20 bad cases but blocked 41/180 good ones. Threshold 0.9 caught 11/20 but blocked only 3/180.",
       "An internal tool can lean permissive. Medical or financial advice should lean strict — that's a business decision, not a library default."])

slide(p("slide-05.png"), 5, 7, "Scan Retrieved Content Too", "Not Just The User's Query",
      ["Anything the agent treats as trusted context — including a document your own retriever returned — is a vector for an attacker who got content into the corpus."])

slide(p("slide-06.png"), 6, 7, "The Real-World Stakes", "The Same Filter That Stops An Attacker Can Stop The Clean-Up Crew",
      ["A documented 2026 incident: hosted safety filters blocked incident responders trying to forensically analyze a live exploit, because the filter couldn't tell a forensic prompt full of exploit payloads from an actual attack.",
       "They ran forensics on a self-hosted model instead — vetted before the incident, not shopped for during one."])

slide(p("slide-07.png"), 7, 7, "Takeaway", "Tune Every Threshold Against The Same Golden Set Used For Eval",
      ["Scoring false-approval and false-rejection rates separately — a deliberate, documented choice, not a default inherited from a library."],
      closing_q="Do you know your guardrail's false-rejection rate, or only whether it blocks the obvious attacks?")

print("done: 88")
