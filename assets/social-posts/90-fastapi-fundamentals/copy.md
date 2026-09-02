--- LINKEDIN ---
Everything up to this point in an agent build runs inside a notebook or a script you call directly. A real user doesn't run your Python file — they need a URL. FastAPI's job is to be that thin wrapping layer: type-annotate a function's inputs and outputs with Pydantic, and it generates request parsing, validation, error responses, and interactive docs from those type hints alone.

Async matters more here than for a typical CRUD API. An agent endpoint spends nearly all its wall-clock time waiting on an LLM call, a vector search, a tool call — not doing CPU work. async def lets one worker serve other requests during that wait instead of blocking on it, which a synchronous framework can't do without more workers.

class ChatResponse(BaseModel):
    route: str
    final_answer: str
    retrieved_doc_ids: list[str]

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    trace = await run_agent(req.query)
    check = guardrail_check(trace)
    if not check["passed"]:
        raise HTTPException(422, detail={"flags": check["flags"]})

response_model isn't just documentation — it filters what actually gets serialized back to the caller. Internal trace fields like tool_call or plan_reasoning deliberately never appear in ChatResponse; leaving them in would silently promote implementation detail into a stable-looking API surface. A guardrail failure surfaces as a 422 with the actual flags in the body — visible to the caller, never silently dropped.

Production practice: validate all required secrets and config at process startup, inside the lifespan hook, not lazily on first use — a missing API key should fail loud at deploy time, not on a random user's request.

Every field in a response_model is a field you've committed to as a stable API contract.

Does your endpoint's response model expose an internal trace field it shouldn't?

#AppliedAI #AIEngineering #LLM #LangGraph

--- INSTAGRAM ---
A real user can't run your Python file. They need a URL. 🌐

FastAPI generates validation, error responses, and docs straight from type hints. async matters here because an agent endpoint spends almost all its time waiting on an LLM, not computing.

response_model filters, it doesn't just document — internal trace fields never leak into the public API.

Full mechanics in the carousel.

#AppliedAI #AIEngineering #LLM #LangGraph #GenAI

--- VISUAL FORMAT ---
carousel — 6 slides
1. Title — "A Real User Can't Run Your Python File"
2. Why async matters here specifically
3. Sample code — response_model filters, it doesn't just document (code)
4. The guardrail response — 422, not a silent drop
5. Production practice — validate config at startup, not on first use
6. Takeaway — every field in response_model is a commitment (closing question)
