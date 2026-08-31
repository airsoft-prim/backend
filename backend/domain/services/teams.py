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
    UnionRecruitmentStatus,
    UnionStatus,
    UnionType,
)
from backend.general.types import FilterMapping, SortMapping
from backend.providers.database.models import Union, UnionMember, UnionProfile

from ._abc import ServiceWithSearch
from ._exc import NotFoundError, ServiceError


@dataclass(frozen=True, slots=True)
class TeamDTO:
    """Полное представление команды: карточка."""

    id: int
    name: str
    city: str | None
    camo_color: str | None
    gear_color: str | None
    type: UnionType
    status: UnionStatus
    recruitment_status: UnionRecruitmentStatus
    date_create: datetime
    members: int
    motto: str | None
    description: str | None
    banner_url: str | None
    avatar_url: str | None


@dataclass(frozen=True, slots=True)
class TeamRecordDTO:
    """Компактная запись о команде для выдачи в поиске."""

    id: int
    name: str
    members: int
    city: str | None
    date_create: datetime
    motto: str | None
    status: UnionStatus
    recruitment_status: UnionRecruitmentStatus
    avatar_url: str | None


@dataclass(frozen=True, slots=True)
class TeamCreatedDTO:
    """Результат создания команды: идентификатор и название."""

    id: int
    name: str


class TeamsService(ServiceWithSearch[TeamRecordDTO]):
    """Сервис команд: поиск, получение и создание объединений-команд."""

    async def search(
        self, page: int, page_size: int, filters: list[FilterMapping], sorts: list[SortMapping]
    ) -> tuple[list[TeamRecordDTO], int]:
        """Выполняет поиск команд и возвращает страницу записей.

        Args:
            page (int): Номер запрашиваемой страницы.
            page_size (int): Количество записей на странице.
            filters (list[FilterMapping]): Правила фильтрации записей.
            sorts (list[SortMapping]): Правила сортировки записей.

        Returns:
            tuple[list[TeamRecordDTO], int]: Записи страницы и общее число команд.
        """
        filters.append(self._get_union_type_filter())

        async with self.unit_of_work() as uow:
            unions_repo = uow.database_repository(UnionsRepository)

            items, total = await unions_repo.get_page(page, page_size, filters, sorts)

        return [self._map_record(i) for i in items], total

    async def get(self, team_id: int) -> TeamDTO:
        """Возвращает команду по идентификатору.

        Args:
            team_id (int): Идентификатор команды.

        Raises:
            NotFoundError: Если команда с данным ID не найдена.

        Returns:
            TeamDTO: Полное представление команды.
        """
        async with self.unit_of_work() as uow:
            unions_repo = uow.database_repository(UnionsRepository)

            union = await unions_repo.get_with_profile(team_id)

            if union is None:
                message = f"Team <{team_id}> not found."
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
    ) -> TeamCreatedDTO:
        """Создаёт команду вместе с профилем и первым членом (командиром).

        Позывной первого члена берётся из профиля пользователя, указанного
        в `creator_id`.

        Args:
            creator_id (int): ID авторизованного пользователя — первого члена команды.
            name (str): Название команды.
            city (str | None): Город размещения. Defaults to None.
            motto (str | None): Девиз команды. Defaults to None.
            avatar_url (str | None): Ссылка на аватар. Defaults to None.

        Raises:
            NotFoundError: Если пользователь с данным ID не найден.

        Returns:
            TeamCreatedDTO: Идентификатор и название созданной команды.
        """
        async with self.unit_of_work() as uow:
            unions_repo = uow.database_repository(UnionsRepository)
            members_repo = uow.database_repository(UnionMembersRepository)
            users_repo = uow.database_repository(UsersRepository)

            if (user := await users_repo.get(creator_id)) is None:
                message = f"User <{creator_id}> not found."
                raise NotFoundError(message) from None

            profile = UnionProfile(motto=motto, avatar_url=avatar_url)
            union = Union(name=name, city=city, type=UnionType.TEAM, profile=profile)

            await unions_repo.save(union)

            default_rank = UnionMemberRank.COMMANDER
            member = UnionMember(union=union, user=user, callsign=user.callsign, rank=default_rank)

            await members_repo.save(member)

        return TeamCreatedDTO(id=union.id, name=union.name)

    async def update(  # noqa: PLR0913 — 9 опциональных полей PATCH
        self,
        team_id: int,
        *,
        name: str | None = None,
        city: str | None = None,
        camo_color: str | None = None,
        gear_color: str | None = None,
        motto: str | None = None,
        description: str | None = None,
        avatar_url: str | None = None,
        banner_url: str | None = None,
        recruitment_status: UnionRecruitmentStatus | None = None,
    ) -> TeamDTO:
        """Обновляет данные команды.

        Обновляются только переданные (не None) поля - семантика PATCH.

        Args:
            team_id (int): Идентификатор команды.
            name (str | None): Новое название. Defaults to None.
            city (str | None): Новый город размещения. Defaults to None.
            camo_color (str | None): Новый цвет камуфляжа. Defaults to None.
            gear_color (str | None): Новый цвет снаряжения. Defaults to None.
            motto (str | None): Новый девиз. Defaults to None.
            description (str | None): Новое описание. Defaults to None.
            avatar_url (str | None): Новая ссылка на аватар. Defaults to None.
            banner_url (str | None): Новая ссылка на баннер. Defaults to None.
            recruitment_status (UnionRecruitmentStatus | None): Новое состояние
                набора. Defaults to None.

        Raises:
            NotFoundError: Если команда с данным ID не найдена.

        Returns:
            TeamDTO: Обновлённая команда.
        """
        async with self.unit_of_work() as uow:
            unions_repo = uow.database_repository(UnionsRepository)

            if (union := await unions_repo.get_with_profile(team_id)) is None:
                message = f"Team <{team_id}> not found."
                raise NotFoundError(message) from None

            self._apply_updates(
                union,
                name=name,
                city=city,
                camo_color=camo_color,
                gear_color=gear_color,
                recruitment_status=recruitment_status,
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
    def _map_item(union: Union) -> TeamDTO:
        """Маппит объединение в полное представление команды.

        Args:
            union (Union): ORM-объединение с подгруженным профилем.

        Returns:
            TeamDTO: Полное представление команды.
        """
        return TeamDTO(
            id=union.id,
            name=union.name,
            city=union.city,
            camo_color=union.camo_color,
            gear_color=union.gear_color,
            type=union.type,
            status=union.status,
            recruitment_status=union.recruitment_status,
            date_create=union.created_at,
            members=union.members_count,
            motto=union.profile.motto,
            description=union.profile.description,
            banner_url=union.profile.banner_url,
            avatar_url=union.profile.avatar_url,
        )

    @staticmethod
    def _map_record(union: Union) -> TeamRecordDTO:
        """Маппит объединение в компактную запись поиска.

        Args:
            union (Union): ORM-объединение со страницы поиска. Профиль
                подгружен полями `avatar_url` и `motto`, `members_count` —
                column_property модели.

        Returns:
            TeamRecordDTO: Запись о команде для ответа поиска.
        """
        return TeamRecordDTO(
            id=union.id,
            name=union.name,
            members=union.members_count,
            city=union.city,
            date_create=union.created_at,
            motto=union.profile.motto,
            status=union.status,
            recruitment_status=union.recruitment_status,
            avatar_url=union.profile.avatar_url,
        )

    @staticmethod
    def _get_union_type_filter() -> FilterMapping:
        """Фильтр по типу объединения: в поиск попадают только команды.

        Returns:
            FilterMapping: Правило фильтрации `type = team`.
        """
        return FilterMapping(
            field="type",
            value=UnionType.TEAM,
            operator=FilterOperator.EQUAL,
        )
