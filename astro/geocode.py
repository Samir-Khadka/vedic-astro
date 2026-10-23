"""Global place search + offline timezone resolution.

Local gazetteer entries (astro.places) always win; for everywhere else on
Earth we ask a chain of free, key-less geocoding providers server-side
(identifying User-Agent, short timeout, small in-memory cache) and resolve
each hit's IANA timezone offline with `timezonefinder` when the provider
does not supply one.

Provider chain (first non-empty answer wins):
  1. Open-Meteo Geocoding — built for server API use, returns an IANA
     `timezone` per hit (preferred over the offline lookup when present).
  2. Photon (Komoot) — OSM geocoder that tolerates datacenter IPs.
  3. Nominatim — last resort only: its usage policy intermittently blocks
     datacenter egress IPs (observed HTTP 403 blocks from Render lasting
     days), which is why it is no longer the primary provider.

Failure policy: geocoding problems NEVER raise to the API layer. Search
returns ([], available) so the UI can fall back to manual coordinates;
the gazetteer keeps working regardless. `available` is True when at
least one global provider answered (even with zero hits).
"""
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from collections import OrderedDict

from timezonefinder import TimezoneFinder

OPEN_METEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
PHOTON_URL = "https://photon.komoot.io/api/"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "VedicAstro/1.2 (https://github.com/Samir-Khadka/vedic-astro)"
TIMEOUT_SECONDS = 4.0
MAX_GLOBAL_RESULTS = 8
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


def _get_json(url: str):
    """GET `url` and parse the JSON body. Raises on any failure."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _place(name: str, country: str, lat: float, lon: float,
           tz: str | None = None) -> dict:
    """One normalized API place dict; tz falls back to the offline lookup."""
    label = f"{name}, {country}" if country and country != name else name
    return {
        "id": None,
        "source": "global",
        "name": name,
        "country": country,
        "label": label,
        "lat": lat,
        "lon": lon,
        "tz": tz if tz else timezone_at(lat, lon),
    }


# ---------------- Open-Meteo (primary) ------------------------------------

def _fetch_open_meteo(query: str) -> dict:
    """One Open-Meteo Geocoding request; returns the raw parsed JSON.

    Kept as a module-level function so tests can monkeypatch it — the
    test suite never touches the live network.
    """
    params = urllib.parse.urlencode({
        "name": query,
        "count": MAX_GLOBAL_RESULTS,
        "language": "en",
        "format": "json",
    })
    return _get_json(f"{OPEN_METEO_URL}?{params}")


def parse_open_meteo(raw: dict) -> list[dict]:
    """Normalize Open-Meteo `results` into API place dicts.

    The provider's own `timezone` field wins when present; otherwise the
    offline timezonefinder lookup fills it in. A response with no matches
    has no `results` key at all — that parses to [].
    """
    out: list[dict] = []
    for item in (raw or {}).get("results") or []:
        try:
            lat = float(item["latitude"])
            lon = float(item["longitude"])
        except (KeyError, TypeError, ValueError):
            continue
        name = (item.get("name") or "").strip()
        if not name:
            continue
        country = (item.get("country") or "").strip()
        tz = (item.get("timezone") or "").strip() or None
        out.append(_place(name, country, lat, lon, tz))
    return out[:MAX_GLOBAL_RESULTS]


# ---------------- Photon (secondary) --------------------------------------

def _fetch_photon(query: str) -> dict:
    """One Photon request; returns the raw parsed GeoJSON dict."""
    params = urllib.parse.urlencode({
        "q": query,
        "limit": MAX_GLOBAL_RESULTS,
        "lang": "en",
    })
    return _get_json(f"{PHOTON_URL}?{params}")


def _photon_rank(feature: dict) -> int:
    """Prefer real places (cities, boundaries) over POIs like stations."""
    props = feature.get("properties") or {}
    if props.get("osm_key") in ("place", "boundary"):
        return 0
    if props.get("type") in ("city", "town", "village", "hamlet", "locality",
                             "county", "district", "state", "country"):
        return 1
    return 2


def parse_photon(raw: dict) -> list[dict]:
    """Normalize Photon GeoJSON features into API place dicts.

    Photon supplies no timezone, so every hit goes through the offline
    timezonefinder lookup. Features are stably re-ranked so settlements
    outrank same-named stations/POIs.
    """
    features = (raw or {}).get("features") or []
    out: list[dict] = []
    for feature in sorted(features, key=_photon_rank):
        props = feature.get("properties") or {}
        coords = (feature.get("geometry") or {}).get("coordinates") or []
        if len(coords) < 2:
            continue
        try:
            lon = float(coords[0])
            lat = float(coords[1])
        except (TypeError, ValueError):
            continue
        name = (props.get("name") or props.get("city") or "").strip()
        if not name:
            continue
        country = (props.get("country") or "").strip()
        out.append(_place(name, country, lat, lon))
    return out[:MAX_GLOBAL_RESULTS]


# ---------------- Nominatim (last resort) ---------------------------------

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
    return _get_json(f"{NOMINATIM_URL}?{params}")


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
        hit = _place(name, region, lat, lon)
        hit["label"] = label
        out.append(hit)
    return out


# ---------------- provider chain ------------------------------------------

# Fetcher names (not function objects) so tests can monkeypatch the
# module-level `_fetch_*` functions and have the chain pick up the mocks.
_PROVIDERS = (
    ("open-meteo", "_fetch_open_meteo", parse_open_meteo),
    ("photon", "_fetch_photon", parse_photon),
    ("nominatim", "_fetch_nominatim", parse_nominatim),
)


def search_global(query: str) -> tuple[list[dict], bool]:
    """(global results, global_available). Cached per normalized query.

    Providers are tried in order; a provider that errors OR answers with
    zero hits falls through to the next. The first non-empty answer wins.
    `global_available` is True when at least one provider answered at
    all, even if every answer was empty.
    """
    q = (query or "").strip()
    if len(q) < MIN_QUERY_CHARS:
        return [], True
    key = q.lower()
    if key in _cache:
        _cache.move_to_end(key)
        return _cache[key]
    results: list[dict] = []
    answered = False
    for _name, fetch_attr, parse in _PROVIDERS:
        fetch = globals()[fetch_attr]
        try:
            hits = parse(fetch(q))
        except Exception:
            continue
        answered = True
        if hits:
            results = hits
            break
    outcome: tuple[list[dict], bool] = (results, answered)
    _cache[key] = outcome
    if len(_cache) > _CACHE_MAX:
        _cache.popitem(last=False)
    return outcome
