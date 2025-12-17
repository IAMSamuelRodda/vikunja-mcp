"""
Utility modules for Vikunja MCP Server.
"""

from src.utils.errors import handle_api_error
from src.utils.formatters import format_task, format_project, format_label
from src.utils.pagination import paginate_results
from src.utils.openbao_secrets import (
    get_mcp_token,
    get_mcp_config,
    is_agent_available,
    OpenBaoError,
    AgentNotRunningError,
    SecretNotFoundError,
    DEV_MODE
)

__all__ = [
    "handle_api_error",
    "format_task",
    "format_project",
    "format_label",
    "paginate_results",
    "get_mcp_token",
    "get_mcp_config",
    "is_agent_available",
    "OpenBaoError",
    "AgentNotRunningError",
    "SecretNotFoundError",
    "DEV_MODE"
]
