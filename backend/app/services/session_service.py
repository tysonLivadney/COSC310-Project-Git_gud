import secrets
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from repositories.sessions_repo import load_all as load_all_sessions
from repositories.sessions_repo import save_all as save_all_sessions

SESSION_DURATION_HOURS = 24


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _to_utc_string(value: datetime) -> str:
    return value.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def create_session(user_id: str) -> dict:
    now = _utc_now()
    expires_at = now + timedelta(hours=SESSION_DURATION_HOURS)
    session = {
        "token": secrets.token_urlsafe(32),
        "user_id": user_id,
        "created_at": _to_utc_string(now),
        "expires_at": _to_utc_string(expires_at),
    }
    sessions = load_all_sessions()
    sessions.append(session)
    save_all_sessions(sessions)
    return session


def resolve_session(token: str) -> str:
    sessions = load_all_sessions()
    now = _utc_now()
    for session in sessions:
        if session["token"] != token:
            continue
        expires_at = datetime.fromisoformat(session["expires_at"].replace("Z", "+00:00"))
        if expires_at <= now:
            raise HTTPException(status_code=401, detail="Session has expired")
        return session["user_id"]
    raise HTTPException(status_code=401, detail="Invalid session token")
