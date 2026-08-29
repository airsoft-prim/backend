class BackendError(Exception):
    """Ошибка рабюоты Backend'a сервиса онлайн-эквайринга."""


class DomainError(BackendError):
    """Ошибка выполнения бизнес-логики."""


class ProviderError(BackendError):
    """Ошибка инфраструктурного провайдера."""


class InternalAPIError(BackendError):
    """Ошибка внутреннего API."""
