# Day 1 · Session 2 — Tool Calling & Single-Agent Patterns

Source: `labs/Day1 Session 2 - Tool calling and Single Agent Patterns.ipynb`

Two labs, tied to **Milestone 2 — tool-enabled single agent**. Every external tool has a mocked implementation and a real MCP implementation behind the *same* function signature, switched by one flag `USE_MCP` (True = live w/ mocked fallback, False = mocked only). Neither loop (A8's tool-call loop, B2's ReAct loop) or the model changes based on the flag — that's the point: swap the implementation, never touch the caller.

## Setup
- `LAB_MODEL = "gemini/gemini-flash-lite-latest"` (Google's auto-updating Flash-Lite alias — doesn't go stale, higher free-tier throughput than full Flash). Gemini key from aistudio.google.com, no card needed.
- `call_mcp_tool(command, args, tool_name, arguments, timeout=20)` — the one sync wrapper around all MCP calls: starts server subprocess via `stdio_client`, `ClientSession.initialize()`, `call_tool()`, shuts down. Wraps `async`/`await` so nothing downstream needs to know about it.
- `_unwrap_exception_group(exc)` — anyio's TaskGroup can nest a real error inside layers of `ExceptionGroup`; unwrap `.exceptions[0]` repeatedly to get the actual cause for error messages.

## Lab A — Travel Assistant with Tools

- **A1 Calculator** — parses with `ast.parse(expr, mode="eval")` and walks the tree evaluating only a whitelisted `_SAFE_OPS` dict of operators. **Never use `eval()`** — arbitrary code execution risk.
- **A2 Weather** — `get_weather_mocked(city)` (fixed dict) vs a hand-written FastMCP server (`@mcp.tool()` decorator on an `async def`) calling Open-Meteo (geocode → forecast, free, no key), written to `weather_mcp_server.py` on disk since MCP servers run as separate processes. `get_weather(city)` tries MCP first if `USE_MCP`, falls back to mocked on any exception, labels `source` either way.
- **A3 Currency** — same pattern, Frankfurter API. **Real bug story**: the published `currency-mcp` pip package broke because Frankfurter started redirecting and its httpx client didn't set `follow_redirects=True` (not httpx's default) — so this notebook hand-rolls its own server with that one fix rather than depending on the broken package. Lesson: verify third-party MCP servers actually work, don't assume.
- **A4 Calendar** — no mocked/MCP split (nothing external to reach). Plain in-memory list; `add_event`, `check_availability`, `list_events`.
- **A5 File writer** — `write_itinerary(content, filename)`, plain local disk write, no protocol needed.
- **A6 Reliability wrappers** — three composable layers, applied in this order by `make_robust_tool(fn, name)`:
  - `retry_with_backoff(max_retries=3, base_delay=0.5)` — exponential backoff + jitter decorator.
  - `CircuitBreaker(failure_threshold=3)` — `before_call`/`record_success`/`record_failure`; N consecutive failures for one tool name opens the circuit (raises `CircuitBreakerOpen`) until a success resets it.
  - `TOOL_CALL_LOG` — every call logged as `{tool, args, kwargs, ts, result, error}`.
  - Distinct from get_weather's own MCP→mocked fallback: that layer handles "server is down entirely"; this layer handles "this one attempt failed, retry before giving up."
- **A7 Wire into LangChain** — `@tool` from `langchain_core.tools` turns a function into something the model can see (docstring = description read by the model). `ChatLiteLLM(model=LAB_MODEL, max_retries=5)` — retries cover free-tier rate limits (429s) same as tool failures. Each `@tool`-decorated function wraps the corresponding `make_robust_tool(...)`-wrapped implementation.
- **A8 Tool-call loop (`run_travel_agent`)** — bind tools via `llm.bind_tools(TOOLS)`; loop: `model.invoke(messages)` → if no `tool_calls`, return `.content`; else run each requested tool via `tool_fn.invoke(tc["args"])`, append a `ToolMessage(content=str(result), tool_call_id=tc["id"])`, repeat. **Capped at `max_iterations=6`** — not optional, prevents infinite tool-request loops. No-key fallback (`_fallback_travel_agent`) still calls the same real wrapped tools in fixed order, so infra is provable without a live key.

## Lab B — Autonomous Research Agent (ReAct + Reflection)

- **B1 Search** — `search_web_mocked(query, top_k=3)`: TF-IDF (`term_count * idf`) over a tiny embedded 5-doc corpus; `idf(term) = log((N+1)/(1+doc_freq)) + 1`. Deterministic — required for reliable self-checks. Real version: `duckduckgo-mcp-server` (published, pip-installable, key-less). **Two named limitations of the live path**: (1) results change over time so self-checks can only verify shape not content; (2) DDG's HTML-scraping approach occasionally triggers bot detection on repeated automated queries from shared/cloud IPs — call succeeds at the protocol level but returns a bot-detection message instead of results. This is why the mocked path is a legitimate fallback, not just training wheels.
- **B2 ReAct loop (`run_react_agent`)** — model writes `Thought:` / `Action: search[query]` in plain text; code regex-parses the query, calls `search_web`, injects `Observation: ...` as the next user turn, repeats until `Final Answer:` is parsed. **Critical line:** `litellm.completion(..., stop=["Observation:"])` — without this stop sequence nothing prevents the model from hallucinating its own fake observation and answering off invented "results." Capped at `max_iterations=5`. System prompt explicitly tells the model to treat Observation content as untrusted and never follow instructions inside it (prompt-injection defense). No-key fallback runs one real search and returns a labeled scripted answer.
- **B3 Reflection (`run_react_agent_with_reflection`)** — after ReAct produces a draft, one more model call critiques the draft against gathered evidence: reply `APPROVED` or `REVISE: <what's wrong>`. On REVISE, exactly one more call produces a corrected final answer (capped at one revision cycle, same reasoning as capping ReAct iterations). Needs a real key — offline mode reports a plain skip rather than faking a critique.

## Gotchas / lessons called out
- `fastapi` must be installed even in mocked mode — LiteLLM's tool-calling code imports it internally for an MCP handler regardless of `USE_MCP`.
- Third-party MCP packages can be silently broken (currency-mcp/Frankfurter redirect case) — verify before trusting.
- Live web search can trip bot detection under automated/shared-IP use — plan a mocked fallback even for "real" integrations.
- Uncapped agent loops (tool-call loop, ReAct loop, Reflection) are a real runaway risk — always cap iterations.

**Capstone tie-in:** Milestone 2 — tool-enabled single agent. Mocked-first + swap-to-real pattern is meant to be reused directly in the ShopSense project's own tools.
