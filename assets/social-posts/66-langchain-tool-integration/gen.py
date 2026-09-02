import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "Your Docstring Is The API Contract, Not Documentation Of One",
      ["A model doesn't call a Python function — it emits a tool name plus JSON arguments. LangChain's @tool decorator builds that bridge from your type hints and docstring."])

slide(p("slide-02.png"), 2, 6, "Sample Code", "Type Hints Become Schema, Docstring Becomes The Pitch",
      ["A vague docstring becomes a broken integration that raises no error — the model just calls it wrongly, or never calls it, and nothing in your logs points at the cause."],
      code="@tool\ndef search_kb(query: str, limit: int = 5) -> list[dict]:\n    \"\"\"Search the internal knowledge base for policy documents matching query.\"\"\"\n    return kb_index.search(query, limit=limit)")

slide(p("slide-03.png"), 3, 6, "The Same Function, Discovered Remotely", "One Line Bridges Local And MCP Tools",
      ["MultiServerMCPClient.get_tools() spawns, initializes, and discovers a running MCP server's tools — indistinguishable from an @tool-defined function to the model."],
      code="client = MultiServerMCPClient({\n    \"project\": {\"transport\": \"stdio\", \"command\": sys.executable, \"args\": [SERVER_PATH]},\n})\ntools = await client.get_tools()")

slide(p("slide-04.png"), 4, 6, "The Gotcha", "MCP Results Arrive As Content Blocks, Not Plain Values",
      ["**Example:** a local @tool returns a bare dict. Over MCP the same call returns [{\"type\": \"text\", \"text\": \"<json>\"}].",
       "A real incident: a successful refund got reported as failed because an isinstance(result, dict) check was written against the wrong shape."])

slide(p("slide-05.png"), 5, 6, "Another One", "sys.executable, Never A Bare \"python\" String",
      ["A bare string resolves against whatever interpreter is first on PATH — the resulting failure looks like a protocol error, not the interpreter mismatch it actually is."])

slide(p("slide-06.png"), 6, 6, "Takeaway", "Normalize The Result Shape Once, At The Call Boundary",
      ["Not per consumer — an isinstance check against one SDK's shape is a version pin in disguise."],
      closing_q="Would your tool-result handling survive an SDK version bump to the response shape?")

print("done: 66")
