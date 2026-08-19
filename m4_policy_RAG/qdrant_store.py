"""
qdrant_store.py - ShopSense M4
Centralised Qdrant client + collection helpers.
Import this everywhere instead of scattering QdrantClient() calls.
"""

import os
import re
import uuid
import time

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "shopsense_policy_rag")
EMBED_MODEL = os.getenv("EMBED_MODEL", "gemini-embedding-001")


def _default_embed_dim_for_model(model: str) -> int:
    if "text-embedding-004" in model:
        return 768
    return 3072


def _parse_int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if not raw:
        return default
    raw = raw.strip()
    if re.fullmatch(r"\d+", raw):
        return int(raw)
    return default


# If EMBED_DIM is missing or polluted with comments, fall back to the model's expected size.
EMBED_DIM = _parse_int_env("EMBED_DIM", _default_embed_dim_for_model(EMBED_MODEL))

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams


def get_client() -> QdrantClient:
    """Return a configured Qdrant client from env vars."""
    return QdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY"),
    )


def ensure_collection(client: QdrantClient) -> None:
    """Create collection if it does not exist yet."""
    existing = {c.name for c in client.get_collections().collections}
    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
        )
        print(f"[qdrant] Created collection: {COLLECTION_NAME} (dim={EMBED_DIM})")
    else:
        print(f"[qdrant] Collection exists: {COLLECTION_NAME} (dim={EMBED_DIM})")


def upsert_chunks(
    client: QdrantClient,
    chunks: list[dict],
    vectors: list[list[float]],
) -> None:
    """Upsert (chunk, vector) pairs into the collection."""
    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=vec,
            payload={
                "text": chunk["text"],
                "source": chunk["source"],
                "chunk_idx": chunk["chunk_idx"],
            },
        )
        for chunk, vec in zip(chunks, vectors)
    ]
    client.upsert(collection_name=COLLECTION_NAME, points=points)


def vector_search(
    client: QdrantClient,
    query_vector: list[float],
    top_k: int = 20,
) -> list[dict]:
    """Dense vector search. Returns list of payload+score dicts."""
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k,
        with_payload=True,
    ).points
    # hits = client.query_points(collection_name=COLLECTION, query=embed_query(query),
    #                                query_filter=qfilter, limit=k).points
    return [
        {
            "text": r.payload["text"],
            "source": r.payload["source"],
            "chunk_idx": r.payload.get("chunk_idx", 0),
            "score": r.score,
        }
        for r in results
    ]


def scroll_all(client: QdrantClient) -> list[dict]:
    """Scroll every point in the collection (for BM25 corpus build)."""
    all_chunks = []
    offset = None
    page = 0
    started = time.perf_counter()
    while True:
        page += 1
        result, offset = client.scroll(
            collection_name=COLLECTION_NAME,
            limit=200,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )
        for point in result:
            all_chunks.append(
                {
                    "text": point.payload["text"],
                    "source": point.payload["source"],
                    "chunk_idx": point.payload.get("chunk_idx", 0),
                }
            )
        print(
            f"[qdrant] scroll page {page}: +{len(result)} chunks (total={len(all_chunks)})",
            flush=True,
        )
        if offset is None:
            break
    elapsed = time.perf_counter() - started
    print(f"[qdrant] scroll complete: {len(all_chunks)} chunks in {elapsed:.2f}s", flush=True)
    return all_chunks

