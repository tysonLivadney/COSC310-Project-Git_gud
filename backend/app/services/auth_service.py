# Passwords are salted and hashed before storage so the JSON file never contains plaintext passwords.
# Every protected route resolves the session from the bearer token and rejects expired tokens.
# This factory returns a FastAPI dependency so routes can declare which roles are allowed.

import hashlib
import hmac
import secrets
import uuid
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from fastapi import Depends, Header, HTTPException
from repositories.sessions_repo import load_all as load_all_sessions
from repositories.sessions_repo import save_all as save_all_sessions
from repositories.users_repo import load_all as load_all_users
from repositories.users_repo import save_all as save_all_users
from schemas.auth import LoginRequest, LoginResponse, RegisterRequest, Role, UserResponse


SESSION_DURATION_HOURS = 24


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _to_utc_string(value: datetime) -> str:
    return value.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _normalize_email(email: str) -> str:
    return email.strip().lower()

def _hash_password(password: str, salt_hex: str) -> str:
    salt = bytes.fromhex(salt_hex)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return digest.hex()


def _build_user_response(user: dict) -> UserResponse:
    return UserResponse(
        id=user["id"],
        name=user["name"],
        email=user["email"],
        role=user["role"],
        created_at=user["created_at"],
    )


def register_user(payload: RegisterRequest) -> UserResponse:
    users = load_all_users()
    normalized_email = _normalize_email(payload.email)

    if any(_normalize_email(user["email"]) == normalized_email for user in users):
        raise HTTPException(status_code=400, detail="An account with that email already exists")

    salt_hex = secrets.token_hex(16)
    user = {
        "id": str(uuid.uuid4()),
        "name": payload.name.strip(),
        "email": normalized_email,
        "role": payload.role,
        "password_salt": salt_hex,
        "password_hash": _hash_password(payload.password, salt_hex),
        "created_at": _to_utc_string(_utc_now()),
    }
    users.append(user)
    save_all_users(users)
    return _build_user_response(user)


def login_user(payload: LoginRequest) -> LoginResponse:
    users = load_all_users()
    normalized_email = _normalize_email(payload.email)

    for user in users:
        if _normalize_email(user["email"]) != normalized_email:
            continue

        expected_hash = _hash_password(payload.password, user["password_salt"])
        if not hmac.compare_digest(expected_hash, user["password_hash"]):
            break

        sessions = load_all_sessions()
        now = _utc_now()
        expires_at = now + timedelta(hours=SESSION_DURATION_HOURS)
        session = {
            "token": secrets.token_urlsafe(32),
            "user_id": user["id"],
            "created_at": _to_utc_string(now),
            "expires_at": _to_utc_string(expires_at),
        }
        sessions.append(session)
        save_all_sessions(sessions)

        return LoginResponse(
            token=session["token"],
            token_type="bearer",
            expires_at=session["expires_at"],
            user=_build_user_response(user),
        )

    raise HTTPException(status_code=401, detail="Invalid email or password")

def _extract_bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Authentication required")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    return token.strip()

def get_current_user(authorization: str | None = Header(default=None)) -> UserResponse:
    token = _extract_bearer_token(authorization)
    sessions = load_all_sessions()
    now = _utc_now()

    active_session = None
    for session in sessions:
        if session["token"] != token:
            continue
        expires_at = datetime.fromisoformat(session["expires_at"].replace("Z", "+00:00"))
        if expires_at <= now:
            raise HTTPException(status_code=401, detail="Session has expired")
        active_session = session
        break

    if active_session is None:
        raise HTTPException(status_code=401, detail="Invalid session token")

    users = load_all_users()
    for user in users:
        if user["id"] == active_session["user_id"]:
            return _build_user_response(user)

    raise HTTPException(status_code=404, detail="User not found")

def require_roles(*allowed_roles: Role) -> Callable[[UserResponse], UserResponse]:
    def role_checker(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="You do not have permission to perform this action")
        return current_user

    return role_checker
