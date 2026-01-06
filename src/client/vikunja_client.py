'''
Vikunja API Client.

This module provides an async HTTP client wrapper for interacting with the
Vikunja REST API (v0.24.0+). It handles authentication, error handling, rate
limiting, and request/response management.

Credential Resolution (in order):
1. OpenBao Agent (if openbao_secrets module available and agent running)
2. Config file: ~/.config/vikunja-mcp/config.json
3. Environment variables: VIKUNJA_URL, VIKUNJA_TOKEN
'''

import os
import json
import asyncio
from pathlib import Path
from typing import Any, Dict, Optional
import httpx
from src.utils.errors import handle_api_error

# Optional OpenBao support - gracefully falls back to env vars if not available
try:
    from src.utils.openbao_secrets import get_mcp_config, is_agent_available
    OPENBAO_AVAILABLE = True
except ImportError:
    OPENBAO_AVAILABLE = False

# Constants
API_VERSION = "v1"
REQUEST_TIMEOUT = 30.0
MAX_RETRIES = 3
RETRY_DELAY = 1.0  # Initial delay in seconds for exponential backoff
CONFIG_FILE_PATH = Path.home() / ".config" / "vikunja-mcp" / "config.json"


class VikunjaClient:
    '''
    Async HTTP client for Vikunja API.

    Handles bearer token authentication, error responses, rate limiting with
    exponential backoff, and provides a consistent interface for all API calls.

    Credential Resolution (in order):
    1. OpenBao Agent (if openbao_secrets module available and agent running)
    2. Config file: ~/.config/vikunja-mcp/config.json
    3. Environment variables: VIKUNJA_URL, VIKUNJA_TOKEN

    Attributes:
        base_url (str): Base URL of the Vikunja instance
        token (str): Bearer token for authentication
        client (httpx.AsyncClient): Reusable async HTTP client
        credential_source (str): Where credentials were loaded from
    '''

    def __init__(self):
        '''Initialize the Vikunja API client with configuration from OpenBao or environment.'''
        config, self.credential_source = self._load_config()

        self.base_url = config.get("url", "").rstrip("/")
        self.token = config.get("token", "")

        if not self.base_url:
            raise ValueError(
                f"Vikunja URL not found. Either:\n"
                f"  1. Create config file: {CONFIG_FILE_PATH}\n"
                f"  2. Set VIKUNJA_URL environment variable\n"
                f"  Run 'setup-credentials.sh' for guided setup."
            )
        if not self.token:
            raise ValueError(
                f"Vikunja token not found. Either:\n"
                f"  1. Create config file: {CONFIG_FILE_PATH}\n"
                f"  2. Set VIKUNJA_TOKEN environment variable\n"
                f"  Run 'setup-credentials.sh' for guided setup."
            )

        # Build API base URL
        self.api_base = f"{self.base_url}/api/{API_VERSION}"

        # Initialize async client (will be created lazily)
        self._client: Optional[httpx.AsyncClient] = None

    def _load_config(self) -> tuple[Dict[str, str], str]:
        '''
        Load configuration from OpenBao agent, config file, or environment variables.

        Tries sources in order:
        1. OpenBao (if available and agent running)
        2. Config file (~/.config/vikunja-mcp/config.json)
        3. Environment variables (VIKUNJA_URL, VIKUNJA_TOKEN)

        Returns:
            Tuple of (config dict with 'url' and 'token', source string)
        '''
        # Try OpenBao first if available
        if OPENBAO_AVAILABLE:
            try:
                if is_agent_available():
                    config = get_mcp_config("vikunja", dev_fallbacks={
                        "token": "VIKUNJA_TOKEN",
                        "url": "VIKUNJA_URL"
                    })
                    return config, "openbao"
            except Exception:
                pass  # Fall through to config file

        # Try config file
        if CONFIG_FILE_PATH.exists():
            try:
                with open(CONFIG_FILE_PATH, 'r') as f:
                    config_data = json.load(f)
                url = config_data.get("url") or config_data.get("vikunja_url", "")
                token = config_data.get("token") or config_data.get("vikunja_token", "")
                if url and token:
                    return {"url": url, "token": token}, f"config file ({CONFIG_FILE_PATH})"
            except (json.JSONDecodeError, IOError):
                pass  # Fall through to env vars

        # Fallback to environment variables
        return {
            "url": os.environ.get("VIKUNJA_URL", ""),
            "token": os.environ.get("VIKUNJA_TOKEN", ""),
        }, "environment"

    async def _get_client(self) -> httpx.AsyncClient:
        '''Get or create the async HTTP client.

        Returns:
            httpx.AsyncClient: Configured async HTTP client with auth headers
        '''
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=REQUEST_TIMEOUT,
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                }
            )
        return self._client

    async def close(self):
        '''Close the HTTP client connection.'''
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        '''
        Make an HTTP request to the Vikunja API with error handling and retry logic.

        This is the core request method used by all API operations. It handles:
        - Bearer token authentication (automatic via client headers)
        - HTTP error responses with user-friendly messages
        - Rate limiting with exponential backoff (429 status)
        - Network timeouts and connection errors

        Args:
            method (str): HTTP method (GET, POST, PATCH, DELETE, etc.)
            endpoint (str): API endpoint path (e.g., "projects/123/tasks")
            params (Optional[Dict[str, Any]]): Query parameters for the request
            json_data (Optional[Dict[str, Any]]): JSON body for POST/PATCH requests
            **kwargs: Additional arguments passed to httpx.request()

        Returns:
            Dict[str, Any]: Parsed JSON response from the API

        Raises:
            httpx.HTTPStatusError: For HTTP error responses (4xx, 5xx)
            httpx.TimeoutException: For request timeouts
            httpx.RequestError: For network/connection errors

        Examples:
            # GET request with query parameters
            tasks = await client.request("GET", "tasks", params={"limit": 20})

            # POST request with JSON body
            task = await client.request(
                "POST",
                "projects/5/tasks",
                json_data={"title": "New task", "description": "Details"}
            )

            # PATCH request for update
            task = await client.request(
                "PATCH",
                "tasks/123",
                json_data={"done": True}
            )
        '''
        client = await self._get_client()
        url = f"{self.api_base}/{endpoint.lstrip('/')}"

        # Implement retry logic with exponential backoff for rate limiting
        for attempt in range(MAX_RETRIES):
            try:
                response = await client.request(
                    method,
                    url,
                    params=params,
                    json=json_data,
                    **kwargs
                )
                response.raise_for_status()

                # Return JSON response
                return response.json()

            except httpx.HTTPStatusError as e:
                # Handle rate limiting with exponential backoff
                if e.response.status_code == 429 and attempt < MAX_RETRIES - 1:
                    delay = RETRY_DELAY * (2 ** attempt)  # Exponential backoff
                    await asyncio.sleep(delay)
                    continue

                # For other HTTP errors or last retry, raise with helpful message
                raise

            except (httpx.TimeoutException, httpx.RequestError) as e:
                # Retry on timeout or network errors
                if attempt < MAX_RETRIES - 1:
                    delay = RETRY_DELAY * (2 ** attempt)
                    await asyncio.sleep(delay)
                    continue
                raise

        # This should never be reached due to raises above
        raise RuntimeError("Request failed after all retries")
