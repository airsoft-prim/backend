from fastapi import APIRouter

from .docs import LOGIN_DOCS, LOGOUT_DOCS, ME_DOCS, REGISTER_DOCS

router = APIRouter(prefix="/auth", tags=["Аутентификация"])


@router.post("/login", **LOGIN_DOCS)
async def login() -> None:
    pass


@router.post("/register", **REGISTER_DOCS)
async def register() -> None:
    pass


@router.post("/logout", **LOGOUT_DOCS)
async def logout() -> None:
    pass


@router.get("/me", **ME_DOCS)
async def me() -> None:
    pass
