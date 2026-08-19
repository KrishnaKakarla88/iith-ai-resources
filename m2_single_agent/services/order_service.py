"""Business logic for ShopSense order actions.

This module knows nothing about MCP or LLMs.
It reads/writes the generated CSV files only.
"""
from __future__ import annotations

import uuid
from datetime import date
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "shopsense" / "mock_api"

ORDERS_CSV = DATA_DIR / "orders.csv"
PRODUCTS_CSV = DATA_DIR / "products.csv"
CUSTOMERS_CSV = DATA_DIR / "customers.csv"
SHIPMENTS_CSV = DATA_DIR / "shipments.csv"
REFUNDS_CSV = DATA_DIR / "refunds.csv"
REPLACEMENTS_CSV = DATA_DIR / "replacements.csv"

AUTO_REFUND_CAP_INR = 2_000

REFUND_REASONS = {
    "damaged", "wrong_item", "not_delivered",
    "changed_mind", "quality", "late_delivery",
}
REPLACEMENT_REASONS = {"damaged", "wrong_item", "quality", "missing_item"}

REPLACEMENT_COLUMNS = [
    "replacement_id", "order_ref", "sku", "quantity",
    "reason_code", "status", "requested_on",
]


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Required data file not found: {path}")
    return pd.read_csv(path)


def _order_row(order_ref: str) -> dict:
    orders = _read_csv(ORDERS_CSV)
    match = orders[orders["order_ref"] == order_ref]
    if match.empty:
        raise ValueError(f"Order '{order_ref}' not found.")
    return match.iloc[0].to_dict()


def lookup_order(order_ref: str) -> dict:
    """Return order details enriched with product and customer data."""
    order = _order_row(order_ref)

    products = _read_csv(PRODUCTS_CSV)
    product_match = products[products["sku"] == order["sku"]]

    customers = _read_csv(CUSTOMERS_CSV)
    customer_match = customers[
        customers["customer_ref"] == order["customer_ref"]
    ]

    result = {"order": order}
    result["product"] = (
        product_match.iloc[0].to_dict() if not product_match.empty else None
    )
    result["customer"] = (
        customer_match.iloc[0].to_dict() if not customer_match.empty else None
    )
    return result


def track_shipment(order_ref: str) -> dict:
    """Return latest shipment information for an order."""
    _order_row(order_ref)

    shipments = _read_csv(SHIPMENTS_CSV)
    match = shipments[shipments["order_ref"] == order_ref]

    if match.empty:
        return {
            "order_ref": order_ref,
            "status": "not_found",
            "message": "No shipment tracking record found.",
        }

    return match.iloc[0].to_dict()


def calculate_refund_amount(order_ref: str, quantity: int) -> dict:
    """Calculate a full item-value refund for requested quantity."""
    if quantity <= 0:
        raise ValueError("Refund quantity must be greater than zero.")

    order = _order_row(order_ref)
    ordered_quantity = int(order["quantity"])

    if quantity > ordered_quantity:
        raise ValueError(
            f"Refund quantity {quantity} exceeds ordered quantity "
            f"{ordered_quantity}."
        )

    order_value = float(order["order_value_inr"])
    unit_price = order_value / ordered_quantity
    refund_amount = round(unit_price * quantity, 2)

    return {
        "order_ref": order_ref,
        "ordered_quantity": ordered_quantity,
        "refund_quantity": quantity,
        "unit_price_inr": round(unit_price, 2),
        "refund_amount_inr": refund_amount,
    }


def process_refund(
    order_ref: str,
    amount_inr: float,
    reason_code: str,
) -> dict:
    """Process or escalate a refund using deterministic guardrails."""
    order = _order_row(order_ref)

    if amount_inr <= 0:
        raise ValueError("Refund amount must be greater than zero.")

    if reason_code not in REFUND_REASONS:
        raise ValueError(
            f"Invalid refund reason '{reason_code}'. "
            f"Allowed: {sorted(REFUND_REASONS)}"
        )

    order_value = float(order["order_value_inr"])
    if amount_inr > order_value:
        raise ValueError(
            f"Refund INR {amount_inr:,.2f} exceeds order value "
            f"INR {order_value:,.2f}."
        )

    if amount_inr > AUTO_REFUND_CAP_INR:
        return {
            "status": "escalated",
            "order_ref": order_ref,
            "amount_inr": amount_inr,
            "reason_code": reason_code,
            "approved_by": None,
            "message": (
                f"Refund INR {amount_inr:,.2f} exceeds auto-approval cap "
                f"INR {AUTO_REFUND_CAP_INR:,.2f}. Human review required."
            ),
        }

    refunds = _read_csv(REFUNDS_CSV)
    refund_id = f"KW-RF-{uuid.uuid4().hex[:8].upper()}"

    row = {
        "refund_id": refund_id,
        "order_ref": order_ref,
        "amount_inr": amount_inr,
        "reason_code": reason_code,
        "status": "processed",
        "approved_by": "auto",
        "requested_on": date.today().isoformat(),
    }

    refunds = pd.concat([refunds, pd.DataFrame([row])], ignore_index=True)
    refunds.to_csv(REFUNDS_CSV, index=False)

    return {
        **row,
        "message": f"Refund INR {amount_inr:,.2f} processed.",
    }


def replace_item(
    order_ref: str,
    sku: str,
    quantity: int,
    reason_code: str,
) -> dict:
    """Create an item-level replacement request."""
    if quantity <= 0:
        raise ValueError("Replacement quantity must be greater than zero.")

    if reason_code not in REPLACEMENT_REASONS:
        raise ValueError(
            f"Invalid replacement reason '{reason_code}'. "
            f"Allowed: {sorted(REPLACEMENT_REASONS)}"
        )

    order = _order_row(order_ref)

    if order["sku"] != sku:
        raise ValueError(f"SKU '{sku}' does not belong to order '{order_ref}'.")

    if quantity > int(order["quantity"]):
        raise ValueError(
            f"Replacement quantity {quantity} exceeds ordered quantity "
            f"{int(order['quantity'])}."
        )

    products = _read_csv(PRODUCTS_CSV)
    product_match = products[products["sku"] == sku]
    if product_match.empty:
        raise ValueError(f"Product '{sku}' not found.")

    in_stock = str(product_match.iloc[0]["in_stock"]).lower() == "true"
    if not in_stock:
        return {
            "status": "unavailable",
            "order_ref": order_ref,
            "sku": sku,
            "quantity": quantity,
            "message": "Replacement unavailable because item is out of stock.",
        }

    if REPLACEMENTS_CSV.exists():
        replacements = pd.read_csv(REPLACEMENTS_CSV)
    else:
        replacements = pd.DataFrame(columns=REPLACEMENT_COLUMNS)

    replacement_id = f"KW-RP-{uuid.uuid4().hex[:8].upper()}"
    row = {
        "replacement_id": replacement_id,
        "order_ref": order_ref,
        "sku": sku,
        "quantity": quantity,
        "reason_code": reason_code,
        "status": "approved",
        "requested_on": date.today().isoformat(),
    }

    replacements = pd.concat(
        [replacements, pd.DataFrame([row])], ignore_index=True
    )
    replacements.to_csv(REPLACEMENTS_CSV, index=False)

    return {
        **row,
        "message": f"Replacement {replacement_id} approved.",
    }
