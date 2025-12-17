"""
OpenBao Secrets Client for MCP Servers.

This module provides a simple interface for MCP servers to read secrets
from a local OpenBao Agent. It replaces direct .env file reading with
secure agent-based secret retrieval.

Usage:
    from src.utils.openbao_secrets import get_mcp_token, get_mcp_config

    # Get MCP token with fallback to env var
    token = get_mcp_token("vikunja", env_fallback="VIKUNJA_TOKEN")

    # Get full MCP config (token, url, etc.)
    config = get_mcp_config("vikunja")
"""

import os
import warnings
from typing import Optional, Dict, Any
from functools import lru_cache

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


# Configuration
AGENT_ADDR = os.getenv("OPENBAO_AGENT_ADDR", "http://127.0.0.1:8200")
AGENT_TIMEOUT = float(os.getenv("OPENBAO_AGENT_TIMEOUT", "5.0"))


class OpenBaoError(Exception):
    """Base exception for OpenBao errors."""
    pass


class AgentNotRunningError(OpenBaoError):
    """Raised when the OpenBao Agent is not running."""
    pass


class SecretNotFoundError(OpenBaoError):
    """Raised when a secret path doesn't exist."""
    pass


def _get_client():
    """Get HTTP client for agent communication."""
    if not HTTPX_AVAILABLE:
        raise OpenBaoError("httpx is required for OpenBao agent support")
    return httpx.Client(
        base_url=AGENT_ADDR,
        timeout=AGENT_TIMEOUT,
        headers={"X-Vault-Request": "true"}
    )


def check_agent_health() -> bool:
    """
    Check if the OpenBao Agent is running and healthy.

    Returns:
        True if agent is healthy, False otherwise.
    """
    if not HTTPX_AVAILABLE:
        return False
    try:
        with _get_client() as client:
            response = client.get("/v1/sys/health")
            return response.status_code in (200, 429, 472, 473, 501, 503)
    except Exception:
        return False


def get_secret(path: str, key: Optional[str] = None) -> Any:
    """
    Read a secret from the OpenBao Agent.

    Args:
        path: Secret path (e.g., "mcp/vikunja")
        key: Optional specific key within the secret data

    Returns:
        The secret data dict, or specific key value if key provided.

    Raises:
        AgentNotRunningError: If agent is not running
        SecretNotFoundError: If secret path doesn't exist
        OpenBaoError: For other OpenBao errors
    """
    if not HTTPX_AVAILABLE:
        raise AgentNotRunningError("httpx not installed - cannot connect to agent")

    # Ensure path doesn't start with /
    path = path.lstrip("/")

    # Build the full path for KV v2
    full_path = f"/v1/secret/data/{path}"

    try:
        with _get_client() as client:
            response = client.get(full_path)

            if response.status_code == 404:
                raise SecretNotFoundError(f"Secret not found: {path}")

            if response.status_code != 200:
                raise OpenBaoError(
                    f"Failed to read secret: {response.status_code} - {response.text}"
                )

            data = response.json()
            secret_data = data.get("data", {}).get("data", {})

            if key:
                if key not in secret_data:
                    raise SecretNotFoundError(f"Key '{key}' not found in {path}")
                return secret_data[key]

            return secret_data

    except httpx.ConnectError:
        raise AgentNotRunningError(
            f"Cannot connect to OpenBao Agent at {AGENT_ADDR}. "
            "Ensure the agent is running: start-openbao-agent"
        )


def get_mcp_token(
    service: str,
    env_fallback: Optional[str] = None,
    required: bool = True
) -> Optional[str]:
    """
    Get an MCP service token from the agent, with optional env var fallback.

    This is a convenience function for MCP servers that provides:
    - Agent-first lookup (secure)
    - Optional fallback to environment variable (for development/migration)
    - Clear error messages

    Args:
        service: Service name (e.g., "vikunja", "joplin")
        env_fallback: Optional environment variable name for fallback
        required: If True, raise error when token not found

    Returns:
        The token string, or None if not found and not required.

    Raises:
        AgentNotRunningError: If agent not running and no fallback
        SecretNotFoundError: If secret not found and no fallback
        ValueError: If required=True and token not found anywhere

    Example:
        # Secure: agent only
        token = get_mcp_token("vikunja")

        # With fallback for development
        token = get_mcp_token("vikunja", env_fallback="VIKUNJA_TOKEN")
    """
    # Try agent first
    try:
        return get_secret(f"mcp/{service}", "token")
    except AgentNotRunningError:
        if env_fallback:
            token = os.getenv(env_fallback)
            if token:
                warnings.warn(
                    f"Using {env_fallback} env var (agent not running). "
                    "This is less secure than agent-based secrets.",
                    UserWarning
                )
                return token
        if required:
            raise
        return None
    except SecretNotFoundError:
        if env_fallback:
            token = os.getenv(env_fallback)
            if token:
                warnings.warn(
                    f"Using {env_fallback} env var (secret not in agent). "
                    "Consider migrating to agent-based secrets.",
                    UserWarning
                )
                return token
        if required:
            raise ValueError(
                f"Token for '{service}' not found in agent or environment. "
                f"Ensure secret exists at secret/mcp/{service}"
            )
        return None


def get_mcp_config(service: str, env_fallbacks: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Get full configuration for an MCP service.

    Returns all keys stored for the service, not just the token.
    Useful for services that need URL, token, and other config.

    Args:
        service: Service name (e.g., "vikunja")
        env_fallbacks: Optional dict mapping config keys to env var names
                       e.g., {"token": "VIKUNJA_TOKEN", "url": "VIKUNJA_URL"}

    Returns:
        Dict with all config keys for the service.

    Example:
        config = get_mcp_config("vikunja", {
            "token": "VIKUNJA_TOKEN",
            "url": "VIKUNJA_URL"
        })
        # Returns: {"token": "xxx", "url": "https://...", ...}
    """
    try:
        return get_secret(f"mcp/{service}")
    except (AgentNotRunningError, SecretNotFoundError):
        if env_fallbacks:
            config = {}
            for key, env_var in env_fallbacks.items():
                value = os.getenv(env_var)
                if value:
                    config[key] = value
            if config:
                warnings.warn(
                    f"Using environment variables for {service} (agent unavailable). "
                    "This is less secure than agent-based secrets.",
                    UserWarning
                )
                return config
        raise


@lru_cache(maxsize=1)
def is_agent_available() -> bool:
    """
    Check if agent is available (cached for performance).

    Use this at startup to decide between agent and fallback mode.
    Result is cached for the lifetime of the process.

    Returns:
        True if agent is available.
    """
    return check_agent_health()


# Convenience aliases
read_secret = get_secret
