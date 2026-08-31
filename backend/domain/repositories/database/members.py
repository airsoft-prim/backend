from backend.providers.database.models import UnionMember

from ._base import DatabaseRepository


class UnionMembersRepository(DatabaseRepository):
    """Репозиторий участников объединений."""

    model = UnionMember
