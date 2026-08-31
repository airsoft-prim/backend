from backend.providers.database.models import User

from ._base import DatabaseRepository


class UsersRepository(DatabaseRepository):
    """Репозиторий доступа к данным пользователей."""

    model = User
