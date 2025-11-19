import sys

from mcp.server import FastMCP
from models import AddInput, AddOutput

mcp = FastMCP("Calculator")


@mcp.tool()
def add(input: AddInput) -> AddOutput:
    print("Tool Called: add(AddInput) -> AddOutput")
    return AddOutput(result=input.a + input.b)


if __name__ == '__main__':
    print("Starting mcp_server_1 server...")
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        mcp.run()
    else:
        mcp.run(transport="stdio")
        print("Shutting down mcp_server_1 server")
