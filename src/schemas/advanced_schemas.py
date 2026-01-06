'''
Pydantic schemas for Vikunja advanced features.

This module defines input validation models for reminders, task relationships,
and team collaboration operations.
'''

from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, field_validator, ConfigDict
from src.schemas.task_schemas import ResponseFormat


# ============================================================================
# REMINDER SCHEMAS
# ============================================================================

class AddReminderInput(BaseModel):
    '''Input model for adding a reminder to a task.'''
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    task_id: int = Field(
        ...,
        description="ID of the task to add reminder to",
        ge=1
    )
    reminder_date: str = Field(
        ...,
        description="Reminder date/time in ISO 8601 format (e.g., '2025-12-25T09:00:00Z')",
        pattern=r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'
    )


class ListRemindersInput(BaseModel):
    '''Input model for listing reminders for a task.'''
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    task_id: int = Field(
        ...,
        description="ID of the task to list reminders for",
        ge=1
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json' (default: markdown)"
    )


class DeleteReminderInput(BaseModel):
    '''Input model for deleting a reminder.'''
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    task_id: int = Field(
        ...,
        description="ID of the task",
        ge=1
    )
    reminder_index: int = Field(
        ...,
        description="Index of the reminder to delete (1-based, as shown in list_reminders output)",
        ge=1
    )


# ============================================================================
# TASK RELATIONSHIP SCHEMAS
# ============================================================================

class RelationKind(str, Enum):
    '''Types of task relationships in Vikunja.'''
    SUBTASK = "subtask"
    PARENTTASK = "parenttask"
    RELATED = "related"
    DUPLICATEOF = "duplicateof"
    DUPLICATES = "duplicates"
    BLOCKING = "blocking"
    BLOCKED = "blocked"
    PRECEDES = "precedes"
    FOLLOWS = "follows"
    COPIEDFROM = "copiedfrom"
    COPIEDTO = "copiedto"


class CreateRelationInput(BaseModel):
    '''Input model for creating a task relationship.'''
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    task_id: int = Field(
        ...,
        description="ID of the source task",
        ge=1
    )
    other_task_id: int = Field(
        ...,
        description="ID of the related task",
        ge=1
    )
    relation_kind: RelationKind = Field(
        ...,
        description="Type of relationship: subtask, parenttask, related, duplicateof, duplicates, blocking, blocked, precedes, follows, copiedfrom, copiedto"
    )


class GetRelationsInput(BaseModel):
    '''Input model for getting task relationships.'''
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    task_id: int = Field(
        ...,
        description="ID of the task to get relationships for",
        ge=1
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json' (default: markdown)"
    )


class DeleteRelationInput(BaseModel):
    '''Input model for deleting a task relationship.'''
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    task_id: int = Field(
        ...,
        description="ID of the source task",
        ge=1
    )
    other_task_id: int = Field(
        ...,
        description="ID of the related task",
        ge=1
    )
    relation_kind: RelationKind = Field(
        ...,
        description="Type of relationship to delete"
    )


# ============================================================================
# TEAM COLLABORATION SCHEMAS
# ============================================================================

class ListTeamsInput(BaseModel):
    '''Input model for listing all teams.'''
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json' (default: markdown)"
    )


class GetTeamMembersInput(BaseModel):
    '''Input model for getting team members.'''
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    team_id: int = Field(
        ...,
        description="ID of the team",
        ge=1
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json' (default: markdown)"
    )


class AssignTaskInput(BaseModel):
    '''Input model for assigning a task to a user.'''
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    task_id: int = Field(
        ...,
        description="ID of the task to assign",
        ge=1
    )
    user_id: int = Field(
        ...,
        description="ID of the user to assign the task to",
        ge=1
    )


class ShareProjectInput(BaseModel):
    '''Input model for sharing a project with a team.'''
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    project_id: int = Field(
        ...,
        description="ID of the project to share",
        ge=1
    )
    team_id: int = Field(
        ...,
        description="ID of the team to share with",
        ge=1
    )
    permission_level: int = Field(
        default=0,
        description="Permission level: 0=read, 1=read+write, 2=admin (default: 0)",
        ge=0,
        le=2
    )
