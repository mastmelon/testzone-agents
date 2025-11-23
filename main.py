import asyncio
import sys
import signal
import os
import yaml

from mcp_servers.multiMCP import MultiMCP


def handle_signal(signum, frame):
    print("ERROR " f"main.py Received signal {signum} in PID {os.getpid()}")
    sys.exit(1)


for sig in (signal.SIGINT, signal.SIGTERM):
    signal.signal(sig, handle_signal)


async def main():
    print("Hello World!")
    print("Loading MCP Server...")
    with open("config/mcp_server_config.yaml", 'r') as f:
        mcp_server_config = yaml.safe_load(f)
        mcp_servers_config_dict = mcp_server_config.get("mcp_servers", [])

    multi_mcp = MultiMCP(mcp_server_configs=mcp_servers_config_dict)
    await multi_mcp.initialize()

    while True:
        query = input("🟢  You: ").strip()
        if query.lower() in {"exit", "quit"}:
            print("👋  Goodbye!")
            break

        # TODO - Do something with query here

        follow = input("\n\nContinue? (press Enter) or type 'exit': ").strip()
        if follow.lower() in {"exit", "quit"}:
            print("👋  Goodbye!")
            break


if __name__ == "__main__":
    asyncio.run(main())
