--- LINKEDIN ---
A conditional edge replaces "always go to node B" with "call this function with the current state, and go wherever it says." The routing function is deliberately boring: it takes state, returns a string, and contains no model call. The lab's slogan for wiring this correctly: decide in a node, route in an edge.

Whatever fuzzy judgment needs to happen — did the draft pass review, which category is this ticket — happens inside a node and gets written to state as a plain value. The conditional edge that follows just reads that value. That keeps the routing function pure state -> str, unit-testable without a graph or a model call.

def route_after_checks(state):
    if state["issues"] and state["revision_count"] < MAX_REVISIONS:
        return "revise"
    return "approval"  # clean, or max revisions hit -> escalate, don't loop forever

The most common conditional-edge bug: if the routing function can return a value not present as a key in path_map, that's a run-time error, not a compile-time one — it can hide until a rare state combination triggers it.

Production practice: validate a routing function's return value against its legal keys before it reaches the edge. An LLM-produced category string is untrusted input to a router exactly like any other tool argument — fall back to a deterministic default rather than letting an unmapped value crash the run.

A loop-back conditional edge needs a state guard as the primary exit condition. LangGraph's recursion_limit is only the crash-instead-of-design backstop, not a substitute for one.

If your router returned a value nobody mapped, would your graph crash gracefully or hang?

#AppliedAI #LangGraph #AIEngineering #LLM

--- INSTAGRAM ---
"Always go to B" becomes "go wherever this function says." 🔀

Decide in a node, route in an edge. The routing function itself never calls a model — pure state -> str.

def route_after_checks(state):
    if state["issues"] and state["revision_count"] < MAX_REVISIONS:
        return "revise"
    return "approval"

An unmapped return value crashes at run time, not compile time.

Full mechanics in the carousel.

#AppliedAI #LangGraph #AIEngineering #LLM #GenAI

--- VISUAL FORMAT ---
carousel — 6 slides
1. Title — "\"Always Go To B\" Becomes \"Go Wherever This Function Says\""
2. The slogan — decide in a node, route in an edge
3. Sample code — the loop-guarded router behind every capped loop (code)
4. The common bug — an unmapped return value fails at run time
5. Production practice — validate the router's output before it reaches the edge
6. Takeaway — a state guard is the real exit condition (closing question)
