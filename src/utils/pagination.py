'''
Pagination utilities for Vikunja MCP server.

This module provides helpers for managing pagination in list operations,
building pagination metadata, and handling page/limit parameters.
'''

from typing import Dict, Any, Optional


def build_pagination_response(
    items: list,
    total: int,
    limit: int,
    offset: int
) -> Dict[str, Any]:
    '''
    Build standardized pagination response metadata.

    Args:
        items (list): The items in the current page
        total (int): Total number of items available
        limit (int): Maximum number of items per page
        offset (int): Current pagination offset

    Returns:
        Dict[str, Any]: Pagination metadata with has_more and next_offset

    Example:
        >>> build_pagination_response(tasks, total=150, limit=20, offset=0)
        {
            "total": 150,
            "count": 20,
            "limit": 20,
            "offset": 0,
            "has_more": True,
            "next_offset": 20
        }
    '''
    count = len(items)
    has_more = (offset + count) < total
    next_offset = (offset + count) if has_more else None

    return {
        "total": total,
        "count": count,
        "limit": limit,
        "offset": offset,
        "has_more": has_more,
        "next_offset": next_offset
    }


def validate_pagination_params(
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    default_limit: int = 20,
    max_limit: int = 100
) -> tuple[int, int]:
    '''
    Validate and normalize pagination parameters.

    Args:
        limit (Optional[int]): Requested page size
        offset (Optional[int]): Requested offset
        default_limit (int): Default limit if not provided
        max_limit (int): Maximum allowed limit

    Returns:
        tuple[int, int]: Validated (limit, offset) pair

    Example:
        >>> validate_pagination_params(limit=150, offset=-5)
        (100, 0)  # Clamped to max_limit and minimum offset
    '''
    # Validate limit
    if limit is None:
        limit = default_limit
    else:
        limit = max(1, min(limit, max_limit))

    # Validate offset
    if offset is None:
        offset = 0
    else:
        offset = max(0, offset)

    return limit, offset
