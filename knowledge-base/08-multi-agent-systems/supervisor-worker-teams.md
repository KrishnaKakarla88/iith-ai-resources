---
stage: "08-multi-agent-systems"
tools: [langgraph]
tags: [multi-agent, supervisor, write-scopes, dual-critic]
last_verified: 2026-08-20
verified_against: "langgraph 1.2.x (this repo's pin)"
---

# Supervisor-worker teams: write-scopes and dual critics

A supervisor-worker team only stays debuggable if every agent can see just enough state to do its job and write only the keys it owns — this page covers those two guardrails, not the graph mechanics that implement them.

## Prerequisites
- [[agent-topologies]]
- [[langgraph-state]]
- [[langgraph-agentic-patterns]]

## In plain English

The full supervisor-worker graph — how the supervisor node routes, how conditional edges read `next_agent`, how a star topology burns two supersteps per unit of work — lives in [[langgraph-agentic-patterns]]. This page assumes you already have that mental model and focuses on the two design decisions that keep a multi-specialist team from quietly corrupting its own state: who gets to *read* what (scoping), and who gets to *write* what (write-scopes), plus why a team of critics needs more than one of them.

A team with five specialists and one shared state dict looks harmless until a specialist reads a field it was never supposed to see, or writes over a field another specialist depends on. Read scoping and write scoping are the two mechanisms that turn "shared state" into "state each agent has a contract with."

## Core mechanics

**Write-scopes.** Each node is wrapped so it may only return updates to the state keys its role owns. A `@scoped(role)` decorator checks the dict a node returns against a per-role allowlist and raises `PermissionError` on violation, before the update ever reaches the graph's reducer. This has to cover async nodes too (`inspect.iscoroutinefunction`), since a scoped decorator that only wraps sync functions silently stops enforcing anything the moment a node becomes async.

**Read scoping** is the companion mechanism and the one that actually earns multi-agent's cost: each agent's `context_for(role, state)` hands it only its state slice, not the whole dict. This is not an optimization — it's what makes specialization real. A Fact-Checker that can read the Writer's brief can be talked into rationalizing a citation it would otherwise reject; a Fact-Checker that only ever sees `{draft, findings}` has no brief to be persuaded by.

**Why two critics, not one.** A single critic sharing full context with the producer tends to approve what it helped shape. Splitting the critic role in two — one **objective/deterministic** check and one **subjective/LLM-judge** check — closes that gap from two different directions:

| Critic | What it checks | How | Shares context with producer? |
|---|---|---|---|
| Fact-Checker | Are all cited claims actually supported by retrieved evidence? | Deterministic regex over citation tags (`\[(S\d+)\]`) against the findings set — the code check *is* the verdict, the model runs alongside only as a logged second opinion | No — sees only `{draft, findings}` |
| Reviewer | Is the draft structurally complete and does an independent judge approve it? | An objective floor (`_structure_notes()` — missing sections, length) runs first; approval requires that floor **and** LLM-judge agreement, AND not OR | No — but judges the finished draft, not the writer's intent |

The AND (not OR) between the objective floor and the judge's opinion matters: an LLM judge alone can be argued around, and a structural check alone can't catch a plausible-sounding fabrication. Requiring both closes each check's individual blind spot.

**Write-scopes need an escape hatch, deliberately.** `fact_check` and `review` are control fields, not accumulating logs — they deliberately have **no** reducer (unlike `findings`/`log`, which use `Annotated[list, add]`). That means the Writer must be allowed to write `{}` into both on every revision. If a rewrite couldn't clear prior verification/approval, an approved-then-edited draft could still ship as "approved" — a control field a team can't reset is a loop it can't correctly exit.

## Sample code

Lab-sourced (Day 3 · Session 2 — `labs/Day3 Session 2 - MultiAgent Teams and Agent Protocols.ipynb`), the write-scope decorator shape:

```python
from functools import wraps
import inspect

WRITE_SCOPES = {
    "fact_checker": {"fact_check", "log"},
    "reviewer": {"review", "log"},
    "writer": {"draft", "fact_check", "review", "log"},  # writer resets both critics
}

def scoped(role: str):
    def decorator(fn):
        @wraps(fn)
        async def async_wrapper(state):
            update = await fn(state)
            _check(role, update)
            return update

        @wraps(fn)
        def sync_wrapper(state):
            update = fn(state)
            _check(role, update)
            return update

        return async_wrapper if inspect.iscoroutinefunction(fn) else sync_wrapper
    return decorator

def _check(role: str, update: dict):
    illegal = set(update) - WRITE_SCOPES[role]
    if illegal:
        raise PermissionError(f"{role} wrote out-of-scope keys: {illegal}")
```

The Writer's entry in `WRITE_SCOPES` is the one that looks like a violation of "least privilege" until you remember the reducer point above — it's a deliberate, documented exception, not scope creep.

## Alternatives

Not applicable — this is a design pattern within LangGraph's state model, not a tool with competing implementations. See [[langgraph-agentic-patterns]] for how other frameworks (Deep Agents, Claude Agent SDK) express the same supervisor-worker shape with different amounts of built-in harness.

## How this shows up in the capstone

Milestone 6 (multi-agent supervisor team + MCP-backed tool swap) — the Triage/Policy-RAG/Order-Actions/Escalation-Reviewer team needs both a write-scope on every specialist and a real read boundary between the customer-facing writer and the compliance-facing reviewer, per [[capstone-milestone-map]].

## Interview fire round

- **Q: Why does read scoping matter more than write scoping for a Fact-Checker specifically?**
  A: Write scoping stops it from corrupting state it doesn't own, but read scoping is what stops it from being *persuaded* — a Fact-Checker that can see the brief can rationalize a citation the document's intent wants to be true; one that only sees `{draft, findings}` has nothing to be talked round by.
- **Q: Why do `fact_check` and `review` deliberately have no reducer, unlike `findings`?**
  A: They're control fields the Writer must be able to reset to `{}` on every revision — a rewrite voids prior verification, and a field that only ever accumulates can't represent "not yet re-approved."
- **Q: Why two critics instead of a single stronger one?**
  A: They close different blind spots — a deterministic check can't catch a plausible-sounding fabrication, an LLM judge alone can be argued around; requiring both (AND, not OR) is what makes an LLM-judge safe to put in a control path.

## Production gotchas & best practices

- Lab gotcha: a `@scoped` decorator that doesn't branch on `inspect.iscoroutinefunction` silently stops enforcing scope the moment a node is converted to `async` (needed once a specialist calls an MCP tool, see [[mcp-fastmcp]]) — write the async branch from the start, not after a specialist goes async.
- Lab gotcha, demonstrated directly (A5 in the lab): swapping in a `hallucinating_writer` that plants a fake citation on its first draft proves the read-scope boundary works — the Fact-Checker, never having seen the brief, can't be talked round, and the fabricated tag is absent from the shipped draft. The same team without that read boundary would not catch it.
- Production practice: treat the write-scope allowlist as reviewed code, not incidental — a role gaining an unreviewed extra key in its allowlist is a permission escalation that won't show up as a bug until two roles both write the same field on the same turn and one silently overwrites the other's judgment.
- Production practice: log every `PermissionError` a `@scoped` decorator raises rather than only using it to hard-fail — a specialist that keeps *attempting* an out-of-scope write is a signal its prompt or its parsing logic drifted, even though the guard caught it.

## Course vs. production

The lab enforces write-scopes with a single in-process decorator and an in-memory state dict — fine for a five-agent notebook run. In production, the same discipline extends across process/service boundaries (a specialist running as a separate deployment, or reached over [[mcp-fastmcp]] or [[agent-protocols-a2a-ap2]]) where a Python decorator can't see the write at all; the equivalent enforcement has to move to the state store or the API boundary itself — see [[auth-and-multi-tenancy]] for the same "re-verify, don't trust the caller" principle applied to identity rather than write-scope.

## Related
- **Builds on** — [[langgraph-agentic-patterns]], [[langgraph-state]]
- **Contrasts with** — [[agent-topologies]] (choreography and actor-critic as alternatives to the supervisor shape)
- **Feeds into** — [[mcp-fastmcp]], [[auth-and-multi-tenancy]]

## Sources

**Lab sources**
- `lab-summaries/Day3-Session2-MultiAgentProtocols.md` (§ "A1 — Team state & permissions", § "A2 — Five specialists", § "A5 — Why the critics exist, demonstrated")
- `labs/Day3 Session 2 - MultiAgent Teams and Agent Protocols.ipynb`

**Web sources**
- No additional web sources — this page covers a state-management pattern local to this repo's LangGraph implementation, not a tool with its own docs; see [[langgraph-agentic-patterns]] and [[langgraph-state]] for LangGraph's own state/reducer documentation citations.
