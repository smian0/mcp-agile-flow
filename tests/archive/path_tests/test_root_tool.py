import asyncio
import json
import os


# Mock root directory
def mock_getcwd():
    return "/"


original_getcwd = os.getcwd
os.getcwd = mock_getcwd

from src.mcp_agile_flow.simple_server import handle_call_tool


async def test():
    # Test get-safe-project-path with no arguments in root
    result = await handle_call_tool("get-safe-project-path", {})
    print("RESULT STATUS:", "ERROR" if result[0].isError else "SUCCESS")
    response = json.loads(result[0].text)
    print("RESPONSE:", json.dumps(response, indent=2))

    # Test with valid path
    valid_path = "/Users/smian/development/mcp-agile-flow"
    result = await handle_call_tool(
        "get-safe-project-path", {"proposed_path": valid_path}
    )
    print("\nRESULT WITH VALID PATH:", "ERROR" if result[0].isError else "SUCCESS")
    response = json.loads(result[0].text)
    print("RESPONSE:", json.dumps(response, indent=2))


# Restore original before exiting
try:
    asyncio.run(test())
finally:
    os.getcwd = original_getcwd
    print(f"\nCurrent real directory: {os.getcwd()}")
