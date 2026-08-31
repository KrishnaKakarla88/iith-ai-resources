--- LINKEDIN ---
ReAct and reflection are the same four moves, wearing different clothes: perceive, plan, act, observe. Nothing here is an LLM invention — it's the same shape as an OODA loop (observe-orient-decide-act) or a basic control-system feedback loop. What's specific to an agentic loop is who owns step two: plan is handed to the model instead of hardcoded, so your code doesn't decide which tool gets called next — the model's output does.

for i in range(MAX_ITERATIONS): decision = plan(state) # delegated to the model; if decision.is_final: return decision.output; result = act(decision) # your code executes this; state = observe(state, result)

One mechanic worth internalizing: state accumulates across iterations — each pass sees everything gathered so far. "Act" stays your code's job throughout: the model's output is a request, never an action it actually took.

That's also why a repair loop from stage 03 isn't usually called "agentic" — no tool/action step, and its plan is fixed by your code, not chosen by the model.

Can you point to the exact line where your loop delegates the plan step to the model?

#AppliedAI #LLM #AIEngineering #LangGraph

--- INSTAGRAM ---
One loop under every agent pattern. 🔁

Perceive → Plan → Act → Observe — the same shape as an OODA loop, nothing LLM-specific about it.

What's agentic: plan is handed to the model, not hardcoded in your code.

for i in range(MAX_ITERATIONS): decision = plan(state) # delegated to the model

State accumulates every pass — full breakdown in the carousel.

Can you point to the line where your loop delegates plan to the model?

#AppliedAI #LLM #AIEngineering #GenAI #Developer

--- VISUAL FORMAT ---
carousel — 6 slides
1. Title — "One Loop Under Every Agent Pattern"
2. The four moves — perceive, plan, act, observe; OODA-loop parallel (diagram)
3. What makes it agentic — plan is delegated to the model
4. Core mechanics — the abstract shape (code)
5. Core mechanics — state accumulates across iterations
6. Takeaway — a repair loop isn't usually "agentic" (closing question)
