---
stage: "04-tool-calling-single-agents"
tools: []
tags: [agent-design, agentic-loop, architecture]
last_verified: 2026-08-20
verified_against: "general agentic-loop framing, current as of 2026-08-20"
---

# Agentic loop fundamentals

The perceive → plan → act → observe loop underneath every agent — the general concept that ReAct and reflection are specific flavors of.

## Prerequisites
- [[workflow-vs-agent-autonomy-spectrum]]

## In plain English

Once a system has crossed over into "agent" territory (see [[workflow-vs-agent-autonomy-spectrum]]), it needs some repeating shape to actually do multi-step work. That shape is almost always a variation on the same four moves, repeated:

1. **Perceive** — take in the current state: the user's request, results from the last action, anything new.
2. **Plan** — decide what to do next given that state (which could be "call this tool," "ask a clarifying question," or "I'm done, answer now").
3. **Act** — actually do it: call a tool, make an API request, write a file.
4. **Observe** — take in the result of that action, which becomes the next loop's "perceive" input.

Then repeat, until the model decides it's done or a hard cap stops it. This is the same idea as an OODA loop (observe-orient-decide-act, from military decision theory) or a basic control-system feedback loop — nothing about it is specific to LLMs. What's specific to *agentic* loops is that step 2 (plan) is delegated to the model instead of being hardcoded: your code doesn't decide which tool gets called next, the model's output does.

Every named pattern in this stage is this same loop wearing different clothes. [[tool-calling-fundamentals]]'s tool-call loop is the loop expressed as structured function calls. [[react-pattern]] is the loop expressed as an explicit text trace (Thought/Action/Observation) instead of a silent decision. [[reflection-pattern]] adds one more pass of the same shape — perceive the draft, plan a critique, "act" by critiquing, observe the verdict — layered on top after the main loop finishes.

## Core mechanics

There's no API surface for "the loop" itself — it's a shape you implement, not a function you call. The mechanism, in the abstract:

```
state = initial_input
for i in range(MAX_ITERATIONS):
    decision = plan(state)              # delegated to the model
    if decision.is_final:
        return decision.output
    result = act(decision)              # your code executes this
    state = observe(state, result)      # result folded back into state
raise LoopExceeded()                    # cap hit — never loop forever
```

Three things are true of every concrete instance of this loop in the lab, regardless of which pattern it's dressed as:

- **The model never executes anything itself.** "Act" is always your code's job — the model's output is a request, not an action (this is the same "model requests, code decides" principle from [[tool-calling-fundamentals]]).
- **State accumulates across iterations.** Each loop pass sees everything gathered so far — messages list, thought/action/observation trace, whatever the pattern's state shape is.
- **The loop is always capped.** `max_iterations` isn't an optimization, it's the thing standing between a bounded system and one that can run (and bill) forever on a model that never converges to "done." Every one of A8, B2, and B3 in the lab enforces this independently.

## Sample code

There's no single lab cell that implements "the generic loop" in isolation — the lab goes straight to concrete instances ([[tool-calling-fundamentals]]'s `run_travel_agent`, [[react-pattern]]'s `run_react_agent`). The generic shape above is the abstraction those two share; see those pages for real, runnable code.

## Alternatives

Not really a library choice — every agent framework's core loop is a variation on this shape:

- **Hand-rolled loop** (this stage's labs) — full visibility into every iteration, most code to own.
- **LangChain's `AgentExecutor`** — wraps the same loop with `bind_tools` + tool execution baked in; less code, less visibility into what happens between iterations.
- **LangGraph's prebuilt ReAct agent** (`create_react_agent`, now superseded by `create_agent` in the `langchain` package) — the loop expressed as a graph with an LLM node and a tool node, gaining LangGraph's state/checkpointing machinery (stage 05's territory) at the cost of more moving parts.

## How this shows up in the capstone

Milestone 1 already had a miniature version of this loop — the structured-output repair cycle (generate → validate → fix, capped) is the same perceive/plan/act/observe shape, just without a tool call in the "act" step. Milestone 2's tool-enabled single agent is the first ShopSense component running the full loop with real tool execution in the "act" step — see [[capstone-milestone-map]]. Every later single-agent milestone (Policy RAG, Order-Actions, Escalation Reviewer) reuses this exact loop shape with a different toolset and stopping condition.

## Interview fire round

- **Q: What are the four steps of the agentic loop?**
  A: Perceive, plan, act, observe — repeated until the model signals it's done or an iteration cap is hit.
- **Q: What makes a loop "agentic" rather than just a `while` loop with an LLM call in it?**
  A: The plan step is delegated to the model — your code doesn't decide what happens next, the model's output does; your code only executes what's requested.
- **Q: Why is the structured-output repair loop from stage 03 not usually called "agentic"?**
  A: It has no tool/action step and its "plan" (retry with the error fed back) is fixed by your code, not chosen by the model — it's closer to a workflow than an agent, per [[workflow-vs-agent-autonomy-spectrum]].

## Production gotchas & best practices

- Lab gotcha, universal across every concrete instance: an uncapped agent loop is a real runaway risk (cost and, in a bad case, damage from repeated tool side effects) — `max_iterations` is not optional in any of A8, B2, or B3.
- Production practice: treat the iteration cap as one layer of a defense-in-depth strategy, not the only safeguard — pair it with per-tool idempotency (so a repeated call from a stuck loop is harmless) and circuit breakers on the tools themselves (briefly noted here, full treatment in [[circuit-breaker-pattern]] and [[retry-fallback-patterns]]).
- Production practice: log every iteration (state in, decision, action, result) — you cannot debug a loop you can't see the trace of, especially once it's non-deterministic by design.

## Course vs. production

The lab implements this loop by hand, once per pattern, so the shared shape is visible in the code rather than hidden behind a framework. In production, most teams reach for a framework's prebuilt loop (LangChain's `AgentExecutor`, LangGraph's agent node) once the hand-rolled version is understood — the framework version trades a bit of visibility for less loop-maintenance code, and adds structured state management ([[langgraph-state]]) that a hand-rolled `messages` list doesn't give you for free.

## Related
- **Builds on** — [[workflow-vs-agent-autonomy-spectrum]], [[architecture-of-an-agentic-system]] (this loop is the agent-loop layer in that reference diagram)
- **Feeds into** — [[tool-calling-fundamentals]], [[react-pattern]], [[reflection-pattern]]
- **Related pattern** — [[langgraph-agentic-patterns]] (the same loop expressed as a graph)

## Sources

**Lab sources**
- `lab-summaries/Day1-Session2-ToolCalling.md` (§ A8 tool-call loop, § B2 ReAct loop, § B3 reflection)
- `presentations/day1.md` (Day 1 · Session 2, Act 2 Q3 — "Thought → Action → Observation → Repeat")

**Web sources**
- [Anthropic — Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) — general agent-loop framing ("LLMs dynamically direct their own processes"), accessed 2026-08-20
