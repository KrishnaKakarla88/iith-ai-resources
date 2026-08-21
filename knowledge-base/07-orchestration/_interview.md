# 07-orchestration — interview fire round

### agent-topologies

- **Q: When does splitting one agent into a multi-agent team actually pay off?**
  A: When there's a nameable reason — distinct expertise that must not share context (a critic that shouldn't see the generator's reasoning), genuinely independent parallelizable sub-tasks, or a generator/critic split — not as a default "more advanced" upgrade.
- **Q: Why is a hierarchical/supervisor topology the one that needs real agent autonomy, while sequential and parallel usually don't?**
  A: In sequential and parallel shapes the designer already knows the path (who runs, in what order); a supervisor topology exists precisely because *which* specialist runs next depends on data the designer can't enumerate ahead of time.

### graph-engineering-mindset

- **Q: What can a graph do that a bare `while` loop structurally cannot?**
  A: Be inspected mid-run by name (named nodes vs. one opaque transcript), be paused and resumed without losing progress (checkpointed state vs. RAM), and have its stopping condition enforced by code rather than hoped for from the model.
- **Q: "Decide in a node, route in an edge" — why does that split matter?**
  A: It keeps every conditional edge a pure function of state with no model call inside it, which makes routing logic unit-testable without a graph, a model, or a token, and makes the decision that produced a given route traceable to one specific node.

### langchain-vs-langgraph

- **Q: If LangChain's `create_agent` already runs on LangGraph internally, why would you ever drop down to raw LangGraph?**
  A: When you need control `create_agent` doesn't expose — custom state fields beyond messages, non-standard conditional routing, multiple cooperating agents with their own read/write scopes, or checkpointing/HITL wired at points a pre-built agent loop doesn't pause at.
- **Q: What's the single question that tells you "chain" vs "graph" fastest?**
  A: Would every run of this task visit the same steps, in the same order, to completion? If yes, a chain is enough and a graph's branching/checkpointing machinery goes unexercised.

### langchain-runnables-lcel

- **Q: What does composing with `|` actually buy you over calling three functions in sequence?**
  A: Every step already implements the same `Runnable` interface, so the resulting chain gets `invoke`/`batch`/`stream` (and their async forms) uniformly for free — you don't write separate streaming logic for a 3-step vs. a 7-step chain.
- **Q: When should you stop composing with LCEL and reach for LangGraph instead?**
  A: The moment the workflow needs a loop that can go backward (not just forward through fixed steps), a pause for human input, or state that must survive a process crash — none of which a `RunnableSequence` models.

### langchain-chains-vs-agents

- **Q: You have a task that always does "classify, then look up a policy, then draft a reply." Chain or agent?**
  A: Chain — the order is fixed and enumerable; wrap it in `create_agent` only if you actually need the model to skip/reorder/repeat those steps based on the ticket content, which this description doesn't require.
- **Q: Why is "let the model produce, let deterministic code decide" relevant to agents specifically, and not just chains?**
  A: An agent's tool-call arguments come from the model and can't be blindly trusted — identity fields, computed amounts, and policy-critical values need to be validated or force-overwritten in code after the model chooses to call the tool, not assumed correct because the model said so.

### langchain-tool-integration

- **Q: Why does a vague tool docstring fail silently instead of raising an error?**
  A: The docstring only shapes what the model is shown to decide whether/how to call the tool — there's no validation step checking "is this description good enough," so a bad one just produces wrong or missing tool calls with nothing in the stack trace pointing back at the docstring.
- **Q: What's the concrete difference in what a `@tool` function returns locally vs. over MCP?**
  A: Locally it returns whatever Python value the function returns; over MCP it arrives wrapped as a list of content blocks (e.g. `[{"type": "text", "text": "<json>"}]`) that has to be unwrapped/parsed before use — code that assumes the local shape breaks silently against the MCP shape.

### langgraph-state

- **Q: Why does a node return a partial update instead of the whole state?**
  A: So the engine can apply a per-key reducer instead of a blind overwrite, and so two nodes touching different keys in the same superstep don't stomp on each other.
- **Q: What happens if two nodes write the same key in the same superstep and it has no reducer?**
  A: `InvalidUpdateError` — the engine refuses to silently pick a winner between two conflicting writes.

### langgraph-nodes

- **Q: Why is it significant that a LangGraph node has no base class or decorator?**
  A: It stays a plain function, callable with a hand-built state dict in a unit test — you can verify node logic without building a graph, wiring a checkpointer, or making a model call.
- **Q: Why keep policy/arithmetic checks out of the LLM node?**
  A: A rule expressible deterministically shouldn't cost model variance — "let the model produce, let deterministic code decide" keeps the fuzzy step (drafting) separate from the trustworthy step (deciding pass/fail).

### langgraph-edges

- **Q: When is a static edge the right choice over a conditional edge?**
  A: When every run visits the same steps in the same order regardless of state — no branch is ever actually taken, so a conditional edge would just be unused machinery.
- **Q: What happens if a node has no outgoing edge at all?**
  A: That path never reaches `END` — the run either hangs on that branch or (for the graph as a whole) errors, depending on whether other branches complete; every node needs a way forward, explicit or via `END`.

### langgraph-conditional-edges

- **Q: Why must the routing function itself never call a model?**
  A: So it stays a pure, unit-testable function of state — "decide in a node, route in an edge" keeps the one non-deterministic step isolated to a node, where its output gets validated and written to state before any routing happens.
- **Q: What's the most common conditional-edge bug, and when does it surface?**
  A: A routing function returning a value that isn't a key in the `path_map` — it raises at run time (when that specific path is actually taken), not at graph-compile time, so it can hide until a rare state combination triggers it.

### langgraph-graph-patterns

- **Q: What's the fastest way to decide which of the five shapes a new problem needs?**
  A: Ask whether you can enumerate the valid paths *right now*. If yes, it's shapes 1-3 (a workflow); if the next action genuinely depends on data you don't have until run time, it's shape 4 or 5 (an agent).
- **Q: Why does shape 5 (multi-agent fan-out) need a reducer that shape 2 (prompt chain) doesn't?**
  A: In shape 2, exactly one node writes to any given key at a time — overwrite is fine. In shape 5, multiple nodes write concurrently in the same superstep; without a reducer, that's an `InvalidUpdateError`, not a silent pick-one.

### langgraph-agentic-patterns

- **Q: Why does Reflection specifically warn that "the critic shares the generator's blind spots"?**
  A: Both are the same model with the same training, so a model-based critic reliably catches sloppiness (a missed step, a shallow answer) but not ignorance (a fact the model was never right about to begin with) — a deterministic checker doesn't share that blind spot.
- **Q: What are the two costs of Supervisor-Worker that a single agent doesn't pay?**
  A: One extra model call per hop for the supervisor's own routing decision, and a lossy re-serialization boundary at every handoff — a worker only sees a summary of state, not the supervisor's full context.
- **Q: Why validate the supervisor's chosen worker against the roster before the conditional edge, rather than letting the edge's path_map mismatch fail naturally?**
  A: An unmapped return value from a routing function is a run-time crash (per [[langgraph-conditional-edges]]), not a graceful fallback — validating upstream lets you substitute a deterministic default worker instead of crashing the run on a hallucinated name.

### langgraph-checkpointing-hitl

- **Q: Why must the checkpointer be wired before the interrupt point, and not the other way round?**
  A: `interrupt()` needs somewhere to persist the paused state to before it can safely stop execution and wait — without a checkpointer already wired at `.compile()`, there's nothing to resume *from*, so wiring it after the interrupt point silently fails to actually pause anything durably.
- **Q: What's the difference between `interrupt_before=["node"]` and calling `interrupt()` inside a node?**
  A: `interrupt_before` is a static, payload-less debugging breakpoint set at compile time; `interrupt()` is called dynamically from inside a node's own logic, carries an arbitrary JSON payload, and is the mechanism used for real approval/edit workflows.
- **Q: Does `interrupt()` record who approved the paused step?**
  A: No — it only pauses and resumes; recording who approved and under what authority has to be written into state/an audit log by your own code.

### idempotency-and-side-effects

- **Q: Why does resuming a paused LangGraph node re-execute code that already ran before the original `interrupt()` call?**
  A: LangGraph doesn't restore a call stack — it replays the node function from the top until `interrupt()` returns the resume value, since a snapshot only captures state between supersteps, not an in-flight Python call frame.
- **Q: Why is `uuid5` preferred over `uuid4` for a re-ingestable or re-runnable write?**
  A: `uuid5` derives the ID from stable inputs, so re-running the same logic produces the same ID and an upsert overwrites in place; `uuid4` is random, so a re-run produces a new ID every time and silently duplicates the row.
- **Q: Where should an irreversible action never live in a checkpointed graph?**
  A: In the same node as the `interrupt()` call that precedes it, or anywhere before an `interrupt()` call in that node — either place means it re-fires on every resume.

## Harder / real-interview-style

Grounded in 2026 web-researched LangGraph/orchestration interview material (search terms: "LangGraph interview questions multi-agent orchestration 2026", cross-referenced against [interviewcoder.co's LangGraph interview guide](https://www.interviewcoder.co/blog/langgraph-interview-questions) and general "supervisor vs network vs hierarchical" multi-agent topology coverage), plus this stage's own pages — [[agent-topologies]], [[graph-engineering-mindset]], [[langchain-vs-langgraph]], the `langchain/` and `langgraph/` subfolder pages, and [[idempotency-and-side-effects]]. This repo pins `langgraph>=1.2.11` (post-`interrupt()`/`Command(resume=)`, pre-`interrupt_before` era) — answers assume that API, not the pre-1.0 shape older blog posts describe.

### State, reducers, and concurrency

- **Q: Two parallel branches in your graph both write to the same state key in one superstep. In dev with a single worker this never surfaced; in production with concurrent load it crashes with `InvalidUpdateError`. Why did dev hide this, and how do you actually fix it?**
  A: Dev likely never actually exercised both branches writing in the *same* superstep — maybe the timing or test data happened to serialize them, or the parallel paths simply weren't both triggered in the cases tested. The engine's behavior is deterministic and correct: without a reducer on that key, it refuses to silently pick a winner between two concurrent writes, exactly per [[langgraph-state]]. The fix isn't error-handling around the crash — it's giving that key a reducer (e.g. `operator.add` for lists, or a custom merge function) that defines how two concurrent partial updates to it should combine, which has to be decided at design time, not discovered by a production crash.

- **Q: A node needs to both update shared state and log to an external system. Where does the "let the model produce, let deterministic code decide" principle apply here, and what goes wrong if you skip it?**
  A: Any policy-critical value the model produces — a computed refund amount, a chosen tool argument, an identity field — should be validated or force-overwritten by deterministic code in the node after the model call, never trusted as-is just because the model called the tool. Skipping this means a model-hallucinated argument (a wrong customer ID, an out-of-policy discount) flows straight into state and potentially into an external side effect, with nothing in the graph structure itself catching it — the graph enforces *order and routing*, not *correctness of values*, which stays the node's job.

### Checkpointing, HITL, and resume semantics

- **Q: You add a checkpointer and an `interrupt()` for human approval before charging a customer's card. In production, a resumed run charges the card twice. What's the most likely root cause, and what's the fix?**
  A: LangGraph resume doesn't restore an in-flight call stack — it replays the node function from the top until `interrupt()` returns the resume value, so any code in that node *before* the `interrupt()` call (including the charge itself, if it's placed before the pause) re-executes on every resume. The fix is placing the irreversible action strictly *after* the `interrupt()` returns, and additionally making the charge itself idempotent (a deterministic idempotency key derived from the order, not a fresh one per attempt) so even a legitimate retry from an upstream failure can't double-charge — this is the checkpointing correctness cost [[idempotency-and-side-effects]] names directly.

- **Q: Design a human-in-the-loop gate for a support agent that can (a) send a routine reply, (b) issue a refund under $50, (c) issue a refund over $50, and (d) close an account. Where do you put `interrupt()` calls, and what's the wrong instinct here?**
  A: The wrong instinct is gating uniformly — either interrupting every action (too slow, defeats the point of automation) or interrupting none (reckless, no human check on consequential actions). The right design gates by blast radius: routine replies and small refunds proceed autonomously, while the >$50 refund and the account closure are the ones that actually pause for approval, at the specific node where that decision is made — with `interrupt()` carrying enough payload (proposed amount, customer, reason) for a human to approve, edit, or reject in one look, not just approve/deny blindly.

- **Q: What's the practical difference between `interrupt_before=["node"]` (older API) and `interrupt()` called from inside a node, and why does this repo's `langgraph>=1.2.11` pin make one of them the primary mechanism?**
  A: `interrupt_before` is a static, payload-less breakpoint set at graph-compile time — closer to a debugger breakpoint than a production approval flow. `interrupt()` is called dynamically from inside a node's own logic, can carry an arbitrary JSON payload describing exactly what needs approval, and resumes via `Command(resume=value)` — this is the mechanism the current LangGraph 1.x API is built around for real approval/edit workflows, and it's what [[langgraph-checkpointing-hitl]] documents; a web tutorial written against a pre-1.0 LangGraph version describing `interrupt_before` as *the* HITL mechanism is describing a superseded pattern for this pinned version.

### Multi-agent topology decisions

- **Q: A team wants to split a single well-performing agent into a "swarm" of five specialist agents that can all call each other directly, because "multi-agent is the more advanced architecture." What's the actual failure risk, and what would you push back with?**
  A: A fully-connected network topology is usually the wrong default — it multiplies coordination surface area (any agent can hand off to any other) without a clear routing authority, which tends to produce unpredictable, hard-to-debug handoff chains and no single place to enforce invariants like "who's allowed to write this field." Per [[agent-topologies]], splitting into multiple agents should be justified by a nameable reason (context isolation, real parallelism, a generator/critic split), not treated as an upgrade; the push-back is that one well-scoped agent with a good tool list is cheaper, simpler, and easier to reason about until it's measurably failing at something a single agent structurally cannot do (context exhaustion, genuinely independent parallel sub-tasks).

- **Q: In a supervisor-worker system, message history keeps growing every hop, and after enough rounds routing quality visibly degrades. What's happening, and what's the standard fix?**
  A: The supervisor's context window is filling with the accumulated transcript of every worker round-trip, and per context-rot dynamics, decision quality degrades well before the hard token limit is hit — the supervisor is trying to route based on a context that's grown noisy and diluted. The standard fix is summarizing each worker's result before it returns to the supervisor rather than forwarding full worker transcripts verbatim — this trades some information loss and per-hop latency (summarization itself costs time) for keeping the supervisor's own context lean enough to route reliably; it's the same lossy-re-serialization-at-every-handoff cost [[langgraph-agentic-patterns]] already names as one of Supervisor-Worker's two structural costs.

- **Q: A conditional edge's routing function occasionally throws at runtime in production, on a state combination that never showed up in testing. What's the bug class, and how do you prevent it structurally rather than just adding a try/except?**
  A: This is the classic conditional-edge bug: the routing function returned a value that isn't a key in the graph's `path_map`, which only raises when that specific unmapped path is actually taken at run time, not at compile time — so it can hide indefinitely until a rare state combination triggers it. A try/except around the edge just converts a crash into a silent misroute; the structural fix is validating the routing function's output against the known roster of valid destinations *before* returning from it, substituting a deterministic default route on an unexpected value instead of letting it reach the graph engine unmapped — the same validate-before-conditional-edge discipline [[langgraph-agentic-patterns]] applies to a supervisor's worker choice.

### LangChain vs. LangGraph decision-making

- **Q: A stakeholder asks "why didn't you just use LangChain's `create_agent` instead of hand-building a LangGraph graph?" for a support-ticket system with a fact-checker, a writer, and an escalation path. How do you answer?**
  A: `create_agent` already runs on LangGraph internally and is the right default for a single agent with a tool list and no unusual control-flow needs — but this system needs custom state fields beyond a plain message list (draft, findings, fact_check, review), non-standard conditional routing between the writer and the fact-checker, and an approval pause before escalation — none of which a pre-built single-agent loop exposes hooks for. The answer isn't "LangGraph is more powerful so we used it" as a blanket preference; it's naming the specific control points (custom state, multi-agent read/write scoping, a checkpointed interrupt) that `create_agent` doesn't give you access to, per [[langchain-vs-langgraph]].

- **Q: What's the fastest diagnostic question to decide whether a new workflow needs a chain (or `create_agent`) versus a hand-built graph?**
  A: Ask whether every run of the task visits the same steps, in the same order, to completion, regardless of the input. If yes, a chain (or LCEL `RunnableSequence`) is enough, and any graph machinery — checkpointing, conditional routing, loops — would go entirely unexercised. The moment the workflow needs to loop backward (not just forward through fixed steps), pause for human input mid-run, or survive a process restart with state intact, that's the signal to move to LangGraph rather than trying to bolt loop-like behavior onto a linear chain.
