---
stage: "00-ai-and-llm-basics"
tags: [primer, context-engineering, context-window]
last_verified: 2026-08-21
---

# Context engineering

Context engineering is the discipline of deciding *everything* that earns a seat in the context window on a given call — system prompt, retrieved chunks, memory, tool results, and history — and it's the umbrella prompt engineering now sits inside, not a replacement for it.

## Prerequisites
- [[context-windows-and-limits]]
- [[prompting-basics]]

## In plain English

Early on, "getting good output from an LLM" mostly meant wording the instruction well: a carefully written system prompt, phrased once, applied to every call. That's still necessary, but it stopped being sufficient once real systems started adding retrieved documents, tool results, and conversation history into every request. The wording of the instruction is now just one ingredient in a much bigger decision: on *this specific call*, what actually goes into the window?

Compare the same task handled two ways. A prompt-engineering-only approach writes one long, carefully worded static instruction and sends it unchanged every time. A context-engineered approach sends a short system prompt plus whatever's actually relevant right now — a freshly retrieved fact ("order #48213 — shipped 2 days ago"), the last couple of turns of history (not the whole transcript), and the latest tool result. The wording in both cases might be fine; the difference is that the second one makes a fresh decision, every call, about what data actually belongs in the window. That decision — not the wording — is context engineering.

This reframes prompt engineering as "one room in a bigger house": the instruction's wording is still one lever, but system prompt + history + retrieved facts + tool output + memory now all have to be actively curated together, every call, to fit inside a fixed budget of tokens.

## Core mechanics

There's no single API for this — it's a design discipline applied across a request, not a library call. The mechanism is a per-call curation decision over these inputs:

| What competes for the window | Question context engineering asks about it |
|---|---|
| System prompt | Is this the minimum standing instruction needed, or bloated with things that belong in a schema/tool description instead? |
| Conversation history | How much of it is still relevant to *this* turn — all of it, the last N turns, or a compressed summary (see [[context-compression]])? |
| Retrieved content (RAG) | Which chunks are actually relevant to this query, and how many can the budget afford (see [[hybrid-retrieval-rrf]], [[reranking]])? |
| Memory | What's durably known about this user/session that should be pulled in now, versus left in long-term storage (see [[memory-types]], [[supermemory]])? |
| Tool/function results | Does the raw tool output need to be included verbatim, or summarized before it re-enters context? |
| Reserved output space | How many tokens are set aside for the model's reply, so the input budget doesn't crowd it out (see [[context-windows-and-limits]])? |

A useful reference table (per course material) tracks, for each item above, two separate questions: does it use context window *now*, and does it become future context (i.e. does it get resent on the next turn)? A tool result, for instance, uses the window immediately and often *does* become future context if left in history — which is exactly why compression and pruning exist.

## Sample code

There's no single lab cell that "does" context engineering — it's the design decision behind several things this course builds separately: the `SessionStore`/messages-list pattern from Milestone 1 (deciding what stays in history), the retrieval pipeline in stage 06 (deciding what gets pulled in from outside), and the memory layer in stage 05 (deciding what persists across sessions). The clearest illustration is the contrast itself:

```python
# Prompt-engineering-only: one long, static instruction, no real data
messages = [
    {"role": "system", "content": (
        "You are a helpful, professional support assistant. Answer clearly, "
        "politely, using good judgement and considering all relevant company "
        "policies, in the style of a senior support agent..."
    )},
    {"role": "user", "content": user_input},
]

# Context-engineered: short instruction + curated, fresh data
messages = [
    {"role": "system", "content": "Acme Shipping support. Be concise."},
    {"role": "user", "content": f"Order fact: {retrieved_order_status}"},
    *last_n_turns,                      # trimmed history, not the whole transcript
    {"role": "user", "content": user_input},
]
```

The second version isn't "better wording" — it's a decision, remade every call, about what data earns a seat.

## How this shows up in the capstone

Every agent in the ShopSense build (Triage, Policy RAG, Order-Actions, Escalation Reviewer) makes its own context-engineering decision per call — which retrieved policy chunks, which customer memory, which prior turns actually belong in that agent's prompt — rather than one static system prompt reused everywhere; see [[capstone-milestone-map]].

## Interview fire round

- **Q: How is context engineering different from prompt engineering?**
  A: Prompt engineering is about wording a single instruction well. Context engineering is the broader, per-call decision about everything that enters the window — history, retrieved facts, tool results, memory — of which the instruction's wording is only one part.
- **Q: Why can two calls with an identically-worded system prompt still produce very different quality of answers?**
  A: Because the rest of the window — what history, retrieved content, and memory got included — differs call to call. Good wording on a bad selection of context still produces a bad answer.

## Production gotchas & best practices

- Per course material (`presentations/day1.md`, Act 2): "prompt engineer" as a distinct job title faded as the discipline widened into context engineering — the wording lever didn't disappear, it just stopped being the whole job.
- Production practice: track, for each candidate item, both whether it consumes window *now* and whether it re-enters as future context (e.g. via history) — an item that's cheap once but silently persists across every subsequent turn is a different cost than one used and discarded.
- Production practice: context curation should be driven by retrieval/eval quality (see [[retrieval-eval-metrics]]), not by "include everything that might be relevant" — over-inclusion has the same failure mode covered in [[context-rot-and-long-context-management]].

## Course vs. production

The lab's Milestone 1 client mostly resends full history verbatim, since its conversations are short. Production systems actively curate what enters each call — trimming history, ranking retrieved chunks, deciding what memory to surface — because at real conversation lengths, unmanaged context is both a cost problem (every resent token is billed) and a quality problem, not just a latency one.

## Related
- **Builds on** — [[context-windows-and-limits]], [[prompting-basics]]
- **Feeds into** — [[context-compression]], [[hybrid-retrieval-rrf]], [[memory-types]]
- **Contrasts with** — [[prompt-engineering-techniques]] (wording craft, a subset of this discipline)

## Sources

**Lab sources**
- `lab-summaries/Day1-Session1-Foundations.md` (§ "Instructions & Input", § "Prompt templating")

**Course material**
- `presentations/day1.md` (Session 1, Act 2, Question 3 — "Prompting Became One Room in a Bigger House"; the context-window composition table)

**Web sources**
- [ByteByteGo — A Guide to Context Engineering for LLMs](https://blog.bytebytego.com/p/a-guide-to-context-engineering-for) — cited in course material as connecting statelessness to the context-engineering discipline, accessed 2026-08-21
- [Anthropic — Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — framing of context engineering as curation of the full window contents, not just prompt wording, accessed 2026-08-21
