import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 5, "Interview Nugget", "Why Did CI Suddenly Need An API Key?",
      ["A real scenario question on env-var validation timing."])

slide(p("slide-02.png"), 2, 5, "The Question", "Import-Time Validation Bit Back",
      ["Your test suite imports a module that defines a Pydantic settings model requiring GROQ_API_KEY.",
       "CI has no real key configured, and it starts failing to even import that module. What's the root mistake?"],
      code="class Settings(BaseSettings):\n    groq_api_key: str  # required — validated at import")

slide(p("slide-03.png"), 3, 5, "The Answer", "The Check Ran At Import, Not Entry",
      ["Validating required config at import time means anything that transitively imports the module is forced to have a real key — including a test that only needs the type, not a live call."])

slide(p("slide-04.png"), 4, 5, "The Fix", "Move The Check To The Entry Point",
      ["Validate at app startup, or lazily on first real use — not at module import.",
       "Importing for tests, tooling, or docs generation shouldn't require secrets a live call would need."],
      code="def main():\n    validate_required_env()")

slide(p("slide-05.png"), 5, 5, "Takeaway", "Import Should Never Cost A Secret",
      ["The same discipline that keeps a unit test from needing a real GROQ_API_KEY just to load a Pydantic model three files away."],
      closing_q="Has an import-time check ever broken your CI unexpectedly?")

print("done: 39")
