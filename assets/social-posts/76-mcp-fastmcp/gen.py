import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 7, "Concept", "MCP Turns M×N Integrations Into M+N",
      ["Before MCP, giving an agent access to an internal system meant a custom integration per client, per framework, per vendor. MCP standardizes the plumbing — not the quality of any tool."])

slide(p("slide-02.png"), 2, 7, "Four Primitives", "Only One Puts The Model In The Loop",
      ["**Tool**: the model decides to invoke it.",
       "**Resource**: the application fetches it — no model decision.",
       "**Prompt**: the user picks it.",
       "**Sampling**: the server asks the client for a completion — inverted from the usual direction."])

slide(p("slide-03.png"), 3, 7, "Sample Code", "Sandbox First, Feature Second",
      ["No delete tool, no arbitrary-path write tool exists in this server's surface at all — the strongest guardrail is a capability that was never exposed."],
      code="def _safe_path(relative, root):\n    candidate = (root / relative).resolve()\n    if not candidate.is_relative_to(root):\n        raise ValueError(\"path escapes project root\")\n    if candidate.is_symlink():\n        raise ValueError(\"symlinks are refused, even inside the sandbox\")\n    return candidate")

slide(p("slide-04.png"), 4, 7, "The Silent Killer", "Never print() To stdout In A stdio Server",
      ["stdout IS the JSON-RPC channel — a stray print corrupts every message after it, and the client fails with a parse error that looks nothing like its actual cause. Log to stderr only."])

slide(p("slide-05.png"), 5, 7, "Another Gotcha", "PROJECT_ROOT Must Come From __file__, Not getcwd()",
      ["The client spawns the server as a subprocess, and that subprocess's working directory is not guaranteed to match the caller's."])

slide(p("slide-06.png"), 6, 7, "The Honest Tradeoff", "MCP Doesn't Make Anything Faster",
      ["Every call now crosses a process boundary plus JSON serialization — latency goes up. It buys decoupling, not speed."])

slide(p("slide-07.png"), 7, 7, "Takeaway", "A Server-Side Tool Error Doesn't Crash The Client",
      ["It comes back as a normal result flagged as an error, which the model can read and try something else with — treating it like a fatal exception misunderstands the protocol."],
      closing_q="Does your MCP server expose any capability it didn't strictly need to?")

print("done: 76")
