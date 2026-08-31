import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "Args, Kwargs And Defaults",
      ["The vocabulary every tool or agent function signature "
       "in this stack is written in."])

slide(p("slide-02.png"), 2, 6, "Concept", "Positional vs Keyword",
      ["**Positional** arguments are matched by position — the first value goes to the first parameter.",
       "**Keyword** arguments are matched by name — order doesn't matter, and the call reads clearly."],
      code="create_agent(llm, TOOLS, memory=None, verbose=True)")

slide(p("slide-03.png"), 3, 6, "Mechanism", "*args and **kwargs",
      ["**args** collects any extra positional arguments into a tuple.",
       "**kwargs** collects any extra keyword arguments into a dict."],
      code="def f(*args, **kwargs): ...")

slide(p("slide-04.png"), 4, 6, "Why It Matters", "Forwarding Any Call Shape",
      ["A decorator wraps a function without knowing its signature ahead of time.",
       "**Example:** a logging wrapper forwards whatever it received, unchanged."],
      code="def wrapper(*args, **kwargs): return fn(*args, **kwargs)")

slide(p("slide-05.png"), 5, 6, "Bonus Mechanic", "Keyword-Only Parameters",
      ["A bare * in a signature forces everything after it to be passed by name.",
       "**Example:** def f(a, *, b) — b must be named at the call site."],
      code="f(1, b=2)  # works. f(1, 2)  # raises TypeError")

slide(p("slide-06.png"), 6, 6, "Takeaway", "Read Any Signature With Confidence",
      ["Positional, keyword, args, kwargs, keyword-only — "
       "five patterns cover every function signature you'll see."],
      closing_q="Which one still trips you up in a real signature?")

print("done: 24")
