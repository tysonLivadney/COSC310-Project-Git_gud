from pathlib import Path
import json
import os
from typing import Any, Dict, List


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "sessions.json"


def load_all() -> List[Dict[str, Any]]:
    if not DATA_PATH.exists():
        return []
    with DATA_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_all(sessions: List[Dict[str, Any]]) -> None:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = DATA_PATH.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as file:
        json.dump(sessions, file, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA_PATH)
