'''
Task management tools for Vikunja MCP server.

This module implements MCP tools for complete task lifecycle management:
create, read, update, delete, and list operations with filtering.
'''

from typing import Dict, Any
import json
from src.client.vikunja_client import VikunjaClient
from src.schemas.task_schemas import (
    CreateTaskInput,
    GetTaskInput,
    ListTasksInput,
    UpdateTaskInput,
    DeleteTaskInput,
    ResponseFormat,
    DetailLevel
)
from src.utils.errors import handle_api_error
from src.utils.formatters import (
    format_task_markdown,
    format_tasks_list_markdown,
    format_json_response,
    truncate_response
)
from src.utils.pagination import build_pagination_response


# Global client instance (will be initialized in server.py)
_client: VikunjaClient = None


def set_client(client: VikunjaClient):
    '''Set the global Vikunja client instance.'''
    global _client
    _client = client


async def vikunja_create_task(params: CreateTaskInput) -> str:
    '''
    Create a new task in Vikunja.

    This tool creates a task in a specified project with title, description,
    priority, and due date. All parameters are validated before submission.

    Args:
        params (CreateTaskInput): Validated input parameters containing:
            - project_id (int): ID of the project/list (required, get with vikunja_list_projects)
            - title (str): Task title (required, 1-500 chars)
            - description (Optional[str]): Detailed description in Markdown
            - priority (Optional[int]): Priority 0-5 (0=None, 1=Low, 2=Medium, 3=High, 4=Urgent, 5=DO NOW)
            - due_date (Optional[str]): Due date in ISO 8601 format
            - start_date (Optional[str]): Start date in ISO 8601 format
            - end_date (Optional[str]): End date in ISO 8601 format

    Returns:
        str: JSON-formatted response with created task details including:
            {
                "id": int,              # New task ID
                "title": str,           # Task title
                "description": str,     # Task description
                "done": bool,           # Completion status (false for new tasks)
                "priority": int,        # Priority level
                "due_date": str,        # Due date (if set)
                "project_id": int,      # Parent project ID
                "created": str,         # Creation timestamp
                "updated": str          # Last update timestamp
            }

        Error response:
            "Error: <error message>" with actionable guidance

    Examples:
        - Create simple task: params with project_id=5, title="Review PR"
        - Create with details: params with project_id=5, title="Deploy v2.0", description="Steps:\n1. Test\n2. Deploy", priority=4, due_date="2025-12-31T23:59:59Z"
        - Don't use when: You want to list existing tasks (use vikunja_list_tasks)
        - Don't use when: You want to update a task (use vikunja_update_task)

    Error Handling:
        - Validation errors handled by Pydantic model
        - Returns "Error: Invalid or expired authentication token" for auth issues (401)
        - Returns "Error: Resource not found" if project_id doesn't exist (404)
        - Returns "Error: Validation failed" for invalid data (422)
    '''
    try:
        # Build request payload
        payload: Dict[str, Any] = {
            "title": params.title,
            "description": params.description or "",
            "priority": params.priority.value if params.priority else 0
        }

        # Add optional date fields
        if params.due_date:
            payload["due_date"] = params.due_date
        if params.start_date:
            payload["start_date"] = params.start_date
        if params.end_date:
            payload["end_date"] = params.end_date

        # Make API request
        response = await _client.request(
            "PUT",
            f"projects/{params.project_id}/tasks",
            json_data=payload
        )

        return format_json_response(response)

    except Exception as e:
        return handle_api_error(e)


async def vikunja_get_task(params: GetTaskInput) -> str:
    '''
    Retrieve a single task by ID.

    This tool fetches complete details for a specific task, including title,
    description, priority, due date, labels, assignees, and timestamps.

    Args:
        params (GetTaskInput): Validated input parameters containing:
            - task_id (int): ID of the task to retrieve (required)
            - response_format (str): Output format 'markdown' or 'json' (default: markdown)

    Returns:
        str: Task details in requested format

        Markdown format:
            ## ○ Task Title (#123)

            Task description here

            - **Project**: 5
            - **Priority**: High
            - **Due**: 2025-12-31 23:59:59 UTC
            - **Labels**: `bug`, `urgent`
            - **Created**: 2025-12-16 10:00:00 UTC

        JSON format:
            {
                "id": 123,
                "title": "Task Title",
                "description": "Task description",
                "done": false,
                "priority": 3,
                "due_date": "2025-12-31T23:59:59Z",
                "project_id": 5,
                "labels": [...],
                "assignees": [...],
                "created": "2025-12-16T10:00:00Z",
                "updated": "2025-12-16T14:30:00Z"
            }

        Error response:
            "Error: Resource not found. Please check the ID is correct and try listing available resources first."

    Examples:
        - Get task details: params with task_id=123, response_format="markdown"
        - Get for processing: params with task_id=123, response_format="json"
        - Don't use when: You want to list multiple tasks (use vikunja_list_tasks)
        - Don't use when: You want to create a task (use vikunja_create_task)

    Error Handling:
        - Returns "Error: Resource not found" if task_id doesn't exist (404)
        - Returns "Error: Invalid or expired authentication token" for auth issues (401)
    '''
    try:
        # Make API request
        response = await _client.request(
            "GET",
            f"tasks/{params.task_id}"
        )

        # Format based on requested format
        if params.response_format == ResponseFormat.MARKDOWN:
            return format_task_markdown(response, detailed=True)
        else:
            return format_json_response(response)

    except Exception as e:
        return handle_api_error(e)


async def vikunja_list_tasks(params: ListTasksInput) -> str:
    '''
    List tasks with filtering, sorting, and pagination.

    This tool retrieves tasks with support for filtering by project, completion
    status, priority, and sorting. Includes pagination for large result sets.

    Args:
        params (ListTasksInput): Validated input parameters containing:
            - project_id (Optional[int]): Filter by project (null = all projects)
            - filter_done (Optional[bool]): Filter by completion (null = all)
            - filter_priority (Optional[int]): Minimum priority level (0-5)
            - sort_by (str): Sort field (id, title, priority, due_date, created, updated)
            - sort_order (str): Sort order (asc, desc)
            - limit (int): Max results per page (1-100, default: 20)
            - offset (int): Pagination offset (default: 0)
            - response_format (str): Output format (markdown, json)
            - detail_level (str): Detail level (concise, detailed)

    Returns:
        str: List of tasks in requested format with pagination metadata

        Markdown concise format:
            # Tasks (20 of 150)

            - ○ **#123**: Complete documentation 🟠
            - ✓ **#124**: Fix login bug
            - ○ **#125**: Deploy v2.0 🔴

            *Showing tasks 1-20 of 150. Use offset=20 to see more.*

        Markdown detailed format:
            # Tasks (20 of 150)

            ## ○ Complete documentation (#123)

            Full task description here

            - **Project**: 5
            - **Priority**: High
            - **Due**: 2025-12-31 23:59:59 UTC
            ...

        JSON format:
            {
                "total": 150,
                "count": 20,
                "limit": 20,
                "offset": 0,
                "has_more": true,
                "next_offset": 20,
                "tasks": [...]
            }

        Error response:
            "Error: <error message>"

    Examples:
        - List all tasks: params with defaults
        - List project tasks: params with project_id=5
        - List incomplete high-priority: params with filter_done=false, filter_priority=3
        - Paginate results: params with limit=50, offset=0 (then offset=50, etc.)
        - Don't use when: You know the task ID (use vikunja_get_task instead)
        - Don't use when: You want to create a task (use vikunja_create_task)

    Error Handling:
        - Returns "Error: Resource not found" if project_id doesn't exist (404)
        - Automatically truncates responses exceeding 25,000 characters with guidance
        - Returns "Error: Invalid request data" for invalid filter/sort parameters (422)
    '''
    try:
        # Build query parameters
        query_params: Dict[str, Any] = {
            "filter_by": [],
            "filter_value": [],
            "filter_comparator": [],
            "filter_concat": "and",
            "sort_by": [params.sort_by],
            "order_by": [params.sort_order],
            "per_page": params.limit,
            "page": (params.offset // params.limit) + 1  # Vikunja uses 1-indexed pages
        }

        # Add filters
        if params.filter_done is not None:
            query_params["filter_by"].append("done")
            query_params["filter_value"].append(str(params.filter_done).lower())
            query_params["filter_comparator"].append("equals")

        if params.filter_priority is not None:
            query_params["filter_by"].append("priority")
            query_params["filter_value"].append(str(params.filter_priority.value))
            query_params["filter_comparator"].append("greater_equals")

        # Determine endpoint based on project filter
        if params.project_id:
            endpoint = f"projects/{params.project_id}/tasks"
        else:
            endpoint = "tasks/all"

        # Make API request
        response = await _client.request(
            "GET",
            endpoint,
            params=query_params
        )

        # Extract tasks and total (Vikunja returns array directly for /tasks/all)
        if isinstance(response, list):
            tasks = response
            total = len(tasks)  # Approximate, Vikunja doesn't provide total for /tasks/all
        else:
            tasks = response.get("tasks", response if isinstance(response, list) else [])
            total = response.get("total", len(tasks))

        # Format based on requested format
        if params.response_format == ResponseFormat.MARKDOWN:
            detailed = (params.detail_level == DetailLevel.DETAILED)
            result = format_tasks_list_markdown(tasks, total, params.offset, detailed)
            return truncate_response(result)
        else:
            # JSON format with pagination metadata
            pagination = build_pagination_response(tasks, total, params.limit, params.offset)
            result = format_json_response({
                **pagination,
                "tasks": tasks
            })
            return truncate_response(result)

    except Exception as e:
        return handle_api_error(e)


async def vikunja_update_task(params: UpdateTaskInput) -> str:
    '''
    Update an existing task (PATCH operation).

    This tool updates specific fields of a task without affecting other fields.
    Only provide the fields you want to change.

    Args:
        params (UpdateTaskInput): Validated input parameters containing:
            - task_id (int): ID of the task to update (required)
            - title (Optional[str]): New title (only if changing)
            - description (Optional[str]): New description (only if changing)
            - done (Optional[bool]): Mark done (true) or not done (false)
            - priority (Optional[int]): New priority (0-5, only if changing)
            - due_date (Optional[str]): New due date in ISO 8601 format

    Returns:
        str: JSON-formatted response with updated task details

        Success response:
            {
                "id": 123,
                "title": "Updated title",
                "done": true,
                "priority": 4,
                ...
            }

        Error response:
            "Error: <error message>"

    Examples:
        - Mark task done: params with task_id=123, done=true
        - Update priority: params with task_id=123, priority=4
        - Update multiple fields: params with task_id=123, title="New title", done=true, priority=3
        - Don't use when: You want to create a new task (use vikunja_create_task)
        - Don't use when: You just need to view the task (use vikunja_get_task)

    Error Handling:
        - Returns "Error: Resource not found" if task_id doesn't exist (404)
        - Returns "Error: Validation failed" for invalid data (422)
        - Returns "Error: Permission denied" if you can't edit this task (403)
    '''
    try:
        # Build request payload (only include fields that were provided)
        payload: Dict[str, Any] = {}

        if params.title is not None:
            payload["title"] = params.title
        if params.description is not None:
            payload["description"] = params.description
        if params.done is not None:
            payload["done"] = params.done
        if params.priority is not None:
            payload["priority"] = params.priority.value
        if params.due_date is not None:
            payload["due_date"] = params.due_date

        # Make API request (POST for Vikunja task update, acts like PATCH)
        response = await _client.request(
            "POST",
            f"tasks/{params.task_id}",
            json_data=payload
        )

        return format_json_response(response)

    except Exception as e:
        return handle_api_error(e)


async def vikunja_delete_task(params: DeleteTaskInput) -> str:
    '''
    Delete a task permanently.

    This tool deletes a task from Vikunja. This operation is destructive and
    cannot be undone. The task and all its data will be permanently removed.

    Args:
        params (DeleteTaskInput): Validated input parameters containing:
            - task_id (int): ID of the task to delete (required)

    Returns:
        str: Success confirmation message

        Success response:
            "Task #123 has been successfully deleted."

        Error response:
            "Error: <error message>"

    Examples:
        - Delete task: params with task_id=123
        - Don't use when: You want to mark a task as done (use vikunja_update_task with done=true)
        - Don't use when: You're not sure which task to delete (use vikunja_get_task first to confirm)

    Error Handling:
        - Returns "Error: Resource not found" if task_id doesn't exist (404)
        - Returns "Error: Permission denied" if you can't delete this task (403)
    '''
    try:
        # Make API request
        await _client.request(
            "DELETE",
            f"tasks/{params.task_id}"
        )

        return f"Task #{params.task_id} has been successfully deleted."

    except Exception as e:
        return handle_api_error(e)
