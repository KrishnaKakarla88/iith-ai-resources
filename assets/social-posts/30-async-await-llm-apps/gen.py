import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 7, "Concept", "Async/Await For LLM Apps",
      ["Nearly every real operation an LLM app does is I/O-bound — "
       "waiting on a response, not computing."])

slide(p("slide-02.png"), 2, 7, "Concept", "Pause At I/O, Don't Block On It",
      ["A synchronous function that calls something slow sits the whole program idle until it returns.",
       "**async def** defines a coroutine — calling it creates an object that must be awaited."],
      code="async def get_tools(): ...")

slide(p("slide-03.png"), 3, 7, "Mechanism", "await Yields Control, Not Just Waits",
      ["**await** pauses the current coroutine and hands control back to the event loop.",
       "The loop runs something else useful, then resumes once the result is ready."],
      diagram=("flow", ["Call", "Await Point", "Loop Runs Elsewhere", "Resume"]))

slide(p("slide-04.png"), 4, 7, "Why It Matters Here", "Every Wait Is a Chance to Overlap",
      ["An LLM completion call, an MCP tool call, a Supermemory write — all I/O-bound, mostly waiting.",
       "Async lets one process handle many such waits concurrently instead of serializing them."])

slide(p("slide-05.png"), 5, 7, "Gotcha", "Calling Async From Sync, Unawaited",
      ["Calling an async def function without awaiting it returns a coroutine object, not a result.",
       "Python usually warns but doesn't raise — the bug surfaces downstream instead."],
      code="result = get_tools()  # coroutine object, not the actual tools")

slide(p("slide-06.png"), 6, 7, "Production Note", "A Session Belongs To One Task",
      ["MCP's stdio transport is built on anyio TaskGroups, scoped to the Task that created them.",
       "LangGraph runs each node in its own Task — caching a session across nodes breaks that scoping."])

slide(p("slide-07.png"), 7, 7, "Takeaway", "Async Pays Off Only On Real I/O-Wait",
      ["It buys nothing for a CPU-bound loop — "
       "the win is proportional to how much waiting there actually is to overlap."],
      closing_q="Where has async actually cut your agent's latency?")

print("done: 30")
