import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "A Retry Loop Doesn't Fix Malformed Data",
      ["A call can \"succeed\" and return the wrong shape — that's not a network problem, so retrying it just re-rolls the same bad odds."])

slide(p("slide-02.png"), 2, 6, "Sample Code", "Retry Only On Transient Exception Types",
      ["Retrying malformed data burns the retry budget on the same bad odds — the lab's own numbers prove it: success rate jumps 57% -> 89.5%, malformed count barely moves."],
      code="@retry(stop=stop_after_attempt(4),\n       wait=wait_exponential(multiplier=0.01, max=0.2),\n       retry=retry_if_exception_type((ConnectionError, TimeoutError)),\n       reraise=True)\ndef retrying_search_kb(topic): return flaky_fn(topic)")

slide(p("slide-03.png"), 3, 6, "The Fallback Layer", "Degradation Has To Be Visible, Never Silent",
      ["A canned record on exhausted retries or malformed data — but the whole point is a returned flag, not just the fallback itself."],
      code="def robust_search_kb(topic):\n    try:\n        res = retrying(topic)\n    except (ConnectionError, TimeoutError):\n        return [FALLBACK_RECORD], True\n    if not all(\"text\" in r for r in res):\n        return [FALLBACK_RECORD], True\n    return res, False   # used_fallback flag, checked by callers and tracing")

slide(p("slide-04.png"), 4, 6, "Why Jitter, Not Just Backoff", "A Fixed Delay Synchronizes Into A Thundering Herd",
      ["Every client retrying at the same moment re-overloads the dependency. Waiting longer each attempt, with randomized jitter, spreads that load instead of concentrating it."])

slide(p("slide-05.png"), 5, 6, "Production Practice", "Watch The Fallback Rate As A Live Metric",
      ["Canary queries — known-answer requests run continuously through the same path — catch a fallback that's silently become the default rather than the exception."])

slide(p("slide-06.png"), 6, 6, "Takeaway", "A System That Silently Degrades Is Worse Than One That Fails Loudly",
      ["A fallback is fine. A fallback nobody can see is not."],
      closing_q="Can you answer \"what fraction of traffic degraded to fallback this week\" right now?")

print("done: 82")
