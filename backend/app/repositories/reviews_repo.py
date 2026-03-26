from pathlib import Path
from typing import Any, Dict, List
from repositories.base_repo import load_json, save_json

_PATH = Path(__file__).resolve().parents[1] / "data" / "reviews.json"


def load_all() -> List[Dict[str, Any]]:
    return load_json(_PATH, [])


def save_all(data: List[Dict[str, Any]]) -> None:
    save_json(_PATH, data)
