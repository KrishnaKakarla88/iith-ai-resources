# 08-multi-agent-systems — interview fire round

### supervisor-worker-teams

- **Q: Why does read scoping matter more than write scoping for a Fact-Checker specifically?**
  A: Write scoping stops it from corrupting state it doesn't own, but read scoping is what stops it from being *persuaded* — a Fact-Checker that can see the brief can rationalize a citation the document's intent wants to be true; one that only sees `{draft, findings}` has nothing to be talked round by.
- **Q: Why do `fact_check` and `review` deliberately have no reducer, unlike `findings`?**
  A: They're control fields the Writer must be able to reset to `{}` on every revision — a rewrite voids prior verification, and a field that only ever accumulates can't represent "not yet re-approved."
- **Q: Why two critics instead of a single stronger one?**
  A: They close different blind spots — a deterministic check can't catch a plausible-sounding fabrication, an LLM judge alone can be argued around; requiring both (AND, not OR) is what makes an LLM-judge safe to put in a control path.

### mcp-fastmcp

- **Q: What does MCP actually buy you if it doesn't make anything faster?**
  A: Not speed — every call now crosses a process boundary plus JSON serialization, so latency goes *up*. It buys decoupling: the knowledge base or tool stops being welded to one client/notebook/framework, and any MCP-compatible client can reach it unchanged.
- **Q: Why is the docstring part of the API contract, not documentation?**
  A: FastMCP turns the function's docstring and type hints into the JSON schema the model reads to decide whether and how to call the tool — a vague docstring doesn't raise an error, it just gets the tool called wrongly or never.
- **Q: When is MCP the wrong call for a given tool?**
  A: When only one client will ever call it and cross-framework reuse is worth nothing to you — then it's "an integration decision, not an upgrade," and a plain Python function is still right.

### agent-protocols-a2a-ap2

- **Q: MCP already lets a model call tools — why would you also need A2A?**
  A: MCP is vertical (an agent using its own tools); A2A is horizontal (one agent handing work to a different, independently-built agent it doesn't control the internals of). MCP answers "how can an agent use this capability," A2A answers "which capable agent should take this work."
- **Q: Why does AP2 need three separate mandates instead of one signature at checkout?**
  A: The three mandates cover three different moments and different signers — what was asked for (Intent, user-signed, before a cart exists), what was agreed to (Cart, agent-signed, once the exact purchase is known), and what was finally charged (Payment) — so a dispute can be resolved from three timestamped signatures instead of reconstructed from chat logs.
- **Q: Why must AP2's Trusted Surface be non-agentic?**
  A: It's the component that shows the user what they're authorizing and collects consent — if it were itself an agent, the thing proving informed consent would be the same untrusted actor the mandate system exists to constrain.

### auth-and-multi-tenancy

- **Q: Why is "the customer typed their order number in the chat" not enough to authorize a lookup?**
  A: Message text is attacker-controlled input, not proof of ownership — an LLM or a naive extractor that trusts it is trusting the same channel a malicious or mistaken user could type any order number into. Identity has to come from an authenticated session, resolved before the agent logic runs, not parsed out of the conversation.
- **Q: Why re-check authorization at the point of mutation if the user already passed a login check?**
  A: Login proves identity at the start of a session; it doesn't prove that a specific write, several tool calls later, is still scoped to that same customer and that specific resource. A session-start check and a mutation-time check answer different questions, and skipping the second is how a scoped conversation drifts into an unscoped write.
- **Q: Why mask a cross-tenant `PermissionError` instead of just returning it?**
  A: The raw error (or even a distinctive error vs. a generic 404) can leak that a resource exists and who owns it — an attacker probing order IDs learns something from the difference between "not found" and "not yours." A masked, generic denial gives nothing away.

## Harder / real-interview-style

Grounded in 2026 web-researched interview material on MCP/A2A/protocol layering and multi-agent handoff failures (search terms: "MCP Model Context Protocol interview questions multi-agent systems A2A protocol", "supervisor multi-agent architecture interview questions handoff context window failure"), cross-referenced against [Atlan's agent interoperability protocols guide](https://atlan.com/know/agent-interoperability-protocols/) and general 2026 supervisor-topology production writeups, plus this stage's own pages — [[supervisor-worker-teams]], [[mcp-fastmcp]], [[agent-protocols-a2a-ap2]], [[auth-and-multi-tenancy]]. This repo pins `fastmcp>=3.4.7` (the standalone `gofastmcp.com` package, not the MCP SDK's bundled v1 variant) and `langchain-mcp-adapters>=0.3.2` — answers assume that surface.

### Protocol layering: MCP vs. A2A vs. AP2

- **Q: A team already has MCP wired up for tool access and asks "why would we ever also need A2A? Doesn't MCP already let agents call things?"**
  A: MCP is vertical — it standardizes how *one* agent accesses its own tools and data sources, e.g. a support agent calling a Qdrant search tool over MCP. A2A is horizontal — it standardizes how one *independently built* agent hands work to another agent it doesn't control the internals of, with its own state, its own tools, possibly its own vendor. You need A2A specifically when the system has to delegate to an agent that isn't just "another tool call" — a specialist built and maintained by a different team or company, where the calling agent should treat it as a peer with its own reasoning, not a function it invokes. MCP answers "how does my agent use this capability"; A2A answers "which other, separately-built agent should take this work."

- **Q: Why does AP2 require three separately signed mandates (Intent, Cart, Payment) instead of one authorization at checkout, and where would you draw the line on what needs its own mandate versus not?**
  A: Each mandate captures a different moment with a different signer and a different piece of information available: Intent captures what was *asked for*, signed by the user before a specific cart even exists; Cart captures what was *agreed to*, signed once the exact purchase (items, price, agent) is known; Payment captures what was actually *charged*. Collapsing these into one signature loses the ability to resolve a dispute from timestamped evidence — "did the agent charge what the user actually agreed to, and did the user actually ask for this in the first place" become three separate, checkable facts instead of one blob you'd have to reconstruct from logs. The line for when a new mandate type is warranted is whenever a new party's authority or a new fact becomes knowable at a genuinely different point in time — not every step needs its own mandate, only the ones where the *information available to sign* actually changes.

- **Q: The AP2 spec insists the "Trusted Surface" — the thing that shows the user what they're authorizing and collects consent — must be non-agentic. Why is that non-negotiable rather than a nice-to-have?**
  A: If the consent-collecting surface were itself an LLM-driven agent, the very component meant to prove informed consent would be the same class of untrusted, potentially-manipulable actor the mandate system exists to constrain — an injected instruction or a hallucinated summary could misrepresent what the user is agreeing to, and there'd be no non-agentic ground truth to check it against. Keeping the Trusted Surface deterministic (a plain rendered UI, not an agent's paraphrase) is what makes the signed mandate meaningful evidence of *actual* user intent rather than an agent's account of it.

### Supervisor-worker production failures

- **Q: A supervisor-worker system works fine in testing with 2-3 hops, but in production, after many rounds of delegation, the supervisor starts routing to the wrong specialist or repeating work already done. What's the mechanism, and what's the standard mitigation?**
  A: Every worker round-trip adds to the supervisor's own message history; even before any hard token limit is hit, decision quality degrades as that accumulated context grows noisy and dilutes the signal the supervisor needs to route correctly (the same context-rot dynamics as [[context-rot-and-long-context-management]], applied to a supervisor's routing prompt specifically). The standard mitigation is summarizing each worker's result before it's folded back into the supervisor's context rather than forwarding full transcripts — this costs some information loss and per-hop latency, but keeps the supervisor's own context lean enough to route reliably over many hops, which raw forwarding cannot sustain indefinitely.

- **Q: A handoff between two independently-built agents loses the "why" behind a decision — the receiving agent redoes work the first agent already ruled out. Why does this happen even when the handoff includes a summary of the conclusion?**
  A: Natural-language handoff summaries tend to favor conclusions because conclusions read as the important part — but assumptions, rejected alternatives, and confidence levels look like mere supporting detail and get compressed out first, even though that "detail" is exactly what would stop the receiving agent from re-deriving (or re-rejecting) the same paths. The fix isn't a longer summary; it's structuring the handoff payload to explicitly carry rejected alternatives and the confidence/assumptions behind the conclusion as first-class fields, not prose the receiving agent has to infer intent from — the same "state carries facts, not vibes" discipline that [[supervisor-worker-teams]] applies to write-scoped fields like `findings` and `fact_check`.

- **Q: Why does write-scoping alone (a worker can only write to its assigned state keys) not fully prevent a Fact-Checker from being manipulated into approving a bad draft?**
  A: Write scoping stops a worker from *corrupting* state fields it doesn't own — it says nothing about whether the worker's own output is trustworthy. What actually protects a Fact-Checker from being persuaded is *read* scoping: a Fact-Checker that can see the full brief/context the Writer used can rationalize why a citation matches the brief's intent even when it doesn't; one that's only shown `{draft, findings}` has nothing but the claim and the evidence to reason from, and no larger narrative to be talked round by. This is why [[supervisor-worker-teams]] treats read scope as the security-relevant boundary for a critic role, not just write scope.

### MCP production tradeoffs

- **Q: If exposing a tool over MCP makes every call slower (a process boundary plus JSON serialization added to every invocation), why would you do it at all?**
  A: Because the value MCP buys isn't speed, it's decoupling — the underlying tool or knowledge base stops being welded to one client, one notebook, or one framework, and becomes reachable by any MCP-compatible client without rewriting the integration each time. That's a real tradeoff, not a free upgrade: for a tool only one client will ever call, where cross-framework reuse has zero value, MCP is the wrong call and a plain Python function call is still correct — the decision is about integration surface, not "MCP is strictly more advanced."

- **Q: An MCP tool's docstring is vague, and in production the model calls it with the wrong arguments about a third of the time — but nothing ever raises an exception pointing at the docstring. Why is this bug invisible in a stack trace?**
  A: FastMCP turns the function's docstring and type hints directly into the JSON schema the model reads to decide whether and how to call the tool — there's no validation step anywhere that checks "is this description good enough for a model to use correctly." A vague docstring doesn't error; it just silently produces wrong or missing tool calls, which look like a model reasoning failure rather than what they actually are — an API-contract problem in the docstring itself. This is why [[mcp-fastmcp]] and [[langchain-tool-integration]] both treat the docstring as part of the API contract, not documentation to clean up later.
