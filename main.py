import uvicorn

from backend.app import app
from backend.core.config import config


def main() -> None:
    """Точка входа в приложение."""
    if not config.app.DEBUG:
        uvicorn.run(app, host="localhost", port=8000)

    else:
        uvicorn.run("main:app", host="localhost", port=8000, reload=True)


if __name__ == "__main__":
    main()
