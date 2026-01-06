# Vikunja MCP Server

MCP server for [Vikunja](https://vikunja.io/) task management (v0.24.0+). Provides 27 tools for comprehensive task, project, and team management.

## Features

- **Task Management**: Create, list, update, delete tasks with filtering and pagination
- **Project Hierarchy**: Nested projects with parent/child relationships
- **Labels & Filtering**: Apply labels and filter with AND/OR logic
- **Reminders**: Time-based task reminders
- **Team Collaboration**: Share projects, assign tasks, manage teams
- **Task Relationships**: Link related, blocking, subtask relationships

## Demo

See the MCP server in action: [vikunja-mcp-demo.mp4](https://github.com/IAMSamuelRodda/arc-forge-plugins/raw/master/demo/vikunja-mcp-demo.mp4)

## Installation

### Option 1: Claude Code Plugin (Recommended)

Install via the Claude Code plugin marketplace:

```
/plugin install vikunja-mcp
```

Then configure your credentials:

```bash
curl -sSL https://raw.githubusercontent.com/IAMSamuelRodda/vikunja-mcp/main/setup-credentials.sh | bash
```

Restart Claude Code to activate.

### Option 2: Local Installation Script

Clone and run the install script:

```bash
git clone https://github.com/IAMSamuelRodda/vikunja-mcp.git
cd vikunja-mcp
./install.sh
```

The script will:
1. Prompt for your Vikunja URL and API token
2. Create a Python virtual environment
3. Register the MCP server with Claude Code

### Option 3: Manual Configuration

For advanced users who prefer manual setup:

1. **Setup credentials** (required for all methods):

```bash
curl -sSL https://raw.githubusercontent.com/IAMSamuelRodda/vikunja-mcp/main/setup-credentials.sh | bash
```

This creates `~/.config/vikunja-mcp/config.json` with your credentials.

2. **Add to Claude Code** using uvx:

```bash
claude mcp add vikunja -s user -- uvx --from git+https://github.com/IAMSamuelRodda/vikunja-mcp vikunja-mcp
```

### Get Your API Token

1. Open your Vikunja instance
2. Go to **Settings** → **API Tokens**
3. Create a new token and copy it

## Credential Configuration

All installation methods use the same config file:

```
~/.config/vikunja-mcp/config.json
```

To update credentials at any time:

```bash
./setup-credentials.sh
# or
curl -sSL https://raw.githubusercontent.com/IAMSamuelRodda/vikunja-mcp/main/setup-credentials.sh | bash
```

### Credential Resolution Order

The server looks for credentials in this order:
1. **OpenBao Agent** (if available) - for enterprise secret management
2. **Config file** (`~/.config/vikunja-mcp/config.json`) - recommended
3. **Environment variables** (`VIKUNJA_URL`, `VIKUNJA_TOKEN`) - backward compatible

## Updating

### Plugin users

```
/plugin update vikunja-mcp
```

### Local installation users

```bash
cd vikunja-mcp
git pull
./install.sh
```

### uvx users

Clear the cache and restart Claude Code:

```bash
uv cache clean vikunja-mcp
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
