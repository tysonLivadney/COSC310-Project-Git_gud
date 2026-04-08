from pathlib import Path
from repositories.base_repo import load_json, save_json

_FILE = Path(__file__).resolve().parent.parent / "data" / "promo_codes.json"


def load_all() -> list:
    return load_json(_FILE, [])


def save_all(data: list) -> None:
    save_json(_FILE, data)
