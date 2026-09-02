import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "Two Different Questions, Two Different Tests",
      ["Does this code do what I intended — a code-correctness question, unit tests, fast, deterministic. Is the agent's behavior good — a quality question, eval against a golden dataset, slower, non-deterministic."])

slide(p("slide-02.png"), 2, 6, "The Key Insight", "A LangGraph Node Is Just fn(state) -> dict",
      ["No graph, checkpointer, or LLM needed to test its logic in isolation — mock the LLM call out and assert on the return value like any other function."],
      code="def test_researcher_node_returns_findings():\n    state = {\"plan\": [\"shipping_delay\"], \"findings\": []}\n    with patch(\"myagent.nodes.search_kb\", return_value=[{\"id\": \"d1\"}]):\n        result = researcher_node(state)\n    assert result[\"findings\"][0][\"topic\"] == \"shipping_delay\"")

slide(p("slide-03.png"), 3, 6, "The Gotcha", "Patch Where It's Imported, Not Where It's Defined",
      ["patch/monkeypatch replace a name in a specific module's namespace. If two callers each did their own import of call_llm, patching one doesn't touch the other."])

slide(p("slide-04.png"), 4, 6, "Production Practice", "Refactor The Flow, Not The Mocked Call Site",
      ["A shared extract-validate-repair flow got factored out, but call_llm stayed local to each caller's module on purpose — centralizing it would have broken every existing test's patch target."])

slide(p("slide-05.png"), 5, 6, "Another Rule", "Observability Must Never Fail The Primary Operation Under Test",
      ["Tracing and cost estimation are defensively wrapped so a broken tracing call doesn't turn a real test failure into an unrelated AttributeError from the instrumentation layer."])

slide(p("slide-06.png"), 6, 6, "Takeaway", "Unit Tests Should Survive A Prompt Change, A Model Swap, A Graph Restructure",
      ["Since they never depend on a real LLM call in the first place — that's what makes an agent safe to refactor."],
      closing_q="Could your node tests run right now with no API key set?")

print("done: 91")
