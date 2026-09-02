import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "PII Doesn't Only Leak Through Tracing Spans",
      ["It moves through every layer an agent touches — chat logs, memory stores, eval datasets, error messages, tool-call arguments. Any of them can persist it verbatim unless something strips it first."])

slide(p("slide-02.png"), 2, 6, "The Fix Pattern", "Decide At Write Time, Never At Read Time",
      ["Once PII is in a log file, a vector store, or a third-party memory service, \"removing it later\" means finding every copy, not editing one field."])

slide(p("slide-03.png"), 3, 6, "Sample Code", "Allowlist, Not Denylist",
      ["A denylist has to anticipate every PII-shaped field, including ones added later by someone who doesn't know the rule. An allowlist blocks a new field by default until someone marks it safe."],
      code="REDACT_KEYS = {\"customer_message\", \"raw_chat_history\", \"draft\"}\n\ndef safe_repr(state):\n    return {k: (\"[REDACTED]\" if k in REDACT_KEYS else v) for k, v in state.items()}")

slide(p("slide-04.png"), 4, 6, "Never Trust The Model To Reproduce A Field",
      "Inject It Programmatically, After The Call",
      ["A model asked to echo an order ID or a raw ticket ref verbatim can still alter, truncate, or hallucinate it — correctness bug and PII risk at once."],
      code="parsed = extract_and_validate(llm_response)\nparsed.setdefault(\"raw_text\", original_ticket_text)  # injected, not model-generated")

slide(p("slide-05.png"), 5, 6, "The Cache Gotcha", "A Purge That Misses The In-Process Cache Isn't A Purge",
      ["A long-lived process that clears only the backing store keeps serving \"deleted\" data to the next request until it restarts."])

slide(p("slide-06.png"), 6, 6, "Takeaway", "Hash Identifiers, Don't Log Them Raw",
      ["A user_id used for filtering doesn't need to be human-readable in a log — hash it once, log the hash."],
      closing_q="Would a hand-maintained allowlist actually catch every free-text field in your system?")

print("done: 89")
