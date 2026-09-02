import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 5, "Interview Nugget", "Cost Jumps 40%. Traffic Didn't Move.",
      ["A real scenario question on diagnosing a cost anomaly using tracing data alone."])

slide(p("slide-02.png"), 2, 5, "The Question", "No Corresponding Traffic Increase",
      ["Walk through how you'd diagnose it using tracing data alone."])

slide(p("slide-03.png"), 3, 5, "The Answer", "Start From generation Spans Specifically",
      ["Only those carry usage_details and model. A cost anomaly usually traces to one of three causes."],
      code="# compare per-trace, before vs after the jump:\n# - token counts   (prompt-length regression)\n# - model names    (silent fallback to a pricier model)\n# - retry counts   (a retry storm multiplying billed tokens)")

slide(p("slide-04.png"), 4, 5, "Why This Works", "The Aggregate Dollar Figure Can't Tell You Which One",
      ["\"More expensive calls\" and \"more calls\" look identical on a total-cost dashboard.",
       "Comparing token counts and model names per trace is what actually localizes the cause."])

slide(p("slide-05.png"), 5, 5, "Takeaway", "A Cost Dashboard Alone Is A Symptom, Not A Diagnosis",
      ["The generation span's usage_details and model fields are what turn a symptom into a specific, fixable cause."],
      closing_q="If your cost jumped 40% tomorrow, could you localize the cause from tracing data alone?")

print("done: 94")
