import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 7, "Concept", "An LLM Judge Inherits Every Blind Spot A Model Has",
      ["A documented failure mode: the judge rewards style. A long, fluent, well-formatted answer scores well even when it's factually wrong."])

slide(p("slide-02.png"), 2, 7, "Three Judges, Cross-Checked", "Agreement Is Stronger Evidence Than Any One Opinion",
      ["**Ragas**: Faithfulness — is the answer entailed by the context.",
       "**DeepEval**: GEval — a custom rubric judge from plain-language criteria, no hand-written prompt needed.",
       "**TruLens**: feedback functions with chain-of-thought reasoning attached to every score."])

slide(p("slide-03.png"), 3, 7, "Auditing The Judge", "Hand-Label A Sample, Compute Agreement",
      ["A worked example: 200 answers scored, 40 hand-labeled, 35/40 agreement — but all four disagreements were long, fluent, wrong answers. The judge was rewarding style."],
      code="agreement = matching_labels / sampled_cases\n# 87.5% overall — but check WHICH direction the mismatches ran")

slide(p("slide-04.png"), 4, 7, "The Direction That Costs You", "Judge Says PASS, Human Says FAIL",
      ["That's the judge certifying bad output as good — invisible unless you specifically go looking for it.",
       "Judge-FAIL/human-PASS just costs a false alarm you'll catch immediately."])

slide(p("slide-05.png"), 5, 7, "Sample Code", "Same Trace, Three Independent Calls",
      [],
      code="correctness = GEval(\n    name=\"Correctness\",\n    criteria=\"Determine whether the actual output is factually correct given the expected output.\",\n    evaluation_params=[\"input\", \"actual_output\", \"expected_output\"],\n)\ncorrectness.measure(test_case)")

slide(p("slide-06.png"), 6, 7, "Production Gotcha", "One Judge's Exception Discards Every Score Already Computed",
      ["Wrap each judge call in its own try/except inside the dispatch function — Python doesn't return partial results on an uncaught exception, so one rate-limited judge silently erases the scores that already succeeded."])

slide(p("slide-07.png"), 7, 7, "Takeaway", "A Judge Audited Against Last Quarter's Model Is An Audit Of A Judge That No Longer Exists",
      ["Recalibrate on every model swap, prompt change, or new domain — track agreement as a number over time, not a one-off sanity check."],
      closing_q="Have you ever audited your LLM judge against a human label, or just trusted the score?")

print("done: 86")
