import ast
import json
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

                            for tool in tools.tools:
                                self.tool_map[tool.name] = {
                                    "config": server_config,
                                    "tool": tool
                                }
                                server_key = server_config["id"]

                                if server_key not in self.server_tools:
                                    self.server_tools[server_key] = []
                                self.server_tools[server_key].append(tool)
                    except Exception as ex:
                        print(f"Session creation failed: {ex}")
                        traceback.print_exc()
            except Exception as e:
                print(f"Error initializing MCP server: {server_config['script']}: {e}")
                traceback.print_exc()

    def tool_description_wrapper(self) -> List[str]:
        """Format tool usage as: tool(type, type)  # description"""
        examples = []
        for tool in self.get_all_tools():
            schema = tool.inputSchema
            if "input" in schema.get("properties", {}):
                inner_key = next(iter(schema.get("$defs", {})), None)
                props = schema["$defs"][inner_key]["properties"]
            else:
                props = schema["properties"]

            arg_types = []
            for k, v in props.items():
                t = v.get("type", "any")
                arg_types.append(t)

            signature_str = ", ".join(arg_types)
            examples.append(f"{tool.name}({signature_str})  # {tool.description}")
        return examples

    def get_all_tools(self) -> List[Any]:
        return [entry["tool"] for entry in self.tool_map.values()]

    async def function_wrapper(self, tool_name: str, *args):
        """
        Call a tool like a function with positional args OR a single string like 'add(45, 55)'.
        Returns the most relevant parsed result.
        """
        # ── Handle LLM-style string input like: "add(45, 55) or ("send_email", ("a@b.com", "hello"))" ─────────────────
        # ── Handle string-form function call like "add(10, 20)" ──────────────
        if isinstance(tool_name, str) and len(args) == 0:
            stripped = tool_name.strip()
            if stripped.endswith(")") and "(" in stripped:
                try:
                    expr = ast.parse(stripped, mode='eval').body
                    if not isinstance(expr, ast.Call) or not isinstance(expr.func, ast.Name):
                        raise ValueError("Invalid function call format")
                    tool_name = expr.func.id
                    args = [ast.literal_eval(arg) for arg in expr.args]
                except Exception as e:
                    raise ValueError(f"Failed to parse function string '{tool_name}': {e}")

        # ── Look up tool ─────────────────────────────────────
        tool_entry = self.tool_map.get(tool_name)
        if not tool_entry:
            raise ValueError(f"Tool '{tool_name}' not found.")

        tool = tool_entry["tool"]
        schema = tool.inputSchema
        params = {}

        # ── Build input payload ──────────────────────────────
        if "input" in schema.get("properties", {}):
            inner_key = next(iter(schema.get("$defs", {})), None)
            inner_props = schema["$defs"][inner_key]["properties"]
            param_names = list(inner_props.keys())
            if len(param_names) != len(args):
                raise ValueError(f"{tool_name} expects {len(param_names)} args, got {len(args)}")
            params["input"] = dict(zip(param_names, args))
        else:
            param_names = list(schema["properties"].keys())
            if len(param_names) != len(args):
                raise ValueError(f"{tool_name} expects {len(param_names)} args, got {len(args)}")
            params = dict(zip(param_names, args))

        # ── Call and Normalize Output ────────────────────────
        result = await self.call_tool(tool_name, params)

        try:
            content_text = getattr(result, "content", [])[0].text.strip()
            parsed = json.loads(content_text)

            if isinstance(parsed, dict):
                if "result" in parsed:
                    return parsed["result"]
                if len(parsed) == 1:
                    return next(iter(parsed.values()))
                return parsed

            return parsed  # primitive type
        except Exception:
            return result  # fallback if parse fails

    async def call_tool(self, tool_name: str, arguments: dict) -> Any:
        entry = self.tool_map.get(tool_name)
        if not entry:
            raise ValueError(f"Tool '{tool_name}' not found on any server.")

        config = entry["config"]
        params = StdioServerParameters(
            command=sys.executable,
            args=[config["script"]],
            cwd=config.get("cwd", os.getcwd())
        )

        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                return await session.call_tool(tool_name, arguments)

    async def shutdown(self):
        pass
