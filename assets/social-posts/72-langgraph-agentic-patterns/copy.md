--- LINKEDIN ---
ReAct, Planner-Executor, and Reflection are all loops. Every loop in this stack needs an explicit, state-based exit condition plus a hard cap as backstop — "until it is good" is not a termination condition.

ReAct is designed against a model calling the same tool forever with no new information. LangGraph's tools_condition prebuilt alone can loop indefinitely against a stubborn model:

def capped_tools_condition(state):
    if state["steps"] >= REACT_STEP_CAP:
        return "end"
    return tools_condition(state)

Planner-Executor produces the whole plan up front, then pops and runs one step per node visit. The known trap: a plan goes stale if executing step 2 invalidates step 3's assumptions. The production fix is replanning — an edge back to the planner after execution, at the cost of one extra model call per replan.

Reflection loops generate -> critique -> revise. The central caution: the critic shares the generator's blind spots — same model, same training, so self-critique catches sloppiness, not ignorance. If a deterministic checker exists for the property you care about, use that as the critic and keep the model only for repair.

def route_after_critique(state):
    if state["verdict"] == "PASS" or state["rounds"] >= MAX_REFLECT_ROUNDS:
        return "end"
    return "revise"

Why the critic sees less than the generator: it sees only the rules and the current draft, never the generator's own reasoning. That independence is the entire value of the separate node — seeing the chain of thought would make it rubber-stamp the draft instead of judging it.

Production gotcha across all four patterns: two layers of loop termination, not one. A state-based guard as the intentional exit, and recursion_limit only as the backstop that turns an undesigned loop into a crash instead of a silent hang.

Does your reflection loop have a deterministic checker available, or only a model critiquing itself?

#AppliedAI #LangGraph #AIEngineering #LLM

--- INSTAGRAM ---
"Until it is good" is not a termination condition. 🔁

ReAct: cap the tool loop or it runs forever. Planner-Executor: replan when step 2 breaks step 3's assumptions. Reflection: the critic shares the generator's blind spots — same model, same training.

def route_after_critique(state):
    if state["verdict"] == "PASS" or state["rounds"] >= MAX_REFLECT_ROUNDS: return "end"

Full mechanics in the carousel.

#AppliedAI #LangGraph #AIEngineering #LLM #GenAI

--- VISUAL FORMAT ---
carousel — 7 slides
1. Title — "\"Until It Is Good\" Is Not A Termination Condition"
2. ReAct — designed against calling the same tool forever (code)
3. Planner-Executor — one plan up front, one step per visit
4. Reflection — the critic shares the generator's blind spots (code)
5. Why the critic sees less
6. Production gotcha — two layers of loop termination, not one
7. Takeaway — every named pattern is a specialization of one shape (closing question)
