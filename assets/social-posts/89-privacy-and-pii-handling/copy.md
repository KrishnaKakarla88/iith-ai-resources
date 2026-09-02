--- LINKEDIN ---
PII doesn't only leak through tracing spans. It moves through every layer an agent touches — chat logs, memory stores, eval datasets, error messages, tool-call arguments. Any of them can persist raw customer data verbatim unless something explicitly strips it first.

The fix pattern is the same everywhere: decide at write time, not read time, what's allowed to persist. Once PII is in a log file, a vector store, or a third-party memory service, "removing it later" means finding every copy, not editing one field.

REDACT_KEYS = {"customer_message", "raw_chat_history", "draft"}

def safe_repr(state):
    return {k: ("[REDACTED]" if k in REDACT_KEYS else v) for k, v in state.items()}

An allowlist beats a denylist here. A denylist has to correctly anticipate every PII-shaped field, including ones added later by someone who doesn't know about the redaction rule. An allowlist inverts the failure mode — a newly added field is blocked by default until someone deliberately marks it safe.

Never ask an LLM to reproduce a field verbatim:
parsed = extract_and_validate(llm_response)
parsed.setdefault("raw_text", original_ticket_text)  # injected, not model-generated
A model asked to echo an order ID or a raw ticket reference exactly can still alter, truncate, or hallucinate it — a correctness bug and a PII risk at the same time.

The cache gotcha worth knowing: a purge that clears only the persistent store but leaves an in-process cache intact keeps serving "deleted" data to the next request until the process restarts.

One more cheap habit: hash identifiers instead of logging them raw. A user_id used for filtering doesn't need to be human-readable in a log.

Would a hand-maintained allowlist actually catch every free-text field in your system?

#AppliedAI #AIEngineering #LLM #LangGraph

--- INSTAGRAM ---
PII doesn't only leak through tracing. It leaks everywhere data persists. 🔒

Decide at write time what's allowed to persist — not read time, when it's already copied to backups and downstream jobs.

REDACT_KEYS = {"customer_message", "raw_chat_history"}

Never ask an LLM to echo a field verbatim — inject it programmatically after the call instead.

Full mechanics in the carousel.

#AppliedAI #AIEngineering #LLM #LangGraph #GenAI

--- VISUAL FORMAT ---
carousel — 6 slides
1. Title — "PII Doesn't Only Leak Through Tracing Spans"
2. The fix pattern — decide at write time, never at read time
3. Sample code — allowlist, not denylist (code)
4. Never trust the model to reproduce a field — inject it programmatically (code)
5. The cache gotcha — a purge that misses the in-process cache isn't a purge
6. Takeaway — hash identifiers, don't log them raw (closing question)
