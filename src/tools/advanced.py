'''
Advanced feature tools for Vikunja MCP server.

This module implements MCP tools for reminders, task relationships,
and team collaboration.
'''

from typing import Dict, Any
from src.client.vikunja_client import VikunjaClient
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
    ShareProjectInput,
    ResponseFormat
)
from src.utils.errors import handle_api_error
from src.utils.formatters import (
    format_timestamp,
    format_json_response,
    truncate_response
)


# Global client instance
_client: VikunjaClient = None


def set_client(client: VikunjaClient):
    '''Set the global Vikunja client instance.'''
    global _client
    _client = client


# ============================================================================
# REMINDER TOOLS
# ============================================================================

async def vikunja_add_reminder(params: AddReminderInput) -> str:
    '''
    Add a reminder to a task.

    Creates a time-based reminder that will trigger at the specified date/time.
    Reminders are managed as part of the task object via the task update endpoint.

    Args:
        params (AddReminderInput): Validated input containing:
            - task_id (int): ID of task (required)
            - reminder_date (str): Date/time in ISO 8601 format (required)

    Returns:
        str: JSON response with created reminder details

    Examples:
        - Add reminder: params with task_id=123, reminder_date="2025-12-25T09:00:00Z"
    '''
    try:
        # First, get the current task to retrieve existing reminders
        task = await _client.request("GET", f"tasks/{params.task_id}")
        existing_reminders = task.get("reminders") or []

        # Create the new reminder object
        new_reminder = {"reminder": params.reminder_date}

        # Append new reminder to existing ones
        updated_reminders = existing_reminders + [new_reminder]

        # Update the task with the new reminders array
        response = await _client.request(
            "POST",
            f"tasks/{params.task_id}",
            json_data={"reminders": updated_reminders}
        )

        # Return just the reminders portion for clarity
        return format_json_response({
            "task_id": params.task_id,
            "reminders": response.get("reminders", [])
        })

    except Exception as e:
        return handle_api_error(e)


async def vikunja_list_reminders(params: ListRemindersInput) -> str:
    '''
    List all reminders for a task.

    Retrieves all reminders set for a specific task.

    Args:
        params (ListRemindersInput): Validated input containing:
            - task_id (int): ID of task (required)
            - response_format (str): 'markdown' or 'json'

    Returns:
        str: List of reminders in requested format

    Examples:
        - List reminders: params with task_id=123
    '''
    try:
        # Get task details which include reminders
        response = await _client.request("GET", f"tasks/{params.task_id}")
        reminders = response.get("reminders", [])

        if params.response_format == ResponseFormat.MARKDOWN:
            lines = [f"# Reminders for Task #{params.task_id}", ""]

            if not reminders:
                return "No reminders set for this task."

            for idx, reminder in enumerate(reminders, 1):
                reminder_date = reminder.get("reminder")
                lines.append(f"{idx}. {format_timestamp(reminder_date)}")

            return "\n".join(lines)
        else:
            return format_json_response({"reminders": reminders})

    except Exception as e:
        return handle_api_error(e)


async def vikunja_delete_reminder(params: DeleteReminderInput) -> str:
    '''
    Delete a reminder from a task.

    Removes a specific reminder by its index in the reminders list.
    Reminders are managed as part of the task object via the task update endpoint.

    Args:
        params (DeleteReminderInput): Validated input containing:
            - task_id (int): ID of task (required)
            - reminder_index (int): 1-based index of reminder to delete (required)

    Returns:
        str: Success confirmation message

    Examples:
        - Delete first reminder: params with task_id=123, reminder_index=1
    '''
    try:
        # Get the current task to retrieve existing reminders
        task = await _client.request("GET", f"tasks/{params.task_id}")
        existing_reminders = task.get("reminders") or []

        # Validate the index
        if params.reminder_index < 1 or params.reminder_index > len(existing_reminders):
            return f"Error: Reminder index {params.reminder_index} is out of range. Task has {len(existing_reminders)} reminder(s)."

        # Get the reminder being deleted for the confirmation message
        deleted_reminder = existing_reminders[params.reminder_index - 1]
        deleted_date = deleted_reminder.get("reminder", "unknown")

        # Remove the reminder at the specified index (convert to 0-based)
        updated_reminders = [
            r for i, r in enumerate(existing_reminders)
            if i != params.reminder_index - 1
        ]

        # Update the task with the filtered reminders array
        await _client.request(
            "POST",
            f"tasks/{params.task_id}",
            json_data={"reminders": updated_reminders}
        )

        return f"Reminder at index {params.reminder_index} ({format_timestamp(deleted_date)}) deleted from task #{params.task_id}."

    except Exception as e:
        return handle_api_error(e)


# ============================================================================
# TASK RELATIONSHIP TOOLS
# ============================================================================

async def vikunja_create_relation(params: CreateRelationInput) -> str:
    '''
    Create a relationship between two tasks.

    Establishes a relationship like parent-child, blocking, or related tasks.

    Args:
        params (CreateRelationInput): Validated input containing:
            - task_id (int): Source task ID (required)
            - other_task_id (int): Related task ID (required)
            - relation_kind (str): Relationship type (required)
              Options: subtask, parenttask, related, duplicateof, duplicates,
              blocking, blocked, precedes, follows, copiedfrom, copiedto

    Returns:
        str: JSON response with created relationship details

    Examples:
        - Create subtask: params with task_id=123, other_task_id=124, relation_kind="subtask"
        - Mark blocking: params with task_id=123, other_task_id=125, relation_kind="blocking"
    '''
    try:
        payload: Dict[str, Any] = {
            "other_task_id": params.other_task_id,
            "relation_kind": params.relation_kind.value
        }

        response = await _client.request(
            "PUT",
            f"tasks/{params.task_id}/relations",
            json_data=payload
        )
        return format_json_response(response)

    except Exception as e:
        return handle_api_error(e)


async def vikunja_get_relations(params: GetRelationsInput) -> str:
    '''
    Get all relationships for a task.

    Retrieves all task relationships including parent-child, blocking, etc.

    Args:
        params (GetRelationsInput): Validated input containing:
            - task_id (int): ID of task (required)
            - response_format (str): 'markdown' or 'json'

    Returns:
        str: Task relationships in requested format

    Examples:
        - Get relationships: params with task_id=123
    '''
    try:
        response = await _client.request("GET", f"tasks/{params.task_id}")
        related_tasks = response.get("related_tasks", {})

        if params.response_format == ResponseFormat.MARKDOWN:
            lines = [f"# Relationships for Task #{params.task_id}", ""]

            if not related_tasks or all(not v for v in related_tasks.values()):
                return "No relationships defined for this task."

            for relation_type, tasks in related_tasks.items():
                if tasks:
                    lines.append(f"## {relation_type.replace('_', ' ').title()}")
                    for task in tasks:
                        task_title = task.get('title', 'Untitled')
                        task_id = task.get('id', '?')
                        lines.append(f"- **#{task_id}**: {task_title}")
                    lines.append("")

            return truncate_response("\n".join(lines))
        else:
            return format_json_response({"related_tasks": related_tasks})

    except Exception as e:
        return handle_api_error(e)


async def vikunja_delete_relation(params: DeleteRelationInput) -> str:
    '''
    Delete a relationship between two tasks.

    Removes a specific relationship.

    Args:
        params (DeleteRelationInput): Validated input containing:
            - task_id (int): Source task ID (required)
            - other_task_id (int): Related task ID (required)
            - relation_kind (str): Relationship type to delete (required)

    Returns:
        str: Success confirmation message

    Examples:
        - Delete subtask relation: params with task_id=123, other_task_id=124, relation_kind="subtask"
    '''
    try:
        await _client.request(
            "DELETE",
            f"tasks/{params.task_id}/relations/{params.relation_kind.value}/{params.other_task_id}"
        )
        return f"Relationship '{params.relation_kind.value}' between task #{params.task_id} and #{params.other_task_id} deleted."

    except Exception as e:
        return handle_api_error(e)


# ============================================================================
# TEAM COLLABORATION TOOLS
# ============================================================================

async def vikunja_list_teams(params: ListTeamsInput) -> str:
    '''
    List all teams.

    Retrieves all teams accessible to the authenticated user.

    Args:
        params (ListTeamsInput): Validated input containing:
            - response_format (str): 'markdown' or 'json'

    Returns:
        str: List of teams in requested format

    Examples:
        - List teams: params with response_format="markdown"
    '''
    try:
        response = await _client.request("GET", "teams")

        if params.response_format == ResponseFormat.MARKDOWN:
            teams = response if isinstance(response, list) else []
            lines = [f"# Teams ({len(teams)})", ""]

            if not teams:
                return "No teams found."

            for team in teams:
                team_name = team.get('name', 'Untitled')
                team_id = team.get('id', '?')
                description = team.get('description', '')

                lines.append(f"## {team_name} (#{team_id})")
                if description:
                    lines.append(f"{description}")
                lines.append("")

            return truncate_response("\n".join(lines))
        else:
            return format_json_response(response)

    except Exception as e:
        return handle_api_error(e)


async def vikunja_get_team_members(params: GetTeamMembersInput) -> str:
    '''
    Get members of a team.

    Retrieves all users who are members of a specific team.

    Args:
        params (GetTeamMembersInput): Validated input containing:
            - team_id (int): ID of team (required)
            - response_format (str): 'markdown' or 'json'

    Returns:
        str: List of team members in requested format

    Examples:
        - Get members: params with team_id=5
    '''
    try:
        response = await _client.request("GET", f"teams/{params.team_id}/members")

        if params.response_format == ResponseFormat.MARKDOWN:
            members = response if isinstance(response, list) else []
            lines = [f"# Team #{params.team_id} Members ({len(members)})", ""]

            if not members:
                return "No members in this team."

            for member in members:
                username = member.get('username', 'Unknown')
                user_id = member.get('id', '?')
                email = member.get('email', '')

                lines.append(f"- **{username}** (#{user_id})")
                if email:
                    lines.append(f"  Email: {email}")

            return "\n".join(lines)
        else:
            return format_json_response(response)

    except Exception as e:
        return handle_api_error(e)


async def vikunja_assign_task(params: AssignTaskInput) -> str:
    '''
    Assign a task to a user.

    Adds a user as an assignee to a task.

    Args:
        params (AssignTaskInput): Validated input containing:
            - task_id (int): ID of task (required)
            - user_id (int): ID of user to assign (required)

    Returns:
        str: JSON response with updated task assignees

    Examples:
        - Assign task: params with task_id=123, user_id=5
    '''
    try:
        payload: Dict[str, Any] = {
            "user_id": params.user_id
        }

        response = await _client.request(
            "PUT",
            f"tasks/{params.task_id}/assignees",
            json_data=payload
        )
        return format_json_response(response)

    except Exception as e:
        return handle_api_error(e)


async def vikunja_share_project(params: ShareProjectInput) -> str:
    '''
    Share a project with a team.

    Grants a team access to a project with specified permission level.

    Args:
        params (ShareProjectInput): Validated input containing:
            - project_id (int): ID of project to share (required)
            - team_id (int): ID of team to share with (required)
            - permission_level (int): 0=read, 1=read+write, 2=admin (default: 0)

    Returns:
        str: JSON response with sharing details

    Examples:
        - Share read-only: params with project_id=5, team_id=3, permission_level=0
        - Share with write access: params with project_id=5, team_id=3, permission_level=1
    '''
    try:
        payload: Dict[str, Any] = {
            "team_id": params.team_id,
            "right": params.permission_level
        }

        response = await _client.request(
            "PUT",
            f"projects/{params.project_id}/teams",
            json_data=payload
        )
        return format_json_response(response)

    except Exception as e:
        return handle_api_error(e)
