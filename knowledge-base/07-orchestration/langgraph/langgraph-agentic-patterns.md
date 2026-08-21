---
stage: "07-orchestration"
tools: [langgraph]
tags: [langgraph, react, planner-executor, reflection, supervisor-worker]
last_verified: 2026-08-20
verified_against: "langgraph 1.2.11 (this repo's pin)"
---

# LangGraph agentic patterns

ReAct, Planner-Executor, Reflection, and Supervisor-Worker expressed as LangGraph graphs, including full supervisor-worker mechanics.

## Prerequisites
- [[langgraph-graph-patterns]]
- [[react-pattern]]
- [[reflection-pattern]]

## In plain English

The four named patterns on this page are all named specializations of [[langgraph-graph-patterns]]' shape 4 (single tool-calling agent, for ReAct) or shape 5 (multi-agent fan-out/fan-in, for the other three). Where shape 4/5 described the raw graph topology, this page is about the *behavioral* pattern each specific wiring produces — what it's for, what it costs, and the specific failure mode each one is designed against. Every pattern here shares one property: each is a **loop**, and every loop in this stack needs an explicit, state-based exit condition plus a hard cap as backstop — "until it is good" is not a termination condition, per both the lab and `presentations/day3.md`.

## Core mechanics: the four patterns

| Pattern | Shape | What loops | Designed-against failure |
|---|---|---|---|
| ReAct | shape 4 (agent ⇄ tools) | Reason → act → observe, repeated | Model calls the same tool forever with no new information |
| Planner-Executor | shape 5 variant (plan once, execute steps) | Executor pops and runs one step per visit | A stale plan once an earlier step invalidates a later one |
| Reflection | shape 5 variant (generate ↔ critic) | Generate → critique → revise | The critic sharing the generator's blind spots (same model) |
| Supervisor-Worker | shape 5 variant (router that loops) | Supervisor repeatedly assigns the next worker | Infinite worker-picking, or a hallucinated worker name |

### ReAct — reason, act, observe, repeated

Built from LangGraph's prebuilts rather than hand-wired: `from langgraph.prebuilt import ToolNode, tools_condition`. `tools_condition` alone can loop forever against a stubborn model, so it's always ANDed with a step cap in the conditional edge — the same `MAX_TOOL_STEPS` discipline from [[langgraph-graph-patterns]]' shape 4. The lab's scenario is an on-call SRE diagnosing an alert: the next lookup genuinely depends on the last finding, which is the irreducible ambiguity that justifies an agent over an enumerated workflow (see [[workflow-vs-agent-autonomy-spectrum]]). See [[react-pattern]] for the prompting-level mechanics (thought/action/observation, the `stop=["Observation:"]` guard against the model narrating its own fake tool output); this page covers only how that loop becomes a graph.

```python
from langgraph.prebuilt import ToolNode, tools_condition

def capped_tools_condition(state) -> str:
    if state["steps"] >= REACT_STEP_CAP:
        return "end"
    return tools_condition(state)   # "tools" or "end" from the prebuilt

builder.add_conditional_edges("agent", capped_tools_condition, {"tools": "tools", "end": END})
```

### Planner-Executor — plan once, execute one step at a time

One call produces the *whole* plan up front, parsed at that boundary into a typed `list[str]` (not left as prose). The `executor` node pops and runs exactly one step per visit — deliberately one node visit per step, not the whole plan in one call — so each step gets its own checkpoint/resume point (see [[langgraph-checkpointing-hitl]]). The known trap: a plan can go stale if executing step 2 invalidates the assumptions behind step 3. The production fix is **replanning** — an edge back to `planner` after execution, at the cost of one extra model call per replan.

```python
def planner_node(state: PlanState) -> dict:
    plan_text = ask(system=PLANNER_PROMPT, user=state["goal"])
    return {"plan": parse_plan_to_steps(plan_text), "step_idx": 0}

def executor_node(state: PlanState) -> dict:
    step = state["plan"][state["step_idx"]]
    result = execute_step(step)
    return {"results": state["results"] + [result], "step_idx": state["step_idx"] + 1}

def route_after_step(state: PlanState) -> str:
    if state["step_idx"] >= len(state["plan"]):
        return "end"
    return "executor"   # or "planner" for a replanning edge, commented-out by default
```

### Reflection — generate, critique, revise, capped

`generate → critique → revise`, looped, capped at `MAX_REFLECT_ROUNDS`. The lab's central caution: **the critic shares the generator's blind spots** (same model, same training) — self-critique catches sloppiness, not ignorance. The rule that follows: if a deterministic checker exists for the property you care about, use *that* as the critic and keep the model only for repair — this is exactly [[langgraph-nodes]]' `check_document()` example, reused here as the critic. Model-critic Reflection is the fallback for when no such oracle exists. Two exit conditions are required, not one: critic says PASS, *or* the round cap is hit — without the cap, a fastidious critic bills forever. The critic node sees only the rules and the current draft, never the generator's reasoning — that independence is the entire value of the separate node; if the critic saw the generator's chain of thought, it would tend to rubber-stamp it.

```python
def route_after_critique(state: ReflectState) -> str:
    if state["verdict"] == "PASS" or state["rounds"] >= MAX_REFLECT_ROUNDS:
        return "end"
    return "revise"
```

### Supervisor-Worker — a router that loops

This is Pattern 3's router ([[langgraph-conditional-edges]]) generalized: instead of choosing once, the supervisor is a router that runs in a loop, re-consulted after every worker's turn. Topology is a **star**: every worker reports back to the supervisor node, never directly to another worker — this is what keeps the fan-in state manageable and the routing logic in one place instead of scattered across worker-to-worker edges.

**Costs, explicit and non-negotiable to account for:** one extra model call per hop (the supervisor's own routing decision), and a **lossy boundary at every handoff** — a worker sees a summary of the task state the supervisor hands it, not the supervisor's full context. This is the same lossy-re-serialization cost [[langgraph-graph-patterns]] flags as the reason multi-agent defaults to NO.

**Two failure modes, two designed-against fixes:**
1. *Infinite worker-picking* — the supervisor keeps assigning work with no natural stopping point. Fix: a hard `MAX_HOPS` cap, checked in the supervisor's own routing function, exactly like the revision-round cap in Reflection.
2. *Hallucinated worker name* — the supervisor's routing output names a worker that doesn't exist in the roster. Fix: **validate the supervisor's chosen worker against the roster before it reaches the conditional edge**, falling back to a deterministic default order rather than letting an unmapped name crash the run at the edge (see [[langgraph-conditional-edges]]'s note on run-time-not-compile-time wiring mismatches).

```python
class TeamState(TypedDict):
    task: str
    reports: Annotated[list[dict], add]   # audit — every worker's report, accumulated
    next_worker: str                      # control — overwrite, read by the router below
    hops: int

WORKER_ROSTER = {"researcher", "writer", "fact_checker"}
DEFAULT_WORKER = "researcher"

def supervisor_node(state: TeamState) -> dict:
    choice = ask(system=SUPERVISOR_PROMPT, user=summarize(state))
    if choice not in WORKER_ROSTER:            # validate before the edge ever sees it
        choice = DEFAULT_WORKER
    return {"next_worker": choice, "hops": state["hops"] + 1}

def route_to_worker(state: TeamState) -> str:
    if state["hops"] >= MAX_HOPS:
        return "end"
    return state["next_worker"]                # pure lookup — no model call in the edge itself

builder.add_conditional_edges(
    "supervisor", route_to_worker,
    {"researcher": "researcher", "writer": "writer", "fact_checker": "fact_checker", "end": END},
)
# every worker node returns an edge back to "supervisor" — the star topology
for w in WORKER_ROSTER:
    builder.add_edge(w, "supervisor")
```

`presentations/day3.md` (Day 3 Session 2 Act 1) frames this same mechanic from the org-design angle: routing is **state-based, not a fixed pipeline** — a supervisor consults an agent directory (each worker's tools, permissions, risk limits, current case state) and matches task state to the right worker, looping back as many times as needed rather than flowing forward once. The `MAX_HOPS`-style cap is presented there as belonging in the design from the start, not bolted on after a runaway-loop incident (per course material).

The write-scopes and dual-critic refinements on top of this star topology — restricting which state keys each worker is allowed to write, and running two independent critics rather than one — are covered in [[supervisor-worker-teams]], which builds on the mechanics above rather than repeating them.

## Alternatives

n/a — these are named usage patterns built from LangGraph's own primitives, not swappable libraries; see [[agent-topologies]] for how these same four shapes compare against non-LangGraph multi-agent frameworks (CrewAI, AutoGen, OpenAI Swarm/Agents SDK) at the topology level.

## How this shows up in the capstone

Milestone 5 (orchestrated LangGraph workflow with checkpointing) and Milestone 6 (multi-agent supervisor team + MCP-backed tool swap) — ShopSense's triage → policy-RAG / order-actions / escalation-reviewer flow is a Supervisor-Worker graph exactly in this shape: a supervisor routes by task state with a hop cap, and the escalation-reviewer path is a Reflection-style generate/critique loop with a deterministic groundedness check as critic where possible. See [[capstone-milestone-map]].

## Interview fire round

- **Q: Why does Reflection specifically warn that "the critic shares the generator's blind spots"?**
  A: Both are the same model with the same training, so a model-based critic reliably catches sloppiness (a missed step, a shallow answer) but not ignorance (a fact the model was never right about to begin with) — a deterministic checker doesn't share that blind spot.
- **Q: What are the two costs of Supervisor-Worker that a single agent doesn't pay?**
  A: One extra model call per hop for the supervisor's own routing decision, and a lossy re-serialization boundary at every handoff — a worker only sees a summary of state, not the supervisor's full context.
- **Q: Why validate the supervisor's chosen worker against the roster before the conditional edge, rather than letting the edge's path_map mismatch fail naturally?**
  A: An unmapped return value from a routing function is a run-time crash (per [[langgraph-conditional-edges]]), not a graceful fallback — validating upstream lets you substitute a deterministic default worker instead of crashing the run on a hallucinated name.

## Production gotchas & best practices

- Lab gotcha: every one of these four patterns needs *two* layers of loop termination — a state-based guard as the intentional exit, and LangGraph's `recursion_limit` only as the backstop that turns an undesigned loop into a crash instead of a silent hang. Removing the state guard and hitting the recursion limit is the lab's own demonstration of `GraphRecursionError`.
- Lab gotcha: in Reflection, prefer a deterministic checker as critic whenever one exists — `check_document()` from [[langgraph-nodes]] is reused as the critic specifically so "does this pass" isn't itself a probabilistic judgment.
- Production practice (`presentations/day3.md`, Day 3 Session 2 Act 2, per course material): a fixed-roster Supervisor-Worker team is the version to build and ship first; a dynamically-composed team (the supervisor deciding its own roster size at run time) is a natural extension once the fixed version works, not a starting point — and if you do extend into dynamic composition, cap spawn depth, concurrency, and total budget in the harness, since "the model won't stop itself."

## Course vs. production

The lab's Supervisor-Worker team has a small, fixed, hardcoded roster known at design time (star topology, 3-5 workers). `presentations/day3.md` describes 2026 production systems moving toward *dynamic* topology — an orchestrator composing the worker roster per task rather than picking from a fixed set — citing Kimi K3's Agent Swarm and LangChain Deep Agents' subagent delegation as concrete implementations (per course material, `presentations/day3.md`; not independently web-verified here). The lab's fixed-roster mechanics above are the correct foundation either way — the source material is explicit that the dynamic version only makes sense once the fixed pattern is proven.

## Related
- **Builds on** — [[langgraph-graph-patterns]], [[react-pattern]], [[reflection-pattern]]
- **Feeds into** — [[supervisor-worker-teams]]
- **Related** — [[agent-topologies]], [[langgraph-conditional-edges]]

## Sources

**Lab sources**
- `lab-summaries/Day3-Session1-LangGraphPatterns.md` (§ A3 "The four named agentic patterns")
- `labs/Day3 Session 1 - LangGraph and Agent Patterns.ipynb`
- `labs/production-notes.md` (§ "Retry / Resilience" — loop guard beneath `recursion_limit`; § "Prompt Engineering" — replacing LLM-inferred rubric with a computed `[FACT]`)

**Web sources**
- [LangChain Reference — langgraph.prebuilt (create_react_agent, ToolNode, tools_condition)](https://reference.langchain.com/python/langgraph.prebuilt) — ReAct prebuilts, accessed 2026-08-20
- `presentations/day3.md` (Session 1 Act 3 "Knowing When to Stop Adding Machinery"; Session 2 Act 1 "Coordinating a Fixed Team"; Session 2 Act 2 "When the Team Isn't Fixed") — per course material, cited inline above
