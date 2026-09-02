--- LINKEDIN ---
Every RAG pipeline diagram starts with a clean box labeled "documents." In reality that means a scanned PDF with a broken text layer, an HTML financial filing whose table reads out of order, and a CSV where every row is really its own tiny fact. Ingestion is the unglamorous first stage that turns each of those into one common shape — usually a list of Document objects with text and metadata — before anything gets chunked or embedded.

There's no universal "read this file" function that does the right thing for all three. PDFs need PyMuPDFLoader with a PyPDFLoader fallback, since one exotic encoding shouldn't halt the whole run. HTML needs BSHTMLLoader, since naive top-to-bottom extraction can garble reading order on multi-column layouts. CSVs need CSVLoader — one row is already a complete, atomic unit, don't merge or split it further.

def load_pdf(path, max_pages=18):
    try:
        docs = PyMuPDFLoader(path).load()
    except Exception:
        docs = PyPDFLoader(path).load()  # fallback
    return docs[:max_pages]

Whatever becomes the eventual chunk/point id downstream should be traceable back to its exact source document and location — so a bad answer can be traced back to exactly which ingested unit produced it.

Production practice: isolate ingestion failures per document. Real archives fail in more ways than a lab dataset — scanned pages, garbled tables, inconsistent structure. Log and skip a bad file rather than crashing the whole batch over one exotic document.

Get ingestion wrong and nothing downstream can fix it — a retriever can only rank the chunks it was given. If extraction lost the number, the "best" retrieved chunk can still be confidently wrong.

Does your pipeline crash on one bad PDF, or skip it and keep going?

#AppliedAI #RAG #LLM #AIEngineering

--- INSTAGRAM ---
"Documents" is never a clean box. 📂

Scanned PDFs, garbled HTML tables, CSV rows that are each their own fact — ingestion normalizes all three before anything gets chunked.

def load_pdf(path):
    try: docs = PyMuPDFLoader(path).load()
    except: docs = PyPDFLoader(path).load()  # fallback

One exotic file shouldn't crash the whole batch. Log and skip.

Full breakdown in the carousel.

#AppliedAI #RAG #LLM #AIEngineering #GenAI

--- VISUAL FORMAT ---
carousel — 6 slides
1. Title — "\"Documents\" Is Never A Clean Box"
2. Different shapes, different loaders — PDF/HTML/CSV
3. Sample code — a fallback on the path most likely to break (code)
4. What carries downstream — a stable identifier per unit
5. Production practice — isolate failures per document
6. Takeaway — get ingestion wrong, nothing downstream fixes it (closing question)
