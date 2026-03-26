from pathlib import Path
import json, os
from typing import Dict, Any

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "locations.json"

def load_all() -> Dict[str, Any]:
    if not DATA_PATH.exists():
        return {
            "users": {},
            "drivers": {},
            "restaurants": {}
        }
    with DATA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_all(locations: Dict[str, Any]) -> None:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = DATA_PATH.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(locations, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA_PATH)