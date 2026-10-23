"""API smoke tests via FastAPI TestClient, incl. premium report and PDF."""
import re

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)
DEVANAGARI = re.compile(r"[\u0900-\u097F]")
SAMPLE = {"name": "Sample", "dob": "1998-05-14", "tob": "06:30", "place_id": "kathmandu"}


def test_health():
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_places_search():
    r = client.get("/api/places", params={"q": "kath"})
    assert r.status_code == 200
    ids = [p["id"] for p in r.json()["places"]]
    assert "kathmandu" in ids
    r2 = client.get("/api/places", params={"q": "urla"})
    assert any(p["id"] == "urlabari" for p in r2.json()["places"])


def test_panchang_endpoint():
    r = client.get("/api/panchang", params={"date": "2026-10-23", "place_id": "kathmandu"})
    assert r.status_code == 200
    body = r.json()
    for key in ("tithi_index", "nakshatra_index", "yoga_index", "karana", "sunrise", "sunset"):
        assert key in body
    assert 0 <= body["tithi_index"] <= 29


def test_kundali_bundle_shape_and_bilingual():
    r = client.post("/api/kundali", json=SAMPLE)
    assert r.status_code == 200
    b = r.json()
    for key in ("lagna", "planets", "charts", "dasha", "kp", "doshas",
                "ashtakavarga", "yogas", "predictions", "report", "karakas"):
        assert key in b, key
    assert set(b["charts"].keys()) >= {"D1", "D9", "D10"}
    # Bilingual predictions: every section statement carries en + ne,
    # and the Nepali text is real Devanagari.
    all_ne = []
    for facts in b["predictions"].values():
        for f in facts:
            assert f["en"] and f["ne"]
            all_ne.append(f["ne"])
    assert any(DEVANAGARI.search(s) for s in all_ne)
    moon = next(p for p in b["planets"] if p["planet"] == "Moon")
    assert DEVANAGARI.search(moon["name_ne"])


def test_premium_report_contents():
    r = client.post("/api/kundali", json=SAMPLE)
    rep = r.json()["report"]
    assert set(rep["chapters"].keys()) == {
        "personality", "career", "finance", "marriage",
        "health", "education", "family", "foreign",
    }
    for facts in rep["chapters"].values():
        assert facts and all(f["en"] and f["ne"] for f in facts)
    assert len(rep["favourable_periods"]) == 10
    assert len(rep["varshphal"]) == 3
    for v in rep["varshphal"]:
        assert 1 <= v["muntha"]["house"] <= 12 and v["year_lord"]
        assert v["reading"]["en"] and DEVANAGARI.search(v["reading"]["ne"])
    gems = rep["remedies"]["gemstones"]
    assert len(gems) == 3 and all(g["stone"]["en"] and g["stone"]["ne"] for g in gems)
    assert rep["remedies"]["mantra"]["beej_ne"]
    assert DEVANAGARI.search(rep["remedies"]["mantra"]["beej_ne"])
    assert rep["lucky"]["number"]["en"]


def test_match_endpoint():
    r = client.post("/api/match", json={"groom": SAMPLE, "bride": SAMPLE})
    assert r.status_code == 200
    body = r.json()
    assert 0 <= body["total"] <= 36 and len(body["breakdown"]) == 8
    assert body["verdict_en"] and body["verdict_ne"]
    assert body["manglik_note"]["en"] and body["manglik_note"]["ne"]


def test_pdf_endpoint_returns_real_pdf():
    r = client.get("/api/report.pdf", params=SAMPLE)
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/pdf")
    assert r.content[:5] == b"%PDF-"
    assert len(r.content) > 3000


def test_kundali_custom_coordinates():
    payload = {"dob": "2000-01-01", "tob": "12:00", "lat": 28.2096, "lon": 83.9856, "tz": "Asia/Kathmandu"}
    r = client.post("/api/kundali", json=payload)
    assert r.status_code == 200
    assert r.json()["birth"]["place"]["name"] == "Custom location"


def test_kundali_bad_place_is_400():
    r = client.post("/api/kundali", json={"dob": "2000-01-01", "tob": "12:00", "place_id": "nowhere"})
    assert r.status_code == 400
