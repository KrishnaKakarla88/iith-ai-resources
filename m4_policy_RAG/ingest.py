"""
ingest.py - ShopSense M4
Load policy PDFs -> chunk -> embed (Gemini) -> upsert to Qdrant.

Run: python ingest.py
"""

import os
import re
import time
import warnings
from pathlib import Path

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

# Config
POLICY_DOCS_DIR = Path(__file__).resolve().parents[2] / "data" / "shopsense" / "corpus" / "pdf"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
EMBED_MODEL = os.getenv("EMBED_MODEL", "gemini-embedding-001")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "900"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "120"))
EMBED_BATCH_SIZE = int(os.getenv("EMBED_BATCH_SIZE", "20"))
EMBED_BATCH_PAUSE = float(os.getenv("EMBED_BATCH_PAUSE", "0"))
DRY_RUN = os.getenv("DRY_RUN", "0") == "1"


def clean_ws(text):
    return re.sub(r"[ \t]+", " ", re.sub(r"\n{3,}", "\n\n", text)).strip()


def load_pdf(path: Path, loader_cls, fallback_cls) -> str:
    """Extract text from a PDF file."""
    print(f"  loading PDF: {path.name}", flush=True)
    try:
        docs = loader_cls(path).load()
    except Exception as e:
        print(f"  PyMuPDFLoader failed on {os.path.basename(path)}: {e} -> PyPDFLoader fallback", flush=True)
        docs = fallback_cls(path).load()
    text = clean_ws("\n".join([d.page_content for d in docs]))
    print(f"  extracted {len(docs)} page docs, {len(text):,} chars", flush=True)
    return text


def chunk_text(text: str, source: str, splitter) -> list[dict]:
    """Split text into chunks and attach source metadata."""
    chunks = splitter.split_text(text)
    return [
        {"text": c, "source": source, "chunk_idx": i}
        for i, c in enumerate(chunks)
        if c.strip()
    ]


def embed_batch(texts: list[str], embedder, max_retries: int = 3) -> list[list[float]]:
    """Embed a batch of texts, retrying briefly on transient rate limits."""
    last_error = None
    for attempt in range(max_retries):
        try:
            return embedder.embed_documents(texts)
        except Exception as exc:  # pragma: no cover - provider-specific failures
            last_error = exc
            if attempt == max_retries - 1 or "429" not in str(exc):
                raise
            wait_s = 2 ** attempt
            print(f"  embed rate-limited, retrying in {wait_s}s", flush=True)
            time.sleep(wait_s)
    raise last_error


def main():
    if not GEMINI_API_KEY:
        raise SystemExit("Missing GEMINI_API_KEY or GOOGLE_API_KEY in the environment.")

    print("Booting ingest...", flush=True)
    print("Importing embedding + Qdrant libraries...", flush=True)

    # The warning is from the still-supported LangChain community loader package.
    warnings.filterwarnings(
        "ignore",
        message="`langchain-community` is being sunset and is no longer actively maintained.*",
        category=DeprecationWarning,
    )

    from langchain_community.document_loaders import PyMuPDFLoader, PyPDFLoader
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from qdrant_store import ensure_collection, get_client, upsert_chunks

    print("Initializing PDF loader backend...", flush=True)
    # Force the one-time PDF backend setup to happen before the loop so it is visible.
    _ = PyMuPDFLoader
    _ = PyPDFLoader

    print(f"Scanning for PDFs in: {POLICY_DOCS_DIR}", flush=True)
    pdf_files = sorted(POLICY_DOCS_DIR.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDFs found in {POLICY_DOCS_DIR}", flush=True)
        print("Put your policy PDF files there and re-run.", flush=True)
        return

    print(f"Found {len(pdf_files)} PDFs", flush=True)
    if DRY_RUN:
        print("DRY_RUN=1, so embeddings and Qdrant writes will be skipped.", flush=True)

    embedder = GoogleGenerativeAIEmbeddings(
        model=EMBED_MODEL,
        google_api_key=GEMINI_API_KEY,
    )

    client = get_client()
    ensure_collection(client)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    total_chunks = 0
    for pdf_path in pdf_files:
        print(f"\nProcessing: {pdf_path.name}", flush=True)
        text = load_pdf(pdf_path, PyMuPDFLoader, PyPDFLoader)
        chunks = chunk_text(text, source=pdf_path.name, splitter=splitter)
        print(f"  chunked into {len(chunks)} chunks", flush=True)

        if DRY_RUN:
            total_chunks += len(chunks)
            continue

        for batch_no, i in enumerate(range(0, len(chunks), EMBED_BATCH_SIZE), start=1):
            batch_chunks = chunks[i : i + EMBED_BATCH_SIZE]
            batch_texts = [c["text"] for c in batch_chunks]
            print(
                f"  embedding batch {batch_no}/{(len(chunks) + EMBED_BATCH_SIZE - 1) // EMBED_BATCH_SIZE} "
                f"({len(batch_texts)} chunks)",
                flush=True,
            )
            vecs = embed_batch(batch_texts, embedder)
            upsert_chunks(client, batch_chunks, vecs)
            if EMBED_BATCH_PAUSE > 0 and i + EMBED_BATCH_SIZE < len(chunks):
                time.sleep(EMBED_BATCH_PAUSE)

        total_chunks += len(chunks)
        print("  -> Upserted", flush=True)

    print(f"\nDone. Total chunks indexed: {total_chunks}", flush=True)
    print(f"Collection: {os.getenv('QDRANT_URL')}", flush=True)


if __name__ == "__main__":
    main()
