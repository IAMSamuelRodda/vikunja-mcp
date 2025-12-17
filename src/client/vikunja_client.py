'''
Vikunja API Client.

This module provides an async HTTP client wrapper for interacting with the
Vikunja REST API (v0.24.0+). It handles authentication, error handling, rate
limiting, and request/response management.

Credential Resolution Order:
1. OpenBao Agent (if running) - secure, memory-only caching
2. Environment variables - fallback for development/migration
'''

import os
import asyncio
from typing import Any, Dict, Optional
import httpx
from src.utils.errors import handle_api_error
from src.utils.openbao_secrets import (
    get_mcp_config,
    is_agent_available,
    AgentNotRunningError,
    SecretNotFoundError
)

# Constants
API_VERSION = "v1"
REQUEST_TIMEOUT = 30.0
MAX_RETRIES = 3
RETRY_DELAY = 1.0  # Initial delay in seconds for exponential backoff


class VikunjiaClient:
    '''
    Async HTTP client for Vikunja API.

    Handles bearer token authentication, error responses, rate limiting with
    exponential backoff, and provides a consistent interface for all API calls.

    Credentials are resolved in order:
    1. OpenBao Agent at http://127.0.0.1:8200 (if running)
    2. VIKUNJA_URL and VIKUNJA_TOKEN environment variables (fallback)

    Attributes:
        base_url (str): Base URL of the Vikunja instance
        token (str): Bearer token for authentication
        client (httpx.AsyncClient): Reusable async HTTP client
    '''

    def __init__(self):
        '''Initialize the Vikunja API client with configuration from OpenBao or environment.'''
        # Try to get config from OpenBao agent first, fallback to env vars
        config = self._load_config()

        self.base_url = config.get("url", "").rstrip("/")
        self.token = config.get("token", "")

        if not self.base_url:
            raise ValueError(
                "Vikunja URL not found. "
                "Set VIKUNJA_URL env var or configure secret/mcp/vikunja in OpenBao."
            )
        if not self.token:
            raise ValueError(
                "Vikunja token not found. "
                "Set VIKUNJA_TOKEN env var or configure secret/mcp/vikunja in OpenBao."
            )

        # Build API base URL
        self.api_base = f"{self.base_url}/api/{API_VERSION}"

        # Initialize async client (will be created lazily)
        self._client: Optional[httpx.AsyncClient] = None

    def _load_config(self) -> Dict[str, str]:
        '''
        Load configuration from OpenBao agent.

        SECURITY: Environment variable fallback only works when
        OPENBAO_DEV_MODE=1 is set. Production always requires the agent.

        Returns:
            Dict with 'url' and 'token' keys.

        Raises:
            AgentNotRunningError: If agent not running (production)
            SecretNotFoundError: If secret not found (production)
        '''
        # Try OpenBao agent (with dev-only fallback if OPENBAO_DEV_MODE=1)
        return get_mcp_config("vikunja", dev_fallbacks={
            "token": "VIKUNJA_TOKEN",
            "url": "VIKUNJA_URL"
        })

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
