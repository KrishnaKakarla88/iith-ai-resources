---
stage: "03-foundations"
tools: [litellm, groq]
tags: [rate-limits, retry, caching, operations]
last_verified: 2026-08-20
verified_against: "litellm>=1.96.2, Groq API rate-limit headers"
---

# Rate limits, quotas, and caching

TPM/RPM limits, parsing a provider's own retry-after signal, and caching responses to avoid re-paying for calls you've already made — the operational reality of calling a real provider at any real volume.

## Prerequisites
- [[litellm-basics]]
- [[env-secrets-and-config]]

## In plain English

Every provider caps how much you can call it: **RPM** (requests per minute), **TPM** (tokens per minute), and often daily equivalents (RPD/TPD). Hit any one of them and you get an HTTP 429 back instead of a completion — this isn't rare in a course/free-tier setting, and it isn't rare in production either once traffic scales. The naive response — retry immediately, or retry after a guessed delay — makes things worse: if many requests all get rate-limited at once and all retry after the same fixed delay, they collide again on the retry, a **thundering herd**. The fix is **jittered exponential backoff**: wait longer after each failure, and add a small random offset so retries from different callers don't land on the exact same instant.

There's a better signal available than guessing, though: **Groq's 429 responses tell you exactly how long to wait** — a `retry-after` header (and body text like "Please try again in 3.86s"). Parsing that and sleeping exactly that long beats any backoff curve, because it's not a guess. Beyond reactive retry, the cheapest fix is often not needing to call the API again at all: **caching** identical or near-identical requests avoids re-paying for (and re-waiting on) a call whose answer you already have.

## Core mechanics

| Concept | What it means |
|---|---|
| RPM / TPM (/ RPD / TPD) | Requests-per-minute / tokens-per-minute (and daily variants) — hitting *any one* triggers a 429 |
| `x-ratelimit-*` headers | Present on every response (success or not) — remaining capacity, reset timing |
| `retry-after` header | Present **only** on a 429 — seconds to wait before retrying, straight from the provider |
| Jittered exponential backoff | `base_delay * 2^(attempt-1) + random.uniform(0, jitter)` — the fallback when no `retry-after` is given |
| Transient vs. permanent errors | Only retry `429`/`5xx`; a `400` (bad request) or `401` (bad auth) retrying won't fix it |
| Deliberate pacing | A flat `time.sleep(n)` between batch calls, chosen to stay under a known TPM ceiling — cheaper than reactive retry for predictable batch workloads |
| Response caching | Store a prior response keyed by (model + messages + params); skip the API call entirely on a cache hit |

## Sample code

Retry-after parsing (lab/production pattern, `labs/production-notes.md` § Retry/Resilience) — regex-extracting Groq's own signal instead of guessing:

```python
import re, time, random

def parse_retry_after(exc: Exception) -> float | None:
    match = re.search(r"try again in ([\d.]+)s", str(exc))
    return float(match.group(1)) if match else None

def call_with_retry(fn, *args, max_attempts=4, base_delay=1.0, **kwargs):
    for attempt in range(1, max_attempts + 1):
        try:
            return fn(*args, **kwargs)
        except Exception as exc:
            if "429" not in str(exc) and "5" not in str(getattr(exc, "status_code", "")):
                raise  # not transient — don't retry a permanent error
            if attempt == max_attempts:
                raise
            delay = parse_retry_after(exc) or (base_delay * 2 ** (attempt - 1) + random.uniform(0, 0.1))
            time.sleep(delay)
```

Deliberate pacing for a known batch workload (lab pattern — 18 sample invoices, Groq free-tier TPM):

```python
import time

for record in records:
    result = parse_invoice(record)
    time.sleep(2)  # stays under Groq's free-tier TPM by design, not reactive
```

Simple disk-based response caching (`functools`-level, before reaching for a dedicated library):

```python
import hashlib, json, os

CACHE_DIR = ".llm_cache"

def _cache_key(model: str, messages: list[dict]) -> str:
    payload = json.dumps({"model": model, "messages": messages}, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()

def cached_completion(model: str, messages: list[dict]):
    key = _cache_key(model, messages)
    path = os.path.join(CACHE_DIR, f"{key}.json")
    if os.path.exists(path):
        return json.load(open(path))
    response = litellm.completion(model=model, messages=messages)
    os.makedirs(CACHE_DIR, exist_ok=True)
    json.dump(response.model_dump(), open(path, "w"))
    return response
```

## Alternatives

| Approach | Where it lives | Boring/simple alternative? |
|---|---|---|
| Manual retry-after parsing + jittered backoff (above) | Your own code | — |
| LiteLLM built-in retry/fallback config | `litellm.completion(..., num_retries=..., fallbacks=[...])` or proxy `config.yaml` | No — same tier, less code to own, but less visibility into exactly what triggered a retry |
| Tenacity | `tenacity` package, general-purpose Python retry decorator | No — a well-tested general retry library (backoff, jitter, exception filtering) rather than something LLM-specific; doesn't know about `retry-after` semantics itself |
| GPTCache | `gptcache` package — semantic caching (embeds the query, matches similar past queries) | No — a heavier, more capable option than exact-match disk caching: catches near-duplicate queries too, at the cost of needing an embedding model + vector store in the loop; production hit rates commonly cited around 30-70% depending on traffic[^gptcache] |
| Exact-match disk cache (above) | Plain Python, `hashlib` + filesystem | **Yes** — the boring option; only catches byte-identical requests, but needs no extra infrastructure and is trivial to reason about |

## How this shows up in the capstone

Underpins every Milestone from 1 onward — any ShopSense agent making real Groq/Gemini calls needs to survive rate limits without crashing; directly referenced again when [[retry-fallback-patterns]] and [[circuit-breaker-pattern]] formalize this into the resilience layer wrapped around every agent; see [[capstone-milestone-map]].

## Interview fire round

- **Q: Why is retrying immediately after a 429 usually worse than waiting?**
  A: If many callers all retry at the same moment, they collide with the still-recovering rate limit again — a thundering herd. Jittered backoff (and honoring the provider's own `retry-after` signal when given) spreads retries out instead.
- **Q: Should your retry logic retry on every exception it sees?**
  A: No — only transient failures (429, 5xx). Retrying a 400 or 401 wastes time and calls; those need a code/config fix, not a retry.
- **Q: When does deliberate pacing (`time.sleep(n)` between calls) beat reactive retry?**
  A: For predictable batch workloads with a known volume and a known TPM ceiling — pacing calls to stay under the limit avoids triggering 429s in the first place, which is cheaper than recovering from them.

## Production gotchas & best practices

- Production gotcha (from `labs/production-notes.md`): **parse the provider's own retry-after signal** — Groq 429s include "Please try again in 3.86s" in the body; regex-extract and sleep that exact duration instead of guessing a backoff curve.
- Production gotcha (from `labs/production-notes.md`): distinguish transient from permanent errors before retrying (`"429" in str(exc)` as the lab's check) — retrying a permanent error (bad schema, bad auth) just burns time and quota for no benefit.
- Production practice (from `labs/production-notes.md`): jitter every backoff, and log every retry attempt — fixed-interval retries synchronize into a thundering herd, and un-logged retries make "it recovered on its own" indistinguishable from "it's silently failing intermittently."
- Production practice (from `labs/production-notes.md`): circuit breakers are a distinct, complementary mechanism to retry — retry assumes "probably transient," a circuit breaker assumes "probably broken" and stops calling entirely for a cooldown window once failures cross a threshold, scoped per-dependency (`time.monotonic()`-based) so one bad tool doesn't trip breakers for unrelated ones. Full detail in [[circuit-breaker-pattern]].
- Production practice (web-verified): every Groq response, success or not, carries `x-ratelimit-remaining-*` headers — proactively watching those (not just reacting to 429s) lets you throttle before you get rate-limited at all.[^groq-limits]

## Course vs. production

The lab handles rate limits with flat deliberate pacing (`time.sleep(2)` between batch calls) — sufficient for a fixed, known-size batch on a free tier. Production traffic is not a fixed batch — it's concurrent and unpredictable — so production systems need the fuller stack: retry-after parsing, jittered backoff, a circuit breaker per dependency, and (increasingly) response caching to reduce load in the first place rather than just surviving it. See [[retry-fallback-patterns]] and [[circuit-breaker-pattern]] for where this gets formalized into a reusable wrapper.

## Related
- **Builds on** — [[litellm-basics]], [[env-secrets-and-config]]
- **Feeds into** — [[retry-fallback-patterns]], [[circuit-breaker-pattern]]
- **Related** — [[structured-output-repair-loops]] (repair-loop retries need the same pacing discipline)

## Sources

**Lab sources**
- `labs/production-notes.md` (§ "Retry / Resilience")
- `lab-summaries/Day1-Session1-Foundations.md` (§ "Repair loop... `time.sleep(2)` between calls to stay under Groq free-tier rate limits")

**Web sources**
- [Groq — Rate Limits docs](https://console.groq.com/docs/rate-limits) — RPM/TPM/RPD/TPD, `retry-after` and `x-ratelimit-*` headers, accessed 2026-08-20
- [Fix Groq Rate Limit Errors in Production: Retry Strategies That Work](https://markaicode.com/errors/groq-rate-limit-exceeded-fix-production/) — retry-after-first, jittered-backoff-fallback strategy, accessed 2026-08-20
- [GPTCache (GitHub)](https://github.com/shiyu22/gptcache) — semantic caching approach and reported hit rates, accessed 2026-08-20

[^groq-limits]: console.groq.com/docs/rate-limits — official Groq rate-limit header reference.
[^gptcache]: github.com/shiyu22/gptcache and zilliz.com overview — semantic caching hit-rate figures, 2026.
