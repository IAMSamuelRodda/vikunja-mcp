"""
Utility modules for Vikunja MCP Server.
"""

from src.utils.errors import handle_api_error
from src.utils.formatters import (
    format_task_markdown,
    format_tasks_list_markdown,
    format_project_markdown,
    format_timestamp,
    truncate_response,
    format_json_response,
    ResponseFormat
)
from src.utils.pagination import build_pagination_response, validate_pagination_params
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
    "format_task_markdown",
    "format_tasks_list_markdown",
    "format_project_markdown",
    "format_timestamp",
    "truncate_response",
    "format_json_response",
    "ResponseFormat",
    "build_pagination_response",
    "validate_pagination_params",
    "get_mcp_token",
    "get_mcp_config",
    "is_agent_available",
    "OpenBaoError",
    "AgentNotRunningError",
    "SecretNotFoundError",
    "DEV_MODE"
]
