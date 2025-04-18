import os
import json
import uuid
import httpx
import random  # <<< Import random module
import sys
from typing import Any
from dotenv import load_dotenv
from dataclasses import dataclass
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from mcp.server.fastmcp import FastMCP, Context

# Import tools and prompts
import tools
from tools import list_agents, get_agent_input_schema, hire_agent, check_job_status, get_job_full_result
from prompts import (
    prompt_list_agents, prompt_get_agent_input_schema, prompt_hire_agent, 
    prompt_check_job_status, prompt_get_job_full_result
)

# --- Configuration ---
load_dotenv()  # Load variables from .env file

# Load base URLs from environment variables
MASUMI_REGISTRY_BASE_URL = os.getenv('MASUMI_REGISTRY_BASE_URL')
MASUMI_PAYMENT_BASE_URL = os.getenv('MASUMI_PAYMENT_BASE_URL')

# Validate required configuration
if not MASUMI_REGISTRY_BASE_URL:
    print("ERROR: MASUMI_REGISTRY_BASE_URL not defined in .env file")
    sys.exit(1)
    
if not MASUMI_PAYMENT_BASE_URL:
    print("ERROR: MASUMI_PAYMENT_BASE_URL not defined in .env file")
    sys.exit(1)

# API paths
REGISTRY_API_PATH = 'api/v1/registry-entry/'
PAYMENT_API_PATH = 'api/v1/purchase/'

# Full URLs - ensure we don't have double slashes
MASUMI_REGISTRY_URL = f"{MASUMI_REGISTRY_BASE_URL.rstrip('/')}/{REGISTRY_API_PATH}"
MASUMI_PAYMENT_URL = f"{MASUMI_PAYMENT_BASE_URL.rstrip('/')}/{PAYMENT_API_PATH}"

# Set URLs in tools module
tools.set_urls(MASUMI_REGISTRY_URL, MASUMI_PAYMENT_URL)

# --- Lifespan Management & Context ---

@dataclass
class MasumiContext:
    """Holds shared resources needed by the server."""
    http_client: httpx.AsyncClient
    registry_token: str
    payment_token: str
    network: str

@asynccontextmanager
async def masumi_lifespan(server: FastMCP) -> AsyncIterator[MasumiContext]:
    """
    Manages the application lifecycle: initialize resources on startup, clean up on shutdown.
    """
    registry_token = os.getenv("MASUMI_REGISTRY_TOKEN")
    payment_token = os.getenv("MASUMI_PAYMENT_TOKEN")
    network = os.getenv("MASUMI_NETWORK", "Preprod") # Default to Preprod

    print("--- Masumi MCP Server Starting ---")
    if not registry_token:
        print("WARNING: MASUMI_REGISTRY_TOKEN not found in .env. Registry features will fail.")
    if not payment_token:
        print("WARNING: MASUMI_PAYMENT_TOKEN not found in .env. Payment features will fail.")
    print(f"Using Masumi Network: {network}")

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            yield MasumiContext(
                http_client=client,
                registry_token=registry_token or "",
                payment_token=payment_token or "",
                network=network
            )
        finally:
            print("--- Masumi MCP Server Shutting Down ---")


# --- MCP Server Initialization ---
mcp = FastMCP(
    "Masumi Agent Manager",
    lifespan=masumi_lifespan,
    dependencies=["httpx", "python-dotenv"]
)

# Register tools
mcp.tool()(list_agents)
mcp.tool()(get_agent_input_schema)
mcp.tool()(hire_agent)
mcp.tool()(check_job_status)
mcp.tool()(get_job_full_result)

# Register prompts
mcp.prompt()(prompt_list_agents)
mcp.prompt()(prompt_get_agent_input_schema)
mcp.prompt()(prompt_hire_agent)
mcp.prompt()(prompt_check_job_status)
mcp.prompt()(prompt_get_job_full_result)

# --- Main Execution ---
if __name__ == "__main__":
    print("Starting Masumi MCP Server...")
    mcp.run()