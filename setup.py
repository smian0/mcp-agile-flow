#!/usr/bin/env python
"""
Setup script for MCP Agile Flow

This package provides MCP server implementations for agile workflow.
"""

from setuptools import setup, find_packages

setup(
    name="mcp-agile-flow",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="MCP server for managing Cursor rules and templates",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mcp-agile-flow",
    packages=find_packages(),
    package_data={
        "mcp_agile_flow": [
            "cursor_rules/*.mdc",
            "cursor_templates/*.md",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.9",
    install_requires=[
        "mcp-server>=0.1.0",
        "aiohttp>=3.8.0",
        "python-dotenv>=0.19.0",
    ],
    entry_points={
        "console_scripts": [
            "mcp-agile-flow=mcp_agile_flow.simple_server:main",
        ],
    },
) 