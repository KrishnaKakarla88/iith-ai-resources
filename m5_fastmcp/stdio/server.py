from __future__ import annotations
import sys
from fastmcp import FastMCP

mcp = FastMCP("simple-mcp-server")

@mcp.tool()
def greet_user(name: str) -> str:
    """To greet the user with a Hello."""
    return f"Hello, {name}!"

mcp.run(transport="stdio", show_banner=False)