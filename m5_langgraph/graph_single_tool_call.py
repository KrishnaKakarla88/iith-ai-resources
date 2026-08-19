from __future__ import annotations

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage, AIMessage
from langgraph.graph import add_messages, StateGraph, START, END
from typing import TypedDict, Annotated

@tool
def news_search(supplier: str) -> str:
    """Search recent news for adverse coverage about a supplier."""
    return f"{supplier}: no adverse news in the last 12 months."

@tool
def sanctions_list(supplier: str) -> str:
    """Check a supplier against sanctions and watchlists."""
    return f"{supplier}: not present on any sanctions list."

@tool
def past_contracts(supplier: str) -> str:
    """Look up our own contract history with a supplier."""
    return f"{supplier}: 2 prior contracts, no disputes."

RESEARCH_TOOLS = [news_search, sanctions_list, past_contracts]
TOOLS_BY_NAME  = {t.name: t for t in RESEARCH_TOOLS}
MAX_TOOL_STEPS = 6          # a cost/latency ceiling: an agent loop with no cap is an open invoice

def agent(state: ResearchState) -> dict:
    """The policy node: look at everything so far, decide to call a tool or to answer."""
    
    used = {m.name for m in state["messages"] if isinstance(m, ToolMessage)}
    todo = [t.name for t in RESEARCH_TOOLS if t.name not in used]
    if todo:
        return {"messages": [AIMessage(content="", tool_calls=[
            {"name": todo[0], "args": {"supplier": "Northgate Pay"}, "id": f"call_{todo[0]}"}])]}
    return {"messages": [AIMessage(content="Northgate Pay: low risk (3 sources checked).")]}

def tools_node(state: ResearchState) -> dict:
    """Execute every tool the model asked for. langgraph.prebuilt.ToolNode does exactly this -
    we hand-roll it once so the mechanism is not magic (see the ReAct cell for the prebuilt)."""
    calls = state["messages"][-1].tool_calls
    return {"messages": [
        # name= is optional for the provider but makes the observation self-describing when you
        # (or a fallback policy) read the message list back.
        ToolMessage(content=TOOLS_BY_NAME[c["name"]].invoke(c["args"]),
                    tool_call_id=c["id"], name=c["name"])
        for c in calls]}

def keep_going(state: ResearchState) -> str:
    """Continuation is decided by the MODEL (did it ask for a tool?), bounded by YOU (the cap)."""
    last = state["messages"][-1]
    if getattr(last, "tool_calls", None) and len(state["messages"]) < MAX_TOOL_STEPS * 2:
        return "tools"
    return END

class ResearchState(TypedDict):
    messages: Annotated[list, add_messages]


graph = StateGraph(ResearchState)

graph.add_node("agent", agent)
graph.add_node("tools", tools_node)

graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", keep_going, {"tools": "tools", END: END})
graph.add_edge("tools", "agent")

agent = graph.compile()

result = agent.invoke({"messages": [
    SystemMessage(content="You assess supplier risk. Use every tool available to you exactly once, "
                          "then write a one-sentence risk memo."),
    HumanMessage(content="Assess the supplier 'Northgate Pay'.")]})

for m in result["messages"]:
    kind = type(m).__name__
    detail = getattr(m, "tool_calls", None) or (m.content[:70] if m.content else "")
    print(f"  {kind:<12} {detail}")

print(agent.get_graph(xray=True).draw_mermaid())