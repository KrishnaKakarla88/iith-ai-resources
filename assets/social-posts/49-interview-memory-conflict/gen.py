import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 5, "Interview Nugget", "Two Memories About The Same User Disagree",
      ["A real scenario question on resolving contradictory long-term memory."])

slide(p("slide-02.png"), 2, 5, "The Question", "Aisle Seat vs. Window Seat, Twice",
      ["Six months ago: \"prefers aisle seat.\" More recently: booked window seat twice in a row.",
       "How should retrieval or write-time logic resolve this?"])

slide(p("slide-03.png"), 3, 5, "The Wrong Answers", "Newest-Wins And Averaging Both Fail Silently",
      ["Silently picking the newer fact discards a preference that may still be genuinely true in other contexts.",
       "Averaging two contradictory facts produces a fact that describes neither situation."])

slide(p("slide-04.png"), 4, 5, "The Answer", "Surface The Conflict, Don't Hide It",
      ["Weight by recency and frequency — two recent window bookings outweigh one old statement — but keep the older fact instead of deleting it.",
       "Intent can be genuinely mixed: aisle for long-haul, window for short-haul.",
       "Some systems use an explicit \"supersedes\" edge between entries instead of treating memory as flat and only-additive."])

slide(p("slide-05.png"), 5, 5, "Takeaway", "Unresolved Contradiction Is A Real Production State",
      ["Not something \"most recent write wins\" correctly resolves."],
      closing_q="Does your memory store even have a way to represent two facts disagreeing with each other?")

print("done: 49")
