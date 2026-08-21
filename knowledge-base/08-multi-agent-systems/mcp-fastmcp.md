---
stage: "08-multi-agent-systems"
tools: [fastmcp, langchain-mcp-adapters]
tags: [mcp, tools, protocol, sandboxing]
last_verified: 2026-08-20
verified_against: "fastmcp 3.4.7, langchain-mcp-adapters 0.3.x (this repo's pins)"
---

# MCP and FastMCP

The Model Context Protocol (MCP) standardizes how an agent reaches a tool or data source it didn't write — M clients times N tools stops being M×N bespoke integrations and becomes M+N, one implementation per side.

## Prerequisites
- [[tool-calling-fundamentals]]
- [[agent-topologies]]
- [[decorators-and-wrappers]]

## In plain English

Before MCP, giving an agent access to your company's internal room-booking system meant writing a custom integration for that one AI product — a different one for the next client, the next framework, the next vendor. MCP is the "USB-C for tools" analogy the course leans on repeatedly: it standardizes the plumbing (how a client discovers what a server offers, how it calls a tool, what a result looks like), not the quality of any given tool. A vague tool doesn't get rejected by the protocol — it just gets called wrongly, or never, by the model reading its schema.

MCP defines four primitives, and only one of them puts the model in the loop at all:

| Primitive | Who decides to use it | What it's for |
|---|---|---|
| Tool | The model | An action the model chooses to invoke, given a description and JSON schema |
| Resource | The application | Read-only data addressed by URI, fetched by the app — no model decision involved |
| Prompt | The user | A templated interaction the user picks, not the model |
| Sampling | The server | The server asks the *client* for a completion — inverted from the usual direction |

FastMCP is the Python framework this repo uses to build the server side: decorators turn a plain typed function into a JSON-RPC endpoint with an auto-generated JSON schema, so the docstring and type hints *are* the API contract a model reads to decide whether and how to call the tool.

## Core mechanics

| API surface | What it does |
|---|---|
| `FastMCP(name)` | Server instance; the thing you decorate functions onto |
| `@mcp.tool` | Registers a function as a model-callable tool; return type + docstring + type hints generate the JSON schema |
| `@mcp.resource("scheme://path")` | Registers an app-fetched, read-only resource addressed by URI |
| `@mcp.prompt` | Registers a user-selectable templated prompt |
| `mcp.run(transport=...)` | Starts the server — `"stdio"` (child process, JSON-RPC over stdin/stdout, local, no auth) or `"http"` (remote, multi-client, needs auth) |
| `MultiServerMCPClient({...})` (`langchain-mcp-adapters`) | Client side: spawns/connects to one or more servers by config dict, keyed by server name |
| `await client.get_tools()` | Spawns → `initialize` (version handshake) → `list_tools` (discovery) → returns LangChain `StructuredTool` objects |
| `async with client.session(name) as session:` | Holds one connection open across multiple calls — needed for stateful servers, sampling/elicitation callbacks, or when per-call session setup is expensive |

Two transports cover almost everything: **stdio** for a local server run as a subprocess of the client process (what this repo's labs use — no network, no auth needed, since the client spawned the process itself), and **streamable HTTP** for a remote server multiple clients connect to, which does need auth. Switching between them is one config key, not a rewrite.

## Sample code

Lab-sourced (Day 3 · Session 2 — `labs/Day3 Session 2 - MultiAgent Teams and Agent Protocols.ipynb`), a sandboxed FastMCP server:

```python
from pathlib import Path
from fastmcp import FastMCP

PROJECT_ROOT = Path(__file__).resolve().parent  # not os.getcwd() — the client
                                                  # launches this as a subprocess whose
                                                  # cwd isn't guaranteed to match the caller's

mcp = FastMCP("project-kb")
MAX_READ_BYTES = 20_000

def _safe_path(relative: str, root: Path) -> Path:
    candidate = (root / relative).resolve()
    if not candidate.is_relative_to(root):
        raise ValueError("path escapes project root")
    if candidate.is_symlink():
        raise ValueError("symlinks are refused, even inside the sandbox")
    return candidate

@mcp.tool
def read_project_file(relative_path: str) -> str:
    """Read a text file inside the project folder. Path is relative to project root."""
    path = _safe_path(relative_path, PROJECT_ROOT)
    return path.read_text()[:MAX_READ_BYTES]

if __name__ == "__main__":
    mcp.run(transport="stdio")  # never print() to stdout here — stdout IS the JSON-RPC channel
```

Client side (`langchain-mcp-adapters`), spawning that server and handing its tools to a LangChain agent:

```python
import sys
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({
    "project": {
        "transport": "stdio",
        "command": sys.executable,   # always sys.executable, never bare "python" —
        "args": ["server.py"],       # resolves against a different interpreter/PATH otherwise,
    }                                 # and the failure looks like a protocol error, not an import error
})
tools = await client.get_tools()
```

`_safe_path`'s three checks — `.resolve()` to collapse `..`/symlinks, `is_relative_to()` to reject traversal or absolute paths, and an explicit symlink refusal — are written before any tool that reads a file, not bolted on after. The lab notes the strongest guardrail here is a capability that was never exposed at all: no delete tool, no arbitrary-path write tool exists in this server's surface.

## Alternatives

| Approach | Where it lives | Boring/simple alternative to MCP? |
|---|---|---|
| Bare MCP Python SDK (`mcp` package, `FastMCP` class bundled in `mcp.server.fastmcp`) | Official reference SDK, `modelcontextprotocol/python-sdk` | No — same protocol, official but less actively developed high-level API; this repo pins the standalone `fastmcp` package instead |
| LangChain tool-calling without MCP (`@tool` decorator, `bind_tools`) | `langchain-core` | No — same tier of tooling for a single framework, skips the cross-framework interoperability MCP buys |
| `unstructured`-style bespoke REST/RPC integration per tool | Plain Python, no shared protocol | **Yes, closer to boring** — works fine for one client talking to one tool, doesn't compose (M×N again the moment a second client or tool shows up) |
| OpenAI function-calling directly (`tools` param in a Chat Completions/Responses call) | OpenAI API | **Yes, the boring option** — "just call your functions directly, skip the protocol": no server process, no schema-generation layer, no discovery; fine until you need the same tool reachable from more than one client/vendor |

## How this shows up in the capstone

Milestone 6 (multi-agent supervisor team + MCP-backed tool swap) — exposing Kartway's order/policy tools as a FastMCP server, swapped into the multi-agent team from [[supervisor-worker-teams]] without touching the rest of the graph, per [[capstone-milestone-map]].

## Interview fire round

- **Q: What does MCP actually buy you if it doesn't make anything faster?**
  A: Not speed — every call now crosses a process boundary plus JSON serialization, so latency goes *up*. It buys decoupling: the knowledge base or tool stops being welded to one client/notebook/framework, and any MCP-compatible client can reach it unchanged.
- **Q: Why is the docstring part of the API contract, not documentation?**
  A: FastMCP turns the function's docstring and type hints into the JSON schema the model reads to decide whether and how to call the tool — a vague docstring doesn't raise an error, it just gets the tool called wrongly or never.
- **Q: When is MCP the wrong call for a given tool?**
  A: When only one client will ever call it and cross-framework reuse is worth nothing to you — then it's "an integration decision, not an upgrade," and a plain Python function is still right.

## Production gotchas & best practices

- Lab gotcha: **sandbox first, feature second** — `_safe_path`'s traversal/symlink checks exist before any file tool is written, and destructive capabilities (delete, arbitrary-path write) are never exposed at all rather than exposed-then-restricted.
- Lab gotcha: **never `print()` to stdout in a stdio server** — stdout is the JSON-RPC channel; a stray print corrupts every message after it and the client fails with a JSON parse error that looks nothing like its actual cause. Log to stderr only.
- Lab gotcha: **`PROJECT_ROOT` must be computed from `__file__`, not `os.getcwd()`** — the client spawns the server as a subprocess, and that subprocess's working directory is not guaranteed to match the caller's.
- Lab gotcha: **hold one session open** (`async with client.session(...)`) instead of calling `get_tools()` per request whenever the server has state between calls, uses sampling/elicitation (the callback needs a live session to answer on), or connection setup is expensive — `get_tools()` per call opens and closes a session each time.
- Lab gotcha: **a server-side tool error doesn't crash the MCP client** — it comes back as a normal result flagged as an error, which the model can read and try something else with; treating it like an exception that should kill the agent loop is a misunderstanding of the protocol, not a bug.
- Production practice (2026 security landscape): the Cloud Security Alliance's MCP security research documents a systemic STDIO command-execution flaw pattern across official SDKs, and a peer-reviewed threat-modeling paper covers prompt-injection-via-tool-poisoning across all six MCP components — treat a newly-added MCP server the way you'd treat any new dependency with code-execution surface, not as "just a config entry." (Cloud Security Alliance, *MCP Security Crisis*, and MDPI, *MCP Threat Modeling*; per course material, `presentations/day3.md`.)
- Production practice: version-skew is a real trap specific to this repo — `pyproject.toml` pins the standalone `fastmcp` v3.x package (`gofastmcp.com`), not the MCP SDK's bundled v1-era `FastMCP` in `mcp.server.fastmcp`. Blog posts and tutorials referencing the bundled SDK's API predate this split and use an older decorator surface; discard those for this repo's version.

## Course vs. production

The lab runs its MCP server over **stdio** — a local child process, no network, no authentication needed because the client spawned it directly. Production MCP servers reached by more than one client typically run over **streamable HTTP**, which does need authentication and — per the identity/scoping discipline in [[auth-and-multi-tenancy]] — a way to know *which* caller is invoking a tool, not just that some caller has a valid token. The lab's `MAX_READ_BYTES` cap and hand-rolled `_safe_path` sandbox are also the kind of control a production deployment would pair with the platform's own auth/rate-limiting layer rather than relying on solely.

## Related
- **Builds on** — [[tool-calling-fundamentals]], [[decorators-and-wrappers]]
- **Contrasts with** — [[agent-protocols-a2a-ap2]] (MCP is agent→tool; A2A is agent→agent)
- **Feeds into** — [[supervisor-worker-teams]], [[auth-and-multi-tenancy]], [[fastapi-fundamentals]]

## Sources

**Lab sources**
- `lab-summaries/Day3-Session2-MultiAgentProtocols.md` (§ "Lab B — Model Context Protocol (Milestone 6)", B1–B5)
- `labs/Day3 Session 2 - MultiAgent Teams and Agent Protocols.ipynb`

**Web sources**
- [FastMCP — Welcome](https://gofastmcp.com/getting-started/welcome) — framework overview, `@mcp.tool`/`@mcp.resource`/`@mcp.prompt`, standalone project vs. SDK-bundled origin, accessed 2026-08-20
- [FastMCP (GitHub, jlowin/fastmcp)](https://github.com/jlowin/fastmcp) — standalone project remains actively maintained after FastMCP 1.0 was incorporated into the official MCP Python SDK in 2024, accessed 2026-08-20
- [fastmcp on PyPI](https://pypi.org/project/fastmcp/) — current release 3.4.7 (Aug 10, 2026), matches this repo's `pyproject.toml` pin (`fastmcp>=3.4.7`), accessed 2026-08-20
- [Model Context Protocol — Introduction](https://modelcontextprotocol.io/introduction) — protocol overview, USB-C analogy, official docs, accessed 2026-08-20
- [Model Context Protocol — Build an MCP server](https://modelcontextprotocol.io/docs/develop/build-server) — bundled Python SDK server-building tutorial, Tools/Resources/Prompts primitives, accessed 2026-08-20
- [OpenAI — Function calling](https://developers.openai.com/api/docs/guides/function-calling) — `tools` schema for calling functions directly without a protocol layer, accessed 2026-08-20
- Cloud Security Alliance, *MCP Security Crisis: Systemic Design Flaws in AI Agent Infrastructure* — cited per course material (`presentations/day3.md`), not independently re-verified this session
- MDPI, *MCP Threat Modeling and Analysis of Vulnerabilities to Prompt Injection with Tool Poisoning* (`mdpi.com/2624-800X/6/3/84`) — cited per course material (`presentations/day3.md`), not independently re-verified this session
