--- LINKEDIN ---
An agent's "correctness" splits into two different questions that get tested two different ways. Does this code do what I intended — a node sets the right state field, a router sends the right requests down the right branch, a malformed response gets caught and retried rather than crashing — that's code-correctness, answered with ordinary unit tests, fast and deterministic, run on every commit. Is the agent's behavior actually good — that's a quality question, answered with eval against a golden dataset, slower and non-deterministic, not something you want gating every commit.

A LangGraph node is just fn(state) -> dict. No graph, checkpointer, or LLM needed to test its logic in isolation.

def test_researcher_node_returns_findings():
    state = {"plan": ["shipping_delay"], "findings": []}
    with patch("myagent.nodes.search_kb", return_value=[{"id": "d1"}]):
        result = researcher_node(state)
    assert result["findings"][0]["topic"] == "shipping_delay"

The gotcha that trips people up: patch/monkeypatch replace a name in a specific module's namespace, not the function's original definition everywhere it's imported. If two callers each imported their own local reference to call_llm, patching one won't affect the other — you have to patch the name where the code under test actually looks it up.

Production practice this forces: refactor the flow, not the mocked call site. A shared extract-validate-repair control flow got factored out into one function, but the actual call_llm invocation stayed local to each caller's module on purpose — centralizing it would have broken every existing test's patch target.

One more rule worth keeping: observability code must never fail the primary operation under test. Tracing and cost estimation are defensively wrapped so a broken tracing call doesn't turn a legitimate test failure into an unrelated AttributeError from the instrumentation layer.

Unit tests should keep passing across a prompt change, a model swap, or a graph restructure — since they never depend on a real LLM call in the first place. That's what makes an agent safe to refactor.

Could your node tests run right now with no API key set?

#AppliedAI #AIEngineering #LLM #LangGraph

--- INSTAGRAM ---
Code correctness and agent quality are different questions. Test them differently. 🧪

A LangGraph node is just fn(state) -> dict — mockable, testable, no graph needed.

def test_researcher_node_returns_findings():
    with patch("myagent.nodes.search_kb", return_value=[...]):
        result = researcher_node(state)

Gotcha: patch where it's imported, not where it's defined.

Full mechanics in the carousel.

#AppliedAI #AIEngineering #LLM #LangGraph #GenAI

--- VISUAL FORMAT ---
carousel — 6 slides
1. Title — "Two Different Questions, Two Different Tests"
2. The key insight — a LangGraph node is just fn(state) -> dict (code)
3. The gotcha — patch where it's imported, not where it's defined
4. Production practice — refactor the flow, not the mocked call site
5. Another rule — observability must never fail the primary operation
6. Takeaway — unit tests should survive a prompt change, a model swap (closing question)
