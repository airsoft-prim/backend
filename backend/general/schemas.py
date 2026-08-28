from collections.abc import Sequence
from enum import StrEnum
import math
from typing import Any

from pydantic import BaseModel, Field, computed_field

from .enums import FilterOperator, SortDirection


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


class SearchParams(BaseModel):
    """Параметры запроса для пагинированного поиска с фильтрацией."""

    page: int = Field(ge=1, default=100)
    page_size: int = Field(ge=1, le=100, default=30)


class Filter[F: StrEnum](BaseModel):
    """Фильтрация по заданным полям."""

    field: F
    value: Any
    operator: FilterOperator


class Sort[S: StrEnum](BaseModel):
    """Сортировка по заданным полям."""

    field: S
    direction: SortDirection = Field(default=SortDirection.ASC)


class SearchBody[F: StrEnum, S: StrEnum](BaseModel):
    """Параметры тела запроса  для пагинированного поиска с фильтрацией."""

    filers: Sequence[Filter[F]]
    sorts: Sequence[Sort[S]]
