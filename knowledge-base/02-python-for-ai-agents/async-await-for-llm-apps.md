---
stage: "02-python-for-ai-agents"
tools: [asyncio]
tags: [primer, async, concurrency, mcp, supermemory]
last_verified: 2026-08-20
verified_against: "Python 3.13 (this repo's pin: requires-python >=3.13); asyncio (fastmcp>=3.4.7, langgraph>=1.2.11 both async-native)"
---

# Async/await for LLM apps

`async`/`await` let one program juggle multiple slow, I/O-bound operations — like waiting on an LLM API or an MCP subprocess — without blocking on any single one, which matters because almost every operation this stack performs is exactly that kind of wait.

## Prerequisites
- [[functions-args-kwargs]]
- [[decorators-and-wrappers]]

## In plain English

A normal ("synchronous") Python function runs top to bottom, and if it calls something slow — a network request, a subprocess — the entire program sits idle waiting for that one thing to finish. For CPU-bound work that's unavoidable; for I/O-bound work (waiting on a network response, a disk write, another process) it's wasted time, because the CPU has nothing to do but wait.

`async`/`await` is Python's way of writing code that can pause at a slow I/O point and hand control back to an **event loop**, which can go run something else useful in the meantime, then resume the paused code once its result is ready. A function defined with `async def` is a *coroutine* — calling it doesn't run it immediately, it creates a coroutine object that has to be `await`ed (or scheduled onto the event loop some other way) to actually execute. `await` marks the point where a coroutine yields control back to the loop while it waits on something.

This matters specifically for LLM apps because nearly every real operation — an LLM completion call, an MCP tool call over a subprocess, a Supermemory write — is I/O-bound: the program spends most of its time waiting on a response, not computing. Async lets a single process handle many such waits concurrently (e.g. fan out several tool calls at once) instead of serializing them one at a time.

## Core mechanics

| Concept | What it means |
|---|---|
| `async def f(): ...` | defines a coroutine function; calling `f()` returns a coroutine object, doesn't run the body yet |
| `await expr` | pauses the current coroutine until `expr` (another coroutine/awaitable) completes, yielding control to the event loop meanwhile |
| Event loop | the scheduler that runs coroutines, switching between them at their `await` points |
| `asyncio.run(coro())` | creates an event loop, runs one top-level coroutine to completion, closes the loop — the standard entry point |
| `async with` | an async context manager — used for resources whose setup/teardown themselves need to await something (e.g. opening an MCP session) |
| `asyncio.TaskGroup` (via `anyio`/`asyncio`) | runs multiple coroutines concurrently as a structured group, waits for all to finish, propagates exceptions from any of them |

A synchronous function calling an `async def` function directly is a common mistake — it just gets back an un-awaited coroutine object, not a result. Async and sync call chains don't mix silently; a sync function needs `asyncio.run(...)` (only at the true top level) or the whole call chain needs to be async.

## Sample code

Lab-sourced MCP client usage (`lab-summaries/Day3-Session2-MultiAgentProtocols.md`, § B2/B4) — spawning a server subprocess and discovering its tools is I/O-bound (waiting on a subprocess handshake), so the whole call chain is async:

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

client = MultiServerMCPClient({
    "project": {"transport": "stdio", "command": sys.executable, "args": [SERVER_PATH]}
})
tools = await client.get_tools()   # spawn -> initialize -> list_tools, all awaited

# holding a session open across multiple calls (state between calls, sampling/elicitation):
async with mcp_client.session("project") as session:
    tools = await load_mcp_tools(session)
    result = await session.call_tool("search_kb", {"query": "refund policy"})
```

`await client.get_tools()` internally spawns a subprocess, performs a JSON-RPC handshake, and lists available tools — every one of those steps is a wait the event loop can use productively elsewhere while it's pending.

## How this shows up in the capstone

MCP tool calls (M6) and Supermemory writes (M3) are both I/O-bound operations this stack awaits rather than blocks on; a graph node that calls an MCP tool becomes `async def` and the whole graph invocation switches to `await team.ainvoke(...)` (`lab-summaries/Day3-Session2-MultiAgentProtocols.md`, § B5).

## Interview fire round

- **Q: What actually happens when you call an `async def` function without `await`ing it?**
  A: You get back a coroutine object, not a result — the function body hasn't run yet. Python usually warns about this ("coroutine was never awaited") but it doesn't raise an error, so the bug can go unnoticed until the missing result causes a failure somewhere downstream.
- **Q: Why does async help with LLM/MCP calls specifically, but not with a CPU-heavy loop?**
  A: Async concurrency works by yielding control at `await` points while waiting on I/O — an LLM API call or MCP subprocess call spends nearly all its time waiting on a response, so the event loop can usefully run other coroutines during that wait. A CPU-bound loop never hits an `await` point to yield at, so async buys it nothing; that needs real parallelism (multiprocessing), not concurrency.
- **Q: Why must an MCP client session stay within one asyncio Task rather than being cached and reused across calls from different Tasks?**
  A: `anyio`'s structured-concurrency `TaskGroup`s (which MCP's stdio transport is built on) are scoped to the Task they were created in — LangGraph runs each node in its own Task, so a session opened in one node's Task and reused in another breaks the TaskGroup's structured-concurrency guarantees (`labs/production-notes.md`, § "Concurrency / Idempotency").

## Production gotchas & best practices

- Supermemory writes are async on the *server* side even when the client call itself returns quickly — the write isn't immediately searchable, so code must poll for searchability rather than assume `add()` means "indexed" (`lab-summaries/Day2-Session1-MemoryEngineering.md`, § "Gotchas": "Supermemory writes are async — always poll for searchability, don't assume `add()` is immediately queryable").
- Async resources backed by structured concurrency (anyio `TaskGroup`s, which MCP's stdio transport uses) must stay within one asyncio Task — caching an MCP session across multiple `tools()` calls broke exactly this way, because LangGraph runs each node in its own Task (`labs/production-notes.md`, § "Concurrency / Idempotency").
- `BaseExceptionGroup` (PEP 654) wraps even single exceptions raised inside a `TaskGroup` — unwrap it (`exc.exceptions[0]`, recursively if nested) at every catch site near a TaskGroup boundary to get the actual underlying error, or error messages become uninformative ("`_unwrap_exception_group`", `lab-summaries/Day1-Session2-ToolCalling.md`, § "Setup"; also `labs/production-notes.md`).
- Current production guidance: trigger a slow library's first-import/first-connection cost eagerly at application startup (e.g. inside a FastAPI `lifespan` handler) rather than lazily on the first real request — a cold first-call cost otherwise shows up as unattributed latency on whichever user request happens to trigger it (`labs/production-notes.md`, § tracing/startup notes).

## Course vs. production

The labs mostly wrap async MCP calls behind a single sync helper function (`call_mcp_tool`, `lab-summaries/Day1-Session2-ToolCalling.md`, § "Setup") so the rest of the notebook doesn't need to go async — a reasonable simplification for a teaching notebook. Production agent code (this stack's LangGraph nodes, FastAPI endpoints) is async natively end-to-end, since the framework itself is built async-first (`fastmcp>=3.4.7`, `langgraph>=1.2.11` — both pinned in `pyproject.toml`) and wrapping every await point behind a sync shim adds overhead and loses the concurrency benefit async exists for.

## Related

- **Builds on** — [[decorators-and-wrappers]]
- **Used by** — [[supermemory]], [[mcp-fastmcp]]

## Sources

**Lab sources**
- `lab-summaries/Day2-Session1-MemoryEngineering.md` (§ "Gotchas" — Supermemory async writes)
- `lab-summaries/Day3-Session2-MultiAgentProtocols.md` (§ B2-B5 — `async with mcp_client.session(...)`, `await client.get_tools()`, `await load_mcp_tools(session)`)
- `lab-summaries/Day1-Session2-ToolCalling.md` (§ "Setup" — sync wrapper around async MCP calls, `_unwrap_exception_group`)
- `labs/production-notes.md` (§ "Concurrency / Idempotency")
- `labs/Day3 Session 2 - MultiAgent Teams and Agent Protocols.ipynb`

**Web sources**
- [Python 3 asyncio docs](https://docs.python.org/3/library/asyncio.html) — coroutines, event loop, `asyncio.run`, accessed 2026-08-20
- [Python 3 — A Conceptual Overview of asyncio](https://docs.python.org/3/howto/a-conceptual-overview-of-asyncio.html) — event loop mental model, accessed 2026-08-20
- [Python 3 — asyncio Task Groups (PEP 654 / structured concurrency)](https://docs.python.org/3/library/asyncio-task.html#task-groups) — `TaskGroup` scoping and `ExceptionGroup` behavior, accessed 2026-08-20
