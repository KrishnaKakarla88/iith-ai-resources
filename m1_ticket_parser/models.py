from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from typing import Literal, Optional

class IssueType(str, Enum):
    refund = "refund"
    replacement = "replacement"
    tracking = "tracking"
    policy_question = "policy_question"
    other = "other"

class Sentiment(str, Enum):
    positive = "positive"
    neutral = "neutral"
    calm = "calm"
    frustrated = "frustrated"
    angry = "angry"
    distressed = "distressed"

class Channel(str, Enum):
    chat = "chat"
    email = "email"
    social = "social"
    app_review = "app_review"

class Urgency(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class Intent(str, Enum):
    track_order = "track_order"
    complaint = "complaint"
    return_request = "return_request"
    refund_request = "refund_request"
    product_information = "product_information"
    wrong_item = "wrong_item"
    delivery_delay = "delivery_delay"
    damaged_delivery = "damaged_delivery"
    cancel_order = "cancel_order"
    payment_issue = "payment_issue"

class Category(str, Enum):
    electronics = "Electronics"
    home_kitchen = "Home & Kitchen"
    apparel = "Apparel"
    toys = "Toys"

class GroundTruth(BaseModel):
    intent: Intent
    category: Category
    sentiment: Sentiment
    claimed_amount_inr: float | None = None
    requires_human: bool
    missing_fields: list[str]

class SupportTicket(BaseModel):
    ticket_id: Optional[str] = None
    channel: Channel | None = None
    received_at: datetime | None = None
    order_ref: str | None = None
    customer_ref: str | None = None
    raw_text: str = Field(description="≤30 word summary of customer's problem")
    ground_truth: GroundTruth | None = None
    record_id: str | None = None    
    customer_id: str | None = None    
    order_id: str | None = None
    issue_type: IssueType
    sentiment: Sentiment
    urgency: Urgency
    requires_human: bool = False