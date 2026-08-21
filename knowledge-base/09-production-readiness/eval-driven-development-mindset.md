---
stage: "09-production-readiness"
tools: [ragas, deepeval, trulens, langfuse]
tags: [eval, golden-set, mindset, regression-testing]
last_verified: 2026-08-20
verified_against: "no eval-library version pinned in this repo's pyproject.toml as of 2026-08-20 — see llm-judges-eval.md for the libraries themselves"
---

# Eval-driven development mindset

Evaluation is what turns "it worked when I tried it" into a repeatable, falsifiable claim about an agent's behavior — the mental model behind golden sets and regression testing, not yet the scoring mechanics themselves.

## Prerequisites
- [[retrieval-eval-metrics]]
- [[agentic-loop-fundamentals]]
- [[testing-agent-code]]

## In plain English

A demo proves an agent *can* work — once, on the input you happened to type, on a day when the model happened to behave. It proves nothing about the input you didn't try, or what happens after you change a prompt next week. Evaluation is the discipline of replacing that single anecdote with a fixed set of cases you chose in advance (a **golden set**), a way of scoring the agent's output against each one, and a habit of re-running that same set every time something changes — the prompt, the model, the retrieval corpus, a dependency version.

That last part is the regression-testing mental model borrowed from software engineering: a unit test suite doesn't prove your code is *good*, it proves a change didn't silently break something that used to work. Eval plays the same role for an agent's behavior, except the "test" isn't a deterministic assert — it's a score, sometimes fuzzy, sometimes itself produced by another LLM (see [[llm-judges-eval]]). Two agents can look identical from the outside — same "final answer: correct" — while one got there on solid tool calls and grounded retrieval and the other got there on a lucky coincidence. Eval-driven development means you'd rather find that out on your own golden set than from a user.

This is a distinct concern from [[testing-agent-code]]: unit tests answer "does this function do what the code says it should do" (deterministic, code-correctness, mock the LLM out); eval answers "is the agent's *behavior* good enough to ship" (probabilistic, quality-of-output, the LLM call is the thing under test). A node can pass every unit test and still route every query to the wrong tool.

## Core mechanics

There's no fixed API surface for "the eval mindset" — it's a structure you build, not a class you import (the scoring mechanics live in [[deterministic-scorers]] and [[llm-judges-eval]]). The structure itself has three parts:

**1. Component-level, not just output-level, grading.** A single "final answer: correct/incorrect" score can hide a broken middle. A trace worth grading typically has four independently-gradable layers, each of which can fail while the others compensate:

| Layer | What it checks | Can still "look right" if broken because |
|---|---|---|
| Tool use | Right tool, right arguments | — |
| Retrieval | Right documents came back | The final answer happened to already be right, or two documents happened to share the answer |
| Planning/routing | Right sub-task/path chosen | The wrong path can still stumble onto a correct-looking answer |
| Final answer | Correct, grounded, well-formed | This is the layer a demo shows you — and the only one a user-facing test would catch by accident |

Grading only the last row is grading a group project by the final presentation alone — it tells you *that* something's wrong, not *where*.

**2. A golden set, not live traffic.** A fixed collection of representative cases — each one carrying whatever a scorer needs to check it (an expected tool + expected args, an expected retrieved doc, an expected route, a reference answer) — run through the same pipeline every time. Fixed inputs are what make the run reproducible and the score comparable release over release; live traffic isn't controlled enough to tell you anything about a specific change.

**3. Audit the judge.** Once an LLM is doing the grading (see [[llm-judges-eval]]), the judge itself is a model with its own blind spots — it can reward a fluent, well-formatted answer that is factually wrong. The fix is to hand-label a sample of the judge's verdicts and compute an agreement rate against a human: sample the judge's PASS/FAIL calls, label the same cases by hand, and count how often they match. The disagreement direction that costs you is *judge says PASS, human says FAIL* — that's the judge quietly certifying bad output as good. Recalibrate the audit whenever the judge model, its prompt, or the domain changes; an audit done once and never repeated is a claim about a judge that no longer exists.

## Sample code

Lab-sourced (`labs/Day4 Session 2 - Evaluation, Guardrails and Continuous Improvement.ipynb`) — the golden-set item shape and the single trace structure every scorer (deterministic and judge alike) reads from, so component boundaries stay clean:

```python
# one golden-set item, category = "retrieval"
{
    "id": "g07",
    "category": "retrieval",
    "query": "What's the late fee for a returned book?",
    "expected_doc_id": "policy_late_fees",
    "expected_keywords": ["late fee", "per day", "grace period"],
}

# run_agent(query) produces one trace dict every scorer reads from
trace = {
    "query": query,
    "route": route,                 # "tool" | "retrieval" | "direct"
    "tool_call": tool_call,
    "tool_result": tool_result,
    "retrieved_docs": retrieved_docs,
    "final_answer": final_answer,
}
```

A `component_scorer(item, trace)` dispatches each golden item to the deterministic/judge scorers appropriate to its `category`, and always runs the guardrail check on top regardless of category — "safety isn't quality-conditional" (see [[guardrails-injection-detection]]).

## How this shows up in the capstone

Milestone 8 (end-to-end evaluation, guardrails & deployment package, the final capstone gate) — the eval-driven mindset is what the ~20-item golden dataset and component scorers in that milestone are *for*; see [[capstone-milestone-map]].

## Interview fire round

- **Q: Why can a system with a 100% "final answer correct" score still be broken?**
  A: The final-answer score doesn't tell you whether the layers underneath (tool use, retrieval, planning) were actually right — two wrong steps can still coincidentally land on a correct-looking answer, and you won't find out until the layers diverge on a case that doesn't get lucky.
- **Q: Your LLM judge agrees with human labels 87% of the time. Which disagreement direction should worry you more?**
  A: Judge-says-PASS/human-says-FAIL — that's the judge certifying a bad answer as good, which is invisible unless you specifically audit for it. Judge-says-FAIL/human-says-PASS just costs you a false alarm you'll notice.
- **Q: How is eval different from the unit tests in [[testing-agent-code]]?**
  A: Unit tests check code correctness with the LLM call mocked out — deterministic, pass/fail on logic. Eval checks the *quality of the LLM's actual behavior* against a golden set — probabilistic, scored, and the LLM call is exactly the thing being measured.

## Production gotchas & best practices

- Lab gotcha: isolate each scorer's failure inside a multi-metric eval harness — under sustained rate limiting a judge call can exhaust its retry budget and raise; without a per-scorer try/except, an uncaught exception discards every score already computed for that item, including the guardrail result, since Python doesn't return partial results on an uncaught exception (`labs/production-notes.md`).
- Lab gotcha: document what an eval metric actually measures rather than assuming the label matches the mechanism — one production case scored `expected_route` against answer *content*, not the structural routing state, because no golden case exercised the real interrupt route; left unflagged, that's a metric that silently measures something narrower than its name implies (`labs/production-notes.md`).
- Per course material (`presentations/day4.md`, Act 1): grade every layer separately across a representative golden set, not just the final output — the same discipline [[retrieval-eval-metrics]] applies to retrieval, generalized across the whole agent.
- Per course material (`presentations/day4.md`, Act 1): a judge you have never audited "is not a measurement, it is an opinion with a number attached" — track the human-agreement rate as a number over time, not a one-time sanity check, and re-run the audit on every model, prompt, or domain change.
- Production practice: treat a self-check pass over the results table — flagging rows where a deterministic score and an LLM judge disagree by a wide margin (e.g. >0.4) — as the worklist for manual review, not the judge's raw score alone; disagreement is a signal to read the transcript, not evidence either scorer is right.

## Course vs. production

The lab runs its ~20-item golden set once per notebook session and reads the results by hand. In production, the same golden set is re-run on every prompt/model/dependency change as an automated regression gate (often wired through the same experiment runner used for tracing, see [[langfuse-tracing]]), and the human-agreement audit on the LLM judge is repeated on a schedule rather than performed once and trusted indefinitely — a judge audited against last quarter's model version is an audit of a judge that no longer exists.

## Related
- **Builds on** — [[agentic-loop-fundamentals]], [[retrieval-eval-metrics]]
- **Contrasts with** — [[testing-agent-code]]
- **Feeds into** — [[deterministic-scorers]], [[llm-judges-eval]], [[guardrails-injection-detection]]

## Sources

**Lab sources**
- `lab-summaries/Day4-Session2-EvalGuardrails.md` (§ "The system under test — four independently-gradable components", § "Golden dataset — 20 items, 5 per component")
- `labs/Day4 Session 2 - Evaluation, Guardrails and Continuous Improvement.ipynb`
- `labs/production-notes.md` (§ "Schema Validation", § "Guardrails")
- `presentations/day4.md` (Session 2, Act 1 — "Proving It's Good": component-level evaluation, auditing the judge via human-agreement rate)

**Web sources**
- No independent web source found specifically for "component-level LLM pipeline evaluation" as a named practice as of 2026-08-20 — treated as course-material framing (`presentations/day4.md` cites only "general references on component-level / multi-stage LLM pipeline evaluation" without a fetchable URL).
