import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "Not A Rivalry — LangChain Runs On LangGraph",
      ["As of LangChain 1.0, LangChain's own agent runtime is built on LangGraph. The real decision is narrower: chain vs. graph."])

slide(p("slide-02.png"), 2, 6, "Three Questions, Three Answers", "Chain, Pre-Built Agent, Or Raw Graph",
      ["Same steps, same order, every run? A **chain** (LCEL).",
       "Model decides which tool and when to stop, in a standard loop? LangChain's **create_agent** — pre-built, runs on LangGraph.",
       "Conditional routing, a human pause, multiple agents, resumability? Raw **LangGraph** — StateGraph, custom nodes/edges."])

slide(p("slide-03.png"), 3, 6, "Sample Code", "The Fixed-Order Case Doesn't Need Either",
      ["**Example:** extract → validate → post. Only extract calls the model — paying a model for a rule check buys only variance."],
      code="invoice_data = chat_model.with_structured_output(InvoiceSchema).invoke(raw_text)\nif not validate(invoice_data):\n    raise ValueError(...)\npost(invoice_data)")

slide(p("slide-04.png"), 4, 6, "When The Model Should Decide", "create_agent Is The 2026 Default Entry Point",
      ["Replaces the older AgentExecutor/create_tool_calling_agent pattern, now maintenance-only."],
      code="from langchain.agents import create_agent\n\nagent = create_agent(\n    model=\"groq:llama-3.1-8b-instant\",\n    tools=[search_supplier_risk, lookup_contract],\n    system_prompt=\"Research supplier risk before recommending a decision.\",\n)")

slide(p("slide-05.png"), 5, 6, "When To Drop Down", "Raw LangGraph For Control create_agent Doesn't Expose",
      ["Custom state fields beyond messages, non-standard conditional routing, multiple cooperating agents with their own read/write scopes, checkpointing wired at points a pre-built loop doesn't pause at."])

slide(p("slide-06.png"), 6, 6, "Takeaway", "The Fastest Test: Same Steps, Same Order, Every Run?",
      ["If yes, a chain is enough — a graph's branching and checkpointing machinery goes unexercised."],
      closing_q="Is your agent actually deciding routing, or is it a chain wearing an agent's clothes?")

print("done: 63")
