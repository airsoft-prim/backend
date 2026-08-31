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
    deprecated: bool
    tags: list[str | Enum]
    status_code: int
    response_description: str
    responses: dict[int | str, dict[str, Any]] | None


class FilterMapping(TypedDict, total=True):
    """Правило фильтрации в независимом от API формате."""

    field: str
    value: Any
    operator: FilterOperator


class SortMapping(TypedDict, total=True):
    """Правило сортировки в независимом от API формате."""

    field: str
    direction: SortDirection
