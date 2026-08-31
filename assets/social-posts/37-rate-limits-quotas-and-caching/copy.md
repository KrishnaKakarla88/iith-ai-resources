--- LINKEDIN ---
Every LLM provider caps how much you can call it — RPM, TPM, often daily equivalents. Hit any one and you get a 429 instead of a completion. Not rare on a free tier, and not rare in production once traffic scales.

Retrying immediately makes things worse: many requests rate-limited at once, all retrying after the same fixed delay, collide again — a thundering herd. Jittered exponential backoff spreads retries out. Better than guessing: Groq's 429 responses include a retry-after header ("Please try again in 3.86s"). Parse it and sleep exactly that long.

Only retry what's actually transient — 429 and 5xx. A 400 or 401 retrying wastes time and calls; those need a code or config fix, not another attempt.

For a predictable batch job with a known TPM ceiling, deliberate pacing beats reactive retry — time.sleep(n) between calls avoids the 429 in the first place. And the cheapest fix of all is not calling the API again — caching a response keyed by model + messages + params skips the call entirely on a hit.

Reactive backoff, deliberate pacing, or both in your stack?

#AppliedAI #LLM #AIEngineering #PromptEngineering

--- INSTAGRAM ---
Every provider caps your calls. RPM, TPM, daily limits. ⏱️

Groq's 429 tells you exactly how long to wait — "Please try again in 3.86s." Parse it, sleep that long, skip the backoff guess.

Only retry 429/5xx. A 400 or 401 retrying just burns calls.

Known batch volume? Deliberate pacing beats reactive retry — avoid the 429 in the first place.

Full breakdown in the carousel.

Reactive backoff, deliberate pacing, or both?

#AppliedAI #LLM #AIEngineering #GenAI #Developer

--- VISUAL FORMAT ---
carousel — 7 slides
1. Title — "Every Provider Caps How Much You Can Call It"
2. Better than guessing — Groq tells you exactly how long to wait (code)
3. The failure mode — retrying immediately is a thundering herd (code)
4. Discipline — only retry what's actually transient (code)
5. For known volume — deliberate pacing beats reactive retry
6. Cheapest fix — don't call the API again at all (code)
7. Takeaway — rate limits aren't rare, even on free tier (closing question)
