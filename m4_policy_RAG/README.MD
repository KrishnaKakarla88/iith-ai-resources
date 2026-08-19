# ShopSense M4 — Production Policy RAG + Groundedness Eval

## What this does
- Ingests 14 policy PDFs → chunks → Qdrant index
- Hybrid search: dense (Gemini embeddings) + sparse (BM25) via RRF fusion
- Cross-encoder reranking (sentence-transformers)
- Grounded answer generation with citations
- Groundedness eval: LLM-as-judge — flags fabricated return windows/refund amounts
- LangFuse logging

## Stack
- `qdrant-client` — vector store (cloud)
- `langchain-google-genai` — Gemini embeddings
- `rank-bm25` — BM25 sparse retrieval
- `sentence-transformers` — cross-encoder rerank
- `litellm` — LLM calls (Groq primary)
- `langfuse` — tracing + eval
- `pypdf` — PDF loading

## Setup
```bash
pip install -r requirements.txt
cp .env.example .env  # fill in keys
```

## Keys needed (.env)
```
GROQ_API_KEY=gsk_...
GEMINI_API_KEY=...       # for embeddings
QDRANT_URL=https://...
QDRANT_API_KEY=...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
```

## Run
```bash
# 1. Ingest PDFs → Qdrant
python src/ingest.py

# 2. Query with hybrid RAG
python src/rag_query.py "What is the return window for electronics?"

# 3. Run groundedness eval on golden set
python src/eval_groundedness.py
```

## Files
```
m4_policy_rag/
├── src/
│   ├── ingest.py          # PDF load → chunk → embed → Qdrant upsert
│   ├── retriever.py       # dense + BM25 + RRF + rerank
│   ├── rag_query.py       # grounded answer with citations
│   └── eval_groundedness.py  # LLM-as-judge eval + LangFuse
├── data/
│   └── policy_docs/       # put your 14 PDF files here
├── tests/
│   └── golden_set.json    # 20-case eval set (subset for M4)
├── requirements.txt
└── .env.example
```
