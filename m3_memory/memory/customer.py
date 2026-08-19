"""Per-customer persistent memory helpers for ShopSense M3.

Maps the lab's memory taxonomy to the project:
  episodic   -> past ticket events
  semantic   -> stable customer facts / preferences
  procedural -> agent-side playbooks, not stored per customer
  working    -> live context window inside the agent
"""
from __future__ import annotations

import os
import time
from typing import Any

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

DEFAULT_NAMESPACE_PREFIX = os.getenv("MEMORY_NS_PREFIX", "shopsense-customer")
DEFAULT_MODEL = os.getenv("LLM_MODEL", "gemini/gemini-flash-latest")


def _ns(customer_ref: str) -> str:
    """Build a tenant-safe namespace for one customer."""
    return f"{DEFAULT_NAMESPACE_PREFIX}-{customer_ref}"


def _client() -> Any:
    try:
        import supermemory
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "supermemory is not installed. Install it to enable persistent customer memory."
        ) from exc

    api_key = os.getenv("SUPERMEMORY_API_KEY")
    if not api_key:
        raise RuntimeError("SUPERMEMORY_API_KEY is required for customer memory.")
    return supermemory.Supermemory(api_key=api_key)


def add_memory(customer_ref: str, text: str, kind: str, **extra: Any):
    """Write a memory item with a kind tag."""
    return _client().add(
        content=text,
        container_tag=_ns(customer_ref),
        metadata={"type": kind, **extra},
    )


def store_episodic(customer_ref: str, text: str, **meta: Any) -> None:
    """Store a ticket event after resolution."""
    _client().add(
        content=text,
        container_tag=_ns(customer_ref),
        metadata={"type": "episodic", **meta},
    )


def store_semantic(customer_ref: str, text: str, **meta: Any) -> None:
    """Store or refresh a stable customer fact."""
    _client().add(
        content=text,
        container_tag=_ns(customer_ref),
        metadata={"type": "semantic", **meta},
    )


def store_procedural(customer_ref: str, text: str, **meta: Any) -> None:
    """Store a reusable playbook for this customer if needed."""
    _client().add(
        content=text,
        container_tag=_ns(customer_ref),
        metadata={"type": "procedural", **meta},
    )


def store_working(customer_ref: str, text: str, **meta: Any) -> None:
    """Store a rolling working-memory summary for a customer."""
    _client().add(
        content=text,
        container_tag=_ns(customer_ref),
        metadata={"type": "working", **meta},
    )


def recall(customer_ref: str, query: str, k: int = 4) -> list[dict[str, Any]]:
    """Semantic search over one customer's memories."""
    mem = _client()
    ns = _ns(customer_ref)
    out: list[dict[str, Any]] = []

    for r in mem.search.memories(q=query, container_tag=ns, limit=k).results:
        if getattr(r, "memory", None):
            out.append(
                {
                    "type": (r.metadata or {}).get("type", "?"),
                    "text": r.memory,
                    "score": float(r.similarity or 0.0),
                }
            )

    if not out:
        for r in mem.search.documents(q=query, container_tags=[ns], limit=k).results:
            text = " ".join(
                c.content for c in (r.chunks or []) if c and c.content
            ).strip()
            if text:
                out.append(
                    {
                        "type": (r.metadata or {}).get("type", "?"),
                        "text": text,
                        "score": float(r.score or 0.0),
                    }
                )
    return out


def recall_formatted(customer_ref: str, query: str, k: int = 4) -> str:
    """Return memory hits in a prompt-ready format."""
    hits = recall(customer_ref, query, k)
    if not hits:
        return "No prior interaction history found for this customer."
    lines = [f"[{h['type']}] {h['text']}" for h in hits]
    return "Customer memory context:\n" + "\n".join(lines)


def recall_working(
    customer_ref: str,
    query: str = "conversation summary",
    k: int = 8,
) -> str | None:
    """Return the latest working-memory summary if one exists."""
    for hit in recall(customer_ref, query, k):
        if hit.get("type") == "working":
            return hit.get("text")
    return None


def seed_customer(
    customer_ref: str,
    tier: str,
    city: str,
    past_tickets: list[str],
) -> None:
    """Seed semantic profile and episodic history for demos/tests."""
    add_memory(
        customer_ref,
        f"Customer {customer_ref} is on the '{tier}' tier, located in {city}.",
        "semantic",
        source="db_seed",
    )
    for ticket in past_tickets:
        add_memory(customer_ref, ticket, "episodic", source="db_seed")

    mem = _client()
    ns = _ns(customer_ref)
    for _ in range(20):
        if mem.search.memories(q="ticket", container_tag=ns, limit=1).results:
            break
        time.sleep(3)


def summarize_turns(turns, prev_summary: str = "") -> str:
    """Compress old turns into a short rolling summary."""
    try:
        import litellm
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "litellm is not installed. Install it to generate working-memory summaries."
        ) from exc

    convo = "\n".join(f'{t["role"]}: {t["content"]}' for t in turns)
    system = (
        "You maintain a running summary of a conversation. Update the existing summary with the "
        "new turns, preserving concrete facts (names, numbers, preferences). Return only the "
        "updated summary, under 100 words."
    )
    user = (
        f"Existing summary:\n{prev_summary or '(none)'}\n\n"
        f"New turns:\n{convo}\n\nUpdated summary:"
    )
    resp = litellm.completion(
        model=DEFAULT_MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return resp.choices[0].message.content.strip()


def token_count(text: str) -> int:
    """Count tokens exactly when possible, otherwise use a simple fallback."""
    try:
        import tiktoken

        return len(tiktoken.get_encoding("cl100k_base").encode(text))
    except Exception:
        return max(1, len(text) // 4)
