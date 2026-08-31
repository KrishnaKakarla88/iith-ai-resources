import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "Type Hints Are The Contract",
      ["Python never enforces them at runtime on its own — "
       "but Pydantic and FastMCP read them and act on them."])

slide(p("slide-02.png"), 2, 6, "Concept", "Annotation, Not Enforcement",
      ["A type hint (def add(a: int, b: int) -> int:) says what a function expects.",
       "CPython ignores it at execution time — nothing stops add(1, \"two\") from running."],
      code="add(1, \"two\")  # runs, then fails later, somewhere else")

slide(p("slide-03.png"), 3, 6, "Why It Matters Here", "The Annotation Is The API",
      ["Pydantic turns a class's type-annotated fields into a validator.",
       "FastMCP turns a function's type-annotated parameters into the JSON schema an LLM reads to call it."])

slide(p("slide-04.png"), 4, 6, "Core Mechanics", "Literal Narrows What str Allows",
      ["**str** accepts any string — a hallucinated route like \"unknown\" would pass.",
       "**Literal** restricts a field to an exact enumerated set of values."],
      code='route: Literal["tool", "retrieval", "direct"]')

slide(p("slide-05.png"), 5, 6, "Core Mechanics", "The Optional Field Pattern",
      ["X | None = None reads as: an int, or nothing, defaulting to nothing.",
       "This is a real behavioral difference from a required field, not just documentation."],
      code="invoice_number: str | None = None   # optional")

slide(p("slide-06.png"), 6, 6, "Takeaway", "Hints Without a Checker Are Just Notes",
      ["Run mypy or pyright in CI — hints alone are only as reliable "
       "as the last person who kept them in sync with the code."],
      closing_q="Do you run a static type checker in CI, or rely on hints alone?")

print("done: 27")
