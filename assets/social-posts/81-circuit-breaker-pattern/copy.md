--- LINKEDIN ---
Retries help with a blip — a connection that drops once and recovers. They actively hurt during a sustained outage: every request still pays the full retry budget against a dependency that has no chance of answering, adding latency without adding any success. A circuit breaker tracks consecutive failures and, past a threshold, stops even trying.

Closed: normal operation, failures counted. Open: every call short-circuits immediately, no network attempt, once the failure threshold hits. Half-open: after a timeout, exactly one trial call tests recovery, without guessing.

def call(self, fn, *args, **kwargs):
    if self.state == "open":
        if time.monotonic() - self.opened_at >= self.reset_timeout:
            self.state = "half_open"
        else:
            raise CircuitOpenError("circuit open")
    ...

The rule that keeps the state machine correct: any failure while half-open re-opens the circuit immediately. Allowing multiple trial calls in half-open risks sending a burst of traffic back at a dependency that's still down — exactly what the breaker exists to prevent.

Production practice: scope one breaker instance per dependency, not one global breaker — otherwise one bad tool trips the breaker for unrelated tools. Compose retry then circuit breaker, in that deliberate order — reversing it makes the breaker's failure count noisier, since it would only see the retry's final exhausted failure, not the earlier individual ones.

A breaker that's open still has to return something to its caller. Without a fallback, "protected from hammering a dead dependency" just becomes "every caller gets CircuitOpenError instead."

Is your circuit breaker scoped per dependency, or one global instance for everything?

#AppliedAI #AIEngineering #LLM #LangGraph

--- INSTAGRAM ---
Retries make an outage worse, not better. 🔌

A circuit breaker: closed (normal), open (short-circuit, no network call), half-open (one trial call to test recovery).

Any failure in half-open re-opens immediately — never allow multiple trial calls against a still-broken dependency.

One breaker per dependency. Retry, then breaker, in that order.

Full mechanics in the carousel.

#AppliedAI #AIEngineering #LLM #LangGraph #GenAI

--- VISUAL FORMAT ---
carousel — 6 slides
1. Title — "Retries Actively Hurt During A Sustained Outage"
2. Three states — closed, open, half-open (diagram)
3. The rule that keeps it correct — any failure while half-open re-opens immediately
4. Sample code — ~25 lines, three states, fully auditable (code)
5. Production practice — one breaker per dependency, retry then breaker
6. Takeaway — a breaker without a fallback just changes the error message (closing question)
