import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "Dunder Methods",
      ["The double-underscore methods that plug a plain class "
       "into Python's own syntax."])

slide(p("slide-02.png"), 2, 6, "Concept", "Python Calls These For You",
      ["print(x) calls x.__repr__() — you never call it directly.",
       "len(x) calls x.__len__().",
       "x == y calls x.__eq__(y).",
       "**Example:** no dunders defined → printing shows <MyClass object at 0x...>."])

slide(p("slide-03.png"), 3, 6, "Core Mechanics", "The Big Three: __init__, __repr__, __eq__",
      ["**__init__** runs when you call MyClass(...) — sets up the instance.",
       "**__repr__** controls what print(x) shows.",
       "**__eq__** controls what x == y checks."])

slide(p("slide-04.png"), 4, 6, "Sample Code", "A Class That Plugs Into Python",
      ["A Ticket class defining all three — printing and comparing "
       "now behave like real data, not a bare memory address."],
      code="t1 == t2  # True, field-by-field, thanks to __eq__")

slide(p("slide-05.png"), 5, 6, "Gotcha", "__eq__ Without __hash__",
      ["Overriding __eq__ to compare by value silently makes instances unhashable.",
       "**Example:** define __eq__ alone → hash(obj) raises TypeError."],
      code="__hash__ = object.__hash__  # re-inherit it explicitly")

slide(p("slide-06.png"), 6, 6, "Takeaway", "Know What's Underneath",
      ["Pydantic's BaseModel and @dataclass generate these for you — "
       "still worth knowing what's running underneath."],
      closing_q="Which dunder have you had to write by hand recently?")

print("done: 25")
