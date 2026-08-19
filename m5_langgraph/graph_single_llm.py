from __future__ import annotations

from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.errors import GraphRecursionError
from typing import TypedDict, Annotated
from operator import add

class EmailState(TypedDict):
    email: str
    urgency: str

VALID_URGENCY = {"high", "normal"}

def classify_urgency(state: EmailState) -> dict:
    label = "High"
    # A model returns free text - "High.", " normal\n", "I would say high". NEVER let that reach
    # state raw. Squeeze it back into your typed vocabulary at the boundary, and keep a
    # deterministic fallback for when it does not fit (or when no model is available at all).
    label = (label or "").lower().strip(" .!\n")
    if label not in VALID_URGENCY:
        label = "high" if any(w in state["email"].lower()
                              for w in ("down", "urgent", "cannot", "outage")) else "normal"
    return {"urgency": label}

graph  = StateGraph(EmailState)

# Add nodes
graph.add_node("classify_urgency", classify_urgency)

# Add edges
graph.add_edge(START, "classify_urgency")
graph.add_edge("classify_urgency", END)

try:
    agent = graph.compile()
    final = agent.invoke({"email": "Production is DOWN, customers cannot check out!", "urgency": ""}, {"recursion_limit": 50})
    print("Final state after invoking the agent:", final)
except GraphRecursionError as e:
    print(e)

# # Show the agent
print(agent.get_graph(xray=True).draw_mermaid())