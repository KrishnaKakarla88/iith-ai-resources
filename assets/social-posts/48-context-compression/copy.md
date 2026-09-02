--- LINKEDIN ---
The API is stateless — every turn, your app resends the entire history it wants the model to see. By turn 40 that's an afternoon's worth of messages before every reply. Naive truncation "fixes" the ceiling by deleting the oldest messages, but it's silent: the order number from turn 3 is just gone, and the user assumes you still know it.

Context compression is the deliberate alternative: keep the last N turns verbatim, replace everything older with a short rolling summary, merged forward each pass so a fact from turn 3 survives even after two more compressions run.

The catch is right in "tries to preserve": summarization is an LLM call, and LLM calls aren't reliable extractors. A summary can read as complete prose and still have dropped the one detail that mattered — a peanut allergy, an urgent flag.

summary = summarize_turns(turns[:-RECENT_KEEP])
assert "kiwi" in summary.lower() # proves the planted fact survived compression

That's the actual lesson: plant a known fact, compress past it, assert it's recoverable. Never trust a summary because it sounds faithful.

One production gotcha worth knowing: LLM summarization reliably paraphrases exact identifiers instead of preserving them verbatim. Keep a raw recent-turns cache for anything identifier-shaped, and fall back to the compressed summary only for softer context. Also — temperature=0 here isn't optional; a summarization prompt is the one place you don't want creative variance.

Has a summarizer ever silently dropped the one detail your agent needed three turns later?

#AppliedAI #LLM #AIEngineering #RAG

--- INSTAGRAM ---
Your summary sounds complete. That doesn't mean it's correct. 📝

Naive truncation silently deletes what the user assumes you still know. Summarization at least tries — but it's lossy, so you have to test it.

Plant a fact, compress past it, assert it survived:
assert "kiwi" in summary.lower()

Keep raw order numbers/IDs uncompressed — summarizers paraphrase them.

Full mechanics in the carousel.

#AppliedAI #LLM #AIEngineering #GenAI #Developer

--- VISUAL FORMAT ---
carousel — 6 slides
1. Title — "Never Trust A Summary Because It Sounds Complete"
2. Two failure modes — naive truncation vs unverified summarization
3. Core mechanics — recent-keep window + rolling summary (diagram)
4. The actual lesson — plant a fact, compress past it, assert (code)
5. Production practice — keep a raw fallback for exact identifiers
6. Takeaway — temperature=0 isn't optional here (closing question)
