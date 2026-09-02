import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "One Tag Is Your Entire Multi-Tenant Wall",
      ["Supermemory is a managed API for durable, per-customer agent memory — and one string decides whether customer A ever sees customer B's data."])

slide(p("slide-02.png"), 2, 6, "The Isolation Key", "container_tag Scopes Every Read And Write",
      ["A stable string per user/tenant — e.g. a customer ID.",
       "Applied on every single call site, or it's a cross-customer memory leak, not a minor bug."],
      code="mem.add(content=text, container_tag=USER_ID,\n        metadata={\"type\": kind})\n\nmem.search.memories(q=query, container_tag=USER_ID, limit=3)")

slide(p("slide-03.png"), 3, 6, "The Gotcha", "Writes Are Asynchronous",
      ["**Example:** call add() then immediately search() for the same fact — it can come back empty.",
       "add() queues indexing, it doesn't complete it. Code that writes then searches needs to poll, not assume."],
      code="write_memory(mem, \"Booked flight AI-302.\", kind=\"episodic\")\nfor _ in range(20):\n    if recall(mem, \"what flight did I book\"):\n        break\n    time.sleep(3)")

slide(p("slide-04.png"), 4, 6, "The Response-Shape Trap", "Two Search Calls, Two Different Shapes",
      ["search.memories() returns a .memory field, singular container_tag.",
       "search.documents() returns a .chunks field, plural container_tags.",
       "A recall() helper that only checks one shape silently misses hits from the other."])

slide(p("slide-05.png"), 5, 6, "Production Practice", "Fail Open, But Log Loudly",
      ["A memory-store outage shouldn't take down the customer-facing turn — swallow the exception, but keep exc_info=True so the failure stays visible in traces, not silent.",
       "Also: identity must come only from the authenticated session, never guessed out of message text."])

slide(p("slide-06.png"), 6, 6, "Takeaway", "No Bulk \"List All\" API Means No Guaranteed Delete",
      ["Purge is a best-effort semantic sweep, not exhaustive — document that limit rather than assuming a delete workflow is complete."],
      closing_q="If container_tag is your only isolation mechanism, how many call sites in your codebase set it correctly?")

print("done: 47")
