---
stage: "09-production-readiness"
tools: [ragas, deepeval, trulens]
tags: [eval, llm-judge, ragas, deepeval, trulens]
last_verified: 2026-08-20
verified_against: "no version pinned in this repo's pyproject.toml — see Course vs. production"
---

# LLM judges for eval

An LLM judge uses a second model call to score the first model's output on a dimension too fuzzy for a deterministic check — grounded-ness, correctness against a rubric, relevance — and, being a model itself, needs its own accuracy audited rather than trusted by default.

## Prerequisites
- [[eval-driven-development-mindset]]
- [[deterministic-scorers]]

## In plain English

Some questions a golden answer can't settle with a keyword check. "Is this answer grounded in the retrieved context, or did the model add a claim the context never supported?" isn't a string match — it needs something that can read the answer and the context and reason about entailment. An LLM judge is exactly that: a separate model call, given the output (and whatever reference material it needs) and a rubric or prompt, that returns a score and — in the better-designed judges — a written reason, so a low score is debuggable instead of a black-box number.

The catch, and the reason [[eval-driven-development-mindset]] insists on auditing the judge: the judge is a model, and it inherits every blind spot a model has. A documented failure mode is the judge rewarding *style* — a long, fluent, well-formatted answer scores well even when it's factually wrong, because "confident and articulate" correlates with "correct" in the judge's training distribution far more than it should. The fix isn't to distrust judges wholesale; it's to measure them: hand-label a sample of the judge's verdicts, compute the agreement rate against a human, and re-check that number whenever the judge model, its prompt, or the domain changes.

## Core mechanics

Three frameworks show up together in the lab, deliberately cross-checked against each other rather than trusted individually — if all three agree an answer is faithful, that's stronger evidence than any one judge's opinion, and disagreement is a signal to read the transcript by hand.

| Framework | Judge mechanism used | Output shape |
|---|---|---|
| Ragas | `Faithfulness` (is the answer entailed by the context) and `ContextPrecisionWithReference` — true LLM-judge metrics | Score 0-1 |
| Ragas | `ToolCallAccuracy` — despite living in the same library, this one is actually deterministic (name+args comparison, no model call) | Score 0-1, no judge involved |
| DeepEval | `GEval` — builds a custom rubric judge from a plain-language description of the grading criteria, no hand-written judge prompt needed | `(score, reason)` |
| TruLens | Feedback-function providers called directly (`groundedness_measure_with_cot_reasons`, `context_relevance_with_cot_reasons`) | `(score, reasons_dict)` with chain-of-thought reasoning |

**Auditing the judge**, per course material (`presentations/day4.md`, Session 2 Act 1): sample the judge's PASS/FAIL calls on a subset of the golden set, hand-label the same cases, and compute agreement = (matches) / (sampled cases). A worked example from the deck: a judge scored 200 answers, 40 were hand-labeled, and agreement came out to 35/40 = 87.5% — but all four disagreements were long, fluent, well-formatted answers that were factually wrong, meaning the judge was rewarding style. The costly disagreement direction is *judge says PASS, human says FAIL*: that's the judge certifying bad output as good, invisible unless you specifically go looking for it. Recalibrate — re-run the audit — on every model swap, prompt change, or new domain, since any of the three can silently shift what the judge rewards.

## Sample code

Lab-sourced (`labs/Day4 Session 2 - Evaluation, Guardrails and Continuous Improvement.ipynb`), one call per framework against the same trace:

```python
# Ragas — must use AsyncOpenAI, not sync OpenAI: .ascore() calls the async path internally
from ragas.metrics import Faithfulness
from openai import AsyncOpenAI

faithfulness = Faithfulness(llm=ragas_llm_wrapper)  # wraps an AsyncOpenAI-compatible client
score = await faithfulness.single_turn_ascore(sample)

# DeepEval — GEval builds a rubric judge from plain-language criteria, no judge prompt to hand-write
from deepeval.metrics import GEval
correctness = GEval(
    name="Correctness",
    criteria="Determine whether the actual output is factually correct given the expected output.",
    evaluation_params=["input", "actual_output", "expected_output"],
)
correctness.measure(test_case)
score, reason = correctness.score, correctness.reason

# TruLens — feedback-function providers called as plain scoring functions
from trulens.providers.openai import OpenAI as TruOpenAI
provider = TruOpenAI()
score, reasons = provider.groundedness_measure_with_cot_reasons(source=context, statement=answer)
```

**Setup gotcha worth keeping**: Ragas 0.4.3 has an upstream bug that imports `ChatVertexAI` from a `langchain_community` path the `langchain-community` package deleted (moved to `langchain-google-vertexai`); the lab's fix registers a harmless stub module under that exact import path in `sys.modules` before importing Ragas. Confirm this is still needed against whatever Ragas version you pin — it's the kind of transient-dependency breakage that gets fixed upstream without notice.

## Alternatives

| Framework | Approach | Boring/simple alternative? |
|---|---|---|
| [Ragas](https://docs.ragas.io/en/stable/) | RAG-pipeline-focused metric suite (`Faithfulness`, `ContextPrecision`, `ContextRecall`); async-native (`.ascore()`); integrates with any OpenAI-compatible endpoint | No |
| [DeepEval](https://deepeval.com/docs/getting-started) | General LLM-eval framework; `GEval` custom rubric metrics from plain-language criteria; plugs into `pytest`/`vitest` so `deepeval test run` behaves like a normal test command; supports OpenAI, Azure OpenAI, Anthropic, Gemini, Ollama, and custom/local models | No |
| [TruLens](https://www.trulens.org/) | OpenTelemetry-native tracing + "RAG triad" feedback functions (groundedness, context relevance, answer relevance); instruments apps via decorators or auto-instrumentation for popular frameworks | No |
| Hand-written rubric prompt + any chat-completion call | A single prompt template that asks the model to score against your own rubric and return JSON, no eval library at all | **Yes** — the boring option; loses the batteries (async batching, pytest integration, pre-built RAG-triad metrics, standardized `(score, reason)` shape) but works with nothing beyond an LLM client you already have |

## How this shows up in the capstone

Milestone 8 — Ragas/DeepEval/TruLens run as three independent judges against the same golden set, cross-checked against each other and against the deterministic scorers in [[deterministic-scorers]], with results logged to Langfuse via `run_experiment`; see [[capstone-milestone-map]].

## Interview fire round

- **Q: Why run three separate LLM-judge frameworks instead of picking one?**
  A: Each judge is a model with its own blind spots. If all three independently agree an answer is faithful, that's stronger evidence than any single judge's opinion; when they disagree, that's a specific signal to read the transcript by hand rather than trust any one number.
- **Q: You audit a judge and get 87.5% agreement with human labels. Is that framework good enough to ship?**
  A: The number alone doesn't say — you have to look at *which* direction the disagreements ran. Judge-says-PASS/human-says-FAIL is the expensive direction (bad output certified as good, invisible without an audit); judge-says-FAIL/human-says-PASS just costs a false alarm you'll catch immediately.
- **Q: Why does Ragas's `ToolCallAccuracy` sit inside an "LLM judge" library if it's deterministic?**
  A: Because it scores a different signal (tool-call correctness) that happens not to need a model call — pure name+argument comparison — while the library's other metrics (`Faithfulness`, `ContextPrecision`) genuinely need an LLM to judge semantic entailment. It's grouped by product, not by mechanism.

## Production gotchas & best practices

- Lab gotcha: each judge call should be individually wrapped in try/except inside the scoring function that dispatches to all of them — under sustained rate limiting, a single judge can exhaust its retry budget and raise, and an uncaught exception discards every score already computed for that item (Python doesn't return partial results on an uncaught exception), including scores from judges that already succeeded (`lab-summaries/Day4-Session2-EvalGuardrails.md`).
- Lab gotcha: free-tier rate limits are shared across every call source, not just the agent — the agent itself and all three judge frameworks make their own HTTP calls against the same quota, so pacing has to gate on total calls-per-minute across all four, not just the agent's own call rate (`lab-summaries/Day4-Session2-EvalGuardrails.md`).
- Production practice: track the human-agreement audit as a number over time on the same dashboard as the eval scores themselves, not a one-off sanity check performed once at setup — a judge audited against last quarter's model version is an audit of a judge that no longer exists (per course material, `presentations/day4.md`).
- Production practice: prefer a judge that returns a reason alongside the score (DeepEval's `GEval`, TruLens's `*_with_cot_reasons`) over a bare number — the reason is what makes a low score debuggable instead of a black box, and is what you'll actually read during the disagreement audit.

## Course vs. production

The lab runs all three frameworks against `gemini-flash-lite-latest` via its OpenAI-compatible endpoint, rate-limit-paced to survive a free tier (65 calls total across the full golden-set run, ~10-15 minutes realistically once 429 retries are counted). In production, judge calls are typically run against a model chosen independently of the model under test — using the same model to both generate and grade an answer risks the judge sharing the generator's blind spots — and batched/scheduled outside the request path entirely, since judge latency has no reason to be on the critical path of a live user request.

## Related
- **Builds on** — [[eval-driven-development-mindset]]
- **Paired with** — [[deterministic-scorers]]
- **Feeds into** — [[guardrails-injection-detection]], [[langfuse-tracing]]

## Sources

**Lab sources**
- `lab-summaries/Day4-Session2-EvalGuardrails.md` (§ "LLM-judge scorers — three independent judges", § "Rate-limit-safe call wrapper")
- `labs/Day4 Session 2 - Evaluation, Guardrails and Continuous Improvement.ipynb`
- `presentations/day4.md` (Session 2, Act 1 — "Proving It's Good": component-level evaluation, auditing the judge via human-agreement rate, the 87.5%-agreement worked example)

**Web sources**
- [Ragas documentation](https://docs.ragas.io/en/stable/) — Faithfulness/ContextPrecision metric definitions, `ascore`/async scoring, accessed 2026-08-20
- [DeepEval — Getting Started](https://deepeval.com/docs/getting-started) — GEval custom metrics, pytest integration (`deepeval test run`), supported providers, accessed 2026-08-20
- [TruLens](https://www.trulens.org/) — OpenTelemetry-native instrumentation, feedback functions, RAG-triad framing, version 2.12 current as of access, accessed 2026-08-20
