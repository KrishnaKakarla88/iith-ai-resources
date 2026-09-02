--- LINKEDIN ---
A call can "succeed" and return malformed data — a record missing a required field. Retrying that just re-rolls the same bad odds; it isn't a network problem, so a retry loop that only catches exceptions won't touch it. Retry and fallback are two separate decisions: one recovers from transient failure, the other contains failure that didn't recover.

@retry(stop=stop_after_attempt(4),
       wait=wait_exponential(multiplier=0.01, max=0.2),
       retry=retry_if_exception_type((ConnectionError, TimeoutError)),
       reraise=True)
def retrying_search_kb(topic): return flaky_fn(topic)

Retrying only on transient exception types matters — the lab's own numbers prove it: success rate jumps 57% to 89.5%, but the malformed-data count barely moves. Retries fix transience, not data quality.

def robust_search_kb(topic):
    try:
        res = retrying(topic)
    except (ConnectionError, TimeoutError):
        return [FALLBACK_RECORD], True
    if not all("text" in r for r in res):
        return [FALLBACK_RECORD], True
    return res, False

The used_fallback flag is the whole point — it's what a caller, or a tracing span tag, checks to answer "what fraction of production traffic degraded to fallback this week," instead of that fraction being invisible.

Why exponential backoff with jitter instead of a fixed delay: a fixed delay across many clients synchronizes into a thundering herd, everyone retrying at the same moment and re-overloading the dependency. Jitter spreads that load instead of concentrating it.

Production practice: watch the fallback rate as a live metric. Canary queries — known-answer requests run continuously through the same path — catch a fallback that's silently become the default rather than the exception.

A system that silently degrades is worse than one that fails loudly. A fallback is fine; a fallback nobody can see is not.

Can you answer "what fraction of traffic degraded to fallback this week" right now?

#AppliedAI #AIEngineering #LLM #LangGraph

--- INSTAGRAM ---
Retrying malformed data fixes nothing. It's not a network problem. 🔁

retry=retry_if_exception_type((ConnectionError, TimeoutError))

Fallback is a separate decision — and the used_fallback flag matters more than the fallback itself. Silent degradation is worse than a loud failure.

Full mechanics in the carousel.

#AppliedAI #AIEngineering #LLM #LangGraph #GenAI

--- VISUAL FORMAT ---
carousel — 6 slides
1. Title — "A Retry Loop Doesn't Fix Malformed Data"
2. Sample code — retry only on transient exception types (code)
3. The fallback layer — degradation has to be visible, never silent (code)
4. Why jitter, not just backoff — a fixed delay synchronizes into a thundering herd
5. Production practice — watch the fallback rate as a live metric
6. Takeaway — a system that silently degrades is worse than one that fails loudly (closing question)
