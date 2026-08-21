---
stage: "00-ai-and-llm-basics"
tools: [litellm, groq]
tags: [primer, decoding, sampling, temperature]
last_verified: 2026-08-21
verified_against: "litellm 1.96.x (this repo's pin)"
---

# How LLMs generate text

An LLM generates text **autoregressively** — one token at a time, each one sampled from a probability distribution conditioned on everything before it — and sampling parameters like temperature, top-p, and top-k are the knobs that decide how that sampling step behaves, which is why the same prompt can produce different output on different runs.

## Prerequisites
- [[what-is-an-llm]]
- [[tokens-and-tokenization]]

## In plain English

Once a model has computed a probability distribution over its whole vocabulary for "what token comes next," it still has to pick one. It doesn't always pick the single most likely token — that would make output rigid and repetitive. Instead it **samples** from the distribution, and a handful of parameters control how that sampling behaves: how random it is, how much of the distribution's tail is even eligible, and how long the response is allowed to run before being cut off. Change any of these and you change the character of the output without touching the prompt at all.

That sampled token then gets appended to the input, and the whole distribution is recomputed for the *next* token — hence "autoregressive": each step feeds on the output of the step before it. This is also why generation is inherently sequential and can't skip ahead: token 50 genuinely depends on tokens 1-49 having already been chosen.

## Core mechanics

| Parameter | What it does |
|---|---|
| `temperature` | Scales how "flat" or "peaked" the probability distribution is before sampling — near 0 pushes toward the single most likely token each step (near-deterministic, not guaranteed); higher values flatten the distribution, letting less-likely tokens get picked more often |
| `top_p` (nucleus sampling) | Restricts sampling to the smallest set of tokens whose cumulative probability reaches `p` — a different lever than temperature for controlling randomness; the lab's own guidance is to use one or the other, not both at once |
| `top_k` | Restricts sampling to only the `k` most probable tokens at each step, before any temperature/top-p is applied |
| `max_tokens` | Hard cap on output length — hitting it truncates the response mid-thought, and the response's `finish_reason` comes back as `"length"` rather than `"stop"`, a signal worth checking explicitly |
| `stop` | One or more strings that end generation immediately once produced — used deliberately in [[react-pattern]] to stop the model from hallucinating its own fake tool observation |
| `seed` | Requests best-effort reproducibility for a given input + parameters — not a hard guarantee across all providers/models |
| `frequency_penalty` / `presence_penalty` | Discourage repeating tokens that already appeared (frequency: scales with how often; presence: any repeat at all) |

## Sample code

Lab-sourced (`labs/Day1 Session 1 - Foundations of Reliable AI Agents.ipynb`), the same `completion()` call with generation knobs exposed:

```python
import litellm

response = litellm.completion(
    model="groq/llama-3.1-8b-instant",
    messages=[{"role": "user", "content": "Summarize this ticket in one sentence."}],
    temperature=0,       # near-deterministic — not a hard guarantee
    max_tokens=150,
    stop=["\n\n"],
)

if response.choices[0].finish_reason == "length":
    ...  # output was truncated at max_tokens, not a natural stopping point
```

Some models additionally separate a reasoning trace from the final answer — e.g. `groq/openai/gpt-oss-120b` with `reasoning_effort="low"` returns `response.choices[0].message.reasoning` alongside `.content`. The field name isn't standardized across providers; the lab's own guidance is to inspect `message.model_dump()` rather than assume a name.

## How this shows up in the capstone

Milestone 1's cost/latency/quality comparison across models runs the same prompt at fixed settings (e.g. `temperature=0`) across providers specifically so output variability is attributable to the model, not to uncontrolled sampling noise; see [[capstone-milestone-map]].

## Interview fire round

- **Q: Why does the same prompt sometimes produce a different answer on two separate calls, even at `temperature=0`?**
  A: `temperature=0` is near-deterministic, not guaranteed — floating-point non-determinism, batching effects on the provider's infrastructure, or minor backend changes can still produce slightly different output.
- **Q: What's the practical difference between `temperature` and `top_p`?**
  A: Temperature reshapes the whole probability distribution (flatter or peakier); `top_p` instead truncates the distribution to its most-probable cumulative mass before sampling. They're two different levers on the same step — the lab's guidance is to tune one, not stack both.

## Production gotchas & best practices

- Lab gotcha: `finish_reason="length"` (hit `max_tokens`) versus `"stop"` (a natural end) look identical if you only read `.content` — always check `finish_reason` before trusting that a response is complete, especially for structured output the rest of your pipeline will parse.
- Lab gotcha: a model's reasoning-trace field name varies by provider/model (`message.reasoning`, or nothing at all) — inspect `message.model_dump()` rather than hardcoding a field name across providers.
- Production practice: pin `temperature=0` (or as low as the task allows) for anything downstream code parses or validates — structured extraction, tool-call argument generation, classification — and reserve higher temperature for genuinely open-ended generation (brainstorming, copy variants), where variability is a feature, not a bug.

## Course vs. production

The lab sets `temperature=0` as a blanket default across its cost/latency comparison to keep the comparison fair. In production, sampling parameters are typically tuned per task rather than globally — deterministic settings for anything feeding a validator or database, higher-temperature settings reserved for tasks that actually want variety, and `seed` used where a provider supports it for debugging reproducibility rather than relied on for production determinism guarantees.

## Related
- **Builds on** — [[what-is-an-llm]], [[tokens-and-tokenization]]
- **Feeds into** — [[prompting-basics]], [[context-windows-and-limits]]
- **Used by** — [[react-pattern]] (`stop` sequences preventing hallucinated observations)

## Sources

**Lab sources**
- `lab-summaries/Day1-Session1-Foundations.md` (§ "Part 1 — Raw LLM Client + LiteLLM Comparison", point 4 — "`completion()` knobs")
- `labs/Day1 Session 1 - Foundations of Reliable AI Agents.ipynb`

**Deck sources**
- `presentations/day1.md` (Session 1 · Act 1 — "One Token, Informed by Everything Before It")
