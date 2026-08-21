---
stage: "00-ai-and-llm-basics"
tools: [litellm, groq, gemini]
tags: [primer, model-selection, cost, latency, benchmarks]
last_verified: 2026-08-21
verified_against: "litellm 1.96.x (this repo's pin); groq/gemini model ids not pinned in pyproject.toml"
---

# Model selection: cost/latency tradeoffs

There is no single "best" model — only the best fit for a given task's budget, latency target, and risk tolerance — which is why this course pairs a fast/cheap model for reasoning with a separate, different-vendor provider for embeddings instead of buying everything from one place.

## Prerequisites
- [[what-is-an-llm]]
- [[tokens-and-tokenization]]

## In plain English

"Which model should I use?" is the wrong first question. The right one is: which model passes my evals at the lowest acceptable cost, latency, and risk for *this* task? A frontier model that tops a general leaderboard can still be the wrong pick if it's too slow for a real-time support flow, too expensive at your request volume, or its provider can't meet a data-residency requirement — none of which a benchmark score captures.

Pricing and latency are both driven by the same underlying unit: tokens (see [[tokens-and-tokenization]]). Cost scales with input tokens *and* output tokens (usually priced separately, output typically pricier), and a longer conversation costs and takes more time on every subsequent call because the entire history is resent and reprocessed each time (see [[context-windows-and-limits]]) — a 50-turn conversation is not "a bit more" than a 2-turn one, it's the whole transcript, billed and processed again, every turn.

This is also why a real system rarely buys every capability from one vendor. Chat/reasoning quality and embedding quality are separate capabilities with separate cost/latency/quality curves — nothing requires the same provider to be best (or even available) at both. This course pairs Groq (`groq/llama-3.1-8b-instant`, fast and cheap inference for chat/reasoning) with Gemini (a separate provider, for embeddings) rather than sourcing both from one vendor — see [[embeddings-models]] for the embedding-side specifics.

## Core mechanics

A rough back-of-envelope for estimating what a chat flow actually costs at volume:

```
tokens/day = (tokens/turn) x (turns/session) x (sessions/day)
cost/day   = (tokens/day / 1,000,000) x price per 1M tokens
```

A worked example from the deck: ~200 tokens/turn x 20 turns/session = 4,000 tokens by the last turn of one session; x 500 sessions/day = 2,000,000 tokens/day; at $2.50/1M tokens that's $5/day — for one *untrimmed* support flow. Change any one number (turns per session, price per token, sessions per day) and the arithmetic scales directly — this is the exact calculation a provider-agnostic client needs to survive at real volume, not just in a notebook.

| Concept | What it means |
|---|---|
| Input vs. output pricing | Most providers price input and output tokens separately, output usually at a higher rate — a chatty system prompt and a verbose reply are billed differently |
| Latency vs. quality | Smaller/cheaper models generally respond faster; larger/frontier models are usually slower and pricier but often stronger on hard reasoning — the tradeoff has to be chosen per task, not assumed |
| Provider dialect | Each vendor's SDK has its own field names, request/response shapes, and supported parameters — "OpenAI-compatible" means a request may parse, not that every parameter behaves identically |
| Benchmark tiering | General leaderboards (LMArena, Artificial Analysis, LiveBench) rank broad capability; task/domain leaderboards (BFCL for tool-use, HealthBench, LegalBench) rank fit for a specific job — the right one depends on the task, not "which is smartest overall" |
| Contamination & saturation | Two known benchmark failure modes: a model may have memorized the test set, or every top model may be bunched near the ceiling — triangulate across multiple boards rather than trusting one number |

## Sample code

Lab-sourced (`labs/Day1 Session 1 - Foundations of Reliable AI Agents.ipynb`) — the same function called across providers by changing only the `model=` string, with latency and token counts collected for comparison:

```python
import time, litellm

def compare_model(model: str, messages: list[dict]) -> dict:
    start = time.time()
    response = litellm.completion(model=model, messages=messages)
    latency = time.time() - start
    return {
        "model": model,
        "latency_sec": latency,
        "input_tokens": litellm.token_counter(model=model, messages=messages),
        "output_tokens": litellm.token_counter(model=model, text=response.choices[0].message.content),
    }

comparison = [compare_model(m, messages) for m in ["groq/llama-3.1-8b-instant", "gpt-4o-mini"]]
```

`groq/llama-3.1-8b-instant` and Gemini model ids are passed as plain strings to LiteLLM — neither is a tracked dependency pin in this repo's `pyproject.toml` (unlike `litellm`, `langgraph`, `fastmcp`, which are versioned project dependencies); the model choice lives in application config/code, not in the dependency lockfile.

## How this shows up in the capstone

Milestone 1's cost/latency/token comparison table is exactly this exercise, run for real across providers before the rest of the pipeline commits to one; see [[capstone-milestone-map]].

## Interview fire round

- **Q: Why can a "worse" model on a general leaderboard still be the right production choice?**
  A: General leaderboards measure broad capability, not fit — cost, latency, data residency, and task-specific performance (a domain leaderboard, not a general one) can all rule out a top-ranked model regardless of its score.
- **Q: Why does a 50-turn conversation cost meaningfully more than a 2-turn one, beyond "more messages"?**
  A: The entire message history is resent and reprocessed on every single call (see [[what-is-an-llm]], [[prompting-basics]]) — cost and latency both scale with the full accumulated transcript, not just the newest turn.

## Production gotchas & best practices

- Lab gotcha: cost/latency comparisons must count tokens *per model*, not off one global ratio — different providers/models tokenize the same text into different counts, so `litellm.token_counter(model=...)` takes a model argument rather than assuming a fixed table (see [[tokens-and-tokenization]]).
- Lab gotcha (per course material, `presentations/day1.md` Act 4): "API-compatible" doesn't mean identical behavior — a request built for one OpenAI-compatible endpoint may parse against another provider without erroring, while quietly ignoring or reinterpreting a parameter the response never signals.
- Production practice (per course material, `presentations/day1.md` Act 4): triangulate model choice across at least one general leaderboard and one task/domain leaderboard, and re-benchmark before committing real traffic — leaderboard contamination and saturation both make a single score unreliable in isolation.
- Production practice: pin the exact model id in config, not just in code that happens to work today — providers periodically retire or silently update "latest"-style aliases, which can change behavior, latency, or cost without a code change on your side.

## Course vs. production

The lab's comparison is a one-off notebook cell, run once against a small fixed prompt set to illustrate the tradeoff. In production, model selection is typically an ongoing, re-evaluated decision — tied to an eval harness (see [[eval-driven-development-mindset]]) rather than a benchmark checked once, because pricing, provider throughput, and the competitive model landscape all shift on a timescale of weeks, not once per project.

## Related
- **Builds on** — [[what-is-an-llm]], [[tokens-and-tokenization]]
- **Feeds into** — [[fine-tuning-vs-rag]], [[embeddings-models]]
- **See also** — [[litellm-as-gateway]] (the provider-abstraction layer this tradeoff assumes)

## Sources

**Lab sources**
- `lab-summaries/Day1-Session1-Foundations.md` (§ "Part 1 — Raw LLM Client + LiteLLM Comparison", point 6 — "Cost/latency/token comparison")
- `labs/Day1 Session 1 - Foundations of Reliable AI Agents.ipynb`
- `lab-summaries/Day1-Session2-ToolCalling.md` (§ "Setup" — `LAB_MODEL = "gemini/gemini-flash-lite-latest"`, chosen for free-tier throughput over the full Flash model)
- `knowledge-base/06-rag/embeddings-models.md` (resolves the Groq-chat/Gemini-embedding provider pairing and the `gemini-embedding-001` vs. `text-embedding-004` discrepancy)

**Deck sources** (per course material — near-future model names below are cited as course material, not independently web-verified)
- `presentations/day1.md` (Session 1 · Act 2 · Question 1 — token-cost arithmetic; Session 1 · Act 4 — provider dialects, benchmark tiering, the Kimi K3/Qwen3.6 worked example)
