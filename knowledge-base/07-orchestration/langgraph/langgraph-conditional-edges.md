---
stage: "07-orchestration"
tools: [langgraph]
tags: [langgraph, conditional-edges, routing]
last_verified: 2026-08-20
verified_against: "langgraph 1.2.11 (this repo's pin)"
---

# LangGraph conditional edges

Edges whose destination is decided at runtime by a routing function reading current state — how branching logic gets expressed as a graph.

## Prerequisites
- [[langgraph-edges]]
- [[langgraph-state]]

## In plain English

A conditional edge replaces "always go to node B" with "call this function with the current state, and go wherever it says." The routing function itself is deliberately boring: it takes state, returns a string (or a label mapped to a node name), and contains **no model call**. The lab's rule for wiring these correctly, stated as a slogan: **decide in a node, route in an edge.** Whatever fuzzy judgment needs to happen (did the draft pass review? which category does this ticket belong to?) happens inside a node and gets written to state as a plain value; the conditional edge that follows just reads that value and picks a path. This keeps the routing function itself unit-testable without a graph or a model call — it's pure `state -> str`.

## Core mechanics

| Concept | What it does |
|---|---|
| Routing function | `def route(state) -> str`, a pure function of state — no model call inside it |
| `builder.add_conditional_edges(node, route_fn, path_map)` | After `node` runs, call `route_fn(state)`; look up its return value in `path_map` to get the next node name |
| `path_map` (optional) | `{return_value: node_name, ...}` — when omitted, the routing function's return value is used directly as the node name |
| Wiring mismatch | If `route_fn` can return a value not present as a key in `path_map`, that's a **run-time** error, not a compile-time one — the most common conditional-edge bug per the lab |
| `Command(goto=..., update=...)` | An alternative to a separate router: a node returns both a state update and its own routing decision in one object — see [[langgraph-graph-patterns]] |

## Sample code

Lab-sourced (Day 3 · Session 1, A2.3 — IT ticket triage router). The model makes exactly one run-time choice; the router itself never touches the model:

```python
def route(state: TriageState) -> str:
    return state["category"]  # already written to state by a prior node; pure lookup here

builder.add_conditional_edges(
    "classify",
    route,
    {"billing": "billing_agent", "technical": "tech_agent", "other": "human_review"},
)
```

Lab B's loop-guarded revision router (Day 3 · Session 1, B3/B4) — the pattern behind every capped loop in this stack:

```python
def route_after_checks(state: ApprovalState) -> str:
    if state["issues"] and state["revision_count"] < MAX_REVISIONS:
        return "revise"
    return "approval"   # either clean, or max revisions hit -> escalate to a human, don't loop forever

builder.add_conditional_edges("check", route_after_checks, {"revise": "revise", "approval": "human_approval"})
```

## Alternatives

n/a — `add_conditional_edges` is LangGraph's own construct; the "boring alternative" to the whole graph-with-routing-function idea is an `if/elif` chain inside a plain Python function, which is exactly what `graph-engineering-mindset` argues stops scaling once branches need independent checkpointing, tracing, or resume.

## How this shows up in the capstone

Milestone 5 — the triage step that routes an incoming customer message to the right ShopSense sub-agent (policy RAG vs. order-actions vs. escalation reviewer) is a conditional edge whose routing function reads a category field written by an upstream classification node, never calling a model itself. See [[capstone-milestone-map]].

## Interview fire round

- **Q: Why must the routing function itself never call a model?**
  A: So it stays a pure, unit-testable function of state — "decide in a node, route in an edge" keeps the one non-deterministic step isolated to a node, where its output gets validated and written to state before any routing happens.
- **Q: What's the most common conditional-edge bug, and when does it surface?**
  A: A routing function returning a value that isn't a key in the `path_map` — it raises at run time (when that specific path is actually taken), not at graph-compile time, so it can hide until a rare state combination triggers it.

## Production gotchas & best practices

- Lab gotcha: validate a routing function's return value against its `path_map`'s legal keys *before* it reaches the edge — the lab's supervisor-worker pattern applies this specifically to a hallucinated worker name, falling back to a deterministic default rather than letting an unmapped return value crash the run.
- Lab gotcha: a loop-back conditional edge needs a **state guard** (e.g. `revision_count < MAX_REVISIONS`) as the primary exit condition, with LangGraph's `recursion_limit` only as the crash-instead-of-design backstop — see [[idempotency-and-side-effects]] and `production-notes.md`'s `MAX_SUPERVISOR_VISITS` pattern ("graceful loop guard beneath the framework's hard limit").
- Production practice: `graph.stream(seed, stream_mode="updates")` shows exactly what each node wrote, which is the fastest way to debug a conditional edge going to the wrong place — check what the state field it reads actually contains before assuming the routing function is buggy.

## Course vs. production

The lab's routers are small, enumerated category sets (billing/technical/other; revise/approval). In production, especially for a supervisor picking among many workers, the router's return value needs the same "validate before it reaches the edge" treatment `production-notes.md` documents for hallucinated worker names — an LLM-produced category string is untrusted input to a router exactly like any other tool argument, per [[auth-and-multi-tenancy]]'s broader "identity/critical fields never come from free text" rule.

## Related
- **Builds on** — [[langgraph-edges]], [[langgraph-nodes]]
- **Feeds into** — [[langgraph-graph-patterns]], [[langgraph-agentic-patterns]]
- **Related** — [[react-pattern]]

## Sources

**Lab sources**
- `lab-summaries/Day3-Session1-LangGraphPatterns.md` (§ A2.3 "Router", § B3 "Wiring: decide in a node, route in an edge", § "A3 Supervisor-Worker")
- `labs/Day3 Session 1 - LangGraph and Agent Patterns.ipynb`
- `labs/production-notes.md` (§ "Retry / Resilience" — `MAX_SUPERVISOR_VISITS`)

**Web sources**
- [LangChain Docs — Graph API (Conditional edges)](https://docs.langchain.com/oss/python/langgraph/graph-api) — `add_conditional_edges` signature, `path_map`, `Command(goto=...)` as an alternative, accessed 2026-08-20
