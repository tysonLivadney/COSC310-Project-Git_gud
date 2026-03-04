# SRP: Session lifecycle management is the sole responsibility of this service.
# DIP: Depends on ISessionRepository (an abstraction), not on the concrete
# JsonSessionRepository, so the storage backend is interchangeable.
import secrets
from datetime import datetime, timedelta, timezone

from interfaces.repositories import ISessionRepository


SESSION_DURATION_HOURS = 24


class SessionService:
    """Handles creating, validating, and expiring user sessions."""

    def __init__(self, session_repo: ISessionRepository) -> None:
        self._repo = session_repo

    def create_session(self, user_id: str) -> dict:
        sessions = self._repo.load_all()
        now = self._utc_now()
        expires_at = now + timedelta(hours=SESSION_DURATION_HOURS)
        session = {
            "token": secrets.token_urlsafe(32),
            "user_id": user_id,
            "created_at": self._to_utc_string(now),
            "expires_at": self._to_utc_string(expires_at),
        }
        sessions.append(session)
        self._repo.save_all(sessions)
        return session

    def get_active_session(self, token: str) -> dict | None:
        """Return the session dict if the token is valid and not expired, else None."""
        sessions = self._repo.load_all()
        now = self._utc_now()
        for session in sessions:
            if session["token"] != token:
                continue
            expires_at = datetime.fromisoformat(session["expires_at"].replace("Z", "+00:00"))
            if expires_at <= now:
                return None
            return session
        return None

    def _utc_now(self) -> datetime:
        return datetime.now(timezone.utc)

    def _to_utc_string(self, value: datetime) -> str:
        return value.replace(microsecond=0).isoformat().replace("+00:00", "Z")
