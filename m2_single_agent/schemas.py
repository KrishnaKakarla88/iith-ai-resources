"""Shared request schemas for ShopSense M2 order tools."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class LookupOrderArgs(StrictBaseModel):
    order_ref: str = Field(..., min_length=1)


class CalculateRefundAmountArgs(StrictBaseModel):
    order_ref: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0)


class ProcessRefundArgs(StrictBaseModel):
    order_ref: str = Field(..., min_length=1)
    amount_inr: float = Field(..., gt=0)
    reason_code: Literal[
        "damaged",
        "wrong_item",
        "not_delivered",
        "changed_mind",
        "quality",
        "late_delivery",
    ]


class ReplaceItemArgs(StrictBaseModel):
    order_ref: str = Field(..., min_length=1)
    sku: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0)
    reason_code: Literal[
        "damaged",
        "wrong_item",
        "quality",
        "missing_item",
    ]


class TrackShipmentArgs(StrictBaseModel):
    order_ref: str = Field(..., min_length=1)


TOOL_SCHEMAS = {
    "lookup_order": LookupOrderArgs,
    "calculate_refund_amount": CalculateRefundAmountArgs,
    "process_refund": ProcessRefundArgs,
    "replace_item": ReplaceItemArgs,
    "track_shipment": TrackShipmentArgs,
}