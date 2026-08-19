from __future__ import annotations

from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.errors import GraphRecursionError
from typing import TypedDict, Annotated
from operator import add

class StudentState(TypedDict):
    student_id: str    
    grade: str
    log: Annotated[list[str], add]

def grader(state: MessagesState):
    return {"log": ["grader invoked "]}

def call_A(state: MessagesState):
    return {"log": ["call_A invoked "], "grade": "A"}

def call_B(state: MessagesState):
    return {"log": ["call_B invoked "], "grade": "B"}

def call_C(state: MessagesState):
    return {"log": ["call_C invoked "], "grade": "C"}

# Conditional edge function to route to the appropriate node
def route_decision(state: StudentState):
    # Return the node name you want to visit next
    if state["grade"] == "A":
        return "call_A"
    elif state["grade"] == "B":
        return "call_B"
    elif state["grade"] == "C":
            return "call_C"

graph  = StateGraph(StudentState)

# Add nodes
graph.add_node("call_A", call_A)
graph.add_node("call_B", call_B)
graph.add_node("call_C", call_C)
graph.add_node("grader", grader)

# Add conditional edge
graph.add_conditional_edges("grader", route_decision, {
     "call_A": "call_A",
     "call_B": "call_B", 
     "call_C": "call_C"
})

# Add edges
graph.add_edge(START, "grader")
graph.add_edge("call_A", END)
graph.add_edge("call_B", END)
graph.add_edge("call_C", END)

try:    
    agent = graph.compile()    
    final = agent.invoke({"grade": "C", "student_id": "12345"})        
    # print("Final state after invoking the agent:", final)
except GraphRecursionError as e:
    print(e)

# # # Show the agent
# print(agent.get_graph(xray=True).draw_mermaid())

# Show Nodes
print()
print("nodes :", sorted(n for n in agent.get_graph().nodes if not n.startswith("__")))
print()

print("=== updates mode: what each node WROTE ===")
for chunk in agent.stream({"grade": "C", "student_id": "12345"}, stream_mode="updates"):
    for node_name, update in chunk.items():
        print(f"  {node_name:>10} -> {update}")

print()
print("\n=== values mode: the FULL state after each superstep ===")
for i, snapshot in enumerate(agent.stream({"grade": "C", "student_id": "12345"}, stream_mode="values")):
    print(f"  step {i}: grade={snapshot.get('grade')} "
          f"student_id={snapshot.get('student_id')} log={snapshot.get('log')}")
    
