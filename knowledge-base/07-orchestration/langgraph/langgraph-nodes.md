---
stage: "07-orchestration"
tools: [langgraph]
tags: [langgraph, nodes]
last_verified: 2026-08-20
verified_against: "langgraph 1.2.11 (this repo's pin)"
---

# LangGraph nodes

A node as a plain function that reads state and returns a partial update — the basic unit of work in a graph.

## Prerequisites
- [[langgraph-state]]

## In plain English

A LangGraph node is just a Python function: it takes the current [[langgraph-state]] (a dict-like object matching your schema) and returns a partial update. There is no base class to inherit, no decorator required, no special registration beyond `builder.add_node("name", fn)`. That plainness is deliberate — because a node is a regular callable, you can call it directly with a hand-built state dict in a unit test, without building a graph, wiring a checkpointer, or running anything through the graph engine at all.

Nodes fall into two kinds, and the lab's central discipline is keeping them separate: **deterministic nodes** (plain code — a policy check, a regex extraction, an arithmetic calculation) and **the one node that calls a model**. A rule expressible in code shouldn't be paid for in model variance — "let the model produce, let deterministic code decide" is the lab's summary of this split: an LLM node can *produce* a new draft, but a deterministic node still *decides* whether that draft passes.

## Core mechanics

| Concept | What it means |
|---|---|
| Node function signature | `def node(state: State) -> dict` — reads full state, returns partial update |
| `builder.add_node(name, fn)` | Registers the function under a string name used by edges to refer to it |
| No base class / decorator | A node is called directly as `fn(some_state_dict)` in a unit test |
| `ToolNode` | A prebuilt node (from `langgraph.prebuilt`) that executes whatever tool calls are in the last AI message — the standard node for the "act" half of a ReAct loop, see [[langgraph-agentic-patterns]] |
| Deterministic node | No model call — a pure function of state; unit-testable, cheap, reproducible |
| LLM node | The one node that calls a model; still returns a state update, not raw prose, wherever the graph needs to route on its output |

## Sample code

Lab-sourced (Day 3 · Session 1, Lab B — document approval workflow). The pure deterministic check node and the one LLM node, side by side:

```python
def check_document(state: ApprovalState) -> dict:
    """Pure function — no model. Callable directly in a test with a bare dict."""
    issues = run_policy_checks(state["draft"])          # required sections, banned terms, word limit
    return {"issues": issues, "issue_log": issues}

def llm_revise_node(state: ApprovalState) -> dict:
    """The one node that calls a model — produces a new draft, doesn't decide anything."""
    new_draft = ask(
        system="Rewrite the draft to resolve the listed issues.",
        user=f"Draft:\n{state['draft']}\n\nIssues:\n{state['issues']}",
    ) or state["draft"]  # ask() returns None on failure — fall back to the unrevised draft
    return {"draft": new_draft, "revision_count": state["revision_count"] + 1}

# unit-testable without a graph, a model, or a checkpointer:
result = check_document({"draft": "...", "issues": [], "issue_log": [], "revision_count": 0})
assert result["issues"] == []
```

Registering nodes on a builder (LangGraph 1.2.x):

```python
from langgraph.graph import StateGraph

builder = StateGraph(ApprovalState)
builder.add_node("check", check_document)
builder.add_node("revise", llm_revise_node)
```

## Alternatives

n/a — "a node is a plain function" is LangGraph's own minimalism, not a component with competing implementations to compare; the boring alternative is a plain Python function called directly inside a `while` loop, covered in [[graph-engineering-mindset]].

## How this shows up in the capstone

Milestone 5 — each ShopSense sub-agent's graph is built from a handful of plain-function nodes (deterministic checks + one model-calling step), unit-tested individually before ever being wired into the compiled graph; see [[capstone-milestone-map]].

## Interview fire round

- **Q: Why is it significant that a LangGraph node has no base class or decorator?**
  A: It stays a plain function, callable with a hand-built state dict in a unit test — you can verify node logic without building a graph, wiring a checkpointer, or making a model call.
- **Q: Why keep policy/arithmetic checks out of the LLM node?**
  A: A rule expressible deterministically shouldn't cost model variance — "let the model produce, let deterministic code decide" keeps the fuzzy step (drafting) separate from the trustworthy step (deciding pass/fail).

## Production gotchas & best practices

- Lab gotcha: `ask(...)` (the lab's model-call wrapper) returns `None` on failure by design, so every LLM node needs an explicit `or <fallback>` — a node that doesn't handle a failed call silently propagates `None` into state.
- Lab gotcha: force-set identity/authorization-critical fields inside the node itself, never trust an upstream LLM tool-call argument for them — `production-notes.md` documents `tool_args["customer_ref"]` being unconditionally overwritten server-side before validation, on the same principle as never asking an LLM to reproduce a verbatim field.
- Production practice: because nodes are plain functions, mock the model call (not the node) in tests — `production-notes.md` notes keeping `call_llm` at each caller's module namespace specifically so `patch()` can target it per-module, even after refactoring shared control flow out.

## Course vs. production

The lab's nodes are single-file, hand-tested in-notebook. In production this becomes a real test suite — see [[testing-agent-code]] for unit-testing nodes/routers as plain functions and mocking LLM calls, which is exactly the pattern this page's "no base class" design enables.

## Related
- **Builds on** — [[langgraph-state]]
- **Feeds into** — [[langgraph-edges]], [[langgraph-conditional-edges]]
- **Related** — [[testing-agent-code]], [[tool-calling-fundamentals]]
- **Instrumented via** — [[langfuse-tracing]] (each node function is a natural span boundary for tracing decorators)

## Sources

**Lab sources**
- `lab-summaries/Day3-Session1-LangGraphPatterns.md` (§ B2 "Nodes are plain functions", § A2.4 "Single tool-calling agent")
- `labs/Day3 Session 1 - LangGraph and Agent Patterns.ipynb`
- `labs/production-notes.md` (§ "Tool Calling", § "Schema Validation")

**Web sources**
- [LangChain Docs — Graph API (Nodes)](https://docs.langchain.com/oss/python/langgraph/graph-api) — node function signature, `add_node`, accessed 2026-08-20
- [LangChain Reference — langgraph.prebuilt (ToolNode)](https://reference.langchain.com/python/langgraph.prebuilt) — prebuilt tool-execution node, accessed 2026-08-20
