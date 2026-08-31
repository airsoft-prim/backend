from collections.abc import Mapping
from copy import copy
from typing import Any, Self

from sqlalchemy import func, select
from sqlalchemy.sql import Select
from sqlalchemy.sql.expression import ColumnElement

from backend.general.enums import SortDirection
from backend.general.types import FilterMapping, SortMapping


# TODO: Добавить проверку на соответствие типа колонки и значения фильтра
class SearchBuilder:
    """Строитель поисковых запросов SQLAlchemy."""

    def __init__(
        self, statement: Select[Any], *, field_map: Mapping[str, str] | None = None
    ) -> None:
        """Инициализация класса.

        Args:
            statement (Select): Select выражение SQLAlchemy.
            field_map (Mapping[str, str] | None): Маппинг названия полей. Необходим в
                случаях, когда имя поля в Select было помечено через label или
                если фильтры/сортировки наследуют изменённые названия полей из
                схемы публичного API. Defaults to None.
        """
        self._statement = statement
        self._field_mapper = field_map or {}

    def complete(self) -> Select[Any]:
        """Завершает строительство выражения, возвращая
        копию результата.

        Returns:
            Select[Any]: Построенное выражение.
        """
        return copy(self._statement)

    def as_count(self) -> Select[tuple[int]]:
        """Оборачивает текущее состояние Statement в count-запрос.

        Подзапрос снимается с текущего состояния без мутаций: дальнейшие
        вызовы add_sorts/add_pagination на билдере не влияют на результат.

        Returns:
            Select[tuple[int]]: Запрос `SELECT count(*) FROM (<Select>)`.
        """
        return select(func.count()).select_from(self._statement.subquery())

    def add_filters(self, filters: list[FilterMapping]) -> Self:
        """Применяет правила фильтрации к Select выражению.

        Каждое правило добавляет в WHERE условие `column <оператор> value`,
        правила объединяются через AND. Колонка ищется через resolve_column,
        поэтому работают field_map и разрешение коллизий имён при выборке
        из нескольких таблиц.

        Args:
            filters (list[FilterMapping]): Правила фильтрации.

        Returns:
            Self: Экземпляр строителя.
        """
        for filter_ in filters:
            column = self._resolve_column(filter_["field"])
            condition = filter_["operator"].python(column, filter_["value"])
            self._statement = self._statement.where(condition)

        return self

    def add_sorts(self, sorts: list[SortMapping]) -> Self:
        """Применяет правила сортировки к Select выражению.

        Каждое правило превращается в `ORDER BY column ASC|DESC`; повторные
        вызовы order_by накапливают критерии, как и where. Колонка ищется
        через resolve_column, поэтому работают field_map и разрешение
        коллизий имён при выборке из нескольких таблиц.

        Args:
            sorts (list[SortMapping]): Правила сортировки.

        Returns:
            Self: Экземпляр строителя.
        """
        for sort_ in sorts:
            column = self._resolve_column(sort_["field"])
            direction = column.asc() if sort_["direction"] == SortDirection.ASC else column.desc()
            self._statement = self._statement.order_by(direction)

        return self

    def add_pagination(self, page: int, page_size: int) -> Self:
        """Применяет параметры пагинации к Select выражению.

        Args:
            page (int): Номер страницы.
            page_size (int): Размер страницы.

        Returns:
            Self: Экземпляр строителя.
        """
        self._statement = self._statement.limit(page_size)
        self._statement = self._statement.offset((page - 1) * page_size)

        return self

    def _resolve_column(self, name: str) -> ColumnElement[Any]:
        """Возвращает колонку Select-выражения по имени поля.

        Имя сначала ищется в field_map — это позволяет обращаться к полям,
        переименованным через label или изменённым в схеме публичного API.
        Колонка берётся из selected_columns, поэтому при выборке из нескольких
        таблиц SQLAlchemy сам разрешает коллизии имён: базовый ключ достаётся
        первой колонке, а дубликаты получают суффикс ``_1``.

        Args:
            name (str): Имя поля (ключ в selected_columns).

        Returns:
            ColumnElement[Any]: Колонка, готовая к использованию в фильтрах
            и сортировках (сравнения, order_by и т. п.).

        Raises:
            AttributeError: Если колонки с таким именем нет в Select.
        """
        target_name = self._field_mapper.get(name) or name
        return getattr(self._statement.selected_columns, target_name)
