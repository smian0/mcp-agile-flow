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
    description="MCP server implementations for agile workflow",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mcp-agile-flow",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "mcp>=0.1.0",
        "aiofiles>=0.8.0",
    ],
    entry_points={
        "console_scripts": [
            "mcp-agile-flow-simple=mcp_agile_flow.simple_server:run",
        ],
    },
) 