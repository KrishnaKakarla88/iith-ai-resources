import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 5, "Interview Nugget", "Answer Quality Silently Drops — No Error, No Crash",
      ["A real postmortem-style scenario question: where do you look first, and why is the model usually not the culprit?"])

slide(p("slide-02.png"), 2, 5, "The Question", "A Schema Change, Then Worse Retrieval",
      ["No exception thrown anywhere. Just quietly worse answers.",
       "Where do you look first?"])

slide(p("slide-03.png"), 3, 5, "The Answer", "Ingestion And Chunking, Before The Model",
      ["Bad chunk boundaries don't throw exceptions — a paragraph split mid-sentence, a table flattened into unreadable text, still gets embedded and indexed successfully.",
       "Retrieval and generation downstream have no way to know the chunk they got was already broken."],
      code="# no error here — just a chunk that no longer answers\n# a question on its own once the source schema shifted")

slide(p("slide-04.png"), 4, 5, "The Trap", "A Hallucinated-Looking Answer Is Usually Garbage-In",
      ["Not the model reasoning poorly — the retriever quietly returning broken chunks it was never told were broken."])

slide(p("slide-05.png"), 5, 5, "Takeaway", "Silent Failures Live Where Nothing Throws",
      ["Chunking is exactly that layer — check it before reaching for a bigger model."],
      closing_q="When answer quality drops with zero errors, is ingestion the first place you look?")

print("done: 60")
