from collections.abc import Sequence
from enum import StrEnum
import math
from typing import Any

from pydantic import BaseModel, Field, computed_field, field_serializer

from .enums import FilterOperator, SortDirection
from .types import FilterMapping, SortMapping


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

    @field_serializer("field", when_used="always")
    def field_as_str(self, field: F) -> str:
        """_summary_"""
        return field.value

    def to_mapping(self) -> FilterMapping:
        """_summary_"""
        return FilterMapping(self.model_dump())


class Sort[S: StrEnum](BaseModel):
    """Сортировка по заданным полям."""

    field: S
    direction: SortDirection = Field(default=SortDirection.ASC)

    @field_serializer("field", when_used="always")
    def field_as_str(self, field: S) -> str:
        """_summary_"""
        return field.value

    def to_mapping(self) -> SortMapping:
        """_summary_"""
        return SortMapping(self.model_dump())


class SearchBody[F: StrEnum, S: StrEnum](BaseModel):
    """Параметры тела запроса  для пагинированного поиска с фильтрацией."""

    filers: Sequence[Filter[F]]
    sorts: Sequence[Sort[S]]
