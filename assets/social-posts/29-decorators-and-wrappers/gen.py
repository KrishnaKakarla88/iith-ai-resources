import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "Decorators: Wrap Without Touching",
      ["Retry, circuit-breaker, and tracing all get bolted onto "
       "agent functions this exact way."])

slide(p("slide-02.png"), 2, 6, "Concept", "A Function That Wraps A Function",
      ["Functions are ordinary objects — they can be passed around and returned from other functions.",
       "**@my_decorator** above a function is shorthand for my_function = my_decorator(my_function)."],
      code="get_weather = retry_with_backoff(max_retries=3)(get_weather)")

slide(p("slide-03.png"), 3, 6, "Mechanism", "Three Nested Levels, One Reason",
      ["The outer function only exists to accept the decorator's own arguments.",
       "It returns the real decorator, which returns wrapper — the function that runs at call time."],
      code="def retry_with_backoff(max_retries=3):\n"
           "    def decorator(fn):\n"
           "        def wrapper(*args, **kwargs):\n"
           "            return fn(*args, **kwargs)")

slide(p("slide-04.png"), 4, 6, "Gotcha", "Forgetting functools.wraps",
      ["Without it, every decorated function's __name__ becomes \"wrapper\" and its docstring disappears.",
       "**Example:** FastMCP reads a tool's name/docstring for its schema — an unwrapped decorator breaks it."],
      code="@functools.wraps(fn)  # keeps fn's real name and docstring")

slide(p("slide-05.png"), 5, 6, "Production Rule", "Stacking Order Changes The Meaning",
      ["@traced above @retry_with_backoff records ONE span covering all retry attempts.",
       "Reversed, it records a separate span per attempt — same code, different trace."],
      code="@traced(role)  # outermost, above @retry_with_backoff(...)")

slide(p("slide-06.png"), 6, 6, "Takeaway", "Order Decides What 'One Failure' Means",
      ["Retry innermost, circuit breaker outermost — "
       "so a burst of retried failures is what actually trips the breaker."],
      closing_q="Which decorator order surprised you the first time?")

print("done: 29")
