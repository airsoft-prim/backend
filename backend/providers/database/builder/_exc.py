from backend.general.exceptions import ProviderError


class QueryBuilderError(ProviderError):
    """Ошибка строителя запросов."""


class NotApplictableError(QueryBuilderError):
    """Неподходящий оператор или значение к целевому полю."""
