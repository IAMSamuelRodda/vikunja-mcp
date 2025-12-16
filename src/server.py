#!/usr/bin/env python3
'''
Vikunja MCP Server.

This server provides tools to interact with Vikunja task management API,
including task CRUD, project management, labels, and advanced features.

Usage:
    Development: mcp dev src/server.py
    Production: python src/server.py
'''

import os
import asyncio
from contextlib import asynccontextmanager
from mcp.server.fastmcp import FastMCP, Context

# Import client
from src.client.vikunja_client import VikunjiaClient

# Import schemas
from src.schemas.task_schemas import (
    CreateTaskInput,
    GetTaskInput,
    ListTasksInput,
    UpdateTaskInput,
    DeleteTaskInput
)

# Import tools
from src.tools import tasks


# Initialize MCP server
mcp = FastMCP("vikunja_mcp")

# Global client instance
_client: VikunjiaClient = None


@asynccontextmanager
async def lifespan():
    '''
    Manage server lifespan - initialize and cleanup resources.

    This context manager sets up the Vikunja API client on server startup
    and ensures proper cleanup on shutdown.
    '''
    global _client

    # Initialize Vikunja client
    _client = VikunjiaClient()
    tasks.set_client(_client)

    print(f"✓ Vikunja MCP server initialized")
    print(f"  URL: {_client.base_url}")
    print(f"  API: {_client.api_base}")

    yield {"client": _client}

    # Cleanup on shutdown
    await _client.close()
    print("✓ Vikunja MCP server shutdown complete")


# Apply lifespan management
mcp = FastMCP("vikunja_mcp", lifespan=lifespan)


# ============================================================================
# TASK MANAGEMENT TOOLS
# ============================================================================

@mcp.tool(
    name="vikunja_create_task",
    annotations={
        "title": "Create Vikunja Task",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True
    }
)
async def create_task(params: CreateTaskInput) -> str:
    '''Create a new task in Vikunja with title, description, priority, and due date.'''
    return await tasks.vikunja_create_task(params)


@mcp.tool(
    name="vikunja_get_task",
    annotations={
        "title": "Get Vikunja Task",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def get_task(params: GetTaskInput) -> str:
    '''Retrieve complete details for a specific task by ID.'''
    return await tasks.vikunja_get_task(params)


@mcp.tool(
    name="vikunja_list_tasks",
    annotations={
        "title": "List Vikunja Tasks",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def list_tasks(params: ListTasksInput) -> str:
    '''List tasks with filtering (project, status, priority), sorting, and pagination.'''
    return await tasks.vikunja_list_tasks(params)


@mcp.tool(
    name="vikunja_update_task",
    annotations={
        "title": "Update Vikunja Task",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def update_task(params: UpdateTaskInput) -> str:
    '''Update existing task fields (title, description, done status, priority, due date). PATCH operation.'''
    return await tasks.vikunja_update_task(params)


@mcp.tool(
    name="vikunja_delete_task",
    annotations={
        "title": "Delete Vikunja Task",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def delete_task(params: DeleteTaskInput) -> str:
    '''Delete a task permanently. This operation cannot be undone.'''
    return await tasks.vikunja_delete_task(params)


# ============================================================================
# SERVER ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Load environment variables from .env if available
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass  # dotenv is optional

    # Run the server
    mcp.run()
