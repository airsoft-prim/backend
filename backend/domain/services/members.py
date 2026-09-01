from dataclasses import dataclass
from typing import Any

from backend.domain.repositories.database import UnionMembersRepository, UsersRepository
from backend.general.enums import UnionMemberRank
from backend.providers.database.models import UnionMember

from ._base import Service
from ._exc import NotFoundError, ServiceError


@dataclass(frozen=True, slots=True)
class UnionMemberDTO:
    """Запись участника объединения в списке членов.

    Участнику без привязанного аккаунта соответствуют только позывной
    и тег; `user_id` и `avatar_url` заполняются, если участник привязан
    к аккаунту игрока.
    """

    id: int
    callsign: str
    user_id: int | None
    tag: str | None
    avatar_url: str | None


class MembersService(Service):
    """Сервис участников объединений: список, добавление и управление.

    Сервису безразличен тип объединения (команда или орг-комитет): он работает
    с записями `UnionMember` по идентификатору объединения. Существование,
    тип и доступность объединения проверяет вызывающий слой — TeamsService
    или CommitteesService в маршруте.
    """

    async def get_members(self, union_id: int) -> list[UnionMemberDTO]:
        """Возвращает список участников объединения.

        Фильтрация не поддерживается: отдаются все участники объединения.
        Участник без привязанного аккаунта представлен только позывным и тегом;
        при привязке к аккаунту дополнительно возвращаются `user_id` (для ссылки
        на профиль игрока) и ссылка на аватар пользователя.

        Args:
            union_id (int): Идентификатор объединения.

        Returns:
            list[UnionMemberDTO]: Участники объединения.
        """
        async with self.unit_of_work() as uow:
            members_repo = uow.database_repository(UnionMembersRepository)

            items = await members_repo.get_by_union(union_id)

        return [self._map_item(i) for i in items]

    async def add_member(self, union_id: int, callsign: str) -> UnionMemberDTO:
        """Добавляет участника в объединение как виртуального бойца.

        Позывной не обязан быть уникальным в объединении. Если в системе уже
        зарегистрирован игрок с таким позывным — участник автоматически
        привязывается к его аккаунту; иначе остаётся виртуальным бойцом.
        Ранг остаётся по умолчанию (участник), тег не задаётся.

        Args:
            union_id (int): Идентификатор объединения.
            callsign (str): Позывной участника.

        Raises:
            ConflictError: Если игрок с таким позывным уже состоит в этом
                объединении — ограничение `(union_id, user_id)` репозитория.

        Returns:
            UnionMemberDTO: Созданный участник.
        """
        async with self.unit_of_work() as uow:
            members_repo = uow.database_repository(UnionMembersRepository)
            users_repo = uow.database_repository(UsersRepository)

            member = UnionMember(union_id=union_id, callsign=callsign)

            if user := await users_repo.get_by_callsign(callsign):
                member.user = user

            await members_repo.save(member)

            # Подгрузка пользователя и профиля (аватар): lazy-загрузка
            # недоступна после закрытия UoW.
            user = await member.awaitable_attrs.user
            if user is not None:
                await user.awaitable_attrs.profile

        return self._map_item(member)

    async def remove_member(self, union_id: int, member_id: int) -> None:
        """Исключает участника из объединения.

        Заявки участника на игры удаляются вместе с ним: на уровне БД
        это каскад `game_registrations.member_id ON DELETE CASCADE`.

        Args:
            union_id (int): Идентификатор объединения.
            member_id (int): Идентификатор участника.

        Raises:
            NotFoundError: Если участник с данным ID не найден в этом объединении.
        """
        async with self.unit_of_work() as uow:
            members_repo = uow.database_repository(UnionMembersRepository)

            member = await members_repo.get(member_id)

            if member is None or member.union_id != union_id:
                message = f"Member <{member_id}> not found."
                raise NotFoundError(message) from None

            await members_repo.delete(member_id)

    async def update_member(
        self,
        member_id: int,
        *,
        union_id: int,
        tag: str | None = None,
        callsign: str | None = None,
        rank: UnionMemberRank | None = None,
    ) -> UnionMemberDTO:
        """Частично обновляет данные участника.

        Обновляются только переданные (не None) поля.

        Args:
            member_id (int): Идентификатор участника.
            union_id (int): Идентификатор объединения, в котором состоит участник.
            tag (str | None): Новый тег. Defaults to None.
            callsign (str | None): Новый позывной. Defaults to None.
            rank (UnionMemberRank | None): Новый ранг. Defaults to None.

        Raises:
            NotFoundError: Если участник с данным ID не найден или
                не состоит в указанном объединении.

        Returns:
            UnionMemberDTO: Обновлённый участник.
        """
        async with self.unit_of_work() as uow:
            members_repo = uow.database_repository(UnionMembersRepository)

            member = await members_repo.get(member_id)

            if member is None or member.union_id != union_id:
                message = f"Member <{member_id}> not found."
                raise NotFoundError(message) from None

            self._apply_updates(member, callsign=callsign, rank=rank, tag=tag)

            await members_repo.save(member)

            # Подгрузка пользователя и профиля (аватар): lazy-загрузка
            # недоступна после закрытия UoW.
            user = await member.awaitable_attrs.user
            if user is not None:
                await user.awaitable_attrs.profile

        return self._map_item(member)

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
    def _map_item(member: UnionMember) -> UnionMemberDTO:
        """Маппит участника объединения в запись списка.

        Args:
            member (UnionMember): ORM-участник объединения с подгруженным
                пользователем и его профилем.

        Returns:
            UnionMemberDTO: Запись участника.
        """
        user = member.user
        avatar_url = user.profile.avatar_url if user and user.profile else None

        return UnionMemberDTO(
            id=member.id,
            callsign=member.callsign,
            tag=member.tag,
            user_id=member.user_id,
            avatar_url=avatar_url,
        )
