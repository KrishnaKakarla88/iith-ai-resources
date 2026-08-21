---
stage: "07-orchestration"
tools: [langgraph]
tags: [langgraph, state, reducers]
last_verified: 2026-08-20
verified_against: "langgraph 1.2.11 (this repo's pin)"
---

# LangGraph state

The typed state object that flows through a graph's nodes, and how reducers control how updates merge into it.

## Prerequisites
- [[graph-engineering-mindset]]
- [[pydantic-basics]]
- [[type-hints-basics]]

## In plain English

A LangGraph graph is built around one shared object: **state**. Every node reads from it and writes back to it, and the graph engine is responsible for merging each node's return value into the running state before the next node sees it. State is declared up front as a typed schema (usually a `TypedDict`), the same way a Pydantic model declares the shape of structured output elsewhere in this stack — except here the schema describes not a single LLM response, but everything the whole run needs to remember between steps.

The one non-obvious rule that trips people up first: a node does not return the *whole* state, it returns a **partial update** — just the keys it touched. The engine takes that partial dict and merges it into the full state using a per-key **reducer**. If you don't specify a reducer for a key, the default reducer is "last write wins" (overwrite). That default is exactly right for some fields (a routing decision) and exactly wrong for others (a running list of messages), which is why reducers exist as an opt-in per field, not a global setting.

## Core mechanics

| Concept | What it does |
|---|---|
| State schema | A `TypedDict` (or Pydantic model) passed to `StateGraph(State)` — declares every key the graph can read/write |
| Partial update | A node's return value — a dict containing only the keys it changed, not the full state |
| Default reducer | Overwrite — the new value replaces the old one for that key |
| `Annotated[type, reducer]` | Opts a key into a custom reducer instead of overwrite |
| `add_messages` | The reducer for chat history — appends new messages, and replaces an existing message if its `id` matches (used for edits/tool results) |
| `operator.add` | Generic accumulate-by-`+` reducer — works for lists (concatenate) and numbers (sum) |
| `InvalidUpdateError` | Raised when two nodes write the *same* un-reduced key in the same superstep — the engine refuses to silently pick a winner |

The **control vs. audit field** split, from the lab, is the practical design pattern that follows directly from the reducer choice: a field a [[langgraph-conditional-edges]] router reads to decide what happens next (e.g. `issues: list[str]`) must stay overwrite-only, or it never becomes empty again once anything has ever failed — the router would loop forever reading stale history. A *separate* field with an accumulate reducer (e.g. `issue_log: Annotated[list[str], add]`) preserves the full history for audit/debugging without corrupting the control field the router depends on. General rule: **facts the graph acts on are control fields (overwrite); everything the graph remembers for a human or a trace is an audit field (accumulate)**.

## Sample code

Lab-sourced (Day 3 · Session 1 — `labs/Day3 Session 1 - LangGraph and Agent Patterns.ipynb`, Lab B, document-approval workflow). LangGraph 1.2.x:

```python
from typing import Annotated
from typing_extensions import TypedDict
from operator import add

class ApprovalState(TypedDict):
    draft: str                                   # overwrite — current draft, one owner
    issues: list[str]                             # overwrite — control field the router reads
    issue_log: Annotated[list[str], add]           # accumulate — audit trail, never read by a router
    revision_count: int                            # overwrite — control field, guards the revise loop

def check_document(state: ApprovalState) -> dict:
    issues = run_policy_checks(state["draft"])
    return {"issues": issues, "issue_log": issues}   # partial update: only these two keys
```

Multi-agent fan-in state, where concurrent writers to the *same* key require a reducer or the run raises `InvalidUpdateError`:

```python
class ResearchState(TypedDict):
    reads: Annotated[list[str], add]   # legal/finance/compliance nodes write in parallel; add fuses their outputs
```

## Alternatives

n/a — state-with-reducers is LangGraph's own mechanism, not a swappable component; see [[langgraph-graph-patterns]] and [[graph-engineering-mindset]] for what the "boring alternative" (a plain dict passed through a `while` loop) gives up.

## How this shows up in the capstone

Milestone 5 (orchestrated LangGraph workflow with checkpointing) — every agent's LangGraph graph starts by defining its state schema, and the control/audit split governs how a supervisor's routing fields stay separate from its worker-visit history; see [[capstone-milestone-map]].

## Interview fire round

- **Q: Why does a node return a partial update instead of the whole state?**
  A: So the engine can apply a per-key reducer instead of a blind overwrite, and so two nodes touching different keys in the same superstep don't stomp on each other.
- **Q: What happens if two nodes write the same key in the same superstep and it has no reducer?**
  A: `InvalidUpdateError` — the engine refuses to silently pick a winner between two conflicting writes.

## Production gotchas & best practices

- Lab gotcha: don't give a control field (one a conditional edge reads to route) an accumulate reducer — it never resets, so the router can never observe "no more issues" and the graph loops forever. Keep a separate audit field for history.
- Lab gotcha: a `TypedDict` is not runtime-validated — a misspelled key in a node's return value silently creates a dead channel nothing ever reads, rather than raising. `production-notes.md` and the lab both call out printing/inspecting state after every node during development as the habit that catches this early.
- Production practice: prefer a Pydantic model over a bare `TypedDict` for state when the graph is complex enough that a typo-silently-swallowed bug would be expensive to find — LangGraph supports either as the schema passed to `StateGraph`.

## Course vs. production

The lab's state schemas are small and hand-checked by re-reading `stream_mode="updates"` output during development. In production, a growing state dict is also a tracing liability, not just a correctness one — `production-notes.md` documents a real incident where a blanket tracing decorator `repr()`'d the full state (including raw customer chat text) onto every node's span; see [[langfuse-tracing]] for the redact-keys fix. State design and observability design aren't separate concerns once the graph is live.

## Related
- **Builds on** — [[graph-engineering-mindset]]
- **Feeds into** — [[langgraph-nodes]], [[langgraph-conditional-edges]]
- **Contrasts with** — [[langchain-runnables-lcel]]

## Sources

**Lab sources**
- `lab-summaries/Day3-Session1-LangGraphPatterns.md` (§ B1 "State: control vs. audit fields", § "Pitfall table")
- `labs/Day3 Session 1 - LangGraph and Agent Patterns.ipynb`
- `labs/production-notes.md` (§ "Concurrency / Idempotency" — "Overwrite semantics for control fields, accumulate only the audit log")

**Web sources**
- [LangChain Docs — Graph API (State, reducers, Annotated)](https://docs.langchain.com/oss/python/langgraph/graph-api) — `TypedDict` state schema, `Annotated[type, reducer]` syntax, `add_messages`/`operator.add` reducers, accessed 2026-08-20
- [LangChain Reference — langgraph.graph.message.add_messages](https://reference.langchain.com/python/langgraph/reference/graphs/) — message-list reducer merge-by-`id` behavior, accessed 2026-08-20
