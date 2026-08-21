---
stage: "09-production-readiness"
tools: [python]
tags: [eval, deterministic-scoring, golden-set]
last_verified: 2026-08-20
verified_against: "plain Python — no library dependency"
---

# Deterministic scorers

A deterministic scorer is pure Python that checks an agent's output against a known-correct expectation — no LLM call, no randomness, the same input always produces the same score.

## Prerequisites
- [[eval-driven-development-mindset]]

## In plain English

Not every eval question needs a language model to answer it. "Did the agent call `search_catalog` with `book_id="9780134685991"`?" is a string comparison. "Did the retrieved context contain the word 'grace period'?" is a substring check. These are cheap (milliseconds, no API call, no rate limit, no cost), perfectly reproducible (the same trace always scores the same), and — critically — a **sanity check on the LLM judges** covered in [[llm-judges-eval]]. LLM-judge scoring is noisy: an eval harness that relies only on judges has no independent signal to notice when a judge is systematically wrong. Pairing at least one deterministic metric per component means a disagreement between the two is something you can actually act on, rather than trusting either number blindly.

The trade-off is exactly what you'd expect: deterministic scorers can only check what you can express as code. They can't tell you whether a final answer is *well-written*, *helpful in tone*, or *faithful to context it didn't literally quote* — that's where an LLM judge earns its cost and latency.

## Core mechanics

| Scorer | What it checks | Credit style |
|---|---|---|
| Tool-match score | Right tool called **and** every expected argument substring present (case-insensitive) | All-or-nothing — any mismatch fails the whole call |
| Keyword-hit score (retrieval / answer) | Fraction of golden keywords present in retrieved context / final answer | Partial credit |
| Route-match score | Exact match against `expected_route` | Binary |
| Schema validity | Output parses against the expected Pydantic model | Binary (see [[structured-output-repair-loops]] for the repair side of this) |

The all-or-nothing vs. partial-credit choice is deliberate per metric, not a default: tool arguments either constitute the call you needed or they don't (a `check_fine_policy` call with the wrong `book_id` is not "80% correct"), while an answer can legitimately cover most of the expected ground without every keyword present.

## Sample code

Lab-sourced (`labs/Day4 Session 2 - Evaluation, Guardrails and Continuous Improvement.ipynb`) — one scorer per category, reading from the same trace dict every other scorer (deterministic and judge) shares:

```python
def tool_match_score(item: dict, trace: dict) -> float:
    """1.0 only if the right tool was called with every expected arg substring present."""
    call = trace.get("tool_call") or {}
    if call.get("name") != item["expected_tool"]:
        return 0.0
    args_str = str(call.get("args", {})).lower()
    if not all(sub.lower() in args_str for sub in item["expected_args_contains"]):
        return 0.0
    return 1.0

def answer_keyword_score(item: dict, trace: dict) -> float:
    """Fraction of golden keywords present in the final answer — partial credit."""
    answer = trace.get("final_answer", "").lower()
    hits = sum(1 for kw in item["expected_keywords"] if kw.lower() in answer)
    return hits / len(item["expected_keywords"])

def route_match_score(item: dict, trace: dict) -> float:
    return 1.0 if trace.get("route") == item["expected_route"] else 0.0
```

Note: Ragas's own `ToolCallAccuracy` metric (covered in [[llm-judges-eval]]) is, despite living in an LLM-judge library, actually deterministic — pure name+args comparison with no model call — and doubles as a second independent check on tool use.

## How this shows up in the capstone

Milestone 8 — the "one per category, no LLM call, milliseconds" scorers that run alongside the three judge frameworks against the same ~20-item golden set; see [[capstone-milestone-map]].

## Interview fire round

- **Q: Why run a deterministic scorer at all if you already have LLM judges?**
  A: LLM-judge scoring is noisy and can be wrong in ways that are hard to detect on its own — a deterministic scorer gives you a cheap, reproducible independent signal. When the two disagree, that disagreement is exactly the case worth reading by hand.
- **Q: Why does `tool_match_score` give no partial credit but `answer_keyword_score` does?**
  A: A tool call with the wrong argument isn't a partially-correct action — it's the wrong call, full stop. A written answer can legitimately capture most of the required information without literally containing every golden keyword, so partial credit reflects that better.

## Production gotchas & best practices

- Lab gotcha: Ragas compares tool call arguments with case-sensitive exact-string equality — args must be lowercased before comparison to match a golden set written in lowercase, or a functionally-correct tool call scores as a mismatch (`lab-summaries/Day4-Session2-EvalGuardrails.md`).
- Lab gotcha: document what a metric actually measures rather than trusting its name — a metric labeled `expected_route` was, in one real case, scored against answer content rather than the structural routing state, because no golden case exercised the code path that would have exposed the mismatch; left unflagged, that's a silent gap between what the metric name promises and what the code checks (`labs/production-notes.md`).
- Production practice: keep deterministic scorers pure functions of `(item, trace)` with no side effects and no external calls — that's what makes them safe to run in the same pass as the LLM judges without adding to rate-limit pressure, and safe to re-run as a regression gate on every change (see [[eval-driven-development-mindset]]).

## Course vs. production

The lab's deterministic scorers are hand-written per golden-item field (`expected_tool`, `expected_keywords`, …) inside the same notebook as the agent under test. In production, deterministic scoring tends to be extracted into a small shared library reused across every agent in the system (tool-match and schema-validity checks are near-identical regardless of which tool or which agent), and wired into CI so a regression is caught before merge rather than in a manual notebook re-run.

## Related
- **Builds on** — [[eval-driven-development-mindset]]
- **Paired with** — [[llm-judges-eval]]
- **Related** — [[structured-output-repair-loops]], [[retrieval-eval-metrics]]

## Sources

**Lab sources**
- `lab-summaries/Day4-Session2-EvalGuardrails.md` (§ "Deterministic scorers", § "LLM-judge scorers — three independent judges")
- `labs/Day4 Session 2 - Evaluation, Guardrails and Continuous Improvement.ipynb`
- `labs/production-notes.md` (§ "Guardrails")

**Web sources**
- No standalone official-docs page found for "deterministic scoring" as a named practice as of 2026-08-20 — this page is lab/notebook-sourced; the LLM-judge counterpart's sourcing is in [[llm-judges-eval]].
