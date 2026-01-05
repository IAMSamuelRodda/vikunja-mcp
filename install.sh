#!/usr/bin/env bash
# Vikunja MCP Server - Claude Code Installation Script

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/config.json"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Check for jq
command -v jq >/dev/null 2>&1 || error "jq is required. Install with: sudo apt install jq"

# Check for config.json
if [[ ! -f "$CONFIG_FILE" ]]; then
    if [[ -f "${SCRIPT_DIR}/config.json.example" ]]; then
        info "Creating config.json from example..."
        cp "${SCRIPT_DIR}/config.json.example" "$CONFIG_FILE"
        warn "Please edit config.json with your Vikunja URL and token, then re-run this script."
        warn "Get your token from: Vikunja → Settings → API Tokens"
        exit 0
    else
        error "config.json not found. Create it from config.json.example"
    fi
fi

# Parse config.json
VIKUNJA_URL=$(jq -r '.vikunja_url // ""' "$CONFIG_FILE")
VIKUNJA_TOKEN=$(jq -r '.vikunja_token // ""' "$CONFIG_FILE")

# Validate
if [[ -z "$VIKUNJA_URL" || "$VIKUNJA_URL" == "https://vikunja.example.com" ]]; then
    error "vikunja_url not configured in config.json"
fi

if [[ -z "$VIKUNJA_TOKEN" ]]; then
    error "vikunja_token not configured in config.json"
fi

# Create Python venv if needed
if [[ ! -d "${SCRIPT_DIR}/.venv" ]]; then
    info "Creating Python virtual environment..."
    python3 -m venv "${SCRIPT_DIR}/.venv"
    info "Installing dependencies..."
    "${SCRIPT_DIR}/.venv/bin/pip" install -q -r "${SCRIPT_DIR}/requirements.txt"
fi

# Register with Claude Code
MCP_NAME="vikunja"
PYTHON_PATH="${SCRIPT_DIR}/.venv/bin/python"

info "Registering MCP server with Claude Code..."
claude mcp add "$MCP_NAME" -s user \
    --env "VIKUNJA_URL=${VIKUNJA_URL}" \
    --env "VIKUNJA_TOKEN=${VIKUNJA_TOKEN}" \
    -- "$PYTHON_PATH" -m src.server

info "Vikunja MCP server registered successfully!"
info "Restart Claude Code to use the new server."
