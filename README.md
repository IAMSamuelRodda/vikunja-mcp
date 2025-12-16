# Vikunja MCP Server

Python-based MCP server providing comprehensive integration with Vikunja task management system (v0.24.0+).

## Features

- **Task Management**: Complete CRUD operations for tasks with filtering and pagination
- **Project/List Management**: Create, list, update, and delete projects with hierarchy support
- **Labels & Filtering**: Apply labels and filter tasks with AND/OR logic
- **Advanced Features**: Reminders, attachments, task relationships, and team collaboration
- **Token-Optimized**: Configurable response formats (JSON/Markdown) with character limits
- **Authentication**: Secure bearer token authentication

## Prerequisites

- Python 3.10+
- Vikunja instance v0.24.0+ with API access
- Bearer token for authentication

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

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` with your Vikunja instance details:
```bash
VIKUNJA_URL=https://your-vikunja-instance.example.com
VIKUNJA_TOKEN=your_bearer_token_here
```

**For do-vps-prod instance:**
- URL: (configured on do-vps-prod)
- Token: Bearer token for samuel@arcforge.au

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

*(Additional tools for reminders, attachments, relationships, and teams coming soon)*

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
pytest
```

### Code Quality

The codebase follows Python MCP server best practices:
- Type hints throughout
- Pydantic v2 for input validation
- Async/await for all I/O
- Comprehensive error handling
- DRY principles with shared utilities

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
