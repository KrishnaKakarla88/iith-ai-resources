import sys, os
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

mcp_client = MultiServerMCPClient({
    "project": {
        "transport": "stdio",           # spawn it as a child process and talk over stdin/stdout
        "command": sys.executable,      # THIS interpreter - see the note above
        "args": [os.path.join(os.path.dirname(__file__), "server.py")],
    }
})

async def main():
    mcp_tools = await mcp_client.get_tools()
    TOOLS_BY_NAME = {t.name: t for t in mcp_tools}

    print("DISCOVERED TOOLS")
    print("-------------------------------------------------------")
    for t in mcp_tools:
        print(f"  {t.name}{tuple(t.args)}")
        print(f"      {t.description.splitlines()[0]}")

    async with mcp_client.session("project") as session:
        # Inside this block `session` is a live mcp.ClientSession - the SAME object the low-level SDK
        # gives you. The adapter did the spawn and the initialize handshake; from here you can use
        # either API. load_mcp_tools() binds LangChain tools to THIS connection...
        session_tools = await load_mcp_tools(session)
        print("tools bound to the live session:", [t.name for t in session_tools])

        # ...and the raw protocol calls are still right there.
        listed = await session.list_tools()
        print("raw list_tools ->", [t.name for t in listed.tools])

        # called = await session.call_tool("search_kb", {"topic": "contract_terms"})
        # print("raw call_tool  ->", [r["id"] for r in json.loads(called.content[0].text)])
   

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())