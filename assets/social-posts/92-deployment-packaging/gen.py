import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "\"It Runs On My Machine\" Proves Almost Nothing",
      ["localhost only exists on the machine that started the process — a teammate, a Postman collection, or a real user anywhere else on the internet can't reach it."])

slide(p("slide-02.png"), 2, 6, "Three Separate Things", "A Demo Can Skip All Three. A Shippable Service Can't.",
      ["A public network path. Configuration and secrets read from the environment, never hardcoded. An operational surface — logging, rate-limit handling, a rollback plan."])

slide(p("slide-03.png"), 3, 6, "Sample Code", "Running Uvicorn From Inside A Notebook Process",
      ["A fresh event loop is required — nest_asyncio's patched asyncio.run() is incompatible with the loop_factory argument server.run() passes internally."],
      code="def _run_server():\n    loop = asyncio.new_event_loop()\n    asyncio.set_event_loop(loop)\n    loop.run_until_complete(server.serve())\n\nthreading.Thread(target=_run_server, daemon=True).start()\npublic_url = ngrok.connect(8000, \"http\")")

slide(p("slide-04.png"), 4, 6, "The Ephemeral-URL Trap", "Share A Postman Collection, Not A URL",
      ["Free-tier ngrok URLs change on every tunnel restart. A shared collection re-points to whatever URL is current; a bare URL just goes stale."])

slide(p("slide-05.png"), 5, 6, "The Real Definition", "\"Ready To Ship\" Is A Document A Team Signs",
      ["Not a claim that the agent gave a right answer once. Its job and limits, an evaluation report, an operational runbook — who can pause it, investigate a trace, roll back a release — and honestly-stated known limitations."])

slide(p("slide-06.png"), 6, 6, "Takeaway", "Validate Every Secret At Startup, Never Lazily",
      ["A missing key caught at process start fails loud before any traffic is served — caught on first use, it surfaces as a random user's request failing, hours after deploy."],
      closing_q="If you had to write the operational runbook for your agent today, could you?")

print("done: 92")
