"""Single FastMCP server exposing all ShopSense M2 order tools."""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastmcp import FastMCP

from reliability.circuit_breaker import CircuitBreaker, with_circuit_breaker
from reliability.retry import retry
from schemas import (
    CalculateRefundAmountArgs,
    LookupOrderArgs,
    ProcessRefundArgs,
    ReplaceItemArgs,
    TrackShipmentArgs,
)
from services import order_service

mcp = FastMCP("ShopSense Order Actions")

# One breaker per dependency/tool.
breakers = {
    name: CircuitBreaker(failure_threshold=3, recovery_timeout_seconds=30)
    for name in [
        "lookup_order",
        "calculate_refund_amount",
        "process_refund",
        "replace_item",
        "track_shipment",
    ]
}


def reliable(tool_name: str):
    """Apply retry first, then circuit-breaker accounting."""
    def decorator(fn):
        retried = retry(max_attempts=3)(fn)
        return with_circuit_breaker(breakers[tool_name])(retried)
    return decorator


@mcp.tool()
@reliable("lookup_order")
def lookup_order(order_ref: str) -> dict:
    """Look up an order with customer and product information."""
    print("lookup_order")
    validated = LookupOrderArgs.model_validate({"order_ref": order_ref})
    return order_service.lookup_order(validated.order_ref)


@mcp.tool()
@reliable("calculate_refund_amount")
def calculate_refund_amount(order_ref: str, quantity: int) -> dict:
    """Calculate the full item-value refund amount.

    Use this before process_refund when refund amount is unknown.
    """
    validated = CalculateRefundAmountArgs.model_validate(
        {"order_ref": order_ref, "quantity": quantity}
    )
    return order_service.calculate_refund_amount(
        validated.order_ref, validated.quantity
    )


@mcp.tool()
@reliable("process_refund")
def process_refund(
    order_ref: str,
    amount_inr: float,
    reason_code: str,
) -> dict:
    """Process a refund.

    Auto-processing is capped at ₹2,000.
    Larger valid refunds are escalated for human review.
    """
    validated = ProcessRefundArgs.model_validate(
        {
            "order_ref": order_ref,
            "amount_inr": amount_inr,
            "reason_code": reason_code,
        }
    )
    return order_service.process_refund(
        validated.order_ref, validated.amount_inr, validated.reason_code
    )


@mcp.tool()
@reliable("replace_item")
def replace_item(
    order_ref: str,
    sku: str,
    quantity: int,
    reason_code: str,
) -> dict:
    """Request replacement for a specific order item."""
    validated = ReplaceItemArgs.model_validate(
        {
            "order_ref": order_ref,
            "sku": sku,
            "quantity": quantity,
            "reason_code": reason_code,
        }
    )
    return order_service.replace_item(
        validated.order_ref,
        validated.sku,
        validated.quantity,
        validated.reason_code,
    )


@mcp.tool()
@reliable("track_shipment")
def track_shipment(order_ref: str) -> dict:
    """Get the latest shipment tracking information."""
    validated = TrackShipmentArgs.model_validate({"order_ref": order_ref})
    return order_service.track_shipment(validated.order_ref)


if __name__ == "__main__":
    mcp.run()

