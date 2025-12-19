'''
Error handling utilities for Vikunja MCP server.

This module provides consistent, user-friendly error formatting across all tools.
Error messages are designed to be actionable and guide LLMs toward correct usage.
'''

import httpx


def handle_api_error(e: Exception) -> str:
    '''
    Convert API exceptions to clear, actionable error messages for LLMs.

    This function transforms technical HTTP and network errors into natural language
    messages that:
    - Explain what went wrong in clear terms
    - Suggest specific next steps to resolve the issue
    - Avoid exposing internal implementation details
    - Guide the LLM toward correct tool usage

    Args:
        e (Exception): The exception to handle (typically httpx exceptions)

    Returns:
        str: User-friendly error message with actionable guidance

    Examples:
        >>> try:
        ...     response = await client.get("/invalid")
        ... except httpx.HTTPStatusError as e:
        ...     return handle_api_error(e)
        "Error: Resource not found. Please check the ID is correct and try listing available resources first."
    '''
    # Check for credential/OpenBao errors first (before generic errors)
    error_str = str(e).lower()
    if isinstance(e, ValueError) and ("openbao" in error_str or "token" in error_str or "agent" in error_str):
        # Pass through the detailed ValueError from credential functions
        return f"Error: {str(e)}"

    if isinstance(e, httpx.HTTPStatusError):
        status = e.response.status_code

        if status == 401:
            return (
                "Error: Invalid or expired authentication token. "
                "Please check that VIKUNJA_TOKEN is correct and has not expired."
            )
        elif status == 403:
            return (
                "Error: Permission denied. You don't have access to this resource. "
                "Please check your user permissions in Vikunja."
            )
        elif status == 404:
            return (
                "Error: Resource not found. Please check the ID is correct and "
                "try listing available resources first."
            )
        elif status == 429:
            return (
                "Error: Rate limit exceeded. The Vikunja API is receiving too many requests. "
                "Please wait a moment before making more requests. The request will be "
                "automatically retried with exponential backoff."
            )
        elif status == 422:
            # Validation error - try to extract details if available
            try:
                error_detail = e.response.json()
                if "message" in error_detail:
                    return f"Error: Validation failed - {error_detail['message']}"
            except:
                pass
            return (
                "Error: Invalid request data. Please check that all required parameters "
                "are provided and have valid values."
            )
        elif status == 500:
            return (
                "Error: Vikunja server error (500). The server encountered an internal error. "
                "Please try again later or contact the Vikunja administrator."
            )
        elif status == 503:
            return (
                "Error: Vikunja service unavailable (503). The server may be under maintenance. "
                "Please try again later."
            )
        else:
            return f"Error: API request failed with status {status}. Please try again."

    elif isinstance(e, httpx.TimeoutException):
        return (
            "Error: Request timed out. The Vikunja server took too long to respond. "
            "Please check your network connection and try again."
        )

    elif isinstance(e, httpx.ConnectError):
        return (
            "Error: Cannot connect to Vikunja server. Please check that VIKUNJA_URL "
            "is correct and the server is accessible."
        )

    elif isinstance(e, httpx.RequestError):
        return (
            "Error: Network error occurred. Please check your connection to the Vikunja server "
            f"and try again. ({type(e).__name__})"
        )

    # Generic fallback for unexpected errors
    return f"Error: Unexpected error occurred - {type(e).__name__}. Please try again."
