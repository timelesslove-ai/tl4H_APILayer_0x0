"""
Pagination utility for API responses.
Provides consistent pagination behavior across all list endpoints.
"""

"""
Pagination utility for API responses.
Provides consistent pagination behavior across all list endpoints.
"""

from math import ceil
from typing import Any, Dict, Generic, List, Optional, Sequence, TypeVar, Union

from fastapi import Depends, Query
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

T = TypeVar('T')


class PaginationParams:
    """Common pagination parameters for all list endpoints"""
    def __init__(
        self, 
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(20, ge=1, le=100, description="Items per page"),
        sort_by: Optional[str] = Query(None, description="Field to sort by"),
        sort_order: str = Query("asc", description="Sort order (asc or desc)")
    ):
        self.page = page
        self.size = size
        self.sort_by = sort_by
        self.sort_order = sort_order.lower()
        self.offset = (page - 1) * size


class Page(GenericModel, Generic[T]):
    """Standard pagination response model"""
    items: List[T]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool
    
    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def create(cls, items: List[T], total: int, params: PaginationParams) -> "Page[T]":
        """Create a pagination response from items and total count"""
        pages = ceil(total / params.size) if total > 0 else 0
        return cls(
            items=items,
            total=total,
            page=params.page,
            size=params.size,
            pages=pages,
            has_next=params.page < pages,
            has_prev=params.page > 1
        )


class CursorPage(GenericModel, Generic[T]):
    """Cursor-based pagination response model for timeline-style pagination"""
    items: List[T]
    total: int
    next_cursor: Optional[str] = None
    prev_cursor: Optional[str] = None
    has_more: bool = False
    
    class Config:
        arbitrary_types_allowed = True


async def paginate(
    db: AsyncSession,
    query,
    params: PaginationParams,
    schema_class = None
) -> Page:
    """
    Execute a paginated query and return standardized pagination response
    
    Args:
        db: Database session
        query: SQLAlchemy select statement
        params: Pagination parameters
        schema_class: Optional Pydantic model to convert results
        
    Returns:
        Page object containing paginated results
    """
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)
    
    # Apply sorting if specified
    if params.sort_by:
        if hasattr(query.column_descriptions[0]['entity'], params.sort_by):
            sort_column = getattr(query.column_descriptions[0]['entity'], params.sort_by)
            query = query.order_by(
                sort_column.desc() if params.sort_order == "desc" else sort_column
            )
    
    # Apply pagination
    query = query.offset(params.offset).limit(params.size)
    
    # Execute query
    result = await db.execute(query)
    items = result.scalars().all()
    
    # Convert to pydantic models if schema provided
    if schema_class:
        items = [schema_class.from_orm(item) for item in items]
    
    return Page.create(items, total, params)


async def cursor_paginate(
    db: AsyncSession,
    query,
    cursor_field: str,
    limit: int = 20,
    cursor: Optional[str] = None,
    direction: str = "forward",
    schema_class = None
) -> CursorPage:
    """
    Execute a cursor-based paginated query, ideal for timeline views
    
    Args:
        db: Database session
        query: SQLAlchemy select statement
        cursor_field: Field to use for cursor (typically timestamp)
        limit: Maximum items to return
        cursor: Encoded cursor for pagination
        direction: 'forward' or 'backward'
        schema_class: Optional Pydantic model to convert results
        
    Returns:
        CursorPage object containing paginated results with cursor info
    """
    # Get total count for the base query
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)
    
    # Default ordering by the cursor field descending (newest first)
    model = query.column_descriptions[0]['entity']
    cursor_column = getattr(model, cursor_field)
    
    # Apply cursor if provided
    if cursor:
        decoded_cursor = _decode_cursor(cursor)
        if direction == "forward":
            query = query.where(cursor_column < decoded_cursor)
            query = query.order_by(cursor_column.desc())
        else:
            query = query.where(cursor_column > decoded_cursor)
            query = query.order_by(cursor_column.asc())
    else:
        # First page, just sort
        query = query.order_by(cursor_column.desc() if direction == "forward" else cursor_column.asc())
    
    # Apply limit with one extra to check for more items
    query = query.limit(limit + 1)
    
    # Execute query
    result = await db.execute(query)
    items = result.scalars().all()
    
    # Check if there are more items
    has_more = len(items) > limit
    if has_more:
        items = items[:limit]
    
    # Get cursors for next/prev page
    next_cursor = None
    prev_cursor = None
    
    if items and has_more:
        last_item = items[-1]
        next_cursor = _encode_cursor(getattr(last_item, cursor_field))
    
    if items and (cursor or direction == "backward"):
        first_item = items[0]
        prev_cursor = _encode_cursor(getattr(first_item, cursor_field))
    
    # Convert to pydantic models if schema provided
    if schema_class:
        items = [schema_class.from_orm(item) for item in items]
    
    # If we were going backward, reverse the items to maintain expected order
    if direction == "backward":
        items.reverse()
    
    return CursorPage(
        items=items,
        total=total,
        next_cursor=next_cursor,
        prev_cursor=prev_cursor,
        has_more=has_more
    )


def _encode_cursor(value: Any) -> str:
    """Simple cursor encoding - would use base64 in production"""
    return str(value)


def _decode_cursor(cursor: str) -> Any:
    """Simple cursor decoding - would use base64 in production"""
    return cursor