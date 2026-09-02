import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 7, "Concept", "A Fact-Checker That Can See The Brief Can Be Talked Round",
      ["A five-agent team with one shared state dict looks harmless until a specialist reads a field it was never meant to see, or writes over one it doesn't own."])

slide(p("slide-02.png"), 2, 7, "Read Scoping", "The Mechanism That Actually Earns Multi-Agent's Cost",
      ["Each agent gets only its own state slice, not the whole dict. A Fact-Checker that only ever sees {draft, findings} has no brief to rationalize a fabricated citation against."])

slide(p("slide-03.png"), 3, 7, "Sample Code", "Write-Scopes: Enforced Before The Reducer Ever Sees It",
      ["A decorator checks a node's returned keys against a per-role allowlist and raises before the update reaches state."],
      code="WRITE_SCOPES = {\n    \"fact_checker\": {\"fact_check\", \"log\"},\n    \"reviewer\": {\"review\", \"log\"},\n    \"writer\": {\"draft\", \"fact_check\", \"review\", \"log\"},\n}\n\ndef _check(role, update):\n    illegal = set(update) - WRITE_SCOPES[role]\n    if illegal:\n        raise PermissionError(f\"{role} wrote out-of-scope keys: {illegal}\")")

slide(p("slide-04.png"), 4, 7, "The Deliberate Exception", "Control Fields Need No Reducer, On Purpose",
      ["fact_check and review must be resettable to {} on every revision — a rewrite voids prior approval.",
       "A control field that only ever accumulates can't represent \"not yet re-approved.\" That's why the Writer alone can reset both."])

slide(p("slide-05.png"), 5, 7, "Why Two Critics, Not One", "Each Closes A Different Blind Spot",
      ["**Fact-Checker**: deterministic regex over citation tags — the code check is the verdict.",
       "**Reviewer**: an objective structural floor AND an LLM-judge, never OR — a judge alone can be argued around, a structural check alone can't catch a plausible fabrication."])

slide(p("slide-06.png"), 6, 7, "Production Gotcha", "An Async Node Silently Bypasses A Sync-Only Guard",
      ["A @scoped decorator that doesn't branch on inspect.iscoroutinefunction stops enforcing scope the moment a node becomes async — write the async branch from the start."])

slide(p("slide-07.png"), 7, 7, "Takeaway", "Proven Directly: A Hallucinating Writer Plants A Fake Citation",
      ["The Fact-Checker, never having seen the brief, can't be talked round — the fabricated tag never ships. The same team without that read boundary would not catch it."],
      closing_q="Could any specialist in your team see a field that lets it rationalize a bad answer?")

print("done: 77")
