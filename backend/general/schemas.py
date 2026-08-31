from collections.abc import Sequence
from enum import StrEnum
import math
from typing import Any

from pydantic import BaseModel, Field, computed_field, field_serializer

from .enums import FilterOperator, SortDirection
from .types import FilterMapping, SortMapping


class PageOf[D: BaseModel](BaseModel):
    """Страница результатов с пагинацией."""

    items: list[D] = Field(default_factory=list, description="Элементы страницы")
    page: int = Field(ge=1, default=1, description="Номер страницы")
    page_size: int = Field(default=1, description="Размер страницы")
    total: int = Field(ge=0, default=0, description="Всего элементов")

    @computed_field(description="Всего страниц")
    @property
    def total_pages(self) -> int:
        """Вычисление общего количества страниц."""
        if self.page_size == self.total:
            return 1

        return math.ceil(self.total / self.page_size)


class SearchParams(BaseModel):
    """Параметры запроса для пагинированного поиска с фильтрацией."""

    page: int = Field(ge=1, default=1, description="Номер страницы")
    page_size: int = Field(ge=1, le=100, default=30, description="Размер страницы")


class Filter[F: StrEnum](BaseModel):
    """Фильтрация по заданным полям."""

    field: F = Field(description="Фильтруемое поле")
    value: Any = Field(description="Сравнительное значение")
    operator: FilterOperator = Field(description="Оператор сравнения")

    @field_serializer("field", when_used="always")
    def field_as_str(self, field: F) -> str:
        """Представляет поле всегда как строку при любой сериализации."""
        return field.value

    def to_mapping(self) -> FilterMapping:
        """Приводит правило фильтрации в независимый формат, удобный для бизнес-логики."""
        return FilterMapping(self.model_dump())


class Sort[S: StrEnum](BaseModel):
    """Сортировка по заданным полям."""

    field: S = Field(description="Сортируемое поле")
    direction: SortDirection = Field(default=SortDirection.ASC, description="Направление")

    @field_serializer("field", when_used="always")
    def field_as_str(self, field: S) -> str:
        """Представляет поле всегда как строку при любой сериализации."""
        return field.value

    def to_mapping(self) -> SortMapping:
        """Приводит сортировки в независимый формат, удобный для бизнес-логики."""
        return SortMapping(self.model_dump())


class SearchBody[F: StrEnum, S: StrEnum](BaseModel):
    """Параметры тела запроса для пагинированного поиска с фильтрацией."""

    filters: Sequence[Filter[F]] = Field(description="Список фильтров по полям ресурса")
    sorts: Sequence[Sort[S]] = Field(description="Список сортировок по полям ресурса")
