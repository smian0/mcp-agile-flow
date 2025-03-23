"""
Pytest configuration file.

This file configures logging and other test settings that apply to all tests.
"""

import logging
import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

# Load environment variables from .env.test
load_dotenv(".env.test")

# Add the project root to the Python path to ensure imports work correctly
sys.path.insert(0, str(Path(__file__).parent.parent))


# Configure logging for all tests
@pytest.fixture(autouse=True)
def setup_logging():
    """
    Configure logging for all tests.

    This fixture runs automatically for all tests and sets up logging with:
    - Format from LOG_FORMAT environment variable
    - Level from LOG_LEVEL environment variable
    - Console output
    """
    # Get configuration from environment variables
    log_level = os.getenv("LOG_LEVEL", "DEBUG")
    log_format = os.getenv(
        "LOG_FORMAT",
        "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s",
    )

    # Create a formatter with the configured format
    formatter = logging.Formatter(log_format)

    # Create handlers
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Remove any existing handlers and add our configured one
    root_logger.handlers = []
    root_logger.addHandler(console_handler)

    yield  # This allows the test to run

    # Cleanup (optional)
    root_logger.handlers = []


@pytest.fixture(autouse=True)
def clean_notes():
    """Reset the notes dictionary before and after each test."""
    # Mock notes instead of importing from simple_server
    notes = {}
    notes.clear()

    yield

    # Clear notes after test
    notes.clear()
