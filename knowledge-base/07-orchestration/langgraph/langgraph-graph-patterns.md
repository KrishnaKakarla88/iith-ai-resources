---
stage: "07-orchestration"
tools: [langgraph]
tags: [langgraph, graph-patterns]
last_verified: 2026-08-20
verified_against: "langgraph 1.2.11 (this repo's pin)"
---

# LangGraph graph patterns

Five minimal graph shapes and a walkthrough of building a sample graph from them.

## Prerequisites
- [[langgraph-conditional-edges]]
- [[workflow-vs-agent-autonomy-spectrum]]

## In plain English

Every LangGraph graph — however elaborate — is assembled from a small set of recurring shapes. The lab builds one minimal, runnable example of each, arranged along the autonomy spectrum from [[workflow-vs-agent-autonomy-spectrum]]: the first three shapes are **workflows** (a human enumerated the paths; the model only fills content or picks among known branches), the last two are **agents** (the model dynamically directs its own next step). Recognizing which shape a problem actually needs — instead of defaulting to the most flexible one — is the same design skill as knowing how to build any of them.

## Core mechanics: the five shapes

| # | Shape | Structure | Autonomy | Use when |
|---|---|---|---|---|
| 1 | Single call | `START → node → END`, no branching | Workflow | One judgment, squeezed into a typed output at the boundary |
| 2 | Prompt chain | `START → step1 → step2 → step3 → END`, all [[langgraph-edges]] | Workflow | A human already knows the step order; the model fills fuzzy content in one step |
| 3 | Router | `START → classify → [[langgraph-conditional-edges]] → one of N branches → END` | Workflow (one run-time choice) | The model makes exactly one categorical decision; everything downstream is fixed per category |
| 4 | Single tool-calling agent (loop) | `START → agent ⇄ tools → END`, a conditional edge decides "call another tool" vs. "done" | Agent | The model decides which tool and when to stop; the sequence of actions can't be enumerated in advance |
| 5 | Multi-agent (fan-out/fan-in) | `START → [node A, node B, node C] (parallel) → merge → END` | Agent (or workflow, if the split is static) | Independent subtasks that can run concurrently and get combined |

Each shape is a composition of the same three primitives covered on the prior pages: [[langgraph-state]] for what flows through, [[langgraph-nodes]]/[[langgraph-edges]] for the fixed structure, and [[langgraph-conditional-edges]] for anywhere a run-time choice needs to be made. Shape 4 additionally needs a **step cap** in its conditional edge (an uncapped tool-calling loop is unbounded cost); shape 5 needs a reducer on any state key multiple parallel nodes write to, or the run raises `InvalidUpdateError` — see [[langgraph-state]].

## Sample code: a walkthrough of shape 4 (the loop pattern most later pages build on)

Lab-sourced (Day 3 · Session 1, A2.4 — supplier risk research agent). The graph is a loop: `agent` decides whether to call a tool or stop; `tools` executes whatever was called and loops back:

```python
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from typing import Annotated
from typing_extensions import TypedDict

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]   # conversation reducer — nodes append, don't overwrite
    steps: int

@tool
def check_supplier_risk(supplier_name: str) -> str:
    """Look up a supplier's risk rating in the vendor database."""
    ...

model_with_tools = chat_model.bind_tools([check_supplier_risk])

def agent_node(state: AgentState) -> dict:
    response = model_with_tools.invoke(state["messages"])
    return {"messages": [response], "steps": state["steps"] + 1}

def should_continue(state: AgentState) -> str:
    last = state["messages"][-1]
    if state["steps"] >= MAX_TOOL_STEPS:   # mandatory cap — an uncapped agent loop is an open invoice
        return "end"
    return "continue" if last.tool_calls else "end"

builder = StateGraph(AgentState)
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode([check_supplier_risk]))
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", should_continue, {"continue": "tools", "end": END})
builder.add_edge("tools", "agent")   # the loop-back edge

graph = builder.compile()
```

The three new pieces this shape introduces over shapes 1-3: `@tool` (the function's docstring is the prompt text the model reads to decide when to call it), `.bind_tools([...])`, and `Annotated[list, add_messages]` — a reducer is now mandatory because both `agent` and `tools` append to the same `messages` key across loop iterations.

## Alternatives

n/a — these are LangGraph's own composable primitives, not a swappable component; see [[langchain-vs-langgraph]] for when reaching for any of these five shapes (vs. a plain chain) is worth the added state/checkpoint machinery in the first place.

## How this shows up in the capstone

Milestone 5 — each ShopSense sub-agent maps to one of these shapes before any code is written (order-actions is shape 4, a bounded tool loop; the supervisor is shape 5's fan-out/fan-in generalized into a repeated loop, covered fully in [[langgraph-agentic-patterns]]). See [[capstone-milestone-map]].

## Interview fire round

- **Q: What's the fastest way to decide which of the five shapes a new problem needs?**
  A: Ask whether you can enumerate the valid paths *right now*. If yes, it's shapes 1-3 (a workflow); if the next action genuinely depends on data you don't have until run time, it's shape 4 or 5 (an agent).
- **Q: Why does shape 5 (multi-agent fan-out) need a reducer that shape 2 (prompt chain) doesn't?**
  A: In shape 2, exactly one node writes to any given key at a time — overwrite is fine. In shape 5, multiple nodes write concurrently in the same superstep; without a reducer, that's an `InvalidUpdateError`, not a silent pick-one.

## Production gotchas & best practices

- Lab gotcha: shape 4's `MAX_TOOL_STEPS` cap and shape 5's fan-in reducer are both non-negotiable, not tuning knobs — an uncapped tool loop is unbounded cost, and an un-reduced concurrent write is a crash, not a silent bug.
- Lab gotcha (A4 decision tree): default to NO on multi-agent (shape 5) even when the problem could technically fan out — a second agent adds a lossy re-serialization boundary at every handoff; split only for a reason you can name (distinct expertise, real parallel speed-up, or a generator/critic split).
- Production practice: build the fixed version of a shape first, even when you expect to eventually need more autonomy — per `presentations/day3.md` (Act 2, "Dynamic Agent Topology"), a dynamic/runtime-composed topology (an agent choosing its own team size, not just its own tool sequence) is presented as a natural extension once a fixed 5-agent shape actually works, not a starting point (per course material, `presentations/day3.md`).

## Course vs. production

The lab's shape 5 example (legal/finance/compliance fan-out) uses a small, fixed set of parallel nodes decided at design time. `presentations/day3.md` frames runtime-composed topology (an agent deciding how many other agents it needs, with hard caps on spawn depth/breadth/budget set by the harness, not the model) as where dynamic multi-agent systems are heading in 2026 — per course material, not something this repo's labs implement. See [[agent-topologies]] for the fixed-vs-dynamic topology decision in full.

## Related
- **Builds on** — [[langgraph-conditional-edges]], [[langgraph-state]]
- **Feeds into** — [[langgraph-agentic-patterns]]
- **Related** — [[agent-topologies]], [[workflow-vs-agent-autonomy-spectrum]]

## Sources

**Lab sources**
- `lab-summaries/Day3-Session1-LangGraphPatterns.md` (§ A1 "The autonomy spectrum", § A2 "One minimal graph per pattern")
- `labs/Day3 Session 1 - LangGraph and Agent Patterns.ipynb`

**Web sources**
- [LangChain Docs — Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api) — `StateGraph`, `add_node`/`add_edge`/`add_conditional_edges` composition, accessed 2026-08-20
- [LangChain Reference — langgraph.prebuilt (ToolNode)](https://reference.langchain.com/python/langgraph.prebuilt) — prebuilt tool-execution node used in shape 4, accessed 2026-08-20
- `presentations/day3.md` (Session 1 Act 1 "Why Graph Engineering, and Why Now?"; Session 2 Act 2 "Dynamic Agent Topology") — per course material, cited inline above
