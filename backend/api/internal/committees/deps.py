from typing import Annotated

from fastapi import Depends

from backend.domain import Container, create_container
from backend.domain._types import SessionFactory
from backend.domain.repositories.database import (
    UnionMembersRepository,
    UnionsRepository,
    UsersRepository,
)
from backend.domain.services import CommitteesService, MembersService
from backend.providers.database import async_session


async def unions_container() -> Container:
    """Возвращает контейнер зависимостей сервиса орг-комитетов.

    Регистрируются только репозитории, нужные CommitteesService.

    Returns:
        Container: Контейнер зависимостей запроса.
    """
    repos = [UnionsRepository, UnionMembersRepository, UsersRepository]
    container = create_container(*repos)

    container.register(async_session, as_type=SessionFactory)

    return container


async def members_container() -> Container:
    """Возвращает контейнер зависимостей сервиса участников.

    Регистрируются только репозитории, нужные MembersService.

    Returns:
        Container: Контейнер зависимостей запроса.
    """
    repos = [UnionMembersRepository, UsersRepository]
    container = create_container(*repos)

    container.register(async_session, as_type=SessionFactory)

    return container


async def get_committees_service(
    container: Annotated[Container, Depends(unions_container)],
) -> CommitteesService:
    """Возвращает сервис орг-комитетов на контейнере текущего запроса.

    Args:
        container (Annotated[Container, Depends]): Контейнер зависимостей.

    Returns:
        CommitteesService: Сервис орг-комитетов.
    """
    return CommitteesService(container=container)


async def get_members_service(
    container: Annotated[Container, Depends(members_container)],
) -> MembersService:
    """Возвращает сервис участников на контейнере текущего запроса.

    Args:
        container (Annotated[Container, Depends]): Контейнер зависимостей.

    Returns:
        MembersService: Сервис участников объединений.
    """
    return MembersService(container=container)
