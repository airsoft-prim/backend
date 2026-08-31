"""Абстракция поисковых сервисов: контракт постраничного поиска
с фильтрацией и сортировкой.
"""

from abc import ABC, abstractmethod
from typing import Any, ClassVar, Protocol

from backend.general.types import FilterMapping, SortMapping

from ._base import Service


class DataclassInstance(Protocol):
    """Протокол экземпляра dataclass - runtime-замена `_typeshed.DataclassInstance`.

    `_typeshed.DataclassInstance` живёт только в стабах typeshed — эталонном
    описании стандартной библиотеки для статических анализаторов. Сам модуль
    `_typeshed` не поставляется вместе с интерпретатором: на этапе исполнения
    `from _typeshed import DataclassInstance` падает с `ModuleNotFoundError`
    и ломает импорт всего пакета.
    """

    __dataclass_fields__: ClassVar[dict[str, Any]]


class ServiceWithSearch[D: DataclassInstance](Service, ABC):
    """Базовый абстрактный сервиса с поиском записей.

    Возвращает страницу записей-датаклассов (DTO) типа `D`, отобранных
    и упорядоченных по переданным правилам фильтрации и сортировки.
    """

    @abstractmethod
    async def search(
        self, page: int, page_size: int, filters: list[FilterMapping], sorts: list[SortMapping]
    ) -> tuple[list[D], int]:
        """Выполняет поиск и возвращает страницу записей.

        Args:
            page (int): Номер запрашиваемой страницы.
            page_size (int): Количество записей на странице.
            filters (list[FilterMapping]): Правила фильтрации записей.
            sorts (list[SortMapping]): Правила сортировки записей.

        Raises:
            NotImplementedError: Если метод не реализован в наследнике.

        Returns:
            tuple[list[D], int]: Записи страницы и общее число записей.
        """
        message = "Method not implemented in child class."
        raise NotImplementedError(message) from None
