---
stage: "05-memory"
tools: [supermemory]
tags: [memory, tool, per-customer-memory]
last_verified: 2026-08-20
verified_against: "supermemory Python SDK (pip install supermemory), API used in labs/Day2 Session 1 - Memory Engineering.ipynb"
---

# Supermemory

Supermemory is a managed memory API this stack uses to give each customer a durable, per-user memory store — writing episodic/semantic/procedural facts and searching them back semantically, isolated by a `container_tag` per customer.

## Prerequisites
- [[memory-types]]

## In plain English

An LLM call is stateless — nothing persists between requests unless your application saves it somewhere and hands it back next time. You could build that "somewhere" yourself: a database table, an embedding call per fact, a similarity search on read. Supermemory is a hosted service that does that job for you — you send it text ("the user prefers aisle seats"), tag it with an identifier for *whose* memory this is, and later ask it "what do we know about seat preferences?" and get relevant memories back, without writing or maintaining the embedding/indexing/search pipeline yourself.

The identifier that keeps one customer's memories from bleeding into another's is called a **`container_tag`** — a stable string per user, workspace, or tenant (e.g. a customer ID). Every write and every search is scoped to a container_tag, which is what makes this usable for a multi-tenant product like ShopSense: customer A's memories are never visible to customer B's queries, as long as the tag is applied on every read and write ([Supermemory — Organizing & Filtering Memories docs](https://supermemory.ai/docs/concepts/filtering), accessed 2026-08-20).

One operational quirk worth knowing before you build against it: writes are **asynchronous**. Calling `add()` queues the memory for indexing — it does not become searchable the instant the call returns. Code that writes a memory and immediately searches for it needs to poll, not assume.

## Core mechanics

| Call | What it does | Notes |
|---|---|---|
| `client.add(content, container_tag, metadata=...)` | Writes a new memory or document | Indexing is async — not immediately searchable |
| `client.search.memories(q, container_tag, limit=k)` | Semantic search over extracted memories | Returns readable text in a `.memory` field; singular `container_tag` |
| `client.search.documents(q, container_tags=[...], limit=k)` | Semantic search over raw document/chunk content | Text lives in a `.chunks` field; plural `container_tags` |
| `client.search(q, container_tag, search_mode=...)` | Newer unified search call | `search_mode` ∈ `"hybrid"` (memories + documents, recommended), `"memories"`, `"documents"` — supersedes the two calls above in current SDK docs, though the lab uses the older split calls ([Supermemory — Search docs](https://supermemory.ai/docs/search), accessed 2026-08-20) |
| `client.memories.profile(container_tag, include=["static"])` | Distills memories into a queryable user profile | Runs after background extraction has had time to run |

The response-shape asymmetry between `search.memories` (`.memory`) and `search.documents` (`.chunks`) is a real gotcha, not a naming accident — a `recall()` helper that only checks one shape will silently return nothing for the other kind of hit.

## Sample code

Lab-sourced (Day 2 · Session 1 — `labs/Day2 Session 1 - Memory Engineering.ipynb`), writing a memory and polling until it's searchable:

```python
import time

def write_memory(mem, text: str, kind: str, **extra):
    mem.add(content=text, container_tag=USER_ID, metadata={"type": kind, **extra})

def recall(mem, query: str, k: int = 3):
    """Semantic search, handling both response shapes."""
    hits = mem.search.memories(q=query, container_tag=USER_ID, limit=k)
    if not hits:
        # fall back to document search — different shape (.chunks, plural container_tags)
        hits = mem.search.documents(q=query, container_tags=[USER_ID], limit=k)
    return hits

# writes are async — poll rather than assume immediate searchability
write_memory(mem, "User booked flight AI-302 on 1 Aug.", kind="episodic")
for _ in range(20):
    if recall(mem, "what flight did I book"):
        break
    time.sleep(3)
```

Import/install note: `pip install supermemory` (current published version 3.45.0 per PyPI, requires Python 3.9+ — [PyPI — supermemory](https://pypi.org/project/supermemory/), accessed 2026-08-20); the API key is read from `SUPERMEMORY_API_KEY`.

## Alternatives

| Approach | Where it lives | Boring/simple alternative? |
|---|---|---|
| Supermemory | Managed API, `supermemory.ai` | — |
| [Mem0](https://github.com/mem0ai/mem0) | Open-source (Apache-2.0), self-hostable or managed cloud (`app.mem0.ai`) | No — same tier of tooling, but genuinely open-source and self-hostable where Supermemory is API-only |
| [Zep](https://www.getzep.com/) | Managed service built on a temporal knowledge graph ([Graphiti](https://github.com/getzep/graphiti), OSS) | No — models memory as a graph over time rather than flat semantic search, a different retrieval shape entirely |
| A Postgres table (e.g. with [pgvector](https://github.com/pgvector/pgvector), 0.8.6, Postgres 13+) + your own summarizer | Plain Python + Postgres, no vendor | **Yes** — the boring option: store raw facts in a row per (user, fact, timestamp), embed and index with pgvector, write your own extraction/summarization prompt to decide what's worth persisting. No managed indexing pipeline, no async-write polling — but you own the extraction quality, dedup, and consolidation logic that Supermemory/Mem0 build in |

## How this shows up in the capstone

Milestone 3 — persistent memory + semantic index. Supermemory is the concrete storage backend behind ShopSense's per-customer memory layer, namespaced by `container_tag = customer/USER_ID` so one customer's history never leaks into another's context — see [[capstone-milestone-map]].

## Interview fire round

- **Q: Why does `recall()` need to check two different response shapes?**
  A: Supermemory's memory search (`search.memories`) and document search (`search.documents`) return different field names (`.memory` vs `.chunks`) and take slightly different parameter shapes (singular vs plural `container_tag`) — a helper that assumes one shape silently misses hits from the other path.
- **Q: What isolates one customer's memories from another's in a multi-tenant deployment?**
  A: The `container_tag` on every read and write. It has to be applied at every call site — a single missed call site is a cross-customer data leak, not just a bug.
- **Q: Why can't you search for a memory immediately after writing it?**
  A: Supermemory indexes writes asynchronously. `add()` returns before indexing completes, so code needs to poll for searchability rather than assume it.

## Production gotchas & best practices

- Lab gotcha: writes are async — poll for searchability (the lab polls up to 20 times, 3s apart) rather than assuming `add()` is immediately queryable.
- Lab gotcha: `search.memories` (singular `container_tag`, `.memory` field) and `search.documents` (plural `container_tags`, `.chunks` field) have different response shapes — handle both if you don't know in advance which path will have the hit.
- Production practice (from `labs/production-notes.md`, TA/logistics references stripped): enforce an **explicit per-tenant namespace on every read and write** — a single missed call site leaks cross-customer data; there is no default isolation Supermemory enforces for you beyond respecting the tag you pass.
- Production practice (from `labs/production-notes.md`): **label recalled memory as untrusted in the prompt** — memory can contain the assistant's own past hallucinations, so wrap recalled content in a system message marked "never the source of a new tool argument," the same discipline applied to RAG output in [[grounded-answers-injection-defense]].
- Production practice (from `labs/production-notes.md`): **identity must come only from the authenticated session, never from message text** — guessing a customer identifier out of free text (e.g. an order reference mentioned in a message) is a real regression class, not a hypothetical.
- Production practice (from `labs/production-notes.md`): Supermemory has **no bulk "list all" API**, so purge/deletion is a best-effort semantic sweep, not a guaranteed-complete operation — document this limitation rather than assuming a delete workflow is exhaustive. Also: a purge must clear any in-process cache, not just the persistent store, or a long-lived process keeps serving stale data after a delete.
- Production practice (from `labs/production-notes.md`): **fail open but log loudly** on a broken memory write — swallow the exception so a memory-store outage doesn't take down the customer-facing turn, but keep `exc_info=True` so the failure is visible in logs/traces, not silent.
- Production practice: per course material (`presentations/day2.md`), 2026-era systems increasingly let the *agent* decide what's worth writing to memory in the moment (agent-managed memory, e.g. Anthropic's `memory_20250818` file-based tool) rather than the application pre-classifying every write — Supermemory's `metadata={"type": ...}` tagging in this lab is still an app-decided scheme, one valid point on that spectrum rather than the only one.

## Course vs. production

The lab writes memories directly from application code with a fixed, pre-decided `type` tag (episodic/semantic/procedural) and polls synchronously for searchability inside a notebook cell. In production, per course material (`presentations/day2.md`), two things typically change: (1) what gets written and when is increasingly left to the agent's own judgment rather than hardcoded in application logic, and (2) uncurated long-term memory accumulates duplicates and stale facts over months of real use — production systems run a **consolidation** pass (an offline batch job between sessions, informally called "Dreaming" per course material) that merges duplicate facts and prunes what's gone stale, something a single-session lab notebook never needs to demonstrate. See [[context-compression]] for the mechanics of that consolidation step.

## Related
- **Builds on** — [[memory-types]]
- **Contrasts with** — a Postgres table + your own summarizer (see Alternatives above)
- **Related** — [[context-compression]], [[grounded-answers-injection-defense]]

## Sources

**Lab sources**
- `lab-summaries/Day2-Session1-MemoryEngineering.md` (§ "Lab A — Four Kinds of Memory", § "Gotchas")
- `labs/Day2 Session 1 - Memory Engineering.ipynb`
- `labs/production-notes.md` (§ "Memory")

**Course material**
- `presentations/day2.md` — Act 3 ("When the Agent Manages Its Own Memory"), agent-managed memory / consolidation framing

**Web sources**
- [Supermemory — Search docs](https://supermemory.ai/docs/search) — `search.memories` vs `search.documents` response shapes, unified `search()` with `search_mode`, accessed 2026-08-20
- [Supermemory — Organizing & Filtering Memories](https://supermemory.ai/docs/concepts/filtering) — `container_tag` semantics, multi-tenant isolation, accessed 2026-08-20
- [PyPI — supermemory](https://pypi.org/project/supermemory/) — current published version 3.45.0, Python 3.9+ requirement, accessed 2026-08-20
- [mem0ai/mem0 (GitHub)](https://github.com/mem0ai/mem0) — Apache-2.0 license, self-hostable, hosted cloud option, accessed 2026-08-20
- [Zep — getzep.com](https://www.getzep.com/) — managed service, temporal knowledge graph model, free tier available, accessed 2026-08-20
- [pgvector (GitHub)](https://github.com/pgvector/pgvector) — current version 0.8.6, Postgres 13+, accessed 2026-08-20
