from __future__ import annotations

from langgraph.graph import add_messages, StateGraph, START, END
from typing import TypedDict, Annotated
from operator import add

# Pattern 5 - MULTI-AGENT.  Use case: enterprise contract review.
# legal / finance / compliance fan OUT (run in parallel), then a merge node fans IN.
CONTRACT = """MASTER SERVICES AGREEMENT (extract)
7. Liability. Supplier's aggregate liability is unlimited for any breach of this agreement.
9. Payment. Fees are payable net-90 from invoice date, in advance of delivery.
14. Data. Customer data may be processed in any jurisdiction at Supplier's discretion."""

class ContractState(TypedDict):
    contract: str
    reads: Annotated[list, add]     # each specialist APPENDS; the reducer merges concurrent writes
    memo: str


def specialist(role: str, brief: str, fallback: str):
    """One factory, three agents. Each gets a NARROW system prompt - that scoping IS the
    'specialisation'; there is no other magic in a multi-agent system."""
    def node(state: ContractState) -> dict:
        # In a real system, this would be a call to an LLM. Here we just simulate it.
        content = f"{role} read the contract and wrote: {brief}"
        return {"reads": [f"{role}: {fallback}"]}
    return node

def merge(state: ContractState) -> dict:
    return {"memo": "\n  ".join(sorted(state["reads"]))}

legal      = specialist("legal", "You care about liability, indemnity and termination.",
                        "clause 7 unlimited liability exceeds playbook risk")
finance    = specialist("finance", "You care about payment terms and cash exposure.",
                        "clause 9 net-90 in advance, exposure high")
compliance = specialist("compliance", "You care about data residency and sanctions.",
                        "clause 14 unrestricted jurisdiction breaks data residency")

graph = StateGraph(ContractState)

for name, fn in [("legal", legal), ("finance", finance), ("compliance", compliance), ("merge", merge)]:
    graph.add_node(name, fn)
for spec in ("legal", "finance", "compliance"):
    graph.add_edge(START, spec)         # fan OUT - all three specialists start in the SAME superstep
    graph.add_edge(spec, "merge")       # fan IN  - merge waits for all three to finish
graph.add_edge("merge", END)

agent = graph.compile()

result = agent.invoke({"contract": CONTRACT, "reads": [], "memo": ""})
print("merged memo:\n  " + result["memo"])

print(agent.get_graph(xray=True).draw_mermaid())