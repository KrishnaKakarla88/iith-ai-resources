---
stage: "04-tool-calling-single-agents"
tools: [langchain-core, langchain-litellm, litellm]
tags: [tool-calling, function-calling, agent-design]
last_verified: 2026-08-20
verified_against: "langchain-litellm>=0.7.0, litellm>=1.96.2 (this repo's pins)"
---

# Tool calling fundamentals

How an LLM requests a function call, how the caller executes it and returns the result, and why this turns a text generator into something that can act.

## Prerequisites
- [[agentic-loop-fundamentals]]
- [[litellm-basics]]
- [[pydantic-basics]]

## In plain English

An LLM's training cutoff freezes its knowledge — it can't know today's weather, today's exchange rate, or a row in your production database, because none of that existed when it was trained, and it can't reach out and check. A **tool** (also called a "function" in older API docs) fixes this by giving the model a way to *ask* your application to do something on its behalf — run a calculation, hit an API, query a database — and hand the result back.

The critical thing to internalize: **the model never executes anything.** It produces text shaped like "I'd like to call `get_weather` with `city="Hyderabad"`." Your code reads that request, decides whether to comply, actually runs the function, and feeds the result back into the conversation as new context. The model is a capable intern who can draft the request — it doesn't have the send button. This is why a tool schema is also a safety boundary: whatever the model can name and shape an argument for, it can *ask* to run, but your code is still the one deciding to run it, and the schema is your first line of defense against a badly-shaped or dangerous request.

## Core mechanics

A tool has three parts the model actually sees, plus one part only your code sees:

| Part | Who writes it | What it's for |
|---|---|---|
| `name` | You | Unambiguous, verb-first identifier the model uses to request the call (`get_weather`, not `weather_helper_v2`) |
| `description` | You (in the function docstring, when using `@tool`) | The highest-leverage field — it's effectively a prompt that decides *when* the model reaches for this tool at all; vague descriptions cause wrong or missed calls |
| `parameters` (JSON Schema) | You (inferred from type hints, when using `@tool`) | Constrains what shape an argument request can take — prefer an `enum` over free text wherever the valid values are a fixed, known set |
| the actual function body | You | Never seen by the model — this is where execution happens, and where you enforce whatever safety checks the schema alone can't (range checks, auth, idempotency keys) |

The loop that ties these together, once tools are bound to a model:

| Step | What happens |
|---|---|
| 1 | Your code calls `model.invoke(messages)` with tools bound via `bind_tools(...)` |
| 2 | Model returns either a final text answer, or one or more `tool_calls` (name + arguments per call) |
| 3 | If no `tool_calls`: return the text, loop ends |
| 4 | If `tool_calls`: your code runs each requested tool, wraps each result in a `ToolMessage` tied back to its `tool_call_id`, appends all of them to `messages` |
| 5 | Repeat from step 1, now with the tool results in context |
| — | Hard cap on iterations — see [[agentic-loop-fundamentals]] |

Note step 2 carefully: the model can request tool calls it didn't execute — always drive what actually runs off the returned `tool_calls` structure, never off the model's prose ("I called the weather tool and got 31°C" is not evidence a tool call happened; a "narrated but unexecuted" tool call is a real failure mode to watch for in more complex agents).

## Sample code

Lab-sourced (Day 1 · Session 2 — `labs/Day1 Session 2 - Tool calling and Single Agent Patterns.ipynb`, Lab A). The calculator is the canonical example of a **safe** tool implementation — parsing with `ast` and evaluating only whitelisted operators, never `eval()`:

```python
import ast
import operator

_SAFE_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.Pow: operator.pow, ast.USub: operator.neg,
}

def _eval_node(node):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _SAFE_OPS:
        return _SAFE_OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _SAFE_OPS:
        return _SAFE_OPS[type(node.op)](_eval_node(node.operand))
    raise ValueError(f"Unsupported expression: {ast.dump(node)}")

def calculate(expr: str) -> float:
    """Evaluate a basic arithmetic expression, e.g. '2 * (3 + 4)'."""
    tree = ast.parse(expr, mode="eval")
    return _eval_node(tree.body)
    # NEVER use eval(expr) here — arbitrary code execution risk;
    # walking a whitelisted operator set is the safe alternative
```

Wiring a tool for the model to see, and running the loop (`langchain_core.tools.tool` + `ChatLiteLLM` + `bind_tools`):

```python
from langchain_core.tools import tool
from langchain_litellm import ChatLiteLLM
from langchain_core.messages import ToolMessage

@tool
def calculator(expr: str) -> float:
    """Evaluate a basic arithmetic expression, e.g. '2 * (3 + 4)'."""
    return calculate(expr)

TOOLS = [calculator]  # + get_weather, get_currency, ... in the full lab
llm = ChatLiteLLM(model="gemini/gemini-flash-lite-latest", max_retries=5)
model = llm.bind_tools(TOOLS)

def run_travel_agent(messages: list, max_iterations: int = 6) -> str:
    tool_by_name = {t.name: t for t in TOOLS}
    for _ in range(max_iterations):
        response = model.invoke(messages)
        if not response.tool_calls:
            return response.content
        messages.append(response)
        for tc in response.tool_calls:
            result = tool_by_name[tc["name"]].invoke(tc["args"])
            messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))
    raise RuntimeError("max_iterations exceeded without a final answer")
```

The `@tool` decorator turns the docstring into the `description` field the model reads and the type-hinted signature into the JSON Schema `parameters` — "docstrings + type hints ARE the API contract" here, same discipline as [[type-hints-basics]] and [[pydantic-basics]] elsewhere in this KB. Every real tool in the lab (weather, currency) is wrapped by `make_robust_tool` before it reaches `@tool` — retry-with-backoff, a circuit breaker, and call logging composed around the implementation; full mechanics in [[retry-fallback-patterns]] and [[circuit-breaker-pattern]].

## Alternatives

| Approach | Where it lives | Trade-off |
|---|---|---|
| Hand-rolled loop (above) | Plain Python + `langchain_core.tools` | Full visibility into every iteration; you own the loop, the cap, and the error handling |
| LangChain `AgentExecutor` | `langchain.agents` | Same `bind_tools` mechanics, loop and iteration limit handled for you; less code to maintain, less to see when something goes wrong |
| LangGraph prebuilt ReAct agent (`create_react_agent`, superseded by `create_agent`) | `langgraph.prebuilt` / `langchain` | The loop as a graph node pair (LLM node, tool node) — gains state/checkpointing machinery from stage 05, more moving parts to understand |
| Native provider tool-use (OpenAI `tools=`, Anthropic `tool_use` blocks) | Direct SDK, no LangChain | Same underlying contract (model requests, you execute) — see [[raw-llm-clients]]; going through LiteLLM/LangChain buys provider-agnosticism at the cost of one more abstraction layer |

## How this shows up in the capstone

Milestone 2 — this is the mechanics: [[capstone-milestone-map]] maps [[tool-calling-fundamentals]] to M2 (tool-enabled single agent). The reliability wrappers referenced above (retry, circuit breaker) belong to Milestone 7 — resilience is wrapped *around* the tool calls built here, not part of the tool-calling mechanism itself. ShopSense's own tools (order lookup, refund issuance, policy search) all follow the mocked-first-then-swap-to-real pattern from Lab A: same function signature, implementation switched behind one flag, neither the loop nor the model ever changes.

## Interview fire round

- **Q: Who actually executes a tool call — the model or your code?**
  A: Your code, always. The model only ever produces a request (name + arguments); your application decides whether to comply and runs the function.
- **Q: Why is the tool's description field described as "the highest-leverage, most-neglected field"?**
  A: It's effectively a prompt the model reads to decide *when* to reach for the tool at all — a vague description causes the model to call the wrong tool, or the right tool at the wrong time, regardless of how correct the parameter schema is.
- **Q: What's wrong with implementing a calculator tool as `eval(expr)`?**
  A: Arbitrary code execution — `eval` runs anything Python can parse as an expression, including attribute access and calls into other code. Parse with `ast.parse` and walk the tree evaluating only a whitelisted operator set instead.

## Production gotchas & best practices

- Lab gotcha: `fastapi` must be installed even when running fully mocked (`USE_MCP=False`) — LiteLLM's tool-calling code imports it internally for an MCP-related handler regardless of whether MCP is actually used.
- Lab gotcha: third-party tool packages can be silently broken — the lab's own currency tool hand-rolls its API call rather than depending on a published MCP package that broke after an upstream API started redirecting and the package's HTTP client didn't follow redirects by default. Verify a third-party tool actually works before trusting it in a loop; see [[mcp-fastmcp]] for the fuller MCP-specific version of this warning.
- Production gotcha: watch for the model *narrating* a tool call it didn't actually make ("I checked the weather and it's 31°C" with no corresponding `tool_calls` entry) — always drive execution and downstream logic off the structured `tool_calls` field, never off the model's prose describing what it did.
- Production practice: prefer forcing deterministic values for sensitive operations (an amount, an account ID) from your own system state rather than trusting the model to compute or recall them correctly inside a tool-call argument — the model is good at deciding *which* tool and *roughly what* arguments, less trustworthy as the source of truth for a number that has to be exactly right.
- Production practice: design every tool to be safe to call twice by accident (idempotency) before making it callable in parallel — a `GET`-shaped lookup is safe to retry, a `charge_card` call is not without an idempotency key.

## Course vs. production

The lab calls tools directly off `bind_tools()` inside a hand-rolled loop, which is the right level of detail for learning the contract. A more mature production setup usually routes every model call — including tool-bound ones — through one centralized LLM wrapper (for consistent tracing, retries, and logging) rather than calling `bind_tools()`/`ainvoke()` directly at each call site; bypassing that central wrapper is a common gotcha once a codebase has more than one agent. [[langfuse-tracing]] (stage 05) covers wiring that observability layer in from the start rather than bolting it on later.

## Related
- **Builds on** — [[agentic-loop-fundamentals]], [[litellm-basics]]
- **Feeds into** — [[react-pattern]], [[reflection-pattern]], [[langchain-tool-integration]]
- **Wrapped by** — [[retry-fallback-patterns]], [[circuit-breaker-pattern]] (resilience layered around tool calls, not part of the calling mechanism itself)
- **Real tool backend** — [[mcp-fastmcp]] (tools can be backed by an MCP server behind the same function signature)

## Sources

**Lab sources**
- `lab-summaries/Day1-Session2-ToolCalling.md` (§ A1 Calculator, § A6 Reliability wrappers, § A7 Wire into LangChain, § A8 Tool-call loop)
- `labs/Day1 Session 2 - Tool calling and Single Agent Patterns.ipynb`
- `presentations/day1.md` (Day 1 · Session 2, Act 1 — "The Model Requests. Your Code Decides.")

**Web sources**
- [LangChain Reference — `ChatLiteLLM.bind_tools`](https://reference.langchain.com/python/langchain-litellm/chat_models/litellm/ChatLiteLLM/bind_tools) — tool-binding signature, `tool_choice` behavior, accessed 2026-08-20
- [LangChain Docs — LiteLLM integration](https://docs.langchain.com/oss/python/integrations/providers/litellm) — tool calling and structured output via `langchain-litellm`, accessed 2026-08-20
- [Claude Platform Docs — How tool use works](https://platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works) — comparison: `tool_use` block contract, client vs. server tools, accessed 2026-08-20
