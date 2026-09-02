--- LINKEDIN ---
LangChain and LangGraph aren't two competing frameworks to pick between forever — as of LangChain 1.0, LangChain's own agent runtime is built on LangGraph. The real decision is narrower than it looks: chain vs. graph.

Does every run visit the same steps, in the same order, to completion? A chain (LCEL) is enough. Does the model need to decide which tool to call and when to stop, in a standard loop? LangChain's create_agent — a pre-built agent running on LangGraph, no custom graph code needed. Does the workflow need conditional routing, a human pause, multiple specialized agents, or resumability after a crash? Raw LangGraph — StateGraph, custom nodes and edges.

The fixed-order case needs neither an agent nor a graph:
invoice_data = chat_model.with_structured_output(InvoiceSchema).invoke(raw_text)
if not validate(invoice_data): raise ValueError(...)
post(invoice_data)
Only extract calls the model — paying a model for a rule or an arithmetic check buys only variance.

When the model should genuinely decide the next step:
agent = create_agent(model="groq:llama-3.1-8b-instant", tools=[...], system_prompt="...")
This replaces the older AgentExecutor/create_tool_calling_agent pattern, now maintenance-only per current LangChain docs.

Drop down to raw LangGraph only when you need control create_agent doesn't expose: custom state fields beyond messages, non-standard conditional routing, multiple cooperating agents with their own read/write scopes, or checkpointing wired at points a pre-built agent loop doesn't pause at.

Is your agent actually deciding routing, or is it a chain wearing an agent's clothes?

#AppliedAI #LangGraph #LangChain #AIEngineering

--- INSTAGRAM ---
LangChain runs on LangGraph. It's not a rivalry. 🔗

Same steps, same order every time? Chain. Model decides which tool + when to stop? create_agent. Branching, human pause, multiple agents, resumability? Raw LangGraph.

agent = create_agent(model="groq:llama-3.1-8b-instant", tools=[...])

Paying a model for a fixed rule check buys only variance.

Full decision guide in the carousel.

#AppliedAI #LangGraph #LangChain #AIEngineering #GenAI

--- VISUAL FORMAT ---
carousel — 6 slides
1. Title — "Not A Rivalry — LangChain Runs On LangGraph"
2. Three questions, three answers
3. Sample code — the fixed-order case doesn't need either (code)
4. When the model should decide — create_agent (code)
5. When to drop down — raw LangGraph
6. Takeaway — the fastest test (closing question)
