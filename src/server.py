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
from src.utils.openbao_secrets import is_agent_available, DEV_MODE

# Import schemas
from src.schemas.task_schemas import (
    CreateTaskInput,
    GetTaskInput,
    ListTasksInput,
    UpdateTaskInput,
    DeleteTaskInput
)
from src.schemas.project_schemas import (
    CreateProjectInput,
    ListProjectsInput,
    UpdateProjectInput,
    DeleteProjectInput,
    GetProjectTasksInput,
    MoveTaskInput,
    CreateLabelInput,
    ListLabelsInput,
    DeleteLabelInput,
    AddLabelToTaskInput,
    RemoveLabelFromTaskInput,
    GetTasksByLabelInput
)
from src.schemas.advanced_schemas import (
    AddReminderInput,
    ListRemindersInput,
    DeleteReminderInput,
    CreateRelationInput,
    GetRelationsInput,
    DeleteRelationInput,
    ListTeamsInput,
    GetTeamMembersInput,
    AssignTaskInput,
    ShareProjectInput
)

# Import tools
from src.tools import tasks, projects, labels, advanced


# Initialize MCP server
mcp = FastMCP("vikunja_mcp")

# Global client instance
_client: VikunjiaClient = None


@asynccontextmanager
async def lifespan(app):
    '''
    Manage server lifespan - initialize and cleanup resources.

    This context manager sets up the Vikunja API client on server startup
    and ensures proper cleanup on shutdown.
    '''
    global _client

    # Initialize Vikunja client
    _client = VikunjiaClient()
    tasks.set_client(_client)
    projects.set_client(_client)
    labels.set_client(_client)
    advanced.set_client(_client)

    # Determine credential source for logging
    if is_agent_available():
        cred_source = "OpenBao Agent"
    elif DEV_MODE:
        cred_source = "Environment Variables [DEV MODE]"
    else:
        cred_source = "OpenBao Agent (REQUIRED)"

    print(f"✓ Vikunja MCP server initialized")
    print(f"  URL: {_client.base_url}")
    print(f"  API: {_client.api_base}")
    print(f"  Credentials: {cred_source}")
    if DEV_MODE:
        print(f"  WARNING: Dev mode enabled - env var fallback allowed")

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
# PROJECT MANAGEMENT TOOLS
# ============================================================================

@mcp.tool(
    name="vikunja_create_project",
    annotations={
        "title": "Create Vikunja Project",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True
    }
)
async def create_project(params: CreateProjectInput) -> str:
    '''Create a new project/list in Vikunja with title, description, color, and optional hierarchy.'''
    return await projects.vikunja_create_project(params)


@mcp.tool(
    name="vikunja_list_projects",
    annotations={
        "title": "List Vikunja Projects",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def list_projects(params: ListProjectsInput) -> str:
    '''List all projects/lists accessible to the authenticated user.'''
    return await projects.vikunja_list_projects(params)


@mcp.tool(
    name="vikunja_update_project",
    annotations={
        "title": "Update Vikunja Project",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def update_project(params: UpdateProjectInput) -> str:
    '''Update existing project fields (title, description, color). PATCH operation.'''
    return await projects.vikunja_update_project(params)


@mcp.tool(
    name="vikunja_delete_project",
    annotations={
        "title": "Delete Vikunja Project",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def delete_project(params: DeleteProjectInput) -> str:
    '''Delete a project and all its tasks permanently. This operation cannot be undone.'''
    return await projects.vikunja_delete_project(params)


@mcp.tool(
    name="vikunja_get_project_tasks",
    annotations={
        "title": "Get Project Tasks",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def get_project_tasks(params: GetProjectTasksInput) -> str:
    '''List all tasks in a specific project with pagination.'''
    return await projects.vikunja_get_project_tasks(params)


@mcp.tool(
    name="vikunja_move_task_to_project",
    annotations={
        "title": "Move Task to Project",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def move_task_to_project(params: MoveTaskInput) -> str:
    '''Move a task to a different project.'''
    return await projects.vikunja_move_task_to_project(params)


# ============================================================================
# LABEL MANAGEMENT TOOLS
# ============================================================================

@mcp.tool(
    name="vikunja_create_label",
    annotations={
        "title": "Create Vikunja Label",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True
    }
)
async def create_label(params: CreateLabelInput) -> str:
    '''Create a new label with title, description, and color for task categorization.'''
    return await labels.vikunja_create_label(params)


@mcp.tool(
    name="vikunja_list_labels",
    annotations={
        "title": "List Vikunja Labels",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def list_labels(params: ListLabelsInput) -> str:
    '''List all labels available in the Vikunja instance.'''
    return await labels.vikunja_list_labels(params)


@mcp.tool(
    name="vikunja_delete_label",
    annotations={
        "title": "Delete Vikunja Label",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def delete_label(params: DeleteLabelInput) -> str:
    '''Delete a label permanently and remove it from all tasks. This operation cannot be undone.'''
    return await labels.vikunja_delete_label(params)


@mcp.tool(
    name="vikunja_add_label_to_task",
    annotations={
        "title": "Add Label to Task",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def add_label_to_task(params: AddLabelToTaskInput) -> str:
    '''Apply an existing label to a task for categorization.'''
    return await labels.vikunja_add_label_to_task(params)


@mcp.tool(
    name="vikunja_remove_label_from_task",
    annotations={
        "title": "Remove Label from Task",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def remove_label_from_task(params: RemoveLabelFromTaskInput) -> str:
    '''Remove a label from a task.'''
    return await labels.vikunja_remove_label_from_task(params)


@mcp.tool(
    name="vikunja_get_tasks_by_label",
    annotations={
        "title": "Get Tasks by Label",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def get_tasks_by_label(params: GetTasksByLabelInput) -> str:
    '''Filter tasks by label with pagination support.'''
    return await labels.vikunja_get_tasks_by_label(params)


# ============================================================================
# REMINDER TOOLS
# ============================================================================

@mcp.tool(
    name="vikunja_add_reminder",
    annotations={
        "title": "Add Task Reminder",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True
    }
)
async def add_reminder(params: AddReminderInput) -> str:
    '''Add a time-based reminder to a task.'''
    return await advanced.vikunja_add_reminder(params)


@mcp.tool(
    name="vikunja_list_reminders",
    annotations={
        "title": "List Task Reminders",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def list_reminders(params: ListRemindersInput) -> str:
    '''List all reminders set for a specific task.'''
    return await advanced.vikunja_list_reminders(params)


@mcp.tool(
    name="vikunja_delete_reminder",
    annotations={
        "title": "Delete Task Reminder",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def delete_reminder(params: DeleteReminderInput) -> str:
    '''Delete a reminder from a task.'''
    return await advanced.vikunja_delete_reminder(params)


# ============================================================================
# TASK RELATIONSHIP TOOLS
# ============================================================================

@mcp.tool(
    name="vikunja_create_relation",
    annotations={
        "title": "Create Task Relationship",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True
    }
)
async def create_relation(params: CreateRelationInput) -> str:
    '''Create a relationship between two tasks (subtask, parent, blocking, related, etc.).'''
    return await advanced.vikunja_create_relation(params)


@mcp.tool(
    name="vikunja_get_relations",
    annotations={
        "title": "Get Task Relationships",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def get_relations(params: GetRelationsInput) -> str:
    '''Get all relationships for a task.'''
    return await advanced.vikunja_get_relations(params)


@mcp.tool(
    name="vikunja_delete_relation",
    annotations={
        "title": "Delete Task Relationship",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def delete_relation(params: DeleteRelationInput) -> str:
    '''Delete a relationship between two tasks.'''
    return await advanced.vikunja_delete_relation(params)


# ============================================================================
# TEAM COLLABORATION TOOLS
# ============================================================================

@mcp.tool(
    name="vikunja_list_teams",
    annotations={
        "title": "List Teams",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def list_teams(params: ListTeamsInput) -> str:
    '''List all teams accessible to the authenticated user.'''
    return await advanced.vikunja_list_teams(params)


@mcp.tool(
    name="vikunja_get_team_members",
    annotations={
        "title": "Get Team Members",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def get_team_members(params: GetTeamMembersInput) -> str:
    '''Get all members of a specific team.'''
    return await advanced.vikunja_get_team_members(params)


@mcp.tool(
    name="vikunja_assign_task",
    annotations={
        "title": "Assign Task to User",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def assign_task(params: AssignTaskInput) -> str:
    '''Assign a task to a user.'''
    return await advanced.vikunja_assign_task(params)


@mcp.tool(
    name="vikunja_share_project",
    annotations={
        "title": "Share Project with Team",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def share_project(params: ShareProjectInput) -> str:
    '''Share a project with a team with specified permission level (read, read+write, admin).'''
    return await advanced.vikunja_share_project(params)


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
