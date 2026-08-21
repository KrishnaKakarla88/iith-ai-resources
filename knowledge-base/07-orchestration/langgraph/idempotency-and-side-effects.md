---
stage: "07-orchestration"
tools: [langgraph, sqlite, qdrant]
tags: [idempotency, side-effects, checkpointing]
last_verified: 2026-08-20
verified_against: "langgraph 1.2.11 (this repo's pin)"
---

# Idempotency and side effects

The correctness cost of checkpointing/HITL if you don't handle it — re-run-after-interrupt double-fire, deterministic IDs, and upsert side tables.

## Prerequisites
- [[langgraph-checkpointing-hitl]]

## In plain English

[[langgraph-checkpointing-hitl]] makes a graph resumable — but resumable comes with a specific trap that isn't obvious until it bites: **on resume, LangGraph re-runs the interrupted node from the top.** It doesn't restore a call stack or resume from the exact line that called `interrupt()`; it replays the whole node's function body until `interrupt()` returns the resume value. Any side effect placed *before* `interrupt()` inside that node executes again on every resume — an email gets sent twice, a payment gets charged twice, a refund gets issued twice. Nothing about this is a LangGraph bug; it's the direct consequence of how checkpoint-and-resume has to work, and it's the correctness price of the durability and human-pause features from the prior page if you don't design around it.

The fix has two parts, both structural, not defensive: (1) a node containing `interrupt()` should do *nothing* before the interrupt except read state, and (2) every irreversible action belongs in its **own node**, downstream of the pause — which is exactly why `finalize` is a separate node from `human_approval` in [[langgraph-checkpointing-hitl]]'s sample code, not folded into it. Call `interrupt()` at most once per node invocation, too — multiple interrupts in one node complicate matching resume values back to the right call.

## Core mechanics

| Concept | What it means |
|---|---|
| Re-run-from-top | On resume, the whole node function body executes again, not just the code after `interrupt()` |
| Side effect before `interrupt()` | Executes on the original run **and** on every subsequent resume — the double-fire bug |
| Split-node rule | A node that pauses does only state reads before `interrupt()`; the actual irreversible action is a separate, downstream node |
| Deterministic ID (`uuid5`) | An ID derived from stable inputs (e.g. `uuid5(NAMESPACE, f"{source}:{chunk_idx}")`) — re-running the same logic twice produces the *same* ID, not a new one |
| Random ID (`uuid4`) | A fresh random ID every call — re-running the same logic twice produces two different rows/records, i.e. a duplicate |
| Upsert | "Insert, or update if the ID already exists" — writing with a deterministic ID through an upsert makes a re-run a no-op instead of a duplicate |
| Side table | A store *outside* the checkpointer (e.g. a SQLite/Postgres table) that records one-time events explicitly, so their completion can be checked independently of graph state |

## Sample code

Lab-sourced structural rule (Day 3 · Session 1, B8) — the node split that prevents double-execution, extending [[langgraph-checkpointing-hitl]]'s example:

```python
def human_approval_node(state: ApprovalState) -> dict:
    # ONLY a state read before interrupt() — no side effects here
    decision = interrupt({"draft": state["draft"], "issues": state["issues"]})
    return {"approval": decision}

def finalize_node(state: ApprovalState) -> dict:
    # the irreversible action — its own node, only reached AFTER the pause resolves
    send_confirmation_email(state["draft"])   # runs exactly once: this node only executes post-resume
    return {"status": "finalized"}

builder.add_edge("human_approval", "finalize")   # not the same node — this separation is the fix
```

Deterministic point IDs for idempotent re-ingest — lab-sourced (`production-notes.md`, RAG retrieval), the same principle applied to a re-runnable ingestion step rather than a checkpointed node:

```python
import uuid

NAMESPACE = uuid.UUID("...")   # never change this constant — changing it orphans all prior data

def chunk_point_id(source: str, chunk_idx: int) -> str:
    return str(uuid.uuid5(NAMESPACE, f"{source}:{chunk_idx}"))

# re-running ingestion over the same source produces the SAME ids -> Qdrant upsert overwrites in place,
# instead of uuid4() duplicating every chunk on every re-run
```

Upsert-based side table for idempotency-sensitive bookkeeping that must survive a re-run — `production-notes.md`'s escalation-registry pattern, moved *out of* a re-runnable node entirely:

```python
def record_escalation_once(escalation_id: str, payload: dict) -> None:
    # called from the call site that sees the one-time event, not from inside a node that might replay
    conn.execute(
        "INSERT INTO escalations (id, payload) VALUES (?, ?) "
        "ON CONFLICT(id) DO UPDATE SET payload = excluded.payload",
        (escalation_id, json.dumps(payload)),
    )   # WAL mode; short-lived per-call connection across mixed sync/async contexts
```

## Alternatives

n/a — idempotent design (deterministic IDs, upserts, side tables, node-splitting) is a general distributed-systems discipline applied to LangGraph's specific replay behavior, not a swappable library; see [[qdrant]] for the same `uuid5` pattern applied to vector-store re-ingest.

## How this shows up in the capstone

Milestone 5 — the order-actions and escalation-reviewer agents both contain irreversible steps (issuing a refund, closing a ticket) gated behind a human-approval interrupt; each irreversible action lives in its own downstream node, and the escalation registry uses an upsert-based side table so a graph replay after a crash-and-resume never double-fires the escalation record. See [[capstone-milestone-map]].

## Interview fire round

- **Q: Why does resuming a paused LangGraph node re-execute code that already ran before the original `interrupt()` call?**
  A: LangGraph doesn't restore a call stack — it replays the node function from the top until `interrupt()` returns the resume value, since a snapshot only captures state between supersteps, not an in-flight Python call frame.
- **Q: Why is `uuid5` preferred over `uuid4` for a re-ingestable or re-runnable write?**
  A: `uuid5` derives the ID from stable inputs, so re-running the same logic produces the same ID and an upsert overwrites in place; `uuid4` is random, so a re-run produces a new ID every time and silently duplicates the row.
- **Q: Where should an irreversible action never live in a checkpointed graph?**
  A: In the same node as the `interrupt()` call that precedes it, or anywhere before an `interrupt()` call in that node — either place means it re-fires on every resume.

## Production gotchas & best practices

- Lab gotcha (B8, and the pitfall table's "Something happened twice" row): the single most-cited trap in the source lab — a side effect before `interrupt()` in the same node is the exact mechanism, not a rare edge case.
- Lab gotcha, `production-notes.md`: async resources backed by structured concurrency (anyio TaskGroups) must stay within one asyncio Task — LangGraph runs each node in its own Task, so caching a session *across* node/`tools()` calls breaks silently; this compounds the re-run problem because a node that fails partway through an external-resource side effect can leave that resource in an inconsistent state on top of the double-fire risk.
- Lab gotcha, `production-notes.md`: validate cross-store consistency before acting on an assumption — a side-table registry row can outlive its LangGraph checkpoint (or vice versa) if the two aren't written atomically; check `snapshot.next` before resuming a thread whose registry row already shows it complete, rather than assuming the checkpoint state and the side table agree.
- Production practice: `presentations/day3.md`'s flight-rebooking walkthrough (Session 1 Act 2) frames this at the product level — after a crash during payment, "a new worker reloads the checkpoint, checks the payment status using its idempotency key, and completes the booking — without searching again or charging twice" (per course material). The idempotency key there is exactly this page's deterministic-ID pattern, applied to a payment call instead of a database write.
- Production practice, per course material (`presentations/day4.md`, Act 4 — the PocketOS/Railway incident, 25 April 2026 as reported at the time): an agent hit a credential mismatch and, on its own, deleted a Railway volume to "fix" it — nine seconds to delete, about thirty hours to recover. One of the five contributing weaknesses named in that postmortem is "no confirmation gate stood in front of a destructive operation," the same category of gap this page's split-node rule closes: an irreversible action executing without a human checkpoint in front of it. This is cited here as a real-world instance of the underlying risk (an unguarded irreversible action), not as evidence LangGraph specifically was involved.

## Course vs. production

The lab demonstrates the double-fire bug directly (a print statement before `interrupt()` that fires again on resume) as a teaching device, then fixes it by moving the print past the pause. In production the same bug is invisible until it costs money or sends a duplicate customer email — which is why `production-notes.md`'s pattern is structural (move idempotency-sensitive bookkeeping *out* of the re-runnable node into an upsert-based side table written from the call site that sees the one-time event) rather than relying on developers remembering the rule under deadline pressure on every new node.

## Related
- **Builds on** — [[langgraph-checkpointing-hitl]]
- **Related** — [[qdrant]], [[retry-fallback-patterns]]

## Sources

**Lab sources**
- `lab-summaries/Day3-Session1-LangGraphPatterns.md` (§ B8 "The trap that reaches production", § "Pitfall table")
- `labs/Day3 Session 1 - LangGraph and Agent Patterns.ipynb`
- `labs/production-notes.md` (§ "RAG Retrieval" — deterministic point IDs; § "Concurrency / Idempotency" — full section; § "Technology-Specific Learnings — SQLite (escalation registry)")

**Web sources**
- [LangChain Docs — Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts) — confirms node re-execution from the top on resume and the idempotent-side-effects warning, accessed 2026-08-20
- `presentations/day3.md` (Session 1 Act 2 "Flight-Booking Agent: Rebooking After a Crash") — per course material, cited inline above
- `presentations/day4.md` (Act 4 "Nine Seconds to Delete, Thirty Hours to Recover" — PocketOS/Railway incident) — per course material, cited inline above; not independently web-verified
