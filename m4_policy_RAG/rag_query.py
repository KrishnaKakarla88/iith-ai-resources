"""
rag_query.py - ShopSense M4
Grounded answer generation with citations + LangFuse tracing.

Usage:
  python rag_query.py "What is the return window for electronics?"
"""

import logging
import os
import sys
import time

from dotenv import find_dotenv, load_dotenv
from langfuse import Langfuse
from litellm import completion

from retriever import HybridRetriever, RetrievedChunk

load_dotenv(find_dotenv())
os.environ.setdefault("GEMINI_API_KEY", os.getenv("GOOGLE_API_KEY", ""))

LLM_MODEL = os.getenv("LLM_MODEL") or os.getenv("GROQ_MODEL") or "groq/llama-3.1-8b-instant"

ANSWER_PROMPT = """\
You are a ShopSense customer support assistant. Answer the customer's question
using ONLY the policy excerpts provided below.

RULES:
1. Cite the source document in brackets after each factual claim, e.g. [returns_policy.pdf].
2. If the answer is not in the excerpts, say: "I don't have that information in the current policy documents."
3. Never invent return windows, refund amounts, or timeframes not explicitly stated.
4. Be concise and direct.

--- POLICY EXCERPTS ---
{context}
--- END EXCERPTS ---

Customer question: {question}

Answer:"""

logger = logging.getLogger(__name__)


def _ensure_logging() -> None:
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(message)s",
        )


def format_context(chunks: list[RetrievedChunk]) -> str:
    if not chunks:
        return "No relevant policy excerpts were retrieved."
    parts = []
    for chunk in chunks:
        parts.append(f"[{chunk.source}] (score: {chunk.score:.3f})\n{chunk.text}")
    return "\n\n".join(parts)


def answer_with_rag(
    question: str,
    retriever: HybridRetriever,
    langfuse: Langfuse | None = None,
) -> dict:
    """Retrieve -> generate grounded answer. Returns dict with answer + chunks."""

    _ensure_logging()
    logger.info("Answering question: %s", question[:120])

    observation = None
    if langfuse:
        observation_ctx = langfuse.start_as_current_observation(
            name="policy_rag",
            as_type="chain",
            input={"question": question},
        )
        observation = observation_ctx.__enter__()

    try:
        t0 = time.perf_counter()
        chunks = retriever.retrieve(question)
        logger.info("Retrieved %d chunks in %.2fs", len(chunks), time.perf_counter() - t0)

        context = format_context(chunks)
        prompt = ANSWER_PROMPT.format(context=context, question=question)

        logger.info("Calling LLM generation with model=%s", LLM_MODEL)
        t1 = time.perf_counter()
        resp = completion(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        answer = resp.choices[0].message.content or ""
        logger.info("LLM generation finished in %.2fs", time.perf_counter() - t1)

        if observation is not None:
            observation.update(
                output={
                    "question": question,
                    "answer": answer,
                    "num_chunks": len(chunks),
                    "sources": [c.source for c in chunks],
                }
            )
    finally:
        if langfuse and observation is not None:
            observation_ctx.__exit__(None, None, None)

    return {
        "question": question,
        "answer": answer,
        "chunks": chunks,
    }


def main():
    _ensure_logging()
    question = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "What is the return window for electronics?"

    logger.info("Starting ShopSense RAG query")

    langfuse = None
    if os.getenv("LANGFUSE_PUBLIC_KEY"):
        langfuse = Langfuse(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            host=os.getenv("LANGFUSE_HOST", os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")),
        )

    retriever = HybridRetriever()
    result = answer_with_rag(question, retriever, langfuse)

    print("\n" + "=" * 60)
    print(f"Q: {result['question']}")
    print(f"\nA: {result['answer']}")
    print("\n--- Retrieved chunks ---")
    for chunk in result["chunks"]:
        print(f"  [{chunk.source}] score={chunk.score:.3f} | {chunk.text[:100]}...")

    if langfuse:
        langfuse.flush()


if __name__ == "__main__":
    main()

