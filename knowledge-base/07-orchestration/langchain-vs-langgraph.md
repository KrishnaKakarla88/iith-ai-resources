---
stage: "07-orchestration"
tools: [langchain, langgraph]
tags: [orchestration, decision-guide]
last_verified: 2026-08-20
verified_against: "langgraph 1.2.x, langchain-litellm 0.7.x, langchain-mcp-adapters 0.3.x (this repo's pins — no direct `langchain` pin, see Course vs. production)"
---

# LangChain vs LangGraph

A decision guide, not a rivalry: LangChain gives you a chain (a fixed sequence of steps) and a batteries-included agent constructor built on top of LangGraph; LangGraph gives you the stateful, resumable graph underneath when a chain's straight line isn't enough.

## Prerequisites
- [[graph-engineering-mindset]]
- [[react-pattern]]

## In plain English

These aren't two competing frameworks to pick one of forever — as of LangChain 1.0, LangChain's own agent runtime is *built on* LangGraph. The real decision is narrower than "LangChain or LangGraph": it's **chain vs. graph**, i.e. does this specific piece of work run the same steps in the same order every time (a chain, composed with LCEL — see [[langchain-runnables-lcel]]), or does it need branching, a human pause point, or resumability after a crash (a graph, see [[graph-engineering-mindset]])? LangChain's `create_agent` sits in between: it's a pre-built ReAct-style agent loop, running on LangGraph underneath, that saves you from wiring your own graph when a standard tool-calling loop is all you need. Reach for raw LangGraph only when you need node-level control a pre-built agent doesn't give you — custom state, non-standard routing, multiple cooperating agents.

## Core mechanics

| Question | Answer points to |
|---|---|
| Does every run visit the same steps, in the same order, to completion? | A **chain** (LCEL) — see [[langchain-runnables-lcel]] |
| Does the model need to decide *which* tool to call and when to stop, in a standard loop? | LangChain's **`create_agent`** — a pre-built agent, running on LangGraph, no custom graph code needed |
| Does the workflow need conditional routing, a human-in-the-loop pause, multiple specialized agents, or resumability after a crash? | Raw **LangGraph** — `StateGraph`, custom nodes/edges — see [[langgraph-state]], [[langgraph-graph-patterns]] |

Concretely, per the current (2026) LangChain docs¹: `create_agent(model=..., tools=[...], system_prompt=..., middleware=[...])` is the recommended entry point for "an LLM that calls tools in a loop," replacing the older `AgentExecutor`/`create_tool_calling_agent` pattern, which is now in maintenance-only mode with LangChain's own docs describing a migration off it. The migration path the docs describe is `AgentExecutor` → `create_agent` (simplest, runs LangGraph internally) → a full custom `StateGraph` (only if you need node-level control `create_agent`'s middleware/hooks don't give you).

A useful three-way split, per course material (`presentations/day3.md`), for how much of the graph you want built for you: raw LangGraph gives maximum control (you build the state machine, nodes, and edges yourself); a batteries-included harness like Deep Agents adds planning, subagents, and a virtual filesystem on top of LangGraph; and vendor-specific opinionated SDKs (e.g. Anthropic's Claude Agent SDK) sit at the other end. None of these is objectively "better" — it's a control-vs-convenience tradeoff for the project at hand, not a maturity ladder.

## Sample code

Lab-sourced (`labs/Day3 Session 1 - LangGraph and Agent Patterns.ipynb`), the lab's own framing of when *not* to reach for a graph — pattern 2, a prompt chain, uses only structured LLM output plus plain code, no graph at all:

```python
# Prompt chain: extract -> validate -> post (fixed order, human decided the steps)
# Only `extract` calls the model; validate/post are plain deterministic code —
# paying a model for a rule or an arithmetic check buys only variance.
invoice_data = chat_model.with_structured_output(InvoiceSchema).invoke(raw_text)
if not validate(invoice_data):
    raise ValueError(...)
post(invoice_data)
```

Contrast with pattern 4 (a tool-calling agent), where the model decides which tool to call and when to stop — this is what `create_agent` (LangChain) or a `ToolNode` + conditional edge (raw LangGraph) exists for:

```python
from langchain.agents import create_agent

agent = create_agent(
    model="groq:llama-3.1-8b-instant",
    tools=[search_supplier_risk, lookup_contract],
    system_prompt="Research supplier risk before recommending a decision.",
)
result = agent.invoke({"messages": [{"role": "user", "content": "..."}]})
```

`create_agent` is a 2026 LangChain doc pattern (verified against the current `docs.langchain.com/oss/python/langchain` site, not this repo's own notebooks — the lab notebooks build LangGraph agents directly with `ToolNode`/`tools_condition` rather than `create_agent`, see [[langgraph-agentic-patterns]]).

## Alternatives

Not applicable in the standard sense — this page *is* the alternatives comparison between LangChain and LangGraph within one vendor's stack. For alternatives to the LangChain/LangGraph ecosystem as a whole, see the Alternatives tables on [[langchain-runnables-lcel]], [[langchain-chains-vs-agents]], and [[langgraph-graph-patterns]].

## How this shows up in the capstone

Milestone 5 (orchestrated LangGraph workflow with checkpointing) is the concrete answer to this page's question for ShopSense: individual tool-calling agents from earlier milestones (Triage, Policy RAG, Order-Actions) are wrapped as **plain chains** wherever a step is fixed and linear, but the multi-agent orchestration connecting them — routing between specialists, looping back to a human on escalation — is a **graph**, because that routing genuinely can't be enumerated as one straight-line sequence; see [[capstone-milestone-map]].

## Interview fire round

- **Q: If LangChain's `create_agent` already runs on LangGraph internally, why would you ever drop down to raw LangGraph?**
  A: When you need control `create_agent` doesn't expose — custom state fields beyond messages, non-standard conditional routing, multiple cooperating agents with their own read/write scopes, or checkpointing/HITL wired at points a pre-built agent loop doesn't pause at.
- **Q: What's the single question that tells you "chain" vs "graph" fastest?**
  A: Would every run of this task visit the same steps, in the same order, to completion? If yes, a chain is enough and a graph's branching/checkpointing machinery goes unexercised.

## Production gotchas & best practices

- Lab gotcha (`lab-summaries/Day3-Session1-LangGraphPatterns.md`, A2): "paying a model for a rule or an arithmetic check buys only variance" — the most common mistake this decision guards against is reaching for an agent (or a graph) where a fixed chain of code would do, not the reverse.
- Production practice: per the current LangChain docs¹, `AgentExecutor`/`create_tool_calling_agent` is deprecated in favor of `create_agent`; new code should not be written against the older pattern, and existing `AgentExecutor` code has a stated migration deadline the docs describe as within 2026.
- Production practice: because this repo's `pyproject.toml` pins `langchain-litellm` and `langchain-mcp-adapters` but not a direct `langchain` package, projects following this stack should pin `langchain` explicitly once they adopt `create_agent`, rather than relying on it as a transitive dependency of an adapter package.

## Course vs. production

The lab notebooks (`labs/Day3 Session 1 - LangGraph and Agent Patterns.ipynb`, `labs/Day3 Session 2 - MultiAgent Teams and Agent Protocols.ipynb`) build every agent — including simple tool-calling ones — directly on raw LangGraph (`ToolNode`, `tools_condition`, hand-wired `StateGraph`s), never via LangChain's `create_agent`. That's a deliberate teaching choice (see the graph internals rather than a wrapped constructor), not a signal that `create_agent` is unavailable or discouraged in production — current LangChain docs¹ present `create_agent` as the default entry point for exactly the tool-calling-loop case the lab builds by hand.

## Related
- **Builds on** — [[graph-engineering-mindset]], [[react-pattern]]
- **Contrasts with** — [[langchain-chains-vs-agents]]
- **Feeds into** — [[langgraph-graph-patterns]], [[langgraph-agentic-patterns]]

## Sources

**Lab sources**
- `lab-summaries/Day3-Session1-LangGraphPatterns.md` (§ A2 "One minimal graph per pattern", § A4 "Decision tree")
- `labs/Day3 Session 1 - LangGraph and Agent Patterns.ipynb`
- `pyproject.toml` (dependency pins)

**Web sources**
- ¹[LangChain — Overview (docs.langchain.com/oss/python/langchain/overview)](https://docs.langchain.com/oss/python/langchain/overview) — `create_agent` as primary entry point, "Agent = Model + Harness," LangChain agents built on LangGraph, accessed 2026-08-20
- ¹[LangChain — Agents (docs.langchain.com/oss/python/langchain/agents)](https://docs.langchain.com/oss/python/langchain/agents) — `create_agent` signature/params, checkpointer/middleware options, and (via cross-referenced search of current LangChain migration guidance) `AgentExecutor`'s maintenance-only status and the `AgentExecutor` → `create_agent` → `StateGraph` migration path, accessed 2026-08-20
- `presentations/day3.md` (Session 1, Act 1 Q2 "What's the difference between a graph, a harness, and a framework?") — control-vs-convenience framing across raw LangGraph / Deep Agents / Claude Agent SDK, cited as course material
