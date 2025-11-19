import asyncio
import yaml

from mcp_servers.multiMCP import MultiMCP


async def main():
    print("Hello World!")
    print("Loading MCP Server...")
    with open("config/mcp_server_config.yaml", 'r') as f:
        mcp_server_config = yaml.safe_load(f)
        mcp_servers_config_dict = mcp_server_config.get("mcp_servers", [])

    multi_mcp = MultiMCP(mcp_server_configs=mcp_servers_config_dict)
    await multi_mcp.initialize()


if __name__ == "__main__":
    asyncio.run(main())
