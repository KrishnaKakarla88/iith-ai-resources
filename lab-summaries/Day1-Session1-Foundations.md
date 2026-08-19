# Day 1 · Session 1 — Foundations of Reliable AI Agents

Source: `labs/Day1 Session 1 - Foundations of Reliable AI Agents.ipynb`

Two parts: (1) raw LLM client vs LiteLLM comparison, (2) structured-output parser with a repair loop, tied to **Milestone 1**.

## Part 1 — Raw LLM Client + LiteLLM Comparison

**Core idea:** LLM APIs are stateless. "Memory" is just resending the full `messages` list every call. Once code sends that shape, swapping providers is just changing the `model=` string.

1. **Basic client** — call Groq SDK directly, then the same request via `OpenAI` SDK pointed at Groq's OpenAI-compatible endpoint (`base_url="https://api.groq.com/openai/v1"`). Same messages shape either way.
2. **Conversation history — `bare_chat(user_input, messages)`**: append user turn → call `client.chat.completions.create(...)` → pull `response.choices[0].message.content` → append assistant turn → return reply. History list is what "remembers", not the model.
3. **`SessionStore`** — dict of `session_id -> messages list`, so concurrent users don't cross-talk:
   ```python
   class SessionStore:
       def get_or_create(self, session_id): ...  # creates fresh list w/ system prompt if missing
       def chat(self, session_id, user_input): ...  # bare_chat scoped to one session
   ```
4. **`completion()` knobs** (via `litellm.completion`, ref: [LiteLLM input docs](https://docs.litellm.ai/docs/completion/input)):
   - **Instructions & Input** — `system` role sets standing behavior (cheapest lever to reshape output without touching code), `user`/`assistant` roles as usual.
   - **Generation hyperparams** — `temperature` (0=~deterministic), `max_tokens` (cap; hitting it → `finish_reason="length"` not `"stop"`), `stop` sequences, `seed` (best-effort reproducibility), also `stream`, `logprobs`, `top_p` (use instead of temperature, not both), `frequency_penalty`, `presence_penalty`.
   - **Reasoning** — some models (e.g. `groq/openai/gpt-oss-120b` with `reasoning_effort="low"`) return `resp.choices[0].message.reasoning` (scratch work) separate from `.content` (final answer). Field name varies by provider — check `message.model_dump()` rather than assuming.
   - **Output format** — plain text vs `response_format={"type": "json_object"}` (JSON mode — valid JSON, not schema-checked) vs `{"type": "json_schema", "json_schema": {..., "strict": True}}` (token-level schema enforcement). **Gotcha: JSON mode requires the literal word "json" in the messages or Groq/OpenAI return a 400**, even if the request obviously implies JSON.
   - **Prompt templating** — `string.Template` or a small `render_template(template, **vars)` helper that `.format()`s a list of `{role, content}` dicts, so the same template is reused with different variables instead of rebuilding messages by hand.
5. **`litellm_chat(model, user_input)`** — thin wrapper: build system+user messages, call `litellm.completion(model=model, messages=...)`, return `.choices[0].message.content`. Proves the same function works unmodified across `"groq/llama-3.1-8b-instant"` and (if key present) `"gpt-4o-mini"`.
6. **Cost/latency/token comparison** — for each model: time the call (`time.time()` before/after), count tokens with `litellm.token_counter(model=m, messages=msgs)` (input) and `token_counter(model=m, text=reply)` (output), collect into a `comparison` list of dicts (`model`, `latency_sec`, `input_tokens`, `output_tokens`).

## Part 2 — Structured Output Parser (Invoice → Pydantic)

**Core idea:** free-form LLM text is unreliable for downstream code. Define the target shape as a **Pydantic model**, ask for JSON (JSON mode), validate with Pydantic, and use a **repair loop** (feed the `ValidationError`/`JSONDecodeError` back to the model) when validation fails — far more reliable than one unchecked pass. 18 sample invoices (`data/sample_invoices.json`) are deliberately messy (typos, missing totals, mixed currencies, bad math on #10) so some *should* fail even after retries — the point is diagnosing which/why, not 18/18.

1. **Schema:**
   ```python
   class LineItem(BaseModel):
       description: str; quantity: float; unit_price: float
   class Invoice(BaseModel):
       invoice_number: str | None = None
       customer: str
       currency: str | None = None
       line_items: list[LineItem]
       total: float | None = None
   ```
   `| None = None` = optional field; missing it alone won't fail validation.
2. **`extract_raw(text)`** — one `completion(..., response_format={"type": "json_object"})` call with an `EXTRACTION_PROMPT.format(text=text)`, returns raw JSON string (parseable, not schema-checked yet).
3. **`validate_invoice(raw)`** — `json.loads` then `Invoice(**data)` inside `try/except (json.JSONDecodeError, ValidationError) as e`; returns `(invoice, None)` or `(None, str(e))`.
4. **Repair loop — `parse_invoice(text, max_retries=2)`**: on failure, appends `str(e)` to an `errors` list; if not the last attempt, builds a `repair_prompt` containing the error + original text + previous JSON attempt, re-calls the model in JSON mode, and retries. Runs over all 18 records with `time.sleep(2)` between calls to stay under Groq free-tier rate limits.
5. **Stretch goal:** bump `max_retries`, log which record IDs still fail, inspect their `errors` for a shared pattern (two currencies in one line, no total at all) and adjust prompt/schema accordingly.

## Gotchas called out in the notebook
- JSON mode needs the word "json" literally present in the prompt (Groq/OpenAI both enforce this).
- Reasoning trace field name varies by provider — inspect `model_dump()`.
- `temperature=0` is only *near*-deterministic, not guaranteed.
- Messy real-world text will legitimately fail validation even after retries — that's expected, not a bug to chase to 100%.

**Capstone tie-in:** satisfies Milestone 1 — provider-agnostic LLM client + structured intake; the validated `Invoice` objects are the structured-intake layer for the data pipeline.
