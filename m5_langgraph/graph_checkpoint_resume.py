from __future__ import annotations

from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.errors import GraphRecursionError
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command
from typing import TypedDict, Annotated
from operator import add
from pydantic import BaseModel, Field

MAX_REVISIONS     = 3
REQUIRED_SECTIONS = ["Purpose", "Scope", "Effective Date"]
BANNED_TERMS      = ["guaranteed", "risk-free"]
MAX_WORDS         = 150

class InvoiceState(TypedDict):
    raw: str
    fields: dict
    valid: bool
    posted: bool
    revision_count: int
    issues: list[str]
    status: str
    approver_note: str
    log: Annotated[list[str], add]

class InvoiceFields(BaseModel):    
    po: str      = Field(description="purchase order reference, e.g. PO-1234")
    amount: float = Field(description="invoice total as a number, no currency symbol or commas")
    vendor: str  = Field(description="vendor name, one or two words")

RAW_INVOICE = """ACME Northgate Supplies Ltd
Invoice INV-88213   PO Reference: PO-4471
Line total ................ 4,200.00 USD"""

def extract(state: InvoiceState) -> dict:
    return {"fields": {"po": "PO-4471", "amount": 4200.0, "vendor": "Northgate"},
            "log": ["extract: parsed fields from raw invoice"]}

def validate(state: InvoiceState) -> dict:
    amount = state["fields"]["amount"]
    valid = amount < 5000
    issues = [] if valid else [f"amount {amount} exceeds 5000 threshold"]
    return {"valid": valid, "issues": issues,
            "log": [f"validate: amount={amount} valid={valid}"]}

def post(state: InvoiceState) -> dict:
    return {"posted": state["valid"], "log": [f"post: posted={state['valid']}"]}

def human_approval_node(state: InvoiceState) -> dict:
    # interrupt() raises a RESUMABLE pause. The payload is handed to the caller under the
    # "__interrupt__" key; whatever the caller later sends back via Command(resume=...) becomes
    # the RETURN VALUE of this call. Everything must be JSON-serialisable, both ways.
    decision = interrupt({
        "question": "Approve this invoice?",
        "outstanding_issues": state["issues"],
        "revisions_attempted": state["revision_count"],
    })

    # Write the human's decision into state. Supported actions: "approved" | "rejected" | "changes_requested".
    action = decision["action"]
    bump = 1 if action == "changes_requested" else 0
    return {"status": action,
            "approver_note": decision.get("note", ""),
            "revision_count": state.get("revision_count", 0) + bump,
            "log": [f"human_approval: {action}"]}

def route_after_validate(state: InvoiceState) -> str:    
    if state["valid"]:
        return "post"    
    return "human_approval"    

def route_after_human(state: InvoiceState) -> str:
    status = state["status"]
    if status == "approved":
        return "post"
    if status == "changes_requested" and state.get("revision_count", 0) < MAX_REVISIONS:
        return "extract"                        # revise and re-validate
    return "end"                                # rejected, or revisions exhausted

graph  = StateGraph(InvoiceState)

# Add nodes
graph.add_node("extract", extract)
graph.add_node("validate", validate)
graph.add_node("human_approval", human_approval_node)
graph.add_node("post", post)

# Add edges
graph.add_edge(START, "extract")
graph.add_edge("extract", "validate")
graph.add_conditional_edges("validate", route_after_validate,
                            {"post": "post", "human_approval": "human_approval"})
graph.add_conditional_edges("human_approval", route_after_human,
                            {"post": "post", "extract": "extract", "end": END})
graph.add_edge("post", END)

config = {"configurable": {"thread_id": "Inv-001"}, "recursion_limit": 50} 

try:    
    memory = InMemorySaver()
    agent = graph.compile(checkpointer=memory)
    
    final = agent.invoke({"raw": RAW_INVOICE, "fields": {}, "valid": False, "posted": False, "revision_count": 0, "issues": [], "status": "pending", "approver_note": ""}, config)
    print("Final state after invoking the agent:", final)

    # Checkpoint
    snap = agent.get_state(config)    
    print()
    print("current status :", snap.values["status"])
    print("pending nodes  :", snap.next, "  <- empty tuple means the run is complete")
    print("checkpoints    :", sum(1 for _ in agent.get_state_history(config)))

    print()
    print("\nTime travel (newest first) — every superstep left a snapshot:")
    for s in agent.get_state_history(config):
        print(f"  next={str(s.next):<14} "
            f"status={s.values.get('status')}")

    print()
    # The human finally answers - in a brand-new process.
    final1 = agent.invoke(Command(resume={"action": "approved", "approver_note": "Approved after restart."}), config)
    print("\nFinal status      :", final1["status"])
    print("approver_note       :", final1["approver_note"])
    print("audit trail         :", final1["log"])    

    print()
    print("\nTime travel (newest first) — every superstep left a snapshot:")
    for s in agent.get_state_history(config):
        print(f"  next={str(s.next):<14} "
            f"status={s.values.get('status')}")
except GraphRecursionError as e:
    print(e)

print()
# # # Show the agent
print(agent.get_graph(xray=True).draw_mermaid())

# Show Nodes
print()
print("nodes :", sorted(n for n in agent.get_graph().nodes if not n.startswith("__")))
print()