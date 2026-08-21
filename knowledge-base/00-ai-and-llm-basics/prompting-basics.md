---
stage: "00-ai-and-llm-basics"
tools: [litellm, groq]
tags: [primer, prompting, roles, messages]
last_verified: 2026-08-21
verified_against: "litellm 1.96.x (this repo's pin)"
---

# Prompting basics

Every LLM call is built from a list of role-tagged messages — `system`, `user`, `assistant` — and whether you show the model zero examples or a few is the smallest structural decision you make; both quietly shape every answer that follows, before any "prompt engineering" technique enters the picture.

## Prerequisites
- [[how-llms-generate-text]]

## In plain English

A "conversation" with an LLM isn't a conversation from the model's point of view — it's a single input: a list of messages, each tagged with a role, sent fresh on every call (see [[what-is-an-llm]] — nothing persists between calls). What you put in that list, and how you tag it, is prompting.

Three roles do almost all the work:

- **`system`** — standing instructions that shape behavior for the whole exchange ("You are support for Acme Shipping. Be concise."). It's the cheapest lever available to reshape output — change the system message, not the code, and behavior changes.
- **`user`** — what the human (or your application, on the human's behalf) is asking right now.
- **`assistant`** — the model's own prior replies, replayed back to it as history so it can be consistent with what it "said" before.

A **session** is just this list, growing turn by turn, kept somewhere in your own application (see the `SessionStore` pattern below) — the model never stores it.

The other basic axis is **how many examples you show**: **zero-shot** prompting gives the model only an instruction and a task, with no worked examples, relying entirely on what it learned during training to infer the expected pattern. **Few-shot** prompting adds a small number of example input→output pairs directly in the prompt before the real task, so the model can pattern-match the shape and style of a good answer instead of inferring it from the instruction alone. Few-shot generally costs more tokens (the examples are sent, and billed, every call) but often improves reliability on tasks where "the right format" is easier to show than to describe.

## Core mechanics

| Concept | What it means |
|---|---|
| `messages` list | An ordered list of `{"role": ..., "content": ...}` dicts — the entire state of the exchange, resent in full on every call |
| `system` role | Standing behavior/persona instructions — set once, applies for the whole session |
| `user` / `assistant` roles | The human's turns and the model's own prior replies, alternating as history accumulates |
| Zero-shot | Instruction + task, no worked examples — relies on the model's training to infer the expected pattern |
| Few-shot | Instruction + a handful of example input→output pairs + the real task — trades extra tokens for a clearer pattern to match |
| Prompt template | A reusable string/structure with variable slots, rendered with different values per call instead of hand-building messages each time |

## Sample code

Lab-sourced (`labs/Day1 Session 1 - Foundations of Reliable AI Agents.ipynb`) — a session-scoped chat function and store, so concurrent users don't cross-talk:

```python
def bare_chat(user_input: str, messages: list[dict]) -> str:
    messages.append({"role": "user", "content": user_input})
    response = client.chat.completions.create(model=MODEL, messages=messages)
    reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": reply})
    return reply

class SessionStore:
    def __init__(self):
        self.sessions: dict[str, list[dict]] = {}

    def get_or_create(self, session_id: str) -> list[dict]:
        if session_id not in self.sessions:
            self.sessions[session_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
        return self.sessions[session_id]

    def chat(self, session_id: str, user_input: str) -> str:
        return bare_chat(user_input, self.get_or_create(session_id))
```

A minimal few-shot prompt, built as a `user` message with worked examples ahead of the real task:

```python
FEW_SHOT = """Classify the sentiment as positive, negative, or neutral.

Text: "Shipping was fast, loved it." -> positive
Text: "Item arrived broken." -> negative

Text: "{ticket_text}"""" -> """
```

## How this shows up in the capstone

Milestone 1's `SessionStore` pattern — one message list per `session_id` — is the exact mechanism that keeps concurrent Kartway customer conversations from bleeding into each other; see [[capstone-milestone-map]].

## Interview fire round

- **Q: If the model has no memory between calls, how does a chatbot seem to remember what you said earlier?**
  A: Your application resends the entire message history — system, user, and assistant turns — on every single call. The illusion of memory lives in your code's growing list, not in the model.
- **Q: When would you reach for few-shot over zero-shot?**
  A: When the expected output format or style is easier to demonstrate than to describe in words — a few worked examples often pin down a pattern more reliably than a longer written instruction, at the cost of extra tokens on every call.

## Production gotchas & best practices

- Lab gotcha: the message list is the *entire* state of a session — nothing about the model "remembers" a prior turn, so a bug that drops or truncates the history silently degrades every downstream reply, with no error to catch it.
- Production practice: keep `system` prompts under version control and treat wording changes as a reviewable diff, not a hotfix in a notebook cell — the system message is the cheapest, highest-leverage lever on behavior, which also makes an undocumented edit to it the easiest way to silently change production behavior.
- Production practice: few-shot examples consume real context-window budget on every call — as history grows over a long session, examples baked into the system prompt compete with retrieved context and conversation history for the same token budget (see [[context-windows-and-limits]]).

## Course vs. production

The lab's `SessionStore` is an in-memory dict, fine for a single notebook process. Production session storage needs to survive process restarts and scale across concurrent requests — typically a database or cache keyed by session/thread id, with the same "resend the whole list" mechanics underneath, which is exactly the gap [[memory-types]] and [[context-compression]] address later for longer-running conversations.

## Related
- **Builds on** — [[how-llms-generate-text]]
- **Feeds into** — [[prompt-engineering-techniques]], [[context-engineering]]
- **Related** — [[tool-calling-fundamentals]] (tool schemas are messages too, of a sort)

## Sources

**Lab sources**
- `lab-summaries/Day1-Session1-Foundations.md` (§ "Part 1 — Raw LLM Client + LiteLLM Comparison", points 2-4)
- `labs/Day1 Session 1 - Foundations of Reliable AI Agents.ipynb`

**Deck sources**
- `presentations/day1.md` (Session 1 · Act 1 · Question 3 — "The Array, Growing Turn by Turn"; Act 2 · Question 3 — "What are Prompts?")
