import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "Never Trust A Summary Because It Sounds Complete",
      ["Context compression keeps a long conversation fitting the window by summarizing old turns — and because summarization is lossy, the only way to trust it is to test it."])

slide(p("slide-02.png"), 2, 6, "Two Failure Modes", "Silent Loss vs. Unverified Loss",
      ["**Naive truncation**: delete the oldest messages once full — silently deletes what the user assumes you still know.",
       "**Unverified summarization**: trust a summary because it reads as complete, without checking it preserved the one detail that mattered."])

slide(p("slide-03.png"), 3, 6, "Core Mechanics", "Recent-Keep Window + Rolling Summary",
      ["Last N turns stay verbatim. Everything older collapses into a short summary, merged forward each pass so a fact from turn 3 survives even after two more compressions."],
      diagram=("flow", ["Old turns", "Summarize", "Merge with prior", "Recent N verbatim"]))

slide(p("slide-04.png"), 4, 6, "The Actual Lesson", "Plant A Fact, Compress Past It, Assert It Survived",
      ["**Example:** \"I have a pet parrot named Kiwi\" gets pushed out of the recent-keep window, then compression runs."],
      code="summary = summarize_turns(turns[:-RECENT_KEEP])\nassert \"kiwi\" in summary.lower()  # proves the fact survived")

slide(p("slide-05.png"), 5, 6, "Production Practice", "Keep A Raw Fallback For Exact Identifiers",
      ["LLM summarization reliably paraphrases order numbers and IDs instead of preserving them verbatim.",
       "Try a raw recent-turns cache first for anything identifier-shaped; fall back to the compressed summary only for softer context."])

slide(p("slide-06.png"), 6, 6, "Takeaway", "temperature=0 Isn't Optional Here",
      ["A summarization prompt is the one place you don't want creative variance — you want the most literal, deterministic compression of what was actually stated."],
      closing_q="Has a summarizer ever silently dropped the one detail your agent needed three turns later?")

print("done: 48")
