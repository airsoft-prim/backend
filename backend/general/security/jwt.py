from enum import StrEnum


class Algorithm(StrEnum):
    """Класс, представляющий алгоритм шифрования."""

    AUTO = "AUTO"
    HS256 = "HS256"
    RS256 = "RS256"


class TokenManager:
    """_summary_"""

    def __init__(self, algorithm: Algorithm | list[Algorithm] = Algorithm.AUTO) -> None:
        """Инициализация класса."""
        self.secret_key: str | None = None

        if isinstance(algorithm, list) and Algorithm.AUTO in algorithm:
            algorithm = Algorithm.AUTO

        self.algorithm = algorithm

    def set_secret_key(self, secret_key: str) -> None:
        """Устанавливает секретный ключ для шифрования токенов.

        Args:
            secret_key (str): Новый секретный ключ.
        """
        self.secret_key = secret_key

    def encode(self, payload: dict) -> str:
        """Метод кодирования полезной нагрузки в JWT токен.

        Args:
            payload (dict): Полезная нагрузка для кодирования.

        Returns:
            str: Закодированный JWT токен.
        """
        return "encoded_token"

    def decode(self, token: str) -> dict:
        return {"sub": "user_id", "roles": ["role1", "role2"]}
