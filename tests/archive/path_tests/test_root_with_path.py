import os


# Mock root directory
def mock_getcwd():
    return "/"


original_getcwd = os.getcwd
os.getcwd = mock_getcwd

from src.mcp_agile_flow.simple_server import get_safe_project_path

# Test with a valid path while in root
valid_path = "/Users/smian/development/mcp-agile-flow"
try:
    path, source = get_safe_project_path({"project_path": valid_path})
    print(f"Safe path: {path}, source: {source}")
except ValueError as e:
    print(f"Error: {e}")

# Try with root path
try:
    path, source = get_safe_project_path({"project_path": "/"})
    print(f"Safe path: {path}, source: {source}")
except ValueError as e:
    print(f"Error correctly raised for root path: {e}")

# Restore original
os.getcwd = original_getcwd
print(f"Current real directory: {os.getcwd()}")
