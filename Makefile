# MCP Agile Flow - Makefile
# -------------------------

.PHONY: help venv install test test-coverage test-kg test-core test-full run-server setup-cursor clean clean-all quality all

# Configuration
# -------------
VENV_DIR := .venv
VENV_ACTIVATE := $(VENV_DIR)/bin/activate
UV := uv
PACKAGE_NAME := mcp_agile_flow
SOURCE_DIR := src
TESTS_DIR := tests
PYTEST_FLAGS := -v
TEST_PATH ?= $(TESTS_DIR)
TEST_MARKERS ?= --ignore=tests/full-stack-fastapi-sample-project -k "not test_mcp_via_agno_agent"

# Help target
# -----------
help:
	@echo "MCP Agile Flow - Make Targets"
	@echo "---------------------------"
	@echo "help:             Show this help message"
	@echo "venv:             Create virtual environment"
	@echo "install:          Install package"
	@echo "test:             Run tests with detailed debug output (skips failing tests)"
	@echo "                  Use TEST_PATH=path/to/test to run specific tests"
	@echo "                  Use TEST_MARKERS=\"\" to clear default markers"
	@echo "test-core:        Run only the core tests (migration and integration)"
	@echo "test-full:        Run all tests with full dependencies"
	@echo "test-coverage:    Run tests with coverage report"
	@echo "test-kg:          Run only the knowledge graph creation test"
	@echo "run-server:       Run the MCP Agile Flow server"
	@echo "setup-cursor:     Set up Cursor MCP integration"
	@echo "clean:            Remove build artifacts and cache files"
	@echo "clean-all:        Remove build artifacts, cache files, and virtual environment"
	@echo "quality:          Run all code quality checks (formatting, linting, type checking)"
	@echo "all:              Install and run tests"

# Virtual environment
# ------------------
venv:
	$(UV) venv $(VENV_DIR) --python=$(shell which python3)

# Installation
# ------------
install: venv
	$(UV) pip install -e .

# Testing
# -------
test: venv
	@echo "Installing development dependencies..."
	$(UV) pip install -e ".[test]"
	$(UV) pip install -e .
	@echo "Running tests with debug output..."
	$(UV) run pytest $(PYTEST_FLAGS) -s --show-capture=all --tb=short $(TEST_MARKERS) $(TEST_PATH)

test-coverage: venv
	@echo "Installing development dependencies..."
	$(UV) pip install -e ".[test]"
	$(UV) pip install -e .
	@echo "Running tests with coverage..."
	$(UV) run pytest $(PYTEST_FLAGS) --cov=$(PACKAGE_NAME) --cov-report=term --cov-report=html $(TESTS_DIR)

test-kg: venv
	@echo "Installing development dependencies..."
	$(UV) pip install -e ".[test]"
	$(UV) pip install -e .
	@echo "Running knowledge graph test..."
	$(UV) run python -c "from tests.test_mcp_via_agno_agent import test_fastapi_project_knowledge_graph; test_fastapi_project_knowledge_graph()"

test-core: venv
	@echo "Installing development dependencies..."
	$(UV) pip install -e ".[test]"
	$(UV) pip install -e .
	@echo "Running core tests only (migration and integration)..."
	$(UV) run pytest $(PYTEST_FLAGS) -s --show-capture=all --tb=short tests/test_mcp_config_migration.py tests/test_integration.py::test_server_imports tests/test_integration.py::test_get_project_settings_tool tests/test_integration.py::test_server_handle_call_tool tests/test_integration.py::test_get_safe_project_path_tool

test-full: venv
	@echo "Installing full development dependencies..."
	$(UV) pip install -e ".[test]"
	$(UV) pip install -e .
	@echo "Installing additional dependencies for FastAPI tests..."
	$(UV) pip install fastapi sqlmodel httpx pytest-cov email-validator pydantic[email]
	@echo "Running all tests with debug output..."
	$(UV) run pytest -v -s --show-capture=all --tb=short --ignore=tests/full-stack-fastapi-sample-project tests

# Server execution
# ---------------
run-server: install
	$(UV) run -m mcp_agile_flow.simple_server

# Setup
# -----
setup-cursor: install
	$(UV) run setup_cursor_mcp.py

# Cleaning
# --------
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf **/__pycache__/
	rm -rf **/.pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/

# Remove everything including the virtual environment
clean-all: clean
	rm -rf $(VENV_DIR)

# Code quality
# ------------
# Combined quality command that runs all checks in one go
quality: venv
	@echo "Installing development dependencies..."
	$(UV) pip install -e ".[test]"
	$(UV) pip install -e .
	@echo "Running code formatting with Black..."
	$(UV) run black $(SOURCE_DIR) $(TESTS_DIR)
	@echo "Running code linting with Flake8..."
	$(UV) run flake8 $(SOURCE_DIR) $(TESTS_DIR)
	@echo "Running type checking with MyPy..."
	$(UV) run mypy $(SOURCE_DIR)

# Default target
# --------------
all: install test
