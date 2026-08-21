# Lab Summaries Index

Condensed reference for each `labs/*.ipynb` notebook — read these first for concept/structure/code-pattern questions; open the actual notebook only when the exact live code, a specific cell's current state, or full output is needed. See `CLAUDE.md` → "Reference before teaching" for when to use which.

For a topic-first, revision-ready reference built from these summaries (concept pages, a capstone milestone map, and interview prep), see `knowledge-base/index.md`.

- [Day1-Session1-Foundations.md](Day1-Session1-Foundations.md) — Raw LLM client vs LiteLLM comparison (stateless APIs, completion() knobs, JSON modes); structured-output invoice parser with a repair loop. Milestone 1.
- [Day1-Session2-ToolCalling.md](Day1-Session2-ToolCalling.md) — Travel-assistant tool calling (mocked+MCP dual implementations, reliability wrappers, tool-call loop) and a research agent (ReAct, Reflection). Milestone 2.
- [Day2-Session1-MemoryEngineering.md](Day2-Session1-MemoryEngineering.md) — Four kinds of memory (working/episodic/semantic/procedural) via Supermemory; lossy context-compression with tested recall. Milestone 3.
- [Day2-Session2-RAGRetrievalEval.md](Day2-Session2-RAGRetrievalEval.md) — Ingestion of 3 real document structures, hybrid (dense+BM25/RRF) retrieval, reranking, cited grounded answers with injection defense, and a precision@k/recall@k/MRR evaluation harness. Milestone 4.
- [Day3-Session1-LangGraphPatterns.md](Day3-Session1-LangGraphPatterns.md) — Agent autonomy spectrum and 5 minimal graph patterns, the 4 named agentic patterns (ReAct/Planner-Executor/Reflection/Supervisor-Worker), and a checkpointed human-in-the-loop document-approval LangGraph workflow surviving a kernel restart. Milestone 5.
- [Day3-Session2-MultiAgentProtocols.md](Day3-Session2-MultiAgentProtocols.md) — Five-agent supervisor research team with enforced write-scopes and dual critics; a sandboxed FastMCP server consumed by LangChain/an agent/the team; appendix on A2A (agent-to-agent) and AP2 (cryptographic payment authorization). Milestone 6.
- [Day4-Session1-LangfuseHardening.md](Day4-Session1-LangfuseHardening.md) — Instrumenting the research team with nested Langfuse spans/tags/cost-tracking, and hardening a flaky tool with seeded fault injection, retries, fallback, and a circuit breaker. Milestone 7.
- [Day4-Session2-EvalGuardrails.md](Day4-Session2-EvalGuardrails.md) — Component-level evaluation of a 4-part agent (tools/retrieval/planning/answer) with deterministic scorers + 3 LLM judges (Ragas/DeepEval/TruLens) via Langfuse experiments, a guardrails layer (schema + injection detection), and packaging behind a FastAPI+ngrok endpoint. Milestone 8.

lab-summaries/Day1-Session2-ToolCalling.md:1:# Day 1 · Session 2 — Tool Calling & Single-Agent Patterns
lab-summaries/Day1-Session2-ToolCalling.md:7:## Setup
lab-summaries/Day1-Session2-ToolCalling.md:12:## Lab A — Travel Assistant with Tools
lab-summaries/Day1-Session2-ToolCalling.md:27:## Lab B — Autonomous Research Agent (ReAct + Reflection)
lab-summaries/Day1-Session2-ToolCalling.md:33:## Gotchas / lessons called out
lab-summaries/Day2-Session1-MemoryEngineering.md:1:# Day 2 · Session 1 — Memory Engineering
lab-summaries/Day2-Session1-MemoryEngineering.md:7:## Lab A — Four Kinds of Memory (CoALA taxonomy)
lab-summaries/Day2-Session1-MemoryEngineering.md:25:## Lab B — When Memory Runs Out (context compression)
lab-summaries/Day2-Session1-MemoryEngineering.md:42:## Gotchas
lab-summaries/Day3-Session2-MultiAgentProtocols.md:1:# Day 3 · Session 2 — Multi-Agent Collaboration and Agent Protocols
lab-summaries/Day3-Session2-MultiAgentProtocols.md:9:## Lab A — Research team with a supervisor
lab-summaries/Day3-Session2-MultiAgentProtocols.md:13:### A1 — Team state & permissions
lab-summaries/Day3-Session2-MultiAgentProtocols.md:16:### A2 — Five specialists
lab-summaries/Day3-Session2-MultiAgentProtocols.md:23:### A3 — The supervisor: model may *route*, not *authorise*
lab-summaries/Day3-Session2-MultiAgentProtocols.md:31:### A4 — Topology
lab-summaries/Day3-Session2-MultiAgentProtocols.md:36:### A5 — Why the critics exist, demonstrated
lab-summaries/Day3-Session2-MultiAgentProtocols.md:39:## Lab B — Model Context Protocol (Milestone 6)
lab-summaries/Day3-Session2-MultiAgentProtocols.md:45:### B1 — FastMCP server (project folder exposed safely)
lab-summaries/Day3-Session2-MultiAgentProtocols.md:54:### B2 — MultiServerMCPClient
lab-summaries/Day3-Session2-MultiAgentProtocols.md:65:### B3 — Agent over MCP
lab-summaries/Day3-Session2-MultiAgentProtocols.md:68:### B4 — Stateful sessions
lab-summaries/Day3-Session2-MultiAgentProtocols.md:77:### B5 — Bring it together (Milestone 6)
lab-summaries/Day3-Session2-MultiAgentProtocols.md:80:## Appendix — A2A and AP2 (illustrative, not coursework)
lab-summaries/Day3-Session2-MultiAgentProtocols.md:88:## Pitfall table highlights (Session 2 specific, beyond Session 1's)
lab-summaries/Day4-Session1-LangfuseHardening.md:1:# Day 4 · Session 1 — LangFuse Instrumentation, Failure Injection, Production...
lab-summaries/Day4-Session1-LangfuseHardening.md:7:## Lab A — Instrument the research team with LangFuse
lab-summaries/Day4-Session1-LangfuseHardening.md:18:### Pitfall table (Lab A)
lab-summaries/Day4-Session1-LangfuseHardening.md:26:## Lab B — Failure Injection & Production Hardening
lab-summaries/Day4-Session1-LangfuseHardening.md:38:### Pitfall table (Lab B)
lab-summaries/Day4-Session1-LangfuseHardening.md:46:## Evaluation section (bridges into Day4-S2)
lab-summaries/Day4-Session2-EvalGuardrails.md:1:# Day 4 · Session 2 — Evaluation, Guardrails & Continuous Improvement
lab-summaries/Day4-Session2-EvalGuardrails.md:9:## Rate-limit-safe call wrapper
lab-summaries/Day4-Session2-EvalGuardrails.md:12:## The system under test — four independently-gradable components
lab-summaries/Day4-Session2-EvalGuardrails.md:20:## Golden dataset — 20 items, 5 per component
lab-summaries/Day4-Session2-EvalGuardrails.md:23:## Guardrails layer — independent of answer quality
lab-summaries/Day4-Session2-EvalGuardrails.md:28:## Deterministic scorers (pure Python, no LLM, milliseconds)
lab-summaries/Day4-Session2-EvalGuardrails.md:34:## LLM-judge scorers — three independent judges
lab-summaries/Day4-Session2-EvalGuardrails.md:40:## Wiring through Langfuse
lab-summaries/Day4-Session2-EvalGuardrails.md:51:## Lab B — Package as a FastAPI service
lab-summaries/Day4-Session2-EvalGuardrails.md:58:## Architecture review write-up template (reusable for Milestone 8)