--- LINKEDIN ---
A LangGraph node is just a Python function — no base class, no decorator, no special registration beyond builder.add_node("name", fn). That plainness is deliberate: because a node is a regular callable, you can call it directly with a hand-built state dict in a unit test, without building a graph, wiring a checkpointer, or running anything through the graph engine.

Nodes fall into two kinds, and keeping them separate is the central discipline: deterministic nodes (a policy check, a regex extraction, an arithmetic calculation) and the one node that calls a model. A rule expressible in code shouldn't be paid for in model variance. "Let the model produce, let deterministic code decide" — an LLM node can produce a new draft, a deterministic node still decides whether it passes.

def check_document(state):
    issues = run_policy_checks(state["draft"])
    return {"issues": issues, "issue_log": issues}

# unit-testable without a graph, a model, or a checkpointer:
result = check_document({"draft": "...", "issues": [], "issue_log": [], "revision_count": 0})

The failure case worth handling explicitly: a model-call wrapper can return None on failure by design, so every LLM node needs an explicit fallback — a node that doesn't handle a failed call silently propagates None into state.

Production practice: because nodes are plain functions, mock the model call, not the node — keeping the LLM-call wrapper at each caller's own module namespace is what lets patch() target it per-module, even after refactoring shared control flow out. And force-set identity/authorization-critical fields inside the node itself — never trust an upstream LLM tool-call argument for them.

Could you unit-test your busiest node right now, with nothing but a dict?

#AppliedAI #LangGraph #AIEngineering #LLM

--- INSTAGRAM ---
A LangGraph node is just a function. No base class, no decorator. 🔧

Two kinds: deterministic (cheap, testable) and the one node that calls a model. Rule: let the model produce, let deterministic code decide.

def check_document(state):
    issues = run_policy_checks(state["draft"])
    return {"issues": issues, "issue_log": issues}

Testable with a bare dict — no graph needed.

Full breakdown in the carousel.

#AppliedAI #LangGraph #AIEngineering #LLM #GenAI

--- VISUAL FORMAT ---
carousel — 6 slides
1. Title — "A Node Is Just A Function — No Base Class, No Decorator"
2. Two kinds of node — deterministic vs the one that calls a model
3. Sample code — both callable directly, no graph required (code)
4. The failure case — a failed model call returns None by design
5. Production practice — mock the model call, not the node
6. Takeaway — force-set identity fields inside the node itself (closing question)
