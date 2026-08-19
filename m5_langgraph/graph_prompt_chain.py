from __future__ import annotations

from langgraph.graph import StateGraph, START, END
from langgraph.errors import GraphRecursionError
from typing import TypedDict
from pydantic import BaseModel, Field

class InvoiceState(TypedDict):
    raw: str
    fields: dict
    valid: bool
    posted: bool

class InvoiceFields(BaseModel):    
    po: str      = Field(description="purchase order reference, e.g. PO-1234")
    amount: float = Field(description="invoice total as a number, no currency symbol or commas")
    vendor: str  = Field(description="vendor name, one or two words")

RAW_INVOICE = """ACME Northgate Supplies Ltd
Invoice INV-88213   PO Reference: PO-4471
Line total ................ 1,290.00 USD"""

def extract(state: InvoiceState) -> dict:    
    return {"fields": {"po": "PO-4471", "amount": 1290.0, "vendor": "Northgate"}}

def validate(state: InvoiceState) -> dict:
    return {"valid": state["fields"]["amount"] < 5000}

def post(state: InvoiceState) -> dict:
    return {"posted": state["valid"]}

graph  = StateGraph(InvoiceState)

# Add nodes
graph.add_node("extract", extract)
graph.add_node("validate", validate)
graph.add_node("post", post)

# Add edges
graph.add_edge(START, "extract")
graph.add_edge("extract", "validate")
graph.add_edge("validate", "post")
graph.add_edge("post", END)

try:
    agent = graph.compile()
    final = agent.invoke({"raw": RAW_INVOICE, "fields": {}, "valid": False, "posted": False}, {"recursion_limit": 50})
    print("Final state after invoking the agent:", final)
except GraphRecursionError as e:
    print(e)

# # Show the agent
print(agent.get_graph(xray=True).draw_mermaid())