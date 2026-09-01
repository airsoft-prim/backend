from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, Query

from backend.api.internal.committees.deps import get_committees_service
from backend.domain.services import CommitteesService
from backend.general.schemas import PageOf

from .docs import (
    ADD_MEMBER_DOCS,
    CREATE_COMMITTEE_DOCS,
    GET_COMMITTEE_DOCS,
    GET_MEMBER_DOCS,
    GET_MEMBERS_DOCS,
    REMOVE_MEMBER_DOCS,
    SEARCH_COMMITTEES_DOCS,
    UPDATE_COMMITTEE_DOCS,
    UPDATE_MEMBER_DOCS,
)
from .schemas import (
    Committee,
    CommitteeRecord,
    CreateCommitteeBody,
    CreatedCommittee,
    SearchCommitteesBody,
    SearchCommitteesParams,
    UpdateCommitteeBody,
)

router = APIRouter(prefix="/committees", tags=["Орг-комитеты"])


@router.post("/search", **SEARCH_COMMITTEES_DOCS)
async def search_committees(
    params: Annotated[SearchCommitteesParams, Query()],
    body: Annotated[SearchCommitteesBody, Body()],
    service: Annotated[CommitteesService, Depends(get_committees_service)],
) -> PageOf[CommitteeRecord]:
    """Ищет орг-комитеты по фильтрам с сортировкой и пагинацией.

    Args:
        params (Annotated[SearchCommitteesParams, Query]): Параметры пагинации.
        body (Annotated[SearchCommitteesBody, Body]): Фильтры и сортировки.
        service (Annotated[CommitteesService, Depends]): Сервис орг-комитетов.

    Returns:
        PageOf[CommitteeRecord]: Страница орг-комитетов.
    """
    items, total = await service.search(
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
    service: Annotated[CommitteesService, Depends(get_committees_service)],
) -> CreatedCommittee:
    """Создаёт орг-комитет вместе с профилем и первым участником.

    Args:
        body (Annotated[CreateCommitteeBody, Body]): Данные создаваемого комитета.
        service (Annotated[CommitteesService, Depends]): Сервис орг-комитетов.

    Returns:
        CreatedCommittee: Идентификатор и название созданного орг-комитета.
    """
    committee = await service.create(
        creator_id=0,  # TODO: Заменить на авторизованного пользователя
        name=body.name,
        city=body.city,
        motto=body.motto,
        avatar_url=body.avatar_url,
    )

    return CreatedCommittee.model_validate(committee)


@router.get("/{committee_id}", **GET_COMMITTEE_DOCS)
async def get_committee(
    committee_id: Annotated[int, Path],
    service: Annotated[CommitteesService, Depends(get_committees_service)],
) -> Committee:
    """Возвращает орг-комитет по его идентификатору.

    Args:
        committee_id (Annotated[int, Path]): Идентификатор орг-комитета.
        service (Annotated[CommitteesService, Depends]): Сервис орг-комитетов.

    Returns:
        Committee: Полные данные об орг-комитете.
    """
    committee = await service.get(committee_id)

    return Committee.model_validate(committee)


@router.patch("/{committee_id}", **UPDATE_COMMITTEE_DOCS)
async def update_committee(
    committee_id: Annotated[int, Path],
    body: Annotated[UpdateCommitteeBody, Body()],
    service: Annotated[CommitteesService, Depends(get_committees_service)],
) -> Committee:
    """Обновляет данные орг-комитета.

    Args:
        committee_id (Annotated[int, Path]): Идентификатор орг-комитета.
        body (Annotated[UpdateCommitteeBody, Body]): Обновляемые поля.
        service (Annotated[CommitteesService, Depends]): Сервис орг-комитетов.

    Returns:
        Committee: Полные, обновлённые данные орг-комитета.
    """
    changes = body.model_dump(exclude_none=True)

    committee = await service.update(committee_id=committee_id, **changes)

    return Committee.model_validate(committee)


@router.get("/{committee_id}/members", **GET_MEMBERS_DOCS)
async def get_committee_members() -> None:
    pass


@router.post("/{committee_id}/members", **ADD_MEMBER_DOCS)
async def add_committee_member() -> None:
    pass


@router.get("/{committee_id}/members/{member_id}", **GET_MEMBER_DOCS)
async def get_committee_member() -> None:
    pass


@router.patch("/{committee_id}/members/{member_id}", **UPDATE_MEMBER_DOCS)
async def update_committee_member() -> None:
    pass


@router.delete("/{committee_id}/members/{member_id}", **REMOVE_MEMBER_DOCS)
async def remove_committee_member() -> None:
    pass
