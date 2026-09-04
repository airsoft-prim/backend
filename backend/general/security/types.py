from pydantic import BaseModel

from backend.general.enums import UserRole


class AuthSession(BaseModel):
    """Базовая модель дляавторизованной сессии."""


class UserSession(AuthSession):
    """Модель данных сессии пользователя."""

    user_id: int
    user_roles: list[UserRole]
