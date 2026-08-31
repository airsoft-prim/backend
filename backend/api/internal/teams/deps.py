from typing import Annotated

from fastapi import Depends

from backend.domain import Container, create_container
from backend.domain._types import SessionFactory
from backend.domain.repositories.database import (
    UnionMembersRepository,
    UnionsRepository,
    UsersRepository,
)
from backend.domain.services import TeamsService
from backend.providers.database import get_session


async def get_teams_service_container() -> Container:
    """Возвращает контейнер зависимостей для текущего запроса.

    Returns:
        Container: Контейнер зависимостей запроса.
    """
    repos = [UnionsRepository, UnionMembersRepository, UsersRepository]
    container = create_container(*repos)

    container.register(get_session, as_type=SessionFactory)

    return container


async def get_teams_service(
    container: Annotated[Container, Depends(get_teams_service_container)],
) -> TeamsService:
    """Возвращает сервис команд на контейнере текущего запроса.

    Args:
        container (Annotated[Container, Depends]): Контейнер зависимостей.

    Returns:
        TeamsService: Сервис команд.
    """
    return TeamsService(container=container)
