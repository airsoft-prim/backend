from backend.general.types import FilterMapping, SortMapping
from backend.providers.database.models import Union

from ._base import DatabaseRepository


class UnionRepository(DatabaseRepository):
    """_summary_"""

    async def get_page(
        self, page: int, page_size: int, filters: list[FilterMapping], sorts: list[SortMapping]
    ) -> tuple[list[Union], int]:

        return [], 0
