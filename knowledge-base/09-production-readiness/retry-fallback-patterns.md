---
stage: "09-production-readiness"
tools: [tenacity]
tags: [reliability, retry, fallback, resilience]
last_verified: 2026-08-20
verified_against: "tenacity 9.1.4 (this repo's lab pin, matches current PyPI release)"
---

# Retry & fallback patterns

Retrying a failed call and falling back to a degraded-but-honest response are two separate decisions — one recovers from transient failure, the other contains failure that didn't recover, and conflating them either burns retries on bad data or hides a real outage behind a silent success.

## Prerequisites
- [[decorators-and-wrappers]]
- [[rate-limits-quotas-and-caching]]

## In plain English

Any call to an external dependency — an LLM API, a vector DB, a tool — can fail, and most of those failures are transient: a dropped connection, a momentary timeout, a rate limit. Retrying with backoff gives the dependency time to recover instead of hammering it immediately again. But not every bad response is an exception — a call can "succeed" and return malformed data (a record missing a required field), and retrying that just re-rolls the same bad odds; it isn't a network problem, so a retry loop that only catches exceptions won't touch it. When retries are exhausted, or the response is malformed rather than an exception, a fallback path returns something usable — a cached snapshot, a canned message — instead of raising. The one rule that makes both patterns safe: **a system that silently degrades is worse than one that fails loudly.** A fallback is fine; a fallback nobody can see is not.

## Core mechanics

| tenacity API | Purpose |
|---|---|
| `@retry(...)` | Decorator that wraps a function in retry logic |
| `stop=stop_after_attempt(n)` | Caps total attempts — bounds cost and prevents an unbounded retry loop |
| `wait=wait_exponential(multiplier=..., max=...)` | Exponential backoff between attempts — waiting longer each time protects a struggling dependency from a retry storm |
| `wait=wait_random_exponential(min=..., max=...)` | Exponential backoff **with jitter** ("Full Jitter") — randomizes the wait within a widening window so retrying clients don't all retry in lockstep |
| `retry=retry_if_exception_type((ExcA, ExcB))` | Retry only on the exception types listed — everything else re-raises immediately |
| `reraise=True` | On final failure, re-raise the original exception instead of tenacity's own `RetryError` wrapper |

## Sample code

Lab-sourced (Day 4 · Session 1 — `labs/Day4 Session 1 - LangFuse Instrumentation, Failure Injection and Production Hardening.ipynb`, tenacity 9.1.4), against a seeded fault-injection harness (`FaultConfig(seed=42, fail_rate=0.2, timeout_rate=0.1, malformed_rate=0.1)`, baseline success rate 57% over 200 calls):

```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

def make_retrying_search_kb(flaky_fn):
    @retry(stop=stop_after_attempt(4),
           wait=wait_exponential(multiplier=0.01, max=0.2),
           retry=retry_if_exception_type((ConnectionError, TimeoutError)),  # never retries malformed data
           reraise=True)
    def retrying_search_kb(topic: str) -> list[dict]:
        return flaky_fn(topic)
    return retrying_search_kb

# result: success rate 57% -> 89.5%; malformed count barely moves (16 -> 20)
# — proves retries fix transience, not data quality
```

The fallback layer, wrapping the retrying call — on exhausted retries **or** malformed data, returns a canned record instead of raising, and always reports whether it degraded:

```python
FALLBACK_RECORD = {"id": "FALLBACK", "text": "fallback: live retrieval unavailable, using cached snapshot"}

def make_robust_search_kb(flaky_fn):
    retrying = make_retrying_search_kb(flaky_fn)
    def robust_search_kb(topic: str) -> tuple[list[dict], bool]:
        """Returns (records, used_fallback) — degradation is visible, never silent."""
        try:
            res = retrying(topic)
        except (ConnectionError, TimeoutError):
            return [dict(FALLBACK_RECORD, topic=topic)], True
        if not all("text" in r for r in res):
            return [dict(FALLBACK_RECORD, topic=topic)], True
        return res, False
    return robust_search_kb

# result: success rate -> 100% (never raises); 21/200 calls served from fallback
```

The `used_fallback` flag is the whole point — it's what a caller (or a [[langfuse-tracing]] span tag) checks to answer "what fraction of production traffic degraded to fallback this week" instead of that fraction being invisible.

## Alternatives

| Approach | Where it lives | Boring/simple alternative? |
|---|---|---|
| `tenacity` | Standalone Python package | — this repo's pin |
| [`backoff`](https://github.com/litl/backoff) | Standalone Python package, decorator-based | No — same tier, smaller API surface, no composable stop/wait objects |
| Provider SDK's own built-in retry (e.g. `litellm`'s internal retry/fallback routing) | Bundled in the LLM gateway library | No — convenient when already on that gateway, but opaque/less tunable than an explicit tenacity policy |
| Hand-rolled `for attempt in range(n): try/except: time.sleep(2**attempt)` | Plain Python, no dependency | **Yes** — the boring option; works for a single call site, loses composability (jitter, mixed stop conditions, per-exception-type policies) once you need more than one retry policy in the codebase |

## How this shows up in the capstone

Milestone 7 (observability + reliability hardening: retry + circuit breaker wrapping the single agent built in Milestone 2) — per [[capstone-milestone-map]].

## Interview fire round

- **Q: Why doesn't a retry loop fix a malformed response?**
  A: `retry_if_exception_type` only fires on raised exceptions — malformed data is a successful call that returned the wrong shape, not an exception. Retrying it just re-rolls the same bad odds; it has to be checked and handled as a separate case (fallback), not retried.
- **Q: Why exponential backoff instead of a fixed delay between retries?**
  A: A fixed delay across many clients synchronizes into a thundering herd — everyone retries at the same moment and re-overloads the dependency. Waiting longer each attempt (ideally with jitter) protects a struggling dependency instead of piling onto it.

## Production gotchas & best practices

- Lab gotcha: retry **only** on the two transient exception types (`ConnectionError`, `TimeoutError`) — retrying malformed data "fixes" nothing and just burns the retry budget on the same bad odds.
- Lab gotcha (`labs/production-notes.md`, `reliability/retry.py`): fixed-interval retries synchronize into a thundering herd across many clients; the fix is jittered exponential backoff (`base_delay * 2^(attempt-1) + random.uniform(0, 0.1)`), logged per attempt so silent recovery stays observable.
- Lab gotcha: parse the provider's own retry-after signal when it exists — Groq 429 responses include a literal "please try again in 3.86s" string; regex-extract and sleep exactly that long instead of guessing a backoff curve.
- Lab gotcha: distinguish transient vs. permanent failure *before* retrying — one lab module retries only on `"429" in str(exc)` and re-raises everything else immediately, rather than retrying a permanent error and wasting the whole budget.
- Lab gotcha: deliberate pacing can beat reactive retry — a batch-processing module uses a flat `time.sleep(2)` between records specifically to stay under a provider's TPM quota, rather than triggering rate-limit errors and retrying around them.
- Production practice: cap retries with `stop_after_attempt` and always pair retry with a fallback or a bounded failure path — an unbounded or generously-capped retry loop inside a larger agent loop (e.g. a LangGraph node with no supervisor-visit cap) risks compounding into the graph's own recursion limit; the lab's `MAX_SUPERVISOR_VISITS` loop guard exists specifically to force `"done"` before that hard limit crashes the run.

### Cost-anomaly triage and canary queries (per course material, `presentations/day4.md`)

When cost or error patterns shift with no exceptions thrown, the failure a retry/fallback layer needs to guard against is often invisible to the layer itself. The course's diagnostic order for "cost doubled, nothing errored": rule out traffic first, then check cache hit rate, then retrieval depth, then a silent retry loop, then session length — a retry policy that's firing far more often than expected (e.g. a dependency degrading but not fully failing) is itself one of the "usual suspects" worth watching as a rate, not just a pass/fail outcome. **Canary queries** — known-answer requests run continuously through the same retry/fallback path — are the course's recommended way to catch a fallback path that's silently become the default rather than the exception: if the fallback rate on canary traffic climbs, the real dependency has drifted even though every individual request still "succeeds" via fallback.

## Course vs. production

The lab measures retry/fallback effectiveness with **exact** success-rate numbers because the fault-injection seed is fixed — reproducible for grading, not "roughly better." In production there's no fixed seed; the same discipline shows up as tracking `used_fallback` rate as a live metric (ideally tagged on a [[langfuse-tracing]] span) rather than a one-time before/after table, and alerting on a rising fallback rate the same way you'd alert on rising latency.

## Related
- **Builds on** — [[decorators-and-wrappers]], [[rate-limits-quotas-and-caching]]
- **Feeds into** — [[circuit-breaker-pattern]]
- **Paired with** — [[langfuse-tracing]] (tag fallback/retry outcomes on spans to make degradation queryable)

## Sources

**Lab sources**
- `lab-summaries/Day4-Session1-LangfuseHardening.md` (§ "Lab B — Failure Injection & Production Hardening")
- `labs/Day4 Session 1 - LangFuse Instrumentation, Failure Injection and Production Hardening.ipynb` (cells: `make_retrying_search_kb`, `make_robust_search_kb`, B1-B3 self-checks)
- `labs/production-notes.md` (§ "Retry / Resilience")

**Web sources**
- [tenacity documentation](https://tenacity.readthedocs.io/) — wait/stop/retry strategy composition, accessed 2026-08-20
- [tenacity on PyPI](https://pypi.org/project/tenacity/) — latest release 9.1.4, matches this repo's lab pin exactly, accessed 2026-08-20
- [tenacity on GitHub](https://github.com/jd/tenacity) — `wait_exponential_jitter`/`wait_random_exponential` ("Full Jitter") behavior, accessed 2026-08-20
- `presentations/day4.md` (Session 1, Act 2 Question 4; Act 3 Question 2) — cost-anomaly triage order, canary queries, silent-failure detection — cited per course material
