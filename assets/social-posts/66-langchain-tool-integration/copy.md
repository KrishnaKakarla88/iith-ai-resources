--- LINKEDIN ---
A model doesn't call a Python function — it emits a tool name plus JSON arguments, and your code dispatches that to the real function. LangChain's @tool decorator automates the bridge: it reads your function's type hints to build the schema the model is shown, and your docstring becomes the description the model uses to decide whether to call this tool at all.

@tool
def search_kb(query: str, limit: int = 5) -> list[dict]:
    """Search the internal knowledge base for policy documents matching query."""
    return kb_index.search(query, limit=limit)

Get the docstring vague and the tool becomes a broken integration that raises no error — the model just calls it wrongly, or never calls it, and nothing in your logs points at the docstring as the cause.

The same function isn't stuck as a local import. MultiServerMCPClient.get_tools() spawns, initializes, and discovers a running MCP server's tools, handing back ordinary LangChain tools indistinguishable from one defined locally:

client = MultiServerMCPClient({"project": {"transport": "stdio", "command": sys.executable, "args": [SERVER_PATH]}})
tools = await client.get_tools()

The gotcha that actually bit in a real incident: locally a tool returns a bare dict; over MCP the same call arrives wrapped as content blocks, [{"type": "text", "text": "<json>"}]. A successful refund call got reported to the customer as failed because an isinstance(result, dict) check was written against the wrong shape. Another one: always pass command=sys.executable, never a bare "python" string — a bare string resolves against whatever interpreter is first on PATH, and the failure looks like a protocol error, not the interpreter mismatch it actually is.

Normalize the result shape once, at the call boundary — not per consumer. An isinstance check against one SDK's shape is a version pin in disguise.

Would your tool-result handling survive an SDK version bump to the response shape?

#AppliedAI #LangChain #MCP #AIEngineering

--- INSTAGRAM ---
Your docstring is the API contract. Not documentation of one. 📝

@tool reads type hints for schema, docstring for "should I call this." Vague docstring = silent broken integration, no error.

Same function works locally and over MCP — but MCP wraps results as content blocks, not plain dicts. A real incident: a successful refund reported as failed over this exact mismatch.

Full mechanics in the carousel.

#AppliedAI #LangChain #MCP #AIEngineering #GenAI

--- VISUAL FORMAT ---
carousel — 6 slides
1. Title — "Your Docstring Is The API Contract, Not Documentation Of One"
2. Sample code — type hints become schema, docstring becomes the pitch (code)
3. The same function, discovered remotely (code)
4. The gotcha — MCP results arrive as content blocks, not plain values
5. Another one — sys.executable, never a bare "python" string
6. Takeaway — normalize the result shape once (closing question)
