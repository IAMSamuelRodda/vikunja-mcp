'''
Pydantic schemas for Vikunja task operations.

This module defines input validation models for all task-related MCP tools,
using Pydantic v2 for comprehensive validation and clear error messages.
'''

from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator, ConfigDict


class ResponseFormat(str, Enum):
    '''Output format for tool responses.'''
    MARKDOWN = "markdown"
    JSON = "json"


class DetailLevel(str, Enum):
    '''Level of detail in response.'''
    CONCISE = "concise"
    DETAILED = "detailed"


class TaskPriority(int, Enum):
    '''Task priority levels (Vikunja standard).'''
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4
    DO_NOW = 5


class CreateTaskInput(BaseModel):
    '''Input model for creating a new task.'''
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    project_id: int = Field(
        default=1,
        description="ID of the project/list to create the task in (default: 1 = Inbox). Get project IDs with vikunja_list_projects.",
        ge=1
    )
    title: str = Field(
        ...,
        description="Task title/name (e.g., 'Complete project documentation', 'Fix bug in login')",
        min_length=1,
        max_length=500
    )
    description: Optional[str] = Field(
        default="",
        description="Detailed description of the task in Markdown format (optional)",
        max_length=50000
    )
    priority: Optional[TaskPriority] = Field(
        default=TaskPriority.NONE,
        description="Task priority: 0=None, 1=Low, 2=Medium, 3=High, 4=Urgent, 5=DO NOW (default: 0)"
    )
    due_date: Optional[str] = Field(
        default=None,
        description="Due date in ISO 8601 format (e.g., '2025-12-31T23:59:59Z') (optional)",
        pattern=r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'
    )
    start_date: Optional[str] = Field(
        default=None,
        description="Start date in ISO 8601 format (optional)",
        pattern=r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'
    )
    end_date: Optional[str] = Field(
        default=None,
        description="End date in ISO 8601 format (optional)",
        pattern=r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'
    )
    repeats: Optional[str] = Field(
        default=None,
        description="RFC 5545 RRULE recurrence string (e.g., 'FREQ=DAILY;INTERVAL=1', 'FREQ=WEEKLY;BYDAY=MO,WE,FR', 'FREQ=MONTHLY;BYMONTHDAY=15')"
    )
    repeats_from_current_date: Optional[bool] = Field(
        default=None,
        description="If true, next occurrence is calculated from completion date rather than original due date"
    )

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        '''Ensure title is not empty after stripping.'''
        if not v.strip():
            raise ValueError("Task title cannot be empty")
        return v.strip()


class GetTaskInput(BaseModel):
    '''Input model for retrieving a single task by ID.'''
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    task_id: int = Field(
        ...,
        description="ID of the task to retrieve (e.g., 123, 456)",
        ge=1
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for machine-readable (default: markdown)"
    )


class ListTasksInput(BaseModel):
    '''Input model for listing tasks with filtering and pagination.'''
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    project_id: Optional[int] = Field(
        default=None,
        description="Filter by project/list ID (e.g., 5). If not provided, lists tasks from all projects.",
        ge=1
    )
    filter_done: Optional[bool] = Field(
        default=None,
        description="Filter by completion status: true=completed only, false=incomplete only, null=all (default: null)"
    )
    filter_priority: Optional[TaskPriority] = Field(
        default=None,
        description="Filter by minimum priority level (e.g., 3 for HIGH and above)"
    )
    sort_by: Optional[str] = Field(
        default="id",
        description="Sort field: 'id', 'title', 'priority', 'due_date', 'created', 'updated' (default: id)",
        pattern=r'^(id|title|priority|due_date|created|updated)$'
    )
    sort_order: Optional[str] = Field(
        default="asc",
        description="Sort order: 'asc' or 'desc' (default: asc)",
        pattern=r'^(asc|desc)$'
    )
    limit: Optional[int] = Field(
        default=20,
        description="Maximum number of tasks to return (1-100, default: 20)",
        ge=1,
        le=100
    )
    offset: Optional[int] = Field(
        default=0,
        description="Number of tasks to skip for pagination (default: 0)",
        ge=0
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json' (default: markdown)"
    )
    detail_level: DetailLevel = Field(
        default=DetailLevel.CONCISE,
        description="Detail level: 'concise' for summary or 'detailed' for full info (default: concise)"
    )


class UpdateTaskInput(BaseModel):
    '''Input model for updating an existing task (PATCH operation).'''
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    task_id: int = Field(
        ...,
        description="ID of the task to update (e.g., 123)",
        ge=1
    )
    title: Optional[str] = Field(
        default=None,
        description="New task title (optional, only if changing)",
        min_length=1,
        max_length=500
    )
    description: Optional[str] = Field(
        default=None,
        description="New task description (optional, only if changing)",
        max_length=50000
    )
    done: Optional[bool] = Field(
        default=None,
        description="Mark task as done (true) or not done (false) (optional)"
    )
    priority: Optional[TaskPriority] = Field(
        default=None,
        description="New priority level (optional, only if changing)"
    )
    due_date: Optional[str] = Field(
        default=None,
        description="New due date in ISO 8601 format (optional)",
        pattern=r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'
    )
    repeats: Optional[str] = Field(
        default=None,
        description="RFC 5545 RRULE recurrence string (e.g., 'FREQ=DAILY;INTERVAL=1'). Set to empty string to remove recurrence."
    )
    repeats_from_current_date: Optional[bool] = Field(
        default=None,
        description="If true, next occurrence is calculated from completion date rather than original due date"
    )

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        '''Ensure title is not empty if provided.'''
        if v is not None and not v.strip():
            raise ValueError("Task title cannot be empty")
        return v.strip() if v else None


class DeleteTaskInput(BaseModel):
    '''Input model for deleting a task.'''
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    task_id: int = Field(
        ...,
        description="ID of the task to delete (e.g., 123)",
        ge=1
    )
