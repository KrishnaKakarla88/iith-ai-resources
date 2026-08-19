import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

SERVER_URL = "http://127.0.0.1:8000/mcp"  # must match host/port/path in server.py's mcp.run()


async def main():
    # streamable_http_client opens the HTTP connection (its own task group runs the
    # background read/write loops). ClientSession wraps it and does the initialize
    # handshake. Both "async with" blocks must stay open for the WHOLE lifetime of
    # anything that uses `session` - that's the "session must stay in one Task" rule
    # from production-notes.md. Everything below runs inside this one block, so the
    # connection/session persists across all three calls instead of reconnecting each time.
    async with streamable_http_client(SERVER_URL) as (read_stream, write_stream, _get_session_id):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            listed = await session.list_tools()
            print("tools ->", [t.name for t in listed.tools])

            result = await session.call_tool("greet_user", {"name": "Krishna"})
            print("call 1 ->", result.content[0].text)

            # same session, no reconnect/re-handshake for this second call
            result2 = await session.call_tool("greet_user", {"name": "again"})
            print("call 2 ->", result2.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
