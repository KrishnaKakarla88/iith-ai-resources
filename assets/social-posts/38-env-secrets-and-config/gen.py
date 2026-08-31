import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "Secrets Don't Belong In Source Files",
      ["A .env file plus python-dotenv is the baseline — the subtler decision is when you check a key exists."])

slide(p("slide-02.png"), 2, 6, "Core Mechanics", "load_dotenv() Fills os.environ",
      ["It reads .env and copies KEY=value pairs into os.environ.",
       "The rest of your code just calls os.getenv() like any environment variable."],
      code='load_dotenv()  # then: os.getenv("GROQ_API_KEY")')

slide(p("slide-03.png"), 3, 6, "Gotcha", "It Never Overwrites A Real Export",
      ["load_dotenv() only sets variables not already present in os.environ.",
       "A real shell or CI export always takes precedence over a stale .env value."])

slide(p("slide-04.png"), 4, 6, "The Real Design Call", "Validate At The Entry Point, Not Import",
      ["Checking a required key at module import breaks anything that imports the module transitively — most commonly your test suite, which shouldn't need a live key to import a model three files away."],
      code="def main():\n    validate_required_env()  # not at module import time")

slide(p("slide-05.png"), 5, 6, "Defensive Parsing", "Env Vars Are Always Strings",
      ["A malformed inline comment like \"PORT=8000 # http port\" breaks a naive int(os.getenv(\"PORT\")).",
       "Regex out the leading integer and fall back to a default instead of trusting the raw string."],
      code='match = re.match(r"\\s*(\\d+)", raw)')

slide(p("slide-06.png"), 6, 6, "Takeaway", "A .env File Is Convenience, Not A Control",
      ["Fine for one developer machine. In production, secrets belong in a manager with rotation and audit trails."],
      closing_q="Do you validate required env vars at import time, or at the entry point?")

print("done: 38")
