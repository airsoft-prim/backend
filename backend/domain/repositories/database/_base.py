from collections.abc import Sequence
from typing import ClassVar, overload
from uuid import UUID

from sqlalchemy import delete as delete_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.domain.repositories import AbstractRepository, RepositoryError
from backend.providers.database import BaseModel

type EntityID = UUID | int


class DatabaseRepository[D: BaseModel](AbstractRepository):
    """Репозиторий для взаимодействия с сущностями в БД."""

    model: type[D]
    primary_key: ClassVar[str] = "id"

    def __init__(self, session: AsyncSession) -> None:
        """Инициализация класса.

        Args:
            session (AsyncSession): Асинхронная сессия БД.
        """
        self._session = session

    @overload
    async def get(self, id_: EntityID) -> D | None: ...

    @overload
    async def get(self, id_: Sequence[EntityID]) -> Sequence[D]: ...

    async def get(self, id_: EntityID | Sequence[EntityID]) -> D | Sequence[D] | None:
        """Метод получения сущности или списка сущностей из БД
        по их идентификатору.

        Для одиночного идентификатора возвращает None, если сущность
        не найдена.

        Args:
            id_ (EntityID | Sequence[EntityID]): Идентификатор или список
                идентификаторов сущностей в БД.

        Returns:
            D | Sequence[D] | None: ORM модель, список моделей или None.
        """
        pk = getattr(self.model, self.primary_key)
        stmt = select(self.model).where(
            pk.in_(id_) if isinstance(id_, Sequence) else pk == id_,
        )

        try:
            result = await self._session.execute(stmt)
            result = result.scalars().all()

        except SQLAlchemyError as error:
            msg = f"{self.model.__name__} getting error."
            raise RepositoryError(msg) from error

        if isinstance(id_, Sequence):
            return result

        return result[0] if result else None

    @overload
    async def save(self, entity: D) -> None: ...

    @overload
    async def save(self, entity: Sequence[D]) -> None: ...

    async def save(self, entity: D | Sequence[D]) -> None:
        """Метод сохранения сущности или списка сущностей в БД.

        Добавляет сущности в сессию и выполняет flush, чтобы получить
        сгенерированные значения (id, server defaults). Commit должен
        контролироваться извне, чтобы гарантировать атомарность операций.

        Args:
            entity (D | Sequence[D]): Сущность или список сущностей
                для сохранения.
        """
        if isinstance(entity, list):
            self._session.add_all(entity)

        else:
            self._session.add(entity)

        try:
            await self._session.flush()

        except SQLAlchemyError as error:
            msg = f"{self.model.__name__} saving error."
            raise RepositoryError(msg) from error

    @overload
    async def delete(self, id_: EntityID) -> D | None: ...

    @overload
    async def delete(self, id_: Sequence[EntityID]) -> Sequence[D]: ...

    async def delete(self, id_: EntityID | Sequence[EntityID]) -> D | Sequence[D] | None:
        """Метод удаления сущности или списка сущностей из БД
        по их идентификатору.

        Возвращает удалённые сущности: для одиночного идентификатора —
        сущность или None, если она не найдена; для списка —
        последовательность удалённых сущностей.

        Args:
            id_ (EntityID | Sequence[EntityID]): Идентификатор или список
                идентификаторов сущностей в БД.

        Returns:
            D | Sequence[D] | None: Удалённые сущности.
        """
        pk = getattr(self.model, self.primary_key)
        stmt = (
            delete_(self.model)
            .where(pk.in_(id_) if isinstance(id_, Sequence) else pk == id_)
            .returning(self.model)
        )

        try:
            result = await self._session.execute(stmt)
            result = result.scalars().all()

        except SQLAlchemyError as error:
            msg = f"{self.model.__name__} deleting error."
            raise RepositoryError(msg) from error

        if isinstance(id_, Sequence):
            return result

        return result[0] if result else None
