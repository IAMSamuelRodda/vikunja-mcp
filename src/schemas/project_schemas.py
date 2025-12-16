'''
Pydantic schemas for Vikunja project and label operations.

This module defines input validation models for project/list management
and label operations.
'''

from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict
from src.schemas.task_schemas import ResponseFormat


# ============================================================================
# PROJECT SCHEMAS
# ============================================================================

class CreateProjectInput(BaseModel):
    '''Input model for creating a new project/list.'''
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    title: str = Field(
        ...,
        description="Project title/name (e.g., 'Work Projects', 'Personal Tasks')",
        min_length=1,
        max_length=250
    )
    description: Optional[str] = Field(
        default="",
        description="Project description (optional)",
        max_length=50000
    )
    hex_color: Optional[str] = Field(
        default=None,
        description="Project color in hex format (e.g., '#FF5733', '#3498DB') (optional)",
        pattern=r'^#[0-9A-Fa-f]{6}$'
    )
    parent_project_id: Optional[int] = Field(
        default=None,
        description="ID of parent project for hierarchy (optional, for nested projects)",
        ge=1
    )

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        '''Ensure title is not empty after stripping.'''
        if not v.strip():
            raise ValueError("Project title cannot be empty")
        return v.strip()


class ListProjectsInput(BaseModel):
    '''Input model for listing all projects.'''
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json' (default: markdown)"
    )


class UpdateProjectInput(BaseModel):
    '''Input model for updating a project.'''
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    project_id: int = Field(
        ...,
        description="ID of the project to update",
        ge=1
    )
    title: Optional[str] = Field(
        default=None,
        description="New project title (optional, only if changing)",
        min_length=1,
        max_length=250
    )
    description: Optional[str] = Field(
        default=None,
        description="New project description (optional, only if changing)",
        max_length=50000
    )
    hex_color: Optional[str] = Field(
        default=None,
        description="New project color in hex format (optional)",
        pattern=r'^#[0-9A-Fa-f]{6}$'
    )

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        '''Ensure title is not empty if provided.'''
        if v is not None and not v.strip():
            raise ValueError("Project title cannot be empty")
        return v.strip() if v else None


class DeleteProjectInput(BaseModel):
    '''Input model for deleting a project.'''
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    project_id: int = Field(
        ...,
        description="ID of the project to delete",
        ge=1
    )


class GetProjectTasksInput(BaseModel):
    '''Input model for listing all tasks in a project.'''
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    project_id: int = Field(
        ...,
        description="ID of the project to list tasks from",
        ge=1
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


class MoveTaskInput(BaseModel):
    '''Input model for moving a task to a different project.'''
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    task_id: int = Field(
        ...,
        description="ID of the task to move",
        ge=1
    )
    target_project_id: int = Field(
        ...,
        description="ID of the destination project",
        ge=1
    )


# ============================================================================
# LABEL SCHEMAS
# ============================================================================

class CreateLabelInput(BaseModel):
    '''Input model for creating a new label.'''
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    title: str = Field(
        ...,
        description="Label name (e.g., 'bug', 'urgent', 'feature-request')",
        min_length=1,
        max_length=100
    )
    description: Optional[str] = Field(
        default="",
        description="Label description (optional)",
        max_length=1000
    )
    hex_color: Optional[str] = Field(
        default="#e8e8e8",
        description="Label color in hex format (e.g., '#FF5733', default: '#e8e8e8')",
        pattern=r'^#[0-9A-Fa-f]{6}$'
    )

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        '''Ensure title is not empty after stripping.'''
        if not v.strip():
            raise ValueError("Label title cannot be empty")
        return v.strip()


class ListLabelsInput(BaseModel):
    '''Input model for listing all labels.'''
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json' (default: markdown)"
    )


class DeleteLabelInput(BaseModel):
    '''Input model for deleting a label.'''
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    label_id: int = Field(
        ...,
        description="ID of the label to delete",
        ge=1
    )


class AddLabelToTaskInput(BaseModel):
    '''Input model for adding a label to a task.'''
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    task_id: int = Field(
        ...,
        description="ID of the task to add the label to",
        ge=1
    )
    label_id: int = Field(
        ...,
        description="ID of the label to add",
        ge=1
    )


class RemoveLabelFromTaskInput(BaseModel):
    '''Input model for removing a label from a task.'''
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    task_id: int = Field(
        ...,
        description="ID of the task to remove the label from",
        ge=1
    )
    label_id: int = Field(
        ...,
        description="ID of the label to remove",
        ge=1
    )


class GetTasksByLabelInput(BaseModel):
    '''Input model for filtering tasks by label.'''
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    label_id: int = Field(
        ...,
        description="ID of the label to filter by",
        ge=1
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
