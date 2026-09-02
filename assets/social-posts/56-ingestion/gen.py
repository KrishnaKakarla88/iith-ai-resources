import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "\"Documents\" Is Never A Clean Box",
      ["A scanned PDF with a broken text layer, an HTML filing whose table reads out of order, a CSV where every row is its own fact — ingestion turns each into one common shape before anything gets chunked."])

slide(p("slide-02.png"), 2, 6, "Different Shapes, Different Loaders", "No Universal \"Read This File\" Function",
      ["**PDF**: PyMuPDFLoader, fallback PyPDFLoader — one exotic PDF shouldn't halt the whole run.",
       "**HTML**: BSHTMLLoader — naive extraction can garble reading order on multi-column layouts.",
       "**CSV**: CSVLoader — one Document per row, already atomic."])

slide(p("slide-03.png"), 3, 6, "Sample Code", "A Fallback On The Path Most Likely To Break",
      ["A try/except on the PDF loader keeps one malformed file from crashing the entire ingestion batch."],
      code="def load_pdf(path, max_pages=18):\n    try:\n        docs = PyMuPDFLoader(path).load()\n    except Exception:\n        docs = PyPDFLoader(path).load()  # fallback\n    return docs[:max_pages]")

slide(p("slide-04.png"), 4, 6, "What Carries Downstream", "A Stable Identifier Per Unit",
      ["Whatever becomes the eventual chunk/point id should be traceable back to its exact source document and location — so a bad answer can be traced back to exactly what produced it."])

slide(p("slide-05.png"), 5, 6, "Production Practice", "Isolate Failures Per Document",
      ["Real archives fail in more ways than a lab dataset: scanned pages, garbled tables, inconsistent structure.",
       "Log and skip a bad file — don't crash the whole batch over one exotic document."])

slide(p("slide-06.png"), 6, 6, "Takeaway", "Get Ingestion Wrong, And Nothing Downstream Can Fix It",
      ["A retriever can only rank the chunks it was given — if extraction lost the number, the \"best\" retrieved chunk can still be confidently wrong."],
      closing_q="Does your pipeline crash on one bad PDF, or skip it and keep going?")

print("done: 56")
