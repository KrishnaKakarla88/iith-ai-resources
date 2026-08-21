---
stage: "00-ai-and-llm-basics"
tools: [groq, litellm]
tags: [primer, llm, fundamentals]
last_verified: 2026-08-21
verified_against: "conceptual primer — no version-specific claims"
---

# What is an LLM

A large language model is a next-token predictor: a huge set of trained numeric weights that, given some text, outputs a probability distribution over what token comes next — nothing more mystical than that, and everything else in this course is built on top of that one mechanism.

## Prerequisites
None — this is the entry point of the knowledge base.

## In plain English

Strip away the branding and an LLM is a function: it takes in text (as tokens) and produces a probability for every possible next token, over and over, one token at a time. It got good at this by reading an enormous amount of text during **training** — adjusting billions of internal numbers (**weights**) so that, statistically, its next-token guesses look like fluent, plausible continuations of whatever came before. Once training is done, the weights are frozen, and every time you send it a message you're running **inference**: a single forward pass through those frozen weights, repeated token by token, with nothing learned or remembered from the call before it.

Two consequences fall directly out of this:

- **Knowledge is frozen at a training cutoff.** Whatever the model "knows" is whatever got compressed into its weights during training — it has no live connection to today's weather, today's stock price, or a row in your database. Anything past the cutoff, or anything that changes over time, has to be handed to it at inference time (a tool call, a retrieved document) — the model cannot go look it up itself.
- **It has no hands.** An LLM can only produce text — including text *shaped like* a request to call a function — it cannot execute code or hit an API on its own. That's the seed of why [[tool-calling-fundamentals]] exists at all: something else has to actually run the action and hand the result back in.

## Core mechanics

| Concept | What it means |
|---|---|
| Weights | Billions of learned numeric parameters, fixed once training finishes — the model's entire "knowledge" lives here, not in any external database |
| Training | The (expensive, one-time-per-model-version) process of adjusting weights against a huge text corpus so next-token predictions get statistically better |
| Inference | Running the already-trained, frozen model on new input — this is what every API call you make actually does |
| Parametric knowledge | Facts implicitly encoded in the weights from training — frozen, not updatable without retraining or fine-tuning |
| Training cutoff | The date training data stops — anything after it, or anything inherently live (weather, prices, your own data), isn't in the weights |
| Next-token prediction | The model's only operation: given tokens so far, output a probability distribution over the next token, sample one, repeat |

## Sample code

There's no API surface specific to "what is an LLM" — the mechanism is conceptual. The shape it takes in code, everywhere in this stack, is a single request/response call:

```python
import litellm

response = litellm.completion(
    model="groq/llama-3.1-8b-instant",
    messages=[{"role": "user", "content": "What is 20% of 75?"}],
)
print(response.choices[0].message.content)
```

Every call like this is a fresh inference pass over frozen weights — see [[how-llms-generate-text]] for what actually happens inside that call, and [[what-is-an-llm]]'s neighbor pages for why nothing is remembered between two calls like it.

## How this shows up in the capstone

Milestone 1's provider-agnostic LLM client exists precisely because inference is "just" a stateless function call per provider — swapping `model="groq/llama-3.1-8b-instant"` for another string is the whole cost of switching providers; see [[capstone-milestone-map]].

## Interview fire round

- **Q: Does an LLM "understand" your question, or predict it?**
  A: Neither in a human sense — it samples the next token from a learned probability distribution, repeated one token at a time, informed by everything before it in the input. There's no separate comprehension step.
- **Q: Why can't an LLM tell you today's weather?**
  A: Its knowledge is frozen at a training cutoff and lives entirely in its weights — there's no live connection to the outside world. It needs a tool call to fetch anything current.

## Production gotchas & best practices

- Per course material (`presentations/day1.md`): a fluent, confident answer is not the same as a correct one — training optimizes for statistically plausible continuations, not verified truth, so treat model output as a claim to validate, not a fact.
- Production practice: never assume a model's parametric knowledge is current — pin an explicit strategy (tool call, RAG, or accept staleness) for anything that changes over time, rather than trusting the weights by default.

## Course vs. production

The labs treat "what is an LLM" as settled background and jump straight to calling one via an API. In production, this framing still matters operationally: every "the model got this wrong" incident report should start by asking whether the answer required knowledge past the training cutoff or live data the model was never given a tool to fetch — that's a design gap, not a model failure.

## Related
- **Feeds into** — [[tokens-and-tokenization]], [[how-llms-generate-text]], [[model-selection-cost-latency-tradeoffs]]

## Sources

**Lab sources**
- `lab-summaries/Day1-Session1-Foundations.md` (§ "Part 1 — Raw LLM Client + LiteLLM Comparison")
- `labs/Day1 Session 1 - Foundations of Reliable AI Agents.ipynb`

**Deck sources**
- `presentations/day1.md` (Session 1 · Act 1 — "What the Model Actually Does"; Session 2 · Act 1 · Question 1 — "What is a Training Cutoff?")
