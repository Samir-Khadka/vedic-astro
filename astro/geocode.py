"""Global place search + offline timezone resolution.

Local gazetteer entries (astro.places) always win; for everywhere else on
Earth we proxy OpenStreetMap Nominatim server-side (identifying
User-Agent, short timeout, small in-memory cache) and resolve each hit's
IANA timezone offline with `timezonefinder` — no API keys anywhere.

Failure policy: geocoding problems NEVER raise to the API layer. Search
returns ([], available=False) so the UI can fall back to manual
coordinates; the gazetteer keeps working regardless.
"""
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from collections import OrderedDict

from timezonefinder import TimezoneFinder

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "VedicAstro/1.1 (https://github.com/Samir-Khadka/vedic-astro)"
TIMEOUT_SECONDS = 4.0
MAX_GLOBAL_RESULTS = 5
MIN_QUERY_CHARS = 3
_CACHE_MAX = 128

_finder: TimezoneFinder | None = None
_cache: "OrderedDict[str, tuple[list[dict], bool]]" = OrderedDict()


def _get_finder() -> TimezoneFinder:
    global _finder
    if _finder is None:
        _finder = TimezoneFinder()
    return _finder


def timezone_at(lat: float, lon: float) -> str | None:
    """IANA timezone name for coordinates, or None (e.g. open ocean)."""
    try:
        return _get_finder().timezone_at(lat=float(lat), lng=float(lon))
    except Exception:
        return None


def _fetch_nominatim(query: str) -> list[dict]:
    """One Nominatim request; returns the raw parsed JSON list.

    Kept as a module-level function so tests can monkeypatch it — the
    test suite never touches the live network.
    """
    params = urllib.parse.urlencode({
        "q": query,
        "format": "jsonv2",
        "limit": MAX_GLOBAL_RESULTS,
        "addressdetails": "0",
        "accept-language": "en",
    })
    req = urllib.request.Request(
        f"{NOMINATIM_URL}?{params}",
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _shorten(display_name: str) -> tuple[str, str, str]:
    """(name, region/country, label) from a Nominatim display_name.

    "Reykjavík, Capital Region, Iceland" -> ("Reykjavík", "Iceland",
    "Reykjavík, Iceland"). Single-part names pass through unchanged.
    """
    parts = [p.strip() for p in (display_name or "").split(",") if p.strip()]
    if not parts:
        return "", "", ""
    name = parts[0]
    region = parts[-1] if len(parts) > 1 else ""
    label = f"{name}, {region}" if region and region != name else name
    return name, region, label


def parse_nominatim(raw: list[dict]) -> list[dict]:
    """Normalize raw Nominatim items into API place dicts with tz attached."""
    out: list[dict] = []
    for item in raw or []:
        try:
            lat = float(item["lat"])
            lon = float(item["lon"])
        except (KeyError, TypeError, ValueError):
            continue
        name, region, label = _shorten(item.get("display_name", ""))
        if not name:
            continue
        out.append({
            "id": None,
            "source": "global",
            "name": name,
            "country": region,
            "label": label,
            "lat": lat,
            "lon": lon,
            "tz": timezone_at(lat, lon),
        })
    return out


def search_global(query: str) -> tuple[list[dict], bool]:
    """(global results, nominatim_available). Cached per normalized query."""
    q = (query or "").strip()
    if len(q) < MIN_QUERY_CHARS:
        return [], True
    key = q.lower()
    if key in _cache:
        _cache.move_to_end(key)
        return _cache[key]
    try:
        results = parse_nominatim(_fetch_nominatim(q))
        outcome: tuple[list[dict], bool] = (results, True)
    except Exception:
        outcome = ([], False)
    _cache[key] = outcome
    if len(_cache) > _CACHE_MAX:
        _cache.popitem(last=False)
    return outcome
