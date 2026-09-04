from abc import ABC, abstractmethod

from fastapi.security import SecurityScopes

from backend.general.enums import UserRole

from .jwt import Algorithm, TokenManager
from .types import AuthSession


class ProtectionSchema[S: AuthSession](ABC):
    """Абстрактный класс схемы защиты API endpiont'ов.

    Конкретные реализации данного класса должны получать ключ доступа
    из выбранной схемы аутентификации (OAuth2, APIKeyHeader ...) и
    проверять доступ клиента по данному токену. Если авторизация была
    произведена успешно - вернуть подходящий подтип авторизованной сессии.
    """

    def __init__(self, token_manager: TokenManager | None = None) -> None:
        """Инициализация класса.

        Args:
            token_manager (TokenManager | None, optional): Менеджер токенов для
                работы с JWT. Defaults to None.
        """
        self.token_manager = token_manager or TokenManager(algorithm=Algorithm.AUTO)

    @abstractmethod
    async def __call__(self, token: str, required: SecurityScopes) -> S:
        """Абстрактный метод авторизации склиента.

        Конкретные реализации данного метода должны получать всю необходимую
        информацию из токена/ключа доступа, полученного отклиента при формировании запроса,
        и сравнивать её с данными, необходимыми для получения доступа. В конечном
        итоге метод должен вернуть подтип авторизованноей сессии с информацией
        об авторизованном клиенте.

        Args:
            token (str): Токен/Ключ доступа, отправленный клиентом.
            required (SecurityScopes): Требуемые Scopes для получения доступа.

        Raises:
            NotImplementedError: Метод не реалзиова в дочернем классе.

        Returns:
            S: Информация об авторизованном клиенте.
        """
        message = "Method not implemented in child class."
        raise NotImplementedError(message) from None

    def _check_roles(self, actual: list[UserRole], required: list[UserRole]) -> bool:
        """Выполняет проверку наличия необходимых разрешений.

        Данный метод сравнивает реальный список прав клиента с требуемым
        списком прав.

        Args:
            actual (list[UserRole]): Права, полученные из ключа доступа.
            required (list[UserRole]): Необходимый список прав.

        Raises:
            bool: Флаг наличия нужной роли.
        """
        return not required or bool(set(actual).intersection(required))
