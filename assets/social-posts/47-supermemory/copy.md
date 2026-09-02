--- LINKEDIN ---
Supermemory is a managed API for durable, per-customer agent memory — you send text, tag it, get relevant memories back later without building the embedding/index/search pipeline yourself. One string decides whether that stays isolated: container_tag.

mem.add(content=text, container_tag=USER_ID, metadata={"type": kind})
mem.search.memories(q=query, container_tag=USER_ID, limit=3)

It has to be applied on every single read and write call site. Miss one, and it's a cross-customer memory leak, not a minor bug.

Two operational gotchas worth knowing before you build against it. First: writes are asynchronous — add() queues indexing, it doesn't complete it, so code that writes a fact and immediately searches for it can get nothing back; poll, don't assume. Second: search.memories() returns hits in a .memory field with a singular container_tag, while search.documents() returns .chunks with a plural container_tags — a recall() helper that only checks one shape silently misses hits from the other.

Production practice from the lab notes: fail open on a memory-store outage (don't take down the customer-facing turn) but log loudly (exc_info=True) so the failure stays visible in traces. And identity has to come from the authenticated session — never guessed out of message text.

One more limit worth documenting up front: there's no bulk "list all" API, so purge is a best-effort semantic sweep, not a guaranteed-complete delete.

If container_tag is your only isolation mechanism, how many call sites in your codebase actually set it correctly?

#AppliedAI #LLM #AIEngineering #RAG

--- INSTAGRAM ---
One string is your entire multi-tenant wall. 🔒

Supermemory gives agents durable per-customer memory — but container_tag has to be set on every read/write or it's a cross-customer leak.

Two gotchas: writes are async (poll before you trust a search), and search.memories() vs search.documents() return different shapes entirely.

Fail open, log loudly, never derive identity from message text.

Full mechanics + code in the carousel.

#AppliedAI #LLM #AIEngineering #GenAI #Developer

--- VISUAL FORMAT ---
carousel — 6 slides
1. Title — "One Tag Is Your Entire Multi-Tenant Wall"
2. The isolation key — container_tag scopes every call (code)
3. The gotcha — writes are asynchronous (code)
4. The response-shape trap — .memory vs .chunks
5. Production practice — fail open, log loudly
6. Takeaway — no bulk list-all API (closing question)
