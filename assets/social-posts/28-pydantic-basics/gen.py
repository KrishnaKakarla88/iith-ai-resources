import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "Pydantic: The Validation Boundary",
      ["Turns unreliable free-form LLM output into something "
       "safe to hand to business logic."])

slide(p("slide-02.png"), 2, 6, "Concept", "A Dict Never Complains Until It's Used",
      ["An LLM's JSON output is a string that merely looks like JSON — nothing checks it until something does.",
       "**Example:** unpacking parsed JSON into Invoice(...) runs real validation, raising ValidationError immediately on a problem."],
      code="Invoice(**data)  # the validation boundary")

slide(p("slide-03.png"), 3, 6, "Core Mechanics", "extra=\"forbid\" Catches Hallucinated Keys",
      ["Without it, a model silently accepts and ignores any field it doesn't declare.",
       "**Example:** an LLM adds an extra key or misspells one — passes validation unnoticed."],
      code='model_config = ConfigDict(extra="forbid")')

slide(p("slide-04.png"), 4, 6, "Core Mechanics", "min_length Alone Isn't Enough",
      ["min_length=1 only checks a field isn't empty — \"...\" has length 3, so it passes.",
       "A **field_validator** inspects the actual value, not just its length."],
      code='if v.strip().lower() in {"", "n/a", "..."}: raise ValueError')

slide(p("slide-05.png"), 5, 6, "Under The Hood", "Dunders, Generated For You",
      ["BaseModel generates __init__, __repr__, __eq__ from your annotated fields — "
       "same mechanism as @dataclass, plus real validation layered on top."],
      code="assert parsed_invoice == expected_invoice  # __eq__, for free")

slide(p("slide-06.png"), 6, 6, "Takeaway", "Never Trust a Verbatim Field",
      ["Never ask the LLM to reproduce a field it already has.",
       "Inject it after parsing instead of trusting a copy."],
      closing_q='Where has extra="forbid" saved you from a silent bug?')

print("done: 28")
