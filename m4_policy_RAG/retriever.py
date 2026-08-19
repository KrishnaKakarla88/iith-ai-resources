"""
retriever.py - ShopSense M4
Hybrid retrieval: dense (Qdrant) + BM25 -> RRF fusion -> cross-encoder rerank.

Key concepts from lab:
- Dense vectors miss exact identifiers ("30-day", "INV-1001") -> BM25 catches them
- RRF (Reciprocal Rank Fusion) combines ranked lists without needing score normalization
- Cross-encoder reranking: expensive but precise - scores query-doc pairs jointly
"""

import logging
import os
import time
from dataclasses import dataclass

import numpy as np
from dotenv import find_dotenv, load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder

from qdrant_store import get_client, scroll_all, vector_search

load_dotenv(find_dotenv())
os.environ.setdefault("GEMINI_API_KEY", os.getenv("GOOGLE_API_KEY", ""))

EMBED_MODEL = os.getenv("EMBED_MODEL", "gemini-embedding-001")
RERANK_MODEL = os.getenv("RERANK_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
DENSE_TOP_K = 20  # candidates from vector search
BM25_TOP_K = 20  # candidates from BM25
RRF_K = 60  # RRF constant (60 is standard)
FINAL_TOP_K = 5  # chunks to feed to LLM

logger = logging.getLogger(__name__)


def _ensure_logging() -> None:
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(message)s",
        )


@dataclass
class RetrievedChunk:
    text: str
    source: str
    score: float
    chunk_idx: int


class HybridRetriever:
    """Dense + BM25 + RRF + cross-encoder reranker."""

    def __init__(self):
        _ensure_logging()
        logger.info(
            "Initializing retriever (embed_model=%s, rerank_model=%s)",
            EMBED_MODEL,
            RERANK_MODEL,
        )
        t0 = time.perf_counter()
        self._embedder = GoogleGenerativeAIEmbeddings(
            model=EMBED_MODEL,
            google_api_key=os.getenv("GEMINI_API_KEY"),
        )
        self._qdrant = get_client()
        self._reranker = CrossEncoder(RERANK_MODEL)
        logger.info("Retriever models ready in %.2fs", time.perf_counter() - t0)

        # BM25 index is built lazily from Qdrant corpus on first query.
        self._bm25: BM25Okapi | None = None
        self._corpus: list[RetrievedChunk] | None = None

    def _load_corpus(self) -> list[RetrievedChunk]:
        """Scroll all points from Qdrant to build BM25 index."""
        logger.info("Loading corpus from Qdrant for BM25 indexing")
        t0 = time.perf_counter()
        corpus = [
            RetrievedChunk(
                text=c["text"],
                source=c["source"],
                score=0.0,
                chunk_idx=c["chunk_idx"],
            )
            for c in scroll_all(self._qdrant)
        ]
        logger.info("Loaded %d chunks in %.2fs", len(corpus), time.perf_counter() - t0)
        return corpus

    def _get_bm25(self) -> tuple[BM25Okapi, list[RetrievedChunk]]:
        if self._bm25 is None:
            logger.info("Building BM25 index from corpus")
            t0 = time.perf_counter()
            self._corpus = self._load_corpus()
            tokenized = [c.text.lower().split() for c in self._corpus]
            logger.info("Tokenized corpus, building BM25 vocabulary")
            self._bm25 = BM25Okapi(tokenized)
            logger.info(
                "BM25 indexed %d chunks in %.2fs",
                len(self._corpus),
                time.perf_counter() - t0,
            )
        return self._bm25, self._corpus

    def _dense_search(self, query: str, top_k: int) -> list[RetrievedChunk]:
        logger.info("Dense search: embedding query and searching top %d", top_k)
        t0 = time.perf_counter()
        query_vec = self._embedder.embed_query(query)
        results = [
            RetrievedChunk(
                text=r["text"],
                source=r["source"],
                score=r["score"],
                chunk_idx=r["chunk_idx"],
            )
            for r in vector_search(self._qdrant, query_vec, top_k)
        ]
        logger.info("Dense search returned %d chunks in %.2fs", len(results), time.perf_counter() - t0)
        return results

    def _bm25_search(self, query: str, top_k: int) -> list[RetrievedChunk]:
        logger.info("BM25 search: scoring query against corpus for top %d", top_k)
        t0 = time.perf_counter()
        bm25, corpus = self._get_bm25()
        tokens = query.lower().split()
        scores = bm25.get_scores(tokens)
        top_indices = np.argsort(scores)[::-1][:top_k]
        results = []
        for idx in top_indices:
            chunk = corpus[idx]
            results.append(
                RetrievedChunk(
                    text=chunk.text,
                    source=chunk.source,
                    score=float(scores[idx]),
                    chunk_idx=chunk.chunk_idx,
                )
            )
        logger.info("BM25 search returned %d chunks in %.2fs", len(results), time.perf_counter() - t0)
        return results

    @staticmethod
    def _rrf_fuse(
        dense_results: list[RetrievedChunk],
        bm25_results: list[RetrievedChunk],
        k: int = RRF_K,
    ) -> list[RetrievedChunk]:
        """
        Reciprocal Rank Fusion:
        score(d) = sum over lists: 1 / (k + rank(d))
        Deduplicates by source + chunk index.
        """
        scores: dict[tuple[str, int], float] = {}
        chunks_map: dict[tuple[str, int], RetrievedChunk] = {}

        for rank, chunk in enumerate(dense_results, start=1):
            key = (chunk.source, chunk.chunk_idx)
            scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank)
            chunks_map[key] = chunk

        for rank, chunk in enumerate(bm25_results, start=1):
            key = (chunk.source, chunk.chunk_idx)
            scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank)
            chunks_map[key] = chunk

        sorted_keys = sorted(scores, key=lambda item: scores[item], reverse=True)
        return [
            RetrievedChunk(
                text=chunks_map[key].text,
                source=chunks_map[key].source,
                score=scores[key],
                chunk_idx=chunks_map[key].chunk_idx,
            )
            for key in sorted_keys
        ]

    def _rerank(
        self,
        query: str,
        candidates: list[RetrievedChunk],
        top_k: int = FINAL_TOP_K,
    ) -> list[RetrievedChunk]:
        if not candidates:
            logger.info("Rerank skipped because there are no candidates")
            return []
        logger.info("Reranking %d candidates to top %d", len(candidates), top_k)
        t0 = time.perf_counter()
        pairs = [(query, c.text) for c in candidates]
        ce_scores = self._reranker.predict(pairs)
        ranked = sorted(
            zip(ce_scores, candidates),
            key=lambda x: x[0],
            reverse=True,
        )
        results = [
            RetrievedChunk(
                text=chunk.text,
                source=chunk.source,
                score=float(score),
                chunk_idx=chunk.chunk_idx,
            )
            for score, chunk in ranked[:top_k]
        ]
        logger.info("Rerank produced %d chunks in %.2fs", len(results), time.perf_counter() - t0)
        return results

    def retrieve(self, query: str) -> list[RetrievedChunk]:
        """Full pipeline: dense + BM25 -> RRF -> rerank -> top-k chunks."""
        _ensure_logging()
        logger.info("Retrieval started: %s", query[:120])
        t0 = time.perf_counter()
        dense = self._dense_search(query, DENSE_TOP_K)
        sparse = self._bm25_search(query, BM25_TOP_K)
        fused = self._rrf_fuse(dense, sparse)
        logger.info("RRF fused %d unique candidates", len(fused))
        final = self._rerank(query, fused[:30])
        logger.info("Retrieval finished in %.2fs", time.perf_counter() - t0)
        return final
