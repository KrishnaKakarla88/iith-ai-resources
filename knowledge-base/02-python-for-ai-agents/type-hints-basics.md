---
stage: "02-python-for-ai-agents"
tools: [typing]
tags: [primer, type-hints, pydantic-prerequisite]
last_verified: 2026-08-20
verified_against: "Python 3.13 (this repo's pin: requires-python >=3.13)"
---

# Type hints basics

Type hints annotate what type a function's parameters, return value, and variables are expected to hold — Python never enforces them at runtime on its own, but every tool schema and structured-output model in this stack is built directly on top of them.

## Prerequisites
- [[functions-args-kwargs]]

## In plain English

Python is dynamically typed — nothing stops you from calling `add(1, "two")` and getting a runtime error three lines later instead of an error at the call site. Type hints (added in Python 3.5, PEP 484) let you write down what a function *expects* — `def add(a: int, b: int) -> int:` — without changing how the function actually runs. Python itself ignores the annotations at runtime; they exist for humans reading the code, and for tools (editors, type checkers like `mypy`/`pyright`, and — critically for this stack — libraries like Pydantic and FastMCP) that read them and act on them.

This "tools read the annotation and do something with it" pattern is exactly why type hints matter here: Pydantic turns a class's type-annotated fields into a validator; FastMCP turns a Python function's type-annotated parameters into the JSON schema an LLM reads to decide how to call it. The annotation isn't decoration — for these libraries, it *is* the contract (`lab-summaries/Day3-Session2-MultiAgentProtocols.md`, § B1: "Docstrings + type hints ARE the API contract").

## Core mechanics

| Hint | Meaning |
|---|---|
| `x: int` | variable annotation — `x` is expected to hold an `int` |
| `def f(a: int, b: str = "x") -> bool:` | parameter and return annotations |
| `list[int]`, `dict[str, float]` | built-in generics (Python 3.9+ — `List[int]` from `typing` is legacy) |
| `int \| None` | union type (Python 3.10+ `X \| Y` syntax; `Optional[int]` from `typing` is the older equivalent) |
| `Literal["a", "b", "c"]` | value restricted to one of an exact enumerated set — not just "a string" |
| `Any` | opt out of type checking for this spot |

`int | None = None` reads as "an int, or nothing, defaulting to nothing" — the standard shape for an optional field.

## Sample code

Lab-sourced (`lab-summaries/Day1-Session1-Foundations.md`, "Structured Output Parser" — see [[pydantic-basics]] for the full context): a field typed as optional versus one that's required is a real behavioral difference, not documentation:

```python
class LineItem(BaseModel):
    description: str
    quantity: float
    unit_price: float

class Invoice(BaseModel):
    invoice_number: str | None = None   # optional — missing field alone won't fail validation
    customer: str                        # required — missing this raises a ValidationError
    currency: str | None = None
    line_items: list[LineItem]
    total: float | None = None
```

And the `Literal` pattern from the guardrails layer (`lab-summaries/Day4-Session2-EvalGuardrails.md`, § "Schema check") — restricting a field to an exact closed set of values, which Python's plain `str` type cannot express:

```python
from typing import Literal

class AgentResponse(BaseModel):
    route: Literal["tool", "retrieval", "direct"]   # any other string fails validation
    final_answer: str
```

## How this shows up in the capstone

Type hints are the substrate every structured-output/tool-schema layer in this build sits on: M1's `Invoice` parsing model, the routing `AgentResponse.route: Literal[...]` guardrail, and FastMCP's auto-generated tool schemas (M6) all read parameter/field annotations to build their contract.

## Interview fire round

- **Q: Does Python enforce type hints at runtime?**
  A: No — CPython ignores them entirely at execution time. Enforcement comes from external tools: static type checkers (mypy, pyright) catch mismatches before running, and libraries like Pydantic add real runtime validation on top of the annotations.
- **Q: Why use `Literal["tool", "retrieval", "direct"]` instead of just `str` for a routing field?**
  A: `str` accepts any string — a hallucinated route like `"unknown"` would pass type-level scrutiny. `Literal` narrows the type to an exact enumerated set, so Pydantic can reject any value outside it at validation time, not downstream when the router tries to act on it.

## Production gotchas & best practices

- Docstrings and type hints together *are* the API contract for FastMCP tools — a vague docstring or a missing/loose type hint (`Any` where a `Literal` belongs) is called out as "a broken integration that raises no error, it just gets called wrongly or never" (`lab-summaries/Day3-Session2-MultiAgentProtocols.md`, § B1).
- Production practice: run a static type checker (mypy or pyright) in CI rather than relying on hints as documentation alone — hints without an enforcing tool are only as reliable as the last person who kept them in sync with the code ([mypy docs — Getting started](https://mypy.readthedocs.io/en/stable/getting_started.html), accessed 2026-08-20).
- Prefer the modern built-in generic syntax (`list[int]`, `X | None`) over the older `typing.List[int]`/`typing.Optional[X]` — both still work, but the built-in forms have been the recommended style since Python 3.9/3.10 and read more naturally ([Python 3 typing docs — Generic Alias Type](https://docs.python.org/3/library/typing.html#typing.Optional), accessed 2026-08-20; this repo pins `requires-python >=3.13`, well past both cutoffs).

## Course vs. production

The labs use type hints mainly to drive Pydantic validation and FastMCP schema generation — a functional dependency, not a discipline enforced independently. Production codebases typically also run a static type checker in CI as a separate quality gate, catching type mismatches before a Pydantic model ever runs at runtime.

## Related

- **Prerequisite for** — [[pydantic-basics]]
- **Feeds into** — [[structured-output-repair-loops]], [[mcp-fastmcp]]

## Sources

**Lab sources**
- `lab-summaries/Day1-Session1-Foundations.md` (§ "Part 2 — Structured Output Parser (Invoice → Pydantic)")
- `lab-summaries/Day4-Session2-EvalGuardrails.md` (§ "Guardrails layer")
- `lab-summaries/Day3-Session2-MultiAgentProtocols.md` (§ B1 — "Docstrings + type hints ARE the API contract")
- `labs/Day1 Session 1 - Foundations of Reliable AI Agents.ipynb`

**Web sources**
- [Python 3 typing module docs](https://docs.python.org/3/library/typing.html) — generic aliases, `Literal`, `Optional`/`X | None`, accessed 2026-08-20
- [PEP 484 — Type Hints](https://peps.python.org/pep-0484/) — original spec, non-enforcement at runtime, accessed 2026-08-20
- [mypy — Getting started](https://mypy.readthedocs.io/en/stable/getting_started.html) — static type checking as a CI gate, accessed 2026-08-20
