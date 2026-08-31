import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 7, "Concept", "Every Provider Caps How Much You Can Call It",
      ["RPM, TPM, and daily equivalents. Hit any one of them and you get a 429 instead of a completion."])

slide(p("slide-02.png"), 2, 7, "Better Than Guessing", "Groq Tells You Exactly How Long To Wait",
      ["A retry-after header (and body text like \"Please try again in 3.86s\") on every 429.",
       "Parse it and sleep exactly that long — not a backoff guess."],
      code='re.search(r"try again in ([\\d.]+)s", str(exc))')

slide(p("slide-03.png"), 3, 7, "The Failure Mode", "Retrying Immediately Is A Thundering Herd",
      ["Many callers rate-limited at once, all retrying after the same fixed delay, collide again on the retry.",
       "Jittered exponential backoff spreads retries out instead of synchronizing them."],
      code="base_delay * 2 ** (attempt - 1) + random.uniform(0, jitter)")

slide(p("slide-04.png"), 4, 7, "Discipline", "Only Retry What's Actually Transient",
      ["Retry 429 and 5xx. A 400 or 401 retrying wastes time and calls — those need a code or config fix, not another attempt."],
      code='if "429" not in str(exc) and "5" not in status: raise')

slide(p("slide-05.png"), 5, 7, "For Known Volume", "Deliberate Pacing Beats Reactive Retry",
      ["A predictable batch job with a known TPM ceiling can just stay under it — time.sleep(n) between calls.",
       "Avoiding the 429 in the first place is cheaper than recovering from one."])

slide(p("slide-06.png"), 6, 7, "Cheapest Fix", "Don't Call The API Again At All",
      ["Cache a response keyed by model + messages + params.",
       "Skip the API call entirely on a cache hit — no re-paying, no re-waiting."],
      code="key = hashlib.sha256(json.dumps({'model': model, 'messages': messages}).encode())")

slide(p("slide-07.png"), 7, 7, "Takeaway", "Rate Limits Aren't Rare, Even On Free Tier",
      ["This isn't an edge case to handle someday — it shows up in a course lab as readily as in production."],
      closing_q="Reactive backoff, deliberate pacing, or both in your stack?")

print("done: 37")
