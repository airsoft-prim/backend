from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from backend.domain.repositories import RepositoryError
from backend.providers.database.models import User

from ._base import DatabaseRepository


class UsersRepository(DatabaseRepository[User]):
    """Репозиторий доступа к данным пользователей."""

    model = User

    async def get_by_callsign(self, callsign: str) -> User | None:
        """Возвращает пользователя по позывному с подгруженным профилем.

        Args:
            callsign (str): Позывной пользователя.

        Returns:
            User | None: Пользователь или None, если не найден.
        """
        statement = select(self.model).where(self.model.callsign == callsign)

        try:
            result = await self._session.scalars(statement)
            return result.one_or_none()

        except SQLAlchemyError as error:
            message = f"{self.model.__name__} getting by callsign error."
            raise RepositoryError(message) from error
