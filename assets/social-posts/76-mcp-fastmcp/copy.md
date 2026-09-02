--- LINKEDIN ---
Before MCP, giving an agent access to an internal system meant writing a custom integration for that one AI product — a different one for the next client, the next framework, the next vendor. MCP standardizes the plumbing (how a client discovers what a server offers, how it calls a tool, what a result looks like), not the quality of any given tool. M clients times N tools stops being M×N bespoke integrations and becomes M+N.

Four primitives, and only one puts the model in the loop: Tool (the model decides to invoke it), Resource (the application fetches it, no model decision), Prompt (the user picks it), Sampling (the server asks the client for a completion — inverted from the usual direction).

def _safe_path(relative, root):
    candidate = (root / relative).resolve()
    if not candidate.is_relative_to(root):
        raise ValueError("path escapes project root")
    if candidate.is_symlink():
        raise ValueError("symlinks are refused, even inside the sandbox")
    return candidate

Sandbox first, feature second — no delete tool, no arbitrary-path write tool exists in this server's surface at all. The strongest guardrail is a capability that was never exposed.

Two gotchas that bite immediately. Never print() to stdout in a stdio server — stdout IS the JSON-RPC channel, and a stray print corrupts every message after it, failing with a parse error that looks nothing like its actual cause. And PROJECT_ROOT must come from __file__, not os.getcwd() — the client spawns the server as a subprocess, and that subprocess's working directory isn't guaranteed to match the caller's.

The honest tradeoff: MCP doesn't make anything faster. Every call now crosses a process boundary plus JSON serialization — latency goes up. It buys decoupling, not speed.

One more thing worth internalizing: a server-side tool error doesn't crash the MCP client. It comes back as a normal result flagged as an error, which the model can read and try something else with.

Does your MCP server expose any capability it didn't strictly need to?

#AppliedAI #MCP #AIEngineering #LLM

--- INSTAGRAM ---
MCP turns M×N integrations into M+N. 🔌

Tool (model decides), Resource (app fetches), Prompt (user picks), Sampling (server asks client) — only one puts the model in the loop.

Never print() to stdout in a stdio server — that's the JSON-RPC channel.

No delete tool exists in this server's surface at all. Sandbox first, feature second.

Full mechanics in the carousel.

#AppliedAI #MCP #AIEngineering #LLM #GenAI

--- VISUAL FORMAT ---
carousel — 7 slides
1. Title — "MCP Turns M×N Integrations Into M+N"
2. Four primitives — only one puts the model in the loop
3. Sample code — sandbox first, feature second (code)
4. The silent killer — never print() to stdout in a stdio server
5. Another gotcha — PROJECT_ROOT must come from __file__
6. The honest tradeoff — MCP doesn't make anything faster
7. Takeaway — a server-side tool error doesn't crash the client (closing question)
