--- LINKEDIN ---
Real interview scenario on agent memory: two memories about the same user directly contradict each other. Six months ago: "prefers aisle seat." More recently: booked a window seat, twice in a row. How should retrieval or write-time logic resolve this?

The naive answers both fail silently. Picking the newer fact discards a preference that may still be genuinely true in a different context. Averaging the two produces a fact that describes neither situation.

The stronger design surfaces the conflict instead of hiding it: weight by recency and frequency — two recent window bookings outweigh one old stated preference — but keep the older fact rather than deleting it, since intent can be genuinely mixed (aisle for long-haul, window for short-haul). Some systems handle this with an explicit "supersedes" edge between memory entries rather than treating memory as one flat, only-additive store.

The interview signal isn't picking the "right" resolution — it's recognizing that unresolved contradiction is a real production state, not something "most recent write wins" correctly resolves.

Does your memory store even have a way to represent two facts disagreeing with each other?

#AppliedAI #LLM #AIEngineering #RAG

--- INSTAGRAM ---
Two memories about the same user disagree. Now what? 🤔

Aisle seat six months ago. Window seat, twice, more recently.

Newest-wins and averaging both fail silently — one discards real context, the other invents a fact that's true of neither.

The real answer: weight by recency, but keep the older fact and surface the conflict.

Full scenario + answer in the carousel.

#AppliedAI #LLM #AIEngineering #GenAI #Developer

--- VISUAL FORMAT ---
carousel — 5 slides
1. Title — "Two Memories About The Same User Disagree"
2. The question — aisle seat vs window seat, twice
3. The wrong answers — newest-wins and averaging both fail silently
4. The answer — surface the conflict, don't hide it
5. Takeaway — unresolved contradiction is a real production state (closing question)
