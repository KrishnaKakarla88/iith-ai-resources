import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 5, "Interview Nugget", "Decorator Order Changes Your Trace",
      ["A real scenario question on stacking retry and tracing decorators."])

slide(p("slide-02.png"), 2, 5, "The Question", "Which Order, Which Trace?",
      ["@traced is stacked above @retry_with_backoff(max_retries=3) on a tool function.",
       "A call fails twice, then succeeds on the third attempt. How many trace spans get recorded?"],
      code="@traced(role) above @retry_with_backoff(max_retries=3)")

slide(p("slide-03.png"), 3, 5, "The Answer", "One Span, Not Three",
      ["@traced above @retry_with_backoff wraps the ENTIRE retrying process as one call.",
       "It records one span covering all three attempts, and only sees the final outcome."])

slide(p("slide-04.png"), 4, 5, "Reverse It", "Same Code, Different Trace",
      ["@retry_with_backoff above @traced instead retries the ALREADY-TRACED function.",
       "That produces three separate spans — one per attempt."])

slide(p("slide-05.png"), 5, 5, "Takeaway", "Order Decides What Each Layer Wraps",
      ["\"Why did our trace show only 1 span for a call we know retried\"",
       "is a decorator-order bug, not a tracing bug."],
      closing_q="Which order does your tracing stack use?")

print("done: 31")
