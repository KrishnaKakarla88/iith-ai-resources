--- LINKEDIN ---
Every LangGraph graph, however elaborate, is assembled from a small set of recurring shapes. Three are workflows — a human enumerated the paths, the model only fills content or picks among known branches. Two are agents — the model dynamically directs its own next step.

The workflows: a single call (one judgment, squeezed into a typed output), a prompt chain (fixed steps, the model fills fuzzy content in one), a router (one categorical decision, everything downstream fixed per category). The agents: a single tool-calling loop (the model decides which tool and when to stop — the sequence can't be enumerated in advance) and multi-agent fan-out/fan-in (independent subtasks running concurrently, combined at a merge node).

def should_continue(state):
    if state["steps"] >= MAX_TOOL_STEPS:  # mandatory cap
        return "end"
    return "continue" if last.tool_calls else "end"

The step cap on the tool-calling loop isn't a tuning knob — an uncapped loop is unbounded cost. The reducer requirement on fan-out isn't optional either: in a prompt chain exactly one node writes to any key at a time, so overwrite is fine; in fan-out, multiple nodes write concurrently in the same superstep, and without a reducer that's InvalidUpdateError, not a silent pick-one.

Production practice worth internalizing: default to NO on multi-agent, even when a problem could technically fan out. A second agent adds a lossy re-serialization boundary at every handoff — split only for a reason you can name.

The fastest way to pick the right shape: can you enumerate the valid paths right now? If yes, it's a workflow. If the next action genuinely depends on data you don't have until run time, it's an agent.

Which of the five shapes does your current graph actually need?

#AppliedAI #LangGraph #AIEngineering #LLM

--- INSTAGRAM ---
Every LangGraph graph is one of five shapes. 🧱

3 workflows: single call, prompt chain, router. 2 agents: tool-calling loop, fan-out/fan-in.

def should_continue(state):
    if state["steps"] >= MAX_TOOL_STEPS: return "end"

An uncapped loop is unbounded cost. Fan-out without a reducer is a crash, not a bug.

Full breakdown in the carousel.

#AppliedAI #LangGraph #AIEngineering #LLM #GenAI

--- VISUAL FORMAT ---
carousel — 7 slides
1. Title — "Every LangGraph Graph Is Built From Five Shapes"
2. The three workflows
3. The two agents
4. Sample code — the loop pattern every later shape builds on (code)
5. The reducer requirement
6. Production practice — default to NO on multi-agent
7. Takeaway — ask if you can enumerate the valid paths right now (closing question)
