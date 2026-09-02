--- LINKEDIN ---
MCP answers "how does an agent use its own tools" — that's vertical, agent to its own capabilities. Three more protocols cover what MCP doesn't touch, and each has its own spec rather than one trying to do everything.

A2A answers "how does one opaque agent delegate work to another, independently-built agent?" — horizontal, across an organizational boundary. AG-UI answers "what does the user see while an agent works for three minutes instead of returning instantly?" — a two-way event stream instead of request/response. AP2 answers "what evidence proves the user actually authorized this agent-performed purchase?" — signed, verifiable mandates instead of trusting a chat transcript after the fact.

AP2's answer is three mandates covering three different moments, signed by different parties. Intent (open, user-signed) sets constraints before a cart exists — allowed merchants, an amount ceiling. Cart (closed, agent-signed) locks in one exact purchase once it's known. Payment (agent-signed) ties the actual charge to the cart mandate at settlement.

A deterministic verifier — no model anywhere in this path — checks signatures, expiry, that the total equals the sum of line items, that the merchant is allow-listed, that the mandate pair hasn't already been consumed. The model may explain a choice. It may never raise the cap, alter a signed checkout, or wave through a replay.

Why the Trusted Surface — the thing that shows the user what they're authorizing — must be non-agentic: if it were itself an agent, the component proving informed consent would be the same untrusted actor the mandate system exists to constrain.

The production guidance worth internalizing regardless of which of these three you touch: adopt the protocol, don't marry it. Protocol-specific code belongs at the integration boundary, never inside domain logic, so swapping or dropping a young standard costs one adapter, not a rewrite.

If your agent handles money, can you prove authorization cryptographically, or only reconstruct it from logs after a dispute?

#AppliedAI #MCP #AIEngineering #LLM

--- INSTAGRAM ---
MCP is vertical. A2A is horizontal. 🔀

A2A: agent delegates to another agent. AG-UI: user watches and steers a long-running agent. AP2: signed mandates prove a purchase was actually authorized.

Three mandates, three signers: Intent (user), Cart (agent), Payment (agent) — a deterministic verifier checks all three, never a model.

Full breakdown in the carousel.

#AppliedAI #MCP #AIEngineering #LLM #GenAI

--- VISUAL FORMAT ---
carousel — 6 slides
1. Title — "MCP Is Vertical. A2A Is Horizontal."
2. Three protocols, three questions
3. AP2's three mandates — three moments, three different signers
4. The deterministic verifier — no model anywhere in this path
5. Why a trusted surface must be non-agentic
6. Takeaway — adopt the protocol, don't marry it (closing question)
