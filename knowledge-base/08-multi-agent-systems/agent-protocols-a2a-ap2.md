---
stage: "08-multi-agent-systems"
tools: [a2a, ap2, ag-ui]
tags: [protocols, a2a, ap2, ag-ui, appendix]
last_verified: 2026-08-20
verified_against: "A2A v1.0.1, AP2 v0.2 (per presentations/day3.md)"
---

# Agent protocols: A2A, AG-UI, and AP2

MCP standardizes agent→tool. Three more protocols cover the layers MCP doesn't touch: A2A for agent→agent delegation, AG-UI for agent→user interaction, and AP2 for proving an agent had authority to spend money — this page is marked optional/appendix, since the labs call this material illustrative rather than coursework.

## Prerequisites
- [[mcp-fastmcp]]
- [[agent-topologies]]

## In plain English

Once MCP answers "how does an agent use a tool," three more questions stay open, and each has its own protocol rather than one protocol trying to do everything:

- **A2A** answers "how does one opaque agent delegate work to another, independently-built agent?" — MCP is vertical (agent to its own tools), A2A is horizontal (agent to another agent, possibly built by a different team or vendor, across an organizational boundary).
- **AG-UI** answers "what does the user see and do while an agent works for three minutes instead of returning instantly?" — a two-way event stream instead of a single request/response.
- **AP2** answers "what evidence proves the user actually authorized this agent-performed purchase?" — signed, verifiable mandates instead of trusting a chat transcript after the fact.

None of these require each other. A system can use A2A without AP2 (delegating research to another agent, no money involved) or AP2 without A2A (one agent handling its own checkout). The course's example composes both: an agent uses A2A to get a quote from a vendor's agent, then AP2-style signed mandates decide whether that quote may actually be paid.

**2026 caveat**: this page's protocol-version and incident detail (A2A v1.0.1, AP2 v0.2, the specific mandate field names) come from `presentations/day3.md`, the only source in this repo covering these protocols in any depth — the labs treat this material as an illustrative appendix, not graded coursework. Where a version number or spec detail can't be independently confirmed against the live spec this session, it's flagged as such below rather than presented as freshly verified.

## Core mechanics

**A2A (Agent2Agent, v1.0.1 per course material)** — an HTTP-based flow for one agent to discover and delegate to another:

| Step | What happens |
|---|---|
| Discover | `GET /.well-known/agent-card.json` — fetches the remote agent's capabilities |
| Pick | Choose one entry from the card's `supportedInterfaces` |
| Authenticate | Resolve credentials from the card's `securitySchemes` |
| Send | `SendMessage` — the response contains exactly one of `result.task` or `result.message` |
| Track | If a `Task` came back, poll or stream it; `contextId` groups a whole conversation, `taskId` identifies one stateful unit of work — same `taskId` + `contextId` continues that Task, same `contextId` with no `taskId` starts a new Task inside the same conversation |

Agent Card "skills" are descriptions for a human/model to read, not RPC method names — the client always sends a `Message`, never calls a skill by ID directly.

**AG-UI (Agent-User Interaction Protocol)** — a transport-agnostic, two-way event protocol (per course material: runs over SSE, WebSockets, or webhooks) for the case where a final request/response model breaks down because the agent runs long and the user needs to watch, steer, and interrupt it. It carries messages and streamed partial results, shared application state (e.g., a live checklist the agent updates), interactive UI elements (choices, forms, rendered tool results), and human control signals (approve, edit, pause, retry, redirect) — without losing the session.

**AP2 (Agent Payments Protocol, v0.2 per course material)** — secures only the payment-authorization step of an agent-performed purchase; catalog browsing, checkout UI, and payment transport are explicitly out of scope. Five roles: Shopping Agent, Trusted Surface (must be non-agentic — the thing that actually shows the user what they're authorizing and collects consent), Merchant, Credential Provider, Merchant Payment Processor.

| Mandate | Signed when | Signed by | Covers |
|---|---|---|---|
| Intent (open) | Before a specific cart exists | User | Constraints: allowed merchants, amount ceiling, payee, instrument — lets the agent act later without the user watching |
| Cart (closed) | Once an exact cart exists | Agent (references the open mandate) | One exact purchase — items, price, merchant |
| Payment | At settlement | Agent | Ties the charge to the cart mandate; the card network sees "agent-initiated, user-authorized, tied to this cart" |

A **deterministic verifier** — no model in this path — checks signatures, expiry, that the `cnf` (key-binding) claim matches across mandates, that the closed cart's hash matches the merchant-signed checkout JWT, that the total equals the sum of line items, that the merchant is on an allow-list, that the payment amount is within the open mandate's `amount_range`, and that the mandate pair hasn't already been consumed (replay protection). Per course material, negative tests over this flow confirmed tampered totals, unapproved merchants, expired authority, mismatched checkout/payment binding, over-cap amounts, and replays are all rejected by the deterministic layer — never by asking the model to notice.

**Where all four protocols sit, as one stack** (per course material — MCP and A2A are now both under Linux Foundation governance, a maturity signal the course treats as meaningfully different from a single-vendor spec):

| Layer | Protocol | Direction |
|---|---|---|
| Tools/context | MCP | Agent → tool/resource |
| Delegation | A2A | Agent → another agent |
| Interaction | AG-UI | Agent → user/application |
| Authority to transact | AP2 | Agent → payment rails, provable after the fact |

## Sample code

No lab notebook implements A2A/AG-UI/AP2 — this is the one topic in this stage sourced primarily from `presentations/day3.md` rather than from a notebook. The course material's own caveat: its AP2 walkthrough uses no real network calls, no trust registries, no payment rails, and no full SD-JWT/KB-SD-JWT — a local ECDSA P-256 JWS wrapper stands in for the real cryptographic stack, with a documented checklist of what a production implementation would need to replace (real Agent Card fetch+cache, real transport/TLS/auth, real key enrollment for user/agent/merchant, a real Credential Provider, durable audit/replay state). Because no clean, versioned code sample exists in this repo for these three protocols, this page omits a Sample code block rather than inventing one — see the official spec sites below for real request/response examples.

## Alternatives

| Approach | Where it lives | Boring/simple alternative? |
|---|---|---|
| A2A (agent delegation) | Linux Foundation / Google, `a2a-protocol.org` | — |
| Bespoke internal REST API between two agent services | Plain Python/HTTP, no shared spec | **Yes** — fine inside one org where both agents are yours; loses the "any conforming agent reaches any conforming agent" property the moment a third party is involved |
| AG-UI (agent-user interaction) | CopilotKit-originated, now with LangGraph/CrewAI adapters, `ag-ui.com` | — |
| Hand-rolled SSE/WebSocket event stream + your own event schema | Plain Python | **Yes, the boring option** — works for one app/one agent framework, loses the "swap the agent framework without rewriting the frontend" property |
| AP2 (payment authorization mandates) | Google Cloud–originated, `ap2-protocol.org` | — |
| Store a signed audit log entry per action, reviewed after the fact | Plain application logging + a signing library | **Yes** — cheaper to build, but reconstructs authority from logs *after* a dispute rather than proving it cryptographically *before* the charge — the exact gap AP2's mandate-before-purchase model is built to close |

## How this shows up in the capstone

Milestone 6 (multi-agent supervisor team + MCP-backed tool swap) — this appendix material isn't built into the capstone's graded deliverable, but the protocol-layer framing (which layer a given cross-boundary problem sits on, before picking a protocol for it) is the same judgment call the capstone's MCP exposure decision required at a smaller scale; per [[capstone-milestone-map]], only [[mcp-fastmcp]] is a graded milestone concept here.

## Interview fire round

- **Q: MCP already lets a model call tools — why would you also need A2A?**
  A: MCP is vertical (an agent using its own tools); A2A is horizontal (one agent handing work to a different, independently-built agent it doesn't control the internals of). MCP answers "how can an agent use this capability," A2A answers "which capable agent should take this work."
- **Q: Why does AP2 need three separate mandates instead of one signature at checkout?**
  A: The three mandates cover three different moments and different signers — what was asked for (Intent, user-signed, before a cart exists), what was agreed to (Cart, agent-signed, once the exact purchase is known), and what was finally charged (Payment) — so a dispute can be resolved from three timestamped signatures instead of reconstructed from chat logs.
- **Q: Why must AP2's Trusted Surface be non-agentic?**
  A: It's the component that shows the user what they're authorizing and collects consent — if it were itself an agent, the thing proving informed consent would be the same untrusted actor the mandate system exists to constrain.

## Production gotchas & best practices

- Per course material (`presentations/day3.md`): "the model may find a report or explain a choice; it may never raise the cap, alter a signed checkout, or wave through a replay" — every AP2 authorization check is deterministic code, never a model judgment call, the same "model for judgement, code for fact" split covered in [[supervisor-worker-teams]]'s Fact-Checker design.
- Per course material: production readiness for any of these three protocols means replacing every fixture the course's demo used — real Agent Card fetch and caching (not a static file), real TLS/transport/auth (not stdio-equivalent trust), real key enrollment for every party, a real Credential Provider, and durable audit/replay-protection state (not an in-memory set).
- Per course material: "adopt the protocol, don't marry it" — protocol-specific code belongs at the integration boundary, never inside domain logic, so that swapping or dropping a young standard costs one adapter, not a rewrite. This matters more for A2A/AG-UI/AP2 than for MCP, since none of the three has MCP's level of ecosystem maturity yet (per course material, discovery across agents in particular is called out as still unsolved industry-wide, not just under-implemented here).

## Course vs. production

Everything on this page is course material with an explicit "as reported at time of writing" / simplified-fixture caveat, not lab code — there is no lab notebook to compare against. The gap here isn't lab-vs-production in the usual sense (a working simplified version vs. a hardened one); it's course walkthrough vs. a real deployment, and the course material itself names the checklist: real network calls, real trust registries, real payment rails, and full SD-JWT/KB-SD-JWT credentials in place of the local JWS stand-in.

## Related
- **Builds on** — [[mcp-fastmcp]]
- **Contrasts with** — [[mcp-fastmcp]] (vertical agent→tool vs. horizontal agent→agent)
- **Related to** — [[supervisor-worker-teams]] (same "model decides, code authorizes" split as AP2's deterministic verifier)

## Sources

**Lab sources**
- `lab-summaries/Day3-Session2-MultiAgentProtocols.md` (§ "Appendix — A2A and AP2 (illustrative, not coursework)") — the labs' own appendix, itself sourced from the same course material below, not a notebook implementation

**Web sources** (per course material, `presentations/day3.md` — 2026-dated protocol version numbers and mandate-flow specifics not independently re-verified this session)
- [Agent2Agent (A2A) protocol specification](https://a2a-protocol.org/) — agent-card discovery, task/message model, per course material
- [AG-UI — Agent-User Interaction Protocol](https://docs.ag-ui.com) — event-based two-way protocol, transport-agnostic, per course material
- [Google Cloud — Announcing the Agent Payments Protocol (AP2)](https://cloud.google.com/blog/products/ai-machine-learning/announcing-agents-to-payments-ap2-protocol) — September 2025, mandate model, per course material
- Prompt20, *AI Agent Protocols: MCP, A2A, ACP and the Interop Stack* — cited per course material (`presentations/day3.md`) as the course's own "map of the 2026 protocol layer," not independently re-verified this session
