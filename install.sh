#!/usr/bin/env bash
# Vikunja MCP Server - Claude Code Installation Script
#
# This script performs a full local installation:
# 1. Sets up credentials (via setup-credentials.sh)
# 2. Creates Python virtual environment
# 3. Registers MCP server with Claude Code
#
# For plugin installations, only run setup-credentials.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="${HOME}/.config/vikunja-mcp"
CONFIG_FILE="${CONFIG_DIR}/config.json"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║        Vikunja MCP Server - Full Installation              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Setup credentials if not already configured
if [[ ! -f "$CONFIG_FILE" ]]; then
    info "Setting up credentials..."
    "${SCRIPT_DIR}/setup-credentials.sh"
else
    info "Credentials already configured: $CONFIG_FILE"
fi

# Validate config exists
if [[ ! -f "$CONFIG_FILE" ]]; then
    error "Config file not found after setup. Please run setup-credentials.sh manually."
fi

# Step 2: Create Python venv if needed
if [[ ! -d "${SCRIPT_DIR}/.venv" ]]; then
    info "Creating Python virtual environment..."
    python3 -m venv "${SCRIPT_DIR}/.venv"
    info "Installing dependencies..."
    "${SCRIPT_DIR}/.venv/bin/pip" install -q -r "${SCRIPT_DIR}/requirements.txt"
else
    info "Python virtual environment already exists"
fi

# Step 3: Register with Claude Code (without env vars - server reads from config file)
MCP_NAME="vikunja"
PYTHON_PATH="${SCRIPT_DIR}/.venv/bin/python"

info "Registering MCP server with Claude Code..."
claude mcp add "$MCP_NAME" -s user -- "$PYTHON_PATH" -m src.server

echo ""
info "Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Restart Claude Code to load the new server"
echo "  2. Try: 'List my Vikunja projects'"
echo ""
echo "To update credentials later, run:"
echo "  ${SCRIPT_DIR}/setup-credentials.sh"
echo ""
