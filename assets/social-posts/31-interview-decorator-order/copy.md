--- LINKEDIN ---
Real interview scenario: stack @traced above @retry_with_backoff(max_retries=3) on a tool function. A call fails twice, then succeeds on the third attempt. How many trace spans does @traced record?

One. @traced above @retry_with_backoff wraps the entire retrying process as a single call — it records one span covering all three attempts, and only sees the final outcome.

Reverse the order — @retry_with_backoff above @traced — and it instead retries the already-traced function. That produces three separate spans, one per attempt. Same underlying code, same retry count, completely different trace.

Neither order is wrong in the abstract. But if the real question is "why did our trace show only 1 span for a call we know retried," the answer is decorator order, not a tracing bug.

Which order does your tracing stack use?

#AppliedAI #Python #LLM #AIEngineering

--- INSTAGRAM ---
Real interview scenario. 🔍

@traced stacked above @retry_with_backoff(max_retries=3). A call fails twice, succeeds on the third try.

How many trace spans does @traced record? One — it wraps the entire retry process as a single call.

Reverse the order and you get three spans instead, one per attempt. Same code, different trace.

Full scenario + answer in the carousel.

Which order does your stack use?

#AppliedAI #Python #LLM #GenAI #Developer

--- VISUAL FORMAT ---
carousel — 5 slides
1. Title — "Decorator Order Changes Your Trace"
2. The Question — which order, which trace (code)
3. The Answer — one span, not three
4. Reverse It — same code, different trace
5. Takeaway + closing question
