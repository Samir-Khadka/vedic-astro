"""Global place search: offline timezone resolution, mocked Nominatim
parsing, gazetteer/global merge behaviour, payload parity and 422s.

The live network is never touched — Nominatim is monkeypatched, and the
geocode cache is cleared around every test so mocks cannot leak.
"""
import pytest
from fastapi.testclient import TestClient

from astro import engine, geocode
from main import app

client = TestClient(app)

SAMPLE_ID = {"dob": "1998-05-14", "tob": "06:30:00", "place_id": "kathmandu"}
SAMPLE_COORDS = {
    "dob": "1998-05-14", "tob": "06:30:00", "place_name": "Kathmandu, Nepal",
    "lat": 27.7172, "lon": 85.3240, "tz": "Asia/Kathmandu",
}

RAW_ULAANBAATAR = [{
    "place_id": 297999082, "lat": "47.9184678", "lon": "106.9177016",
    "display_name": "Ulaanbaatar, Mongolia", "type": "city",
}]
RAW_REYKJAVIK = [{
    "place_id": 123456, "lat": "64.146582", "lon": "-21.942635",
    "display_name": "Reykjavík, Capital Region, Iceland", "type": "city",
}]


@pytest.fixture(autouse=True)
def _clear_geocode_cache():
    geocode._cache.clear()
    yield
    geocode._cache.clear()


# ---------------- timezone golden cases (offline timezonefinder) ---------

@pytest.mark.parametrize("lat,lon,expected", [
    (27.7172, 85.3240, "Asia/Kathmandu"),       # Kathmandu
    (40.7128, -74.0060, "America/New_York"),    # New York
    (-33.8688, 151.2093, "Australia/Sydney"),   # Sydney
    (51.5074, -0.1278, "Europe/London"),        # London
    (47.9184, 106.9177, "Asia/Ulaanbaatar"),    # Ulaanbaatar
    (64.1466, -21.9426, "Atlantic/Reykjavik"),  # Reykjavik
])
def test_timezone_golden_cases(lat, lon, expected):
    assert geocode.timezone_at(lat, lon) == expected


def test_tz_endpoint():
    r = client.get("/api/tz", params={"lat": 27.7172, "lon": 85.3240})
    assert r.status_code == 200 and r.json() == {"tz": "Asia/Kathmandu"}


def test_tz_endpoint_rejects_bad_coords():
    assert client.get("/api/tz", params={"lat": 91, "lon": 0}).status_code == 422
    assert client.get("/api/tz", params={"lat": 0, "lon": -181}).status_code == 422


# ---------------- Nominatim parsing (mocked HTTP) -------------------------

def test_nominatim_parsing_attaches_timezone():
    results = geocode.parse_nominatim(RAW_ULAANBAATAR)
    assert len(results) == 1
    hit = results[0]
    assert hit["id"] is None and hit["source"] == "global"
    assert hit["name"] == "Ulaanbaatar" and hit["country"] == "Mongolia"
    assert hit["label"] == "Ulaanbaatar, Mongolia"
    assert hit["lat"] == pytest.approx(47.9184678)
    assert hit["tz"] == "Asia/Ulaanbaatar"


def test_nominatim_label_shortening_drops_region():
    hit = geocode.parse_nominatim(RAW_REYKJAVIK)[0]
    assert hit["name"] == "Reykjavík"
    assert hit["label"] == "Reykjavík, Iceland"
    assert hit["tz"] == "Atlantic/Reykjavik"


def test_search_global_uses_mocked_fetch(monkeypatch):
    monkeypatch.setattr(geocode, "_fetch_nominatim", lambda q: RAW_ULAANBAATAR)
    results, available = geocode.search_global("ulaanbaatar")
    assert available is True and results[0]["tz"] == "Asia/Ulaanbaatar"


def test_search_global_degrades_without_raising(monkeypatch):
    def boom(q):
        raise OSError("nominatim unreachable")
    monkeypatch.setattr(geocode, "_fetch_nominatim", boom)
    results, available = geocode.search_global("nowhereville")
    assert results == [] and available is False


def test_search_global_short_query_skips_network(monkeypatch):
    def boom(q):
        raise AssertionError("network must not be called")
    monkeypatch.setattr(geocode, "_fetch_nominatim", boom)
    assert geocode.search_global("ab") == ([], True)


# ---------------- /api/places merge behaviour -----------------------------

def test_places_gazetteer_first_and_deduped(monkeypatch):
    raw_dup = [{"lat": "27.7172", "lon": "85.3240",
                "display_name": "Kathmandu, Bagmati Province, Nepal"}]
    monkeypatch.setattr(geocode, "_fetch_nominatim", lambda q: raw_dup)
    r = client.get("/api/places", params={"q": "kathmandu"})
    assert r.status_code == 200
    body = r.json()
    kathmandus = [p for p in body["places"] if p["name"] == "Kathmandu"]
    assert len(kathmandus) == 1 and kathmandus[0]["id"] == "kathmandu"
    assert body["places"][0]["id"] == "kathmandu"
    assert body["global_available"] is True


def test_places_global_appended_after_local(monkeypatch):
    monkeypatch.setattr(geocode, "_fetch_nominatim", lambda q: RAW_ULAANBAATAR)
    r = client.get("/api/places", params={"q": "urla"})
    places = r.json()["places"]
    assert places[0]["id"] == "urlabari"  # curated local entry still first
    assert any(p.get("source") == "global" for p in places)


def test_places_survives_nominatim_outage(monkeypatch):
    def boom(q):
        raise TimeoutError("slow")
    monkeypatch.setattr(geocode, "_fetch_nominatim", boom)
    r = client.get("/api/places", params={"q": "urla"})
    assert r.status_code == 200
    body = r.json()
    assert body["global_available"] is False
    assert body["places"][0]["id"] == "urlabari"


# ---------------- payload parity + validation ---------------------------

def test_kundali_parity_place_id_vs_global_coords():
    a = engine.compute_kundali(SAMPLE_ID)
    b = engine.compute_kundali(SAMPLE_COORDS)
    assert a["lagna"]["longitude"] == b["lagna"]["longitude"]
    assert [p["longitude"] for p in a["planets"]] == [p["longitude"] for p in b["planets"]]
    assert a["dasha"]["current"] == b["dasha"]["current"]
    assert b["birth"]["place"]["name"] == "Kathmandu, Nepal"


def test_match_accepts_global_coords_payload():
    r = client.post("/api/match", json={"groom": SAMPLE_COORDS, "bride": SAMPLE_COORDS})
    assert r.status_code == 200
    assert 0 <= r.json()["total"] <= 36


def test_kundali_reykjavik_end_to_end():
    r = client.post("/api/kundali", json={
        "dob": "1990-01-15", "tob": "12:00", "place_name": "Reykjavík, Iceland",
        "lat": 64.1466, "lon": -21.9426, "tz": "Atlantic/Reykjavik",
    })
    assert r.status_code == 200
    body = r.json()
    assert body["birth"]["place"]["tz"] == "Atlantic/Reykjavik"
    assert 0 <= body["lagna"]["sign"] <= 11


def test_invalid_tz_is_422():
    payload = {"dob": "2000-01-01", "tob": "12:00",
               "lat": 10.0, "lon": 10.0, "tz": "Mars/Olympus_Mons"}
    assert client.post("/api/kundali", json=payload).status_code == 422


def test_invalid_coords_are_422():
    base = {"dob": "2000-01-01", "tob": "12:00", "tz": "UTC"}
    assert client.post("/api/kundali", json={**base, "lat": 91, "lon": 0}).status_code == 422
    assert client.post("/api/kundali", json={**base, "lat": 0, "lon": -181}).status_code == 422
    assert client.post("/api/match", json={
        "groom": {**base, "lat": 0, "lon": 999}, "bride": SAMPLE_ID}).status_code == 422


def test_panchang_invalid_tz_is_422():
    r = client.get("/api/panchang", params={
        "date": "2026-10-23", "lat": 10, "lon": 10, "tz": "Bad/Zone"})
    assert r.status_code == 422
