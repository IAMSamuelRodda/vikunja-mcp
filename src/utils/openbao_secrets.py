"""
OpenBao Secrets Client for MCP Servers.

This module provides a simple interface for MCP servers to read secrets
from a local OpenBao Agent. It replaces direct .env file reading with
secure agent-based secret retrieval.

SECURITY: Environment variable fallback is DISABLED by default.
Only enable for local development environments, never in production.

Usage:
    from src.utils.openbao_secrets import get_mcp_token, get_mcp_config

    # Production: Agent only (no fallback)
    token = get_mcp_token("vikunja")

    # Development only: Allow env var fallback (explicit opt-in)
    token = get_mcp_token("vikunja", dev_fallback="VIKUNJA_TOKEN")

    # Get full MCP config
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
# Default port 18200 is the local agent listener (distinct from VPS tunnel on 8200)
AGENT_ADDR = os.getenv("OPENBAO_AGENT_ADDR", "http://127.0.0.1:18200")
AGENT_TIMEOUT = float(os.getenv("OPENBAO_AGENT_TIMEOUT", "5.0"))

# Development mode detection
# Set OPENBAO_DEV_MODE=1 to allow env var fallbacks (local dev only)
DEV_MODE = os.getenv("OPENBAO_DEV_MODE", "").lower() in ("1", "true", "yes")


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
    dev_fallback: Optional[str] = None,
    required: bool = True
) -> Optional[str]:
    """
    Get an MCP service token from the OpenBao agent.

    SECURITY: Environment variable fallback is DISABLED by default.
    Fallback only works when OPENBAO_DEV_MODE=1 is set AND dev_fallback
    is specified. This ensures production environments always use the agent.

    Args:
        service: Service name (e.g., "vikunja", "joplin")
        dev_fallback: Environment variable name for dev-only fallback.
                      Only used when OPENBAO_DEV_MODE=1 is set.
        required: If True, raise error when token not found

    Returns:
        The token string, or None if not found and not required.

    Raises:
        AgentNotRunningError: If agent not running (production)
        SecretNotFoundError: If secret not found (production)
        ValueError: If required=True and token not found

    Example:
        # Production: Agent only (will fail if agent not running)
        token = get_mcp_token("vikunja")

        # Development: Allow env fallback (requires OPENBAO_DEV_MODE=1)
        token = get_mcp_token("vikunja", dev_fallback="VIKUNJA_TOKEN")
    """
    # Try agent first
    try:
        return get_secret(f"mcp/{service}", "token")
    except AgentNotRunningError as e:
        # Only allow fallback in dev mode with explicit fallback specified
        if DEV_MODE and dev_fallback:
            token = os.getenv(dev_fallback)
            if token:
                warnings.warn(
                    f"[DEV MODE] Using {dev_fallback} env var (agent not running). "
                    "This fallback is disabled in production.",
                    UserWarning
                )
                return token
        if required:
            raise AgentNotRunningError(
                f"OpenBao Agent not running at {AGENT_ADDR}. "
                "Start the agent with: start-openbao-agent"
            ) from e
        return None
    except SecretNotFoundError as e:
        # Only allow fallback in dev mode with explicit fallback specified
        if DEV_MODE and dev_fallback:
            token = os.getenv(dev_fallback)
            if token:
                warnings.warn(
                    f"[DEV MODE] Using {dev_fallback} env var (secret not in agent). "
                    "This fallback is disabled in production.",
                    UserWarning
                )
                return token
        if required:
            raise ValueError(
                f"Token for '{service}' not found in agent at secret/mcp/{service}. "
                "Ensure the secret exists in OpenBao."
            ) from e
        return None


def get_mcp_config(service: str, dev_fallbacks: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Get full configuration for an MCP service from the OpenBao agent.

    SECURITY: Environment variable fallback is DISABLED by default.
    Fallback only works when OPENBAO_DEV_MODE=1 is set AND dev_fallbacks
    is specified. This ensures production environments always use the agent.

    Args:
        service: Service name (e.g., "vikunja")
        dev_fallbacks: Dict mapping config keys to env var names for dev-only fallback.
                       Only used when OPENBAO_DEV_MODE=1 is set.
                       e.g., {"token": "VIKUNJA_TOKEN", "url": "VIKUNJA_URL"}

    Returns:
        Dict with all config keys for the service.

    Example:
        # Production: Agent only
        config = get_mcp_config("vikunja")

        # Development: Allow env fallback (requires OPENBAO_DEV_MODE=1)
        config = get_mcp_config("vikunja", dev_fallbacks={
            "token": "VIKUNJA_TOKEN",
            "url": "VIKUNJA_URL"
        })
    """
    try:
        return get_secret(f"mcp/{service}")
    except (AgentNotRunningError, SecretNotFoundError) as e:
        # Only allow fallback in dev mode with explicit fallbacks specified
        if DEV_MODE and dev_fallbacks:
            config = {}
            for key, env_var in dev_fallbacks.items():
                value = os.getenv(env_var)
                if value:
                    config[key] = value
            if config:
                warnings.warn(
                    f"[DEV MODE] Using environment variables for {service} (agent unavailable). "
                    "This fallback is disabled in production.",
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
