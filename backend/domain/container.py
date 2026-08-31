from typing import Any, cast

from backend.domain.repositories.database import DatabaseRepository

from ._exc import ContainerError


class Container:
    """Контейнер зависимостей, не привязанный к конкретному типу.

    Хранит произвольные зависимости (репозитории, сервисы, мапперы, фабрики сессий
    и клиентов, конфигурацию и т.п.) и отдаёт их по типу. Классы (например, фабрики
    репозиториев) регистрируются под собственным именем и возвращаются
    как есть; экземпляры — под своим типом. Для дженерик-типов (например,
    фабрик сессий) укажите `as_type` — стабильный тип-ключ.
    """

    def __init__(self) -> None:
        """Инициализация контейнера."""
        self._dependencies: dict[type[object], object] = {}

    def register(self, dependency: object, *, as_type: type[object] | None = None) -> None:
        """Регистрирует зависимость.

        Ключом по умолчанию служит сам класс, если регистрируется класс
        (например, фабрика репозитория), иначе — тип экземпляра.

        Args:
            dependency (object): Зависимость: экземпляр или класс-фабрика.
            as_type (type[object] | None): Явный тип-ключ для поиска;
                по умолчанию выводится из регистрируемого объекта.
        """
        key = as_type or (type(dependency) if not isinstance(dependency, type) else dependency)
        self._dependencies[key] = dependency

    def get[D: Any](self, dependency: type[D]) -> D:
        """Возвращает зависимость по её типу.

        Args:
            dependency (type[D]): Тип зависимости.

        Raises:
            ContainerError: Если зависимость не зарегистрирована.

        Returns:
            D: Экземпляр зависимости.
        """
        try:
            return cast(D, self._dependencies[dependency])

        except KeyError as error:
            msg = f"Missing {dependency.__name__} dependency."
            raise ContainerError(msg) from error


def create_container(*repositories: type[DatabaseRepository]) -> Container:
    """Создаёт контейнер зависимостей.

    Регистрирует фабрику сессий и переданные классы репозиториев:
    сессия будет создана фабрикой на каждый запрос, а репозитории
    инстанцируются UnitOfWork на этой сессии.

    Args:
        *repositories (type[DatabaseRepository]): Классы репозиториев.

    Returns:
        Container: Контейнер с зарегистрированными зависимостями.
    """
    container = Container()

    for repository in repositories:
        container.register(repository)

    return container
