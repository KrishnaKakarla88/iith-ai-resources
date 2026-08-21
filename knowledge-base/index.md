# ShopSense Knowledge Base

A topic-first reference for the AI-agent stack behind the ShopSense/Kartway capstone, written for a reader who knows basic Python but nothing about this stack yet. Read [[capstone-milestone-map]] alongside it to see how each concept lands in the capstone.

## Start Here (guided path)

Read in this order — each stage assumes the ones before it.

1. **00 — AI & LLM basics**, starting at [[what-is-an-llm]] — what an LLM actually is, tokens, context windows, prompting, and the fine-tune-vs-RAG decision.
2. **01 — Python refresher**, starting at [[python-data-types-and-mutability]] — the everyday Python the labs assume you already have fluent.
3. **02 — Python for AI agents**, starting at [[type-hints-basics]] — type hints, Pydantic, decorators, async — the patterns this stack leans on.
4. **03 — Foundations**, starting at [[raw-llm-clients]] — calling an LLM directly, then through LiteLLM as a gateway, structured output, streaming, rate limits.
5. **04 — Tool calling & single agents**, starting at [[workflow-vs-agent-autonomy-spectrum]] — the autonomy spectrum, the agentic loop, tool calling, ReAct, reflection.
6. **05 — Memory**, starting at [[memory-types]] — memory types, Supermemory, context compression.
7. **06 — RAG**, starting at [[ingestion]] — ingestion through chunking, embeddings, hybrid retrieval, reranking, and retrieval eval.
8. **07 — Orchestration**, starting at [[agent-topologies]] — graph-engineering mindset, LangChain vs LangGraph, LangGraph state/nodes/edges/patterns.
9. **08 — Multi-agent systems**, starting at [[supervisor-worker-teams]] — supervisor-worker teams, MCP/FastMCP, agent protocols, auth & multi-tenancy.
10. **09 — Production readiness**, starting at [[testing-agent-code]] — testing, tracing, privacy, retry/circuit-breaker, eval, guardrails, FastAPI, deployment.

Once you've been through 00-09, **[[interview-prep-overview]]** (stage 10) is a separate mock-interview session — harder, real-interview-style questions organized by interview round (fundamentals, system design, production reliability, coding/debugging, behavioral) rather than by topic, meant to be worked through right before an actual interview.

For a full page-by-page listing of every stage, use the sidebar nav (MkDocs) or the file explorer/graph view (Obsidian).

## Tools & Libraries quick index

*(Alphabetical, cross-stage.)*

- **FastAPI** — [[fastapi-fundamentals]]
- **FastMCP** — [[mcp-fastmcp]], [[langchain-tool-integration]]
- **Langfuse** — [[langfuse-tracing]], [[eval-driven-development-mindset]]
- **LangChain** — [[langchain-vs-langgraph]], [[langchain-runnables-lcel]], [[langchain-chains-vs-agents]], [[langchain-tool-integration]]
- **LangGraph** — [[agent-topologies]], [[graph-engineering-mindset]], [[langgraph-state]], [[langgraph-nodes]], [[langgraph-edges]], [[langgraph-conditional-edges]], [[langgraph-graph-patterns]], [[langgraph-agentic-patterns]], [[langgraph-checkpointing-hitl]], [[idempotency-and-side-effects]], [[auth-and-multi-tenancy]], [[supervisor-worker-teams]]
- **LiteLLM** — [[litellm-basics]], [[litellm-as-gateway]], and used across most of stages 00/03/04/05
- **Pydantic** — [[pydantic-basics]], [[structured-output-repair-loops]], [[fastapi-fundamentals]], [[guardrails-injection-detection]]
- **Qdrant** — [[qdrant]], [[dense-retrieval]]
- **Ragas / DeepEval / TruLens** — [[llm-judges-eval]], [[eval-driven-development-mindset]]
- **Supermemory** — [[supermemory]], [[memory-types]]
- **tenacity / pybreaker** — [[retry-fallback-patterns]], [[circuit-breaker-pattern]]
- **rank_bm25 / sentence-transformers** — [[bm25-sparse-retrieval]], [[reranking]]
