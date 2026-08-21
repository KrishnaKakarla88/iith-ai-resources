---
stage: "02-python-for-ai-agents"
tools: [pydantic]
tags: [primer, pydantic, structured-output, validation]
last_verified: 2026-08-20
verified_against: "Pydantic v2 (see repo transitive dep via litellm/langgraph; API shown is v2 BaseModel)"
---

# Pydantic basics

`BaseModel` turns a type-annotated class into a schema that validates data at runtime — the mechanism this entire stack relies on to turn unreliable free-form LLM output into something safe to hand to business logic.

## Prerequisites
- [[type-hints-basics]]

## In plain English

An LLM's raw output is text. Even when you ask for JSON, what comes back is a string that merely *looks like* JSON — nothing guarantees the fields are present, correctly typed, or within any sensible range until something actually checks. Pydantic is that check: you declare the shape you expect as a class (a `BaseModel` subclass with type-annotated fields), and constructing an instance of that class from raw data (`Invoice(**parsed_json)`) runs real validation — wrong type, missing required field, or a value outside a declared constraint all raise a `ValidationError` with a specific, readable reason, instead of a mystery `KeyError`/`TypeError` three functions downstream.

This is why structured LLM output and tool schemas in this stack are built as Pydantic models rather than raw dicts: a raw dict never complains until something tries to use a field that isn't there; a Pydantic model complains immediately, at the boundary, with a message specific enough to feed back into a repair prompt.

## Core mechanics

| Concept | What it does |
|---|---|
| `class X(BaseModel): field: Type` | declares a required field of the given type |
| `field: Type \| None = None` | declares an optional field with a default |
| `Field(gt=0)`, `Field(min_length=1)` | attaches a constraint beyond bare type (numeric bounds, string length, etc.) |
| `field_validator` | custom validation function for a field, runs after type coercion |
| `model_config = ConfigDict(extra="forbid")` | reject any field not declared on the model (fails loudly on unexpected/hallucinated keys) |
| `Model(**data)` | construct + validate in one step; raises `pydantic.ValidationError` on failure |
| `model_dump()` | instance → plain dict |
| `model_dump_json()` | instance → JSON string |

`Model(**data)` is the validation boundary — everything before it is untrusted; everything after it is a typed, checked object.

## Sample code

Lab-sourced (`lab-summaries/Day1-Session1-Foundations.md`, "Structured Output Parser") — schema, then the validate step that turns raw JSON text into a checked object or a specific error:

```python
from pydantic import BaseModel, ValidationError
import json

class LineItem(BaseModel):
    description: str
    quantity: float
    unit_price: float

class Invoice(BaseModel):
    invoice_number: str | None = None
    customer: str
    currency: str | None = None
    line_items: list[LineItem]
    total: float | None = None

def validate_invoice(raw: str) -> tuple[Invoice | None, str | None]:
    try:
        data = json.loads(raw)
        return Invoice(**data), None
    except (json.JSONDecodeError, ValidationError) as e:
        return None, str(e)   # feeds a repair prompt — see structured-output-repair-loops
```

The `Literal` + `extra="forbid"` guardrail pattern (`lab-summaries/Day4-Session2-EvalGuardrails.md`, § "Schema check"; `labs/production-notes.md` § "Pydantic" notes `extra="forbid"` as standard on every tool-arg schema in production hardening):

```python
from typing import Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict

class AgentResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")   # reject any field the router didn't declare

    route: Literal["tool", "retrieval", "direct"]
    final_answer: str = Field(min_length=1, max_length=2000)

    @field_validator("final_answer")
    @classmethod
    def not_a_placeholder(cls, v: str) -> str:
        if v.strip().lower() in {"", "n/a", "todo", "..."}:
            raise ValueError("placeholder answer, not a real response")
        return v
```

`min_length=1` alone would pass a literal `"..."` — the `field_validator` catches what the bare length constraint can't.

## How this shows up in the capstone

M1's invoice-parser structured-output lab and M8's guardrail layer both use Pydantic as the validation boundary between raw LLM text and business logic; `Literal["tool","retrieval","direct"]` constrains a router's output exactly the way a `route` field constrains M8's `AgentResponse`.

## Interview fire round

- **Q: Why not just use a plain dict and check keys manually with `if`/`get()`?**
  A: A dict never fails until code tries to use a missing/wrong-typed field, often far from where the bad data entered — the bug surfaces downstream and is harder to trace. A Pydantic model fails immediately at construction, with a specific error naming the field and reason, right at the boundary where untrusted data enters.
- **Q: What does `extra="forbid"` protect against that a bare type-checked model doesn't?**
  A: Without it, a model silently accepts and ignores any field it doesn't declare — an LLM hallucinating an extra key, or a subtly wrong key name, passes validation unnoticed. `extra="forbid"` turns an unexpected key into a `ValidationError` instead of silent data loss.
- **Q: Why does `min_length=1` alone not catch a placeholder answer like `"..."`?**
  A: `min_length` only checks the field isn't empty — `"..."` has length 3, so it passes. Catching content-level junk (placeholders, empty-but-nonzero-length strings) needs a `field_validator` that inspects the actual value, not just its length.

## Production gotchas & best practices

- `extra="forbid"` on every tool-arg schema, `Literal` enums, and `Field(gt=0)`-style numeric constraints are called out as standard practice specifically to stop unvalidated LLM args from reaching business logic (`labs/production-notes.md`, § "Pydantic").
- Never ask the LLM to reproduce a field verbatim that the caller already has (e.g. an order ID, raw ticket text) — inject it after parsing via `setdefault` instead of trusting the model to copy it correctly (`labs/production-notes.md`, § "Pydantic": "Never trust the LLM to reproduce a verbatim field").
- Current Pydantic (v2, a full Rust-core rewrite from v1) uses `model_`-prefixed methods (`model_dump()`, `model_validate()`) — v1's `.dict()`/`.parse_obj()` are deprecated aliases kept only for migration, not the current API to write new code against ([Pydantic Migration Guide](https://docs.pydantic.dev/latest/migration/), accessed 2026-08-20).

## Course vs. production

The lab's repair loop (feed a `ValidationError` back into the prompt, retry) is the same shape production systems use, but production typically adds a cap on repair attempts tied to cost/latency budgets and logs every validation failure as a signal (a recurring failure pattern on one field usually means the prompt or schema needs adjusting, not just more retries) — see [[structured-output-repair-loops]] for the full pattern.

## Related

- **Builds on** — [[type-hints-basics]]
- **Feeds into** — [[structured-output-repair-loops]], [[guardrails-injection-detection]], [[mcp-fastmcp]]

## Sources

**Lab sources**
- `lab-summaries/Day1-Session1-Foundations.md` (§ "Part 2 — Structured Output Parser (Invoice → Pydantic)")
- `lab-summaries/Day4-Session2-EvalGuardrails.md` (§ "Guardrails layer")
- `labs/production-notes.md` (§ "Pydantic")
- `labs/Day1 Session 1 - Foundations of Reliable AI Agents.ipynb`

**Web sources**
- [Pydantic docs — Models](https://docs.pydantic.dev/latest/concepts/models/) — BaseModel, field declaration, validation behavior, accessed 2026-08-20
- [Pydantic docs — Validators](https://docs.pydantic.dev/latest/concepts/validators/) — `field_validator` usage, accessed 2026-08-20
- [Pydantic Migration Guide (v1 → v2)](https://docs.pydantic.dev/latest/migration/) — `model_`-prefixed method naming, `extra="forbid"` config, accessed 2026-08-20
