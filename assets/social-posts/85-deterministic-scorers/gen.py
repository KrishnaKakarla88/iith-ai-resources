import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "Not Every Eval Question Needs A Language Model",
      ["\"Did the agent call search_catalog with the right book_id?\" is a string comparison — cheap, reproducible, and a sanity check on the LLM judges you're also running."])

slide(p("slide-02.png"), 2, 6, "Sample Code", "One Scorer Per Category, Reading The Same Trace",
      ["A tool call with the wrong argument isn't 80% correct — it's the wrong call, full stop."],
      code="def tool_match_score(item, trace):\n    call = trace.get(\"tool_call\") or {}\n    if call.get(\"name\") != item[\"expected_tool\"]:\n        return 0.0\n    args_str = str(call.get(\"args\", {})).lower()\n    if not all(sub.lower() in args_str for sub in item[\"expected_args_contains\"]):\n        return 0.0\n    return 1.0")

slide(p("slide-03.png"), 3, 6, "All-Or-Nothing vs. Partial Credit", "The Choice Is Deliberate, Not A Default",
      ["A wrong tool argument fails the whole call — binary.",
       "A written answer can legitimately cover most of the expected ground without every keyword present — partial credit fits."])

slide(p("slide-04.png"), 4, 6, "The Real Value", "An Independent Signal When Judges Are Wrong",
      ["LLM-judge scoring is noisy — an eval harness relying only on judges has no way to notice a judge is systematically wrong.",
       "When the two disagree, that disagreement is exactly the case worth reading by hand."])

slide(p("slide-05.png"), 5, 6, "Production Gotcha", "A Metric's Name Doesn't Guarantee Its Mechanism",
      ["A metric labeled expected_route was, in one real case, scored against answer content rather than structural routing state — no golden case ever exercised the path that would have exposed it."])

slide(p("slide-06.png"), 6, 6, "Takeaway", "The Trade-Off Is Exactly What You'd Expect",
      ["Deterministic scorers can only check what you can express as code — they can't tell you if an answer is well-written or helpful in tone. That's where an LLM judge earns its cost."],
      closing_q="Do your eval scores ever disagree with each other, or do you only run one kind?")

print("done: 85")
