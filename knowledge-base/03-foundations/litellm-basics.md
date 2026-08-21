---
stage: "03-foundations"
tools: [litellm]
tags: [litellm, completion-api, llm-client]
last_verified: 2026-08-20
verified_against: "litellm>=1.96.2"
---

# LiteLLM basics

LiteLLM's unified `litellm.completion()` call — one function signature and one response shape across providers, instead of a different SDK and message format per vendor.

## Prerequisites
- [[raw-llm-clients]]

## In plain English

[[raw-llm-clients]] showed that Groq's SDK and the OpenAI SDK against Groq's endpoint use the identical `messages` shape and call pattern — the only thing that differs across real providers (OpenAI, Anthropic, Gemini) is the SDK object and some field names. LiteLLM is a thin library that normalizes that difference away entirely: you call `litellm.completion(model=..., messages=...)` and it dispatches to whichever provider's SDK/API the `model=` string names, returning a response shaped like OpenAI's `ChatCompletion` object regardless of which provider actually answered. The messages list, the roles, and the response's `.choices[0].message.content` path stay the same no matter what's behind `model=`.

The other half of `completion()` is the set of generation "knobs" — parameters that shape *how* the model generates, not *what* you're asking it. `temperature` controls randomness, `max_tokens` caps length, `stop` sequences end generation early, `response_format` switches between prose and JSON. These aren't LiteLLM inventions — they're the OpenAI-style parameter set that most providers converged on — but LiteLLM validates and forwards them per-provider so you don't need to know which provider supports which knob.

## Core mechanics

| Parameter | What it controls | Notes |
|---|---|---|
| `model` | Which provider + model to call | `"groq/llama-3.1-8b-instant"`, `"gpt-4o-mini"`, `"anthropic/claude-sonnet-4-6"` — the provider prefix is what routes the call |
| `messages` | The conversation | List of `{"role": "system"/"user"/"assistant", "content": ...}` |
| `temperature` | Randomness, 0–2 | 0 ≈ deterministic (not guaranteed); higher = more varied |
| `max_tokens` | Hard cap on output length | Hitting the cap sets `finish_reason="length"`, not `"stop"` — a truncated, not a complete, answer |
| `stop` | Up to 4 sequences that end generation early | LiteLLM truncates longer lists unless `litellm.disable_stop_sequence_limit = True` |
| `seed` | Best-effort reproducibility | Same seed + same params *should* return the same result — not guaranteed across all providers |
| `stream` | Return chunks instead of one response | See [[streaming-responses]] |
| `response_format` | `{"type": "json_object"}` (JSON mode) or `{"type": "json_schema", ...}` (schema-enforced) | See [[structured-output-repair-loops]] |
| `top_p` | Nucleus sampling — alternative to `temperature` | Provider guidance: tune one or the other, not both together |
| `frequency_penalty` / `presence_penalty` | Penalize token repetition | Numeric, provider-supported to varying degrees |

`litellm.token_counter(model=..., messages=...)` counts input tokens using the tokenizer registered for that model (falling back to `tiktoken` otherwise); pass `text=...` instead of `messages=...` to count output tokens. See [[tokens-and-tokenization]] for why per-model counting matters.

## Sample code

Lab-sourced (Day 1 · Session 1 — `labs/Day1 Session 1 - Foundations of Reliable AI Agents.ipynb`):

```python
import litellm

response = litellm.completion(
    model="groq/llama-3.1-8b-instant",
    messages=[
        {"role": "system", "content": "You are a concise support assistant."},
        {"role": "user", "content": "Where's my order #48213?"},
    ],
    temperature=0.2,
    max_tokens=200,
)
reply = response.choices[0].message.content

# thin wrapper — same function, unmodified across models
def litellm_chat(model: str, user_input: str) -> str:
    response = litellm.completion(
        model=model,
        messages=[{"role": "system", "content": "..."}, {"role": "user", "content": user_input}],
    )
    return response.choices[0].message.content

# cost/latency/token comparison across models
import time
comparison = []
for m in ["groq/llama-3.1-8b-instant", "gpt-4o-mini"]:
    start = time.time()
    reply = litellm_chat(m, "Summarize our return policy in one sentence.")
    latency = time.time() - start
    input_tokens = litellm.token_counter(model=m, messages=[{"role": "user", "content": "..."}])
    output_tokens = litellm.token_counter(model=m, text=reply)
    comparison.append({"model": m, "latency_sec": latency, "input_tokens": input_tokens, "output_tokens": output_tokens})
```

Reasoning-capable models (e.g. `groq/openai/gpt-oss-120b` with `reasoning_effort="low"`) return a separate scratch-work field — `resp.choices[0].message.reasoning` — alongside `.content`. The field name isn't standardized across providers; inspect `message.model_dump()` rather than assuming the name.

## Alternatives

| Approach | Where it lives | Boring/simple alternative to LiteLLM? |
|---|---|---|
| `litellm.completion()` | Standalone `litellm` package | — |
| Provider SDKs directly, per-provider | `openai`, `anthropic`, `google-genai`, etc. | **Yes** — the boring option; see [[raw-llm-clients]]. Full control, no abstraction bugs to debug, but every provider swap is a rewrite |
| LangChain chat model wrappers (`ChatOpenAI`, `ChatGroq`) | LangChain ecosystem | No — same abstraction tier, tied to LangChain's broader runnable/chain machinery ([[langchain-runnables-lcel]]) rather than a standalone call |
| OpenRouter | Hosted gateway, OpenAI-compatible single endpoint | No — a hosted service rather than a library; widest model catalog with least setup, but adds a credit markup and a third-party hop[^gateway-2026] |
| PydanticAI | Agent framework with built-in model-agnostic calling | No — a heavier framework (agents, tools, typed outputs) that happens to include multi-provider calling, not a drop-in `completion()` replacement |

## How this shows up in the capstone

Milestone 1 (provider-agnostic LLM client + structured intake) — `litellm.completion()` is the call every later agent in ShopSense makes; see [[capstone-milestone-map]].

## Interview fire round

- **Q: What does `finish_reason="length"` tell you that `finish_reason="stop"` doesn't?**
  A: The model hit `max_tokens` and was cut off mid-generation — the response is truncated, not a complete answer the model chose to stop at.
- **Q: Is `temperature=0` guaranteed to return the same output every time?**
  A: No — it's near-deterministic in practice, not a guarantee. Same for `seed`: providers make a "best effort," not a hard promise.
- **Q: Why does `litellm.token_counter` take a `model=` argument instead of using one global token-to-character ratio?**
  A: Different providers/models tokenize the same string into different counts — see [[tokens-and-tokenization]] — so a fixed ratio would misreport cost/context usage per model.

## Production gotchas & best practices

- Lab gotcha: JSON mode (`response_format={"type": "json_object"}`) requires the literal word "json" to appear somewhere in the messages, or Groq/OpenAI return a 400 — even when JSON is obviously implied by the schema you're asking for.
- Lab gotcha: the reasoning-trace field name varies by provider (`.reasoning`, or nested differently) — check `message.model_dump()` rather than hardcoding a field name.
- Production practice (from `labs/production-notes.md`): match provider tool-call/error text by substring, not exception class — exception classes for the same failure aren't standardized across providers routed through LiteLLM.
- Production practice (from `labs/production-notes.md`): LiteLLM's first import carries a real cost (~11s in one observed case) — pay it once at process startup (eager warm-up in a FastAPI `lifespan` hook, for instance), not lazily inside the first customer-facing call, where it shows up as unattributed latency on whichever request happens to trigger it.

## Course vs. production

The lab calls `litellm.completion()` synchronously, one call at a time, timing each manually for the cost/latency comparison table. In production, the same call is usually wrapped with retry/circuit-breaker logic ([[retry-fallback-patterns]], [[circuit-breaker-pattern]]) and instrumented for tracing ([[langfuse-tracing]]) from the first call onward — cost/latency isn't a one-off comparison, it's continuously observed.

## Related
- **Builds on** — [[raw-llm-clients]], [[tokens-and-tokenization]]
- **Feeds into** — [[litellm-as-gateway]], [[structured-output-repair-loops]], [[streaming-responses]]

## Sources

**Lab sources**
- `lab-summaries/Day1-Session1-Foundations.md` (§ "`completion()` knobs")
- `labs/Day1 Session 1 - Foundations of Reliable AI Agents.ipynb`

**Web sources**
- [LiteLLM — Input Params for `completion()`](https://docs.litellm.ai/docs/completion/input) — full parameter reference, accessed 2026-08-20
- [LiteLLM — Groq provider docs](https://docs.litellm.ai/docs/providers/groq) — `model="groq/<name>"` prefix format, accessed 2026-08-20
- [LiteLLM — Track Token & Response Usage](https://docs.litellm.ai/docs/completion/token_usage) — `token_counter` signature, accessed 2026-08-20

[^gateway-2026]: layer3labs.io 2026 gateway comparison — OpenRouter vs self-hosted LiteLLM tradeoffs.
