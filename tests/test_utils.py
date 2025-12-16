'''Unit tests for utility modules.'''

import pytest
import httpx
from unittest.mock import MagicMock
from src.utils.errors import handle_api_error
from src.utils.formatters import (
    format_timestamp,
    format_priority,
    format_task_markdown,
    format_json_response,
    truncate_response
)
from src.utils.pagination import build_pagination_response


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

def test_handle_api_error_401():
    '''Test 401 authentication error formatting.'''
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"

    error = httpx.HTTPStatusError("401", request=MagicMock(), response=mock_response)
    result = handle_api_error(error)

    assert "Invalid or expired authentication token" in result
    assert "VIKUNJA_TOKEN" in result


def test_handle_api_error_404():
    '''Test 404 not found error formatting.'''
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"

    error = httpx.HTTPStatusError("404", request=MagicMock(), response=mock_response)
    result = handle_api_error(error)

    assert "Resource not found" in result
    assert "ID is correct" in result


def test_handle_api_error_429():
    '''Test 429 rate limit error formatting.'''
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.text = "Too Many Requests"

    error = httpx.HTTPStatusError("429", request=MagicMock(), response=mock_response)
    result = handle_api_error(error)

    assert "Rate limit exceeded" in result
    assert "too many requests" in result


def test_handle_api_error_500():
    '''Test 500 server error formatting.'''
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"

    error = httpx.HTTPStatusError("500", request=MagicMock(), response=mock_response)
    result = handle_api_error(error)

    assert "Server error" in result
    assert "500" in result


def test_handle_api_error_403():
    '''Test 403 forbidden error formatting.'''
    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.text = "Forbidden"

    error = httpx.HTTPStatusError("403", request=MagicMock(), response=mock_response)
    result = handle_api_error(error)

    assert "Permission denied" in result


def test_handle_api_error_generic_http():
    '''Test generic HTTP error formatting.'''
    mock_response = MagicMock()
    mock_response.status_code = 418
    mock_response.text = "I'm a teapot"

    error = httpx.HTTPStatusError("418", request=MagicMock(), response=mock_response)
    result = handle_api_error(error)

    assert "HTTP 418" in result
    assert "I'm a teapot" in result


def test_handle_api_error_network_error():
    '''Test network error formatting.'''
    error = httpx.ConnectError("Connection refused")
    result = handle_api_error(error)

    assert "Network error" in result
    assert "VIKUNJA_URL" in result


def test_handle_api_error_timeout():
    '''Test timeout error formatting.'''
    error = httpx.TimeoutException("Request timed out")
    result = handle_api_error(error)

    assert "Request timed out" in result


def test_handle_api_error_generic_exception():
    '''Test generic exception formatting.'''
    error = ValueError("Something went wrong")
    result = handle_api_error(error)

    assert "Error" in result
    assert "Something went wrong" in result


# ============================================================================
# FORMATTER TESTS
# ============================================================================

def test_format_timestamp_valid_iso():
    '''Test timestamp formatting with valid ISO 8601 string.'''
    result = format_timestamp("2025-12-25T09:00:00Z")
    assert "2025-12-25" in result
    assert "09:00" in result


def test_format_timestamp_none():
    '''Test timestamp formatting with None.'''
    result = format_timestamp(None)
    assert result == "Not set"


def test_format_timestamp_empty_string():
    '''Test timestamp formatting with empty string.'''
    result = format_timestamp("")
    assert result == "Not set"


def test_format_priority_levels():
    '''Test priority formatting for all levels.'''
    assert format_priority(0) == "None"
    assert format_priority(1) == "Low (1)"
    assert format_priority(2) == "Medium (2)"
    assert format_priority(3) == "High (3)"
    assert format_priority(4) == "Urgent (4)"
    assert format_priority(5) == "Critical (5)"
    assert format_priority(99) == "Unknown (99)"


def test_format_task_markdown_basic():
    '''Test basic task markdown formatting.'''
    task = {
        "id": 123,
        "title": "Test Task",
        "done": False
    }

    result = format_task_markdown(task, detailed=False)

    assert "○ Test Task (#123)" in result
    assert "##" in result


def test_format_task_markdown_completed():
    '''Test completed task markdown formatting.'''
    task = {
        "id": 456,
        "title": "Done Task",
        "done": True
    }

    result = format_task_markdown(task, detailed=False)

    assert "✓ Done Task (#456)" in result


def test_format_task_markdown_detailed():
    '''Test detailed task markdown formatting.'''
    task = {
        "id": 789,
        "title": "Detailed Task",
        "description": "This is a description",
        "priority": 4,
        "due_date": "2025-12-31T23:59:59Z",
        "done": False,
        "labels": [
            {"title": "bug", "hex_color": "#FF0000"}
        ]
    }

    result = format_task_markdown(task, detailed=True)

    assert "Detailed Task" in result
    assert "This is a description" in result
    assert "Urgent (4)" in result
    assert "2025-12-31" in result
    assert "bug" in result


def test_format_json_response_dict():
    '''Test JSON response formatting for dict.'''
    data = {"id": 1, "name": "Test"}
    result = format_json_response(data)

    assert '"id": 1' in result
    assert '"name": "Test"' in result


def test_format_json_response_list():
    '''Test JSON response formatting for list.'''
    data = [{"id": 1}, {"id": 2}]
    result = format_json_response(data)

    assert '"id": 1' in result
    assert '"id": 2' in result


def test_truncate_response_short_text():
    '''Test truncate_response with text under limit.'''
    text = "Short text"
    result = truncate_response(text)
    assert result == "Short text"


def test_truncate_response_long_text():
    '''Test truncate_response with text over limit.'''
    text = "x" * 30000
    result = truncate_response(text, truncation_message="... [TRUNCATED]")

    assert len(result) < 30000
    assert result.endswith("... [TRUNCATED]")


# ============================================================================
# PAGINATION TESTS
# ============================================================================

def test_build_pagination_response_first_page():
    '''Test pagination for first page with more results.'''
    items = [{"id": i} for i in range(1, 21)]
    result = build_pagination_response(items, total=100, limit=20, offset=0)

    assert result["total"] == 100
    assert result["count"] == 20
    assert result["limit"] == 20
    assert result["offset"] == 0
    assert result["has_more"] is True
    assert result["next_offset"] == 20


def test_build_pagination_response_middle_page():
    '''Test pagination for middle page.'''
    items = [{"id": i} for i in range(21, 41)]
    result = build_pagination_response(items, total=100, limit=20, offset=20)

    assert result["total"] == 100
    assert result["count"] == 20
    assert result["offset"] == 20
    assert result["has_more"] is True
    assert result["next_offset"] == 40


def test_build_pagination_response_last_page():
    '''Test pagination for last page.'''
    items = [{"id": i} for i in range(81, 101)]
    result = build_pagination_response(items, total=100, limit=20, offset=80)

    assert result["total"] == 100
    assert result["count"] == 20
    assert result["offset"] == 80
    assert result["has_more"] is False
    assert result["next_offset"] is None


def test_build_pagination_response_partial_last_page():
    '''Test pagination for partial last page.'''
    items = [{"id": i} for i in range(91, 96)]
    result = build_pagination_response(items, total=95, limit=20, offset=80)

    assert result["total"] == 95
    assert result["count"] == 15
    assert result["has_more"] is False
    assert result["next_offset"] is None


def test_build_pagination_response_empty():
    '''Test pagination with no results.'''
    result = build_pagination_response([], total=0, limit=20, offset=0)

    assert result["total"] == 0
    assert result["count"] == 0
    assert result["has_more"] is False
    assert result["next_offset"] is None
