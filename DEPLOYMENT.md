# Vikunja MCP Server Deployment Guide

This guide covers deployment options for the Vikunja MCP server, from local development to production integration with Claude Code and lazy-mcp.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local Development](#local-development)
- [Claude Code Integration](#claude-code-integration)
- [Lazy-MCP Deployment](#lazy-mcp-deployment)
- [Production Deployment](#production-deployment)
- [Troubleshooting](#troubleshooting)

## Prerequisites

- Python 3.10+
- Vikunja instance v0.24.0+ with API access
- Bearer token for authentication
- Claude Code CLI (for Claude integration)

## Local Development

### 1. Environment Setup

```bash
# Navigate to project directory
cd /path/to/vikunja-mcp

# Create virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt
```

### 2. Configuration

Create `.env` file with your Vikunja instance details:

```bash
VIKUNJA_URL=https://your-vikunja-instance.example.com
VIKUNJA_TOKEN=your_bearer_token_here
```

**For do-vps-prod deployment:**
```bash
VIKUNJA_URL=https://vikunja.do-vps-prod.example.com
VIKUNJA_TOKEN=<token_for_samuel@arcforge.au>
```

### 3. Development Server

Run with MCP Inspector for interactive testing:

```bash
mcp dev src/server.py
```

This opens the MCP Inspector interface where you can:
- Test individual tools
- View request/response payloads
- Debug validation errors
- Monitor server lifecycle

## Claude Code Integration

### Standard Integration (Direct)

Add the server to your Claude Code configuration (`~/.claude.json`):

```json
{
  "mcpServers": {
    "vikunja": {
      "command": "python",
      "args": ["/absolute/path/to/vikunja-mcp/src/server.py"],
      "env": {
        "VIKUNJA_URL": "https://your-instance.example.com",
        "VIKUNJA_TOKEN": "your_token_here"
      }
    }
  }
}
```

**Restart Claude Code** to load the new server:
```bash
# If running as daemon, restart it
claude-code restart
```

### Project-Scoped Integration

For project-specific deployment, create `.mcp.json` in your project root:

```json
{
  "mcpServers": {
    "vikunja": {
      "command": "python",
      "args": ["./vikunja-mcp/src/server.py"],
      "env": {
        "VIKUNJA_URL": "https://your-instance.example.com",
        "VIKUNJA_TOKEN": "your_token_here"
      }
    }
  }
}
```

### Verification

Test the integration:

```bash
# In Claude Code session
"List all my Vikunja projects"
```

You should see the `vikunja_list_projects` tool being invoked.

## Lazy-MCP Deployment

lazy-mcp provides progressive disclosure and categorization for large tool collections.

### 1. Install lazy-mcp

```bash
# Clone lazy-mcp-preload repository
git clone https://github.com/your-org/lazy-mcp-preload.git
cd lazy-mcp-preload

# Install dependencies
npm install
```

### 2. Configure Vikunja Integration

Create `config/servers/vikunja.json`:

```json
{
  "name": "vikunja",
  "command": "python",
  "args": ["/absolute/path/to/vikunja-mcp/src/server.py"],
  "env": {
    "VIKUNJA_URL": "https://your-instance.example.com",
    "VIKUNJA_TOKEN": "your_token_here"
  },
  "categories": {
    "tasks": {
      "description": "Task management operations",
      "tools": [
        "vikunja_create_task",
        "vikunja_get_task",
        "vikunja_list_tasks",
        "vikunja_update_task",
        "vikunja_delete_task"
      ]
    },
    "projects": {
      "description": "Project and list management",
      "tools": [
        "vikunja_create_project",
        "vikunja_list_projects",
        "vikunja_update_project",
        "vikunja_delete_project",
        "vikunja_get_project_tasks",
        "vikunja_move_task_to_project"
      ]
    },
    "labels": {
      "description": "Label and tag management",
      "tools": [
        "vikunja_create_label",
        "vikunja_list_labels",
        "vikunja_delete_label",
        "vikunja_add_label_to_task",
        "vikunja_remove_label_from_task",
        "vikunja_get_tasks_by_label"
      ]
    },
    "advanced": {
      "description": "Reminders, relationships, and team collaboration",
      "tools": [
        "vikunja_add_reminder",
        "vikunja_list_reminders",
        "vikunja_delete_reminder",
        "vikunja_create_relation",
        "vikunja_get_relations",
        "vikunja_delete_relation",
        "vikunja_list_teams",
        "vikunja_get_team_members",
        "vikunja_assign_task",
        "vikunja_share_project"
      ]
    }
  }
}
```

### 3. Register with Claude Code

Update `~/.claude.json`:

```json
{
  "mcpServers": {
    "lazy-mcp": {
      "command": "node",
      "args": ["/path/to/lazy-mcp-preload/dist/index.js"],
      "env": {
        "CONFIG_DIR": "/path/to/lazy-mcp-preload/config"
      }
    }
  }
}
```

### 4. Usage

With lazy-mcp, tools are accessed via dot notation:

```bash
# Get tools in category
mcp__lazy-mcp__get_tools_in_category --path "vikunja.tasks"

# Execute specific tool
mcp__lazy-mcp__execute_tool --tool_path "vikunja.tasks.vikunja_create_task" --arguments '{...}'
```

## Production Deployment

### Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ ./src/

# Environment variables (override at runtime)
ENV VIKUNJA_URL=""
ENV VIKUNJA_TOKEN=""

CMD ["python", "src/server.py"]
```

Build and run:

```bash
# Build image
docker build -t vikunja-mcp:latest .

# Run container
docker run -d \
  --name vikunja-mcp \
  -e VIKUNJA_URL="https://your-instance.example.com" \
  -e VIKUNJA_TOKEN="your_token" \
  vikunja-mcp:latest
```

### Systemd Service (Linux)

Create `/etc/systemd/system/vikunja-mcp.service`:

```ini
[Unit]
Description=Vikunja MCP Server
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/vikunja-mcp
Environment="VIKUNJA_URL=https://your-instance.example.com"
Environment="VIKUNJA_TOKEN=your_token"
ExecStart=/usr/bin/python3 /path/to/vikunja-mcp/src/server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable vikunja-mcp
sudo systemctl start vikunja-mcp
sudo systemctl status vikunja-mcp
```

### Environment Variable Management

**Never hardcode secrets in configuration files.** Use one of these approaches:

#### 1. Environment Files (Development)
```bash
# .env (gitignored)
VIKUNJA_URL=https://instance.example.com
VIKUNJA_TOKEN=secret_token
```

#### 2. Secret Management (Production)

**Infisical** (recommended for do-vps-prod):
```bash
# Install Infisical CLI
curl -1sLf 'https://dl.cloudsmith.io/public/infisical/infisical-cli/setup.deb.sh' | sudo -E bash
sudo apt-get update && sudo apt-get install -y infisical

# Login and pull secrets
infisical login
infisical run --env=prod -- python src/server.py
```

**Docker Secrets**:
```bash
# Create secrets
echo "your_token" | docker secret create vikunja_token -

# Use in docker-compose.yml
services:
  vikunja-mcp:
    image: vikunja-mcp:latest
    secrets:
      - vikunja_token
    environment:
      VIKUNJA_TOKEN_FILE: /run/secrets/vikunja_token
```

## Troubleshooting

### Authentication Errors

**Error**: `Invalid or expired authentication token`

**Solutions**:
1. Verify token is correct in `.env` or environment
2. Check token has not expired (regenerate if needed)
3. Ensure `VIKUNJA_TOKEN` does NOT include "Bearer " prefix (added automatically)

### Connection Errors

**Error**: `Network error: Could not connect to Vikunja instance`

**Solutions**:
1. Verify `VIKUNJA_URL` is correct and accessible
2. Check firewall rules allow outbound HTTPS
3. Test connectivity: `curl -I https://your-instance.example.com`
4. Verify Vikunja instance is running

### Rate Limiting

**Error**: `Rate limit exceeded`

**Solutions**:
- The server implements exponential backoff (3 retries)
- If persistent, reduce request frequency
- Check Vikunja instance rate limit configuration

### Tool Not Found

**Error**: Tool `vikunja_*` not found

**Solutions**:
1. Verify server is running: `mcp dev src/server.py`
2. Check Claude Code configuration in `~/.claude.json`
3. Restart Claude Code to reload MCP servers
4. Check logs for initialization errors

### Validation Errors

**Error**: Pydantic validation failed

**Solutions**:
- Check input parameters match schema requirements
- Verify required fields are provided
- Ensure data types are correct (e.g., `task_id` must be integer ≥ 1)
- Review tool documentation in `README.md`

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'mcp'`

**Solutions**:
```bash
# Reinstall dependencies
uv pip install -r requirements.txt

# Verify installation
python -c "import mcp; print(mcp.__version__)"
```

## Testing Deployment

### Health Check

```bash
# Test server initialization
python src/server.py --help

# Test with MCP Inspector
mcp dev src/server.py
```

### Integration Test

```bash
# Run test suite
pytest

# Test specific integration
pytest tests/test_tools.py -v
```

### End-to-End Test

1. Start server: `mcp dev src/server.py`
2. In MCP Inspector, test `vikunja_list_projects`
3. Verify response contains your projects
4. Test CRUD operations on test project

## Monitoring

### Logs

**Development**:
```bash
# Server outputs to stdout
python src/server.py 2>&1 | tee vikunja-mcp.log
```

**Production (systemd)**:
```bash
# View logs
journalctl -u vikunja-mcp -f

# Recent errors
journalctl -u vikunja-mcp -p err -n 50
```

**Production (Docker)**:
```bash
# View logs
docker logs -f vikunja-mcp

# Last 100 lines
docker logs --tail 100 vikunja-mcp
```

### Metrics

Key metrics to monitor:
- Request latency (track slow API calls)
- Error rate (401, 404, 429, 500 responses)
- Retry frequency (429 rate limit triggers)
- Character truncation events (responses > 25k)

## Security Considerations

1. **Token Security**
   - Never commit tokens to version control
   - Use environment variables or secret managers
   - Rotate tokens regularly

2. **Network Security**
   - Always use HTTPS for Vikunja instance
   - Implement firewall rules for production
   - Use VPN/private network when possible

3. **Access Control**
   - Token grants full access to user's Vikunja data
   - Use least-privilege principle
   - Consider read-only tokens for monitoring

## Performance Optimization

1. **Response Formats**
   - Use JSON for programmatic processing (smaller)
   - Use Markdown only when human readability needed

2. **Pagination**
   - Keep `limit` under 50 for faster responses
   - Use `offset` for efficient pagination
   - Cache frequently accessed lists

3. **Character Limits**
   - Default 25k limit prevents context overflow
   - Adjust in `src/utils/formatters.py` if needed
   - Monitor truncation events

## Support

For issues, questions, or contributions:
- Check `ISSUES.md` for known issues
- Review `PROGRESS.md` for implementation status
- Open GitHub issue with reproduction steps
- Include logs and configuration (redact secrets!)

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
