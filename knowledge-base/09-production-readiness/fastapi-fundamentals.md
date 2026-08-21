---
stage: "09-production-readiness"
tools: [fastapi, starlette, pydantic, uvicorn]
tags: [fastapi, api, deployment]
last_verified: 2026-08-20
verified_against: "no fastapi version pinned in this repo's pyproject.toml as of 2026-08-20 — see Course vs. production"
---

# FastAPI fundamentals

FastAPI is a Python web framework, built on Starlette (ASGI) and Pydantic, that turns a working agent into a callable HTTP endpoint — request/response validated by the same type hints you'd already be using for tool schemas.

## Prerequisites
- [[pydantic-basics]]
- [[async-await-for-llm-apps]]
- [[env-secrets-and-config]]

## In plain English

Everything in this knowledge base up to this point runs inside a notebook or a script you call directly. A real user doesn't run your Python file — they need a URL to send a request to. FastAPI's job is to be that thin wrapping layer: define a function, decorate it with the HTTP method and path, type-annotate its inputs and outputs with Pydantic models, and FastAPI generates the request parsing, validation, error responses, and interactive API documentation (`/docs`) from those type hints alone — the same declare-the-shape-with-types habit [[pydantic-basics]] and [[structured-output-repair-loops]] already built for LLM tool schemas, now applied to the HTTP boundary.

Because it's built on Starlette (an ASGI framework, not the older synchronous WSGI model Flask started from), an endpoint can `await` an LLM call, a retrieval query, or a database read without blocking the whole worker process on that one request — which matters directly for agent endpoints, since almost every request spends most of its wall-clock time waiting on an external LLM or vector-DB call, exactly the kind of I/O-bound wait [[async-await-for-llm-apps]] covers.

## Core mechanics

| Concept | What it does |
|---|---|
| `@app.get`/`@app.post`/… | Registers a path + HTTP method against a handler function |
| Request body model | A Pydantic `BaseModel` type-annotated as a function parameter — FastAPI parses and validates the JSON body against it automatically |
| Response model | `response_model=` (or a return type annotation) — validates and filters the outgoing shape, so internal fields never leak by accident |
| `HTTPException` | Raise to return a specific status code + detail body (e.g. 422 for a guardrail rejection) instead of a generic 500 |
| Dependency injection (`Depends`) | Shared setup (a DB session, an authenticated identity, a warmed-up client) resolved once per request and injected into the handler |
| `lifespan` context manager | Startup/shutdown hooks — the place to warm up clients and validate required config *before* the first request, not on it |
| Automatic docs | `/docs` (Swagger UI) and `/redoc`, generated from the same type hints, no separate spec file to maintain |

## Sample code

Lab-sourced (`labs/Day4 Session 2 - Evaluation, Guardrails and Continuous Improvement.ipynb`) — the `/chat` and `/health` endpoints wrapping the agent and guardrail check from [[guardrails-injection-detection]]:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    route: str
    final_answer: str
    retrieved_doc_ids: list[str]
    # deliberately omits internal trace fields (tool_call, tool_result,
    # plan_reasoning) — not part of the public API contract

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    trace = await run_agent(req.query)
    check = guardrail_check(trace)
    if not check["passed"]:
        # guardrail failures are visible to the caller, not silently dropped
        raise HTTPException(status_code=422, detail={"flags": check["flags"]})
    return ChatResponse(
        route=trace["route"],
        final_answer=trace["final_answer"],
        retrieved_doc_ids=[d["id"] for d in trace["retrieved_docs"]],
    )

@app.get("/health")
async def health():
    return {"status": "ok"}  # cheap liveness check, no LLM call, never rate-limited
```

Version note: this repo's `pyproject.toml` doesn't pin `fastapi` — treat the [official docs](https://fastapi.tiangolo.com/) as current-version truth rather than any specific pinned release when adding it as a dependency.

## Alternatives

| Framework | Approach | Boring/simple alternative to FastAPI? |
|---|---|---|
| [Flask](https://flask.palletsprojects.com/en/stable/) | WSGI by default (synchronous, one worker per request); optional `async def` views since 2.0 via `asgiref`, but each async view still ties up one worker for its duration rather than freeing it for other requests | No — same tier, older concurrency model |
| [Django REST Framework](https://www.django-rest-framework.org/) | Full-featured REST toolkit built on top of Django; serializer classes for validation, a browsable API UI, requires a full Django project underneath | No — heavier, brings the whole Django ORM/admin/auth stack whether you need it or not |
| [Starlette](https://www.starlette.io/) | The ASGI toolkit FastAPI itself is built on — routing, middleware, WebSockets, background tasks, no built-in request/response validation or auto-docs | **Yes** — the boring option; genuinely async, but you write the Pydantic validation and OpenAPI wiring yourself instead of getting it generated from type hints |
| Raw ASGI (no framework) | Implement the `async def app(scope, receive, send)` protocol directly | Yes, more extreme — no routing, no validation, no docs; almost never chosen outside teaching ASGI itself |

## How this shows up in the capstone

Milestone 8 — `/chat` and `/health` package the full agent (guardrails + eval-hardened) as a deployable HTTP service; `/chat` wraps `run_agent` + `guardrail_check` and returns a filtered `ChatResponse`, `/health` is a liveness probe; see [[capstone-milestone-map]].

## Interview fire round

- **Q: Why does FastAPI's async support matter more for an agent endpoint than for a typical CRUD API?**
  A: An agent endpoint spends nearly all its wall-clock time waiting on external I/O — an LLM call, a vector search, a tool call — not doing CPU work. `async def` handlers let one worker serve other requests during that wait instead of blocking on it, which a synchronous WSGI framework can't do without more workers/processes.
- **Q: Why does `ChatResponse` deliberately omit fields like `tool_call` and `plan_reasoning` that the trace dict contains?**
  A: A `response_model` isn't just documentation — it filters what actually gets serialized back to the caller. Internal trace fields aren't part of the public API contract, and leaving them in `response_model` would silently promote implementation detail into a stable-looking API surface.

## Production gotchas & best practices

- Lab gotcha: running `uvicorn.run()` inside a notebook blocks the cell forever — run the server in a background daemon thread with its own fresh event loop, driven via `loop.run_until_complete(server.serve())` rather than `server.run()`, because `nest_asyncio.apply()` (needed elsewhere for async LLM-judge scorers) patches `asyncio.run()` in a way incompatible with the `loop_factory` argument `server.run()` passes internally (`lab-summaries/Day4-Session2-EvalGuardrails.md`).
- Lab gotcha (this repo, `labs/production-notes.md` — FastAPI section): prefix-based ownership checks on identifiers like `thread_id` prevent one tenant's request from touching another's resource by ID guessing; a deliberate asymmetry between a customer-facing resume endpoint and an internal reviewer-decision endpoint keeps their permission models from being accidentally merged; eager dependency warm-up inside `lifespan` avoids unattributed latency landing on whichever request happens to arrive first.
- Production practice: validate all required secrets/config at process startup (in `lifespan`), not lazily on first use — see [[env-secrets-and-config]] — so a missing API key fails loud at deploy time instead of on a random user's request.
- Production practice: keep the response model narrow and explicit rather than returning an internal state dict directly — every field in a `response_model` is a field you've committed to as a stable API contract.

## Course vs. production

The lab exposes the agent through a single FastAPI process run inside the same notebook as the agent code, tunneled out via ngrok for testing (see [[deployment-packaging]]). In production, the FastAPI app is typically deployed as its own process/container behind a real reverse proxy or load balancer, with authentication middleware, structured logging, and tracing (see [[langfuse-tracing]]) wired in at the application layer rather than tunneled ad hoc — and horizontally scaled across multiple workers rather than the lab's single background thread.

## Related
- **Builds on** — [[pydantic-basics]], [[async-await-for-llm-apps]]
- **Feeds into** — [[deployment-packaging]], [[putting-it-all-together]]
- **Related** — [[guardrails-injection-detection]] (422 rejection response), [[env-secrets-and-config]]

## Sources

**Lab sources**
- `lab-summaries/Day4-Session2-EvalGuardrails.md` (§ "Lab B — Package as a FastAPI service")
- `labs/Day4 Session 2 - Evaluation, Guardrails and Continuous Improvement.ipynb`
- `labs/production-notes.md` (§ "FastAPI" line under the summary table)
- `presentations/day4.md` (Session 2, Act 4 — "Shipping It, and What Happens After": FastAPI packaging as one gate of production-readiness)

**Web sources**
- [FastAPI documentation](https://fastapi.tiangolo.com/) — async support, Pydantic-based validation, automatic OpenAPI docs, built on Starlette + Pydantic, accessed 2026-08-20
- [Flask — Using async and await (3.1.x)](https://flask.palletsprojects.com/en/stable/async-await/) — WSGI-by-default, optional coroutine views via `asgiref`, one worker per request even for async views, accessed 2026-08-20
- [Django REST Framework](https://www.django-rest-framework.org/) — serializer-based validation, browsable API, requires Django 5.2/6.0/6.1 + Python 3.10-3.14, accessed 2026-08-20
- [Starlette](https://www.starlette.io/) — "the little ASGI framework that shines," lightweight toolkit FastAPI builds on, accessed 2026-08-20
