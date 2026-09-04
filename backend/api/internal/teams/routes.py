from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, Query

from backend.api.internal.teams.deps import get_members_service, get_teams_service
from backend.domain.services import MembersService, TeamsService
from backend.general.schemas import PageOf
from backend.general.security.types import UserSession

from .docs import (
    ADD_MEMBER_DOCS,
    CREATE_TEAM_DOCS,
    GET_MEMBERS_DOCS,
    GET_TEAM_DOCS,
    REMOVE_MEMBER_DOCS,
    SEARCH_TEAMS_DOCS,
    UPDATE_MEMBER_DOCS,
    UPDATE_TEAM_DOCS,
)
from .schemas import (
    AddMemberBody,
    CreatedTeam,
    CreateTeamBody,
    Member,
    SearchTeamsBody,
    SearchTeamsParams,
    Team,
    TeamRecord,
    UpdateMemberBody,
    UpdateTeamBody,
)
from .security import COMMON_TEAMS_SEC

router = APIRouter(prefix="/teams", tags=["Команды"])


@router.post("/search", **SEARCH_TEAMS_DOCS)
async def search_teams(
    params: Annotated[SearchTeamsParams, Query()],
    body: Annotated[SearchTeamsBody, Body()],
    teams_service: Annotated[TeamsService, Depends(get_teams_service)],
    _session: Annotated[UserSession, COMMON_TEAMS_SEC],
) -> PageOf[TeamRecord]:
    """Ищет команды по фильтрам с сортировкой и пагинацией.

    Args:
        params (Annotated[SearchTeamsParams, Query]): Параметры пагинации.
        body (Annotated[SearchTeamsBody, Body]): Фильтры и сортировки.
        teams_service (Annotated[TeamsService, Depends]): Сервис команд.
        _session (Annotated[UserSession, Security]): Авторизованная сессия пользователя.

    Returns:
        PageOf[TeamRecord]: Страница команд.
    """
    items, total = await teams_service.search(
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
    teams_service: Annotated[TeamsService, Depends(get_teams_service)],
    _session: Annotated[UserSession, COMMON_TEAMS_SEC],
) -> CreatedTeam:
    """Создаёт команду вместе с профилем и первым участником.

    Args:
        body (Annotated[CreateTeamBody, Body]): Данные создаваемой команды.
        teams_service (Annotated[TeamsService, Depends]): Сервис команд.
        _session (Annotated[UserSession, Security]): Авторизованная сессия пользователя.

    Returns:
        CreatedTeam: Идентификатор и название созданной команды.
    """
    team = await teams_service.create(
        creator_id=_session.user_id,
        name=body.name,
        city=body.city,
        motto=body.motto,
        avatar_url=body.avatar_url,
    )

    return CreatedTeam.model_validate(team)


@router.get("/{team_id}", **GET_TEAM_DOCS)
async def get_team(
    team_id: Annotated[int, Path],
    teams_service: Annotated[TeamsService, Depends(get_teams_service)],
    _session: Annotated[UserSession, COMMON_TEAMS_SEC],
) -> Team:
    """Возвращает команду по её идентификатору.

    Args:
        team_id (Annotated[int, Path]): Идентификатор команды.
        teams_service (Annotated[TeamsService, Depends]): Сервис команд.
        _session (Annotated[UserSession, Security]): Авторизованная сессия пользователя.

    Returns:
        Team: Полные данные о команде.
    """
    team = await teams_service.get(team_id)

    return Team.model_validate(team)


@router.patch("/{team_id}", **UPDATE_TEAM_DOCS)
async def update_team(
    team_id: Annotated[int, Path],
    body: Annotated[UpdateTeamBody, Body()],
    teams_service: Annotated[TeamsService, Depends(get_teams_service)],
    _session: Annotated[UserSession, COMMON_TEAMS_SEC],
) -> Team:
    """Обновляет данные команды.

    Args:
        team_id ( Annotated[int, Path]): Идентификатор команды.
        body (Annotated[UpdateTeamBody, Body]): Обновляемые поля.
        teams_service (Annotated[TeamsService, Depends]): Сервис команд.
        _session (Annotated[UserSession, Security]): Авторизованная сессия пользователя.

    Returns:
        Team: Полные, обновлённые данные команды.
    """
    changes = body.model_dump(exclude_none=True)

    team = await teams_service.update(team_id=team_id, **changes)

    return Team.model_validate(team)


@router.get("/{team_id}/members", **GET_MEMBERS_DOCS)
async def get_team_members(
    team_id: Annotated[int, Path],
    service: Annotated[TeamsService, Depends(get_teams_service)],
    members_service: Annotated[MembersService, Depends(get_members_service)],
    _session: Annotated[UserSession, COMMON_TEAMS_SEC],
) -> list[Member]:
    """Возвращает список участников команды.

    Args:
        team_id (Annotated[int, Path]): Идентификатор команды.
        service (Annotated[TeamsService, Depends]): Сервис команд.
        members_service (Annotated[MembersService, Depends]): Сервис участников.
        _session (Annotated[UserSession, Security]): Авторизованная сессия пользователя.

    Returns:
        list[Member]: Участники команды.
    """
    team = await service.get(team_id)

    members = await members_service.get_members(union_id=team.id)

    return [Member.model_validate(m) for m in members]


@router.post("/{team_id}/members", **ADD_MEMBER_DOCS)
async def add_team_member(
    team_id: Annotated[int, Path],
    body: Annotated[AddMemberBody, Body()],
    teams_service: Annotated[TeamsService, Depends(get_teams_service)],
    members_service: Annotated[MembersService, Depends(get_members_service)],
    _session: Annotated[UserSession, COMMON_TEAMS_SEC],
) -> Member:
    """Добавляет участника в команду.

    Args:
        team_id (Annotated[int, Path]): Идентификатор команды.
        body (Annotated[AddMemberBody, Body]): Данные участника.
        teams_service (Annotated[TeamsService, Depends]): Сервис команд.
        members_service (Annotated[MembersService, Depends]): Сервис участников.
        _session (Annotated[UserSession, Security]): Авторизованная сессия пользователя.

    Returns:
        Member: Созданный участник.
    """
    team = await teams_service.get(team_id)

    member = await members_service.add_member(union_id=team.id, callsign=body.callsign)

    return Member.model_validate(member)


@router.patch("/{team_id}/members/{member_id}", **UPDATE_MEMBER_DOCS)
async def update_team_member(
    team_id: Annotated[int, Path],
    member_id: Annotated[int, Path],
    body: Annotated[UpdateMemberBody, Body()],
    teams_service: Annotated[TeamsService, Depends(get_teams_service)],
    members_service: Annotated[MembersService, Depends(get_members_service)],
    _session: Annotated[UserSession, COMMON_TEAMS_SEC],
) -> Member:
    """Обновляет данные участника команды.

    Args:
        team_id (Annotated[int, Path]): Идентификатор команды.
        member_id (Annotated[int, Path]): Идентификатор участника.
        body (Annotated[UpdateMemberBody, Body]): Обновляемые поля.
        teams_service (Annotated[TeamsService, Depends]): Сервис команд.
        members_service (Annotated[MembersService, Depends]): Сервис участников.
        _session (Annotated[UserSession, Security]): Авторизованная сессия пользователя.

    Returns:
        Member: Обновлённый участник.
    """
    team = await teams_service.get(team_id)

    changes = body.model_dump(exclude_none=True)
    member = await members_service.update_member(member_id=member_id, union_id=team.id, **changes)

    return Member.model_validate(member)


@router.delete("/{team_id}/members/{member_id}", **REMOVE_MEMBER_DOCS)
async def remove_team_member(
    team_id: Annotated[int, Path],
    member_id: Annotated[int, Path],
    teams_service: Annotated[TeamsService, Depends(get_teams_service)],
    members_service: Annotated[MembersService, Depends(get_members_service)],
    _session: Annotated[UserSession, COMMON_TEAMS_SEC],
) -> None:
    """Исключает участника из команды.

    Args:
        team_id (Annotated[int, Path]): Идентификатор команды.
        member_id (Annotated[int, Path]): Идентификатор участника.
        teams_service (Annotated[TeamsService, Depends]): Сервис команд.
        members_service (Annotated[MembersService, Depends]): Сервис участников.
        _session (Annotated[UserSession, Security]): Авторизованная сессия пользователя.
    """
    team = await teams_service.get(team_id)

    await members_service.remove_member(union_id=team.id, member_id=member_id)
