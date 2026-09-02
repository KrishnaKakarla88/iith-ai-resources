import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 5, "Interview Nugget", "Routing Quality Degrades After Enough Hops",
      ["A real scenario question on why a supervisor-worker system gets worse the longer it runs."])

slide(p("slide-02.png"), 2, 5, "The Question", "Message History Grows Every Hop",
      ["After enough rounds, the supervisor's routing visibly degrades.",
       "What's happening, and what's the standard fix?"])

slide(p("slide-03.png"), 3, 5, "The Answer", "The Supervisor's Own Context Window Is Filling Up",
      ["The accumulated transcript of every worker round-trip dilutes the context the supervisor routes on.",
       "Decision quality degrades well before the hard token limit is hit — a context-rot problem, not a capacity problem."])

slide(p("slide-04.png"), 4, 5, "The Fix", "Summarize Each Worker's Result Before It Returns",
      ["Not the full transcript, forwarded verbatim — a summary.",
       "Trades some information loss and per-hop latency for keeping the supervisor's own context lean enough to route reliably."])

slide(p("slide-05.png"), 5, 5, "Takeaway", "The Same Lossy Handoff Cost, Named Earlier",
      ["A worker only ever sees a summary of state, not the supervisor's full context — this is that same tradeoff, now showing up on the way back up."],
      closing_q="Does your supervisor route on raw worker transcripts, or on summaries?")

print("done: 75")
