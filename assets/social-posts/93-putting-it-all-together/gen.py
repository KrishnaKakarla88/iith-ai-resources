import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 7, "Concept", "One Request, Every Layer This Series Covered",
      ["\"My order #KW-88213 hasn't arrived and it's been 9 days — what's your policy, and can I get a refund?\" Here's every hop it takes."])

slide(p("slide-02.png"), 2, 7, "The Path", "Five Hops, Simplified",
      [],
      diagram=("flow", ["Intake", "Plan/Route", "Tools + RAG", "Guardrails", "Response"]))

slide(p("slide-03.png"), 3, 7, "Hops 1-3", "Validated Before Any Agent Code Runs",
      ["Intake: a Pydantic request model checks the shape first.",
       "Identity: comes from the authenticated session, never guessed from message text.",
       "Planning: one LLM call decides tool, retrieval, or both — forced into a structured shape."])

slide(p("slide-04.png"), 4, 7, "Hops 4-6", "Deterministic Where Possible, Checked Everywhere",
      ["Tools fetch live order status — no ambiguity about what happened.",
       "Retrieval embeds, searches hybrid, reranks, and checks the returned chunk for injected instructions before trusting it as context.",
       "Guardrails check the final answer independent of whether it's good — replaced with a safe fallback if it fails."])

slide(p("slide-05.png"), 5, 7, "Hops 7-9", "Off To The Side, Not On The Critical Path",
      ["Every hop above is a nested span under one trace ID, redacted before it leaves the process.",
       "This exact request isn't evaluated live, but it's the shape a golden-set item represents.",
       "Every dependency call sits behind retry, fallback, and circuit-breaker protection."])

slide(p("slide-06.png"), 6, 7, "The Single Most Common Gap", "Guardrails, Tracing, Eval, Reliability Aren't Add-Ons",
      ["Treating them as something layered on at the end, rather than built in from Agent 1, is the gap between a demo and something production-ready."])

slide(p("slide-07.png"), 7, 7, "Takeaway", "One Trace Dict, Written Once, Read By Every Layer",
      ["What makes a request both debuggable — tracing — and gradable — eval — from the same object, instead of three separate representations drifting apart."],
      closing_q="Could you trace one customer request through every layer of your own system, by name?")

print("done: 93")
