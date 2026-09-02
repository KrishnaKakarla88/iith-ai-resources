--- LINKEDIN ---
Between API calls an LLM is stateless — nothing persists unless your app resends context or writes something down. The chat history you resend every turn is memory, but only one kind: episodic, and a crude one (a raw transcript, not a distilled "what happened"). The CoALA framework names three more your agent needs too.

Working memory: what's in front of me right now, one turn, never persisted. Episodic: what happened, and when — a timestamped event. Semantic: what's stably true, no story attached. Procedural: how do I do this task, a reusable recipe.

The discriminator that sorts a new fact into episodic vs. semantic: does it have a specific "when"? "User booked flight AI-302 on 1 Aug" has one — episodic. "User prefers aisle seats" doesn't — semantic.

def remember(mem, text, kind, **extra): mem.add(content=text, container_tag=USER_ID, metadata={"type": kind, **extra})

The write call never changes — only the metadata tag decides which bucket a fact lands in. The lab has application code pre-decide that tag. 2026-era systems increasingly hand the judgment to the model itself: Anthropic's memory tool lets Claude read/write files under /memories with no vector DB required.

A plain chat buffer is episodic memory in disguise — no durable facts extracted, no reusable procedures, gone the moment the session ends unless something deliberately persists it.

Next time an agent "re-asks" something it should already know — is that a memory bug, or a working-memory bug?

#AppliedAI #LLM #AIEngineering #RAG

--- INSTAGRAM ---
Your agent's "memory" is probably just a transcript. 🧠

CoALA names four kinds: working (this turn only), episodic (what happened, when), semantic (what's stably true), procedural (how to do a task).

Test: does the fact have a specific "when"? Booked flight AI-302 on 1 Aug = episodic. Prefers aisle seats = semantic.

One write call, different metadata tag — full breakdown in the carousel.

Is your agent forgetting things, or just never writing them down?

#AppliedAI #LLM #AIEngineering #GenAI #Developer

--- VISUAL FORMAT ---
carousel — 6 slides
1. Title — "Why Chat History Isn't Memory Enough"
2. The CoALA taxonomy — working/episodic/semantic/procedural
3. The discriminator — does it have a specific "when"?
4. Core mechanics — one write call, different tags (code)
5. Production practice — who decides what gets written (agent-managed memory)
6. Takeaway — a chat buffer is episodic memory in disguise (closing question)
