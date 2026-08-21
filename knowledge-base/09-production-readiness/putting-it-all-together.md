---
stage: "09-production-readiness"
tags: [architecture, end-to-end, capstone]
last_verified: 2026-08-20
---

# Putting it all together

One customer request, walked through every layer this knowledge base covered — intake, agent, tools/RAG/memory, orchestration, tracing, API — closing the loop [[architecture-of-an-agentic-system]] opened back in stage 00.

## Prerequisites
- [[architecture-of-an-agentic-system]]
- [[fastapi-fundamentals]]
- [[langfuse-tracing]]
- [[eval-driven-development-mindset]]

## In plain English

Every earlier page in this knowledge base zoomed into one layer — how tokens work, how a tool call is routed, how a chunk gets embedded, how a graph checkpoints its state. None of them individually show what a real request actually experiences on its way through a deployed system. This page is the reverse move: pick one concrete request, and trace it through every layer in order, naming which earlier page covers each hop. It's the same request [[architecture-of-an-agentic-system]] promised to show you once you'd read everything else — this is that promise paid off.

Take a Kartway customer message: *"My order #KW-88213 hasn't arrived and it's been 9 days — what's your policy, and can I get a refund?"*

## Core mechanics

The request's path, one hop at a time, each hop naming the layer that handles it and the page that explains it:

1. **Intake — the request arrives at the API boundary.** A FastAPI `/chat` endpoint (see [[fastapi-fundamentals]]) receives `{"query": "...", "session_id": "..."}"`, validated against a Pydantic request model before any agent code runs.

2. **Identity and memory lookup.** The customer's identity comes from the authenticated session, never guessed from the message text (see [[auth-and-multi-tenancy]]) — a `customer_ref` in the free text is not trusted for identity. That identity scopes a memory lookup (see [[memory-types]], [[supermemory]]) for anything relevant already known about this customer or this order.

3. **Planning/routing.** One LLM call decides which path this request needs — a tool call (order status lookup), a retrieval call (policy question), or both — forced into a structured shape via [[structured-output-repair-loops]]-style constrained output, the same "schema governs what the model can produce" mechanism covered there.

4. **Tools and RAG, in parallel or in sequence depending on topology** (see [[agent-topologies]]):
   - A tool call fetches live order status — deterministic, no ambiguity about "what happened," handled per [[tool-calling-fundamentals]].
   - A retrieval call answers "what's your policy" — the query is embedded (see [[embeddings-models]]), searched via hybrid retrieval (see [[hybrid-retrieval-rrf]], [[qdrant]]), reranked (see [[reranking]]), and the retrieved policy chunk is checked for injected instructions before it's trusted as context (see [[grounded-answers-injection-defense]]).

5. **Orchestration.** If this spans more than one specialized agent (an order-status agent and a policy/RAG agent, say), a graph coordinates them — state passed between nodes, conditional edges deciding whether escalation is needed, a supervisor merging both agents' output into one response (see [[graph-engineering-mindset]], [[langgraph-agentic-patterns]], [[supervisor-worker-teams]]). If a refund needs human sign-off above a threshold, that's a checkpointed interrupt, not a blind tool call (see [[langgraph-checkpointing-hitl]], [[idempotency-and-side-effects]] for what happens if the process restarts mid-approval).

6. **Guardrails, independent of whether the answer is *good*.** The final answer is schema-checked, scanned for injected content it might have picked up from the retrieved policy chunk, and — if it fails — replaced with a safe fallback rather than shown (see [[guardrails-injection-detection]]).

7. **Tracing, the whole way through.** Every hop above — the planning call, the tool call, the retrieval call, the guardrail check — is a nested span under one trace ID, tagged with session/customer identifiers and cost/token counts, redacted of PII before it leaves the process (see [[langfuse-tracing]], [[privacy-and-pii-handling]]). This is what makes "why did this answer take 14 seconds" a lookup instead of a guess.

8. **Response.** The API layer returns a filtered response model — `route`, `final_answer`, whatever public fields the contract defines — deliberately omitting internal trace fields like tool arguments or planning reasoning (see [[fastapi-fundamentals]]).

9. **Off to the side, not on the request path: eval and reliability.** This one request isn't evaluated live — but it's exactly the shape of case a golden-set item would represent, scored on tool-use/retrieval/planning/final-answer separately (see [[eval-driven-development-mindset]], [[deterministic-scorers]], [[llm-judges-eval]]), and every dependency call in steps 4-6 sits behind retry/fallback and circuit-breaker protection so a flaky vector DB or LLM provider degrades this request gracefully instead of failing it outright (see [[retry-fallback-patterns]], [[circuit-breaker-pattern]]).

## Sample code

There's no single lab notebook that runs all nine hops end to end — this page is a synthesis, not a lab transcript. The two lab-sourced fragments that anchor the two ends of the chain (already shown in full on their own pages): the FastAPI `/chat` handler in [[fastapi-fundamentals]] is the entry point, and the `run_agent(query)` trace dict in [[eval-driven-development-mindset]]/[[deterministic-scorers]] is the shape every layer above writes into and every scorer/guardrail reads from — the trace dict *is* the seam where "one request" and "one gradable, traceable unit" are the same object.

## How this shows up in the capstone

This page spans the whole capstone arc rather than one milestone: M1 (single agent, tool calling) is hop 3-4's tool-call half; M2 (retry + circuit breaker) is hop 9's reliability layer; M3 (tracing from Agent 1 onward) is hop 7; M4 (policy RAG) is hop 4's retrieval half; M5 (order-actions agent) and M6 (escalation reviewer agent) are the specialized agents orchestrated in hop 5; M7 (multi-agent orchestration via LangGraph) is hop 5 in full; M8 (MCP server exposure, FastAPI endpoint, guardrails/eval) is hops 1, 6, 8, and 9. See [[capstone-milestone-map]] for the concept-to-milestone table this page's hops draw from.

## Interview fire round

- **Q: Walk me through what happens between a user's message arriving and a response going back, for a system with RAG, tools, and multi-agent orchestration.**
  A: Intake validates the request at the API boundary; identity comes from the session, never the message text; a planning step routes to tool and/or retrieval; tools execute deterministically while retrieval embeds, searches, and reranks; an orchestration layer coordinates multiple specialized agents and handles any human-in-the-loop step; guardrails check the final answer independent of whether it's *good*; every hop is a traced span under one trace ID; and the API layer returns a filtered response — while eval and reliability protections (retries, circuit breakers, golden-set scoring) sit around the whole path rather than on it.
  A: (See the Core mechanics numbered list above for the full nine-hop breakdown.)
- **Q: Why is the trace dict from the eval notebook the same shape referenced in the tracing and guardrail layers?**
  A: Keeping one trace structure that every layer writes into and every scorer/guardrail reads from is what keeps component boundaries clean — a change to how tool calls are recorded doesn't require updating three separate representations, and it's exactly what makes a request both debuggable (tracing) and gradable (eval) from the same object.

## Production gotchas & best practices

- The single most common gap between "the demo works" and "this is production-ready" is treating steps 6-9 above (guardrails, tracing, eval, reliability) as optional add-ons layered on at the end rather than built in from Agent 1 — this repo's own build order (see `CLAUDE.md`) deliberately bakes tracing in from the first agent onward rather than bolting it on later, for exactly this reason.
- Per course material (`presentations/day4.md`, Session 2 Act 4): "ready to ship" is a document a team signs — the agent's job and limits, its evaluation report, an operational runbook, and honestly-stated known limitations — not a claim that emerges automatically once every layer above technically works.
- Identity handling (hop 2) is a recurring real-incident source across this repo's own build notes: guessing customer identity from message text, rather than the authenticated session, is called out independently in both the memory and auth gotchas (`labs/production-notes.md`) as a mistake made and fixed more than once.

## Course vs. production

The lab builds and demonstrates each layer above in its own notebook, largely in isolation — a RAG notebook, a memory notebook, an orchestration notebook, an eval-and-guardrails notebook — each proving its own piece works. In production, all of these layers run inside one continuously-deployed service handling concurrent requests, where a failure in one layer (a slow vector DB, a rate-limited LLM provider, a guardrail false-rejection) has to degrade the request gracefully rather than crash the whole call — which is precisely why retry/circuit-breaker patterns, tracing, and eval aren't separate concerns bolted on after the fact, but part of the same request path from the start.

## Related
- **Builds on** — [[architecture-of-an-agentic-system]]
- **Synthesizes** — [[tool-calling-fundamentals]], [[hybrid-retrieval-rrf]], [[memory-types]], [[graph-engineering-mindset]], [[langfuse-tracing]], [[fastapi-fundamentals]]
- **Protected by** — [[guardrails-injection-detection]], [[retry-fallback-patterns]], [[circuit-breaker-pattern]], [[eval-driven-development-mindset]]

## Sources

**Lab sources**
- `lab-summaries/Day4-Session2-EvalGuardrails.md` (§ "The system under test — four independently-gradable components", § "Lab B — Package as a FastAPI service")
- `presentations/day4.md` (Session 2, Act 4 — "Shipping It, and What Happens After": the production-readiness checklist this page's end-to-end walkthrough is organized against)
- [[capstone-milestone-map]] (M1-M8 concept-to-milestone table this page's "How this shows up in the capstone" section is drawn from)
- `CLAUDE.md` (this repo's own build order — tracing baked in from Agent 1, not bolted on later)

**Web sources**
- No new web sources — this page synthesizes concepts already sourced individually on the pages it links to; see each linked page's own Sources section for its citations.
