import os
import sys
import traceback
from typing import List, Dict, Any
from mcp import StdioServerParameters, stdio_client, ClientSession


class MultiMCP:
    def __init__(self, mcp_server_configs: List[dict]):
        self.mcp_server_configs = mcp_server_configs
        self.tool_map: Dict[str, Dict[str, Any]] = {}
        self.server_tools: Dict[str, List[Any]] = {}

    async def initialize(self):
        print("Initializing MultiMCP...")
        for server_config in self.mcp_server_configs:
            try:
                studio_server_params = StdioServerParameters(
                    command=sys.executable,
                    args=[server_config['script']],
                    cwd=server_config.get('cwd', os.getcwd())
                )

                print(f"Scanning tools for {server_config['script']} in {server_config['cwd']}")
                async with stdio_client(studio_server_params) as (read, write):
                    print("Connection established, creating session...")
                    try:
                        async with ClientSession(read, write) as session:
                            print("MCP session initializing")
                            await session.initialize()
                            print("MCP session initialized")

                            tools = await session.list_tools()
                            print(f"\n→ Tools received: {[tool.name for tool in tools.tools]}")
                    except Exception as ex:
                        print(f"Session creation failed: {ex}")
                        traceback.print_exc()
            except Exception as e:
                print(f"Error initializing MCP server: {server_config['script']}: {e}")
                traceback.print_exc()
