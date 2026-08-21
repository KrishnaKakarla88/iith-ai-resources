---
stage: "07-orchestration"
tools: [langchain, langgraph]
tags: [orchestration, langchain, agents, chains]
last_verified: 2026-08-20
verified_against: "langgraph 1.2.x (this repo's pin); langchain create_agent per current docs.langchain.com"
---

# LangChain chains vs. agents

A chain runs a fixed sequence of steps you designed; an agent, in LangChain's current terminology, is `create_agent`'s pre-built tool-calling loop where the model decides which tool to call and when to stop — the same workflow-vs-autonomy line drawn again, one layer lower, inside LangChain's own vocabulary.

## Prerequisites
- [[langchain-runnables-lcel]]
- [[workflow-vs-agent-autonomy-spectrum]]

## In plain English

"Chain" and "agent" are not two rungs of a maturity ladder — they're two different control shapes, and the choice between them is the same one from [[workflow-vs-agent-autonomy-spectrum]] applied specifically inside LangChain's API surface. A chain (built with LCEL, see [[langchain-runnables-lcel]]) has a designer-fixed order of steps: `prompt | model | parser` always runs in that order, every time. An agent, in LangChain's current sense, wraps a *loop*: call the model, let it choose a tool from a bound set, run the tool, feed the result back, repeat until the model decides to stop (or a step cap is hit). The model is making a real run-time decision — which tool, how many times — that the designer didn't enumerate in advance.

This matters because "agent" gets used loosely in casual conversation to mean "the fancy version." Inside LangChain specifically it means something narrower and mechanical: a `create_agent` call is *always* running a loop with tool-choice inside it, on top of LangGraph. If your task's steps are the same every run and only the *content* at each step is fuzzy (e.g. "extract these fields from this text"), that's a chain wearing an LLM call, not an agent — reach for `with_structured_output` inside an LCEL step, not `create_agent`.

## Core mechanics

| Aspect | Chain | Agent (`create_agent`) |
|---|---|---|
| Step order | Fixed by the developer | Decided by the model, per turn, from the bound tool set |
| Stopping condition | Runs until the last step | Model decides "no more tools needed," or a step/iteration cap fires |
| Underlying primitive | `RunnableSequence` (LCEL) | A pre-built LangGraph loop (`create_agent` runs on LangGraph internally) |
| Testability | Each step is a pure function/`Runnable` — easy | The loop as a whole is data-dependent; individual tool functions are still unit-testable in isolation |
| When it's the right call | Every run needs the same steps, in the same order | The set/order of actions genuinely can't be enumerated ahead of time (data-dependent research, diagnosis, multi-step tool use) |

The critical production discipline that applies to *both*, per the lab's own repeated pattern: **let the model produce, let deterministic code decide.** Even inside an agent's tool-choice loop, whatever a tool call is allowed to actually do (which values, which mutations) should be validated/enforced in code — never trusted as-is from the model's arguments. See Production gotchas below.

## Sample code

Lab-sourced (`labs/Day3 Session 1 - LangGraph and Agent Patterns.ipynb`) — pattern 2 (prompt chain: fixed order, model fills only the fuzzy step) contrasted with pattern 4 (tool-calling agent: model decides tool + when to stop), both from the same lab:

```python
# CHAIN — fixed order, human wrote the step order
invoice = chat_model.with_structured_output(InvoiceSchema).invoke(raw_text)  # only fuzzy step
if not validate(invoice):          # plain code — no model
    raise ValueError("invalid invoice")
post(invoice)                      # plain code — no model

# AGENT — model decides which tool + when to stop, graph is a loop
@tool
def lookup_supplier_risk(supplier_id: str) -> dict:
    """Look up a supplier's current risk rating and recent flags."""
    ...

agent = create_agent(
    model="groq:llama-3.1-8b-instant",
    tools=[lookup_supplier_risk, lookup_contract_terms],
    system_prompt="Research supplier risk before recommending a decision.",
)
result = agent.invoke({"messages": [{"role": "user", "content": ticket_text}]})
```

The lab's own note on pattern 2 applies directly: "paying a model for a rule or an arithmetic check buys only variance" — `validate()` and `post()` stay plain code precisely because they're not fuzzy. `create_agent` usage above is adapted from current LangChain docs¹ (this repo's own notebooks build the equivalent loop directly on raw LangGraph with `@tool`/`.bind_tools()`, not via `create_agent` — see [[langchain-vs-langgraph]]).

## Alternatives

| Approach | Where it lives | Boring/simple alternative to LangChain's chain/agent split? |
|---|---|---|
| LCEL chain + `create_agent` | LangChain | — |
| Raw LangGraph (`StateGraph`, `ToolNode`, `tools_condition`) | Same vendor, lower-level | No — same tier, more control, more code to own; this repo's labs use this directly |
| LlamaIndex `FunctionAgent` / Workflows | LlamaIndex framework | No — same tier of tooling, different framework, data-centric bias |
| Plain Python: an `if/elif` for a chain, a hand-rolled `while` + `json.loads` tool-call parsing for an agent | No dependency | **Yes** — the boring option; loses the standardized tool schema generation, message-history management, and step-cap defaults `create_agent` provides |

## How this shows up in the capstone

Milestone 5: ShopSense's Order-Actions agent is a genuine agent in this sense (it must decide which order-mutation tool to call based on the ticket, and when it's done); the deterministic pieces around it — validating a refund amount, formatting a response — stay plain chained code, not additional agent autonomy, per "let the model produce, let deterministic code decide"; see [[capstone-milestone-map]].

## Interview fire round

- **Q: You have a task that always does "classify, then look up a policy, then draft a reply." Chain or agent?**
  A: Chain — the order is fixed and enumerable; wrap it in `create_agent` only if you actually need the model to skip/reorder/repeat those steps based on the ticket content, which this description doesn't require.
- **Q: Why is "let the model produce, let deterministic code decide" relevant to agents specifically, and not just chains?**
  A: An agent's tool-call arguments come from the model and can't be blindly trusted — identity fields, computed amounts, and policy-critical values need to be validated or force-overwritten in code after the model chooses to call the tool, not assumed correct because the model said so.

## Production gotchas & best practices

- Lab gotcha (`labs/production-notes.md`, "Tool Calling"): force-set authorization-critical fields (e.g. a customer identifier) server-side, unconditionally overwriting whatever the model's tool-call argument contained — never trust an LLM tool-call arg for identity, even inside a well-scoped agent.
- Lab gotcha (`labs/production-notes.md`, "Tool Calling"): enforce deterministic values in code, not just in the prompt — telling the model to "copy this computed number" isn't enough; force-overwrite the argument in code and log a warning on disagreement.
- Lab gotcha (`labs/production-notes.md`, "Tool Calling"): detect narrated-but-not-executed outcomes — a model can narrate "refund processed" in its final text without actually having called the tool; a regex/keyword check on outcome language, paired with re-injecting a system message forcing it back into the tool loop, catches this because the prompt instruction alone isn't reliable.
- Production practice: per current LangChain docs¹, the older `AgentExecutor`/`create_tool_calling_agent` pattern is maintenance-only with a stated migration deadline — new agent code should target `create_agent` (or raw LangGraph, if more control is needed), not `AgentExecutor`.

## Course vs. production

The lab (`labs/Day3 Session 1 - LangGraph and Agent Patterns.ipynb`) never uses LangChain's `create_agent` wrapper — every agent, including simple tool-calling ones, is built directly on raw LangGraph primitives (`@tool`, `.bind_tools()`, `ToolNode`, `tools_condition`) as a deliberate teaching choice, to make the loop's internals visible. Current LangChain docs¹ present `create_agent` as the default production entry point for exactly this shape of agent, reserving raw LangGraph for cases needing node-level control beyond what `create_agent`'s middleware/hooks expose.

## Related
- **Builds on** — [[langchain-runnables-lcel]], [[workflow-vs-agent-autonomy-spectrum]]
- **Contrasts with** — [[langchain-vs-langgraph]]
- **Feeds into** — [[langchain-tool-integration]], [[react-pattern]]

## Sources

**Lab sources**
- `lab-summaries/Day3-Session1-LangGraphPatterns.md` (§ A2 "One minimal graph per pattern" — patterns 2 and 4)
- `labs/production-notes.md` (§ "Tool Calling")

**Web sources**
- ¹[LangChain — Agents (docs.langchain.com/oss/python/langchain/agents)](https://docs.langchain.com/oss/python/langchain/agents) — `create_agent` signature, `AgentExecutor` maintenance-only status and migration path, accessed 2026-08-20
