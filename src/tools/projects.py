'''
Project management tools for Vikunja MCP server.

This module implements MCP tools for project/list CRUD operations
and project-task relationships.
'''

from typing import Dict, Any
from src.client.vikunja_client import VikunjaClient
from src.schemas.project_schemas import (
    CreateProjectInput,
    ListProjectsInput,
    UpdateProjectInput,
    DeleteProjectInput,
    GetProjectTasksInput,
    MoveTaskInput,
    ResponseFormat
)
from src.utils.errors import handle_api_error
from src.utils.formatters import (
    format_project_markdown,
    format_tasks_list_markdown,
    format_json_response,
    truncate_response
)
from src.utils.pagination import build_pagination_response


# Global client instance
_client: VikunjaClient = None


def set_client(client: VikunjaClient):
    '''Set the global Vikunja client instance.'''
    global _client
    _client = client


async def vikunja_create_project(params: CreateProjectInput) -> str:
    '''
    Create a new project/list in Vikunja.

    Projects (also called "lists" in Vikunja) are containers for organizing tasks.
    They can be nested to create hierarchies.

    Args:
        params (CreateProjectInput): Validated input containing:
            - title (str): Project name (required, 1-250 chars)
            - description (Optional[str]): Project description
            - hex_color (Optional[str]): Color in hex format (e.g., '#FF5733')
            - parent_project_id (Optional[int]): Parent project for hierarchy

    Returns:
        str: JSON response with created project details

    Examples:
        - Create simple project: params with title="Work Projects"
        - Create with color: params with title="Personal", hex_color="#3498DB"
        - Create nested: params with title="Q1 Goals", parent_project_id=5
    '''
    try:
        payload: Dict[str, Any] = {
            "title": params.title,
            "description": params.description or ""
        }

        if params.hex_color:
            payload["hex_color"] = params.hex_color
        if params.parent_project_id:
            payload["parent_project_id"] = params.parent_project_id

        response = await _client.request("PUT", "projects", json_data=payload)
        return format_json_response(response)

    except Exception as e:
        return handle_api_error(e)


async def vikunja_list_projects(params: ListProjectsInput) -> str:
    '''
    List all projects/lists.

    Retrieves all projects accessible to the authenticated user, including
    nested projects and their hierarchies.

    Args:
        params (ListProjectsInput): Validated input containing:
            - response_format (str): 'markdown' or 'json' (default: markdown)

    Returns:
        str: List of projects in requested format

    Examples:
        - List all projects: params with response_format="markdown"
        - Get for processing: params with response_format="json"
    '''
    try:
        response = await _client.request("GET", "projects")

        if params.response_format == ResponseFormat.MARKDOWN:
            projects = response if isinstance(response, list) else []
            lines = [f"# Projects ({len(projects)})", ""]

            if not projects:
                return "No projects found."

            for project in projects:
                lines.append(format_project_markdown(project, detailed=False))
                lines.append("")

            return truncate_response("\n".join(lines))
        else:
            return format_json_response(response)

    except Exception as e:
        return handle_api_error(e)


async def vikunja_update_project(params: UpdateProjectInput) -> str:
    '''
    Update an existing project.

    Updates specific fields of a project. Only provide fields you want to change.

    Args:
        params (UpdateProjectInput): Validated input containing:
            - project_id (int): ID of project to update (required)
            - title (Optional[str]): New title
            - description (Optional[str]): New description
            - hex_color (Optional[str]): New color

    Returns:
        str: JSON response with updated project details

    Examples:
        - Rename project: params with project_id=5, title="New Name"
        - Change color: params with project_id=5, hex_color="#FF5733"
    '''
    try:
        payload: Dict[str, Any] = {}

        if params.title is not None:
            payload["title"] = params.title
        if params.description is not None:
            payload["description"] = params.description
        if params.hex_color is not None:
            payload["hex_color"] = params.hex_color

        response = await _client.request(
            "POST",
            f"projects/{params.project_id}",
            json_data=payload
        )
        return format_json_response(response)

    except Exception as e:
        return handle_api_error(e)


async def vikunja_delete_project(params: DeleteProjectInput) -> str:
    '''
    Delete a project permanently.

    Deletes a project and all its tasks. This operation is destructive and
    cannot be undone.

    Args:
        params (DeleteProjectInput): Validated input containing:
            - project_id (int): ID of project to delete (required)

    Returns:
        str: Success confirmation message

    Examples:
        - Delete project: params with project_id=5
    '''
    try:
        await _client.request("DELETE", f"projects/{params.project_id}")
        return f"Project #{params.project_id} has been successfully deleted."

    except Exception as e:
        return handle_api_error(e)


async def vikunja_get_project_tasks(params: GetProjectTasksInput) -> str:
    '''
    List all tasks in a specific project.

    Retrieves tasks belonging to a project with pagination support.

    Args:
        params (GetProjectTasksInput): Validated input containing:
            - project_id (int): ID of project (required)
            - limit (int): Max results (1-100, default: 20)
            - offset (int): Pagination offset (default: 0)
            - response_format (str): 'markdown' or 'json'

    Returns:
        str: List of tasks with pagination metadata

    Examples:
        - List project tasks: params with project_id=5
        - Paginate: params with project_id=5, limit=50, offset=0
    '''
    try:
        # Calculate page number (Vikunja uses 1-indexed pages)
        page = (params.offset // params.limit) + 1

        response = await _client.request(
            "GET",
            f"projects/{params.project_id}/tasks",
            params={"per_page": params.limit, "page": page}
        )

        tasks = response if isinstance(response, list) else []
        total = len(tasks)

        if params.response_format == ResponseFormat.MARKDOWN:
            result = format_tasks_list_markdown(tasks, total, params.offset, detailed=False)
            return truncate_response(result)
        else:
            pagination = build_pagination_response(tasks, total, params.limit, params.offset)
            return format_json_response({**pagination, "tasks": tasks})

    except Exception as e:
        return handle_api_error(e)


async def vikunja_move_task_to_project(params: MoveTaskInput) -> str:
    '''
    Move a task to a different project.

    Relocates a task from its current project to a target project.

    Args:
        params (MoveTaskInput): Validated input containing:
            - task_id (int): ID of task to move (required)
            - target_project_id (int): Destination project ID (required)

    Returns:
        str: JSON response with updated task details

    Examples:
        - Move task: params with task_id=123, target_project_id=5
    '''
    try:
        response = await _client.request(
            "POST",
            f"tasks/{params.task_id}",
            json_data={"project_id": params.target_project_id}
        )
        return format_json_response(response)

    except Exception as e:
        return handle_api_error(e)
