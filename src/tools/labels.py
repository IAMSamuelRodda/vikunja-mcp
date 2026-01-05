'''
Label management tools for Vikunja MCP server.

This module implements MCP tools for label CRUD operations and
label-based task filtering.
'''

from typing import Dict, Any
from src.client.vikunja_client import VikunjaClient
from src.schemas.project_schemas import (
    CreateLabelInput,
    ListLabelsInput,
    DeleteLabelInput,
    AddLabelToTaskInput,
    RemoveLabelFromTaskInput,
    GetTasksByLabelInput,
    ResponseFormat
)
from src.utils.errors import handle_api_error
from src.utils.formatters import (
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


async def vikunja_create_label(params: CreateLabelInput) -> str:
    '''
    Create a new label.

    Labels are tags that can be applied to tasks for categorization and filtering.

    Args:
        params (CreateLabelInput): Validated input containing:
            - title (str): Label name (required, 1-100 chars, e.g., 'bug', 'urgent')
            - description (Optional[str]): Label description
            - hex_color (Optional[str]): Color in hex format (default: '#e8e8e8')

    Returns:
        str: JSON response with created label details

    Examples:
        - Create simple label: params with title="bug"
        - Create with color: params with title="urgent", hex_color="#FF0000"
        - Create with description: params with title="feature-request", description="New feature ideas"
    '''
    try:
        payload: Dict[str, Any] = {
            "title": params.title,
            "description": params.description or "",
            "hex_color": params.hex_color
        }

        response = await _client.request("PUT", "labels", json_data=payload)
        return format_json_response(response)

    except Exception as e:
        return handle_api_error(e)


async def vikunja_list_labels(params: ListLabelsInput) -> str:
    '''
    List all labels.

    Retrieves all labels available in the Vikunja instance.

    Args:
        params (ListLabelsInput): Validated input containing:
            - response_format (str): 'markdown' or 'json' (default: markdown)

    Returns:
        str: List of labels in requested format

    Examples:
        - List all labels: params with response_format="markdown"
        - Get for processing: params with response_format="json"
    '''
    try:
        response = await _client.request("GET", "labels")

        if params.response_format == ResponseFormat.MARKDOWN:
            labels = response if isinstance(response, list) else []
            lines = [f"# Labels ({len(labels)})", ""]

            if not labels:
                return "No labels found."

            for label in labels:
                color = label.get('hex_color', '#e8e8e8')
                title = label.get('title', 'Untitled')
                label_id = label.get('id', '?')
                description = label.get('description', '')

                lines.append(f"## {title} (#{label_id})")
                lines.append(f"- **Color**: {color}")
                if description:
                    lines.append(f"- **Description**: {description}")
                lines.append("")

            return truncate_response("\n".join(lines))
        else:
            return format_json_response(response)

    except Exception as e:
        return handle_api_error(e)


async def vikunja_delete_label(params: DeleteLabelInput) -> str:
    '''
    Delete a label permanently.

    Deletes a label and removes it from all tasks. This operation cannot be undone.

    Args:
        params (DeleteLabelInput): Validated input containing:
            - label_id (int): ID of label to delete (required)

    Returns:
        str: Success confirmation message

    Examples:
        - Delete label: params with label_id=10
    '''
    try:
        await _client.request("DELETE", f"labels/{params.label_id}")
        return f"Label #{params.label_id} has been successfully deleted."

    except Exception as e:
        return handle_api_error(e)


async def vikunja_add_label_to_task(params: AddLabelToTaskInput) -> str:
    '''
    Add a label to a task.

    Applies an existing label to a task for categorization.

    Args:
        params (AddLabelToTaskInput): Validated input containing:
            - task_id (int): ID of task (required)
            - label_id (int): ID of label to add (required)

    Returns:
        str: JSON response with updated task labels

    Examples:
        - Add label: params with task_id=123, label_id=10
    '''
    try:
        response = await _client.request(
            "PUT",
            f"tasks/{params.task_id}/labels",
            json_data={"label_id": params.label_id}
        )
        return format_json_response(response)

    except Exception as e:
        return handle_api_error(e)


async def vikunja_remove_label_from_task(params: RemoveLabelFromTaskInput) -> str:
    '''
    Remove a label from a task.

    Removes a label from a task.

    Args:
        params (RemoveLabelFromTaskInput): Validated input containing:
            - task_id (int): ID of task (required)
            - label_id (int): ID of label to remove (required)

    Returns:
        str: Success confirmation message

    Examples:
        - Remove label: params with task_id=123, label_id=10
    '''
    try:
        await _client.request("DELETE", f"tasks/{params.task_id}/labels/{params.label_id}")
        return f"Label #{params.label_id} removed from task #{params.task_id}."

    except Exception as e:
        return handle_api_error(e)


async def vikunja_get_tasks_by_label(params: GetTasksByLabelInput) -> str:
    '''
    Get all tasks with a specific label.

    Filters tasks by label with pagination support.

    Args:
        params (GetTasksByLabelInput): Validated input containing:
            - label_id (int): ID of label to filter by (required)
            - limit (int): Max results (1-100, default: 20)
            - offset (int): Pagination offset (default: 0)
            - response_format (str): 'markdown' or 'json'

    Returns:
        str: List of tasks with pagination metadata

    Examples:
        - Get tasks by label: params with label_id=10
        - Paginate: params with label_id=10, limit=50, offset=0
    '''
    try:
        # Calculate page number
        page = (params.offset // params.limit) + 1

        response = await _client.request(
            "GET",
            f"labels/{params.label_id}/tasks",
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
