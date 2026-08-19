"""Local entry point."""
import asyncio

from agents.order_agent import main

if __name__ == "__main__":
    asyncio.run(main())
