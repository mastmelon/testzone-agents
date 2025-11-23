import sys

from mcp.server import FastMCP
from models import AddInput, AddOutput

mcp = FastMCP("Calculator")


@mcp.tool()
def add(input: AddInput) -> AddOutput:
    print("Tool Called: add(AddInput) -> AddOutput")
    return AddOutput(result=input.a + input.b)


def mcp_log(level: str, filename: str, message: str) -> None:
    sys.stderr.write(f"{level}: {filename}: {message}\n")
    sys.stderr.flush()


if __name__ == '__main__':
    mcp_log("INFO", "mcp_server_1.py", "Starting mcp_server_1 server...")
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        mcp.run()
    else:
        mcp.run(transport="stdio")
        mcp_log("INFO", "mcp_server_1.py", "Shutting down mcp_server_1 server")
