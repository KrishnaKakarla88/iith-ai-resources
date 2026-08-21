---
stage: "06-rag"
tools: [langchain-community, pymupdf, pypdf]
tags: [rag, ingestion, loaders]
last_verified: 2026-08-20
verified_against: "not pinned in this repo's pyproject.toml — installed ad hoc in the Day 2 Session 2 notebook"
---

# Ingestion

Ingestion is getting raw source documents — PDFs, HTML, CSVs, whatever a real corpus is actually made of — into a normalized, loadable form before anything gets chunked or embedded.

## Prerequisites
- [[what-is-an-llm]]

## In plain English

Every RAG pipeline diagram starts with a clean box labeled "documents." In reality, "documents" means a scanned PDF with a broken text layer, an HTML financial filing with a table that reads out of order, and a CSV where every row is really its own tiny fact. Ingestion is the unglamorous first stage that turns each of those into a common shape — usually a list of `Document` objects with `text` and `metadata` — so the rest of the pipeline (chunking, embedding, indexing) doesn't need to know or care what format the source file was.

Get ingestion wrong and nothing downstream can fix it: a retriever can only rank the chunks it was given, and a reranker can only reorder them. If extraction lost the number, or OCR misread it, the "best" retrieved chunk can still be confidently wrong.

## Core mechanics

Different document shapes need different loaders — there's no one universal "read this file" function that does the right thing for a PDF, an HTML filing, and a CSV table all at once.

| Document type | Loader | Notes |
|---|---|---|
| PDF (text layer present) | `PyMuPDFLoader`, fallback `PyPDFLoader` | Two-tier fallback matters — one exotic PDF (odd encoding, broken layer) shouldn't halt the whole ingestion run |
| PDF (scanned, no text layer) | OCR (not covered in the lab) | Without OCR there is no text to extract at all — this is a hard requirement, not an edge case |
| HTML | `BSHTMLLoader` (stdlib `html.parser`, no `lxml` needed) | Naive top-to-bottom text extraction can garble reading order on multi-column or tabular layouts |
| CSV / tabular | `CSVLoader` | One `Document` per row — a row is already an atomic, complete unit; don't merge or split it further |

Two ingestion-time decisions carry into every later stage:

- **Per-source caps.** Limiting how many pages/rows/chunks a source contributes (e.g. `PDF_PAGES=18`) keeps a demo corpus inside a free-tier embedding budget — see [[embeddings-models]] for why that budget exists.
- **A stable identifier per unit.** Whatever becomes the eventual chunk/point id (see [[chunking]], [[qdrant]]) should be assignable back to its source document and location, so a bad answer can be traced back to exactly which ingested unit produced it.

## Sample code

Lab-sourced (Day 2 · Session 2 — `labs/Day2 Session 2 - RAG, Retrieval and Evaluation.ipynb`), one loader per document structure with a fallback on the PDF path:

```python
from langchain_community.document_loaders import PyMuPDFLoader, PyPDFLoader, BSHTMLLoader, CSVLoader

def load_pdf(path, max_pages=18):
    try:
        docs = PyMuPDFLoader(path).load()
    except Exception:
        docs = PyPDFLoader(path).load()  # fallback for PDFs PyMuPDF chokes on
    return docs[:max_pages]

def load_html(path):
    return BSHTMLLoader(path).load()  # stdlib html.parser — no lxml dependency

def load_csv(path):
    return CSVLoader(path).load()  # one Document per row, already atomic
```

Every loaded `Document` carries `page_content` and `metadata` (source path, page number where applicable) — [[chunking]] reads from this normalized shape rather than from each file format directly.

`langchain_community`'s document loaders are not pinned in this repo's `pyproject.toml` — the notebook installs them ad hoc rather than as a tracked project dependency, unlike `langgraph`/`litellm`/`fastmcp` which are.

## Alternatives

| Approach | Where it lives | Boring/simple alternative? |
|---|---|---|
| `langchain_community` document loaders | LangChain ecosystem | — |
| LlamaIndex `SimpleDirectoryReader` / readers | LlamaIndex framework | No — same tier, different framework |
| [Docling](https://github.com/docling-project/docling) | Open-source, now under Linux Foundation governance | No — heavier, purpose-built for messy real-world PDF/table/layout extraction; the strongest self-hosted parser as of 2026 per course material (`presentations/day2.md`) |
| `pdfplumber` / stdlib `csv` + manual dict-building | Plain Python, minimal dependencies | **Yes** — the boring option; fine for small, clean, known-format corpora, but you own every fallback and edge case yourself |

## How this shows up in the capstone

Milestone 4 (production RAG + evaluation baseline) — ingestion is the entry point of the policy-RAG agent's pipeline, feeding [[chunking]] directly; see [[capstone-milestone-map]].

## Interview fire round

- **Q: Why not use one generic "extract text from file" function for everything?**
  A: A CSV row, an HTML filing, and a PDF page aren't the same kind of unit or failure mode — a row is already complete, HTML can garble reading order, and PDFs can lack a text layer entirely. Each needs a loader (and fallback) suited to its actual failure modes.
- **Q: What's the practical cost of skipping a fallback loader?**
  A: One malformed or unusually-encoded document can throw an exception and halt the whole ingestion run instead of just being skipped or degraded — production ingestion treats "one exotic file" as an expected event, not an outage.

## Production gotchas & best practices

- Lab gotcha: per-source page/row caps (`PDF_PAGES=18`, etc.) exist to keep the corpus inside a free embedding-tier rate limit — a classroom-scoped constraint, not an ingestion-quality decision; don't treat the specific cap numbers as a best practice.
- Lab gotcha: the HTML loader used stdlib `html.parser` specifically to avoid an `lxml` dependency — a reasonable simplification for a course notebook, but production HTML with heavier markup often benefits from a more robust parser.
- Production practice: real document archives fail in many more ways than a lab dataset — scanned pages with no text layer, multi-column layouts that garble reading order, and inconsistent table structures are all common; treat extraction failure as a standing operational concern, not a one-time fix, per course material (`presentations/day2.md`).
- Production practice: isolate ingestion failures per-document so one bad file doesn't block the batch — log and skip, don't crash the pipeline.

## Course vs. production

The lab's fixed three-document set (one PDF, one HTML filing, one CSV) is a controlled sample of document shapes, each clean enough that a single fallback loader per type is sufficient. Production ingestion pipelines run against much larger, messier, and less predictable archives — scanned pages needing OCR, inconsistent table extraction, versioned/superseded documents that need to be deduplicated or marked stale — and typically invest in a dedicated parsing layer (e.g. Docling, per course material) rather than a handful of LangChain loaders with a try/except fallback.

## Related
- **Feeds into** — [[chunking]]
- **Precedes** — [[embeddings-models]]

## Sources

**Lab sources**
- `lab-summaries/Day2-Session2-RAGRetrievalEval.md` (§ "Lab A — Getting Real Documents In", § "Gotchas")
- `labs/Day2 Session 2 - RAG, Retrieval and Evaluation.ipynb`

**Web sources**
- [Docling (GitHub, docling-project/docling)](https://github.com/docling-project/docling) — self-hosted document parser, Linux Foundation governance, accessed 2026-08-20
- Per course material (`presentations/day2.md`, Act 1 "What Breaks in Real-World Document Ingestion?") — messy-archive failure modes (multi-column layout, OCR requirement, versioning), not independently web-verified as course-specific framing
