from collections.abc import Mapping
from typing import ClassVar

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from backend.domain.repositories import RepositoryError
from backend.general.types import FilterMapping, SortMapping
from backend.providers.database.builder import SearchBuilder
from backend.providers.database.models import Union, UnionProfile

from ._base import DatabaseRepository


class UnionsRepository(DatabaseRepository):
    """Репозиторий доступа к данным объединений."""

    model = Union

    FIELD_MAP: ClassVar[Mapping[str, str]] = {
        "date_create": "created_at",
        "members": "members_count",
    }

    async def get_page(
        self, page: int, page_size: int, filters: list[FilterMapping], sorts: list[SortMapping]
    ) -> tuple[list[Union], int]:
        """Возвращает страницу объединений и общее число записей.

        Количество участников доступно на каждом объединении как
        `Union.members_count` — column_property модели (коррелированный
        COUNT-подзапрос, без размножения строк).

        Args:
            page (int): Номер запрашиваемой страницы.
            page_size (int): Количество записей на странице.
            filters (list[FilterMapping]): Правила фильтрации.
            sorts (list[SortMapping]): Правила сортировки.

        Returns:
            tuple[list[Union], int]: Страница объединений и общее число записей.
        """
        builder = SearchBuilder(
            select(self.model).options(
                joinedload(self.model.profile).load_only(
                    UnionProfile.avatar_url,
                    UnionProfile.motto,
                )
            ),
            field_map=self.FIELD_MAP,
        ).add_filters(filters)

        count_stmt = builder.as_count()

        builder.add_sorts(sorts)
        builder.add_pagination(page, page_size)

        items_stmt = builder.complete()

        try:
            total = await self._session.scalar(count_stmt)
            items = await self._session.scalars(items_stmt)

        except SQLAlchemyError as error:
            message = f"{self.model.__name__} page getting error."
            raise RepositoryError(message) from error

        return list(items.all()), total or 0

    async def get_with_profile(self, union_id: int) -> Union | None:
        """Возвращает объединение с подгруженным профилем.

        Args:
            union_id (int): Идентификатор объединения.

        Returns:
            Union | None: Объединение с профилем или None, если не найдено.
        """
        statement = (
            select(self.model)
            .where(self.model.id == union_id)
            .options(joinedload(self.model.profile))
        )

        try:
            result = await self._session.scalars(statement)
            return result.one_or_none()

        except SQLAlchemyError as error:
            message = f"{self.model.__name__} getting error."
            raise RepositoryError(message) from error

    async def get_by_name(self, name: str) -> Union | None:
        """Возвращает объединение по названию.

        Args:
            name (str): Название объединения.

        Returns:
            Union | None: Объединение или None, если не найдено.
        """
        statement = select(self.model).where(self.model.name == name)

        try:
            result = await self._session.scalars(statement)
            return result.one_or_none()

        except SQLAlchemyError as error:
            message = f"{self.model.__name__} getting by name error."
            raise RepositoryError(message) from error
