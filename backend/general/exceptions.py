class BackendError(Exception):
    """Ошибка работы Backend-сервиса."""


class DomainError(BackendError):
    """Ошибка выполнения бизнес-логики."""


class ProviderError(BackendError):
    """Ошибка инфраструктурного провайдера."""


class InternalAPIError(BackendError):
    """Ошибка внутреннего API."""


class SecurityError(BackendError):
    """Ошибка безопасности."""
