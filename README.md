# Vikunja MCP Server

MCP server for [Vikunja](https://vikunja.io/) task management (v0.24.0+). Provides 27 tools for comprehensive task, project, and team management.

## Features

- **Task Management**: Create, list, update, delete tasks with filtering and pagination
- **Project Hierarchy**: Nested projects with parent/child relationships
- **Labels & Filtering**: Apply labels and filter with AND/OR logic
- **Reminders**: Time-based task reminders
- **Team Collaboration**: Share projects, assign tasks, manage teams
- **Task Relationships**: Link related, blocking, subtask relationships

## Installation

### Option 1: uvx (Recommended)

Zero-install method using [uv](https://docs.astral.sh/uv/). Add to `~/.claude.json`:

```json
{
  "mcpServers": {
    "vikunja": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/IAMSamuelRodda/vikunja-mcp", "vikunja-mcp"],
      "env": {
        "VIKUNJA_URL": "https://your-vikunja-instance.com",
        "VIKUNJA_TOKEN": "your-api-token"
      }
    }
  }
}
```

### Option 2: Local Clone

```bash
mkdir -p ~/.claude/mcp-servers
git clone https://github.com/IAMSamuelRodda/vikunja-mcp.git ~/.claude/mcp-servers/vikunja-mcp
cd ~/.claude/mcp-servers/vikunja-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Add to `~/.claude.json`:

```json
{
  "mcpServers": {
    "vikunja": {
      "command": "~/.claude/mcp-servers/vikunja-mcp/.venv/bin/python",
      "args": ["-m", "src.server"],
      "cwd": "~/.claude/mcp-servers/vikunja-mcp",
      "env": {
        "VIKUNJA_URL": "https://your-vikunja-instance.com",
        "VIKUNJA_TOKEN": "your-api-token"
      }
    }
  }
}
```

### Get Your API Token

1. Open your Vikunja instance
2. Go to **Settings** → **API Tokens**
3. Create a new token and copy it

## Updating

### uvx users

Clear the cache and restart Claude Code:

```bash
uv cache clean vikunja-mcp
```

### Local clone users

```bash
cd ~/.claude/mcp-servers/vikunja-mcp
git pull
source .venv/bin/activate
pip install -r requirements.txt
```

## Available Tools (27 total)

### Tasks
- `vikunja_create_task` / `vikunja_get_task` / `vikunja_list_tasks`
- `vikunja_update_task` / `vikunja_delete_task`

### Projects
- `vikunja_create_project` / `vikunja_list_projects` / `vikunja_update_project`
- `vikunja_delete_project` / `vikunja_get_project_tasks` / `vikunja_move_task_to_project`

### Labels
- `vikunja_create_label` / `vikunja_list_labels` / `vikunja_delete_label`
- `vikunja_add_label_to_task` / `vikunja_remove_label_from_task` / `vikunja_get_tasks_by_label`

### Reminders
- `vikunja_add_reminder` / `vikunja_list_reminders` / `vikunja_delete_reminder`

### Relationships
- `vikunja_create_relation` / `vikunja_get_relations` / `vikunja_delete_relation`

### Teams
- `vikunja_list_teams` / `vikunja_get_team_members` / `vikunja_assign_task` / `vikunja_share_project`

## Usage Examples

```
"Show my tasks for today"
"Create a task called 'Review PR' in the Development project"
"List all projects"
"Add a reminder for task 42 tomorrow at 9am"
"What tasks are blocking task 15?"
```

## License

MIT
