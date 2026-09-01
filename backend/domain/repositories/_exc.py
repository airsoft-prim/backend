from backend.general.exceptions import DomainError


class RepositoryError(DomainError):
    """Ошибка работы репозитория."""


class ConflictError(RepositoryError):
    """Нарушение ограничения целостности БД.

    Возникает при попытке сохранить запись с неуникальным значением,
    удалить запись, на которую ссылаются другие записи, или изменить
    данные вопреки ограничению.
    """
