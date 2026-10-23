"""Built-in place gazetteer (data/places.json).

API callers may bypass it entirely by supplying raw lat/lon/tz.
"""
from __future__ import annotations

import json
from pathlib import Path

_PATH = Path(__file__).resolve().parent.parent / "data" / "places.json"
_PLACES: list[dict] = json.loads(_PATH.read_text(encoding="utf-8"))
_BY_ID = {p["id"]: p for p in _PLACES}


def get_place(place_id: str) -> dict | None:
    return _BY_ID.get(place_id)


def search_places(query: str, limit: int = 10) -> list[dict]:
    q = (query or "").strip().lower()
    if not q:
        return _PLACES[:limit]
    hits = [
        p for p in _PLACES
        if q in p["name"].lower() or q in p["country"].lower() or q in p["id"]
    ]
    hits.sort(key=lambda p: (not p["name"].lower().startswith(q), p["name"]))
    return hits[:limit]


def all_places() -> list[dict]:
    return list(_PLACES)
