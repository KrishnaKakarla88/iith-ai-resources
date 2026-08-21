---
stage: "05-memory"
tools: [supermemory, tiktoken]
tags: [memory, coala, taxonomy]
last_verified: 2026-08-20
verified_against: "labs/Day2 Session 1 - Memory Engineering.ipynb"
---

# Memory types

An agent needs four different kinds of memory — working, episodic, semantic, and procedural — because "remembering" isn't one problem: a plain chat history only covers one of the four.

## Prerequisites
- [[context-windows-and-limits]]
- [[tokens-and-tokenization]]

## In plain English

Ask a human receptionist what memory they're using at any given moment and you'd get different answers depending on what they're doing. Mid-checkin, they're tracking what you just said (working memory). They recall you complained about a noisy room last March (episodic — a specific, timestamped event). They know checkout is 11am regardless of who's asking (semantic — a durable fact, no story attached). And they run a card through the machine without consciously thinking through the steps (procedural — a learned skill).

An LLM-based agent has none of this by default. Between API calls, the model is stateless — it has no memory at all unless your application resends context or writes something down. The chat history you pass back in on every turn *is* a form of memory, but it's only one kind: **episodic**, and a crude version at that (a raw transcript, not a distilled "what happened"). The CoALA framework (Cognitive Architectures for Language Agents) names the other three kinds explicitly, precisely because "just keep resending the transcript" quietly assumes chat history is the only memory an agent needs — and it isn't.

The same sentence, "I'm allergic to peanuts," takes a different shape in each memory type: it sits in working memory only while the current turn is being processed; as episodic memory it becomes `{"date": "2026-03-03", "event": "user mentioned a peanut allergy while ordering item #4471"}`; as semantic memory it becomes `{"fact": "user has a peanut allergy", "confidence": "high"}` — no date, no story, just the fact; and as a procedural consequence it might become a standing rule: "always screen ingredient lists before recommending a recipe to this user." Four different shapes, one underlying fact, and only the first is free — the other three require someone (or something) to deliberately write them down.

## Core mechanics

| Memory kind | Question it answers | Lifespan | Where it lives in this stack |
|---|---|---|---|
| Working | What's in front of me right now? | One turn / one conversation, transient | An in-memory list of turns, held in the process, never persisted |
| Episodic | What happened, and when? | Durable, timestamped | Written to [[supermemory]] with `metadata={"type": "episodic", ...}` |
| Semantic | What is stably true? | Durable, no timestamp needed | Written to Supermemory as a distilled fact, or surfaced via a memory `profile()` call |
| Procedural | How do I do this task? | Durable | Written to Supermemory as reusable steps, not a raw transcript |

CoALA's own framing (per course material, `presentations/day2.md`, citing Sumers, Yao, Narasimhan & Griffiths' CoALA paper) splits agent memory into **working memory** (short-term) and **long-term memory** (subdivided into episodic, semantic, and procedural), and further separates *external* actions (the agent acting on the outside world — grounding) from *internal* actions (the agent acting on its own memory — retrieval, reasoning, and learning). Writing to long-term memory is a *learning* action; recalling from it is a *retrieval* action. Both are internal actions the agent takes deliberately, not something that happens automatically the way appending to a chat list does.

A useful discriminator when you're not sure which bucket something belongs in: **does it have a specific "when," or is it timeless?** "The user booked flight AI-302 on 1 Aug" has a when — episodic. "The user prefers aisle seats" doesn't need one — semantic. "To book travel: check the budget freeze, then use the corporate vendor" is neither a moment nor a static fact — it's a recipe — procedural.

## Sample code

Lab-sourced (Day 2 · Session 1 — `labs/Day2 Session 1 - Memory Engineering.ipynb`). Working memory is nothing more than a list and a token counter:

```python
import tiktoken

enc = tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    try:
        return len(enc.encode(text))
    except Exception:
        return len(text) // 4  # rough fallback if tiktoken is unavailable

working_memory = []  # list of {"role": ..., "content": ...} turns, transient
```

Writing the other three kinds means tagging *what kind* of memory this is at write time, via `metadata`, then querying it back with a semantic `recall()`:

```python
def remember(mem, text: str, kind: str, **extra):
    mem.add(content=text, container_tag=USER_ID, metadata={"type": kind, **extra})

# episodic — a specific, timestamped event
remember(mem, "On 1 Aug the user booked flight AI-302.", kind="episodic", date="2026-08-01")

# semantic — a durable preference, no date attached
remember(mem, "The user prefers aisle seats.", kind="semantic")

# procedural — reusable steps, not a raw transcript
remember(mem, "To book travel: check the budget freeze, then use the corporate vendor.", kind="procedural")
```

Note what does *not* change between the three: the same `mem.add()` call, the same `container_tag`. What distinguishes episodic/semantic/procedural memory in this stack is entirely the `metadata={"type": ...}` tag and what you chose to write down — Supermemory itself doesn't enforce the taxonomy. See [[supermemory]] for `recall()` and the full write/search API.

## How this shows up in the capstone

Milestone 3 — persistent memory + semantic index. The four memory types map directly onto ShopSense's memory layer: working memory is the live conversation buffer inside one agent turn, episodic/semantic/procedural memory are what gets written to Supermemory so a returning customer's agent remembers them across sessions. See [[capstone-milestone-map]].

## Interview fire round

- **Q: Why isn't a plain chat history "memory enough" for an agent?**
  A: A chat history is only episodic memory — a raw, undistilled transcript of what was said. It has no durable facts extracted (semantic), no reusable procedures (procedural), and it usually doesn't survive the session ending unless something deliberately persists it.
- **Q: How do you decide whether a fact belongs in episodic or semantic memory?**
  A: Ask whether it has a specific "when." "User booked flight AI-302 on 1 Aug" is a moment — episodic. "User prefers aisle seats" is timeless — semantic.

## Production gotchas & best practices

- Lab gotcha: a plain chat-history buffer is only episodic memory in disguise — building semantic/procedural memory takes a deliberate write step (`mem.add(..., metadata={"type": ...})`), it does not fall out of just keeping a longer conversation buffer.
- Lab gotcha: episodic recall has to work across paraphrase — the lab's test query ("what flight did I book") never uses the word "flight" the way the stored memory does, and semantic search still has to find it; this is a property of the *retrieval* mechanism (embeddings), not the memory type itself.
- Production practice: per course material (`presentations/day2.md`), 2026-era agents increasingly let the *model itself* decide what's worth writing to durable memory, rather than the application pre-deciding it — see [[supermemory]]'s "agent-managed memory" note and Anthropic's `memory_20250818` tool, which lets Claude read/write files under `/memories` via ordinary tool calls with no vector database required ([Anthropic — Memory tool docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool), accessed 2026-08-20).
- Production practice: uncurated long-term memory accumulates duplicates and stale facts over time (per course material, `presentations/day2.md`) — see [[context-compression]] for the consolidation ("Dreaming") pattern that addresses this.

## Course vs. production

The lab treats the four memory types as something the *application code* decides and tags explicitly at write time (`metadata={"type": "episodic"}`). Current production patterns (per course material, `presentations/day2.md`, and Anthropic's memory-tool docs) increasingly hand that judgment to the agent itself — the model decides in the moment what's worth persisting, instead of a fixed pre-classification scheme. The taxonomy stays the same either way; what changes is who decides which bucket a given fact lands in.

## Related
- **Feeds into** — [[supermemory]], [[context-compression]]
- **Builds on** — [[context-windows-and-limits]], [[tokens-and-tokenization]], [[context-engineering]] (memory is one input the broader context-engineering discipline has to decide about)

## Sources

**Lab sources**
- `lab-summaries/Day2-Session1-MemoryEngineering.md` (§ "Lab A — Four Kinds of Memory (CoALA taxonomy)")
- `labs/Day2 Session 1 - Memory Engineering.ipynb`

**Course material**
- `presentations/day2.md` — Act 1 ("What Memory Actually Is"), CoALA taxonomy framing, working/episodic/semantic/procedural examples, internal vs. external actions

**Web sources**
- [CoALA — Cognitive Architectures for Language Agents (arXiv 2309.02427)](https://arxiv.org/abs/2309.02427) — Sumers, Yao, Narasimhan, Griffiths — the canonical taxonomy source cited in `presentations/day2.md`, accessed 2026-08-20
- [Anthropic — Memory tool docs (memory_20250818)](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool) — agent-managed, file-based memory, no vector DB required, accessed 2026-08-20
