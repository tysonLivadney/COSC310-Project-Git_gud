from pathlib import Path
from typing import Any, Dict
from repositories.base_repo import load_json, save_json

_PATH = Path(__file__).resolve().parents[1] / "data" / "locations.json"

_DEFAULT: Dict[str, Any] = {"users": {}, "drivers": {}, "restaurants": {}}


def load_all() -> Dict[str, Any]:
    return load_json(_PATH, _DEFAULT)


def save_all(data: Dict[str, Any]) -> None:
    save_json(_PATH, data)
