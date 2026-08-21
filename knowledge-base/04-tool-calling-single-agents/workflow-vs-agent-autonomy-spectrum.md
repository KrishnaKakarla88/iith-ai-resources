---
stage: "04-tool-calling-single-agents"
tools: []
tags: [agent-design, workflows, autonomy, architecture]
last_verified: 2026-08-20
verified_against: "Anthropic 'Building Effective Agents' (engineering blog, current as of 2026-08-20)"
---

# Workflow vs agent: the autonomy spectrum

Fixed workflow vs autonomous agent is the course's central thesis — don't deploy an agent where a workflow would do — and it's the lens every pattern in this stage gets evaluated through.

## Prerequisites
- [[architecture-of-an-agentic-system]]
- [[structured-output-repair-loops]]

## In plain English

Every "AI does a multi-step task" system sits somewhere on a spectrum between two poles. At one end, a **workflow**: your code decides the steps and their order in advance, and each step calls an LLM to do one well-defined piece of work — the control flow is a fixed graph you wrote. At the other end, an **agent**: the model itself decides what to do next, in what order, using which tools, based on what it observes as it goes — the control flow lives inside the model's own reasoning, call by call.

Neither is "more advanced" than the other. A workflow is predictable, cheap, and easy to test — you can enumerate every path it can take, because you wrote them. An agent is flexible and can handle problems you didn't fully anticipate — but that flexibility means you can't fully enumerate its paths, only bound them (iteration caps, tool allowlists, guardrails). The mistake this stage keeps warning against is reaching for agent autonomy by default. If a task's steps are actually fixed — validate input, look something up, format an answer — a workflow does that job with less cost, less latency, and dramatically less surface area for something to go wrong. Autonomy is a cost you pay for genuine unpredictability in the task, not a feature you add because agents are the interesting part of the course.

## Core mechanics

There's no single knob here — it's a spectrum, and most real systems sit somewhere in the middle rather than at either pole:

| Point on the spectrum | Who decides the next step | Example shape |
|---|---|---|
| Fixed workflow | Your code, ahead of time | `validate() → retrieve() → format()`, one LLM call per stage, no branching decided by the model |
| Workflow with routing | Your code picks a branch based on classifying the input | Prompt chaining / routing: one LLM call classifies intent, code picks which fixed sub-path runs next |
| Single tool-calling agent | The model, but bounded by a small fixed toolset and an iteration cap | This stage: [[tool-calling-fundamentals]], [[react-pattern]] — model picks *which* tool and *when to stop*, your code still owns execution and the ceiling |
| Multi-agent orchestration | Multiple models, each with their own bounded autonomy, coordinated by a planner | Stage 07's territory — previewed below |

The question to ask before building anything: **does this task have a fixed, enumerable set of steps?** If yes, a workflow is strictly better — same outcome, less risk. If the steps genuinely depend on what's discovered mid-task (search returns something unexpected, a tool fails and a different one is needed), that's the actual signal for agent autonomy, not "this sounds like it needs AI."

## Sample code

There's no single "sample" for a spectrum decision — it's a design call made before code, not a library call. But the shape of each pole is worth contrasting directly:

```python
# Workflow: code owns every step, in fixed order
def handle_return_request(ticket: dict) -> str:
    order = lookup_order(ticket["order_id"])          # step 1, fixed
    policy = retrieve_policy(order["category"])        # step 2, fixed
    return format_response(order, policy)               # step 3, fixed
    # the model (if used inside format_response) never decides *what* runs next

# Agent: the model decides which tool to call and when to stop
def handle_return_request_agentic(ticket: dict) -> str:
    messages = [{"role": "user", "content": ticket["text"]}]
    for _ in range(MAX_ITERATIONS):                     # see tool-calling-fundamentals
        response = model.invoke(messages)
        if not response.tool_calls:
            return response.content
        # model chose which tool(s) to call and with what args — code still executes them
        messages = run_requested_tools(response, messages)
```

The workflow version has no cap because it has no open-ended loop to bound. The agent version needs `MAX_ITERATIONS` precisely because the model, not your code, is choosing the path.

## Alternatives

This is a design framework, not a library — the "alternatives" are the other points on the spectrum itself, each covered by its own page:

- **Prompt chaining / routing** (fixed workflow with an LLM-driven branch) — covered conceptually here, not a separate page in this stage.
- **Single-agent tool-calling loop** — [[tool-calling-fundamentals]], [[react-pattern]] — bounded autonomy, one model.
- **Multi-agent orchestration** (planner + worker agents, each independently bounded) — stage 07's [[supervisor-worker-teams]], [[agent-topologies]]; day1.md's "300 sub-agents" framing is the extreme end of this same spectrum, not a different idea.

## How this shows up in the capstone

Milestone 1 already made this call implicitly — the structured-intake repair loop from stage 03 is a workflow (generate → validate → fix, capped), not an agent, because its steps are fixed. Milestone 2 (tool-enabled single agent, this stage) is the first ShopSense component that crosses into agent territory: Triage and later agents get to choose which tool to call, not just execute a fixed pipeline. Later milestones (M5 orchestrated LangGraph workflow, M6 multi-agent orchestration) push further along the spectrum — see [[capstone-milestone-map]]. Each new agent in the build order should be a deliberate choice to spend autonomy, not a default.

## Interview fire round

- **Q: When should you use a workflow instead of an agent?**
  A: When the steps and their order are knowable in advance — a workflow gets the same outcome with less cost, lower latency, and a fully enumerable set of execution paths to test.
- **Q: Is an agent always "better" because it's more flexible?**
  A: No — flexibility is a cost (unpredictable paths, harder to bound, more tokens/latency), justified only when the task's steps genuinely can't be fixed ahead of time.
- **Q: What's the actual signal that a task needs agent autonomy?**
  A: The next step depends on something discovered mid-task (an unexpected tool result, a failure requiring a different approach) — not "this task involves an LLM" or "this feels complex."

## Production gotchas & best practices

- Per course material (`presentations/day1.md`): "Agent = model + harness" — the harness (loop, executor, retries, permissions, context management) is what makes an agent reliable, not the model alone; the same model in two different harnesses behaves very differently. This reframes the workflow-vs-agent choice as also a harness-design choice, not just a prompting choice.
- Production practice: start with the simplest structure that solves the task and add agentic complexity only when evals show the simpler version failing — this is Anthropic's explicit recommendation, not just a course simplification ([Anthropic, "Building Effective Agents"](https://www.anthropic.com/engineering/building-effective-agents), accessed 2026-08-20).
- Gotcha: "agent" gets used loosely in marketing and even in some docs to mean "has an LLM call in it" — when scoping a component, ask the concrete question (fixed steps vs. model-decided steps) rather than trusting the label.

## Course vs. production

The lab treats this as a framing lesson before any code — the actual notebooks (tool-call loop, ReAct loop) are both already agentic, because the course's job is to teach the agent patterns. In production, the harder and more common decision is the opposite: recognizing when a proposed feature *doesn't* need agent autonomy at all, and building the cheaper workflow instead — Anthropic's own guidance explicitly frames most of its five patterns (prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer) as workflows, with true open-ended agents reserved for genuinely unpredictable tasks.

## Related
- **Builds on** — [[architecture-of-an-agentic-system]]
- **Feeds into** — [[agentic-loop-fundamentals]], [[tool-calling-fundamentals]], [[react-pattern]]
- **Contrasts with** — [[agent-topologies]], [[supervisor-worker-teams]] (multi-agent end of the same spectrum)

## Sources

**Lab sources**
- `presentations/day1.md` (Day 1 · Session 2 finale — "Agent = Model + Harness"; Session 1 finale — "What is an Agent?")
- `lab-summaries/Day1-Session2-ToolCalling.md`

**Web sources**
- [Anthropic — Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) — workflows-vs-agents framing, five workflow patterns, "find the simplest solution" guidance, accessed 2026-08-20
