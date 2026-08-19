# Day 3 · Session 2 — Multi-Agent Collaboration and Agent Protocols

Source: `labs/Day3 Session 2 - MultiAgent Teams and Agent Protocols.ipynb`

Lab A (five-agent supervisor team) + Lab B (MCP server, tied to **Milestone 6**) + an appendix on A2A/AP2. Every agent (Planner, Researcher, Writer, Fact-Checker, Reviewer, Supervisor) is a real `ChatLiteLLM` call with deterministic fallbacks. Recurring principle, shown 3x: **let the model produce; let deterministic code decide** (Planner's topics filtered against a whitelist, Fact-Checker's verdict overruled by regex, Supervisor's route rejected if illegal).

Model handle: `ask(system, user)` (text→text) and `ask_structured(system, user, Schema)` (text→validated Pydantic object via `chat_model.with_structured_output(Schema)`) — both return `None` on failure so callers write `value = ask_structured(...) or <fallback>`. `LLM_CALL_PAUSE_SECONDS=3.0` after every call to avoid rate limits in a chatty 5-agent star. `_STRUCTURED_CACHE` caches one structured-output runnable per schema class.

## Lab A — Research team with a supervisor

**Team patterns**: Supervisor (one coordinator routes, traceable, but a bottleneck), Choreography (peer-to-peer handoff, emergent/hard to debug), Actor-critic (producer + independent critic). Team here = supervisor **with two embedded critics** (Fact-Checker, Reviewer) — most common in production. Trigger for splitting into 5 agents: genuine **separation of expertise** (a fact-checker sharing the writer's context would confirm its invented citation); planner/writer sharing context is a weaker trigger (could defensibly be one agent).

### A1 — Team state & permissions
Two mechanisms: **read scoping** (each agent gets only its state slice — the real reason multi-agent helps) and **write scoping** (each agent may only update its own keys, enforced by a `@scoped(role)` decorator that raises `PermissionError` on violation, handles async nodes too via `inspect.iscoroutinefunction`). State fields split control vs audit exactly as Day3-S1: `findings`/`log` use `Annotated[list, add]` (accumulate); `fact_check`/`review` deliberately have **no** reducer, because the **Writer must be able to reset them to `{}`** — any rewrite voids prior verification/approval, and a control field you can't empty is a loop you can't exit.

### A2 — Five specialists
Common node shape: `@scoped(role)` → `context_for(role, state)` (read scope) → `ask_structured(...)` → validate/filter deterministically → return partial update. Read slices are the real boundary — e.g. the **Fact-Checker sees no brief, no plan**, only `{draft, findings}`, so it can't be persuaded by the document's intent. Typed contracts (`Plan`, `NextTopic`, `FactCheck`, `Review`, `Route` — all Pydantic `BaseModel`s) drive control flow; every model output is validated/filtered before touching state (planner topics ∩ whitelist; researcher's chosen topic must be in the not-yet-retrieved list or fall back).

- **Fact-Checker is built "backwards"**: the deterministic check (`cited - supported` via regex `\[(S\d+)\]`) **is** the verdict; the model runs alongside as a logged second opinion, never routed on. Rule of thumb: model for **judgement**, code for **fact**.
- **Reviewer** is LLM-as-judge over an objective floor: `_structure_notes()` (missing sections, length) always runs first; approval requires **both** no objective defects **and** judge agreement (AND, never OR) — the standard shape for putting an LLM-judge in a control path.
- **Escalate** node: team couldn't converge within budget, hands to a human rather than burning tokens — Session 1's human-in-the-loop gate, reached automatically.

### A3 — The supervisor: model may *route*, not *authorise*
Production shape: wrap an LLM router in a pure-function policy.
1. `legal_routes(state)` computes every **structurally possible** route right now (the model's leash).
2. Ask the model to choose (`Route` schema).
3. Accept only if `out.next_agent in legal`; otherwise fall back to `supervisor_policy(state)` (pure function, no I/O).

Ordering **is** the design: plan before research (unbounded otherwise) → research before writing (writer with no findings invents them) → fact-check before review (cheap objective check before expensive subjective one) → both critics can send work back only within `MAX_REVISIONS`, then `escalate`. Two things the model is **structurally unable** to do: route to `writer` once budget is spent (not in the legal set), or route to `done` while fact-check/review are outstanding (shipping is an authorization, not a token-sampler decision). `supervisor_policy` tested via 9 hand-written cases with **no graph, model, or token** — the payoff of writing the supervisor as a pure function.

### A4 — Topology
Every specialist returns to the supervisor (star); no specialist edges to another — that constraint *is* the supervisor pattern. `tb.add_conditional_edges("supervisor", lambda s: s["next_agent"], {...})` — the **node** decided (wrote `next_agent`), the **edge** only reads it. Every unit of work costs **two supersteps** (specialist + supervisor's next decision) — a 5-agent team runs ~19 supersteps against LangGraph's default recursion limit of 25; set `recursion_limit` explicitly (used `50`).

Self-check pattern: assert **invariants**, never exact transcript text (planner stayed on-whitelist, every planned topic researched, revisions ≤ budget, converged run has passed fact-check AND approval, all cited tags resolve to retrieved records) — "if you find yourself asserting on generated prose, you've written a test that fails on Tuesdays."

### A5 — Why the critics exist, demonstrated
Swap in a `hallucinating_writer` that plants a fake `[S9]` citation on its first draft. Trace shows: fact-checker names S9 (never having seen the brief — can't be talked round), supervisor routes back to writer, `revision_count` increments, and the fabricated tag is **absent from the shipped draft**. Also demonstrates a `stubborn_writer` that never actually fixes anything — proves the loop **cannot** run forever: once `MAX_REVISIONS` is spent, `"writer"` leaves `legal_routes()` entirely, so neither the policy nor the model can pick it — `escalated_to_human` instead.

## Lab B — Model Context Protocol (Milestone 6)

**The problem**: M clients × N data sources = M×N bespoke integrations. MCP makes it M+N — wrap each source once as a server, each app's client side once, any client talks to any server. Analogy: MCP is USB-C for tools (standardizes plumbing, not tool quality).

**Four primitives**: Tool (model decides to call), Resource (application fetches, read-only, addressed by URI — no model in the loop), Prompt (user chooses a templated interaction), Sampling (server asks client for a completion). Transports: **stdio** (server = child process, JSON-RPC over stdin/stdout, local, no auth — used here) vs **streamable HTTP** (remote, multi-client, needs auth — one config key different). Libraries: `fastmcp` (server, decorators generate JSON-RPC + JSON schema from type hints) / `langchain-mcp-adapters` (`MultiServerMCPClient`, spawns+handshakes+discovers, hands back LangChain tools).

### B1 — FastMCP server (project folder exposed safely)
Server exposes the project folder: `list_project_files`, `read_project_file`, `search_kb`, `write_note`. **Sandbox is the first thing built, not a feature added later**:
- `_safe_path(relative, root)`: `.resolve()` (collapses `..`/symlinks) → `is_relative_to(root)` (rejects traversal/absolute paths) → `is_symlink()` refused outright (a symlink inside the sandbox can still point outside).
- Reads size-capped (`MAX_READ_BYTES=20_000`); writes go **only** into `mcp_workspace/`; **no delete tool, no arbitrary-path write tool exists at all** — "the strongest guardrail is a capability you never exposed."
- `PROJECT_ROOT = Path(__file__).resolve().parent`, **not** `os.getcwd()` — the client launches this as a subprocess whose cwd isn't guaranteed to match the notebook's.
- **Docstrings + type hints ARE the API contract** — FastMCP turns them into the JSON schema the model reads to decide whether/how to call a tool; a vague docstring is a broken integration that raises no error, it just gets called wrongly or never.
- **Never `print()` to stdout in a stdio server** — stdout IS the JSON-RPC channel; log to stderr only.
- One `@mcp.resource("kb://policy/citation-rules")` — app-driven, no model decision involved.

### B2 — MultiServerMCPClient
```python
client = MultiServerMCPClient({"project": {"transport": "stdio", "command": sys.executable, "args": [SERVER_PATH]}})
tools = await client.get_tools()   # spawn -> initialize -> list_tools -> LangChain StructuredTools
```
- **Always `command=sys.executable`**, never bare `"python"` — resolves against a different interpreter/PATH otherwise, failure looks like a protocol error not an import error.
- Adding a server = one dict entry — the M+N claim made concrete.
- `parse_tool_result(raw)` helper: MCP results arrive as content blocks (`[{'type':'text','text':'<json>'}]`), not plain Python values — every real MCP project ends up writing this normalizer.
- Notebook-specific plumbing: Jupyter's `sys.stderr` isn't a real file (no `fileno()`), so the stdio transport needs a patched `errlog` pointing at a real log file (`mcp_server.log`) — not needed outside notebooks.
- Sandbox self-check: 4 escape attempts (parent traversal, absolute path, `..` listing, write outside workspace) all refused; legitimate reads/writes still work. **When a tool raises server-side, MCP doesn't crash the client** — the error comes back as a normal result flagged as an error, so a model can read it and try something else (an exception would kill the agent loop).

### B3 — Agent over MCP
`create_agent(chat_model, mcp_tools)` — LangChain's prebuilt ReAct agent. Nobody told the agent `search_kb` exists; it appeared through discovery, chosen from the FastMCP-generated schema. Contrast with Lab A: there the *graph* chose what to do and the model chose *how*; here the *model* chooses what to do.

### B4 — Stateful sessions
`get_tools()` per call is convenient but opens/closes a session each time. Hold one open when the server has state between calls, uses sampling/elicitation (callbacks need a live session), pushes notifications, or connection setup is expensive:
```python
async with mcp_client.session("project") as session:
    tools = await load_mcp_tools(session)
    # session.list_tools() / session.call_tool() / session.list_resources() / session.read_resource() also usable directly
```
Raw handshake: spawn → `initialize` (version negotiation — where SDK skew fails loudly) → `list_tools` (discovery) → `call_tool` → `list_resources`/`read_resource` (app-driven).

### B5 — Bring it together (Milestone 6)
Swap the team's Researcher node for an MCP-backed version — **only that node changes**; state, scopes, supervisor policy, loop-backs, cap, both critics stay untouched (proof the layering held). Node becomes `async` (awaits the MCP call); invoke the graph with `await team.ainvoke(...)`. `scoped()` already handles async via `inspect.iscoroutinefunction`. Self-check compares MCP-backed run's retrieved record ids against the local-function run's — identical evidence, possibly different draft wording (draft text isn't asserted, since a model wrote it). **What MCP actually buys**: not speed (latency goes up, every call crosses a process boundary + JSON serialization) — it buys that the knowledge base is no longer welded to one notebook; any client (this agent, Claude Desktop, a colleague's framework) reaches it unchanged. **MCP is an integration decision, not an upgrade** — if that's worth nothing for a given tool, a plain Python function is still right.

## Appendix — A2A and AP2 (illustrative, not coursework)

Three protocols on one map: **MCP** = agent→tool/resource. **A2A** = agent→remote agent ("how does one opaque agent delegate to another?"). **AP2** = security inside a commerce/payment flow ("what evidence proves the user authorized this agent-performed purchase?"). AP2 doesn't require A2A and vice versa; this scenario composes them (A2A gets a quote from a vendor agent; AP2-style mandates decide whether it may be paid).

- **A2A** (v1.0.1): fetch `GET /.well-known/agent-card.json` → pick a `supportedInterfaces` entry → resolve auth from `securitySchemes` → `SendMessage` (response has exactly one of `result.task`/`result.message`) → poll/stream a `Task` if returned. `contextId` groups a conversation; `taskId` identifies one stateful unit — same `taskId`+`contextId` continues a Task, same `contextId` with no `taskId` starts a new Task in the same conversation. Roles/states are enums (`ROLE_USER`, `TASK_STATE_COMPLETED`); a `Part` is flattened (`{"text":...}` or `{"data":...}`). Agent Card skills are descriptive, not RPC method names — the client sends a Message, not a skill-ID call.
- **AP2** (v0.2): secures agent-performed payments only (catalog/checkout/transport are out of scope). Five roles: Shopping Agent, Trusted Surface (must be **non-agentic** — shows authority to user, gets consent), Merchant, Credential Provider, Merchant Payment Processor. Two mandate types (Checkout, Payment), each **open** (constrains allowed merchants/amount/payee/instrument, before the exact purchase exists, user-signed, includes agent's public key in `cnf`) or **closed** (one exact purchase, agent-signed, references the open mandate). Autonomous flow: user signs open mandates once (e.g. a 30-min authority window); later the agent signs closed mandates for a purchase, and a **deterministic verifier** (no model involved) checks: signatures valid, `vct` types correct, not expired, `cnf` key matches across mandates, closed checkout's hash matches the merchant-signed checkout JWT, checkout total = sum of line items, merchant is in the allow-list, line items match what was authorized, payment amount within `payment.amount_range`, payee/instrument match, open Payment Mandate references the right open Checkout Mandate, and the open mandate pair hasn't already been consumed (replay protection). Negative tests proved: tampered checkout totals, unapproved merchants, expired authority, mismatched checkout/payment binding, over-cap amounts, and replay are all rejected — **the model may find a report or explain a choice; it may never raise the cap, alter a signed checkout, or wave through a replay.**
- **What's simplified here** (explicitly flagged): no real network calls, no trust registries, no payment rails, no full SD-JWT/KB-SD-JWT — a local ECDSA P-256 JWS wrapper stands in. Production checklist covers replacing every fixture (real Agent Card fetch+cache, real transport/TLS/auth, real user/agent/merchant key enrollment, real Credential Provider, durable audit/replay state).

## Pitfall table highlights (Session 2 specific, beyond Session 1's)
| Symptom | Cause | Fix |
|---|---|---|
| `GraphRecursionError` in a supervisor graph | star topology = 2 supersteps/unit of work, default limit 25 | set `recursion_limit` deliberately |
| LLM router picks a step with nothing to do | asked an open question | offer `legal_routes(state)`, discard anything outside it |
| Critic "approves" a fabricated citation | critic shares producer's context | scope the critic's read slice, deny it the brief |
| Approved doc ships with unverified edits | rewrite didn't void prior approvals | let the writer reset `fact_check`/`review` |
| `io.UnsupportedOperation: fileno` spawning stdio server | Jupyter's `sys.stderr` isn't a real file | pass a real file as `errlog` |
| MCP client fails with JSON parse error | a stray `print()` to stdout in the server | log to stderr only |
| Tool discovered but model never calls it | vague docstring/untyped params | docstring IS the contract, write for a stranger |
| Server state resets between calls | each `get_tools()` opened its own session | hold one open with `async with client.session(...)` |
| Agent purchase settles above user's cap | cap was prompt text, not verified in code | compare integer minor-unit amount against `payment.amount_range` deterministically |

**Capstone tie-in:** Milestone 6 — the MCP-backed researcher swap is the deliverable; the supervisor team + enforced scopes + revision cap + dual critics is a direct template for the capstone's multi-agent orchestration.
