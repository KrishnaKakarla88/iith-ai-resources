---
stage: "07-orchestration"
tools: [langgraph, langgraph-checkpoint-sqlite]
tags: [langgraph, checkpointing, human-in-the-loop, interrupt]
last_verified: 2026-08-20
verified_against: "langgraph 1.2.11, langgraph-checkpoint-sqlite 3.1.1 (this repo's pins)"
---

# LangGraph checkpointing & human-in-the-loop

Persisting graph state so execution can pause, resume, and accept human input mid-run via `interrupt()`/`Command(resume=)`.

## Prerequisites
- [[langgraph-state]]
- [[langgraph-agentic-patterns]]

## In plain English

A bare `while` loop that dies mid-run loses everything — there's no saved position to resume from, so a crash at minute forty means starting over at minute zero (per `presentations/day3.md`'s framing of what a loop cannot do). A **checkpointer** fixes this by snapshotting the graph's state after every [[langgraph-state]] superstep, so a crashed or paused run can pick up exactly where it left off instead of restarting.

That same save-point mechanism is also what makes **human-in-the-loop (HITL)** possible: a graph can pause itself mid-node, wait — for seconds or for days — and resume later with a human's input folded into the resumed state. Both capabilities depend on the same primitive: nothing about pausing or resuming works without a checkpointer wired in first.

## Core mechanics

| Term | Meaning |
|---|---|
| Checkpointer | Pluggable saver, snapshots state after every superstep; wired at `.compile(checkpointer=...)` |
| Thread | One run, identified by a `thread_id` inside the `config` dict passed to every graph call |
| Checkpoint | One snapshot within a thread |
| `interrupt(payload)` | Called *inside* a node; pauses the graph and surfaces a JSON-serializable payload to the caller |
| `Command(resume=value)` | Resumes a paused thread; `value` becomes `interrupt()`'s return value inside the node that called it |
| `graph.get_state_history(config)` | Walks a thread's checkpoint history — the "`git log`" of a run |
| `InMemorySaver` | RAM-only — dies with the process; fine for tests, not for anything that must survive a restart |
| `SqliteSaver` / `PostgresSaver` | File- or database-backed — survives a process/kernel restart |

**Analogy the lab uses**: checkpointer = git for execution; `thread_id` = branch; `get_state_history()` = `git log`.

### Dynamic `interrupt()` vs. static `interrupt_before`/`interrupt_after`

There are two distinct interrupt mechanisms in current LangGraph, and they are not interchangeable:

- **`interrupt(payload)`** — called from inside a node, at a point of your choosing, carrying an arbitrary JSON-serializable payload. This is the production HITL primitive: approve a refund, edit a draft, choose between options.
- **Static `interrupt_before=["node_name"]` / `interrupt_after=[...]`** — passed to `.compile()`, these are unconditional breakpoints with **no payload** — debugging tools, not a production approval mechanism.

**Version note for this repo**: `interrupt_before`/`interrupt_after` are still present in current LangGraph 1.x and are not deprecated — but they remain what they always were, static debugging breakpoints. Some older web content (pre-1.0) describes `interrupt_before` as *the* HITL mechanism; that's outdated framing, not a wrong API — the dynamic `interrupt()` + `Command(resume=...)` pair is what carries a payload and what this repo's labs and this page both use for real approval flows. Don't mistake "still exists" for "still the recommended approach for approvals."

**Three preconditions for `interrupt()` to work at all**, per the lab: a checkpointer wired at `.compile()` **before** the pause point is ever reached, a `thread_id` present in the call's `config`, and a JSON-serializable payload. Missing any of the three fails silently or errors in a way that's easy to misattribute — see the pitfall table below.

**Three response shapes**, all handled by the same `Command(resume=...)` primitive: approve (`Command(resume={"action": "approved", "note": "..."})`), reject, or edit-then-approve (the resume value replaces the field being reviewed, e.g. `edited_draft` replacing `draft` mid-run).

**`interrupt()` gives no authorization by itself** — it only pauses and resumes. *Who* approved and *under what authority* has to be written into state/an audit log explicitly by your own code; the primitive doesn't record that for you.

## Sample code

Lab-sourced (Day 3 · Session 1, Lab B — document approval workflow), LangGraph 1.2.x current API:

```python
from langgraph.types import interrupt, Command
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

def human_approval_node(state: ApprovalState) -> dict:
    # nothing before interrupt() except reading state — see idempotency-and-side-effects
    decision = interrupt({
        "draft": state["draft"],
        "issues": state["issues"],
        "prompt": "Approve, reject, or edit this draft?",
    })
    return {"approval": decision}   # decision is whatever Command(resume=...) supplied

builder.add_node("human_approval", human_approval_node)
builder.add_node("finalize", finalize_node)   # irreversible action — its own node, downstream of the pause
builder.add_edge("human_approval", "finalize")

conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)
saver = SqliteSaver(conn)
saver.setup()   # one-line swap from InMemorySaver — "durability is a deployment concern, not a design one"

graph = builder.compile(checkpointer=saver)

config = {"configurable": {"thread_id": "approval-run-42"}}
graph.invoke(seed_state, config=config)          # runs until the interrupt, then pauses

# ... later, possibly after a real process/kernel restart, same thread_id:
graph.invoke(Command(resume={"action": "approved", "note": "looks good"}), config=config)
```

Debugging habit the lab calls out explicitly: `graph.stream(seed, stream_mode="updates")` shows what each node wrote; `stream_mode="values"` shows the full state after each superstep — since `TypedDict` state isn't runtime-validated, a misspelled key silently creates a dead channel, and this is the fastest way to catch that.

## Alternatives

| Approach | Where it lives | Boring/simple alternative to LangGraph's checkpointer? |
|---|---|---|
| LangGraph checkpointer (`InMemorySaver`/`SqliteSaver`/`PostgresSaver`) | Built into `langgraph` + separate `langgraph-checkpoint-*` packages | — |
| Temporal | Standalone durable-execution engine (`temporal.io`) | No — a heavier, general-purpose workflow engine; teams increasingly pair it with LangGraph rather than choose one, using Temporal for macro-level durable orchestration and LangGraph for the in-node agent reasoning loop |
| Prefect / Dagster | Data/workflow orchestration platforms | No — built for scheduled data pipelines, not per-conversation agent state; usable for the outer job schedule around an agent, not the agent's own turn-by-turn state |
| A hand-rolled state table (Postgres row per thread, JSON column) + manual resume logic | Plain Python, no framework | **Yes** — the boring option; you write your own snapshot-after-each-step and resume-from-snapshot logic instead of getting it from the framework |

## How this shows up in the capstone

Milestone 5 (orchestrated LangGraph workflow with checkpointing) — the escalation-reviewer agent's human-approval step is exactly this pattern: `SqliteSaver` (swapped for Postgres in deployment) wired before the pause, `interrupt()` carrying the case details, `Command(resume=...)` carrying the reviewer's decision, and the irreversible action (executing a refund, closing a ticket) living in its own node downstream of the pause. See [[capstone-milestone-map]].

## Interview fire round

- **Q: Why must the checkpointer be wired before the interrupt point, and not the other way round?**
  A: `interrupt()` needs somewhere to persist the paused state to before it can safely stop execution and wait — without a checkpointer already wired at `.compile()`, there's nothing to resume *from*, so wiring it after the interrupt point silently fails to actually pause anything durably.
- **Q: What's the difference between `interrupt_before=["node"]` and calling `interrupt()` inside a node?**
  A: `interrupt_before` is a static, payload-less debugging breakpoint set at compile time; `interrupt()` is called dynamically from inside a node's own logic, carries an arbitrary JSON payload, and is the mechanism used for real approval/edit workflows.
- **Q: Does `interrupt()` record who approved the paused step?**
  A: No — it only pauses and resumes; recording who approved and under what authority has to be written into state/an audit log by your own code.

## Production gotchas & best practices

- Lab gotcha: `InMemorySaver` dies with the kernel — `SqliteSaver` (file-backed) or a Postgres-backed saver is required for anything that must survive a real process restart; this is the entire point of Milestone 5 in the source lab.
- Lab gotcha: a checkpointer persists **state**, never **code** — after a restart, node functions and graph wiring must be rebuilt (in production: your service importing and re-compiling the graph at startup) before a paused thread can resume; nothing about the state itself is lost, it's sitting in the `.sqlite`/Postgres store.
- Lab gotcha, pitfall table: "Resume starts fresh" → wrong or missing `thread_id` — reuse the *exact* config dict used for the original run, not a fresh one. "No checkpointer" errors on interrupt → checkpointer wasn't wired at `.compile()`. "Old thread won't resume" → the state schema changed after checkpoints were already written for that thread — mint a new `thread_id`, or freeze the schema early.
- Lab gotcha, production note: checkpoint files are a deserialization surface — `LANGGRAPH_STRICT_MSGPACK=true` or an explicit allow-list restricts what gets reconstructed on resume; treat the checkpoint store like a database (backed up, access-controlled), not a scratch file.
- Lab gotcha, `production-notes.md`: scope `thread_id` to the unit of work, not the session — a fresh `thread_id` per turn is correct in the lab's memory design; reusing one `thread_id` across a whole session leaked finished state into the next turn's routing.
- Production practice: don't over-interrupt — pausing on every model call trains reviewers to rubber-stamp. Reserve `interrupt()` for irreversible, high-blast-radius, or regulated actions, and for plan approval before expensive execution, per both the lab and `presentations/day3.md`.

## Course vs. production

The lab demonstrates durability with a local `.sqlite` file and a genuine kernel restart inside the notebook — enough to prove the mechanism, not enough to run multi-worker. In production, `PostgresSaver`/`AsyncPostgresSaver` is the recommended checkpointer for multi-worker services (per LangChain's own persistence docs), since a file-based SQLite store doesn't safely support concurrent writers across processes. The lab's one-line swap (`InMemorySaver` → `SqliteSaver`) generalizes directly to `SqliteSaver` → `PostgresSaver` for deployment, with no change to graph logic — exactly the point the lab makes about durability being a deployment concern, not a design one.

## Related
- **Builds on** — [[langgraph-state]], [[langgraph-agentic-patterns]]
- **Feeds into** — [[idempotency-and-side-effects]]
- **Related** — [[auth-and-multi-tenancy]]

## Sources

**Lab sources**
- `lab-summaries/Day3-Session1-LangGraphPatterns.md` (§ B5 "Persistence vocabulary", § B6 "Human interrupt", § B7 "The milestone: surviving a real kernel restart", § "Pitfall table")
- `labs/Day3 Session 1 - LangGraph and Agent Patterns.ipynb`
- `labs/production-notes.md` (§ "Concurrency / Idempotency", § "Technology-Specific Learnings — LangGraph")

**Web sources**
- [LangChain Docs — Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts) — `interrupt()`/`Command(resume=...)` current API, checkpointer/thread_id requirements, side-effect-before-interrupt warning, accessed 2026-08-20
- [LangChain Docs — Persistence](https://docs.langchain.com/oss/python/langgraph/persistence) — `InMemorySaver`/`SqliteSaver`/`PostgresSaver`, production recommendation for multi-worker services, accessed 2026-08-20
- [LangChain Reference — interrupt (langgraph.types)](https://reference.langchain.com/python/langgraph/types/interrupt) — function signature, accessed 2026-08-20
- `presentations/day3.md` (Session 1 Act 2 "Making the Graph Survive Reality") — per course material, cited inline above
