from pathlib import Path

from interfaces.repositories import IUserRepository
from repositories.base_json_repo import BaseJsonRepository


class JsonUserRepository(BaseJsonRepository, IUserRepository):
    """Concrete JSON-file implementation of IUserRepository.

    LSP: Fully satisfies the IUserRepository contract so any caller can
    substitute another IUserRepository implementation without behavioural
    changes (e.g. a database-backed repository in the future).
    """

    @property
    def data_path(self) -> Path:
        return Path(__file__).resolve().parents[1] / "data" / "users.json"
