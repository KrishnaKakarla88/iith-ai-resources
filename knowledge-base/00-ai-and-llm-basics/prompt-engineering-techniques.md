---
stage: "00-ai-and-llm-basics"
tools: [litellm, pydantic]
tags: [primer, prompt-engineering, chain-of-thought, templates]
last_verified: 2026-08-21
verified_against: "litellm 1.96.x (this repo's pin)"
---

# Prompt engineering techniques

Prompt engineering is the concrete craft of *how you word and structure* a prompt — chain-of-thought, few-shot patterns, reusable templates, and asking for structured output — to reliably get the answer you actually want, rather than one that merely looks plausible.

## Prerequisites
- [[prompting-basics]]

## In plain English

Knowing that a prompt is a `system`/`user`/`assistant` message list ([[prompting-basics]]) doesn't tell you *what to write in it*. Prompt engineering is the layer above that: specific, repeatable techniques for wording a prompt so the model's output is more reliable, not just more likely-sounding.

Four techniques cover most of what actually moves the needle:

- **Chain-of-thought (CoT)** — asking the model to reason step by step *before* giving a final answer, rather than jumping straight to a conclusion. This exploits the fact that generation is sequential (see [[how-llms-generate-text]]): a model that "thinks out loud" first has that reasoning available as context when it produces the final token, and errors are often easier to catch when they're visible in the reasoning trace instead of buried in a one-line answer.
- **Few-shot patterns** ([[prompting-basics]]) — showing worked examples in the prompt so the model pattern-matches format and style, rather than inferring it purely from an instruction.
- **Templates** — a prompt with variable slots (`{text}`, `{errors}`), rendered with different data on each call instead of hand-building a new prompt string every time. This is what makes a repair loop or a batch pipeline maintainable: one template, reused, not dozens of near-duplicate ad hoc strings.
- **Structured-output prompting** — explicitly asking for a specific format (JSON, a fixed schema) and pairing it with a mechanism that actually enforces or checks that shape. Prompting alone can *ask* for JSON; it can't *guarantee* it — that's why this technique pairs with a code-side mechanism (JSON mode, then Pydantic validation) rather than trusting wording to be enough. The full mechanics of that pairing — plus what to do when validation fails — are covered in [[structured-output-repair-loops]]; this page is about the prompt side of asking for it.

## Core mechanics

| Technique | What it looks like | Why it helps |
|---|---|---|
| Chain-of-thought | "Think through this step by step, then give your final answer as: ..." | Makes intermediate reasoning explicit and inspectable, instead of hidden inside a single generation step |
| Few-shot examples | 2-3 worked input→output pairs before the real task | Shows the expected shape/style directly, rather than describing it in prose |
| Prompt template | A string/function with named slots, rendered per call with real data | One reviewable prompt, reused everywhere it's needed — no drift between near-duplicate hand-written prompts |
| Structured-output request | "Respond with JSON matching this exact shape: {...}" + the literal word "json" in the prompt | Sets up JSON mode / schema-constrained decoding to actually enforce the shape — the request alone is not enforcement |
| Repair prompt | Original input + the model's failed attempt + the specific error, asked to correct just that | Turns a validation failure into a targeted second try, not a blind retry (see [[structured-output-repair-loops]]) |

## Sample code

Lab-sourced (`labs/Day1 Session 1 - Foundations of Reliable AI Agents.ipynb`) — a template helper rendering a `{role, content}` message list from named variables, so the same template serves every record in a batch:

```python
from string import Template

EXTRACTION_TEMPLATE = Template(
    "Extract the invoice fields as JSON with keys "
    "invoice_number, customer, currency, line_items, total.\n"
    "Text:\n$text"
)

def render_template(template: Template, **vars) -> list[dict]:
    return [{"role": "user", "content": template.substitute(**vars)}]

messages = render_template(EXTRACTION_TEMPLATE, text=raw_invoice_text)
```

Chain-of-thought, worded as an explicit instruction rather than a separate API parameter (this course's models don't expose a dedicated "reasoning mode" toggle the way some frontier models do — see the note on `message.reasoning` in [[how-llms-generate-text]] for the cases that do):

```python
COT_PROMPT = (
    "Work through this step by step, showing your reasoning, "
    "then give your final answer on its own line as 'Answer: <value>'."
)
```

## How this shows up in the capstone

Milestone 1's `EXTRACTION_PROMPT` and repair-loop re-prompt are both rendered templates — the same technique from this page, reused across all 18 sample invoices rather than hand-written per record; see [[capstone-milestone-map]].

## Interview fire round

- **Q: Does asking a model to "return valid JSON" guarantee it will?**
  A: No — the request itself is just wording. Reliability comes from pairing it with an actual enforcement mechanism (JSON mode, schema-constrained decoding) and a validation layer on top, not from the phrasing alone.
- **Q: Why does chain-of-thought prompting tend to help on multi-step reasoning tasks specifically?**
  A: Generation is sequential and autoregressive — a model that writes out intermediate reasoning has that reasoning available as context for the tokens that follow, including the final answer, rather than having to arrive at the answer in one uninterrupted step.

## Production gotchas & best practices

- Lab gotcha: JSON mode requires the literal word "json" to appear somewhere in the prompt or Groq/OpenAI return a 400 — even when JSON is the obviously implied format from the schema description alone.
- Lab gotcha (`presentations/day1.md`, Act 3): forcing an entire reasoning process into a rigid output schema can hurt answer quality on genuinely hard problems — the recommended pattern is staged: let the model reason freely (chain-of-thought), then constrain only the final answer to a strict schema.
- Production practice: version-control prompt templates the same way you version code — a template edited inline in a notebook cell, with no diff history, is indistinguishable from a silent behavior change once it ships.

## Course vs. production

The lab writes prompt templates as plain Python `string.Template`/`.format()` calls, rendered inline in the notebook. Production prompt management typically externalizes templates (files, a prompt-management service, or at minimum a dedicated module) so they can be versioned, A/B tested, and audited independently of the code that calls them — the technique (render a template with variables) stays the same either way.

## Related
- **Builds on** — [[prompting-basics]]
- **Feeds into** — [[structured-output-repair-loops]], [[context-engineering]]
- **Related** — [[reflection-pattern]] (a second model call critiquing the first is a technique built from the same primitives)

## Sources

**Lab sources**
- `lab-summaries/Day1-Session1-Foundations.md` (§ "Part 1 — Raw LLM Client + LiteLLM Comparison", point 4 — "Prompt templating"; § "Part 2 — Structured Output Parser")
- `labs/Day1 Session 1 - Foundations of Reliable AI Agents.ipynb`

**Deck sources**
- `presentations/day1.md` (Session 1 · Act 3 — "Making It Speak Data, Not Prose")
