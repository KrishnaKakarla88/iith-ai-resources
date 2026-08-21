---
stage: "09-production-readiness"
tools: [pytest]
tags: [testing, mocking, unit-tests]
last_verified: 2026-08-20
verified_against: "no version-pinned test framework in this repo's pyproject.toml — pattern-level guidance"
---

# Testing agent code

A LangGraph node or a router function is still just a Python function — it takes state in and returns a dict out — which means it's unit-testable the same way any function is, as long as the LLM call inside it is mocked out. This is deliberately narrower than eval: it checks that your code does what you meant, not that your agent is good.

## Prerequisites
- [[langgraph-nodes]]
- [[decorators-and-wrappers]]

## In plain English

An agent's "correctness" splits into two different questions that get tested two different ways. **Does this code do what I intended?** — a node that's supposed to set `plan` and append to `log` actually does so, a router sends `"order"` requests down the order branch, a malformed LLM response gets caught and retried rather than crashing — that's a code-correctness question, answered with ordinary unit tests, fast and deterministic, run on every commit. **Is the agent's behavior actually good?** — does it retrieve the right policy, does it refuse when it should, does its final answer hold up against a judge or a human — that's a quality question, answered with eval against a golden dataset (see [[eval-driven-development-mindset]]), slower, often non-deterministic, and not something you want gating every commit. Testing agent code is the first kind: plain unit tests, with the LLM call replaced by something predictable, so a test asserts "given this state, this node produces that state" without ever making a real network call.

## Core mechanics

| Technique | What it's for |
|---|---|
| Call the node function directly with a hand-built state dict | A LangGraph node is `fn(state) -> dict` — no graph, checkpointer, or LLM needed to test its logic in isolation |
| `unittest.mock.patch` / `pytest-mock`'s `mocker.patch` | Replace the LLM-call function with a mock that returns a fixed value, so the test doesn't need network access or a live API key |
| `pytest`'s `monkeypatch` fixture | Built-in, no extra dependency — swaps an attribute/function for the test's duration and auto-reverts after; good for simple return-value substitution without needing call-count assertions |
| `pytest.fixture` for shared test state | Build a reusable seed state dict once, reuse it across many node tests |
| `pytest.mark.parametrize` | Run the same test logic across many input/expected-output pairs — useful for router functions with several branches |

Where to patch matters: patch the function at the module path the code under test actually imports it from, not where it's originally defined — a shared `call_llm` helper factored into a common module still gets mocked per-caller if each caller imported it into its own namespace (`labs/production-notes.md` calls this out explicitly: "refactor the flow, not the mocked call site").

## Sample code

Pattern adapted from `unittest.mock`/`pytest` conventions, applied to this repo's node shape (a LangGraph node is a plain function — see [[langgraph-nodes]]):

```python
from unittest.mock import patch

def test_researcher_node_returns_findings():
    state = {"plan": ["shipping_delay"], "findings": [], "already": set()}
    with patch("myagent.nodes.search_kb", return_value=[{"id": "d1", "text": "..."}]):
        result = researcher_node(state)
    assert result["findings"][0]["topic"] == "shipping_delay"
    assert "researcher: retrieved 1 record(s)" in result["log"][0]

def test_router_sends_order_requests_to_order_branch():
    state = {"intent": "order_status", "customer_ref": "c_123"}
    assert route(state) == "order_agent"

# monkeypatch variant — no context manager, auto-reverts after the test
def test_planner_falls_back_when_llm_reply_unparseable(monkeypatch):
    monkeypatch.setattr("myagent.nodes.call_llm", lambda messages: FakeMsg(content="nonsense"))
    state = {"brief": "shipping delays this week"}
    result = llm_planner_node(state)
    assert result["plan"], "must fall back to keyword match, never return an empty plan"
```

## How this shows up in the capstone

No milestone in [[capstone-milestone-map]] names this page directly — it's the discipline that makes every agent built from Milestone 1 onward safe to refactor: a node's unit tests should keep passing across a prompt change, a model swap, or a graph restructure, since they never depend on a real LLM call in the first place.

## Interview fire round

- **Q: Why not just eval the agent instead of unit-testing individual nodes?**
  A: Eval measures whether the agent's *behavior* is good against a golden dataset — slower, often non-deterministic, and answers a quality question. Unit tests measure whether a specific piece of code does what you intended — fast, deterministic, and catch a broken router or a crashing parser long before an eval run would even notice. See [[eval-driven-development-mindset]] for the eval side.
- **Q: Why does it matter *where* you patch a shared `call_llm` helper?**
  A: `patch`/`monkeypatch` replace a name in a specific module's namespace, not the function's original definition everywhere it's imported. If two callers each did `from llm_helpers import call_llm`, patching `llm_helpers.call_llm` won't affect a caller that already imported its own local reference — you have to patch the name where the code under test looks it up.

## Production gotchas & best practices

- Lab gotcha (`labs/production-notes.md`, § "Schema Validation"): a shared extract→validate→repair control flow was factored out into one function, but the actual `call_llm` invocation was deliberately kept local to each caller's module — because tests `patch()` it by module path, and centralizing the call site would have broken every existing test's patch target. Refactor the *flow*, not the mocked call site, without checking who's patching what first.
- Lab gotcha: central fail-fast env-var validation (`validate_required_env`) is called at entry points only, never at import time — tests import the module transitively without live API keys, and import-time validation would make every test file require real credentials just to collect.
- Lab gotcha: observability code (tracing, cost estimation) must never fail the primary operation under test — both are defensively wrapped/truncated so a broken tracing call doesn't turn a legitimate test failure into an unrelated `AttributeError` from the instrumentation layer.
- Production practice: keep the LLM-call boundary as a single, patchable seam per module — the harder it is to find where "the real call happens," the harder it is to mock cleanly, and the harder it is to spot a second code path that bypasses the seam entirely (see [[langfuse-tracing]]'s gotcha about a second SDK call path that skipped a centralized instrumentation wrapper — the same shape of bug shows up in testing: an untested path that quietly calls the LLM directly).

## Course vs. production

The labs' self-checks are closer to integration assertions than unit tests — they run the whole graph end-to-end with a deterministic stub team and assert on exact aggregate values (a fixed seed making `success_rate == 0.57` reproducible). That's appropriate for a graded notebook cell, but production test suites typically separate the two: fast, isolated unit tests per node/router (mocked LLM, no graph) that run on every commit, and a smaller set of slower integration tests that exercise the compiled graph end-to-end — closer to what the lab's self-checks already do — run less frequently (pre-merge, not on every save).

## Related
- **Builds on** — [[langgraph-nodes]], [[decorators-and-wrappers]]
- **Contrasts with** — [[eval-driven-development-mindset]] (code correctness vs. agent quality — see there for golden-set/regression framing)
- **Related pattern** — [[langfuse-tracing]] (both rely on a clean, single seam around the LLM call — one for mocking, one for instrumenting)

## Sources

**Lab sources**
- `labs/production-notes.md` (§ "Schema Validation" — `call_llm` module-path patching note; § "Error Handling" — entry-point-only validation, observability-must-not-fail-primary-operation)

**Web sources**
- [pytest — How to monkeypatch/mock modules and environments](https://docs.pytest.org/en/stable/how-to/monkeypatch.html) — built-in `monkeypatch` fixture, auto-revert behavior, accessed 2026-08-20
- No official docs page found specifically for "testing LangGraph nodes" as of 2026-08-20 — LangGraph's own docs focus on graph construction, not node unit-testing conventions; guidance here is the general Python mocking pattern (`unittest.mock`/`pytest`) applied to a node's plain-function shape, not a framework-provided testing utility
