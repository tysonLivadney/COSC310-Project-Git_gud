from pathlib import Path

from interfaces.repositories import ISessionRepository
from repositories.base_json_repo import BaseJsonRepository


class JsonSessionRepository(BaseJsonRepository, ISessionRepository):
    """Concrete JSON-file implementation of ISessionRepository.

    LSP: Fully satisfies the ISessionRepository contract so callers are
    decoupled from the JSON storage detail.
    """

    @property
    def data_path(self) -> Path:
        return Path(__file__).resolve().parents[1] / "data" / "sessions.json"
