"""Single ShopSense agent using LiteLLM and MCP tools.

Flow:
user -> LLM -> MCP tool -> observation -> LLM -> ... -> final answer
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from pydantic import ValidationError

REPO_ROOT = Path(__file__).resolve().parents[3]
M2_ROOT = Path(__file__).resolve().parents[1]
for path in (REPO_ROOT, M2_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from agents.agent_helpers import (
    build_llm,
    build_reason_hint,
    enrich_tool_args,
    lookup_order_follow_up,
    pre_llm_grounding_follow_up,
    validation_follow_up,
)
from agents.memory_bridge import (
    build_memory_context,
    remember_turn,
    resolve_customer_ref,
)
from schemas import TOOL_SCHEMAS

MCP_SERVER = Path(__file__).resolve().parents[1] / "mcp" / "order_server.py"

SYSTEM_PROMPT = """
You are the ShopSense order-actions agent.

Use tools whenever order data or an order action is required.

Rules:
- If required information is missing or uncertain, ask a follow-up question instead of guessing.
- Never invent order, product, refund, replacement, or shipment data.
- Never generate tool arguments that are not explicitly present in user text or previous tool outputs.
- If a required value is missing, respond with a clarification question and do not call tools.
- Use lookup_order when order details are required.
- Use calculate_refund_amount instead of calculating refunds yourself.
- Use process_refund only after the refund amount is known.
- Ask user for refund/replace reason only if it cannot be inferred from the user message or previous tool output.
- If the customer's message clearly states a reason such as damaged, broken, wrong item, late delivery, or quality, treat that reason as already provided.
- Use replace_item for item-level replacement requests.
- Use track_shipment for delivery tracking.
- Respect every validation and guardrail returned by tools.
- If a refund is escalated, clearly say human review is required.
- Keep the final response concise.
""".strip()


async def run_order_agent(
    customer_message: str,
    max_iterations: int = 6,
) -> str:
    preflight_follow_up = pre_llm_grounding_follow_up(customer_message)
    if preflight_follow_up:
        return preflight_follow_up

    customer_ref = resolve_customer_ref(customer_message)
    memory_context = (
        build_memory_context(customer_ref, customer_message) if customer_ref else None
    )

    client = MultiServerMCPClient(
        {
            "orders": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [str(MCP_SERVER)],
            }
        }
    )

    tools = await client.get_tools()
    tools_by_name = {tool.name: tool for tool in tools}

    llm = build_llm()
    model_with_tools = llm.bind_tools(tools)

    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    if memory_context:
        messages.append(SystemMessage(content=memory_context))

    reason_hint = build_reason_hint(customer_message)
    if reason_hint:
        messages.append(SystemMessage(content=reason_hint))

    messages.append(HumanMessage(content=customer_message))

    for _ in range(max_iterations):
        ai_message = await model_with_tools.ainvoke(messages)
        messages.append(ai_message)

        if not ai_message.tool_calls:
            final_response = str(ai_message.content)
            if customer_ref:
                try:
                    remember_turn(customer_ref, customer_message, final_response)
                except Exception:
                    pass
            return final_response

        for tool_call in ai_message.tool_calls:
            tool_name = tool_call["name"]
            tool = tools_by_name.get(tool_name)
            schema = TOOL_SCHEMAS.get(tool_name)

            if tool is None:
                result = f"ERROR: Unknown tool '{tool_name}'."
            elif schema is None:
                result = f"ERROR: No schema configured for tool '{tool_name}'."
            else:
                try:
                    raw_tool_args = tool_call.get("args") or {}
                    tool_args = enrich_tool_args(
                        tool_name,
                        raw_tool_args,
                        customer_message,
                    )
                    validated_args = schema.model_validate(tool_args)
                    result = await tool.ainvoke(validated_args.model_dump())
                except ValidationError as exc:
                    return validation_follow_up(tool_name, exc)
                except Exception as exc:
                    result = f"ERROR: {type(exc).__name__}: {exc}"

            messages.append(
                ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call["id"],
                )
            )

    return "Stopped after reaching the maximum tool-call iterations."


async def main() -> None:
    print("ShopSense M2 agent. Type 'exit' to stop.")

    while True:
        message = input("\nYou: ").strip()
        if message.lower() in {"exit", "quit"}:
            break
        if not message:
            continue

        response = await run_order_agent(message)
        print(f"Agent: {response}")


if __name__ == "__main__":
    asyncio.run(main())
