from enum import StrEnum


class UserRole(StrEnum):
    """Роль пользователя на портале."""

    PLAYER = "player"
    ADMIN = "admin"
