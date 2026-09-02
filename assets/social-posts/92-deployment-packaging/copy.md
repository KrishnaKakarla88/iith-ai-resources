--- LINKEDIN ---
A working FastAPI app on localhost:8000 proves the code runs. It proves nothing about whether a teammate, a Postman collection, or a real user anywhere else on the internet can reach it — localhost only exists on the machine that started the process.

Three separate things have to be sorted, and a demo can skip all three while a shippable service can't: a public network path, configuration and secrets read from the environment rather than hardcoded, and an operational surface — logging, rate-limit handling, a rollback plan — that nobody's production depends on a demo needing.

def _run_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(server.serve())

threading.Thread(target=_run_server, daemon=True).start()
public_url = ngrok.connect(8000, "http")

Running uvicorn inside a notebook process needs its own fresh event loop specifically because a patched asyncio.run() (needed elsewhere for async judge scorers) is incompatible with the loop_factory argument server.run() passes internally.

The ephemeral-URL trap: free-tier ngrok URLs change on every tunnel restart. Share a Postman collection with teammates, not the bare URL — a collection re-points to whatever's current; a URL just goes stale.

The real definition worth internalizing: "ready to ship" is a document a team can sign off on — the agent's job and limits, an evaluation report, an operational runbook covering who can pause it or roll back a release, and honestly-stated known limitations. Not a claim that emerges automatically once the agent gave a right answer once.

Validate every required secret at process startup, never lazily on first use — a missing key should fail loud before any traffic is served, not surface as a random user's request failing hours after deploy.

If you had to write the operational runbook for your agent today, could you?

#AppliedAI #AIEngineering #LLM #LangGraph

--- INSTAGRAM ---
"It runs on my machine" proves almost nothing. 🌐

Three things a demo skips that a shippable service can't: a public path, env-based config, an operational surface.

public_url = ngrok.connect(8000, "http")

Free-tier URLs are ephemeral — share a Postman collection, not the raw URL.

"Ready to ship" is a document a team signs, not a claim that emerges automatically.

Full breakdown in the carousel.

#AppliedAI #AIEngineering #LLM #LangGraph #GenAI

--- VISUAL FORMAT ---
carousel — 6 slides
1. Title — "\"It Runs On My Machine\" Proves Almost Nothing"
2. Three separate things — a demo can skip all three
3. Sample code — running uvicorn from inside a notebook process (code)
4. The ephemeral-URL trap — share a Postman collection, not a URL
5. The real definition — "ready to ship" is a document a team signs
6. Takeaway — validate every secret at startup, never lazily (closing question)
