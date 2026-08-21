---
stage: "05-memory"
tools: [litellm]
tags: [memory, context-window, summarization, compression]
last_verified: 2026-08-20
verified_against: "labs/Day2 Session 1 - Memory Engineering.ipynb"
---

# Context compression

Context compression keeps a long-running conversation fitting inside the context window by summarizing older turns instead of endlessly resending the full transcript — and because summarization is lossy, the only way to trust it is to test that the fact you care about survived.

## Prerequisites
- [[context-windows-and-limits]]
- [[memory-types]]

## In plain English

The API is stateless: nothing about "the conversation" exists on the server between calls. Every turn, your application resends the entire history it wants the model to see. That works fine for turn 5. By turn 40, you're resending an afternoon's worth of messages before every reply — latency climbs (bigger prompt, more to process), cost climbs (billed per input token, every turn), and eventually you hit the context window's hard ceiling. Naive truncation — just deleting the oldest messages once you're full — "fixes" the ceiling but silently deletes information the user assumes you still know: drop the wrong five messages and the order number from turn 3 is just gone.

Context compression is the deliberate alternative: keep the most recent turns verbatim (they're most likely to be relevant to the current reply), and replace everything older than that with a running summary — a much shorter piece of text that tries to preserve the facts that matter (names, numbers, preferences, decisions) while discarding the exact wording. The catch is right there in "tries to preserve": summarization is an LLM call, and LLM calls are not reliable extractors. A summary that reads as complete prose can still have silently dropped the one detail — a peanut allergy, an urgent flag — that actually mattered. The only way to know a summary is trustworthy is to test it: plant a fact, compress past it, check the fact is still recoverable from the summary. Believing a summary is faithful because it *sounds* faithful is exactly the failure mode this technique exists to catch.

## Core mechanics

| Concept | What it means |
|---|---|
| Recent-keep window | The last N turns, kept verbatim, never summarized |
| Token budget | The threshold (measured in tokens, not turns/characters) that triggers a compression pass once the buffer exceeds it |
| Rolling summary | A short piece of text (tens of words, not paragraphs) representing everything older than the recent-keep window, regenerated and merged forward each time compression runs |
| Merge-with-previous | Each compression pass folds the new material into the *existing* summary, rather than starting fresh — so a fact from turn 3 isn't lost just because compression has already run twice since then |
| Self-check / recall test | Plant a known fact early, force compression to run past it, assert the fact is still present in the resulting summary |

Two failure modes this guards against, both named explicitly in course material (`presentations/day2.md`): **naive truncation** (silently dropping the oldest messages once the window is full — deletes information the user assumes you still know) and **unverified summarization** (trusting a summary that "sounds complete" without checking whether it actually preserved the load-bearing detail).

## Sample code

Lab-sourced (Day 2 · Session 1 — `labs/Day2 Session 1 - Memory Engineering.ipynb`):

```python
import litellm

RECENT_KEEP = 4       # turns kept verbatim, never summarized
TOKEN_BUDGET = 220     # summarize once the older-turns buffer exceeds this many tokens

def summarize_turns(turns, prev_summary=""):
    """
    Compresses everything except the last RECENT_KEEP turns into a short
    rolling summary, merged with any prior summary so earlier facts aren't
    dropped on repeated compressions.
    """
    system = (
        "Summarize the conversation so far in under 100 words. "
        "Preserve concrete facts: names, numbers, dates, preferences, decisions. "
        "Merge with the previous summary — do not drop anything it already captured."
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": f"Previous summary: {prev_summary}\n\nTurns to fold in: {turns}"},
    ]
    response = litellm.completion(model=LLM_MODEL, temperature=0, messages=messages)
    return response.choices[0].message.content

# --- the actual lesson: don't trust the summary, test it ---
turns = [
    {"role": "user", "content": "I have a pet parrot named Kiwi."},
    *padding_turns,  # enough filler to push the buffer past TOKEN_BUDGET
]
summary = summarize_turns(turns[:-RECENT_KEEP])
assert "kiwi" in summary.lower()  # proves the planted fact survived compression
```

`temperature=0` is deliberate here — a summarization prompt isn't a place you want creative variance; you want the most literal, deterministic compression of "what facts were stated," not a stylistically varied retelling.

## How this shows up in the capstone

Milestone 3 — persistent memory + semantic index. Context compression is Lab B of the memory session, and it's the mechanism that keeps a long ShopSense support conversation usable: recent turns stay verbatim for the agent's immediate reasoning, older turns collapse into a rolling summary, and anything durable enough to matter beyond the session gets promoted to [[supermemory]] instead of living only in the summary — see [[capstone-milestone-map]].

## Interview fire round

- **Q: Why is naive truncation (just dropping the oldest messages) worse than summarization?**
  A: Truncation is silent — it deletes information the user assumes you still know, with no trace that anything was lost. Summarization at least attempts to preserve the important facts in compressed form; the failure mode shifts from "definitely lost" to "possibly lost and you have to verify."
- **Q: How do you actually know a summary preserved what mattered?**
  A: You test it — plant a known fact, run compression past it, assert the fact is recoverable from the resulting summary. Never assume a summary is faithful just because it reads as complete.
- **Q: Why merge each new summary with the previous one instead of re-summarizing the whole history each time?**
  A: Re-summarizing from scratch every pass risks losing facts from early in the conversation that already fell out of the recent-keep window — merging forward means each pass only has to preserve what the *previous summary* already captured, not re-derive it from a transcript that's no longer fully available.

## Production gotchas & best practices

- Lab gotcha: summarization is inherently lossy — the notebook's core lesson is to test recall of a planted fact after compression rather than assume the summary is faithful; this is a testing discipline, not a one-time check.
- Lab gotcha: `TOKEN_BUDGET` and `RECENT_KEEP` are small, notebook-scale values (220 tokens, 4 turns) tuned for a short demo conversation — treat the *mechanism* as the takeaway, not these specific numbers.
- Production practice (from `labs/production-notes.md`, TA/logistics references stripped): keep a **raw, uncompressed fallback for exact identifiers** — LLM-compressed summaries reliably drop literal values like order references (an LLM asked to "summarize" tends to paraphrase numbers/IDs, not preserve them verbatim); try a raw recent-turns cache first for anything identifier-shaped, and fall back to the compressed summary only for softer context.
- Production practice: per course material (`presentations/day2.md`), the naive "just resend everything" approach doesn't only get slower — the model itself gets measurably worse at using very long, mostly-irrelevant context (see [[context-rot-and-long-context-management]]), so compression is a quality lever as much as a cost/latency one.
- Production practice: Anthropic's `memory_20250818` tool ships a related but distinct server-side mechanism called **compaction** — it summarizes the whole conversation automatically once it nears the context-window limit, and is designed to pair with file-based memory: compaction keeps active context small without client-side bookkeeping, while memory (see [[memory-types]]) preserves the specific facts that must survive summarization ([Anthropic — Context editing / compaction docs](https://platform.claude.com/docs/en/build-with-claude/compaction), accessed 2026-08-20).
- Production practice: MemGPT's "virtual context management" (per course material, `presentations/day2.md`, citing Packer et al., arXiv 2310.08560) frames this as an OS-style memory hierarchy — the context window plays the role of RAM (fast, scarce), while a recall store and an archival store play the role of disk; the agent explicitly moves data between tiers via function calls rather than the application silently truncating.

## Course vs. production

The lab implements compression as a single hand-rolled function (`summarize_turns`) called synchronously inside a notebook cell, with fixed small thresholds and a manual `assert` as the only verification. In production, per course material (`presentations/day2.md`), this becomes two related but separate concerns done more systematically: **session-scoped compression** (what this page covers — collapsing old turns into a rolling summary to stay under the context window for the *current* conversation) versus **long-term memory consolidation** (an offline batch job run *between* sessions, informally "Dreaming," that merges duplicate facts and prunes stale ones out of durable storage like [[supermemory]] — a different timescale and a different failure mode, clutter rather than context-window overflow). A single lab notebook only needs to demonstrate the first; a system running for months needs both.

## Related
- **Builds on** — [[context-windows-and-limits]], [[memory-types]]
- **Related** — [[context-rot-and-long-context-management]], [[supermemory]]

## Sources

**Lab sources**
- `lab-summaries/Day2-Session1-MemoryEngineering.md` (§ "Lab B — When Memory Runs Out (context compression)")
- `labs/Day2 Session 1 - Memory Engineering.ipynb`
- `labs/production-notes.md` (§ "Memory")

**Course material**
- `presentations/day2.md` — Act 2 ("When Memory Outgrows the Window"), session-vs-long-term memory, naive-truncation-vs-deliberate-compression framing, MemGPT/consolidation references

**Web sources**
- [MemGPT: Towards LLMs as Operating Systems (arXiv 2310.08560)](https://arxiv.org/abs/2310.08560) — Packer et al., virtual context management, recall/archival store framing, cited in `presentations/day2.md`, accessed 2026-08-20
- [Anthropic — Context editing / compaction docs](https://platform.claude.com/docs/en/build-with-claude/compaction) — server-side automatic compaction, pairing with file-based memory, accessed 2026-08-20
