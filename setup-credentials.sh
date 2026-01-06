#!/usr/bin/env bash
# Vikunja MCP - Credentials Setup Script
#
# This script configures credentials for the Vikunja MCP server.
# Works for both plugin and manual installations.
#
# Usage:
#   ./setup-credentials.sh
#   curl -sSL https://raw.githubusercontent.com/IAMSamuelRodda/vikunja-mcp/main/setup-credentials.sh | bash

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }
prompt() { echo -e "${BLUE}[?]${NC} $1"; }

# Config location
CONFIG_DIR="${HOME}/.config/vikunja-mcp"
CONFIG_FILE="${CONFIG_DIR}/config.json"

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║           Vikunja MCP - Credentials Setup                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if config already exists
if [[ -f "$CONFIG_FILE" ]]; then
    warn "Config file already exists: $CONFIG_FILE"
    echo ""
    read -p "Do you want to overwrite it? [y/N] " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        info "Keeping existing configuration."
        exit 0
    fi
fi

# Prompt for Vikunja URL
echo ""
prompt "Enter your Vikunja instance URL"
echo "   Example: https://vikunja.example.com"
echo "   (without trailing slash)"
read -p "> " VIKUNJA_URL

# Validate URL
if [[ -z "$VIKUNJA_URL" ]]; then
    error "URL cannot be empty"
fi

# Remove trailing slash if present
VIKUNJA_URL="${VIKUNJA_URL%/}"

# Prompt for API token
echo ""
prompt "Enter your Vikunja API token"
echo "   Get it from: Vikunja -> Settings -> API Tokens -> Create Token"
read -sp "> " VIKUNJA_TOKEN
echo ""

# Validate token
if [[ -z "$VIKUNJA_TOKEN" ]]; then
    error "Token cannot be empty"
fi

# Create config directory
mkdir -p "$CONFIG_DIR"

# Write config file
cat > "$CONFIG_FILE" << EOF
{
  "url": "${VIKUNJA_URL}",
  "token": "${VIKUNJA_TOKEN}"
}
EOF

# Secure the config file (readable only by owner)
chmod 600 "$CONFIG_FILE"

echo ""
info "Configuration saved to: $CONFIG_FILE"
info "File permissions set to 600 (owner read/write only)"
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    Setup Complete!                         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "  1. Restart Claude Code to pick up the new configuration"
echo "  2. The Vikunja MCP server will automatically use these credentials"
echo ""
