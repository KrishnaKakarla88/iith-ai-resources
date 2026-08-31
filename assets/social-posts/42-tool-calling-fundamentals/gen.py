import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 7, "Concept", "The Model Never Executes Anything",
      ["It produces a request — name and arguments. Your code decides whether to comply and runs it."])

slide(p("slide-02.png"), 2, 7, "Core Mechanics", "Three Parts The Model Sees",
      ["**name**: an unambiguous, verb-first identifier. **parameters**: a JSON Schema constraining the argument shape.",
       "**description**: the highest-leverage field — it's effectively a prompt deciding when the model reaches for this tool."])

slide(p("slide-03.png"), 3, 7, "Safety First", "Never eval() A Calculator Tool",
      ["eval(expr) is arbitrary code execution — anything Python can parse as an expression.",
       "Parse with ast.parse and walk the tree, evaluating only a whitelisted operator set."],
      code="_SAFE_OPS = {ast.Add: operator.add, ast.Mult: operator.mul, ...}")

slide(p("slide-04.png"), 4, 7, "Sample Code", "The Bind-Execute-Feedback Loop",
      ["Model requests a call, your code runs it, wraps the result as a ToolMessage, and loops again."],
      code="for tc in response.tool_calls:\n    result = tool_by_name[tc['name']].invoke(tc['args'])\n    messages.append(ToolMessage(content=str(result), tool_call_id=tc['id']))")

slide(p("slide-05.png"), 5, 7, "Gotcha", "Narrated Isn't Executed",
      ["\"I checked the weather and it's 31°C\" with no tool_calls entry is not evidence a tool ran.",
       "Always drive execution off the structured tool_calls field, never off the model's prose."])

slide(p("slide-06.png"), 6, 7, "Production Practice", "Don't Trust The Model With Exact Numbers",
      ["Force deterministic values — an amount, an account ID — from your own system state.",
       "The model is good at picking which tool and roughly what arguments, not the source of truth for a number."])

slide(p("slide-07.png"), 7, 7, "Takeaway", "The Description Is Your Prompt You Forgot You Wrote",
      ["A vague description causes the wrong tool call, or the right tool at the wrong time — no amount of schema tightening fixes that."],
      closing_q="When did a vague tool description cause a wrong-tool call for you?")

print("done: 42")
