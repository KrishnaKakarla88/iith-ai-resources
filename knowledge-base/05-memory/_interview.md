# 05-memory — interview fire round

### memory-types

- **Q: Why isn't a plain chat history "memory enough" for an agent?**
  A: A chat history is only episodic memory — a raw, undistilled transcript of what was said. It has no durable facts extracted (semantic), no reusable procedures (procedural), and it usually doesn't survive the session ending unless something deliberately persists it.
- **Q: How do you decide whether a fact belongs in episodic or semantic memory?**
  A: Ask whether it has a specific "when." "User booked flight AI-302 on 1 Aug" is a moment — episodic. "User prefers aisle seats" is timeless — semantic.

### supermemory

- **Q: Why does `recall()` need to check two different response shapes?**
  A: Supermemory's memory search (`search.memories`) and document search (`search.documents`) return different field names (`.memory` vs `.chunks`) and take slightly different parameter shapes (singular vs plural `container_tag`) — a helper that assumes one shape silently misses hits from the other path.
- **Q: What isolates one customer's memories from another's in a multi-tenant deployment?**
  A: The `container_tag` on every read and write. It has to be applied at every call site — a single missed call site is a cross-customer data leak, not just a bug.
- **Q: Why can't you search for a memory immediately after writing it?**
  A: Supermemory indexes writes asynchronously. `add()` returns before indexing completes, so code needs to poll for searchability rather than assume it.

### context-compression

- **Q: Why is naive truncation (just dropping the oldest messages) worse than summarization?**
  A: Truncation is silent — it deletes information the user assumes you still know, with no trace that anything was lost. Summarization at least attempts to preserve the important facts in compressed form; the failure mode shifts from "definitely lost" to "possibly lost and you have to verify."
- **Q: How do you actually know a summary preserved what mattered?**
  A: You test it — plant a known fact, run compression past it, assert the fact is recoverable from the resulting summary. Never assume a summary is faithful just because it reads as complete.
- **Q: Why merge each new summary with the previous one instead of re-summarizing the whole history each time?**
  A: Re-summarizing from scratch every pass risks losing facts from early in the conversation that already fell out of the recent-keep window — merging forward means each pass only has to preserve what the *previous summary* already captured, not re-derive it from a transcript that's no longer fully available.

## Harder / real-interview-style

Grounded in 2026 web-researched interview material on agent memory architecture and production long-term-memory engineering, cross-checked against this stage's [[memory-types]], [[supermemory]], and [[context-compression]] pages. Sourcing note: search terms "LLM agent memory interview questions long-term memory context compression production" and "AI memory management for LLMs and agents"; general practice, not one single citable source per question.

### Memory architecture & design tradeoffs

- **Q: A customer-support agent correctly recalls a user's seat preference from three months ago, but a teammate complains it "feels dumb" because it re-asks basic questions within the same ticket. What's actually wrong, and is it a memory bug?**
  A: Almost certainly not a long-term-memory bug — it's a working-memory problem. The agent is retrieving semantic facts correctly across sessions but isn't carrying the current conversation's own episodic content (what was already said in *this* ticket) forward turn-to-turn, or it's re-running a recall query on every turn instead of trusting what's already in the live context window. The fix is distinguishing "what needs retrieval because it's outside the window" from "what's already in-context and shouldn't be re-fetched" — conflating the two either wastes a recall call or, worse, lets a stale retrieved fact silently override what the user just said this turn.

- **Q: Design the memory-write policy for a support agent: should every fact the user mentions get written to long-term memory automatically, or only some?**
  A: Auto-writing everything is the naive answer and it's wrong — it inflates storage and search-noise with low-value, one-off facts ("I'm annoyed today") and creates staleness risk for facts that change ("my current order is X"). The interview-strength answer separates facts by durability and reuse value: stable preferences and identity facts (semantic memory) are worth an automatic or lightly-gated write; specific one-off events (episodic) are worth writing only if they'll matter later (an escalation, a broken promise, a policy exception granted); and anything transient to the current task shouldn't be persisted past the session at all. The tell in a real interview is whether the candidate treats "write everything" as free — it isn't, both in retrieval precision and in privacy/retention exposure (see [[privacy-and-pii-handling]]).

- **Q: Two memories about the same user directly contradict each other — one from six months ago says "prefers aisle seat," a later one says "booked window seat twice in a row." How should retrieval or write-time logic resolve this?**
  A: Don't silently pick the newer one and don't silently average them — both are legitimate failure-prone strategies. The stronger design surfaces the conflict rather than hiding it: weight by recency and frequency (two recent window bookings outweigh one old stated preference) but keep the older fact rather than deleting it, since intent can be genuinely mixed (aisle for long-haul, window for short-haul). Some systems handle this with an explicit "supersedes" edge between memory entries rather than treating memory as one flat, only-additive fact store — the interview signal is recognizing that unresolved contradiction is a real production state, not something a naive "most recent write wins" resolves correctly.

### Supermemory & multi-tenant production concerns

- **Q: A test writes a fact via `add()` and immediately asserts it's recoverable via `search.memories()` in the next line — the test is flaky, sometimes passing, sometimes failing. Why, and what's the actual production risk if this isn't handled?**
  A: This is the asynchronous-indexing behavior [[supermemory]] already covers at the fire-round level, but the production risk is more specific than test flakiness: if an agent writes a fact and then, in the *same turn*, tries to use that fact by recalling it rather than keeping it in the active context, the recall can race the index and silently return nothing — the agent behaves as if the user never said it, in the same conversation where they just said it. The fix isn't "poll until indexed" in the hot path (too slow for a live turn); it's keeping the just-written fact available in working context for the rest of that turn and letting only *future* turns depend on the indexed, searchable copy.

- **Q: If `container_tag` is the entire tenant-isolation mechanism, what's the worst way a team could derive it, and why?**
  A: Deriving it from anything in the message text or an LLM-parsed field — e.g. trusting a "my customer ID is X" string the model extracted from the conversation — because that's attacker- or mistake-controlled input, not an authenticated identity. This is the same failure class covered in [[auth-and-multi-tenancy]]: identity, and therefore the tag that scopes every memory read/write, has to come from the authenticated session before the agent logic runs, never be inferred from what the user typed. A single call site that derives `container_tag` the wrong way is a cross-tenant memory leak, not a minor bug.

- **Q: Your agent calls a memory search on every single turn "to be safe." A teammate says this is a production cost problem, not just a latency one. Explain both, and what you'd do instead.**
  A: Latency-wise, every recall call is a network round-trip on the critical path of the response, and it adds up across a multi-turn conversation. Cost-wise, most turns don't actually need retrieval — a user saying "yes, that's right" doesn't need a memory search — so an always-recall policy pays for search traffic (and if it's LLM-mediated query construction, LLM calls) that most turns discard the results of. The stronger design gates recall on a signal that the turn plausibly needs older context (a new topic, an ambiguous reference, an explicit "as I mentioned before") rather than running it unconditionally, the same "don't do work you don't need" discipline that shows up in [[context-compression]]'s compress-only-when-near-limit trigger.

### Context compression failure modes

- **Q: A coding agent compresses its history to control cost, and afterward it opens the same pull request three times. What class of information got lost, and how should the compression policy have treated it differently?**
  A: This is a documented real failure pattern (not hypothetical): reasoning traces are safe to compress because they're re-derivable if needed; observations are mostly safe because they're often re-fetchable; but records of *irreversible side effects* — "I already opened PR #142" — are load-bearing and must never be compressed away, because there's no way to re-derive "did I already do this" from a summary that dropped it. This is the same principle [[idempotency-and-side-effects]] covers from the checkpointing/resume angle: a summarizer that treats all history as equally compressible will eventually erase the one line that prevented a duplicate irreversible action.

- **Q: Merge-forward summarization (fold each new summary into the last one) avoids re-deriving facts from a shrinking transcript, but what failure mode does it introduce over a very long-running conversation?**
  A: Compounding error — each summarization pass is itself lossy, and merge-forward means every subsequent summary is built from an already-imperfect prior summary rather than the original transcript, so small omissions or distortions can accumulate over many passes the way a repeated retelling drifts from the original story. The mitigation isn't "never summarize a summary" (that's what merge-forward exists to avoid doing worse) — it's periodically testing recoverability of specific planted facts across several compression passes, not just one, and treating a summary as suspect after enough rounds rather than assuming durability without re-checking it.

- **Q: A system has a 200K-token context window, well under the model's max, but a user reports the agent "forgot" an instruction given early in a long conversation, before any compression triggered. Is this a memory problem?**
  A: Not a memory-system problem at all — it's context rot / lost-in-the-middle, a property of how attention degrades over long uncompressed context even when nothing was ever dropped (see [[context-rot-and-long-context-management]]). The instructive point for an interview is that compression and summarization aren't only cost-saving tools — done well, pulling the important facts to the front/recent part of the prompt can actually *improve* reliability versus leaving everything in raw, uncompressed order, because a bigger window doesn't make every position in it equally "visible" to the model.
