from typing import Annotated, Final

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, SecurityScopes

from .general.enums import UserRole
from .general.security import AuthorizationError
from .general.security.schema import ProtectionSchema
from .general.security.types import UserSession

SCHEME_DESCRIPTION: Final[str] = """
Данная схема доступа требует отправки Bearer токена в заголоке
Authorization при каждом запросе к API.
"""


token = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
    scheme_name="Клиентская схема аутентификации.",
    description=SCHEME_DESCRIPTION,
    auto_error=False,
)

JWTToken = Annotated[str, Depends(token)]


# TODO: Сейчас это Mock-класс
class RequireBearerToken(ProtectionSchema[UserSession]):
    """Схема защиты endpoint'ов, требующая Bearer токена доступа."""

    async def __call__(self, token: JWTToken, required: SecurityScopes) -> UserSession:
        """Метод авторизации пользователя по Bearer ключу доступа.

        Args:
            token (JWTToken): Ключ доступа, отправленный пользователем.
            required (SecurityScopes): Требуемые Scopes для получения доступа.

        Returns:
            UserSession: Информация об авторизованном пользователе.
        """
        payload = ...  # TODO: Декодировать токен
        subject_roles = []  # TODO: Получить роли пользователя из токена
        required_roles = [UserRole(scope) for scope in required.scopes]

        if not self._check_roles(subject_roles, required_roles):
            message = "Lack permissions for the request."
            raise AuthorizationError(message) from None

        return UserSession(user_id=1, user_roles=subject_roles)
