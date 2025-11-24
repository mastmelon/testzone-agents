# test_process_documents.py
import asyncio
import sys
from pathlib import Path

# Add parent directory to path BEFORE any mcp_servers imports
# This is needed because mcp_server_3.py imports from mcp_servers.models
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from mcp_servers.mcp_server_3 import duckduckgo_search_results, download_raw_html_from_url
from mcp_servers.models import SearchInput, UrlInput


# Mock Context class for testing
class MockContext:
    """Simple mock context for testing FastMCP functions"""

    async def info(self, message: str):
        print(f"INFO: {message}")

    async def error(self, message: str):
        print(f"ERROR: {message}")


async def test_duckduckgo_search():
    """Test the duckduckgo_search_results function"""
    # Create a SearchInput with a test query
    search_input = SearchInput(
        query="Python programming",
        max_results=5
    )

    # Create a mock context
    ctx = MockContext()

    # Call the async function
    result = await duckduckgo_search_results(search_input, ctx)

    # Print the results
    print("\n" + "=" * 50)
    print("SEARCH RESULTS:")
    print("=" * 50)
    print(result.result)
    print("=" * 50)

    return result


async def test_download_raw_html_from_url():
    """Test the download_raw_html_from_url function"""
    # Create a UrlInput with a test URL
    url_input = UrlInput(
        url="https://en.wikipedia.org/wiki/Car"
    )

    # Create a mock context
    ctx = MockContext()

    # Call the async function
    result = await download_raw_html_from_url(url_input, ctx)

    # Print the results
    print("\n" + "=" * 50)
    print("HTML CONTENT:")
    print("=" * 50)
    print(result.result)
    print("=" * 50)

    return result


if __name__ == "__main__":
    # Run the async tests
    print("Testing DuckDuckGo search...")
    asyncio.run(test_duckduckgo_search())

    print("\n\nTesting HTML download...")
    asyncio.run(test_download_raw_html_from_url())
