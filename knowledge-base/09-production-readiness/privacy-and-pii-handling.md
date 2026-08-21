---
stage: "09-production-readiness"
tools: [presidio]
tags: [privacy, pii, redaction, logging]
last_verified: 2026-08-20
verified_against: "no version-pinned library in this repo — pattern-level, cites Microsoft Presidio as the reference OSS tool"
---

# Privacy & PII handling

Personally identifiable information doesn't only leak through tracing spans — it moves through every layer an agent touches: chat logs, memory stores, eval datasets, error messages, and the tool-call arguments themselves. Treat every one of those as a place PII can persist verbatim unless something explicitly strips it first.

## Prerequisites
- [[langfuse-tracing]]
- [[memory-types]]

## In plain English

A trace span is one place raw customer data can leak, but it's not the only one. The same "just log/store whatever's in scope" instinct that leaked chat text onto tracing spans (see [[langfuse-tracing]]'s PII-in-traces incident) shows up anywhere a system persists data: application logs (`print`/`logging` statements with a user's message in them), a memory store that's supposed to hold summaries but gets fed raw turns, an eval golden set built from real customer tickets, or an error message that echoes back the exact input that caused it. The fix pattern is the same everywhere: decide **at write time**, not read time, what's allowed to persist — because once PII is in a log file, a vector store, or a third-party memory service, "removing it later" means finding every copy, not editing one field.

## Core mechanics

| Concern | What to do about it |
|---|---|
| Redact before it leaves the process | Strip/replace PII in application memory, before the data is transmitted to any logging/tracing/storage backend — not after, in a dashboard or downstream job |
| Allowlist, not denylist, for what gets logged | An explicit list of fields safe to log (routing/audit fields: role, status, ids) beats trying to enumerate every PII-shaped field that might show up in a growing state dict |
| Hash, don't log raw, identifiers | A `user_id` used for filtering doesn't need to be human-readable in a log — hash it once, log the hash |
| Never ask an LLM to reproduce a verbatim field | If a field must appear unchanged in output (an order ID, a raw ticket ref), inject it programmatically after the LLM call rather than trusting the model not to alter, truncate, or hallucinate it |
| Label untrusted/recalled content in prompts | Content pulled from memory or retrieval can itself contain a past hallucination or a stored PII fragment — mark it as untrusted in the prompt, not as ground truth |
| Purge must clear every store, not just the primary one | A purge that clears a persistent store but leaves an in-process cache intact still serves the "deleted" data to the next request in that process |

## Sample code

Lab-sourced pattern (`labs/production-notes.md`, `parsing/ticket_parser.py` and the tracing-decorator incident) — never trust the model to echo a field verbatim, and redact known free-text keys before any blanket capture:

```python
# Never ask the LLM to reproduce a field verbatim — inject it after parsing instead.
parsed = extract_and_validate(llm_response)
parsed.setdefault("raw_text", original_ticket_text)  # injected, not model-generated

# Redact-keys allowlist applied before a tracing/logging decorator captures shared state —
# routing/audit fields stay visible, free-text fields are blanked first.
REDACT_KEYS = {"customer_message", "raw_chat_history", "draft"}

def safe_repr(state: dict) -> dict:
    return {k: ("[REDACTED]" if k in REDACT_KEYS else v) for k, v in state.items()}
```

Provider-documented pattern for structured redaction rather than a hand-maintained key list (from `presentations/day4.md`'s Act 1 example — attribute what's safe to keep, strip the rest at the SDK boundary):

```python
span.set_attributes({
    "session.id": sid,
    "user.id": hash(uid),          # hashed, not raw
    "model": "groq/llama-3.1-8b-instant",
})
# stored, not the raw prompt:
# prompt: "My card ending [REDACTED], DOB [REDACTED]..."
```

## Alternatives

| Approach | Where it lives | Boring/simple alternative? |
|---|---|---|
| [Microsoft Presidio](https://github.com/microsoft/presidio) (Analyzer + Anonymizer) | Open source, Microsoft | No — NER + regex + context-aware detection for common PII types (names, SSNs, card numbers, phone numbers); heavier than a hand-written key allowlist, but catches PII in free text you didn't anticipate a field for |
| Provider-side redaction (e.g. a logging pipeline's built-in scrubber, a cloud log service's PII filters) | Vendor-managed | No — convenient when already on that platform, but opaque about exactly what it catches and easy to over-trust as "handled" |
| Explicit redact-keys allowlist (as in the lab) | Plain Python, no dependency | **Yes** — the boring option; fast and auditable for known state-dict shapes, but only as good as the list — it won't catch PII that leaks through a field nobody flagged as free-text |

## How this shows up in the capstone

No milestone in [[capstone-milestone-map]] currently names this page directly — it applies wherever a milestone persists customer data: the tracing layer built in Milestone 7 ([[langfuse-tracing]]) and the per-customer memory layer are the two places this discipline has to be applied deliberately, not bolted on after a leak is found.

## Interview fire round

- **Q: Why redact "before it leaves the process" rather than in the dashboard/storage layer?**
  A: Once PII reaches a log/trace/storage backend, removing it means finding and scrubbing every copy — the dashboard, backups, any downstream consumer. Stripping it in application memory before transmission means it never exists in those places at all.
- **Q: Why is an allowlist safer than a denylist for what gets logged from a shared state object?**
  A: A denylist has to correctly anticipate every PII-shaped field, including ones added later by someone who doesn't know about the redaction rule. An allowlist inverts the failure mode — a newly added field is blocked by default until someone deliberately marks it safe, rather than leaked by default until someone notices.

## Production gotchas & best practices

- Lab gotcha (`labs/production-notes.md`): the tracing-decorator PII leak (see [[langfuse-tracing]]) generalizes beyond tracing — any code that captures "whatever's currently in scope" (a blanket `repr()`, a catch-all logger, a debug dump) is a PII leak waiting on the next field someone adds to shared state.
- Lab gotcha: `raw_text`/verbatim fields are never asked of the LLM — they're injected via `setdefault` after parsing, because a model asked to reproduce a field exactly can still alter, truncate, or paraphrase it, which is both a correctness bug and (if the field contains PII) a place the model's own generation could leak or fabricate sensitive-looking data.
- Lab gotcha: memory recall is labeled untrusted in the prompt (`SystemMessage` marked "never the source of a new tool argument") — recalled memory can itself carry PII or a past hallucination forward; treating it as ground truth compounds both risks.
- Lab gotcha: purge must clear the in-process cache, not just the persistent store — a long-lived process that caches then purges only the backing store keeps serving the "deleted" data to the next request until the process restarts.
- Production practice: apply sampling with an "always keep" override for anything security- or PII-relevant — per `presentations/day4.md`, sample healthy traffic down aggressively but keep 100% of errored/refused/over-threshold runs, since those are exactly the runs most likely to need review, and uniform sampling has no concept of "this one matters more."

## Course vs. production

The lab's PII leak was caught and fixed within one course project's tracing layer — a single decorator, a single fix. In production, PII handling is a cross-cutting concern that has to be audited across every layer independently (logs, traces, memory, eval datasets, error responses), because a fix in one layer says nothing about whether the same "capture whatever's in scope" pattern exists in another. Tools like Presidio exist precisely because a hand-maintained allowlist doesn't scale past a small, well-understood set of fields — production systems with free-text user input at multiple entry points typically need automated detection, not just discipline at known write sites.

## Related
- **Builds on** — [[langfuse-tracing]]
- **Related pattern** — [[memory-types]] (recalled memory as untrusted content), [[auth-and-multi-tenancy]] (identity/ownership data is its own PII-adjacent concern)

## Sources

**Lab sources**
- `labs/production-notes.md` (§ "Prompt Engineering" — the PII-in-traces incident; § "Schema Validation" — never trust the LLM to reproduce a verbatim field; § "Memory" — untrusted-memory labeling, purge-must-clear-cache)

**Web sources**
- [Microsoft Presidio (GitHub)](https://github.com/microsoft/presidio) — Analyzer/Anonymizer architecture, detection methods (regex, NER, context-aware), accessed 2026-08-20
- `presentations/day4.md` (Session 1, Act 1 Question 2) — tag-at-write-time / sample-but-keep-failures / redact-at-the-boundary framework, the hashed-user-id and redacted-prompt example — cited per course material
