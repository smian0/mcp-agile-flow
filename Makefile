# MCP Agile Flow - Makefile
# -------------------------

.PHONY: help venv install test test-coverage coverage test-kg test-core test-nl-commands test-full test-agent test-via-agent run-server setup-cursor clean clean-all clean-archived quality format lint type-check fix-lint setup-quality all

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
TEST_MARKERS ?= --ignore=tests/full-stack-fastapi-sample-project --ignore=tests/test_mcp_via_agno_agent.py

# Help target
# -----------
help:
	@echo "MCP Agile Flow - Make Targets"
	@echo "---------------------------"
	@echo "help:             Show this help message"
	@echo "venv:             Create virtual environment"
	@echo "install:          Install package"
	@echo "test:             Run tests with detailed debug output (excludes agent tests)"
	@echo "                  Use TEST_PATH=path/to/test to run specific tests"
	@echo "                  Use TEST_MARKERS=\"\" to clear default markers"
	@echo "test-coverage:    Run tests with coverage report (basic)"
	@echo "coverage:         Run tests with detailed coverage reports and badge generation"
	@echo "test-core:        Run only the core tests (migration and integration)"
	@echo "test-nl-commands: Run only the natural language command detection tests"
	@echo "test-agent:       Run only the agent tests (test_mcp_via_agno_agent.py)"
	@echo "test-via-agent:   Run only the tests that use an AI agent for testing"
	@echo "test-full:        Run all tests with full dependencies"
	@echo "test-kg:          Run only the knowledge graph creation test"
	@echo "run-server:       Run the MCP Agile Flow server"
	@echo "setup-cursor:     Set up Cursor MCP integration"
	@echo "setup-quality:    Set up quality tools (formatting, linting, type checking)"
	@echo "clean:            Remove build artifacts and cache files"
	@echo "clean-all:        Remove build artifacts, cache files, and virtual environment"
	@echo "clean-archived:   Remove archived files (creates backup first)"
	@echo "quality:          Run all code quality checks (formatting, linting, type checking)"
	@echo "dead-code:        Run dead code analysis and generate reports"
	@echo "format:           Run code formatting with Black"
	@echo "lint:             Run code linting with Ruff and Flake8"
	@echo "type-check:       Run type checking with MyPy"
	@echo "fix-lint:         Automatically fix linting issues with Ruff"
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
	@echo "Installing test dependencies..."
	$(UV) pip install -e ".[test]"
	@echo "Running tests with debug output..."
	$(UV) run pytest $(PYTEST_FLAGS) -s --show-capture=all --tb=short $(TEST_MARKERS) $(TEST_PATH)

test-coverage: venv
	@echo "Installing test dependencies..."
	$(UV) pip install -e ".[test]"
	@echo "Running tests with coverage..."
	$(UV) run pytest $(PYTEST_FLAGS) --cov=$(PACKAGE_NAME) --cov-report=term --cov-report=html $(TEST_MARKERS) $(TESTS_DIR)

coverage: venv
	@echo "Installing test and development dependencies..."
	$(UV) pip install -e ".[dev]"
	@echo "Running tests with detailed coverage report..."
	. $(VENV_ACTIVATE) && UV_LINK_MODE=copy coverage run -m pytest $(TEST_MARKERS) $(TESTS_DIR)
	. $(VENV_ACTIVATE) && coverage report -m
	. $(VENV_ACTIVATE) && coverage html
	. $(VENV_ACTIVATE) && coverage xml
	. $(VENV_ACTIVATE) && coverage-badge -o coverage.svg -f
	@echo "Coverage report generated at htmlcov/index.html"
	@echo "Coverage badge generated at coverage.svg"

test-kg: venv
	@echo "Installing test dependencies..."
	$(UV) pip install -e ".[test]"
	@echo "Running knowledge graph test..."
	$(UV) run python -c "from tests.test_mcp_via_agno_agent import test_fastapi_project_knowledge_graph; test_fastapi_project_knowledge_graph()"

# test-agent is an alias for test-via-agent for backward compatibility
test-agent: test-via-agent

test-via-agent: venv
	@echo "Installing test and agent-specific dependencies..."
	$(UV) pip install -e ".[test]"
	$(UV) pip install agno rich openai
	@echo "Running tests via AI agent..."
	$(UV) run pytest $(PYTEST_FLAGS) -s --show-capture=all --tb=short tests/test_mcp_via_agno_agent.py

test-core: venv
	@echo "Installing test dependencies..."
	$(UV) pip install -e ".[test]"
	@echo "Running core tests only (migration and integration)..."
	$(UV) run pytest $(PYTEST_FLAGS) -s --show-capture=all --tb=short tests/test_integration.py::test_get_project_settings tests/test_project_configuration.py::test_get_project_settings_tool tests/test_integration.py::test_get_project_settings_with_path

test-nl-commands: venv
	@echo "Installing test dependencies..."
	$(UV) pip install -e ".[test]"
	@echo "Running natural language command detection tests..."
	$(UV) run pytest $(PYTEST_FLAGS) -s --show-capture=all --tb=short tests/test_nl_commands.py

test-full: venv
	@echo "Installing full development dependencies..."
	$(UV) pip install -e ".[dev]"
	@echo "Installing additional dependencies for FastAPI tests..."
	$(UV) pip install fastapi sqlmodel httpx email-validator pydantic[email]
	@echo "Installing agent dependencies..."
	$(UV) pip install agno rich openai
	@echo "Running all tests with debug output..."
	$(UV) run pytest -v -s --show-capture=all --tb=short --ignore=tests/full-stack-fastapi-sample-project tests

# Server execution
# ---------------
run-server: install
	$(UV) run -m mcp_agile_flow.server

# Setup
# -----
setup-cursor: install
	$(UV) run setup_cursor_mcp.py

setup-quality: venv
	@echo "Installing quality tools..."
	$(UV) pip install -e ".[test]"
	$(UV) pip install black==24.3.0 flake8==7.0.0 mypy==1.9.0 ruff==0.3.0
	@echo "Creating .mypy.ini file if it doesn't exist..."
	@if [ ! -f .mypy.ini ]; then \
		echo "[mypy]\npython_version = 3.10\nwarn_return_any = true\nwarn_unused_configs = true\ndisallow_untyped_defs = false\ndisallow_incomplete_defs = false\nignore_missing_imports = true\n" > .mypy.ini; \
	fi
	@echo "Setup complete. You can now run 'make quality' to check code quality."

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
	rm -rf dead_code_report*

# Remove everything including the virtual environment
clean-all: clean
	rm -rf $(VENV_DIR)

# Remove archived files (with backup)
clean-archived:
	@echo "Running cleanup script for archived files..."
	chmod +x scripts/cleanup_archives.sh && ./scripts/cleanup_archives.sh

# Code quality
# ------------
# Dead code analysis
dead-code: venv
	@echo "Installing dead code analyzer dependencies..."
	$(UV) pip install vulture>=2.14
	@echo "Running dead code analysis with Vulture..."
	$(UV) run python scripts/quality/analyze_dead_code.py --src $(SOURCE_DIR) --output reports/dead_code_report --html --json
	@echo "Dead code reports generated in reports/ directory"

# Combined quality command that runs all checks in one go
quality: venv
	@echo "Installing development dependencies..."
	$(UV) pip install -e ".[test]"
	@echo "Installing quality tools explicitly..."
	$(UV) pip install black==24.3.0 flake8==7.0.0 mypy==1.9.0 ruff==0.3.0 vulture>=2.14
	@echo "Running code formatting with Black..."
	$(UV) run black $(SOURCE_DIR) $(TESTS_DIR)
	@echo "Running code linting with Ruff..."
	$(UV) run ruff check $(SOURCE_DIR) $(TESTS_DIR)
	@echo "Running code linting with Flake8..."
	$(UV) run flake8 $(SOURCE_DIR)
	@echo "Running type checking with MyPy..."
	$(UV) run mypy $(SOURCE_DIR)
	@echo "Running dead code analysis with Vulture..."
	mkdir -p reports
	$(UV) run python scripts/quality/analyze_dead_code.py --src $(SOURCE_DIR) --output reports/dead_code_report --html --json

# Default target
# --------------
all: install test
