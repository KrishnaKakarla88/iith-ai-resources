"""Bridge helpers that connect the M2 order agent to M3 memory."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.agent_helpers import extract_order_refs
from milestones.m2_single_agent.services.order_service import lookup_order
from milestones.m3_memory.memory.customer import (
    recall_formatted,
    recall_working,
    store_episodic,
    store_working,
    summarize_turns,
)

_SESSION_WORKING_SUMMARIES: dict[str, str] = {}
_SESSION_RECENT_TURNS: dict[str, list[dict[str, str]]] = {}


def resolve_customer_ref(customer_message: str) -> str | None:
    """Resolve a customer_ref from the order reference in the message."""
    refs = sorted(extract_order_refs(customer_message))
    if not refs:
        return None

    try:
        lookup = lookup_order(refs[0])
    except Exception:
        return None

    customer = lookup.get("customer") or {}
    if customer.get("customer_ref"):
        return str(customer["customer_ref"])

    order = lookup.get("order") or {}
    if order.get("customer_ref"):
        return str(order["customer_ref"])

    return None


def load_working_summary(customer_ref: str) -> str:
    """Load the latest rolling summary from session memory or M3 storage."""
    if customer_ref in _SESSION_WORKING_SUMMARIES:
        return _SESSION_WORKING_SUMMARIES[customer_ref]

    try:
        working = recall_working(customer_ref)
    except Exception:
        working = None

    if working:
        _SESSION_WORKING_SUMMARIES[customer_ref] = working
        return working

    return ""


def build_memory_context(
    customer_ref: str,
    customer_message: str,
    max_hits: int = 4,
) -> str | None:
    """Create a prompt-ready memory block for the current turn."""
    summary = load_working_summary(customer_ref)

    try:
        history = recall_formatted(customer_ref, customer_message, k=max_hits)
    except Exception:
        history = "No prior interaction history found for this customer."

    blocks: list[str] = []
    if summary:
        blocks.append(f"Working memory summary:\n{summary}")
    if history and history != "No prior interaction history found for this customer.":
        blocks.append(history)

    if not blocks:
        return None

    return "Customer memory context:\n" + "\n\n".join(blocks)


def _update_session_summary(customer_ref: str, turns: list[dict[str, str]]) -> str:
    previous_summary = load_working_summary(customer_ref)

    try:
        summary = summarize_turns(turns, previous_summary)
    except Exception:
        summary_lines = [previous_summary] if previous_summary else []
        summary_lines.extend(
            f"{turn['role']}: {turn['content']}" for turn in turns[-4:]
        )
        summary = " | ".join(line for line in summary_lines if line).strip()

    _SESSION_WORKING_SUMMARIES[customer_ref] = summary

    try:
        store_working(customer_ref, summary, source="session_summary")
    except Exception:
        pass

    return summary


def remember_turn(
    customer_ref: str,
    customer_message: str,
    assistant_message: str,
) -> str:
    """Store the latest exchange in episodic and working memory."""
    turns = _SESSION_RECENT_TURNS.setdefault(customer_ref, [])
    turns.extend(
        [
            {"role": "user", "content": customer_message},
            {"role": "assistant", "content": assistant_message},
        ]
    )
    if len(turns) > 8:
        del turns[:-8]

    try:
        store_episodic(
            customer_ref,
            f"User: {customer_message}\nAssistant: {assistant_message}",
            source="session_turn",
        )
    except Exception:
        pass

    return _update_session_summary(customer_ref, turns)
