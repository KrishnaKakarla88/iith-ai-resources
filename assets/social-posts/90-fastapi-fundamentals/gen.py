import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "A Real User Can't Run Your Python File",
      ["FastAPI is the thin wrapping layer: type-annotate a function's inputs and outputs with Pydantic, and it generates request parsing, validation, error responses, and docs from those type hints alone."])

slide(p("slide-02.png"), 2, 6, "Why Async Matters Here Specifically", "Almost Every Request Is Waiting, Not Computing",
      ["An agent endpoint spends nearly all its wall-clock time waiting on an LLM call, a vector search, a tool call.",
       "async def lets one worker serve other requests during that wait instead of blocking on it."])

slide(p("slide-03.png"), 3, 6, "Sample Code", "response_model Filters, It Doesn't Just Document",
      ["Internal trace fields — tool_call, plan_reasoning — deliberately never appear here. Leaving them in would silently promote implementation detail into a stable-looking API surface."],
      code="class ChatResponse(BaseModel):\n    route: str\n    final_answer: str\n    retrieved_doc_ids: list[str]\n\n@app.post(\"/chat\", response_model=ChatResponse)\nasync def chat(req: ChatRequest):\n    trace = await run_agent(req.query)\n    check = guardrail_check(trace)\n    if not check[\"passed\"]:\n        raise HTTPException(422, detail={\"flags\": check[\"flags\"]})")

slide(p("slide-04.png"), 4, 6, "The Guardrail Response", "422, Not A Silent Drop",
      ["A guardrail failure is visible to the caller in the response body — never a request that just quietly disappears."])

slide(p("slide-05.png"), 5, 6, "Production Practice", "Validate Config At Startup, Not On First Use",
      ["A missing API key checked in the lifespan hook fails loud at deploy time — not lazily, on a random user's request."])

slide(p("slide-06.png"), 6, 6, "Takeaway", "Every Field In response_model Is A Commitment",
      ["A stable API contract you now have to maintain, not just a return value you happened to expose."],
      closing_q="Does your endpoint's response model expose an internal trace field it shouldn't?")

print("done: 90")
