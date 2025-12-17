# Vikunja MCP Server

Python-based MCP server providing comprehensive integration with Vikunja task management system (v0.24.0+).

## Features

- **Task Management**: Complete CRUD operations for tasks with filtering and pagination
- **Project/List Management**: Create, list, update, and delete projects with hierarchy support
- **Labels & Filtering**: Apply labels and filter tasks with AND/OR logic
- **Advanced Features**: Reminders, attachments, task relationships, and team collaboration
- **Token-Optimized**: Configurable response formats (JSON/Markdown) with character limits
- **Secure Credentials**: OpenBao agent integration with Arc Forge secret path pattern
- **Multi-User Support**: Auto-detection of user credentials from git email

## Prerequisites

- Python 3.10+
- Vikunja instance v0.24.0+ with API access
- Bearer token for authentication
- OpenBao agent for secure credential management (production)
  - Or `OPENBAO_DEV_MODE=1` with environment variables (development)

## Installation

### Using uv (recommended)

```bash
# Clone the repository
cd vikunja-mcp

# Install dependencies
uv pip install -r requirements.txt
```

### Using pip

```bash
pip install -r requirements.txt
```

## Configuration

### Production (OpenBao Agent - Recommended)

Credentials are automatically retrieved from the OpenBao agent using the Arc Forge secret path pattern:

```
secret/{namespace}/{environment}-mcp-vikunja-{identifier}
```

For example:
- `secret/client0/prod-mcp-vikunja-iamsamuelrodda` (user-scoped)
- `secret/client0/prod-mcp-vikunja-kayla` (different user)

The identifier is auto-detected from your git email (`git config user.email`).

**Store your credentials in OpenBao:**

```bash
# For the current user
bao kv put secret/client0/prod-mcp-vikunja-$(git config user.email | cut -d@ -f1) \
  token="your-vikunja-token" \
  url="https://tasks.rodda.xyz/"

# For a specific user
bao kv put secret/client0/prod-mcp-vikunja-kayla \
  token="kayla-token" \
  url="https://tasks.rodda.xyz/"
```

The MCP server will automatically connect to the OpenBao agent at `http://127.0.0.1:18200`.

### Development (Environment Variables)

For local development only, enable dev mode to use environment variables:

```bash
export OPENBAO_DEV_MODE=1
export VIKUNJA_TOKEN=your_bearer_token_here
export VIKUNJA_URL=https://your-vikunja-instance.example.com
```

**WARNING**: Environment variable fallback is disabled in production for security.

### Configuration Variables

- `ARC_CLIENT`: Arc Forge namespace (default: `client0`)
- `ARC_ENVIRONMENT`: Environment prefix (default: `prod`)
- `OPENBAO_AGENT_ADDR`: Agent address (default: `http://127.0.0.1:18200`)
- `OPENBAO_DEV_MODE`: Set to `1` to enable env var fallback for development

## Usage

### Development Mode

Run the server in development mode with MCP Inspector:
```bash
mcp dev src/server.py
```

### Production Deployment

See `DEPLOYMENT.md` (coming soon) for detailed deployment instructions including:
- Claude Code integration
- lazy-mcp proxy configuration
- Production deployment patterns

## Examples

### Basic Task Creation

```python
# Via MCP tool
{
  "tool": "vikunja_create_task",
  "params": {
    "project_id": 5,
    "title": "Implement user authentication",
    "description": "Add OAuth 2.0 support with JWT tokens",
    "priority": 4,
    "due_date": "2025-12-31T23:59:59Z"
  }
}
```

### Project Hierarchy

```python
# Create parent project
{
  "tool": "vikunja_create_project",
  "params": {
    "title": "Q1 2025",
    "hex_color": "#3498DB"
  }
}

# Create child project (assuming parent ID = 10)
{
  "tool": "vikunja_create_project",
  "params": {
    "title": "Marketing Campaigns",
    "parent_project_id": 10,
    "hex_color": "#E74C3C"
  }
}
```

### Task Relationships Workflow

```python
# Create blocking relationship (task 50 blocks task 51)
{
  "tool": "vikunja_create_relation",
  "params": {
    "task_id": 50,
    "other_task_id": 51,
    "relation_kind": "blocking"
  }
}

# Get all relationships for a task
{
  "tool": "vikunja_get_relations",
  "params": {
    "task_id": 50,
    "response_format": "markdown"
  }
}
```

### Label-Based Organization

```python
# Create labels
{
  "tool": "vikunja_create_label",
  "params": {
    "title": "bug",
    "hex_color": "#FF0000",
    "description": "Bug reports and fixes"
  }
}

# Apply label to task
{
  "tool": "vikunja_add_label_to_task",
  "params": {
    "task_id": 123,
    "label_id": 10
  }
}

# Filter tasks by label
{
  "tool": "vikunja_get_tasks_by_label",
  "params": {
    "label_id": 10,
    "limit": 50,
    "response_format": "markdown"
  }
}
```

### Team Collaboration

```python
# List teams
{
  "tool": "vikunja_list_teams",
  "params": {
    "response_format": "markdown"
  }
}

# Assign task to user
{
  "tool": "vikunja_assign_task",
  "params": {
    "task_id": 123,
    "user_id": 5
  }
}

# Share project with team (read+write permission)
{
  "tool": "vikunja_share_project",
  "params": {
    "project_id": 10,
    "team_id": 3,
    "permission_level": 1
  }
}
```

### Reminders

```python
# Add reminder for Christmas morning
{
  "tool": "vikunja_add_reminder",
  "params": {
    "task_id": 77,
    "reminder_date": "2025-12-25T09:00:00Z"
  }
}

# List all reminders
{
  "tool": "vikunja_list_reminders",
  "params": {
    "task_id": 77
  }
}
```

## Architecture

```
vikunja-mcp/
├── src/
│   ├── server.py              # Main MCP server entry point
│   ├── client/                # Vikunja API client layer
│   │   ├── vikunja_client.py  # HTTP client wrapper
│   │   └── auth.py            # Authentication handling
│   ├── tools/                 # MCP tool implementations
│   │   ├── tasks.py           # Task CRUD operations
│   │   ├── projects.py        # Project/list management
│   │   ├── labels.py          # Label operations
│   │   └── advanced.py        # Reminders, attachments, relationships
│   ├── schemas/               # Pydantic validation models
│   │   ├── task_schemas.py
│   │   └── project_schemas.py
│   └── utils/                 # Shared utilities
│       ├── formatters.py      # JSON/Markdown response formatting
│       ├── pagination.py      # Page handling
│       └── errors.py          # Error handling
├── evaluations/
│   └── vikunja_eval.xml       # Evaluation scenarios
├── tests/
│   ├── test_tasks.py
│   ├── test_projects.py
│   └── test_client.py
├── requirements.txt
├── README.md
└── .env.example
```

## Available Tools

### Task Management
- `vikunja_create_task` - Create new tasks with full parameter support
- `vikunja_get_task` - Retrieve single task by ID
- `vikunja_list_tasks` - List tasks with pagination and filtering
- `vikunja_update_task` - Update existing tasks (PATCH support)
- `vikunja_delete_task` - Delete tasks with confirmation

### Project Management
- `vikunja_create_project` - Create projects with hierarchy support
- `vikunja_list_projects` - List all projects
- `vikunja_update_project` - Update project details
- `vikunja_delete_project` - Delete projects
- `vikunja_get_project_tasks` - List all tasks in a project
- `vikunja_move_task_to_project` - Relocate tasks between projects

### Label Management
- `vikunja_create_label` - Create labels with colors
- `vikunja_list_labels` - List all labels
- `vikunja_delete_label` - Delete labels
- `vikunja_add_label_to_task` - Apply labels to tasks
- `vikunja_remove_label_from_task` - Remove labels from tasks
- `vikunja_get_tasks_by_label` - Filter tasks by label

### Reminders & Notifications
- `vikunja_add_reminder` - Add time-based reminder to task
- `vikunja_list_reminders` - List all reminders for a task
- `vikunja_delete_reminder` - Delete reminder from task

### Task Relationships
- `vikunja_create_relation` - Create relationship between tasks (11 types: subtask, parenttask, related, duplicateof, duplicates, blocking, blocked, precedes, follows, copiedfrom, copiedto)
- `vikunja_get_relations` - Get all relationships for a task
- `vikunja_delete_relation` - Delete relationship between tasks

### Team Collaboration
- `vikunja_list_teams` - List all accessible teams
- `vikunja_get_team_members` - Get members of a specific team
- `vikunja_assign_task` - Assign task to a user
- `vikunja_share_project` - Share project with team (read, read+write, admin permissions)

**Total: 27 MCP tools**

## Response Formats

All list/get operations support configurable response formats:

- **Markdown** (default): Human-readable tables and lists
- **JSON**: Structured data for programmatic processing

Response detail levels:
- **Detailed**: Complete object with all fields
- **Concise**: Minimal fields (id, title, status) for overview

## Development

### Running Tests

```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/test_client.py

# Run with verbose output
pytest -v

# Generate HTML coverage report
pytest --cov-report=html
open htmlcov/index.html
```

**Test Coverage**: 85%+ coverage across all modules
- Unit tests: Client, utilities, schemas
- Integration tests: All 27 MCP tools
- Evaluation scenarios: 20 complex workflows

### Code Quality

The codebase follows Python MCP server best practices:
- Type hints throughout
- Pydantic v2 for input validation
- Async/await for all I/O
- Comprehensive error handling with LLM-friendly messages
- DRY principles with shared utilities
- Exponential backoff retry logic for rate limiting
- Character limits (25k tokens) with graceful truncation

## Contributing

See `PROGRESS.md` for current implementation status and `ISSUES.md` for known issues and planned features.

## License

[License information to be added]

## Acknowledgments

Built with:
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Vikunja](https://vikunja.io/) - Open-source task management

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
