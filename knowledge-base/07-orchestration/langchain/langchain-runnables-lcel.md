---
stage: "07-orchestration"
tools: [langchain]
tags: [orchestration, langchain, lcel, chains]
last_verified: 2026-08-20
verified_against: "langchain_core (transitive via langchain-litellm 0.7.x — no direct `langchain` pin in this repo, see Course vs. production)"
---

# LangChain Runnables & LCEL

LCEL (LangChain Expression Language) is the `|`-operator syntax for composing `Runnable` objects — LangChain's common interface for "a thing that takes an input and produces an output," synchronously, asynchronously, streamed, or batched.

## Prerequisites
- [[langchain-vs-langgraph]]

## In plain English

Every piece you'd want to chain together in LangChain — a prompt template, a chat model, an output parser, a retriever — implements the same `Runnable` interface. That shared interface is what makes the pipe operator (`|`) work: `prompt | model | parser` isn't string concatenation, it's building a `RunnableSequence` where each step's output becomes the next step's input. Because every `Runnable` supports the same set of execution modes (`invoke`, `stream`, `batch`, and their async equivalents) *for free*, once you've composed a chain with `|`, you get streaming and batching without writing any extra code for them — that's the actual payoff of LCEL over hand-writing `step2(step1(x))`.

The tradeoff, and the reason this page exists right next to [[langchain-vs-langgraph]]: LCEL composition is for **straight-line or simply-branching pipelines**. It has no concept of a loop, no persisted state across steps beyond what flows through the pipe, and no pause-and-resume. The moment a workflow needs conditional routing that can send work backward, a human-in-the-loop pause, or state that survives a crash, you've outgrown a chain and want a graph — see [[graph-engineering-mindset]].

## Core mechanics

| Method / operator | What it does |
|---|---|
| `invoke(input)` / `ainvoke(input)` | Run once, synchronously / asynchronously, return the final output |
| `batch([inputs])` / `abatch([inputs])` | Run over a list of inputs, in parallel where the runnable supports it |
| `stream(input)` / `astream(input)` | Yield output incrementally as it's produced (token-by-token for a chat model) |
| `\|` (pipe operator) | Compose two Runnables into a `RunnableSequence` — output of the left becomes input of the right |
| `RunnableSequence` | The result of chaining with `\|`; runs steps in order |
| `RunnableParallel` | Runs multiple Runnables concurrently against the same input, returns a dict of their outputs |
| `RunnableLambda` | Wraps a plain Python function so it can sit inside a `\|` chain |
| `RunnablePassthrough` | Forwards input unchanged — used to keep an original value alongside a transformed one in a `RunnableParallel` |

Every `Runnable` in a chain supports all of `invoke`/`batch`/`stream` (and async variants) uniformly — this is the concrete meaning of "LCEL chains support sync, async, batch, and streaming as first-class features," verified against LangChain's current `langchain_core` reference.¹

## Sample code

Adapted from LangChain's own reference docs¹ (this repo's labs don't build LCEL chains directly — they build agents on raw LangGraph, see [[langchain-vs-langgraph]] — so this snippet is web-sourced, not lab-sourced, and marked as such):

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_litellm import ChatLiteLLM

prompt = ChatPromptTemplate.from_template("Summarize this ticket: {ticket_text}")
model = ChatLiteLLM(model="groq/llama-3.1-8b-instant", temperature=0)
parser = StrOutputParser()

chain = prompt | model | parser          # RunnableSequence
summary = chain.invoke({"ticket_text": raw_text})   # sync
async for token in chain.astream({"ticket_text": raw_text}):  # streamed
    print(token, end="")
```

`ChatLiteLLM` (from `langchain-litellm`, this repo's pinned model wrapper — see [[litellm-basics]]) is itself a `Runnable`, so it composes with `|` the same as any other LangChain component.

## Alternatives

| Approach | Where it lives | Boring/simple alternative to LCEL? |
|---|---|---|
| LCEL (`\|`, `Runnable*`) | `langchain_core`, standalone from the rest of LangChain | — |
| LlamaIndex Workflows (`@step`-decorated event-driven steps) | LlamaIndex framework | No — same tier of tooling, event-driven rather than pipe-composed, and LlamaIndex's own docs position it as also handling branching/loops that LCEL doesn't² |
| LangGraph nodes/edges | Same vendor, one level up in capability | No — a graph subsumes what a chain does plus branching/state/resume; see [[langchain-vs-langgraph]] |
| Plain Python function composition (`step3(step2(step1(x)))`) | No dependency | **Yes** — the boring option; loses uniform streaming/batching/async and the declarative `\|` readability, fine for a one-off script that's never going to need to stream |

## How this shows up in the capstone

Milestone 5 (orchestrated LangGraph workflow with checkpointing): any strictly sequential piece inside an agent's own processing — e.g. prompt-template-in, structured-output-out for a single classification step — is a natural fit for an LCEL chain even inside a larger LangGraph node, since a node function is free to build and invoke its own small `Runnable` chain internally; see [[capstone-milestone-map]].

## Interview fire round

- **Q: What does composing with `|` actually buy you over calling three functions in sequence?**
  A: Every step already implements the same `Runnable` interface, so the resulting chain gets `invoke`/`batch`/`stream` (and their async forms) uniformly for free — you don't write separate streaming logic for a 3-step vs. a 7-step chain.
- **Q: When should you stop composing with LCEL and reach for LangGraph instead?**
  A: The moment the workflow needs a loop that can go backward (not just forward through fixed steps), a pause for human input, or state that must survive a process crash — none of which a `RunnableSequence` models.

## Production gotchas & best practices

- Production practice (web-sourced¹): LCEL's uniform `batch`/`astream` support is the concrete reason to prefer it over hand-rolled function composition for anything that will eventually need to scale to concurrent requests or stream partial output to a UI — retrofitting streaming onto ad hoc Python composition later is more work than composing with `|` from the start.
- Lab-adjacent gotcha (`labs/production-notes.md`, "LangChain" row): a fix to a centralized LLM-call wrapper (tracing, retry, cost accounting) only covers call sites that actually go through that wrapper — a code path that builds its own chain and calls `.invoke()`/`.ainvoke()` directly bypasses it silently. Audit for parallel LCEL chains built outside the shared wrapper before calling an instrumentation fix complete.

## Course vs. production

This repo's labs never build LCEL chains — every agent is built directly on raw LangGraph (see [[langchain-vs-langgraph]], Course vs. production). In production LangChain usage more broadly, LCEL is the default for the straight-line pieces (a single structured-extraction call, a summarization step) precisely because most real workflows are a mix: a handful of always-fixed steps (chains) embedded inside a larger stateful, branching workflow (a graph) — not one or the other for the whole system.

## Related
- **Builds on** — [[langchain-vs-langgraph]]
- **Contrasts with** — [[graph-engineering-mindset]]
- **Related tool** — [[litellm-basics]] (`ChatLiteLLM` as a `Runnable`)

## Sources

**Lab sources**
- `labs/production-notes.md` (§ "Langfuse" and "Technology-Specific Learnings" — centralized-wrapper bypass gotcha)
- `pyproject.toml` (no direct `langchain` pin — noted in Course vs. production)

**Web sources**
- ¹[LangChain Core — Runnable reference (reference.langchain.com/python/langchain_core)](https://reference.langchain.com/python/langchain_core/) — `invoke`/`ainvoke`/`batch`/`abatch`/`stream`/`astream`, `RunnableSequence`/`RunnableParallel`/`RunnableLambda`/`RunnablePassthrough`, accessed 2026-08-20
- ²[LlamaIndex — Workflows module guide](https://developers.llamaindex.ai/python/framework/module_guides/workflow/) — event-driven `@step` composition as LlamaIndex's chain-composition alternative, accessed 2026-08-20
