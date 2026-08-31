import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)
def p(name): return os.path.join(OUT, name)

slide(p("slide-01.png"), 1, 6, "Concept", "Mutability In Python",
      ["The split that decides whether changing a value in one place "
       "silently changes it everywhere else it's referenced."])

slide(p("slide-02.png"), 2, 6, "Core Idea", "Mutable vs Immutable",
      ["**Immutable** objects can't change after creation — reassigning a name just points it at a new object.",
       "**Mutable** objects change in place — appending to a list modifies the same object every reference sees."])

slide(p("slide-03.png"), 3, 6, "Mechanism", "is vs ==",
      ["**is** checks identity — same object in memory.",
       "**==** checks value — do they represent the same data.",
       "**Example:** copy a list, then compare — equal in value, but not the same object."],
      code="a = [1,2]; b = a.copy()  # a == b: True, a is b: False")

slide(p("slide-04.png"), 4, 6, "The Bug", "One Shared List, Every Call",
      ["A default argument value is evaluated once, at function-definition time — not per call.",
       "**Example:** a function with history=[] as a default — every call skipping history shares that same list."],
      code='log_event("a"); log_event("b")  # -> [\'a\',\'b\'] leaked')

slide(p("slide-05.png"), 5, 6, "The Fix", "Default To None, Build Fresh Inside",
      ["**None** is immutable — sharing the same default across every call is harmless.",
       "The real mutable object gets created inside the function body, fresh, on every call."],
      code="history = history if history is not None else []")

slide(p("slide-06.png"), 6, 6, "Takeaway", "Check Every Mutable Default",
      ["Any list, dict, or set sitting as a default argument value "
       "is a shared-state bug waiting to happen."],
      closing_q="Ever debugged state 'leaking' across unrelated calls?")

print("done: 22")
