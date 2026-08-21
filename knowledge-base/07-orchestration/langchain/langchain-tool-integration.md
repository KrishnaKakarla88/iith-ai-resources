---
stage: "07-orchestration"
tools: [langchain, langchain-mcp-adapters, fastmcp]
tags: [orchestration, langchain, tools, mcp]
last_verified: 2026-08-20
verified_against: "langchain-mcp-adapters 0.3.x, fastmcp 3.4.x (this repo's pins)"
---

# LangChain tool integration

LangChain gives a tool two things a model needs to call it correctly: a JSON schema (generated from your function's type hints) and a description (generated from your docstring) — and the same `@tool`-decorated function works whether it's called directly or discovered remotely over MCP.

## Prerequisites
- [[tool-calling-fundamentals]]
- [[langchain-chains-vs-agents]]

## In plain English

A model doesn't call a Python function — it emits structured text (a tool name plus JSON arguments) that your code then dispatches to the real function. LangChain's `@tool` decorator automates the boring, error-prone part of that bridge: it reads your function's type hints to build the JSON schema the model is shown, and your docstring becomes the natural-language description the model uses to decide *whether* to call this tool at all. Get the docstring vague and the tool becomes what the labs call a broken integration that raises no error — the model just calls it wrongly, or never calls it, and nothing in your logs points at the docstring as the cause.

Once tools are defined this way, they're not stuck as local functions. `langchain-mcp-adapters` bridges the other direction: given a running MCP server (see [[mcp-fastmcp]]), `MultiServerMCPClient.get_tools()` performs the whole MCP handshake (spawn → initialize → discover) and hands back a list of ordinary LangChain `StructuredTool` objects — indistinguishable, from the model's point of view, from a tool defined locally with `@tool`. This is the concrete mechanism behind the M+N claim in [[mcp-fastmcp]]: any LangChain agent can consume any MCP server's tools without writing a custom adapter per server.

## Core mechanics

| Piece | What it does |
|---|---|
| `@tool` decorator | Wraps a plain function as a LangChain `Tool`; docstring → description, type hints → input schema |
| `args_schema` (Pydantic model, optional) | Overrides the auto-generated schema for tools with complex/validated inputs |
| `.bind_tools([...])` | Attaches a set of tools to a chat model so its output can include tool calls |
| `MultiServerMCPClient({name: {transport, command, args}})` | Configures one or more MCP servers to connect to |
| `await client.get_tools()` | Spawns/connects to configured servers, discovers their tools, returns them as LangChain `StructuredTool`s |
| `async with client.session(name) as session:` | Holds one MCP session open across multiple calls, instead of opening/closing per `get_tools()` call |

Two contract-level details that matter more than they look:

- **The docstring + type hints ARE the API contract**, not documentation of one — this is true for a local `@tool` function and doubles down when the same function is served over [[mcp-fastmcp]] (FastMCP generates the JSON-RPC schema straight from them). Writing for "a stranger who's never seen this code" isn't a style preference, it's the actual integration surface.
- **MCP results arrive as content blocks, not plain Python values** — a tool call over MCP returns something like `[{"type": "text", "text": "<json>"}]`, not the bare dict/string a locally-defined `@tool` would return directly. Code written against one shape silently misbehaves against the other; normalize once at the call boundary (see Production gotchas).

## Sample code

Lab-sourced (`labs/Day3 Session 2 - MultiAgent Teams and Agent Protocols.ipynb`, §B1-B2), a local tool and its MCP-served equivalent side by side:

```python
from langchain_core.tools import tool

@tool
def search_kb(query: str, limit: int = 5) -> list[dict]:
    """Search the internal knowledge base for policy documents matching query."""
    return kb_index.search(query, limit=limit)
```

```python
# MCP side: the *same* function, defined once on a FastMCP server, discovered
# remotely instead of imported — sys.executable, never bare "python", or
# resolution falls back to a different interpreter and fails looking like a
# protocol error, not an import error
import sys
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({
    "project": {"transport": "stdio", "command": sys.executable, "args": [SERVER_PATH]},
})
tools = await client.get_tools()   # spawn -> initialize -> list_tools -> StructuredTools
agent = create_agent(model=chat_model, tools=tools)  # search_kb usable here, never imported
```

`MultiServerMCPClient`/`get_tools()` verified against current `langchain-mcp-adapters` reference docs¹ (v0.3.x, matching this repo's `pyproject.toml` pin `langchain-mcp-adapters>=0.3.2`).

## Alternatives

| Approach | Where it lives | Boring/simple alternative to LangChain's `@tool` + MCP adapters? |
|---|---|---|
| `@tool` + `langchain-mcp-adapters` | LangChain ecosystem | — |
| Raw OpenAI/Anthropic function-calling schemas (hand-written JSON schema per tool) | Provider SDKs directly, no framework | No — same tier of manual work LangChain's `@tool` is automating away, but framework-free |
| LlamaIndex `FunctionTool` | LlamaIndex framework | No — same tier of tooling, different framework |
| A plain `dict[str, Callable]` dispatch table + manual JSON schema written by hand | No dependency | **Yes** — the boring option; works for a small, stable tool set, loses auto-schema-from-type-hints and any MCP interoperability |

## How this shows up in the capstone

Milestone 6 (multi-agent supervisor team + MCP-backed tool swap) is where this page's second half becomes real for ShopSense: an existing LangChain-tool-based agent node gets its tools swapped for MCP-discovered ones without changing anything else about the graph — state, routing, and caps stay untouched, which is the actual proof that the tool-integration layer is doing its job; see [[mcp-fastmcp]] and [[capstone-milestone-map]].

## Interview fire round

- **Q: Why does a vague tool docstring fail silently instead of raising an error?**
  A: The docstring only shapes what the model is shown to decide whether/how to call the tool — there's no validation step checking "is this description good enough," so a bad one just produces wrong or missing tool calls with nothing in the stack trace pointing back at the docstring.
- **Q: What's the concrete difference in what a `@tool` function returns locally vs. over MCP?**
  A: Locally it returns whatever Python value the function returns; over MCP it arrives wrapped as a list of content blocks (e.g. `[{"type": "text", "text": "<json>"}]`) that has to be unwrapped/parsed before use — code that assumes the local shape breaks silently against the MCP shape.

## Production gotchas & best practices

- Lab gotcha (`labs/production-notes.md`, "Tool Calling"): a tool-execution library's return shape can change across SDK versions with no error raised — a real incident cited: a successful `process_refund` call got reported to the customer as *failed* because the MCP adapter returned the newer content-block-list shape instead of the bare dict an `isinstance(result, dict)` check was written against. Fix: normalize the result shape once at the MCP-call boundary, not per consumer — an `isinstance` check against one SDK's shape is a version pin in disguise.
- Lab gotcha (`lab-summaries/Day3-Session2-MultiAgentProtocols.md`, B2): always pass `command=sys.executable`, never a bare `"python"` string, when spawning an MCP server as a subprocess — a bare string resolves against whatever interpreter is first on `PATH`, and the resulting failure looks like a protocol error, not the interpreter-mismatch it actually is.
- Lab gotcha (`lab-summaries/Day3-Session2-MultiAgentProtocols.md`, B2): match provider tool-call errors by message text, not exception class — exception classes for malformed tool calls aren't standardized across providers routed through LiteLLM (see [[litellm-basics]]).
- Lab gotcha (`labs/production-notes.md`, "Tool Calling"): regex/keyword extraction from model output is a fallback, never the source of truth — structured tool-call extraction plus schema validation is primary; a keyword-based fallback exists for when structured extraction fails, not as a first-choice parsing strategy.
- Production practice: per FastMCP/MCP behavior confirmed in the lab, when a tool raises server-side over MCP, the protocol returns the error as a normal (flagged) result rather than crashing the client connection — an agent loop can read the error and try something else, so tool implementations should raise real exceptions server-side rather than swallowing them into an ambiguous success value.

## Course vs. production

The lab (`labs/Day3 Session 2 - MultiAgent Teams and Agent Protocols.ipynb`, §B4) opens and closes an MCP session per `get_tools()` call by default, which is fine for a stateless demo but loses any server-side state between calls. Production usage holding a session open (`async with client.session(name) as session:`) is needed whenever the server has state between calls, uses sampling/elicitation callbacks, or connection setup is expensive — the lab flags this explicitly rather than treating the stateless default as always sufficient.

## Related
- **Builds on** — [[tool-calling-fundamentals]], [[langchain-chains-vs-agents]]
- **Feeds into** — [[mcp-fastmcp]]
- **Related tool** — [[litellm-basics]]

## Sources

**Lab sources**
- `lab-summaries/Day3-Session2-MultiAgentProtocols.md` (§ "Lab B — Model Context Protocol", B1-B4)
- `labs/production-notes.md` (§ "Tool Calling")
- `pyproject.toml` (`langchain-mcp-adapters>=0.3.2`, `fastmcp>=3.4.7`)

**Web sources**
- ¹[langchain_mcp_adapters — MultiServerMCPClient reference (reference.langchain.com)](https://reference.langchain.com/python/langchain-mcp-adapters/client/MultiServerMCPClient) — `get_tools()` behavior, current v0.3.x, accessed 2026-08-20
- [LangChain — Tools (docs.langchain.com/oss/python/langchain/tools)](https://docs.langchain.com/oss/python/langchain/tools) — `@tool` decorator, docstring-as-description, `args_schema`, accessed 2026-08-20
