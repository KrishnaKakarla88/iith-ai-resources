"""Shared helper utilities for the ShopSense M2 order agent."""
from __future__ import annotations

import os
import re

from pydantic import ValidationError

from schemas import TOOL_SCHEMAS

ORDER_REF_PATTERN = re.compile(r"\bKW-O-[0-9]{3,}\b", re.IGNORECASE)

ACTION_KEYWORDS = {
    "track": (
        "track",
        "tracking",
        "status",
        "shipment",
        "delivery",
        "where",
    ),
    "refund": (
        "refund",
        "return",
        "money back",
    ),
    "replace": (
        "replace",
        "replacement",
        "exchange",
    ),
    "details": (
        "details",
        "detail",
        "show",
        "check",
        "items",
    ),
}

REASON_PHRASES = {
    "damaged": (
        "damaged",
        "damage",
        "broken",
        "defective",
        "cracked",
    ),
    "wrong_item": (
        "wrong item",
        "incorrect item",
        "different item",
        "not what i ordered",
        "not what i expected",
    ),
    "not_delivered": (
        "not delivered",
        "didn't arrive",
        "never arrived",
        "not received",
    ),
    "changed_mind": (
        "changed mind",
        "change of mind",
        "no longer need",
        "dont want",
        "don't want",
    ),
    "quality": (
        "quality",
        "poor quality",
        "bad quality",
    ),
    "late_delivery": (
        "late",
        "delayed",
        "delay",
    ),
    "missing_item": (
        "missing item",
        "item missing",
        "missing",
    ),
}

TOOL_REASON_CODES = {
    "process_refund": {
        "damaged",
        "wrong_item",
        "not_delivered",
        "changed_mind",
        "quality",
        "late_delivery",
    },
    "replace_item": {
        "damaged",
        "wrong_item",
        "quality",
        "missing_item",
    },
}


def validation_follow_up(tool_name: str, exc: ValidationError) -> str:
    invalid_fields = sorted(
        {
            str(err["loc"][-1])
            for err in exc.errors()
            if err.get("loc")
        }
    )
    fields_text = ", ".join(invalid_fields) or "required fields"

    tool_schema = TOOL_SCHEMAS.get(tool_name)
    if tool_schema is None:
        return (
            f"I need valid values for: {fields_text}. "
            "Please provide those details and I will continue."
        )

    required_fields = [
        name
        for name, field in tool_schema.model_fields.items()
        if field.is_required()
    ]
    required_text = ", ".join(required_fields) or "required fields"
    return (
        f"I need valid values for: {fields_text}. "
        f"Required fields for {tool_name}: {required_text}. "
        "Please provide those details and I will continue."
    )


def lookup_order_follow_up() -> str:
    return (
        "Please share your order reference (for example, KW-O-000123) so I can continue."
    )


def action_follow_up(order_ref: str | None = None) -> str:
    if order_ref:
        return (
            f"I found order reference {order_ref}. "
            "Please tell me what you want to do: track shipment, refund, replacement, or order details."
        )
    return (
        "Please tell me what you want to do: track shipment, refund, replacement, or order details."
    )


def extract_order_refs(text: str) -> set[str]:
    if not text:
        return set()
    return {match.group(0).upper() for match in ORDER_REF_PATTERN.finditer(text)}


def is_grounded_lookup_ref(customer_message: str, order_ref: str) -> bool:
    if not customer_message or not order_ref:
        return False
    return order_ref.upper() in extract_order_refs(customer_message)


def needs_order_ref_before_llm(customer_message: str) -> bool:
    lower = customer_message.lower()
    action_keywords = (
        "order",
        "status",
        "track",
        "shipment",
        "delivery",
        "refund",
        "replace",
    )
    return any(keyword in lower for keyword in action_keywords)


def has_action_intent(customer_message: str) -> bool:
    lower = customer_message.lower()
    for keywords in ACTION_KEYWORDS.values():
        if any(keyword in lower for keyword in keywords):
            return True
    return False


def pre_llm_grounding_follow_up(customer_message: str) -> str | None:
    if not customer_message:
        return None

    refs = sorted(extract_order_refs(customer_message))
    action_intent = has_action_intent(customer_message)

    # If user only gave an order ref, require explicit intent before tool selection.
    if refs and not action_intent:
        return action_follow_up(refs[0])

    if needs_order_ref_before_llm(customer_message):
        if not refs:
            return lookup_order_follow_up()

    return None


def infer_reason_code(customer_message: str, tool_name: str) -> str | None:
    allowed_codes = TOOL_REASON_CODES.get(tool_name)
    if not customer_message or not allowed_codes:
        return None

    lower = customer_message.lower()
    for code, phrases in REASON_PHRASES.items():
        if code not in allowed_codes:
            continue
        if any(phrase in lower for phrase in phrases):
            return code
    return None


def enrich_tool_args(tool_name: str, tool_args: dict, customer_message: str) -> dict:
    args = dict(tool_args)
    if "reason_code" in args:
        return args

    inferred_reason = infer_reason_code(customer_message, tool_name)
    if inferred_reason:
        args["reason_code"] = inferred_reason

    return args


def build_reason_hint(customer_message: str) -> str | None:
    """Return a prompt hint when the user already gave an actionable reason."""
    reason_code = infer_reason_code(customer_message, "process_refund")
    if reason_code:
        return (
            f"Detected refund reason_code={reason_code} from the customer's message. "
            "Treat it as provided and do not ask the customer to repeat the refund reason."
        )

    reason_code = infer_reason_code(customer_message, "replace_item")
    if reason_code:
        return (
            f"Detected replacement reason_code={reason_code} from the customer's message. "
            "Treat it as provided and do not ask the customer to repeat the replacement reason."
        )

    return None


def build_llm():
    from langchain_litellm import ChatLiteLLM

    model = os.getenv("LLM_MODEL", "groq/llama-3.1-8b-instant")
    return ChatLiteLLM(
        model=model,
        api_key=os.getenv("LLM_API_KEY") or os.getenv("GROQ_API_KEY"),
        temperature=0,
        max_retries=2,
    )
