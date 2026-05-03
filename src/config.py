from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


DEFAULT_GESTURES: List[Dict[str, Any]] = [
    {
        "name": "Move Left",
        "key": "a",
        "pattern": {
            "thumb": False,
            "index": False,
            "middle": False,
            "ring": False,
            "pinky": False,
        },
    },
    {
        "name": "Move Right",
        "key": "d",
        "pattern": {
            "thumb": True,
            "index": True,
            "middle": True,
            "ring": True,
            "pinky": True,
        },
    },
    {
        "name": "Jump",
        "key": "space",
        "pattern": {
            "thumb": False,
            "index": True,
            "middle": False,
            "ring": False,
            "pinky": False,
        },
    },
]


def load_config(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return data if isinstance(data, list) else []


def save_config(path: Path, gestures: List[Dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as file:
        json.dump(gestures, file, indent=2)
