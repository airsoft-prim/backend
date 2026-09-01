from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from backend.domain.repositories import RepositoryError
from backend.providers.database.models import UnionMember, User, UserProfile

from ._base import DatabaseRepository


class UnionMembersRepository(DatabaseRepository):
    """Репозиторий участников объединений."""

    model = UnionMember

    async def get_by_union(self, union_id: int) -> list[UnionMember]:
        """Возвращает всех участников объединения.

        Для участников, привязанных к аккаунту, подгружается профиль
        пользователя (аватар): relationship-доступ вне контекста сессии
        невозможен без явной eager-подгрузки.

        Args:
            union_id (int): Идентификатор объединения.

        Returns:
            list[UnionMember]: Участники объединения.
        """
        statement = (
            select(self.model)
            .where(self.model.union_id == union_id)
            .options(
                joinedload(self.model.user)
                .joinedload(User.profile)
                .load_only(UserProfile.avatar_url)
            )
        )

        statement = statement.order_by(self.model.callsign)

        try:
            result = await self._session.scalars(statement)

        except SQLAlchemyError as error:
            message = f"{self.model.__name__} listing error."
            raise RepositoryError(message) from error

        return list(result.all())
