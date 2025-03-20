import os

# Mock root directory
mock_getcwd = lambda: '/'
original_getcwd = os.getcwd
os.getcwd = mock_getcwd

from src.mcp_agile_flow.simple_server import get_safe_project_path

try:
    path, source = get_safe_project_path()
    print(f'Safe path: {path}, source: {source}')
except ValueError as e:
    print(f'Error correctly raised: {e}')

# Restore original
os.getcwd = original_getcwd
print(f'Current real directory: {os.getcwd()}')
