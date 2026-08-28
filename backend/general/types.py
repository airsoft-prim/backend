from collections.abc import Awaitable, Callable
from enum import Enum
import math
from typing import TypedDict

from fastapi import Request, Response
from pydantic import BaseModel, Field, computed_field

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


class PageOf[D: BaseModel](BaseModel):
    """Страница результатов с пагинацией."""

    items: list[D] = Field(default_factory=list)
    page: int = Field(ge=1, default=1)
    total: int = Field(ge=0, default=0)
    page_size: int = Field(default=1)

    @computed_field
    @property
    def total_pages(self) -> int:
        """Вычисление общего кол-ва страниц."""
        if self.page_size == self.total:
            return 1

        return math.ceil(self.total / self.page_size)
