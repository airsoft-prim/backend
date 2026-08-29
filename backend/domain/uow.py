from __future__ import annotations

from types import TracebackType
from typing import Self, cast

from sqlalchemy.ext.asyncio import AsyncSession

from ._types import SessionFactory
from .container import Container
from .repositories.database import DatabaseRepository


class UnitOfWork:
    """Единица работы.

    Открывает сессию через фабрику сессий из контейнера зависимостей,
    берёт из контейнера классы репозиториев и спавнит их на этой сессии,
    управляет транзакцией: commit при успешном выходе из контекста,
    rollback при ошибке.
    """

    def __init__(self, container: Container) -> None:
        """Инициализация единицы работы.

        Args:
            container (Container): Контейнер зависимостей с фабрикой сессий.
        """
        self._container = container
        self._session: AsyncSession | None = None

    @property
    def session(self) -> AsyncSession:
        """Текущая сессия БД.

        Raises:
            RuntimeError: Если сессия ещё не открыта (вне контекста).
        """
        if self._session is None:
            msg = "Session is not opened. Use UnitOfWork as async context manager."
            raise RuntimeError(msg)

        return self._session

    # TODO: Подумать над реализацией для ЛЮБОГО репозитория.
    # * Пока что этот метод выглядит слишком узким.
    def database_repository[R: DatabaseRepository](self, repository: type[R]) -> R:
        """Спавнит репозиторий на текущей сессии, беря его класс из контейнера.

        Args:
            repository (type[R]): Тип-ключ репозитория в контейнере.

        Returns:
            R: Экземпляр репозитория, привязанный к сессии единицы работы.
        """
        repository_type = self._container.get(repository)

        return cast(type[R], repository_type)(self.session)

    async def __aenter__(self) -> Self:
        """Открывает сессию и возвращает единицу работы."""
        session_factory = self._container.get(SessionFactory)
        self._session = session_factory()

        return self

    async def __aexit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc: BaseException | None,
        _traceback: TracebackType | None,
    ) -> None:
        """Завершает транзакцию: commit или rollback, затем закрывает сессию."""
        if self._session is None:
            return

        try:
            await (self._session.rollback() if _exc_type else self._session.commit())

        finally:
            await self._session.close()
            self._session = None
