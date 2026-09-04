from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, Query

from backend.api.internal.committees.deps import get_committees_service, get_members_service
from backend.domain.services import CommitteesService, MembersService
from backend.general.schemas import PageOf
from backend.general.security.types import UserSession

from .docs import (
    ADD_MEMBER_DOCS,
    CREATE_COMMITTEE_DOCS,
    GET_COMMITTEE_DOCS,
    GET_MEMBERS_DOCS,
    REMOVE_MEMBER_DOCS,
    SEARCH_COMMITTEES_DOCS,
    UPDATE_COMMITTEE_DOCS,
    UPDATE_MEMBER_DOCS,
)
from .schemas import (
    AddMemberBody,
    Committee,
    CommitteeRecord,
    CreateCommitteeBody,
    CreatedCommittee,
    Member,
    SearchCommitteesBody,
    SearchCommitteesParams,
    UpdateCommitteeBody,
    UpdateMemberBody,
)
from .security import COMMON_COMMITTEE_SEC

router = APIRouter(prefix="/committees", tags=["Орг-комитеты"])


@router.post("/search", **SEARCH_COMMITTEES_DOCS)
async def search_committees(
    params: Annotated[SearchCommitteesParams, Query()],
    body: Annotated[SearchCommitteesBody, Body()],
    committee_service: Annotated[CommitteesService, Depends(get_committees_service)],
    _session: Annotated[UserSession, COMMON_COMMITTEE_SEC],
) -> PageOf[CommitteeRecord]:
    """Ищет орг-комитеты по фильтрам с сортировкой и пагинацией.

    Args:
        params (Annotated[SearchCommitteesParams, Query]): Параметры пагинации.
        body (Annotated[SearchCommitteesBody, Body]): Фильтры и сортировки.
        committee_service (Annotated[CommitteesService, Depends]): Сервис орг-комитетов.
        _session (Annotated[UserSession, Security]): Авторизованная сессия пользователя.

    Returns:
        PageOf[CommitteeRecord]: Страница орг-комитетов.
    """
    items, total = await committee_service.search(
        page=params.page,
        page_size=params.page_size,
        filters=[f.to_mapping() for f in body.filters],
        sorts=[s.to_mapping() for s in body.sorts],
    )

    return PageOf[CommitteeRecord](
        items=map(CommitteeRecord.model_validate, items),
        page=params.page,
        page_size=params.page_size,
        total=total,
    )


@router.post("/", **CREATE_COMMITTEE_DOCS)
async def create_committee(
    body: Annotated[CreateCommitteeBody, Body()],
    committee_service: Annotated[CommitteesService, Depends(get_committees_service)],
    _session: Annotated[UserSession, COMMON_COMMITTEE_SEC],
) -> CreatedCommittee:
    """Создаёт орг-комитет вместе с профилем и первым участником.

    Args:
        body (Annotated[CreateCommitteeBody, Body]): Данные создаваемого комитета.
        committee_service (Annotated[CommitteesService, Depends]): Сервис орг-комитетов.
        _session (Annotated[UserSession, Security]): Авторизованная сессия пользователя.

    Returns:
        CreatedCommittee: Идентификатор и название созданного орг-комитета.
    """
    committee = await committee_service.create(
        creator_id=_session.user_id,
        name=body.name,
        city=body.city,
        motto=body.motto,
        avatar_url=body.avatar_url,
    )

    return CreatedCommittee.model_validate(committee)


@router.get("/{committee_id}", **GET_COMMITTEE_DOCS)
async def get_committee(
    committee_id: Annotated[int, Path],
    committee_service: Annotated[CommitteesService, Depends(get_committees_service)],
    _session: Annotated[UserSession, COMMON_COMMITTEE_SEC],
) -> Committee:
    """Возвращает орг-комитет по его идентификатору.

    Args:
        committee_id (Annotated[int, Path]): Идентификатор орг-комитета.
        committee_service (Annotated[CommitteesService, Depends]): Сервис орг-комитетов.
        _session (Annotated[UserSession, Security]): Авторизованная сессия пользователя.

    Returns:
        Committee: Полные данные об орг-комитете.
    """
    committee = await committee_service.get(committee_id)

    return Committee.model_validate(committee)


@router.patch("/{committee_id}", **UPDATE_COMMITTEE_DOCS)
async def update_committee(
    committee_id: Annotated[int, Path],
    body: Annotated[UpdateCommitteeBody, Body()],
    committee_service: Annotated[CommitteesService, Depends(get_committees_service)],
    _session: Annotated[UserSession, COMMON_COMMITTEE_SEC],
) -> Committee:
    """Обновляет данные орг-комитета.

    Args:
        committee_id (Annotated[int, Path]): Идентификатор орг-комитета.
        body (Annotated[UpdateCommitteeBody, Body]): Обновляемые поля.
        committee_service (Annotated[CommitteesService, Depends]): Сервис орг-комитетов.
        _session (Annotated[UserSession, Security]): Авторизованная сессия пользователя.

    Returns:
        Committee: Полные, обновлённые данные орг-комитета.
    """
    changes = body.model_dump(exclude_none=True)

    committee = await committee_service.update(committee_id=committee_id, **changes)

    return Committee.model_validate(committee)


@router.get("/{committee_id}/members", **GET_MEMBERS_DOCS)
async def get_committee_members(
    committee_id: Annotated[int, Path],
    committee_service: Annotated[CommitteesService, Depends(get_committees_service)],
    members_service: Annotated[MembersService, Depends(get_members_service)],
    _session: Annotated[UserSession, COMMON_COMMITTEE_SEC],
) -> list[Member]:
    """Возвращает список участников орг-комитета.

    Args:
        committee_id (Annotated[int, Path]): Идентификатор орг-комитета.
        committee_service (Annotated[CommitteesService, Depends]): Сервис орг-комитетов.
        members_service (Annotated[MembersService, Depends]): Сервис участников.
        _session (Annotated[UserSession, Security]): Авторизованная сессия пользователя.

    Returns:
        list[Member]: Участники орг-комитета.
    """
    committee = await committee_service.get(committee_id)

    members = await members_service.get_members(union_id=committee.id)

    return [Member.model_validate(m) for m in members]


@router.post("/{committee_id}/members", **ADD_MEMBER_DOCS)
async def add_committee_member(
    committee_id: Annotated[int, Path],
    body: Annotated[AddMemberBody, Body()],
    committee_service: Annotated[CommitteesService, Depends(get_committees_service)],
    members_service: Annotated[MembersService, Depends(get_members_service)],
    _session: Annotated[UserSession, COMMON_COMMITTEE_SEC],
) -> Member:
    """Добавляет участника в орг-комитет.

    Args:
        committee_id (Annotated[int, Path]): Идентификатор орг-комитета.
        body (Annotated[AddMemberBody, Body]): Данные участника.
        committee_service (Annotated[CommitteesService, Depends]): Сервис орг-комитетов.
        members_service (Annotated[MembersService, Depends]): Сервис участников.
        _session (Annotated[UserSession, Security]): Авторизованная сессия пользователя.

    Returns:
        Member: Созданный участник.
    """
    committee = await committee_service.get(committee_id)

    member = await members_service.add_member(union_id=committee.id, callsign=body.callsign)

    return Member.model_validate(member)


@router.patch("/{committee_id}/members/{member_id}", **UPDATE_MEMBER_DOCS)
async def update_committee_member(
    committee_id: Annotated[int, Path],
    member_id: Annotated[int, Path],
    body: Annotated[UpdateMemberBody, Body()],
    committee_service: Annotated[CommitteesService, Depends(get_committees_service)],
    members_service: Annotated[MembersService, Depends(get_members_service)],
    _session: Annotated[UserSession, COMMON_COMMITTEE_SEC],
) -> Member:
    """Обновляет данные участника орг-комитета.

    Args:
        committee_id (Annotated[int, Path]): Идентификатор орг-комитета.
        member_id (Annotated[int, Path]): Идентификатор участника.
        body (Annotated[UpdateMemberBody, Body]): Обновляемые поля.
        committee_service (Annotated[CommitteesService, Depends]): Сервис орг-комитетов.
        members_service (Annotated[MembersService, Depends]): Сервис участников.
        _session (Annotated[UserSession, Security]): Авторизованная сессия пользователя.

    Returns:
        Member: Обновлённый участник.
    """
    committee = await committee_service.get(committee_id)

    changes = body.model_dump(exclude_none=True)
    member = await members_service.update_member(
        member_id=member_id, union_id=committee.id, **changes
    )

    return Member.model_validate(member)


@router.delete("/{committee_id}/members/{member_id}", **REMOVE_MEMBER_DOCS)
async def remove_committee_member(
    committee_id: Annotated[int, Path],
    member_id: Annotated[int, Path],
    committee_service: Annotated[CommitteesService, Depends(get_committees_service)],
    members_service: Annotated[MembersService, Depends(get_members_service)],
    _session: Annotated[UserSession, COMMON_COMMITTEE_SEC],
) -> None:
    """Исключает участника из орг-комитета.

    Args:
        committee_id (Annotated[int, Path]): Идентификатор орг-комитета.
        member_id (Annotated[int, Path]): Идентификатор участника.
        committee_service (Annotated[CommitteesService, Depends]): Сервис орг-комитетов.
        members_service (Annotated[MembersService, Depends]): Сервис участников.
        _session (Annotated[UserSession, Security]): Авторизованная сессия пользователя.
    """
    committee = await committee_service.get(committee_id)

    await members_service.remove_member(union_id=committee.id, member_id=member_id)
