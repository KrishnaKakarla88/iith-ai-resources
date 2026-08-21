---
stage: "00-ai-and-llm-basics"
tags: [primer, architecture, agents, capstone]
last_verified: 2026-08-21
---

# Architecture of an agentic system

This is the map: one labeled walkthrough of every layer a real agentic system is built from — intake, agent loop, tools/RAG/memory, orchestration across multiple agents, tracing, and the API boundary around it — so every later stage in this knowledge base has somewhere to slot in.

## Prerequisites
- [[what-is-an-llm]]
- [[tokens-and-tokenization]]

## In plain English

Every stage after this one zooms into a single piece of a bigger system — how a chunk gets embedded, how a graph checkpoints its state, how a trace gets logged. Before any of that, it helps to see the whole shape once, at a level a newcomer can hold in their head: a request comes in, something decides what to do about it, that something can call tools and look things up, multiple such somethings can be coordinated together, and the whole thing is wrapped in observability and an API so it's usable and debuggable in production.

Two ideas do most of the work here. First, **a model is not an agent**: an agent is the model *plus a harness* around it — the loop that decides when to call the model again, the tools it's allowed to reach for, the retries and permissions and logging wrapped around every call. Swap the harness and the same model can feel completely different; swap the model inside a fixed harness and the shape of the system barely changes. Second, **most systems aren't one agent** — they're several narrowly-scoped agents, each responsible for one kind of decision, coordinated by something that routes work between them.

## Core mechanics

The assembled stack, one layer at a time — read top to bottom as a request's path through the system:

| Layer | What it does | Covered in |
|---|---|---|
| **Intake** | A request arrives at a defined boundary (an API endpoint), validated against a schema before any agent logic runs — not trusted as free text | [[fastapi-fundamentals]], [[structured-output-repair-loops]] |
| **The agent loop** | The core cycle underneath every agent: perceive the current state → decide what to do next → act (often by calling a tool) → observe the result → repeat, capped at a maximum number of iterations so it can't run forever | [[agentic-loop-fundamentals]], [[react-pattern]] |
| **Tool calling** | The model requests a named, schema-defined function be run; it never executes anything itself — your code decides whether to comply, executes the call, and returns the result as new context | [[tool-calling-fundamentals]] |
| **RAG (retrieval)** | When the agent needs facts it wasn't trained on or that change over time, a retrieval pipeline (chunk → embed → search → rerank) supplies relevant context instead of the model guessing | [[hybrid-retrieval-rrf]], [[qdrant]], [[reranking]] |
| **Memory** | What persists about a user or session beyond one conversation — and what gets compressed or summarized so a long conversation doesn't blow the context window | [[memory-types]], [[supermemory]], [[context-compression]] |
| **Orchestration** | When one agent's job needs another agent's specialty, a graph or supervisor coordinates state, routing, and hand-offs between multiple bounded agents rather than one agent trying to do everything | [[agent-topologies]], [[graph-engineering-mindset]], [[langgraph-agentic-patterns]], [[supervisor-worker-teams]] |
| **Tracing/observability** | Every hop above — planning calls, tool calls, retrieval calls — is logged as a span under one trace, so "why did this answer take 14 seconds" or "which step went wrong" is a lookup, not a guess | [[langfuse-tracing]] |
| **Guardrails & eval** | The final answer is checked independent of whether it's *good* (schema-valid, no injected instructions followed) and separately scored against a golden set to catch regressions before they reach users | [[guardrails-injection-detection]], [[eval-driven-development-mindset]], [[deterministic-scorers]], [[llm-judges-eval]] |
| **Reliability** | Every dependency call (LLM provider, vector DB, external API) sits behind retry-with-backoff and a circuit breaker, so one flaky dependency degrades a request gracefully instead of failing it outright | [[retry-fallback-patterns]], [[circuit-breaker-pattern]] |
| **API boundary** | The system is exposed through a defined interface (a FastAPI endpoint, an MCP server) — never as raw model access, so the outside world talks to a contract, not to internal reasoning | [[fastapi-fundamentals]], [[mcp-fastmcp]] |

Every one of these is optional in isolation — a single tool-calling agent with no retrieval, memory, or orchestration is still a complete, valid system for a narrow task (see [[workflow-vs-agent-autonomy-spectrum]] for when that's the *right* call rather than an unfinished one). The point of this page is that they compose in this order when a system needs more than one of them.

## Sample code

There's no single lab notebook that builds every layer at once — each is demonstrated in its own dedicated notebook across the course. The one piece of code worth seeing here is the shape of the agent loop itself, the primitive every layer above ultimately sits around (lab-sourced, `labs/Day1 Session 2 - Tool calling and Single Agent Patterns.ipynb`):

```python
def run_agent(messages, tools, max_iterations=6):
    for _ in range(max_iterations):           # uncapped loops are a real runaway risk
        response = model.invoke(messages, tools=tools)
        if not response.tool_calls:
            return response.content            # model decided it's done
        for call in response.tool_calls:        # model requests; code executes
            result = run_tool(call)
            messages.append(tool_result_message(call, result))
    raise MaxIterationsExceeded()
```

Everything else in the table above — retrieval, memory, orchestration, tracing — either feeds new context into this same loop (as a tool result, a retrieved chunk, a memory lookup) or wraps around it (a trace span, a retry, a supervisor coordinating several of these loops at once). Nothing in the rest of this knowledge base replaces this shape; it all attaches to it.

## How this shows up in the capstone

This is the shape ShopSense is built to, one agent at a time, per the repo's own build order: a single tool-calling agent first (Triage), wrapped with retry/circuit-breaker resilience and Langfuse tracing baked in from that first agent onward — then the same pattern repeated for Policy RAG, Order-Actions, and Escalation Reviewer, each a bounded agent with its own tools/retrieval/memory as needed. Once all four exist, a LangGraph orchestration layer coordinates them as a supervisor-worker topology, the whole thing gets exposed via an MCP server and a FastAPI endpoint, and guardrails/eval wrap the final system. See [[capstone-milestone-map]] for the concept-to-milestone breakdown, and [[putting-it-all-together]] (stage 09) for one concrete request walked through every layer of this same shape end to end.

## Interview fire round

- **Q: What's the difference between a model and an agent?**
  A: A model is one replaceable component. An agent is the model plus a harness around it — the loop, the tool executor, retries, permissions, context management — and it's the harness, not the model alone, that determines whether the system feels reliable.
- **Q: Why do most real systems use several narrow agents instead of one agent with every tool?**
  A: Coordination and reliability — a single agent with dozens of tools and unbounded scope is harder to reason about, harder to bound, and harder to recover from a bad decision in. Several bounded agents, each owning a narrow decision, coordinated by an orchestration layer, keeps each piece testable and each failure contained.
- **Q: Where do guardrails and tracing fit relative to the agent loop itself?**
  A: Around it, not inside it — tracing wraps every hop as an observable span, guardrails check the final output independent of the reasoning that produced it, and retries/circuit-breakers wrap every dependency call the loop makes. None of them change what the loop itself does.

## Production gotchas & best practices

- Per course material (`presentations/day1.md`, Act 2): "Agent = Model + Harness" is worth taking literally — the same model dropped into two different harnesses (different loop, different tool permissions, different context management) can feel like a completely different product, which is why harness design gets as much attention as model choice.
- Production practice: build tracing and reliability wrappers in from the first agent, not as a retrofit once multiple agents exist — a build order that bakes tracing in from Agent 1 avoids the common failure of treating observability as something added right before shipping.
- Gotcha: it's tempting to reach for multi-agent orchestration by default because it's the more sophisticated-looking part of the stack — [[workflow-vs-agent-autonomy-spectrum]] and [[agent-topologies]] both warn against this: add a layer (tools, retrieval, memory, orchestration) only once a single simpler layer has been shown, by evaluation, to fall short.

## Course vs. production

The labs build and prove each layer above in its own isolated notebook. A real deployed system runs all of them concurrently, inside one continuously-running service, where a failure in any one layer (a slow vector DB, a rate-limited provider, a guardrail false-rejection) has to degrade gracefully rather than take down the whole request — which is exactly why reliability, tracing, and guardrails are treated as part of the architecture from the start in this page's table, not bolted onto a finished agent afterward. [[putting-it-all-together]] in stage 09 walks this exact contrast through one concrete request.

## Related
- **Feeds into** — [[agentic-loop-fundamentals]], [[tool-calling-fundamentals]] (the agent-loop layer); [[memory-types]], [[supermemory]] (the memory layer); [[hybrid-retrieval-rrf]], [[qdrant]] (the RAG layer); [[agent-topologies]], [[supervisor-worker-teams]] (orchestration); [[langfuse-tracing]], [[guardrails-injection-detection]] (tracing/guardrails)
- **Builds on** — [[what-is-an-llm]], [[tokens-and-tokenization]]
- **Closed by** — [[putting-it-all-together]] (the same shape, walked through one real request end to end)

## Sources

**Lab sources**
- `lab-summaries/Day1-Session2-ToolCalling.md` (harness/tool-call loop, ReAct loop, reliability wrappers)
- `labs/Day1 Session 2 - Tool calling and Single Agent Patterns.ipynb`
- [[capstone-milestone-map]] (concept-to-milestone table this page's capstone section draws from, including the repeatable single-agent → resilience → tracing build pattern each capstone agent follows)

**Course material**
- `presentations/day1.md` (Session 1 finale — "What is an Agent?"; Session 2, Act 2, Question 2 — "Agent = Model + Harness")

**Web sources**
- [Anthropic — Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) — workflow vs. agent framing, the agent loop as perceive/decide/act, accessed 2026-08-21
