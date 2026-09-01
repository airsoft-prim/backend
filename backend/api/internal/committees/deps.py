from typing import Annotated

from fastapi import Depends

from backend.domain import Container, create_container
from backend.domain._types import SessionFactory
from backend.domain.repositories.database import (
    UnionMembersRepository,
    UnionsRepository,
    UsersRepository,
)
from backend.domain.services import CommitteesService
from backend.providers.database import async_session


async def get_committees_service_container() -> Container:
    """Возвращает контейнер зависимостей для текущего запроса.

    Returns:
        Container: Контейнер зависимостей запроса.
    """
    repos = [UnionsRepository, UnionMembersRepository, UsersRepository]
    container = create_container(*repos)

    # Фабрикой сессий служит sessionmaker: генератор get_session
    # рассчитан на FastAPI-DI и здесь не подходит.
    container.register(async_session, as_type=SessionFactory)

    return container


async def get_committees_service(
    container: Annotated[Container, Depends(get_committees_service_container)],
) -> CommitteesService:
    """Возвращает сервис орг-комитетов на контейнере текущего запроса.

    Args:
        container (Annotated[Container, Depends]): Контейнер зависимостей.

    Returns:
        CommitteesService: Сервис орг-комитетов.
    """
    return CommitteesService(container=container)
