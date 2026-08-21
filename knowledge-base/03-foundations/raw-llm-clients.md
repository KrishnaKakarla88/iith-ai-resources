---
stage: "03-foundations"
tools: [groq-sdk, openai-sdk]
tags: [llm-client, statelessness, messages]
last_verified: 2026-08-20
verified_against: "groq python SDK, openai python SDK (OpenAI-compatible base_url)"
---

# Raw LLM clients

Calling a provider's SDK directly, before any gateway abstraction sits in front of it — the baseline every later abstraction ([[litellm-basics]]) is judged against.

## Prerequisites
- [[what-is-an-llm]]
- [[env-secrets-and-config]]

## In plain English

Before reaching for a provider-agnostic wrapper, it's worth calling a provider directly at least once, because it exposes the fact every wrapper is built to hide: **an LLM API call is stateless**. The model has no memory of any call before it — not the previous message in "this conversation," not the fact you called it a minute ago. What looks like a chatbot remembering your name from three turns back is your application resending the entire conversation, from message one, on every single call. Nothing about the model persists between requests; the illusion of memory lives entirely in the growing list your code maintains and resends.

Groq ships its own Python SDK, but it also exposes an **OpenAI-compatible endpoint** — meaning you can point the standard `openai` Python package at Groq's base URL and it works unmodified, because Groq's API mimics OpenAI's request/response shape. Calling both ways back to back makes the point concrete: the `messages` list, the response shape, and the code around it are identical either way. The only thing that changes is which client object you instantiate and which `base_url` it points at — which is exactly the seam [[litellm-as-gateway]] later automates away.

## Core mechanics

| Concept | What it is |
|---|---|
| `messages` list | Ordered list of `{"role": ..., "content": ...}` dicts — `system` (standing instructions), `user`, `assistant` |
| `client.chat.completions.create(...)` | The call shape both the Groq SDK and OpenAI SDK share |
| `response.choices[0].message.content` | Where the reply text lives in the response object |
| `base_url` | What makes the OpenAI SDK talk to Groq instead of OpenAI — Groq mirrors the OpenAI request/response contract |
| Session store | An app-level dict mapping `session_id -> messages list`, so concurrent users' histories don't cross-talk |

## Sample code

Lab-sourced (Day 1 · Session 1 — `labs/Day1 Session 1 - Foundations of Reliable AI Agents.ipynb`). Same request, two clients:

```python
# Groq SDK directly
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{"role": "user", "content": "Hello"}],
)
reply = response.choices[0].message.content
```

```python
# OpenAI SDK, pointed at Groq's OpenAI-compatible endpoint — same shape
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)
response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{"role": "user", "content": "Hello"}],
)
reply = response.choices[0].message.content  # identical extraction
```

Conversation history — the "memory" is just the list being resent:

```python
def bare_chat(user_input: str, messages: list[dict]) -> str:
    messages.append({"role": "user", "content": user_input})
    response = client.chat.completions.create(model="llama-3.1-8b-instant", messages=messages)
    reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": reply})
    return reply

class SessionStore:
    def __init__(self):
        self._sessions: dict[str, list[dict]] = {}

    def get_or_create(self, session_id: str) -> list[dict]:
        if session_id not in self._sessions:
            self._sessions[session_id] = [{"role": "system", "content": "You are support for Acme."}]
        return self._sessions[session_id]

    def chat(self, session_id: str, user_input: str) -> str:
        return bare_chat(user_input, self.get_or_create(session_id))
```

`SessionStore` exists because a single shared `messages` list across concurrent users would leak one customer's conversation into another's — each `session_id` needs its own isolated history.

## Alternatives

| Approach | Where it lives | Boring/simple alternative? |
|---|---|---|
| Groq SDK directly | `groq` PyPI package | — |
| OpenAI SDK against Groq's `base_url` | `openai` PyPI package | Same tier — proves API-compatibility, not really "simpler" |
| `litellm.completion()` | See [[litellm-basics]] | No — one layer up, trades a bit of directness for provider-agnostic code |
| `requests`/`httpx` raw HTTP calls against the provider's REST API | Standard library / any HTTP client | **Yes** — the boring option; works, but you reimplement retry/auth/response-parsing that the SDK already gives you for free |

## How this shows up in the capstone

Milestone 1 (provider-agnostic LLM client + structured intake) starts here — the raw client is what proves the messages-list-as-memory pattern before it gets wrapped in [[litellm-basics]]; see [[capstone-milestone-map]].

## Interview fire round

- **Q: If you call the same LLM API twice with the identical `messages` list, does the second call "know" about the first?**
  A: No — each call is completely stateless. Any apparent continuity comes entirely from your application resending the growing message history, not from anything the model retains.
- **Q: Why does pointing the OpenAI SDK at Groq's `base_url` work at all?**
  A: Groq exposes an OpenAI-compatible endpoint — same request/response JSON shape as OpenAI's API — so any client built against that contract works against Groq unmodified.

## Production gotchas & best practices

- Lab gotcha: a shared `messages` list across users is a real bug, not a hypothetical — `SessionStore` scoped per `session_id` exists specifically to prevent concurrent-user cross-talk.
- Production practice (from `labs/production-notes.md`): scope thread/session identity to the unit of work, not loosely to "the session" — reusing one identity across turns/tenants can leak state that should have been isolated; the same principle `SessionStore` demonstrates here recurs at every later memory layer.
- Production practice: never guess a user's identity from message text — identity should come from an authenticated session key, not something parsed out of the conversation.

## Course vs. production

The lab calls two SDKs directly to make the statelessness/compatibility point concrete once. In production, no code should be maintained twice per provider — the moment you need to support more than one model or provider, the direct-SDK pattern shown here gets replaced by a single abstraction layer ([[litellm-basics]], [[litellm-as-gateway]]) so provider swaps are a one-line `model=` change, not a rewrite.

## Related
- **Builds on** — [[env-secrets-and-config]]
- **Feeds into** — [[litellm-basics]], [[litellm-as-gateway]]
- **Contrasts with** — [[litellm-as-gateway]] (same call, one layer of abstraction removed)

## Sources

**Lab sources**
- `lab-summaries/Day1-Session1-Foundations.md` (§ "Part 1 — Raw LLM Client + LiteLLM Comparison")
- `labs/Day1 Session 1 - Foundations of Reliable AI Agents.ipynb`

**Web sources**
- [Groq API docs — OpenAI compatibility](https://console.groq.com/docs/openai) — `base_url` pattern for the OpenAI SDK, accessed 2026-08-20
