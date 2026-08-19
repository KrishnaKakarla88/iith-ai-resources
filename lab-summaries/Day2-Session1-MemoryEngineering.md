# Day 2 · Session 1 — Memory Engineering

Source: `labs/Day2 Session 1 - Memory Engineering.ipynb`

Two labs, tied to **Milestone 3 — persistent memory**. Stack: Gemini via LiteLLM (`LLM_MODEL = "gemini/gemini-flash-latest"`), Supermemory for long-term storage (`SUPERMEMORY_API_KEY`), `USER_ID` = a container tag namespacing one user's memories (multi-tenant isolation).

## Lab A — Four Kinds of Memory (CoALA taxonomy)

| Kind | Question it answers | Example |
|---|---|---|
| Working | What's in front of me right now? | current conversation buffer / context window |
| Episodic | What happened, and when? | "On 1 Aug the user booked flight AI-302" |
| Semantic | What is stably true? | "The user prefers aisle seats" |
| Procedural | How do I do this task? | "To book travel: check budget freeze, use corporate vendor…" |

A plain chat history is only **episodic**. The other three are built deliberately.

- **Working memory** — just an in-memory list of turns; transient. Token count via `tiktoken.get_encoding("cl100k_base").encode(text)`, falling back to `len(text)//4` if tiktoken unavailable.
- **Writing long-term memory** — `mem.add(content=text, container_tag=USER_ID, metadata={"type": kind, **extra})`. Supermemory indexes **asynchronously**, so poll (`for _ in range(20): ... time.sleep(3)`) rather than a fixed sleep, until the memory becomes searchable.
- **`recall(query, k=3)`** — semantic search helper: query `client.search.memories(q=query, container_tag=USER_ID, limit=k)` first (returns readable `.memory` text, singular `container_tag`); fall back to `client.search.documents(q=query, container_tags=[USER_ID], limit=k)` (text lives in `.chunks`, plural `container_tags`) only if the first returns nothing.
- **Episodic recall** — asked in different words than stored; semantic search still finds it (e.g. query "what flight did I book" finds a memory that never says "flight" the same way).
- **Semantic recall** — stable facts/preferences. Note: Supermemory can distill memories into a queryable profile via `mem.profile(container_tag=USER_ID, include=["static"])` once background extraction has run.
- **Procedural recall** — stores reusable *steps*, not raw transcripts, so a similar future task recalls the procedure.

## Lab B — When Memory Runs Out (context compression)

**Core idea:** context window is bounded; resending everything gets slow/costly and models get "lost" in very long context ("context rot"). Fix: keep recent turns verbatim, compress older turns into a rolling summary. **Summarization is lossy — test that the important fact survived, don't assume it.**

```python
RECENT_KEEP = 4      # turns kept verbatim
TOKEN_BUDGET = 220    # summarize once buffer exceeds this many tokens

def summarize_turns(turns, prev_summary=""):
    # builds a system prompt instructing: preserve concrete facts (names, numbers, preferences),
    # merges with prev_summary so earlier facts aren't dropped on repeated compressions,
    # calls litellm.completion(model=LLM_MODEL, temperature=0, messages=[...])
    # returns the updated summary text (<100 words)
```

**Self-check pattern (the actual lesson):** plant a fact in turn 1 ("pet parrot named Kiwi"), bury it under enough padding turns to exceed `TOKEN_BUDGET`, compress everything except the last `RECENT_KEEP` turns via `summarize_turns`, then `assert "kiwi" in summary.lower()` — proving the planted fact survived lossy compression rather than trusting it did.

## Gotchas
- Supermemory writes are async — always poll for searchability, don't assume `add()` is immediately queryable.
- `search.memories` (singular tag) vs `search.documents` (plural tags) have different response shapes (`.memory` vs `.chunks`) — the notebook's `recall()` handles both.
- Summarization is inherently lossy; always test recall of a known fact after compression, never assume the summary is faithful.

**Capstone tie-in:** Milestone 3 — persistent memory. Maps directly to the assistant's memory layer: what it holds in the moment (working), what it summarizes (compression), what it writes down to remember the user next time (episodic/semantic/procedural via Supermemory).
