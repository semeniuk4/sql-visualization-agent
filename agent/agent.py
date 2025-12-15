import os
from google.adk.agents import Agent
from google.adk.planners.built_in_planner import BuiltInPlanner
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams, StreamableHTTPConnectionParams
from google.genai.types import ThinkingConfig
from google.auth import compute_engine
import google.auth.transport.requests
import google.oauth2.id_token
from agent.prompts.root_agent_prompt import root_instructions
from agent.visualization_tools import (
    create_bar_chart,
    create_line_chart,
    create_pie_chart,
    create_heatmap,
    create_scatter_plot,
    create_histogram,
    create_box_plot
)
import vertexai
from vertexai import agent_engines
from vertexai.preview import reasoning_engines

# Replace this URL with the correct endpoint for your MCP server.
MCP_SERVER_URL = "http://127.0.0.1:5000/mcp"
if not MCP_SERVER_URL:
    raise ValueError("The MCP_SERVER_URL is not set.")


root_agent = Agent(
    model='gemini-2.5-flash',
    name='data_analyzer_agent',
    description='Expert agent for analyzing Olist E-commerce database with SQL queries, data insights, and advanced visualizations.',
    instruction=root_instructions,
    planner=BuiltInPlanner(
  thinking_config=ThinkingConfig(include_thoughts=False, thinking_budget=0)
    ),
    tools=[
        MCPToolset(
        connection_params=StreamableHTTPConnectionParams(
        url=MCP_SERVER_URL
        ),
        errlog=None,
        # Load all tools from the MCP server at the given URL
        tool_filter=None,
        ),
        # Add visualization tools
        create_bar_chart,
        create_line_chart,
        create_pie_chart,
        create_heatmap,
        create_scatter_plot,
        create_histogram,
        create_box_plot
     ],
)

