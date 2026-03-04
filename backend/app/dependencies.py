# DIP: This module is the single place where abstract interfaces are bound to
# concrete implementations.  Routers and services depend only on the abstractions;
# swapping storage backends (e.g. JSON → SQLite) requires changes here only.
from fastapi import Depends, Header, HTTPException

from repositories.items_repo import JsonItemRepository
from repositories.sessions_repo import JsonSessionRepository
from repositories.users_repo import JsonUserRepository
from schemas.auth import UserResponse
from services.auth_service import AuthService
from services.items_service import ItemService
from services.password_service import PasswordService
from services.session_service import SessionService


# ---------------------------------------------------------------------------
# Repository providers
# ---------------------------------------------------------------------------

def get_user_repo() -> JsonUserRepository:
    return JsonUserRepository()


def get_session_repo() -> JsonSessionRepository:
    return JsonSessionRepository()


def get_item_repo() -> JsonItemRepository:
    return JsonItemRepository()


# ---------------------------------------------------------------------------
# Service providers
# ---------------------------------------------------------------------------

def get_password_service() -> PasswordService:
    return PasswordService()


def get_session_service(
    session_repo: JsonSessionRepository = Depends(get_session_repo),
) -> SessionService:
    return SessionService(session_repo)


def get_auth_service(
    user_repo: JsonUserRepository = Depends(get_user_repo),
    password_service: PasswordService = Depends(get_password_service),
    session_service: SessionService = Depends(get_session_service),
) -> AuthService:
    return AuthService(user_repo, password_service, session_service)


def get_item_service(
    item_repo: JsonItemRepository = Depends(get_item_repo),
) -> ItemService:
    return ItemService(item_repo)


# ---------------------------------------------------------------------------
# Shared FastAPI dependency: resolved current user
# ---------------------------------------------------------------------------

def _extract_bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Authentication required")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    return token.strip()


def get_current_user(
    authorization: str | None = Header(default=None),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    token = _extract_bearer_token(authorization)
    return auth_service.get_current_user(token)
