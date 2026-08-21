---
stage: "09-production-readiness"
tools: [pybreaker]
tags: [reliability, circuit-breaker, chaos-engineering]
last_verified: 2026-08-20
verified_against: "pattern demonstrated with a hand-rolled breaker in labs/Day4 Session 1 notebook; pybreaker 1.4.1 as the production library reference"
---

# Circuit breaker pattern

A circuit breaker stops calling a dependency that's already down, instead of retrying against it forever — the pattern that protects a struggling service from a thundering herd of retries, and protects your own system from paying the full retry cost on every request during a sustained outage.

## Prerequisites
- [[retry-fallback-patterns]]
- [[decorators-and-wrappers]]

## In plain English

Retries help with a blip — a connection that drops once and recovers. They actively hurt during a sustained outage: every request still pays the full retry budget (multiple attempts, each with backoff) against a dependency that has no chance of answering, adding latency without adding any success. A circuit breaker tracks consecutive failures and, past a threshold, stops even trying — it "opens" and short-circuits every call immediately, no network attempt at all, until enough time has passed to test recovery. This is a general distributed-systems pattern (Netflix Hystrix / resilience4j popularized it), not LLM-specific — it applies to any flaky dependency a tool call or agent might reach: a vector DB, a payment API, a downstream microservice.

## Core mechanics

Three states, one direction of travel per failure, and exactly one way back:

| State | Behavior |
|---|---|
| `closed` | Normal operation — calls go through; failures are counted |
| `open` | Every call short-circuits immediately (no network attempt) once `failure_threshold` consecutive failures are hit |
| `half_open` | After `reset_timeout` elapses, exactly **one** trial call is allowed, to test recovery without guessing |

Rules that make the state machine correct: any failure while `half_open` re-opens the circuit immediately (a "recovered" breaker that allows multiple trial calls in `half_open` risks hammering a still-broken dependency); a success while `closed` resets the failure counter to zero. `failure_threshold`/`reset_timeout` are tuned per dependency in production — too low and normal blips trip the breaker; too high and you keep hammering a dead service anyway.

## Sample code

Lab-sourced (Day 4 · Session 1 — `labs/Day4 Session 1 - LangFuse Instrumentation, Failure Injection and Production Hardening.ipynb`), a minimal breaker built from scratch to show the state machine explicitly (`time.monotonic()` avoids clock-adjustment bugs — see `labs/production-notes.md`):

```python
import time

class CircuitOpenError(Exception):
    """Raised when the breaker is open and short-circuits a call."""

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, reset_timeout: float = 10.0):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.state = "closed"          # closed -> open -> half_open -> closed
        self.opened_at = None

    def call(self, fn, *args, **kwargs):
        if self.state == "open":
            if time.monotonic() - self.opened_at >= self.reset_timeout:
                self.state = "half_open"
            else:
                raise CircuitOpenError("circuit open - call short-circuited")
        try:
            result = fn(*args, **kwargs)
        except Exception:
            self.failures += 1
            if self.state == "half_open" or self.failures >= self.failure_threshold:
                self.state = "open"
                self.opened_at = time.monotonic()
            raise
        else:
            self.failures = 0
            self.state = "closed"
            return result
```

Demonstrated against a fully-dead dependency (`FaultConfig(fail_rate=1.0)`), 10 calls:

```python
breaker = CircuitBreaker(failure_threshold=3, reset_timeout=10.0)
# result: {'real_attempts': 3, 'short_circuited': 7, 'calls_that_hit_the_dependency': 3}
# — breaker opens after 3 real failures, short-circuits the remaining 7 without ever
#   touching the dead dependency again
```

Before/after across the whole Lab B sequence: baseline 57% success → retries alone 89.5% → retries + fallback 100% (never raises). The circuit breaker is demonstrated separately because it needs a *sustained* outage that the lab's modest fault rates (`fail_rate=0.2`) don't reliably produce over 200 calls — it's shown against `fail_rate=1.0` instead, where its benefit (protecting the dependency, not the caller's success rate) is unambiguous.

## Alternatives

| Library | Where it lives | Boring/simple alternative? |
|---|---|---|
| Hand-rolled `CircuitBreaker` class (above) | Plain Python, no dependency | This lab's own approach — explicit, auditable, three states in ~25 lines |
| [`pybreaker`](https://github.com/danielfm/pybreaker) | Standalone Python package | No — adds `fail_max`/`reset_timeout`/`success_threshold` config, decorator usage, and event listeners (`state_change`, `failure`, `success`) for free; async support via `call_async()` |
| [`purgatory`](https://mardiros.github.io/purgatory/) | Standalone Python package, async-first | No — supports pluggable state storage (in-memory or Redis), useful when multiple process instances need to share breaker state |
| resilience4j (Java) / Hystrix (Java, in maintenance mode) | JVM ecosystem | No — the pattern's origin point, not a Python option, but the canonical reference implementation the pattern is usually attributed to |

## How this shows up in the capstone

Milestone 7 (observability + reliability hardening: retry + circuit breaker wrapping the single agent built in Milestone 2) — per [[capstone-milestone-map]].

## Interview fire round

- **Q: Why exactly one trial call in `half_open`, not a few?**
  A: `half_open` exists to test recovery without guessing — allowing multiple trial calls risks sending a burst of traffic back at a dependency that's still down, defeating the point of the breaker. One call, and any failure re-opens immediately.
- **Q: When does a circuit breaker help that a retry alone doesn't?**
  A: During a *sustained* outage. Retries still pay the full retry budget (multiple attempts with backoff) on every request against a dead dependency — a breaker stops that spend entirely once it opens, protecting both the caller's latency and the dependency from a retry storm while it's down.

## Production gotchas & best practices

- Lab gotcha (`labs/production-notes.md`, `reliability/circuit_breaker.py`): scope one breaker instance **per dependency**, not one global breaker — otherwise one bad tool trips the breaker for unrelated tools that share it.
- Lab gotcha: compose retry *then* circuit breaker, in that deliberate order (`reliable()` in `mcp/server.py`) — retry handles the blip inside a single call, the breaker handles the sustained pattern across many calls; reversing the order (breaker wrapping retry) makes the breaker's failure count noisier, since it would only see the retry's final exhausted failure, not the earlier individual ones.
- Lab gotcha: a "recovered" breaker that immediately re-opens is usually a `half_open` bug — treating `half_open` like `closed` (allowing multiple trial calls) rather than exactly one.
- Production practice: pair the breaker with a fallback (see [[retry-fallback-patterns]]) — a breaker that's open still has to return *something* to its caller; without a fallback, "protected from hammering a dead dependency" just becomes "every caller gets `CircuitOpenError` instead."

### Seeded fault injection and chaos engineering (per course material, `presentations/day4.md`)

The course frames practicing failure as a fire drill: "find out the exit is chained shut on a quiet Tuesday, not while the building is burning." **Seeded fault injection** means choosing a dependency, breaking it on purpose with a fixed random seed (so the exact same failure sequence replays identically), and measuring the blast radius — what the user saw, what was logged, how long recovery took — before and after hardening. A fixed seed is what makes a fix provable rather than hoped-for: `inject(target="vector_db", mode="timeout", rate=1.0, seed=42)` produces the same failure every run, so "did this circuit breaker actually help" has a reproducible before/after answer instead of an anecdote. The course's own worked example: before hardening, an agent facing a fully-down vector DB waits 30 seconds and then answers from memory alone, confidently, with no citation — a silent failure, logged as nothing unusual. After hardening (retry x2 with backoff, then circuit opens, then fallback path), the same seeded fault produces a visibly different outcome: the user sees "I can't reach the policy database right now — please try again shortly," and the system logs `circuit_open`, `degraded_response`, and fires one alert. Same fault, same seed, two very different blast radii — that difference is what a retry/fallback/circuit-breaker stack is actually for, not the 57%→100% success-rate table on its own. This is the reasoning the lab's fault-injection harness (`FaultConfig(seed=42, ...)`) implements directly: reproducibility isn't a grading convenience, it's what makes the hardening claim checkable at all.

## Course vs. production

The lab demonstrates the breaker against a fully-dead dependency (`fail_rate=1.0`) in a single synchronous demo — clean, but production dependencies rarely fail at exactly 0% or 100%; real breaker tuning (`failure_threshold`, `reset_timeout`) happens against observed failure-rate distributions and is revisited as traffic patterns change. Production breaker state also typically needs to be shared across process instances (a breaker that's process-local doesn't protect a dependency from a fleet of separate workers each running their own instance) — see `purgatory`'s Redis-backed state store above, versus the lab's single in-process object.

## Related
- **Builds on** — [[retry-fallback-patterns]]
- **Feeds into** — [[langfuse-tracing]] (tag `circuit_open`/`degraded_response` events on spans, per the course's hardening example)
- **Related pattern** — [[idempotency-and-side-effects]] (a breaker prevents piling onto a dead dependency; idempotency prevents a resumed/retried call from double-firing a side effect)

## Sources

**Lab sources**
- `lab-summaries/Day4-Session1-LangfuseHardening.md` (§ "B4 — circuit breaker")
- `labs/Day4 Session 1 - LangFuse Instrumentation, Failure Injection and Production Hardening.ipynb` (`CircuitBreaker` class, B4 demonstration cell)
- `labs/production-notes.md` (§ "Retry / Resilience" — circuit breaker entry)

**Web sources**
- [pybreaker on GitHub](https://github.com/danielfm/pybreaker) — states, `fail_max`/`reset_timeout`/`success_threshold`, decorator and listener API, async support, accessed 2026-08-20
- [purgatory documentation](https://mardiros.github.io/purgatory/) — async-first design, pluggable Redis/in-memory state backend, accessed 2026-08-20
- `presentations/day4.md` (Session 1, Act 3 Question 3) — seeded fault injection, chaos engineering, blast-radius measurement — cited per course material
