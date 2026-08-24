--- LINKEDIN ---
Asking for JSON isn't enforcing JSON

Prompting alone can request a shape — "respond with JSON matching this schema." It can't guarantee it. Reliability comes from pairing the request with an actual enforcement mechanism (JSON mode, schema-constrained decoding) and a validation layer on top, not from the wording alone.

The gotcha that catches people off guard: JSON mode requires the literal word "json" to appear somewhere in the prompt, or Groq/OpenAI return a 400 — even when JSON is the obviously implied format from the schema description alone.

The other lesson worth internalizing: forcing an entire reasoning process into a rigid output schema can hurt answer quality on genuinely hard problems. The staged pattern fixes this — let the model reason freely first (chain-of-thought), then constrain only the final answer to a strict schema.

Have you actually tested what happens when your prompt implies JSON but never says the word?

#AppliedAI #LLM #AIEngineering #PromptEngineering

--- INSTAGRAM ---
Asking for JSON isn't enforcing JSON ⚠️

Prompting alone can request a shape — it can't guarantee it.

The gotcha: JSON mode needs the literal word "json" in your prompt, or you get a 400.

Fix for hard problems: let it reason freely first, constrain only the final answer.

Have you tested what happens when your prompt implies JSON but never says it?

#AppliedAI #LLM #AIEngineering #GenAI #PromptEngineering

--- VISUAL FORMAT ---
single image
- kicker: Production Tradeoff
- headline: Asking For JSON Isn't Enforcing JSON
- 1. Asking Isn't Enforcing — Prompting alone can request a shape. It can't guarantee it.
- 2. The Gotcha — The word "json" must appear in the prompt or Groq/OpenAI return a 400.
- 3. The Staged Pattern — Let the model reason freely first, then constrain only the final answer.
- footer code: response_format={"type": "json_object"}  # needs "json" in prompt

--- SCHEDULE ---
Thu 9/10: IG 9am · LinkedIn 1pm
