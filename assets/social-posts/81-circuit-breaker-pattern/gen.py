import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "Retries Actively Hurt During A Sustained Outage",
      ["Every request still pays the full retry budget against a dependency with no chance of answering — adding latency without adding a single success."])

slide(p("slide-02.png"), 2, 6, "Three States", "Closed, Open, Half-Open",
      ["**Closed**: normal operation, failures counted.",
       "**Open**: every call short-circuits immediately, no network attempt, once the failure threshold hits.",
       "**Half-open**: after a timeout, exactly one trial call tests recovery — without guessing."],
      diagram=("flow", ["Closed", "Open (threshold hit)", "Half-open (1 trial)", "Closed or Open"]))

slide(p("slide-03.png"), 3, 6, "The Rule That Keeps It Correct", "Any Failure While Half-Open Re-Opens Immediately",
      ["Allowing multiple trial calls in half-open risks hammering a still-broken dependency with a burst of traffic — exactly what the breaker exists to prevent."])

slide(p("slide-04.png"), 4, 6, "Sample Code", "~25 Lines, Three States, Fully Auditable",
      [],
      code="def call(self, fn, *args, **kwargs):\n    if self.state == \"open\":\n        if time.monotonic() - self.opened_at >= self.reset_timeout:\n            self.state = \"half_open\"\n        else:\n            raise CircuitOpenError(\"circuit open\")\n    ...")

slide(p("slide-05.png"), 5, 6, "Production Practice", "One Breaker Per Dependency, Retry Then Breaker",
      ["A global shared breaker lets one bad tool trip the breaker for unrelated tools.",
       "Compose retry then circuit breaker, in that order — reversing it makes the breaker's failure count noisier, since it only sees the retry's final exhausted failure."])

slide(p("slide-06.png"), 6, 6, "Takeaway", "A Breaker Without A Fallback Just Changes The Error Message",
      ["An open breaker still has to return something to its caller — without a fallback, \"protected from hammering a dead dependency\" becomes \"every caller gets CircuitOpenError instead.\""],
      closing_q="Is your circuit breaker scoped per dependency, or one global instance for everything?")

print("done: 81")
