'''
Response formatters for Vikunja MCP server.

This module provides utilities for formatting API responses in different output formats
(JSON, Markdown) with configurable detail levels (detailed, concise).
'''

import json
from typing import Any, Dict, List
from enum import Enum
from datetime import datetime


# Constants
CHARACTER_LIMIT = 25000  # Maximum response size in characters


class ResponseFormat(str, Enum):
    '''Output format options for tool responses.'''
    MARKDOWN = "markdown"
    JSON = "json"


def format_timestamp(timestamp_str: str) -> str:
    '''
    Convert ISO timestamp to human-readable format.

    Args:
        timestamp_str (str): ISO 8601 timestamp string

    Returns:
        str: Human-readable timestamp (e.g., "2024-12-16 14:30:00 UTC")
    '''
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except:
        return timestamp_str  # Return original if parsing fails


def format_rrule(rrule: str) -> str:
    '''
    Convert RFC 5545 RRULE string to human-readable format.

    Args:
        rrule (str): RRULE string (e.g., "FREQ=DAILY;INTERVAL=1")

    Returns:
        str: Human-readable recurrence description
    '''
    if not rrule:
        return ""

    # Parse RRULE components
    parts = {}
    for part in rrule.split(';'):
        if '=' in part:
            key, value = part.split('=', 1)
            parts[key.upper()] = value

    freq = parts.get('FREQ', '').upper()
    interval = int(parts.get('INTERVAL', '1'))

    # Build human-readable description
    freq_map = {
        'DAILY': ('day', 'days'),
        'WEEKLY': ('week', 'weeks'),
        'MONTHLY': ('month', 'months'),
        'YEARLY': ('year', 'years'),
    }

    if freq not in freq_map:
        return rrule  # Return raw if unknown frequency

    singular, plural = freq_map[freq]
    if interval == 1:
        base = f"Every {singular}"
    else:
        base = f"Every {interval} {plural}"

    # Add day details for weekly
    if freq == 'WEEKLY' and 'BYDAY' in parts:
        day_map = {'MO': 'Mon', 'TU': 'Tue', 'WE': 'Wed', 'TH': 'Thu', 'FR': 'Fri', 'SA': 'Sat', 'SU': 'Sun'}
        days = [day_map.get(d, d) for d in parts['BYDAY'].split(',')]
        base += f" on {', '.join(days)}"

    # Add day details for monthly
    if freq == 'MONTHLY' and 'BYMONTHDAY' in parts:
        day = parts['BYMONTHDAY']
        base += f" on day {day}"

    return base


def format_task_markdown(task: Dict[str, Any], detailed: bool = True) -> str:
    '''
    Format a single task as Markdown.

    Args:
        task (Dict[str, Any]): Task data from Vikunja API
        detailed (bool): If True, include all fields; if False, only key fields

    Returns:
        str: Markdown-formatted task representation
    '''
    lines = []

    # Title and ID
    done_marker = "✓" if task.get("done") else "○"
    lines.append(f"## {done_marker} {task.get('title', 'Untitled')} (#{task.get('id')})")

    # Description (detailed only)
    if detailed and task.get('description'):
        lines.append(f"\n{task['description']}")

    # Key fields
    lines.append("")
    if task.get('project_id'):
        lines.append(f"- **Project**: {task['project_id']}")

    if task.get('priority'):
        priority_map = {0: "None", 1: "Low", 2: "Medium", 3: "High", 4: "Urgent", 5: "DO NOW"}
        priority_text = priority_map.get(task['priority'], str(task['priority']))
        lines.append(f"- **Priority**: {priority_text}")

    if task.get('due_date'):
        lines.append(f"- **Due**: {format_timestamp(task['due_date'])}")

    if task.get('repeats'):
        repeat_text = format_rrule(task['repeats'])
        if task.get('repeats_from_current_date'):
            repeat_text += " (from completion)"
        lines.append(f"- **Repeats**: {repeat_text}")

    if task.get('labels') and len(task['labels']) > 0:
        label_names = [f"`{label.get('title', 'Unknown')}`" for label in task['labels']]
        lines.append(f"- **Labels**: {', '.join(label_names)}")

    # Detailed fields
    if detailed:
        if task.get('assignees'):
            assignee_names = [a.get('username', 'Unknown') for a in task['assignees']]
            lines.append(f"- **Assigned to**: {', '.join(assignee_names)}")

        if task.get('created'):
            lines.append(f"- **Created**: {format_timestamp(task['created'])}")

        if task.get('updated'):
            lines.append(f"- **Updated**: {format_timestamp(task['updated'])}")

    return "\n".join(lines)


def format_tasks_list_markdown(
    tasks: List[Dict[str, Any]],
    total: int,
    offset: int,
    detailed: bool = False
) -> str:
    '''
    Format a list of tasks as Markdown.

    Args:
        tasks (List[Dict[str, Any]]): List of task data from Vikunja API
        total (int): Total number of tasks matching the query
        offset (int): Current pagination offset
        detailed (bool): If True, show full task details; if False, concise summary

    Returns:
        str: Markdown-formatted task list
    '''
    lines = [f"# Tasks ({len(tasks)} of {total})", ""]

    if not tasks:
        return "No tasks found."

    for task in tasks:
        if detailed:
            lines.append(format_task_markdown(task, detailed=True))
            lines.append("")
        else:
            # Concise format: one line per task
            done_marker = "✓" if task.get("done") else "○"
            title = task.get('title', 'Untitled')
            task_id = task.get('id', '?')
            priority = task.get('priority', 0)

            line = f"- {done_marker} **#{task_id}**: {title}"
            if priority > 0:
                priority_map = {1: "🔵", 2: "🟡", 3: "🟠", 4: "🔴", 5: "🚨"}
                line += f" {priority_map.get(priority, '')}"
            if task.get('repeats'):
                line += " 🔁"
            lines.append(line)

    # Pagination info
    if offset + len(tasks) < total:
        lines.append("")
        lines.append(f"*Showing tasks {offset + 1}-{offset + len(tasks)} of {total}. Use offset={offset + len(tasks)} to see more.*")

    return "\n".join(lines)


def format_project_markdown(project: Dict[str, Any], detailed: bool = True) -> str:
    '''
    Format a single project as Markdown.

    Args:
        project (Dict[str, Any]): Project data from Vikunja API
        detailed (bool): If True, include all fields; if False, only key fields

    Returns:
        str: Markdown-formatted project representation
    '''
    lines = []

    # Title and ID
    lines.append(f"## 📁 {project.get('title', 'Untitled')} (#{project.get('id')})")

    # Description (detailed only)
    if detailed and project.get('description'):
        lines.append(f"\n{project['description']}")

    lines.append("")

    # Key fields
    if project.get('parent_project_id'):
        lines.append(f"- **Parent Project**: {project['parent_project_id']}")

    if project.get('hex_color'):
        lines.append(f"- **Color**: {project['hex_color']}")

    # Detailed fields
    if detailed:
        if project.get('created'):
            lines.append(f"- **Created**: {format_timestamp(project['created'])}")

        if project.get('updated'):
            lines.append(f"- **Updated**: {format_timestamp(project['updated'])}")

    return "\n".join(lines)


def truncate_response(response: str, truncation_message: str = "") -> str:
    '''
    Truncate response if it exceeds CHARACTER_LIMIT.

    Args:
        response (str): The response string to potentially truncate
        truncation_message (str): Custom message to append if truncated

    Returns:
        str: Original response if under limit, truncated response with message if over
    '''
    if len(response) <= CHARACTER_LIMIT:
        return response

    # Truncate and add notice
    truncated = response[:CHARACTER_LIMIT - 500]  # Leave room for message

    if not truncation_message:
        truncation_message = (
            "\n\n---\n**Response Truncated**\n\n"
            f"The response exceeded {CHARACTER_LIMIT} characters and was truncated. "
            "Use pagination parameters (limit, offset) or add filters to reduce the result set."
        )

    return truncated + truncation_message


def format_json_response(data: Any, indent: int = 2) -> str:
    '''
    Format data as JSON string.

    Args:
        data (Any): Data to serialize as JSON
        indent (int): Number of spaces for indentation

    Returns:
        str: JSON-formatted string
    '''
    return json.dumps(data, indent=indent, ensure_ascii=False)
