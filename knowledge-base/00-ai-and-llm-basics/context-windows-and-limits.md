---
stage: "00-ai-and-llm-basics"
tools: [litellm]
tags: [primer, context-window, tokens]
last_verified: 2026-08-21
verified_against: "litellm 1.96.x (this repo's pin)"
---

# Context windows and limits

The context window is the fixed number of tokens an LLM call can see at once — system prompt, conversation history, retrieved text and tool output all compete for the same fixed budget, and once it's full, something has to give.

## Prerequisites
- [[tokens-and-tokenization]]
- [[how-llms-generate-text]]

## In plain English

An LLM call is stateless — nothing about a prior call persists on the model's side. So "conversation" is an illusion your application maintains by resending the entire message history, from the very first turn, on every single call. That history, plus the system prompt, plus whatever tool results or retrieved documents got added, plus room reserved for the reply, all has to fit inside one number: the model's context window, measured in tokens.

Think of it as a room with a fixed number of chairs. Every turn adds more chairs' worth of content — but the room itself doesn't grow. A 2-turn conversation might use a few hundred tokens; by turn 50, with tool results and history piling up, the same conversation can be tens of thousands of tokens before the model even sees the new question. Two things scale with that growth: cost (every input token is billed, every turn, including all the history resent from before) and latency (more tokens in means more to process before the first output token appears).

A bigger window (some current models advertise context windows past a million tokens) doesn't remove this problem, it just moves the wall further away. The room is still a fixed size — a fatter binder just delays the day it stops closing, it doesn't remove that day. And even well inside the limit, stuffing the window full has its own cost, covered separately in [[context-rot-and-long-context-management]].

## Core mechanics

| Concept | What it means |
|---|---|
| Context window | The maximum number of tokens (input + reserved output) one API call can process — a hard ceiling set by the model, not a soft guideline |
| What competes for it | System prompt + conversation history + retrieved/tool content + the user's new input + tokens reserved for the model's reply |
| Hitting the ceiling | Depending on the API, either the call is rejected outright, or older content is silently truncated before the request is sent — neither is a "graceful" default |
| `max_tokens` | A cap you set on the *reply length*, not the input — hitting it mid-generation ends the response early with `finish_reason="length"` instead of `"stop"`, a common source of truncated JSON or a cut-off answer |
| Cost/latency scaling | `tokens/day = tokens-per-turn × turns-per-session × sessions-per-day`; cost follows the same multiplication against a per-token price — an untrimmed history compounds this on every single turn |

## Sample code

Lab-sourced (`labs/Day1 Session 1 - Foundations of Reliable AI Agents.ipynb`) — the gotcha that shows the ceiling isn't just theoretical: a capped reply silently gets cut off rather than erroring loudly.

```python
response = litellm.completion(
    model="groq/llama-3.1-8b-instant",
    messages=messages,
    max_tokens=50,   # too small for a full structured-output reply
)

reply = response.choices[0].message.content
finish_reason = response.choices[0].finish_reason  # "length", not "stop"
# reply is valid-looking text that just stops mid-sentence/mid-JSON —
# code that assumes finish_reason == "stop" will silently accept a truncated answer
```

Checking `finish_reason` before trusting a reply is the same discipline as validating structured output in [[structured-output-repair-loops]] — a response can look complete and not be.

## How this shows up in the capstone

Milestone 1's provider-agnostic client has to account for context-window limits per model (they differ across Groq/Gemini/etc.) when deciding how much history and retrieved content to send on each call — see [[capstone-milestone-map]].

## Interview fire round

- **Q: Does a 1M-token context window mean you never have to think about context limits again?**
  A: No — it moves the ceiling further away, it doesn't remove it. A big-enough conversation with tools and retrieved content still fills it, and (per [[context-rot-and-long-context-management]]) quality can degrade well before the hard limit is reached.
- **Q: Why does a 50-turn conversation cost noticeably more than a 2-turn one, given the same model?**
  A: Every turn resends the full history from turn 1 onward — there's no incremental "just the new part" billing. All of it is tokenized and billed again, every single call.

## Production gotchas & best practices

- Lab gotcha: a `max_tokens` set too low for the expected output silently truncates a reply — `finish_reason="length"` is the signal, and code that only checks for an exception will miss it.
- Production practice: budget the context window explicitly per call — reserve tokens for the expected reply length before deciding how much history/retrieved content to include, rather than discovering the ceiling via a truncated response in production.
- Production practice: different providers report and enforce context-window limits differently (some reject over-limit requests, others silently drop the oldest turns) — never assume one behavior across providers without checking that model's actual API docs.

## Course vs. production

The lab treats `max_tokens` mostly as a knob to demonstrate finish-reason behavior on a handful of calls. In production, context-window budgeting is a standing design decision — how much history to keep, how much retrieved content to allow, how much room to reserve for output — revisited continuously as conversations grow, not set once and forgotten. That budgeting problem is exactly what [[context-engineering]] and [[context-rot-and-long-context-management]] cover next.

## Related
- **Builds on** — [[tokens-and-tokenization]], [[how-llms-generate-text]]
- **Feeds into** — [[context-engineering]], [[context-rot-and-long-context-management]], [[model-selection-cost-latency-tradeoffs]]

## Sources

**Lab sources**
- `lab-summaries/Day1-Session1-Foundations.md` (§ "`completion()` knobs" — `max_tokens`, `finish_reason`)
- `labs/Day1 Session 1 - Foundations of Reliable AI Agents.ipynb`

**Course material**
- `presentations/day1.md` (Session 1, Act 2 — "What That Costs You": context window composition, the tokens/day cost formula, "a room with a fixed number of chairs")

**Web sources**
- [LiteLLM — Completion function docs](https://docs.litellm.ai/docs/completion/input) — `max_tokens`, `finish_reason` behavior across providers, accessed 2026-08-21
