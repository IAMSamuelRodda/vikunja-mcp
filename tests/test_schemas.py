'''Unit tests for Pydantic schema validation.'''

import pytest
from pydantic import ValidationError
from src.schemas.task_schemas import (
    CreateTaskInput,
    GetTaskInput,
    UpdateTaskInput,
    DeleteTaskInput,
    ListTasksInput,
    TaskPriority,
    ResponseFormat
)
from src.schemas.project_schemas import (
    CreateProjectInput,
    UpdateProjectInput,
    CreateLabelInput
)
from src.schemas.advanced_schemas import (
    AddReminderInput,
    CreateRelationInput,
    RelationKind,
    ShareProjectInput
)


# ============================================================================
# TASK SCHEMA TESTS
# ============================================================================

def test_create_task_input_valid():
    '''Test valid CreateTaskInput.'''
    data = {
        "project_id": 5,
        "title": "Test Task",
        "description": "Test description",
        "priority": 3
    }
    task = CreateTaskInput(**data)

    assert task.project_id == 5
    assert task.title == "Test Task"
    assert task.description == "Test description"
    assert task.priority == TaskPriority.HIGH


def test_create_task_input_minimal():
    '''Test minimal CreateTaskInput with only required fields.'''
    data = {
        "project_id": 1,
        "title": "Minimal Task"
    }
    task = CreateTaskInput(**data)

    assert task.project_id == 1
    assert task.title == "Minimal Task"
    assert task.description is None
    assert task.priority == TaskPriority.NONE


def test_create_task_input_whitespace_stripping():
    '''Test that whitespace is stripped from title.'''
    data = {
        "project_id": 1,
        "title": "  Spaced Task  "
    }
    task = CreateTaskInput(**data)

    assert task.title == "Spaced Task"


def test_create_task_input_empty_title_fails():
    '''Test that empty title fails validation.'''
    data = {
        "project_id": 1,
        "title": "   "
    }

    with pytest.raises(ValidationError) as exc_info:
        CreateTaskInput(**data)

    assert "title cannot be empty" in str(exc_info.value).lower()


def test_create_task_input_invalid_project_id():
    '''Test that project_id must be >= 1.'''
    data = {
        "project_id": 0,
        "title": "Test"
    }

    with pytest.raises(ValidationError):
        CreateTaskInput(**data)


def test_create_task_input_title_too_long():
    '''Test that title has max length validation.'''
    data = {
        "project_id": 1,
        "title": "x" * 501
    }

    with pytest.raises(ValidationError):
        CreateTaskInput(**data)


def test_create_task_input_valid_due_date():
    '''Test valid ISO 8601 due date format.'''
    data = {
        "project_id": 1,
        "title": "Task with deadline",
        "due_date": "2025-12-31T23:59:59Z"
    }
    task = CreateTaskInput(**data)

    assert task.due_date == "2025-12-31T23:59:59Z"


def test_create_task_input_invalid_due_date_format():
    '''Test that invalid due date format fails.'''
    data = {
        "project_id": 1,
        "title": "Task",
        "due_date": "2025-12-31"  # Missing time component
    }

    with pytest.raises(ValidationError):
        CreateTaskInput(**data)


def test_create_task_input_forbids_extra_fields():
    '''Test that extra fields are forbidden.'''
    data = {
        "project_id": 1,
        "title": "Test",
        "unknown_field": "value"
    }

    with pytest.raises(ValidationError):
        CreateTaskInput(**data)


def test_update_task_input_all_fields_optional():
    '''Test that UpdateTaskInput allows all fields to be optional.'''
    data = {"task_id": 123}
    task = UpdateTaskInput(**data)

    assert task.task_id == 123
    assert task.title is None
    assert task.description is None


def test_list_tasks_input_defaults():
    '''Test ListTasksInput default values.'''
    data = {}
    params = ListTasksInput(**data)

    assert params.limit == 20
    assert params.offset == 0
    assert params.response_format == ResponseFormat.MARKDOWN


def test_list_tasks_input_limit_validation():
    '''Test that limit is constrained to 1-100.'''
    with pytest.raises(ValidationError):
        ListTasksInput(limit=0)

    with pytest.raises(ValidationError):
        ListTasksInput(limit=101)

    # Valid boundaries
    params1 = ListTasksInput(limit=1)
    params100 = ListTasksInput(limit=100)

    assert params1.limit == 1
    assert params100.limit == 100


# ============================================================================
# PROJECT SCHEMA TESTS
# ============================================================================

def test_create_project_input_valid():
    '''Test valid CreateProjectInput.'''
    data = {
        "title": "New Project",
        "description": "Project description",
        "hex_color": "#3498DB"
    }
    project = CreateProjectInput(**data)

    assert project.title == "New Project"
    assert project.hex_color == "#3498DB"


def test_create_project_input_invalid_hex_color():
    '''Test that invalid hex color fails validation.'''
    data = {
        "title": "Project",
        "hex_color": "blue"  # Not hex format
    }

    with pytest.raises(ValidationError):
        CreateProjectInput(**data)


def test_create_project_input_hex_color_validation():
    '''Test various hex color format validations.'''
    # Valid formats
    valid_colors = ["#FF0000", "#00ff00", "#3498DB"]
    for color in valid_colors:
        project = CreateProjectInput(title="Test", hex_color=color)
        assert project.hex_color == color

    # Invalid formats
    invalid_colors = ["#FFF", "#GGGGGG", "FF0000", "#12345"]
    for color in invalid_colors:
        with pytest.raises(ValidationError):
            CreateProjectInput(title="Test", hex_color=color)


def test_create_project_input_title_length():
    '''Test project title length validation.'''
    # Too long
    with pytest.raises(ValidationError):
        CreateProjectInput(title="x" * 251)

    # Maximum valid length
    project = CreateProjectInput(title="x" * 250)
    assert len(project.title) == 250


def test_update_project_input_partial_update():
    '''Test UpdateProjectInput with partial fields.'''
    data = {
        "project_id": 10,
        "title": "Updated Title"
    }
    project = UpdateProjectInput(**data)

    assert project.project_id == 10
    assert project.title == "Updated Title"
    assert project.description is None
    assert project.hex_color is None


# ============================================================================
# LABEL SCHEMA TESTS
# ============================================================================

def test_create_label_input_valid():
    '''Test valid CreateLabelInput.'''
    data = {
        "title": "bug",
        "description": "Bug reports",
        "hex_color": "#FF0000"
    }
    label = CreateLabelInput(**data)

    assert label.title == "bug"
    assert label.description == "Bug reports"
    assert label.hex_color == "#FF0000"


def test_create_label_input_default_color():
    '''Test CreateLabelInput uses default color.'''
    data = {"title": "feature"}
    label = CreateLabelInput(**data)

    assert label.hex_color == "#e8e8e8"


# ============================================================================
# ADVANCED SCHEMA TESTS
# ============================================================================

def test_add_reminder_input_valid():
    '''Test valid AddReminderInput.'''
    data = {
        "task_id": 123,
        "reminder_date": "2025-12-25T09:00:00Z"
    }
    reminder = AddReminderInput(**data)

    assert reminder.task_id == 123
    assert reminder.reminder_date == "2025-12-25T09:00:00Z"


def test_add_reminder_input_invalid_date_format():
    '''Test that reminder date must match ISO 8601 format.'''
    data = {
        "task_id": 123,
        "reminder_date": "2025-12-25 09:00:00"  # Missing T and Z
    }

    with pytest.raises(ValidationError):
        AddReminderInput(**data)


def test_create_relation_input_all_relation_kinds():
    '''Test CreateRelationInput with all RelationKind values.'''
    for kind in RelationKind:
        data = {
            "task_id": 100,
            "other_task_id": 200,
            "relation_kind": kind.value
        }
        relation = CreateRelationInput(**data)

        assert relation.task_id == 100
        assert relation.other_task_id == 200
        assert relation.relation_kind == kind


def test_create_relation_input_invalid_kind():
    '''Test that invalid relation_kind fails validation.'''
    data = {
        "task_id": 100,
        "other_task_id": 200,
        "relation_kind": "invalid_relation"
    }

    with pytest.raises(ValidationError):
        CreateRelationInput(**data)


def test_share_project_input_permission_levels():
    '''Test ShareProjectInput permission level validation.'''
    # Valid levels
    for level in [0, 1, 2]:
        data = {
            "project_id": 5,
            "team_id": 3,
            "permission_level": level
        }
        share = ShareProjectInput(**data)
        assert share.permission_level == level

    # Invalid levels
    for level in [-1, 3, 10]:
        with pytest.raises(ValidationError):
            ShareProjectInput(project_id=5, team_id=3, permission_level=level)


def test_share_project_input_default_permission():
    '''Test ShareProjectInput defaults to read-only permission.'''
    data = {
        "project_id": 5,
        "team_id": 3
    }
    share = ShareProjectInput(**data)

    assert share.permission_level == 0  # Read-only
