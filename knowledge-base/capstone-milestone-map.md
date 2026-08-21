# Capstone milestone map

Maps each concept in this knowledge base to the ShopSense/Kartway capstone milestone (M1-M8) it shows up in — the thread from `lab-summaries/`'s own "Capstone tie-in" lines, kept alive without naming any file after a day/session.

| Milestone | What it builds | Key concepts |
|---|---|---|
| M1 | Provider-agnostic LLM client + structured intake | [[raw-llm-clients]], [[litellm-basics]], [[structured-output-repair-loops]], [[tokens-and-tokenization]] |
| M2 | Tool-enabled single agent | [[tool-calling-fundamentals]], [[agentic-loop-fundamentals]], [[react-pattern]], [[reflection-pattern]] |
| M3 | Persistent memory | [[memory-types]], [[supermemory]], [[context-compression]] |
| M4 | Production RAG + evaluation baseline | [[ingestion]], [[chunking]], [[embeddings-models]], [[bm25-sparse-retrieval]], [[dense-retrieval]], [[hybrid-retrieval-rrf]], [[qdrant]], [[reranking]], [[grounded-answers-injection-defense]], [[retrieval-eval-metrics]] |
| M5 | Orchestrated LangGraph workflow with checkpointing | [[agent-topologies]], [[graph-engineering-mindset]], [[langgraph-state]], [[langgraph-nodes]], [[langgraph-edges]], [[langgraph-conditional-edges]], [[langgraph-graph-patterns]], [[langgraph-checkpointing-hitl]], [[idempotency-and-side-effects]] |
| M6 | Multi-agent supervisor team + MCP-backed tool swap | [[supervisor-worker-teams]], [[langgraph-agentic-patterns]], [[mcp-fastmcp]], [[agent-protocols-a2a-ap2]], [[auth-and-multi-tenancy]] |
| M7 | Observability + reliability hardening | [[langfuse-tracing]], [[retry-fallback-patterns]], [[circuit-breaker-pattern]] |
| M8 | Evaluation, guardrails, and packaged endpoint | [[eval-driven-development-mindset]], [[deterministic-scorers]], [[llm-judges-eval]], [[guardrails-injection-detection]], [[fastapi-fundamentals]], [[deployment-packaging]] |

[[architecture-of-an-agentic-system]] and [[putting-it-all-together]] are the two whole-system pages that tie all eight milestones together rather than belonging to any single one.

## Notes

- This table's milestone numbers and titles are taken directly from each `lab-summaries/*.md` file's own "Capstone tie-in" line and `lab-summaries/INDEX.md` — separate from the project's own numbered build order, which describes a different thing: the repeatable *pattern* ("single agent → resilience → tracing, repeated per agent") each of the four ShopSense agents (Triage, Policy RAG, Order-Actions, Escalation Reviewer) follows, not a sequence of milestones. M2/M7's resilience-and-tracing pattern is that build order applied to the specific agents built in M6-M7's labs; M1/M3/M4 are earlier layers the same pattern doesn't yet apply to. Read the build order as *how* each agent gets built, and this table as *what got built when*.
- Some pages don't map to any milestone above and are intentionally omitted: [[testing-agent-code]] and [[privacy-and-pii-handling]] are cross-cutting concerns the labs demonstrate but that don't tie to one specific milestone's deliverable.
