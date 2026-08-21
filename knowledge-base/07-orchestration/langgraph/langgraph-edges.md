---
stage: "07-orchestration"
tools: [langgraph]
tags: [langgraph, edges]
last_verified: 2026-08-20
verified_against: "langgraph 1.2.11 (this repo's pin)"
---

# LangGraph edges

Static edges that connect nodes into a fixed execution path through the graph.

## Prerequisites
- [[langgraph-nodes]]

## In plain English

An edge is simply "after node A finishes, run node B next." It carries no logic of its own — a static edge always goes to the same destination, every run, regardless of what state contains. Every graph needs at least two special edges to be valid: one from the built-in `START` marker into your first node, and one from your last node into the built-in `END` marker. Everything in between is either a static edge (this page) or a [[langgraph-conditional-edges]] (branching decided at run time).

The lab's framing for when a static edge is the right tool: if every run of your graph visits the same steps in the same order, you don't need branching at all — a prompt chain like `extract → validate → post` is entirely static edges, because a human already decided the step order and the model only fills in fuzzy content within one step.

## Core mechanics

| Concept | What it does |
|---|---|
| `START` | Built-in entry marker — every graph needs `add_edge(START, "first_node")` |
| `END` | Built-in exit marker — a path with no outgoing edge from a node never terminates that branch |
| `builder.add_edge(a, b)` | Fixed transition: after node `a` completes, run node `b` next, unconditionally |
| Parallel fan-out | Multiple `add_edge(START, node)` calls (or one node with several outgoing static edges) run those nodes concurrently within the same superstep |
| Superstep | One execution tick — all nodes scheduled to run "at the same time" run within one superstep before the engine checks state and schedules the next one |

## Sample code

Lab-sourced (Day 3 · Session 1, A2.2 — invoice prompt chain, `extract → validate → post`). Human wrote the step order; only `extract` uses a model:

```python
from langgraph.graph import StateGraph, START, END

builder = StateGraph(InvoiceState)
builder.add_node("extract", extract_node)   # model, with_structured_output(PydanticModel)
builder.add_node("validate", validate_node) # plain code
builder.add_node("post", post_node)         # plain code

builder.add_edge(START, "extract")
builder.add_edge("extract", "validate")
builder.add_edge("validate", "post")
builder.add_edge("post", END)

graph = builder.compile()
```

Static fan-out (Day 3 · Session 1, A2.5 — parallel legal/finance/compliance specialists), each running concurrently before a `merge` node fans back in — see [[langgraph-graph-patterns]] for the full map-reduce shape:

```python
builder.add_edge(START, "legal")
builder.add_edge(START, "finance")
builder.add_edge(START, "compliance")
builder.add_edge("legal", "merge")
builder.add_edge("finance", "merge")
builder.add_edge("compliance", "merge")
builder.add_edge("merge", END)
```

## Alternatives

n/a — a static edge is LangGraph's own primitive; the boring alternative to the whole graph abstraction (sequential function calls in a script) is discussed in [[graph-engineering-mindset]] and [[langgraph-graph-patterns]], not something that competes at the edge-primitive level.

## How this shows up in the capstone

Milestone 5 — the deterministic parts of each ShopSense sub-agent's workflow (e.g. a fixed validate-then-execute sequence) are wired as static edges; only the genuinely data-dependent branches use [[langgraph-conditional-edges]]. See [[capstone-milestone-map]].

## Interview fire round

- **Q: When is a static edge the right choice over a conditional edge?**
  A: When every run visits the same steps in the same order regardless of state — no branch is ever actually taken, so a conditional edge would just be unused machinery.
- **Q: What happens if a node has no outgoing edge at all?**
  A: That path never reaches `END` — the run either hangs on that branch or (for the graph as a whole) errors, depending on whether other branches complete; every node needs a way forward, explicit or via `END`.

## Production gotchas & best practices

- Lab gotcha (A4, decision tree): "can *you* enumerate the paths now?" is the test for whether a step should be a static edge (workflow, cheaper/testable/reproducible) versus something needing a conditional edge or full agent autonomy — don't reach for branching machinery you don't structurally need.
- Production practice: a graph made entirely of static edges is functionally a chain — see [[langchain-vs-langgraph]] and [[langgraph-graph-patterns]] for when the state/checkpoint machinery is worth carrying even without branching (mainly: you still want checkpointing/resume for a long-running fixed sequence).

## Course vs. production

The lab's static-edge chains (invoice extract-validate-post) run in seconds inside a notebook cell, so checkpointing rarely matters there in practice. In production, the same fixed sequence often still gets a checkpointer wired at `compile()` purely for resume-after-crash durability, even though no edge in the graph is conditional — durability and branching are separate reasons to use LangGraph, and a graph can need one without the other. See [[langgraph-checkpointing-hitl]].

## Related
- **Builds on** — [[langgraph-nodes]]
- **Feeds into** — [[langgraph-conditional-edges]], [[langgraph-graph-patterns]]
- **Contrasts with** — [[langchain-runnables-lcel]]

## Sources

**Lab sources**
- `lab-summaries/Day3-Session1-LangGraphPatterns.md` (§ A2.2 "Prompt chain", § A2.5 "Multi-agent", § A4 "Decision tree")
- `labs/Day3 Session 1 - LangGraph and Agent Patterns.ipynb`

**Web sources**
- [LangChain Docs — Graph API (Edges, START/END)](https://docs.langchain.com/oss/python/langgraph/graph-api) — `add_edge`, `START`/`END` markers, superstep execution model, accessed 2026-08-20
