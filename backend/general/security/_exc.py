from backend.general.exceptions import SecurityError


class IdentificationError(SecurityError):
    """Ошибка идентификации клиента."""


class AuthenticationError(SecurityError):
    """Ошибка аутентификации клиента."""


class AuthorizationError(SecurityError):
    """Ошибка авторизации клиента."""
