from collections.abc import Awaitable, Callable
from enum import Enum
from typing import TypedDict

from fastapi import Request, Response

type CallNext = Callable[[Request], Awaitable[Response]]


class RouteDocs(TypedDict, total=False):
    """Формат документирующих данных к пути API."""

    summary: str
    description: str
    status_code: int
    deprecated: bool
    tags: list[str | Enum]
    response_description: str
