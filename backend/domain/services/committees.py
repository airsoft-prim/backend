from dataclasses import dataclass
from datetime import datetime
from typing import Any

from backend.domain.repositories.database import (
    UnionMembersRepository,
    UnionsRepository,
    UsersRepository,
)
from backend.general.enums import (
    FilterOperator,
    UnionMemberRank,
    UnionStatus,
    UnionType,
)
from backend.general.types import FilterMapping, SortMapping
from backend.providers.database.models import Union, UnionMember, UnionProfile

from ._abc import ServiceWithSearch
from ._exc import NotFoundError, ServiceError


@dataclass(frozen=True, slots=True)
class CommitteeDTO:
    """Полное представление орг-комитета: карточка."""

    id: int
    name: str
    city: str | None
    camo_color: str | None
    gear_color: str | None
    type: UnionType
    status: UnionStatus
    date_create: datetime
    members: int
    motto: str | None
    description: str | None
    banner_url: str | None
    avatar_url: str | None


@dataclass(frozen=True, slots=True)
class CommitteeRecordDTO:
    """Компактная запись об орг-комитете для выдачи в поиске."""

    id: int
    name: str
    members: int
    city: str | None
    date_create: datetime
    motto: str | None
    status: UnionStatus
    avatar_url: str | None


@dataclass(frozen=True, slots=True)
class CommitteeCreatedDTO:
    """Результат создания орг-комитета: идентификатор и название."""

    id: int
    name: str


class CommitteesService(ServiceWithSearch[CommitteeRecordDTO]):
    """Сервис орг-комитетов: поиск, получение и создание объединений-комитетов.

    Орг-комитет отличается от команды: у него нет камуфляжа (`camo_color`
    всегда `None`), а цвет снаряжения фиксирован — светоотражающий
    (`REFLECTIVE_GEAR_COLOR`). Набор (`recruitment_status`) к комитетам
    не применяется, поэтому в API он не выставляется.
    """

    async def search(
        self, page: int, page_size: int, filters: list[FilterMapping], sorts: list[SortMapping]
    ) -> tuple[list[CommitteeRecordDTO], int]:
        """Выполняет поиск орг-комитетов и возвращает страницу записей.

        Args:
            page (int): Номер запрашиваемой страницы.
            page_size (int): Количество записей на странице.
            filters (list[FilterMapping]): Правила фильтрации записей.
            sorts (list[SortMapping]): Правила сортировки записей.

        Returns:
            tuple[list[CommitteeRecordDTO], int]: Записи страницы и общее число комитетов.
        """
        filters.append(self._get_union_type_filter())

        async with self.unit_of_work() as uow:
            unions_repo = uow.database_repository(UnionsRepository)

            items, total = await unions_repo.get_page(page, page_size, filters, sorts)

        return [self._map_record(i) for i in items], total

    async def get(self, committee_id: int) -> CommitteeDTO:
        """Возвращает орг-комитет по идентификатору.

        Args:
            committee_id (int): Идентификатор орг-комитета.

        Raises:
            NotFoundError: Если орг-комитет с данным ID не найден
                (в том числе если ID принадлежит объединению другого типа).

        Returns:
            CommitteeDTO: Полное представление орг-комитета.
        """
        async with self.unit_of_work() as uow:
            unions_repo = uow.database_repository(UnionsRepository)

            union = await unions_repo.get_with_profile(committee_id)

            if union is None or union.type != UnionType.COMMITTEE:
                message = f"Committee <{committee_id}> not found."
                raise NotFoundError(message) from None

        return self._map_item(union)

    async def create(
        self,
        creator_id: int,
        name: str,
        *,
        city: str | None = None,
        motto: str | None = None,
        avatar_url: str | None = None,
    ) -> CommitteeCreatedDTO:
        """Создаёт орг-комитет вместе с профилем и первым членом (главой).

        Позывной первого члена берётся из профиля пользователя, указанного
        в `creator_id`. Камуфляж комитету не задаётся (`camo_color = None`),
        цвет снаряжения фиксируется как «Светоотражающий».

        Args:
            creator_id (int): ID авторизованного пользователя — первого члена.
            name (str): Название орг-комитета.
            city (str | None): Город размещения. Defaults to None.
            motto (str | None): Девиз орг-комитета. Defaults to None.
            avatar_url (str | None): Ссылка на аватар. Defaults to None.

        Raises:
            NotFoundError: Если пользователь с данным ID не найден.
            ConflictError: Если орг-комитет с таким названием уже существует.

        Returns:
            CommitteeCreatedDTO: Идентификатор и название созданного комитета.
        """
        async with self.unit_of_work() as uow:
            unions_repo = uow.database_repository(UnionsRepository)
            members_repo = uow.database_repository(UnionMembersRepository)
            users_repo = uow.database_repository(UsersRepository)

            if (user := await users_repo.get(creator_id)) is None:
                message = f"User <{creator_id}> not found."
                raise NotFoundError(message) from None

            profile = UnionProfile(motto=motto, avatar_url=avatar_url)
            union = Union(name=name, city=city, type=UnionType.COMMITTEE, profile=profile)

            await unions_repo.save(union)

            default_rank = UnionMemberRank.COMMANDER
            member = UnionMember(union=union, user=user, callsign=user.callsign, rank=default_rank)

            await members_repo.save(member)

        return CommitteeCreatedDTO(id=union.id, name=union.name)

    async def update(  # noqa: PLR0913
        self,
        committee_id: int,
        *,
        name: str | None = None,
        city: str | None = None,
        motto: str | None = None,
        description: str | None = None,
        avatar_url: str | None = None,
        banner_url: str | None = None,
    ) -> CommitteeDTO:
        """Обновляет данные орг-комитета.

        Обновляются только переданные (не None) поля - семантика PATCH.
        Камуфляж, цвет снаряжения и состояние набора у комитета фиксированы
        и обновлению не подлежат.

        Args:
            committee_id (int): Идентификатор орг-комитета.
            name (str | None): Новое название. Defaults to None.
            city (str | None): Новый город размещения. Defaults to None.
            motto (str | None): Новый девиз. Defaults to None.
            description (str | None): Новое описание. Defaults to None.
            avatar_url (str | None): Новая ссылка на аватар. Defaults to None.
            banner_url (str | None): Новая ссылка на баннер. Defaults to None.

        Raises:
            NotFoundError: Если орг-комитет с данным ID не найден
                (в том числе если ID принадлежит объединению другого типа).
            ConflictError: Если новое название занято другим объединением.

        Returns:
            CommitteeDTO: Обновлённый орг-комитет.
        """
        async with self.unit_of_work() as uow:
            unions_repo = uow.database_repository(UnionsRepository)

            union = await unions_repo.get_with_profile(committee_id)

            if union is None or union.type != UnionType.COMMITTEE:
                message = f"Committee <{committee_id}> not found."
                raise NotFoundError(message) from None

            self._apply_updates(
                union,
                name=name,
                city=city,
            )
            self._apply_updates(
                union.profile,
                motto=motto,
                description=description,
                avatar_url=avatar_url,
                banner_url=banner_url,
            )

            await unions_repo.save(union)

        return self._map_item(union)

    @staticmethod
    def _apply_updates(entity: Any, **changes: Any) -> None:
        """Применяет к сущности только переданные (не None) поля.

        Значение `None` означает "не менять". Имя поля проверяется
        по сущности, чтобы опечатка не стала тихим no-op.

        Args:
            entity (Any): ORM-модель.
            **changes: Имя поля и его новое значение.

        Raises:
            ServiceError: Если поле не существует у сущности.
        """
        for field, value in changes.items():
            if value is None:
                continue

            if not hasattr(entity, field):
                message = f"Unknown field {field!r} for {type(entity).__name__}."
                raise ServiceError(message) from None

            setattr(entity, field, value)

    @staticmethod
    def _map_item(union: Union) -> CommitteeDTO:
        """Маппит объединение в полное представление орг-комитета.

        Args:
            union (Union): ORM-объединение с подгруженным профилем.

        Returns:
            CommitteeDTO: Полное представление орг-комитета.
        """
        return CommitteeDTO(
            id=union.id,
            name=union.name,
            city=union.city,
            camo_color=union.camo_color,
            gear_color=union.gear_color,
            type=union.type,
            status=union.status,
            date_create=union.created_at,
            members=union.members_count,
            motto=union.profile.motto,
            description=union.profile.description,
            banner_url=union.profile.banner_url,
            avatar_url=union.profile.avatar_url,
        )

    @staticmethod
    def _map_record(union: Union) -> CommitteeRecordDTO:
        """Маппит объединение в компактную запись поиска.

        Args:
            union (Union): ORM-объединение со страницы поиска. Профиль
                подгружен полями `avatar_url` и `motto`, `members_count` —
                column_property модели.

        Returns:
            CommitteeRecordDTO: Запись об орг-комитете для ответа поиска.
        """
        return CommitteeRecordDTO(
            id=union.id,
            name=union.name,
            members=union.members_count,
            city=union.city,
            date_create=union.created_at,
            motto=union.profile.motto,
            status=union.status,
            avatar_url=union.profile.avatar_url,
        )

    @staticmethod
    def _get_union_type_filter() -> FilterMapping:
        """Фильтр по типу объединения: в поиск попадают только комитеты.

        Returns:
            FilterMapping: Правило фильтрации `type = committee`.
        """
        return FilterMapping(
            field="type",
            value=UnionType.COMMITTEE,
            operator=FilterOperator.EQUAL,
        )
