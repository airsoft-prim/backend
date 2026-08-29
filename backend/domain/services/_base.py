"""Базовый класс сервиса приложения."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from backend.domain.container import Container
from backend.domain.uow import UnitOfWork


class Service:
    """Базовый класс сервиса приложения.

    Сервис принимает контейнер зависимостей и через него работает
    с UnitOfWork: репозитории спавнятся, транзакции контролируются
    внутри контекста единицы работы.
    """

    def __init__(self, container: Container) -> None:
        """Инициализация сервиса.

        Args:
            container (Container): Контейнер зависимостей сервиса.
        """
        self._container = container

    @property
    def container(self) -> Container:
        """Контейнер зависимостей сервиса."""
        return self._container

    @asynccontextmanager
    async def unit_of_work(self) -> AsyncIterator[UnitOfWork]:
        """Открывает UnitOfWork на время выполнения блока.

        Yields:
            AsyncIterator[UnitOfWork]: Единица работы с репозиториями
                и транзакцией.
        """
        async with UnitOfWork(self._container) as uow:
            yield uow
