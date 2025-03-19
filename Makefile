.PHONY: install install-dev test test-debug run clean format lint venv

# Virtual environment settings
VENV_DIR = .venv
VENV_ACTIVATE = $(VENV_DIR)/bin/activate
UV = uv

# Define the package name and paths
PACKAGE_NAME = mcp_agile_flow
SOURCE_DIR = src
TESTS_DIR = tests

# Python settings
PYTEST_FLAGS := -v -s  # Always show print statements

# Virtual environment target
venv:
	$(UV) venv $(VENV_DIR) --python=$(shell which python3)

# Installation targets
install: venv
	$(UV) pip install -e .

install-dev: venv
	$(UV) pip install pytest pytest-asyncio black flake8 mypy
	$(UV) pip install -e .

# Testing targets
test: venv
	$(UV) run pytest $(PYTEST_FLAGS) $(TESTS_DIR)

test-debug: venv
	$(UV) run pytest $(PYTEST_FLAGS) --show-capture=all --tb=short $(TESTS_DIR)

# Run the server targets
run-server: venv
	$(UV) run run_mcp_server.py

run-simple-server: venv
	$(UV) run run_simple_mcp_server.py

# Setup Cursor MCP
setup-cursor: venv
	$(UV) run setup_cursor_mcp.py

# Clean temporary files and build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf **/__pycache__/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/

# Code quality targets
format: venv
	$(UV) run black $(SOURCE_DIR) $(TESTS_DIR)

lint: venv
	$(UV) run flake8 $(SOURCE_DIR) $(TESTS_DIR)
	$(UV) run mypy $(SOURCE_DIR)

# Default target
all: install test 