---
stage: "04-tool-calling-single-agents"
tools: [litellm]
tags: [reflection, self-critique, agent-design, fail-open]
last_verified: 2026-08-20
verified_against: "litellm>=1.96.2 (this repo's pin)"
---

# Reflection pattern

Having the model critique and revise its own output before returning it — a cheap accuracy win that doesn't require a second model.

## Prerequisites
- [[react-pattern]]
- [[structured-output-repair-loops]]

## In plain English

[[structured-output-repair-loops]] (stage 03) checks whether the model's output has the right *shape* — valid JSON, right types, passes a Pydantic validator. Reflection checks something different: whether the answer actually *satisfies the goal*, given whatever evidence the agent gathered. Same skeleton — generate, check, fix — one layer up, now applied to reasoning instead of shape.

Concretely: after a [[react-pattern]] (or any tool-calling) loop produces a draft answer, one more model call is made — not to answer the question again, but to critique the draft against the evidence already gathered. That call replies either `APPROVED` or `REVISE: <what's wrong>`. On `REVISE`, exactly one more call produces a corrected final answer. That's it — one critique pass, one correction pass, both capped, same reasoning as capping ReAct's iterations: bounded cost, bounded risk, no open-ended self-argument with itself.

Your analyst, rereading their own memo against the original brief — not spell-checking it, actually checking whether it answers the question. It's a cheap win specifically because it doesn't need a second, more capable model or a human in the loop — the same model that produced the draft is often perfectly capable of noticing "75 × 0.20 = 15, not 16" when asked to check rather than asked to answer from scratch. Checking is an easier task than generating correctly the first time.

## Core mechanics

The loop, as two extra calls appended after a normal ReAct/tool-calling loop finishes:

1. Run the main loop (ReAct or tool-calling) to a draft answer, as usual.
2. **Critique call**: prompt the model with the original goal, the evidence gathered, and the draft — ask it to reply `APPROVED` or `REVISE: <what's wrong>`.
3. If `APPROVED`: return the draft, done.
4. If `REVISE: ...`: one more call, using the critique as new context, produces a corrected final answer. Return that — do **not** loop back into another critique round.

This is capped at **exactly one revision cycle** by design, not as a lab shortcut — an uncapped "critique the critique" cycle has the same runaway-cost risk as an uncapped ReAct loop, for a much smaller accuracy payoff per additional round.

The other mechanic worth internalizing is what happens when the reflection pass itself can't run — no API key, an outage, whatever. The lab's answer is **fail open**: skip the critique, return the original draft, and report the verdict as a plain `"SKIPPED"` rather than fabricating a fake `APPROVED`. A quality-improvement pass that's currently broken should never block the main pipeline from returning an answer at all — it should degrade the *quality bar*, visibly, not the *availability* of the whole system.

## Sample code

Lab-sourced (Day 1 · Session 2 — `labs/Day1 Session 2 - Tool calling and Single Agent Patterns.ipynb`, Lab B, `run_react_agent_with_reflection`):

```python
import litellm

CRITIQUE_PROMPT = """You are reviewing a draft answer against the original
question and the evidence gathered while producing it.

Question: {question}
Evidence: {evidence}
Draft answer: {draft}

Reply with exactly one of:
APPROVED
REVISE: <one sentence on what's wrong>"""

def run_react_agent_with_reflection(question: str) -> dict:
    draft, evidence = run_react_agent(question)  # the loop from react-pattern.md

    if not litellm_key_available():
        # fail open: a broken/unavailable quality pass never blocks the pipeline
        return {"answer": draft, "reflection": "SKIPPED"}

    critique_response = litellm.completion(
        model="gemini/gemini-flash-lite-latest",
        messages=[{"role": "user", "content": CRITIQUE_PROMPT.format(
            question=question, evidence=evidence, draft=draft)}],
    )
    verdict = critique_response.choices[0].message.content.strip()

    if verdict.startswith("APPROVED"):
        return {"answer": draft, "reflection": verdict}

    # exactly one revision cycle — never loop back into another critique round
    revise_response = litellm.completion(
        model="gemini/gemini-flash-lite-latest",
        messages=[{"role": "user", "content":
            f"Question: {question}\nEvidence: {evidence}\n"
            f"Original draft: {draft}\nCritique: {verdict}\n"
            f"Produce a corrected final answer."}],
    )
    corrected = revise_response.choices[0].message.content
    return {"answer": corrected, "reflection": verdict}
```

## Alternatives

| Approach | Where it lives | Trade-off |
|---|---|---|
| Single-pass self-critique (above) | Hand-rolled, one model, one revision cap | Cheapest — reuses the same model, bounded to one extra round-trip |
| Full Reflexion (persistent verbal reinforcement across attempts) | Research pattern, not this stage's scope | Maintains reflective memory across *multiple* attempts at a task rather than one in-conversation pass — a fuller, stateful treatment; see the forward-pointer below, this is stage 09's territory |
| LLM-as-judge evaluating a separate, independently-produced answer | Eval harnesses (stage 09/10) | A different model or a fresh, isolated call reviews the draft rather than the same model critiquing its own recent output — reduces the "shares its own blind spots" risk at the cost of a second call/model |

## How this shows up in the capstone

Milestone 2 — reflection is the optional quality layer on top of the tool-enabled single agent; [[capstone-milestone-map]] groups it with M2's single-agent tool-calling work. The Escalation Reviewer agent later in the build order (M6) is conceptually the same critique-then-decide shape, applied to a different draft (another agent's proposed action rather than a text answer).

## Interview fire round

- **Q: What does reflection check that the stage-03 structured-output repair loop doesn't?**
  A: Repair checks shape (valid JSON, right types); reflection checks whether the answer actually satisfies the goal given the evidence gathered — a shape-valid answer can still be substantively wrong.
- **Q: Why cap reflection at exactly one revision cycle instead of looping until `APPROVED`?**
  A: Same reasoning as capping ReAct's iterations — bounded cost and risk. Additional critique rounds have diminishing accuracy payoff and the same runaway-loop risk as any uncapped agentic loop.
- **Q: What should happen if the reflection pass itself can't run (no key, outage)?**
  A: Fail open — skip the critique and return the original draft with a plain `"SKIPPED"` label, rather than fabricating a fake `APPROVED` or blocking the whole pipeline on a broken quality-improvement step.

## Production gotchas & best practices

- Lab gotcha: needs a real model key to run at all — the offline/no-key path reports a plain skip rather than faking a critique, exactly the fail-open behavior above.
- Production practice (fail open): a broken quality-improvement pass should degrade gracefully, not take the main pipeline down with it — this generalizes past reflection to any optional post-processing step.
- Production practice: a model critiquing its own output shares its own blind spots — reflection catches arithmetic slips and obvious gaps well, but is not a substitute for an independent eval harness ([[llm-judges-eval]], [[deterministic-scorers]]) for anything higher-stakes than a quality nudge.
- Defense-in-depth framing: an iteration cap and a reflection/fabrication check aren't redundant safeguards — they're layered defense at different points (bounding the *search* for an answer vs. checking the *quality* of the one found), the same pattern as enforcing a hard business-rule cap at both the orchestration layer and the service layer rather than trusting one check alone.

## Course vs. production

The lab's reflection is a single in-conversation critique pass — draft, one critique, at most one correction, all within the same run. This is deliberately narrower than full **Reflexion** (Shinn et al.) as a production pattern, which maintains reflective text in a persistent memory buffer *across multiple separate attempts* at a task, closer to a lightweight learning signal than a one-shot quality check. That fuller, stateful treatment belongs to stage 09 — this page's reflection is the cheap, bounded version worth reaching for first.

## Related
- **Builds on** — [[react-pattern]], [[structured-output-repair-loops]]
- **Narrower version of** — full Reflexion-as-production-pattern (stage 09, not duplicated here)
- **Same fail-open discipline appears in** — [[retry-fallback-patterns]], [[circuit-breaker-pattern]]
- **Independent-check alternative** — [[llm-judges-eval]], [[deterministic-scorers]]

## Sources

**Lab sources**
- `lab-summaries/Day1-Session2-ToolCalling.md` (§ B3 Reflection)
- `labs/Day1 Session 2 - Tool calling and Single Agent Patterns.ipynb`
- `presentations/day1.md` (Day 1 · Session 2, Act 3 Q2 — "Reflection: The Same Loop, One Layer Up")
- `labs/production-notes.md` — fail-open behavior on a broken reflection pass, defense-in-depth framing for layered caps/checks

**Web sources**
- [Shinn et al., "Reflexion: Language Agents with Verbal Reinforcement Learning" (arXiv:2303.11366)](https://arxiv.org/abs/2303.11366) — persistent verbal self-reinforcement across attempts, NeurIPS 2023, accessed 2026-08-20
