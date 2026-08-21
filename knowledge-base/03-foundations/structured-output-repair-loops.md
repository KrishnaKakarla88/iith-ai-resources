---
stage: "03-foundations"
tools: [pydantic, litellm]
tags: [structured-output, validation, repair-loop, json-mode]
last_verified: 2026-08-20
verified_against: "pydantic v2, litellm>=1.96.2"
---

# Structured output repair loops

Getting an LLM to reliably return data your code can trust: constrain the shape with JSON mode, validate the values with Pydantic, and feed validation failures back to the model when it gets it wrong.

## Prerequisites
- [[litellm-basics]]
- [[pydantic-basics]]

## In plain English

An LLM is trained to sound fluent, not to produce parseable data. Ask it for an invoice total and you might get `"the total comes to around $450, though the tax line is a bit unclear"` — perfectly reasonable prose, and useless to code that expects `total: float`. Two separate mechanisms close that gap, and it's worth keeping them distinct: **shape** and **value**.

JSON mode (`response_format={"type": "json_object"}`) constrains the model's *shape* — you get back a string that's guaranteed to parse as JSON. It does **not** check whether the values inside are sensible. A JSON-mode response can be shape-perfect and still wrong: `{"total": -450.00, "currency": "XYZ"}` parses fine and is nonsense. That's where Pydantic comes in — a schema with typed fields and, where needed, `@field_validator`s that check business rules ("total cannot be negative") catches what JSON mode structurally cannot.

When validation fails, the naive move is to just ask again and hope. The better move — the **repair loop** — is to hand the model its own mistake: take the `ValidationError` (which field, what rule, what value), fold it into a new prompt alongside the original text and the model's failed attempt, and re-call. This is the smallest possible agentic loop: generate → validate → observe the failure → act on it → repeat, capped at a small number of tries (2-3 is typical). Hit the cap without success, and the correct move is to fail loudly and route to a human — never let unvalidated data flow through silently.

## Core mechanics

| Step | What happens |
|---|---|
| Schema definition | A Pydantic `BaseModel` with typed, and where relevant optional (`\| None = None`), fields describing the target shape |
| `extract_raw()` | One completion call with `response_format={"type": "json_object"}` — shape-constrained, not value-checked |
| `validate_invoice()` | `json.loads()` then `Schema(**data)` inside `try/except (json.JSONDecodeError, ValidationError)` |
| Repair prompt | Contains: the validation error text, the original source text, and the model's previous (failed) JSON attempt |
| Retry cap | `max_retries` (2-3 typical) — bounds cost and stops an unfixable case from looping forever |
| Escalation on cap exhaustion | Flag for a human / fail loudly — never silently pass unvalidated data downstream |

## Sample code

Lab-sourced (Day 1 · Session 1 — Invoice → Pydantic parser):

```python
from pydantic import BaseModel, ValidationError
import json, litellm

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

def extract_raw(text: str) -> str:
    response = litellm.completion(
        model="groq/llama-3.1-8b-instant",
        messages=[{"role": "user", "content": EXTRACTION_PROMPT.format(text=text)}],
        response_format={"type": "json_object"},  # requires the word "json" in the prompt
    )
    return response.choices[0].message.content

def validate_invoice(raw: str) -> tuple[Invoice | None, str | None]:
    try:
        data = json.loads(raw)
        return Invoice(**data), None
    except (json.JSONDecodeError, ValidationError) as e:
        return None, str(e)

def parse_invoice(text: str, max_retries: int = 2) -> tuple[Invoice | None, list[str]]:
    errors = []
    raw = extract_raw(text)
    for attempt in range(max_retries + 1):
        invoice, error = validate_invoice(raw)
        if invoice is not None:
            return invoice, errors
        errors.append(error)
        if attempt < max_retries:
            repair_prompt = (
                f"Your last response failed validation: {error}\n"
                f"Original text: {text}\nPrevious attempt: {raw}\n"
                f"Return corrected JSON only."
            )
            raw = litellm.completion(
                model="groq/llama-3.1-8b-instant",
                messages=[{"role": "user", "content": repair_prompt}],
                response_format={"type": "json_object"},
            ).choices[0].message.content
    return None, errors  # cap exhausted — caller must flag for a human, not proceed
```

Run over a real batch with deliberate pacing to respect rate limits (see [[rate-limits-quotas-and-caching]]) — `time.sleep(2)` between records in the lab. Not every record is expected to succeed even after retries: 18 deliberately-messy sample invoices in the lab include some that should legitimately fail (two currencies in one line, missing totals) — the point is diagnosing *why*, not forcing 18/18.

## Alternatives

| Approach | Where it lives | Boring/simple alternative to the manual repair loop? |
|---|---|---|
| Manual extract→validate→repair loop (above) | Your own code, `json.loads` + Pydantic + a retry `for` loop | — |
| Instructor | `instructor` package, patches OpenAI/Anthropic/LiteLLM clients | No — same idea, packaged: automatic Pydantic-validated retry loop (3 attempts by default) with far less boilerplate; the safe default for most projects starting today[^struct-2026] |
| Outlines | `outlines` package, constrained decoding via FSMs | No — a fundamentally different mechanism: guarantees schema-valid output *during generation* (zero retries needed) rather than validating after the fact, but requires local/open-weight model access to constrain token-level sampling |
| Native provider structured output (OpenAI `response_format={"type": "json_schema", "strict": True}`, Anthropic tool-use forcing) | Provider API feature | No — token-level schema enforcement built into the API itself; still needs a value-level validation layer (Pydantic) on top since strict shape ≠ correct value |
| Regex/keyword extraction as a fallback | Plain Python | **Yes** — the boring option, but per `labs/production-notes.md`, this should only ever be a fallback path, never the primary source of truth — structured LLM extraction + schema validation stays primary |

## How this shows up in the capstone

Milestone 1 (provider-agnostic LLM client + structured intake) — the validated `Invoice`-style objects from this pattern *are* the structured-intake layer feeding the rest of the pipeline; see [[capstone-milestone-map]].

## Interview fire round

- **Q: A JSON-mode response parses successfully. Does that mean it's correct?**
  A: No — JSON mode only guarantees valid *shape*. It never checks whether the values inside make sense (a negative total, a made-up currency code); that's a separate validation layer's job.
- **Q: What exactly gets sent back to the model in a repair loop, and why not just re-ask the same question?**
  A: The actual validation error text (which field, what rule, what value), plus the original input and the model's previous failed attempt — giving the model its own specific mistake to correct is far more reliable than asking again with no new information.
- **Q: Why cap repair-loop retries instead of looping until it succeeds?**
  A: Cost and the fact that some inputs are legitimately unparseable — capping at 2-3 attempts and escalating to a human on exhaustion prevents both runaway spend and silently passing bad data downstream.

## Production gotchas & best practices

- Lab gotcha: JSON mode requires the literal word "json" to appear somewhere in the prompt, or Groq/OpenAI return a 400 — even when JSON is obviously the implied format.
- Lab gotcha: some inputs will legitimately fail validation even after every retry (bad math, genuinely ambiguous source text) — that's an expected outcome to surface, not a bug to chase to 100% pass rate.
- Production practice (from `labs/production-notes.md`): the extract→validate→repair *control flow* is worth sharing across call sites, but keep the actual LLM-calling function (`call_llm`) defined per-module rather than centralized — if tests `patch()` it by module path, centralizing it breaks every test that mocks the old location. Refactor the flow, not the mocked call site.
- Production practice (from `labs/production-notes.md`): never ask the model to reproduce a verbatim field it was given (like raw customer text) — inject it back via `setdefault` after parsing instead of trusting the model not to paraphrase it.
- Production practice (from `labs/production-notes.md`): on unparseable judge/extraction output, fail closed to a safe sentinel (e.g. `{"grounded": False, "score": 0}`), never let a parse failure crash the pipeline or silently pass.
- Production practice (day1.md framing): use structured output in *stages* rather than forcing an entire reasoning process into one rigid schema — let the model reason freely, then return the final answer in a strict schema; research (cited in the deck) suggests over-constraining reasoning into JSON hurts answer quality on genuinely hard problems.[^format-restrict]

## Course vs. production

The lab hand-rolls the extract→validate→repair loop to teach the mechanism explicitly. In production, most teams reach for a library like Instructor once the pattern is proven — it's the same loop, just with the retry/error-injection boilerplate factored out and battle-tested edge cases (partial JSON, streaming validation) already handled. The underlying discipline — shape via JSON mode/schema, value via Pydantic, capped repair, fail loud on exhaustion — stays identical either way.

## Related
- **Builds on** — [[litellm-basics]], [[pydantic-basics]]
- **Related** — [[rate-limits-quotas-and-caching]] (pacing repair-loop retries against provider limits)
- **Echoes in** — [[reflection-pattern]] (same generate→check→fix skeleton, applied to reasoning quality instead of JSON shape)

## Sources

**Lab sources**
- `lab-summaries/Day1-Session1-Foundations.md` (§ "Part 2 — Structured Output Parser")
- `labs/Day1 Session 1 - Foundations of Reliable AI Agents.ipynb`
- `labs/production-notes.md` (§ "Schema Validation")

**Deck sources**
- `presentations/day1.md` (Day 1 · Session 1 · Act 3 — "Making It Speak Data, Not Prose": shape-vs-value framing, the repair-loop trace example)

**Web sources**
- [Top 5 Structured Output Libraries for LLMs in 2026](https://dev.to/thedailyagent/top-5-structured-output-libraries-for-llms-in-2026-48g0) — Instructor/Outlines comparison, accessed 2026-08-20
- [Instructor documentation](https://python.useinstructor.com/) — automatic retry-loop behavior, accessed 2026-08-20

[^struct-2026]: dev.to/thedailyagent — 2026 structured-output library comparison; Instructor described as the safe default, Outlines for constrained-decoding/local-model use cases.
[^format-restrict]: Tam et al., "Let Me Speak Freely? A Study on the Impact of Format Restrictions on Performance of Large Language Models" (arxiv.org/abs/2408.02442), cited in `presentations/day1.md` Act 3 deep-dive.
