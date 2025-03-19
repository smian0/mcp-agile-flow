#!/usr/bin/env python3
# /// script
# dependencies = [
#   "ollama",
#   "agno",
#   "openai",
#   "python-dotenv",
#   "yfinance",
#   "duckduckgo-search",
#   "rich",
#   "mcp",
# ]
# ///

import os
import sys
import asyncio
from textwrap import dedent

from agno.agent import Agent
from agno.tools.mcp import MCPTools
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from agno.models.lmstudio import LMStudio
from agno.utils.pprint import pprint_run_response
from rich.pretty import pprint

async def run_github_agent(message):
   

    try:
        server_params = StdioServerParameters(
            command="/Users/smian/development/mcp-agile-flow/.venv/bin/python",
            args=["-m", "mcp_agile_flow"],
            env={"PROJECT_PATH": "/Users/smian/development/mcp-agile-flow/tests/test_outputs"}
        )

        # Create client session
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize MCP toolkit
                mcp_tools = MCPTools(session=session)
                await mcp_tools.initialize()

                # Create agent
                agent = Agent(
                    model=LMStudio(
                        id="mistral-small-3.1-24b-instruct-2503",
                        base_url="https://finwiz-lmstudio-22.localcan.dev/v1",
                        api_key="sk-lmstudio-1a2efea8c59dc9bc11eb6c9692e20737"
                    ),
                    tools=[mcp_tools],
                    instructions=dedent("""\
                        You are an AI coding assistant.
                    """),
                    markdown=True,
                    show_tool_calls=True,
                    debug_mode=True
                )

                # Run agent
                response = await agent.arun(message)
                return response.content
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    # Check if a command line argument was provided
    
    result = asyncio.run(run_github_agent("What is your agile flow project setting?"))
    # result = asyncio.run(run_github_agent("What is your IDE?"))
    # result = asyncio.run(run_github_agent("initialize rules"))
    # result = asyncio.run(run_github_agent("initialize rules for cline"))
    print(result)
