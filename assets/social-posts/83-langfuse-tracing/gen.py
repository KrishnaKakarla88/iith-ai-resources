import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 7, "Concept", "\"Wrong Answer, 14 Seconds, No Error\" Isn't Debuggable",
      ["Without tracing, a multi-agent run only shows you the final state — you can't tell which agent produced the bad value or which step ate the latency."])

slide(p("slide-02.png"), 2, 7, "The Fix", "A Tree Of Timed, Inspectable Spans",
      ["Open a span inside code already running inside another span, and it nests automatically — Langfuse follows the Python call stack, you never pass a span object by hand."],
      diagram=("flow", ["supervisor.run", "retrieval_agent.run", "vector_search / rerank"]))

slide(p("slide-03.png"), 3, 7, "Sample Code", "A Span That Survives Failure",
      [],
      code="def traced(role):\n    def decorator(fn):\n        def wrapper(state):\n            with langfuse.start_as_current_observation(\n                    as_type=\"span\", name=f\"agent:{role}\") as span:\n                result = fn(state)\n                span.update(input=state.get(\"plan\"), output=sorted(result))\n                return result\n        return wrapper\n    return decorator")

slide(p("slide-04.png"), 4, 7, "Cost Accounting", "Cost Only Exists Once Real Tokens Are Spent",
      ["A deterministic node with no LLM call legitimately has no cost figure — it should read as absent, not zero.",
       "A generation span needs model and usage_details wired from the actual response object — the built-in price table can't resolve every provider-prefixed model name."])

slide(p("slide-05.png"), 5, 7, "Production Gotcha", "Fails Silently By Design On A Missing Key",
      ["Nothing shows up in the UI if LANGFUSE_PUBLIC_KEY/SECRET_KEY are missing — check auth_check() first, rather than assuming a config problem elsewhere."])

slide(p("slide-06.png"), 6, 7, "The Real Incident", "A repr() Decorator Leaked Raw Chat Text Onto Every Span",
      ["A blanket tracing decorator that repr()s its arguments put the customer's raw message onto every node's span, every turn — missed by a grep because it was applied as a plain call, not @traced_node."])

slide(p("slide-07.png"), 7, 7, "Takeaway", "Redact Named Fields, Never Capture \"Whatever's In Scope\"",
      ["Any tracing layer that captures the full state blindly is a PII leak waiting on the next field someone adds."],
      closing_q="Does your tracing decorator capture named fields, or whatever happens to be in scope?")

print("done: 83")
