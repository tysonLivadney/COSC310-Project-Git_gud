# OCP: New storage backends can be added by extending BaseJsonRepository or the abstract
# interfaces without modifying any existing service code.
# DRY: The identical load/save pattern from all three repo modules is consolidated here.
from abc import abstractmethod
from pathlib import Path
from typing import Any, Dict, List
import json
import os


class BaseJsonRepository:
    """Shared JSON-file persistence logic for all repository implementations."""

    @property
    @abstractmethod
    def data_path(self) -> Path:
        ...

    def load_all(self) -> List[Dict[str, Any]]:
        if not self.data_path.exists():
            return []
        with self.data_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def save_all(self, data: List[Dict[str, Any]]) -> None:
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.data_path.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, self.data_path)
