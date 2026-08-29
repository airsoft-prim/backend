from typing import Any, Protocol

from sqlalchemy.ext.asyncio import AsyncSession


class SessionFactory(Protocol):
    """Протокол фабрики асинхронных сессий БД."""

    def __call__(self, *args: Any, **kwargs: Any) -> AsyncSession: ...
