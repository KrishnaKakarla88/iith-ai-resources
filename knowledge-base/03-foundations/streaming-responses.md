---
stage: "03-foundations"
tools: [litellm]
tags: [streaming, latency, sse]
last_verified: 2026-08-20
verified_against: "litellm>=1.96.2"
---

# Streaming responses

`stream=True` returns a response token-by-token as it's generated, instead of waiting for the whole reply — the difference between a user staring at a blank screen and watching an answer appear in real time.

## Prerequisites
- [[litellm-basics]]

## In plain English

By default, `completion()` blocks until the model has finished generating the *entire* response, then hands it all back at once. For a short reply that's fine; for a 300-token answer, the user waits for the slowest part of the whole generation before seeing anything. `stream=True` changes the shape of the call: instead of one response object, you get an iterable of small **chunks**, each carrying a fragment of the growing answer, delivered as soon as the model produces it. Your code prints (or forwards to a client) each fragment as it arrives.

This doesn't make the model faster — total generation time is roughly the same either way. What it changes is **perceived** latency: time-to-first-token (how long before *anything* shows up) is what a user actually feels, and it's dramatically shorter than time-to-last-token. This is exactly the mechanism behind the typewriter effect in ChatGPT, Claude, and every modern chat UI — and it's the same primitive a FastAPI endpoint needs to stream tokens to a browser later in this stack (stage 09, [[fastapi-fundamentals]]).

## Core mechanics

| Concept | What it is |
|---|---|
| `stream=True` | Passed to `litellm.completion()` — returns an iterable of chunks instead of one response |
| Chunk | Each item has `chunk.choices[0].delta.content` — the incremental text for that piece, `""`/`None` when there's nothing new (e.g. metadata-only chunks) |
| Sync iteration | `for chunk in response: ...` |
| Async iteration | `async for chunk in response: ...` — response implements `__anext__` |
| `stream_chunk_builder()` | LiteLLM helper to reassemble the full response from a collected list of chunks, when you need the complete text after streaming finished |
| Time-to-first-token (TTFT) | What streaming actually improves — not total generation time |

## Sample code

Adapted from LiteLLM's streaming docs (pattern matches the lab's `completion()` knob list, which flags `stream` alongside `temperature`/`max_tokens`):

```python
import litellm

response = litellm.completion(
    model="groq/llama-3.1-8b-instant",
    messages=[{"role": "user", "content": "Explain context windows in two sentences."}],
    stream=True,
)

full_reply = ""
for chunk in response:
    piece = chunk.choices[0].delta.content or ""
    print(piece, end="", flush=True)
    full_reply += piece
```

Reassembling the full response object when you need both streaming *and* the final structured result:

```python
from litellm import stream_chunk_builder

chunks = list(litellm.completion(model="groq/llama-3.1-8b-instant", messages=[...], stream=True))
complete_response = stream_chunk_builder(chunks)
```

What this sets up for later — a FastAPI Server-Sent Events endpoint (stage 09) forwards each chunk to the browser as it arrives, rather than the client polling or waiting:

```python
# preview only — full pattern lives in fastapi-fundamentals
from fastapi.responses import StreamingResponse

async def stream_reply(user_input: str):
    response = litellm.completion(model="groq/llama-3.1-8b-instant",
                                    messages=[{"role": "user", "content": user_input}], stream=True)
    for chunk in response:
        piece = chunk.choices[0].delta.content or ""
        if piece:
            yield f"data: {piece}\n\n"

# return StreamingResponse(stream_reply(user_input), media_type="text/event-stream")
```

## Alternatives

| Approach | Where it lives | Boring/simple alternative to streaming? |
|---|---|---|
| `stream=True` + SSE (`text/event-stream`) | Provider/LiteLLM native support + FastAPI `StreamingResponse` | — |
| WebSockets | Bidirectional persistent connection | No — heavier setup than SSE for a one-directional token stream; worth it only if the client also needs to push data mid-stream (e.g. interrupt/cancel) |
| Long-polling | Client re-requests on an interval | No — strictly worse UX and more request overhead than either SSE or WebSockets for this use case |
| Non-streaming, block until complete | Default `completion()` behavior | **Yes** — the boring option; simplest code, fine for backend-to-backend calls or short replies where perceived latency doesn't matter |

## How this shows up in the capstone

Sets up the FastAPI streaming endpoint built in stage 09 ([[fastapi-fundamentals]]) — the same `stream=True` chunk-forwarding pattern shown here is what a ShopSense chat endpoint uses to stream agent replies to a client in real time; not itself one of Milestones 1-8 but the mechanism they eventually expose over HTTP.

## Interview fire round

- **Q: Does streaming make the model generate a response faster overall?**
  A: No — total generation time is roughly unchanged. What improves is time-to-first-token, which is what a user actually perceives as "fast."
- **Q: What's in a streamed chunk, and how do you know when there's nothing new in it?**
  A: `chunk.choices[0].delta.content` holds the incremental text fragment; it can be empty or `None` for metadata-only chunks (e.g. the final chunk carrying `finish_reason`), so guard with `or ""` before appending.

## Production gotchas & best practices

- Production practice (web-verified): for a browser-facing streaming endpoint, prefer Server-Sent Events over raw chunked HTTP — SSE gives built-in reconnection and a clean client-side `EventSource` API, and disable reverse-proxy buffering explicitly (`X-Accel-Buffering: no`, `Cache-Control: no-cache`) or an intermediary proxy can quietly re-batch your stream back into one blocking response.[^sse-2026]
- Production practice: when streaming and also needing the complete final text (for logging, validation, or a repair loop — [[structured-output-repair-loops]]), accumulate chunks and use `stream_chunk_builder()` (or your own accumulator) rather than making a second, non-streaming call for the same content.
- Production gotcha (adjacent, from `labs/production-notes.md`'s tracing notes): a generation span isn't useful without the actual input/output text and an explicit cost computation — for a streamed call, that means capturing the full accumulated text at the end of the stream for tracing, not just token counts.

## Course vs. production

The lab introduces `stream=True` as one line-item among `completion()`'s knobs, without wiring it into a real client. In production, streaming is rarely optional for a user-facing chat interface — it's the default expectation, and the FastAPI SSE endpoint built in stage 09 is where this stage's `stream=True` call becomes something a browser actually consumes.

## Related
- **Builds on** — [[litellm-basics]]
- **Feeds into** — [[fastapi-fundamentals]]
- **Related** — [[structured-output-repair-loops]] (streaming + validation interact once you need both)

## Sources

**Lab sources**
- `lab-summaries/Day1-Session1-Foundations.md` (§ "`completion()` knobs" — `stream` listed alongside other generation params)

**Web sources**
- [LiteLLM — Streaming Responses](https://docs.litellm.ai/docs/completion/stream) — chunk shape, `stream_chunk_builder`, accessed 2026-08-20
- [FastAPI Server-Sent Events for LLM Streaming: Smooth Tokens, Low Latency](https://medium.com/@2nick2patel2/fastapi-server-sent-events-for-llm-streaming-smooth-tokens-low-latency-1b211c94cff5) — SSE vs raw StreamingResponse, proxy-buffering gotcha, accessed 2026-08-20

[^sse-2026]: medium.com/@2nick2patel2 — 2026 FastAPI SSE streaming guide, buffering-disable headers.
