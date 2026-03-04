# SRP: AuthService is responsible only for user registration and login.
#      Session lifecycle is delegated to SessionService.
#      Password hashing is delegated to PasswordService.
# DIP: AuthService depends on abstract interfaces (IUserRepository,
#      SessionService, PasswordService), not on concrete implementations.
import uuid
from collections.abc import Callable
from datetime import datetime, timezone

from fastapi import Depends, Header, HTTPException
from interfaces.repositories import IUserRepository
from schemas.auth import LoginRequest, LoginResponse, RegisterRequest, Role, UserResponse
from services.password_service import PasswordService
from services.session_service import SessionService


class AuthService:
    """Handles user registration, login, and identity resolution."""

    def __init__(
        self,
        user_repo: IUserRepository,
        password_service: PasswordService,
        session_service: SessionService,
    ) -> None:
        self._user_repo = user_repo
        self._password_service = password_service
        self._session_service = session_service

    def register_user(self, payload: RegisterRequest) -> UserResponse:
        users = self._user_repo.load_all()
        normalized_email = _normalize_email(payload.email)

        if any(_normalize_email(u["email"]) == normalized_email for u in users):
            raise HTTPException(status_code=400, detail="An account with that email already exists")

        salt_hex = self._password_service.generate_salt()
        user = {
            "id": str(uuid.uuid4()),
            "name": payload.name.strip(),
            "email": normalized_email,
            "role": payload.role,
            "password_salt": salt_hex,
            "password_hash": self._password_service.hash_password(payload.password, salt_hex),
            "created_at": _to_utc_string(datetime.now(timezone.utc)),
        }
        users.append(user)
        self._user_repo.save_all(users)
        return _build_user_response(user)

    def login_user(self, payload: LoginRequest) -> LoginResponse:
        users = self._user_repo.load_all()
        normalized_email = _normalize_email(payload.email)

        for user in users:
            if _normalize_email(user["email"]) != normalized_email:
                continue

            if not self._password_service.verify_password(
                payload.password, user["password_salt"], user["password_hash"]
            ):
                break

            session = self._session_service.create_session(user["id"])
            return LoginResponse(
                token=session["token"],
                token_type="bearer",
                expires_at=session["expires_at"],
                user=_build_user_response(user),
            )

        raise HTTPException(status_code=401, detail="Invalid email or password")

    def get_current_user(self, token: str) -> UserResponse:
        session = self._session_service.get_active_session(token)
        if session is None:
            raise HTTPException(status_code=401, detail="Invalid or expired session token")

        users = self._user_repo.load_all()
        for user in users:
            if user["id"] == session["user_id"]:
                return _build_user_response(user)

        raise HTTPException(status_code=404, detail="User not found")


# ---------------------------------------------------------------------------
# Module-level helpers (pure functions with no external dependencies)
# ---------------------------------------------------------------------------

def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _to_utc_string(value: datetime) -> str:
    return value.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _build_user_response(user: dict) -> UserResponse:
    return UserResponse(
        id=user["id"],
        name=user["name"],
        email=user["email"],
        role=user["role"],
        created_at=user["created_at"],
    )


# ---------------------------------------------------------------------------
# FastAPI dependency helpers (kept here so routers import from one place)
# ---------------------------------------------------------------------------

def require_roles(*allowed_roles: Role) -> Callable:
    """Factory that returns a FastAPI dependency enforcing role-based access."""
    from dependencies import get_current_user  # deferred to avoid circular import

    def role_checker(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to perform this action",
            )
        return current_user

    return role_checker
