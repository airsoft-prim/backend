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
    async def get(self, id_: EntityID) -> D: ...

    @overload
    async def get(self, id_: Sequence[EntityID]) -> Sequence[D]: ...

    async def get(self, id_: EntityID | Sequence[EntityID]) -> D | Sequence[D]:
        """Метод получения сущности или списка сущностей из БД
        по их идентификатору.

        Args:
            id_ (EntityID | Sequence[EntityID]): Идентификатор или список
                идентификаторов сущностей в БД.

        Returns:
            D | Sequence[D]: ORM модель список моделей сущности.
        """
        pk = getattr(self.model, self.primary_key)
        stmt = select(self.model).where(
            pk.in_(id_) if isinstance(id_, Sequence) else pk == id_,
        )

        try:
            result = await self._session.execute(stmt)
            result = result.scalars().all()

        except SQLAlchemyError as error:
            msg = f"{self.model.__class__.__name__} getting error."
            raise RepositoryError(msg) from error

        return result[0] if len(result) == 1 else result

    @overload
    async def save(self, entity: D) -> None: ...

    @overload
    async def save(self, entity: Sequence[D]) -> None: ...

    async def save(self, entity: D | Sequence[D]) -> None:
        """Метод сохранения сущности или списка сущностей в БД.

        Args:
            entity (D | Sequence[D]): Сущность или список сущностей
                для сохранения.
        """
        if isinstance(entity, list):
            self._session.add_all(entity)

        else:
            self._session.add(entity)

        try:
            await self._session.commit()

        except SQLAlchemyError as error:
            msg = f"{self.model.__class__.__name__} saving error."
            raise RepositoryError(msg) from error

    @overload
    async def delete(self, id_: EntityID) -> None: ...

    @overload
    async def delete(self, id_: Sequence[EntityID]) -> None: ...

    async def delete(self, id_: EntityID | Sequence[EntityID]) -> None:
        """Метод удаления сущности или списка сущностей из БД
        по их идентификатору.

        Args:
            entity (EntityID | list[EntityID]): Идентификатор или список
                идентификаторов сущностей в БД.
        """
        pk = getattr(self.model, self.primary_key)
        stmt = delete_(self.model).where(
            pk.in_(id_) if isinstance(id_, Sequence) else pk == id_,
        )

        try:
            await self._session.execute(stmt)

        except SQLAlchemyError as error:
            msg = f"{self.model.__class__.__name__} deleting error."
            raise RepositoryError(msg) from error
