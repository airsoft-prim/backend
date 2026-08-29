from collections.abc import Awaitable, Callable
from enum import Enum
from typing import Any, TypedDict

from fastapi import Request, Response

from .enums import FilterOperator, SortDirection

type CallNext = Callable[[Request], Awaitable[Response]]


class RouteDocs(TypedDict, total=False):
    """Формат документирующих данных к пути API."""

    summary: str
    operation_id: str
    description: str
    status_code: int
    deprecated: bool
    tags: list[str | Enum]
    response_description: str


class FilterMapping(TypedDict, total=True):
    """_summary_"""

    field: str
    value: Any
    operator: FilterOperator


class SortMapping(TypedDict, total=True):
    """_summary_"""

    field: str
    direction: SortDirection
