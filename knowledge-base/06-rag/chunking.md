---
stage: "06-rag"
tools: [langchain-text-splitters]
tags: [rag, chunking, ingestion]
last_verified: 2026-08-19
verified_against: "langchain_text_splitters (current split from legacy langchain.text_splitter)"
---

# Chunking

Chunking splits a source document into retrieval-sized pieces — get it wrong and even a perfect retriever returns text that's too big to be relevant or too small to make sense on its own.

## Prerequisites
- [[ingestion]]

## In plain English

A retriever doesn't search whole documents — it searches chunks. If a chunk is too large, it dilutes the embedding (a 5,000-word chunk about ten different subtopics doesn't strongly match a query about any one of them) and wastes context-window budget when it's retrieved. If a chunk is too small, it loses the surrounding context that made it meaningful (a single sentence pulled from the middle of a legal clause, with no idea what clause it's part of). Chunking strategy has to match the shape of the source document — a PDF research paper, an HTML financial filing, and a CSV table of rows are not the same problem.

## Core mechanics

| Strategy | When to use | Notes |
|---|---|---|
| Fixed-size character/token splitting | Quick baseline, unstructured prose | Cuts mid-sentence/mid-word without overlap; rarely used alone in production |
| Recursive character splitting | Default for most prose (papers, articles, filings) | Tries a hierarchy of separators (paragraph → sentence → word) so it prefers natural boundaries before falling back to a hard cut |
| Row/record-atomic | Structured tabular data (CSV, DB rows) | Each row is already a complete, retrievable unit — don't further split it |
| Header-aware splitting | Markdown/HTML with real heading structure | Carries heading path into chunk metadata, so a chunk still "knows" what section it came from |
| Semantic/embedding-based splitting | High-value corpora where boundary quality matters more than speed | Splits where embedding similarity between adjacent sentences drops, instead of a fixed character count |

Two knobs matter most on the character-based splitters: **chunk size** (target chunk length) and **chunk overlap** (characters repeated between consecutive chunks, so a concept split across a boundary isn't entirely lost to either chunk).

## Sample code

Lab-sourced (Day 2 · Session 2 — `labs/Day2 Session 2 - RAG, Retrieval and Evaluation.ipynb`), matched per document type rather than one splitter for everything:

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Prose sources (PDF research paper, HTML financial filing)
splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=120)
chunks = splitter.split_text(document_text)

# Tabular source (CSV) — rows are already atomic, no further splitting
# each row from CSVLoader becomes one chunk, unchanged

# every chunk normalized to the same shape before embedding:
chunk = {"cid": chunk_id, "text": chunk_text, "source": source_name, "doc_type": doc_type}
```

`cid` doubles as the Qdrant point id later in [[qdrant]], so it's assigned at chunking time, not at embedding time.

Import note: `RecursiveCharacterTextSplitter` now lives in the standalone `langchain_text_splitters` package (`from langchain_text_splitters import RecursiveCharacterTextSplitter`) — the older `from langchain.text_splitter import ...` path is legacy and shouldn't be used for new code.

## Alternatives

| Approach | Where it lives | Boring/simple alternative to LangChain's splitters? |
|---|---|---|
| `langchain_text_splitters` | Standalone LangChain package | — |
| LlamaIndex `NodeParser`s (`SentenceSplitter`, `SemanticSplitterNodeParser`) | LlamaIndex framework | No — same tier of tooling, different framework |
| `unstructured` (partitioning + chunking) | Open-source, `unstructured-io/unstructured` | No — heavier, specializes in messy real-world doc formats (scanned PDFs, mixed layouts) |
| Manual `str.split()` on paragraph breaks + a fixed-length fallback | Plain Python, no dependency | **Yes** — the boring option; fine for small, clean corpora, loses the separator-hierarchy fallback and overlap handling |

## How this shows up in the capstone

Milestone 4 (production RAG + evaluation baseline) — chunking is Lab A of the RAG session, feeding the policy-RAG agent's ingestion pipeline directly; see [[capstone-milestone-map]].

## Interview fire round

- **Q: Why not just use one fixed chunk size for every document type?**
  A: A CSV row and a PDF paragraph aren't the same kind of unit — a row is already atomic and complete, while prose needs a size/overlap tuned to preserve sentence-level meaning. One splitter for both either mangles rows or over-chunks prose.
- **Q: What does chunk overlap actually buy you?**
  A: It prevents a concept that straddles a chunk boundary from being fully lost to both halves — a small amount of repeated text at each boundary gives each chunk enough surrounding context to stand alone in a retrieval result.

## Production gotchas & best practices

- Lab gotcha: per-source chunk caps (e.g. `PAPER_CHUNKS=60`) exist to keep the whole corpus inside a free embedding-tier rate limit (100 req/min, 1000/day) — a classroom-scoped constraint, not a chunking-quality decision; don't read the cap numbers themselves as a best practice.
- Lab gotcha: heavily structured markup (real Markdown/HTML with headings) is better served by header-aware splitters that carry heading context into metadata — the lab notes this as an available but unused option, since its HTML filing didn't have clean heading structure to exploit.
- Production practice: chunk size/overlap should be tuned against your actual retrieval eval (see [[retrieval-eval-metrics]]), not picked once and left — a chunk size that works for a manual page won't necessarily work for a return-policy FAQ.

## Course vs. production

The lab caps corpus size and chunk counts to survive a free-tier rate limit — a classroom constraint. In production, chunking is typically re-evaluated per corpus and per retrieval-quality metrics, and a mismatched chunk size is diagnosed and fixed via the eval harness in [[retrieval-eval-metrics]], not fixed once at ingestion time and forgotten.

## Related
- **Builds on** — [[ingestion]]
- **Feeds into** — [[embeddings-models]], [[dense-retrieval]], [[bm25-sparse-retrieval]]
- **Evaluated by** — [[retrieval-eval-metrics]]

## Sources

**Lab sources**
- `lab-summaries/Day2-Session2-RAGRetrievalEval.md` (§ "A2 Structure-aware chunking")
- `labs/Day2 Session 2 - RAG, Retrieval and Evaluation.ipynb`

**Web sources**
- [LangChain OpenTutorial — RecursiveCharacterTextSplitter](https://langchain-opentutorial.gitbook.io/langchain-opentutorial/07-textsplitter/02-recursivecharactertextsplitter) — separator hierarchy behavior, accessed 2026-08-19
- [LangChain Reference — RecursiveCharacterTextSplitter](https://reference.langchain.com/python/langchain-text-splitters/character/RecursiveCharacterTextSplitter) — current `langchain_text_splitters` package location, accessed 2026-08-19
