from typing import Annotated

from fastapi import Body, Depends, Path, Query

from backend.api.internal.teams.deps import get_teams_service
from backend.domain.services import TeamsService
from backend.general.schemas import PageOf

from . import router
from .docs import (
    ADD_MEMBER_DOCS,
    CREATE_TEAM_DOCS,
    GET_MEMBER_DOCS,
    GET_MEMBERS_DOCS,
    GET_TEAM_DOCS,
    REMOVE_MEMBER_DOCS,
    SEARCH_TEAMS_DOCS,
    UPDATE_MEMBER_DOCS,
    UPDATE_TEAM_DOCS,
)
from .schemas import (
    CreatedTeam,
    CreateTeamBody,
    SearchTeamsBody,
    SearchTeamsParams,
    Team,
    TeamRecord,
    UpdateTeamBody,
)


@router.post("/search", **SEARCH_TEAMS_DOCS)
async def search_teams(
    params: Annotated[SearchTeamsParams, Query()],
    body: Annotated[SearchTeamsBody, Body()],
    service: Annotated[TeamsService, Depends(get_teams_service)],
) -> PageOf[TeamRecord]:
    """Ищет команды по фильтрам с сортировкой и пагинацией.

    Args:
        params (Annotated[SearchTeamsParams, Query]): Параметры пагинации.
        body (Annotated[SearchTeamsBody, Body]): Фильтры и сортировки.
        service (Annotated[TeamsService, Depends]): Сервис команд.

    Returns:
        PageOf[TeamRecord]: Страница команд.
    """
    items, total = await service.search(
        page=params.page,
        page_size=params.page_size,
        filters=[f.to_mapping() for f in body.filters],
        sorts=[s.to_mapping() for s in body.sorts],
    )

    return PageOf[TeamRecord](
        items=map(TeamRecord.model_validate, items),
        page=params.page,
        page_size=params.page_size,
        total=total,
    )


@router.post("/", **CREATE_TEAM_DOCS)
async def create_team(
    body: Annotated[CreateTeamBody, Body()],
    service: Annotated[TeamsService, Depends(get_teams_service)],
) -> CreatedTeam:
    """Создаёт команду вместе с профилем и первым участником.

    Args:
        body (Annotated[CreateTeamBody, Body]): Данные создаваемой команды.
        service (Annotated[TeamsService, Depends]): Сервис команд.

    Returns:
        CreatedTeam: Идентификатор и название созданной команды.
    """
    team = await service.create(
        creator_id=0,  # TODO: Заменить на авторизованного пользователя
        name=body.name,
        city=body.city,
        motto=body.motto,
        avatar_url=body.avatar_url,
    )

    return CreatedTeam.model_validate(team)


@router.get("/{team_id}", **GET_TEAM_DOCS)
async def get_team(
    team_id: Annotated[int, Path],
    service: Annotated[TeamsService, Depends(get_teams_service)],
) -> Team:
    """Возвращает команду по её идентификатору.

    Args:
        team_id (Annotated[int, Path]): Идентификатор команды.
        service (Annotated[TeamsService, Depends]): Сервис команд.

    Returns:
        Team: Полные данные о команде.
    """
    team = await service.get(team_id)

    return Team.model_validate(team)


@router.patch("/{team_id}", **UPDATE_TEAM_DOCS)
async def update_team(
    team_id: Annotated[int, Path],
    body: Annotated[UpdateTeamBody, Body()],
    service: Annotated[TeamsService, Depends(get_teams_service)],
) -> Team:
    """Обновляет данные команды.

    Args:
        team_id ( Annotated[int, Path]): Идентификатор команды.
        body (Annotated[UpdateTeamBody, Body]): Обновляемые поля.
        service (Annotated[TeamsService, Depends]): Сервис команд.

    Returns:
        Team: Полные, обновлённые данные команды.
    """
    changes = body.model_dump(exclude_none=True)

    team = await service.update(team_id=team_id, **changes)

    return Team.model_validate(team)


@router.get("/{team_id}/members", **GET_MEMBERS_DOCS)
async def get_team_members() -> None:
    pass


@router.post("/{team_id}/members", **ADD_MEMBER_DOCS)
async def add_team_member() -> None:
    pass


@router.get("/{team_id}/members/{member_id}", **GET_MEMBER_DOCS)
async def get_team_member() -> None:
    pass


@router.patch("/{team_id}/members/{member_id}", **UPDATE_MEMBER_DOCS)
async def update_team_member() -> None:
    pass


@router.delete("/{team_id}/members/{member_id}", **REMOVE_MEMBER_DOCS)
async def remove_team_member() -> None:
    pass
