from backend.general.exceptions import DomainError


class ServiceError(DomainError):
    """Ошибка работы сервиса."""


class NotFoundError(ServiceError):
    """Целевой объект не найден."""


class ConflictError(ServiceError):
    """Конфликт с текущим состоянием данных."""
