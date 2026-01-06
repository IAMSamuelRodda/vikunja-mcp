---
description: Set up vikunja-mcp with Python venv and credentials
---

# Vikunja MCP Setup

Run these setup steps:

1. Create Python virtual environment and install dependencies:
```bash
cd ${CLAUDE_PLUGIN_ROOT}
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

2. Set environment variables (add to ~/.bashrc or ~/.zshrc):
```bash
export VIKUNJA_URL="https://your-vikunja-instance.com"
export VIKUNJA_TOKEN="your-api-token"
```

3. Restart Claude Code for the MCP server to activate.

## Get Your API Token

1. Open your Vikunja instance
2. Go to **Settings** → **API Tokens**
3. Create a new token and copy it
