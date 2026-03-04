from pathlib import Path

from interfaces.repositories import IItemRepository
from repositories.base_json_repo import BaseJsonRepository


class JsonItemRepository(BaseJsonRepository, IItemRepository):
    """Concrete JSON-file implementation of IItemRepository.

    LSP: Fully satisfies the IItemRepository contract so the storage
    backend can be replaced (e.g. SQLite) without touching service code.
    """

    @property
    def data_path(self) -> Path:
        return Path(__file__).resolve().parents[1] / "data" / "items.json"
