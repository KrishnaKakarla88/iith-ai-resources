import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "A Retriever Never Searches Whole Documents",
      ["It searches chunks — get the chunk size wrong and even a perfect retriever returns text that's too big to be relevant or too small to make sense."])

slide(p("slide-02.png"), 2, 6, "Too Big vs. Too Small", "Chunking Is A Tradeoff, Not A Setting",
      ["**Example:** a 5,000-word chunk covering ten subtopics dilutes the embedding — it doesn't strongly match a query about any one of them.",
       "A single sentence pulled from a legal clause loses the clause it belonged to."])

slide(p("slide-03.png"), 3, 6, "Match The Strategy To The Source", "One Splitter Doesn't Fit Every Document",
      ["**Recursive character splitting**: default for prose — tries paragraph, then sentence, then word boundaries before a hard cut.",
       "**Row-atomic**: a CSV row is already a complete unit — don't split it further.",
       "**Header-aware**: carries the heading path into chunk metadata for structured Markdown/HTML."])

slide(p("slide-04.png"), 4, 6, "Core Mechanics", "Chunk Size + Overlap",
      ["Overlap repeats a few characters at each boundary, so a concept split across a cut isn't fully lost to either side."],
      code="from langchain_text_splitters import RecursiveCharacterTextSplitter\n\nsplitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=120)\nchunks = splitter.split_text(document_text)")

slide(p("slide-05.png"), 5, 6, "Production Practice", "Tune Against The Eval, Not Once And Forget",
      ["A chunk size that works for a manual page won't necessarily work for a return-policy FAQ.",
       "Re-check chunk size/overlap against the retrieval eval harness whenever the corpus changes."])

slide(p("slide-06.png"), 6, 6, "Takeaway", "The cid Gets Assigned At Chunking Time",
      ["Not at embedding time — it doubles as the Qdrant point id downstream, so it has to exist before either step runs."],
      closing_q="Is your chunk size tuned against a retrieval eval, or just picked once and left?")

print("done: 50")
