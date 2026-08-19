# Day 3 · Session 1 — Agent Architectures & LangGraph Fundamentals

Source: `labs/Day3 Session 1 - LangGraph and Agent Patterns.ipynb`

Two labs. **Lab A** (patterns, decision framework) + **Lab B** (checkpointed workflow, tied to **Milestone 5**). Core thesis: don't deploy an agent where a workflow would do — non-determinism, cost, and untestability are a price you pay only for irreducible uncertainty.

Model handle: `ChatLiteLLM(model=LLM_MODEL, temperature=0)`, `LLM_MODEL="gemini/gemini-3.1-flash-lite"`. A one-token probe call (`_probe_model()`) checks the key actually works (not just present) and sets `LLM_ENABLED`; every model call goes through `ask(system, user, model=None)` which returns `None` on failure so callers can write `ask(...) or <fallback>` — every cell/self-check still runs and passes with no key.

## Lab A — Agentic Patterns

### A1 — The autonomy spectrum
```
DESIGN TIME ──────────────────────────────────► RUN TIME
[1] single call  [2] prompt chain  [3] router  [4] tool-agent  [5] multi-agent
```
Per Anthropic's terminology: 1-3 are **workflows** (predefined code paths, LLM fills content/picks a branch); 4-5 are **agents** (LLM dynamically directs its own process). **Rule: push autonomy to the model only where the space of valid action sequences is too large/data-dependent to enumerate — enumerate everywhere else.**

### A2 — One minimal graph per pattern (each run against a real model + visualized via `show_graph`)
1. **Single LLM call** — email urgency classification. `START → classify → END`, no branching. Squeeze free-text model output back into a typed vocabulary at the boundary, with a deterministic fallback for out-of-vocab replies.
2. **Prompt chain** — invoice `extract → validate → post`. Human wrote the step order; model only fills fuzzy steps. Only `extract` uses the model (`chat_model.with_structured_output(PydanticModel)` — returns a validated object instead of prose to regex); `validate`/`post` are plain code — **paying a model for a rule or an arithmetic check buys only variance.**
3. **Router** — IT ticket triage into one of N enumerated categories. Model makes exactly **one** run-time choice; the routing function `route(state) -> str` is a pure function of state, unit-testable without a graph or model call. `add_conditional_edges(node, route_fn, {return_val: node_name, ...})` — a mismatch between what the router returns and the map's keys is the most common wiring bug, and it raises at **run time**, not compile time.
4. **Single tool-calling agent** — supplier risk research. Model decides tool + when to stop; the graph is a loop. New pieces: `@tool` (docstring = the prompt the model reads), `.bind_tools([...])`, `Annotated[list, add_messages]` (conversation reducer — nodes append, don't overwrite). **`MAX_TOOL_STEPS` cap is mandatory** — an uncapped agent loop is an open invoice.
5. **Multi-agent** — parallel legal/finance/compliance specialists fan out from `START`, fan in to a `merge` node. State field `reads: Annotated[list, add]` — without the reducer, concurrent writes in one superstep raise `InvalidUpdateError` (proven in B1), not a silent overwrite.

### A3 — The four named agentic patterns (all specializations of pattern 5, or pattern 4 for ReAct)
| Topology | Shape | Use when |
|---|---|---|
| Map-reduce | fan out → merge | independent subtasks joined |
| Verification | generate → verify → repair | correctness is checkable **by code** — prefer this whenever it applies |
| Critic-revision | generator ↔ critic loop | quality improves with rounds, "good enough" is judged not computed |
| Supervisor | router agent delegates repeatedly | which specialist needed depends on input, order unknowable |
| Debate | N agents argue → judge | correctness contested, no checker exists — expensive, rarely first choice |

- **ReAct** — built with LangGraph's prebuilts: `from langgraph.prebuilt import ToolNode, tools_condition`. `tools_condition` alone can loop forever against a stubborn model — AND it with a step cap (`REACT_STEP_CAP`). Scenario: on-call SRE diagnosing an alert (next lookup depends on last finding — the irreducible ambiguity that justifies an agent over a workflow).
- **Planner-Executor** — one call produces the *whole* plan up front (parsed into a typed `list[str]` at that boundary); `executor` pops and executes one step per visit (so each step gets its own checkpoint/resume point, and one node visit = one step, not the whole plan). Trap: a stale plan if step 2 invalidates step 3 — production fix is **replanning** (commented-out edge back to `planner`, costs one call/step).
- **Reflection** — `generate → critique → revise`, looped, capped at `MAX_REFLECT_ROUNDS`. **The critic shares the generator's blind spots (same model/training) — self-critique catches sloppiness, not ignorance.** Rule: if a deterministic checker exists, use *that* as critic (this is exactly what Lab B's `check_document()` does) and keep the model only for repair; Reflection-with-model-critic is the fallback when no such oracle exists. Two exit conditions needed: critic says PASS, OR round cap hit (without the cap, a fastidious critic bills forever). Critic sees only the RULES + draft, not the generator's reasoning — independence is the whole value of that node.
- **Supervisor-Worker** — a router that runs in a loop (vs. Pattern 3's router, which chooses once). Costs: one extra model call per hop, and a lossy boundary at every handoff (workers see a summary, not full context). Two failure modes designed against: infinite worker-picking (fix: `MAX_HOPS` cap) and hallucinated worker name (fix: validate against roster before it reaches the edge, fall back to a deterministic order). Star topology: every worker reports back to the supervisor node.

### A4 — Decision tree
Q1 (the important one): can *you* enumerate the paths now? If yes, workflow — cheaper, testable, reproducible. Q2 defaults to NO for multi-agent: a second agent adds a lossy re-serialization boundary; split only for a reason you can name (distinct expertise, parallel speed-up, generator/critic split). Six-problem worksheet with solutions (redaction→single call; claim routing→router; on-call diagnosis→ReAct; config-gen-and-repair→Verification multi-agent; due-diligence pack→map-reduce multi-agent; bank "ask anything"→Supervisor-Worker).

## Lab B — Document Approval Workflow (Milestone 5)

Target: `draft → checks → conditional route → [revise loop] → human_approval interrupt → finalize`, checkpointed to survive a **real kernel restart**. Deterministic everywhere except `revise`'s optional LLM variant (rewriting prose is the one genuinely fuzzy step; everything that *decides* stays deterministic and testable).

### B1 — State: control vs. audit fields
Two non-obvious rules: (1) a node returns a **partial** update (`{"issues": [...]}` only touches that key); (2) default merge is **overwrite** — `Annotated[list, add]` (or `add_messages`, or `operator.or_` for dicts) registers a reducer that accumulates instead.

**The design trap**: don't give `issues` (a **control** field the router reads) a reducer — it would never become empty after the first failure, looping forever. Keep a *separate* `issue_log: Annotated[list[str], add]` (an **audit** field) to preserve full history. General principle: **separate facts (control) from history (audit)**. Two nodes writing the same un-reduced key in one superstep raises `InvalidUpdateError` — the framework refusing to silently pick a winner, not a bug.

### B2 — Nodes are plain functions
`state -> partial update`, no base class/decorator — callable directly with a dict, so every node unit-tests without building a graph. `check_document(draft) -> list[str]` is a pure deterministic policy check (required sections, banned terms, word limit) — no model, because a rule expressible deterministically shouldn't cost model variance.

**The one LLM node**: `llm_revise_node` — model *produces* a new draft; `check_document()` (the same pure function the router reads) still *decides* whether it passed. **"Let the model produce, let deterministic code decide"** is what makes a fuzzy step safe inside a trusted workflow.

### B3 — Wiring: decide in a node, route in an edge
Conditional edge = pure function of state, **no model call inside**; the decision itself is written to state upstream, by a node. `LLM output → state field (typed) → deterministic router (unit-testable)`. `route_after_checks`: issues + `revision_count < MAX_REVISIONS` → `"revise"`, else `"approval"` (deliberately: after max revisions, escalate to a human rather than loop forever). Debugging habit: `graph.stream(seed, stream_mode="updates")` shows what each node wrote; `stream_mode="values"` shows full state after each superstep — `TypedDict` isn't runtime-validated, so a misspelled key silently creates a dead channel.

### B4 — Loops terminate because you made them
Framework gives a **recursion limit** as a backstop (a crash, not a design). Need two layers: a **guard in state** (`revision_count < MAX_REVISIONS`, the intentional exit → escalate) plus the recursion limit as the safety net. Removing the guard demonstrates `GraphRecursionError`.

### B5 — Persistence vocabulary
| Term | Meaning |
|---|---|
| Checkpointer | pluggable saver, snapshots state after every superstep, wired at `compile()` |
| Thread | one run, identified by `thread_id` in config |
| Checkpoint | one snapshot within a thread |
| Superstep | one execution tick |

Analogy: checkpointer = git for execution; `thread_id` = branch; `get_state_history()` = `git log`. `InMemorySaver` — dies with the kernel. `SqliteSaver` — file-backed, survives restarts (needed for B7).

### B6 — Human interrupt
`interrupt(payload)` (dynamic, inside a node, JSON-serializable payload) vs. static `interrupt_before=["node"]` breakpoints (debugging only, no payload). Three preconditions: checkpointer wired **before** the pause, a `thread_id` in config, JSON-serializable payload. Caller resumes with `Command(resume=value)` — that value becomes `interrupt()`'s return value inside the node. Interrupt on: irreversible/high-blast-radius/regulated actions, plan approval before expensive execution. Don't interrupt on every model call — trains reviewers to rubber-stamp. **`interrupt()` gives no authorization** — who approved and under what authority must be written into state/audit log yourself. Three response shapes all handled by the same primitive: approve (`{"action": "approved", "note": ...}`), reject, edit-then-approve (`edited_draft` replaces `draft` mid-run).

### B7 — The milestone: surviving a real kernel restart
`SqliteSaver(conn); saver.setup()` — one-line swap from `InMemorySaver`, "durability is a deployment concern, not a design one." **A checkpointer persists STATE, never CODE** — after restart, node functions/graph wiring must be rebuilt (in prod: your repo importing at startup) before you can resume; nothing about the *state* is lost, it's in the `.sqlite` file. Production note: checkpoint files are a deserialization surface — `LANGGRAPH_STRICT_MSGPACK=true` or an explicit allow-list restricts what gets reconstructed on resume; treat the checkpoint store like a database (backed up, access-controlled).

### B8 — The trap that reaches production
**On resume, the node re-runs from the top** — LangGraph doesn't restore a call stack, it replays the node until `interrupt()` returns the resume value. **Any side effect placed before `interrupt()` in the same node executes twice** (email sent twice, payment charged twice). Two rules: (1) a node containing `interrupt()` should do nothing before it except read state; (2) every irreversible action belongs in its own node, downstream of the pause — why `finalize` is separate from `human_approval`. Also: call `interrupt()` at most once per node invocation.

## Pitfall table (from the notebook, worth keeping)
| Symptom | Cause | Fix |
|---|---|---|
| `InvalidUpdateError` on a key | two nodes wrote it, no reducer | `Annotated[list, add]`, or single-owner |
| Field mysteriously empty | node returned whole state or misspelled key (TypedDict unvalidated) | print every node's return while developing |
| "No checkpointer" on interrupt | not wired at `compile()` | wire before the pause |
| Resume starts fresh | wrong/missing `thread_id` | reuse exact config dict |
| Resume fails after restart | `InMemorySaver` | `SqliteSaver`/Postgres |
| Something happened twice | side effect before `interrupt()` | move to downstream node |
| Old thread won't resume | state schema changed after checkpoints written | new `thread_id`, or freeze schema early |
| Graph never terminates | unguarded loop / accumulating control field | state guard + recursion limit; split control/audit |
| Agent loops on same tool forever | no step cap | cap tool steps in the conditional edge |

## Four sentences to carry forward
1. Autonomy is a cost paid for irreducible uncertainty, not a feature bought for its own sake.
2. Decide in a node, route in an edge.
3. Let the model produce; let deterministic code decide.
4. The irreversible step lives in its own node, downstream of every pause.

**Capstone tie-in:** Milestone 5 — "orchestrated LangGraph workflow with checkpointing." The rebuilt post-restart graph is a valid skeleton: swap the document policy for the domain's checks, swap `SqliteSaver` for Postgres in deployment, keep the human gate exactly where it is.
