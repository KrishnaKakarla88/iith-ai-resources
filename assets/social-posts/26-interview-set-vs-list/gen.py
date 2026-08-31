import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 5, "Interview Nugget", "Set vs List At Scale",
      ["A real scenario question on choosing collections under load."])

slide(p("slide-02.png"), 2, 5, "The Question", "Thousands Of IDs, One Check",
      ["A junior engineer stores thousands of already-processed ticket IDs in a list.",
       "Every new ticket is checked with membership: if ticket_id in processed."],
      code="if ticket_id in processed:  # looks fine... at first")

slide(p("slide-03.png"), 3, 5, "The Problem", "O(n) Scan, Every Single Check",
      ["**in** on a list scans linearly — the check gets slower as the list grows.",
       "Doing this per-ticket across thousands of tickets turns into O(n^2) total work."])

slide(p("slide-04.png"), 4, 5, "The Fix", "Swap List For Set",
      ["A set gives O(1) average membership checks via hashing — "
       "the entire reason it exists as a distinct type from a list."],
      code="processed = set()  # same check, O(1) avg instead of O(n)")

slide(p("slide-05.png"), 5, 5, "Takeaway", "Know Your Collection's Big-O",
      ["Syntax knowledge isn't enough — this is a "
       "'do you understand what you reach for' interview probe."],
      closing_q="Have you shipped this exact bug before catching it?")

print("done: 26")
