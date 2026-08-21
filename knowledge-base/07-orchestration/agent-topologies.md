---
stage: "07-orchestration"
tools: [langgraph]
tags: [orchestration, multi-agent, architecture]
last_verified: 2026-08-20
verified_against: "langgraph 1.2.x (this repo's pin)"
---

# Agent topologies

A topology is the shape of a multi-agent system — which agents exist and who hands work to whom — and the single-vs-multi-agent decision is an organizational cost/benefit call, not a maturity upgrade.

## Prerequisites
- [[workflow-vs-agent-autonomy-spectrum]]
- [[agentic-loop-fundamentals]]

## In plain English

Once you've decided a task needs an agent at all (see [[workflow-vs-agent-autonomy-spectrum]]), a second, separate decision follows: does it need *one* agent, or several? "Topology" names the shape of the answer — the roster of agents plus the routing between them. A single well-scoped agent with several tools is not a multi-agent system; splitting into multiple agents only pays off when there's a reason you can name — genuine separation of expertise (a fact-checker sharing the writer's context would confirm its own fabricated citation), independent parallelizable sub-tasks, or a generator/critic split where the critic needs to *not* share the generator's blind spots. Coordination between agents is a real, additional cost: message passing, state synchronization, lossy re-serialization at every handoff (a worker sees a summary, not the supervisor's full context), and entirely new failure modes that a single agent's loop never has to deal with. Per course material (`presentations/day3.md`), most measured multi-agent failures are coordination/specification bugs, not model mistakes — the topology you pick is itself a source of risk, not just a design nicety.

## Core mechanics

Topology shapes fall into three families, ordered roughly by how much coordination they cost:

| Shape | Structure | Use when |
|---|---|---|
| Sequential (pipeline/chain) | A → B → C, fixed order | Each stage's output is exactly what the next stage needs, no revision loop |
| Parallel (fan-out/fan-in) | Split → N independent workers → merge | Sub-tasks are genuinely independent and can run concurrently (map-reduce) |
| Hierarchical (supervisor-worker) | One coordinator routes repeatedly to N specialists, all report back (star) | Which specialist is needed depends on the task, and the order isn't knowable in advance |

A few structural notes that matter when picking between them:

- **Sequential and parallel are still workflows** in the [[workflow-vs-agent-autonomy-spectrum]] sense if the human designer can enumerate the path — a fixed A→B→C pipeline or a fan-out/merge over a known set of subtasks doesn't need an LLM deciding *who talks to whom*, only content at each step.
- **Hierarchical (supervisor-worker) is what actually needs "agent" autonomy at the routing layer** — a router that runs in a loop, choosing the next worker based on current task state, is unbounded unless capped. This shape, and the ReAct/Planner-Executor/Reflection/Supervisor-Worker patterns built on top of it, is graph-building territory — see [[langgraph-agentic-patterns]] for the mechanics (state, conditional edges, loop-back caps) and [[supervisor-worker-teams]] for the write-scoping and dual-critic design that makes a supervisor team safe to loop.
- **Topology is usually fixed at design time.** Per course material (`presentations/day3.md`), a fixed roster can only reroute work it anticipated — a task needing a capability outside the roster means an escalation or a redeploy, not a runtime decision. Dynamic topology (an agent composing its own team at runtime, e.g. Deep Agents' subagent delegation) is flagged in the same material as a 2026 frontier extension of the fixed pattern, worth building only after the fixed version already works, and worth capping hard: depth, concurrency, and budget, set by the harness, not left for the model to self-limit.

## Sample code

Topology is a design decision, not an API call — there's no single class you instantiate for "sequential" vs "hierarchical." The shape shows up in *how a graph is wired*: a sequential topology is a chain of nodes with no branching edges; a parallel topology fans out from one node to several running concurrently, joined by a reducer field; a hierarchical topology is every worker node routing back to one supervisor node via a conditional edge keyed on state. That wiring — `add_conditional_edges`, state reducers, loop-back caps — is covered in [[langgraph-graph-patterns]] and [[langgraph-agentic-patterns]]; this page stays at the shape-and-tradeoff level on purpose, to avoid duplicating that mechanics.

## Alternatives

Not applicable — this is a concept/architecture page, not a tool page. See [[langchain-vs-langgraph]] and [[langgraph-graph-patterns]] for the tooling used to implement any of these shapes.

## How this shows up in the capstone

Milestone 5 (orchestrated LangGraph workflow with checkpointing) is exactly this decision made concrete: ShopSense's Triage → Policy RAG → Order-Actions → Escalation Reviewer agents are wired as a hierarchical (supervisor-worker) topology, not a fixed pipeline, because which specialist handles a ticket depends on its content and can require looping back (e.g. escalation after a failed order action) — see [[capstone-milestone-map]].

## Interview fire round

- **Q: When does splitting one agent into a multi-agent team actually pay off?**
  A: When there's a nameable reason — distinct expertise that must not share context (a critic that shouldn't see the generator's reasoning), genuinely independent parallelizable sub-tasks, or a generator/critic split — not as a default "more advanced" upgrade.
- **Q: Why is a hierarchical/supervisor topology the one that needs real agent autonomy, while sequential and parallel usually don't?**
  A: In sequential and parallel shapes the designer already knows the path (who runs, in what order); a supervisor topology exists precisely because *which* specialist runs next depends on data the designer can't enumerate ahead of time.

## Production gotchas & best practices

- Per course material (`presentations/day3.md`): a fixed roster serving unanticipated task shapes is a recurring production failure mode — the fix is either an escalation path or, at the cost of much more coordination overhead, dynamic team composition with hard depth/concurrency/budget caps (the model will not stop itself).
- Lab gotcha (`lab-summaries/Day3-Session1-LangGraphPatterns.md`): the decision tree for adding a second agent defaults to *no* — split only for a reason you can name; "it feels more sophisticated" is not one.
- Production practice: coordination overhead compounds with topology depth — a star topology (every worker reporting to one supervisor) costs two supersteps per unit of work, so a 5-agent team can burn through a default recursion limit fast; this is a topology-level cost to budget for, not just a graph-wiring detail (see [[langgraph-agentic-patterns]]).

## Course vs. production

The lab's supervisor team (`lab-summaries/Day3-Session2-MultiAgentProtocols.md`) is a fixed, hand-wired 5-agent star topology, decided entirely at design time. Course material (`presentations/day3.md`) flags dynamic topology — an agent choosing its own team composition at runtime — as an emerging 2026 pattern (Deep Agents' subagent delegation, Kimi K3's Agent Swarm cited as examples), explicitly recommending the fixed version be built and proven first, since the dynamic version adds unbounded fan-out risk on top of ordinary coordination cost.

## Related
- **Builds on** — [[workflow-vs-agent-autonomy-spectrum]], [[agentic-loop-fundamentals]]
- **Implemented via** — [[langgraph-agentic-patterns]], [[langgraph-graph-patterns]]
- **Contrasts with** — [[graph-engineering-mindset]] (topology is *what shape*; graph engineering is *how you build any shape*)
- **Feeds into** — [[supervisor-worker-teams]]

## Sources

**Lab sources**
- `lab-summaries/Day3-Session1-LangGraphPatterns.md` (§ A3 "The four named agentic patterns", § A4 "Decision tree")
- `lab-summaries/Day3-Session2-MultiAgentProtocols.md` (§ "Lab A — Research team with a supervisor", § A4 "Topology")

**Web sources**
- `presentations/day3.md` (Day 3 Session 1 Act 3 "Knowing When to Stop Adding Machinery"; Session 2 Act 2 "When the Team Isn't Fixed") — per-course-material framing for dynamic topology, unbounded fan-out, coordination cost; near-future product names (Kimi K3, Deep Agents subagent delegation) reported as course material, not independently web-verified
