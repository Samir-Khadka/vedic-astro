"""API smoke tests via FastAPI TestClient, incl. premium report and PDF."""
import re

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)
DEVANAGARI = re.compile(r"[\u0900-\u097F]")
SAMPLE = {"name": "Sample", "dob": "1998-05-14", "tob": "06:30", "place_id": "kathmandu"}


def test_health():
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_health_head():
    # UptimeRobot's free checks use HEAD; a GET-only route answered 405.
    r = client.head("/health")
    assert r.status_code == 200


def test_horoscope_bad_tz_is_400_not_500():
    r = client.get("/api/horoscope", params={"sign": 3, "tz": "Mars/Olympus"})
    assert r.status_code == 400


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


def test_bundle_has_phase2_sections():
    r = client.post("/api/kundali", json=SAMPLE)
    assert r.status_code == 200
    data = r.json()
    for key in ("strength", "transits_detail", "lal_kitab", "numerology",
                "name_letters", "dasha_phala", "yogini", "tribhagi"):
        assert key in data, key
    sb = data["strength"]["shadbala"]["planets"]
    assert set(sb) == {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"}
    assert data["name_letters"]["syllable_en"] == "Yu"
    assert data["numerology"]["moolank"]["value"] == 5
    assert len(data["report"]["year_ahead"]) >= 3
    # koota details are bilingual now
    m = client.post("/api/match", json={"groom": SAMPLE, "bride": SAMPLE})
    assert m.status_code == 200
    for row in m.json()["breakdown"]:
        assert set(row["detail"]) == {"en", "ne"}


def test_prashna_endpoint():
    r = client.post("/api/prashna", json={
        "number": 108, "question": "Will I get the job?",
        "place_name": "Kathmandu", "lat": 27.7172, "lon": 85.324,
        "tz": "Asia/Kathmandu",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["number"] == 108
    assert len(data["ruling_planets"]) == 7
    assert len(data["cusps"]) == 12
    assert data["sub"]["start_longitude"] < data["sub"]["end_longitude"]


def test_prashna_invalid_number():
    r = client.post("/api/prashna", json={
        "number": 250, "place_name": "Kathmandu", "lat": 27.7172, "lon": 85.324,
        "tz": "Asia/Kathmandu",
    })
    assert r.status_code == 422


def test_kundali_rejects_oversized_name():
    # Unbounded free-text fields let one request park megabytes in the
    # compute/PDF path and the localStorage share payload.
    r = client.post("/api/kundali", json={**SAMPLE, "name": "x" * 5000})
    assert r.status_code == 422
    r2 = client.post("/api/kundali", json={**SAMPLE, "place_name": "y" * 5000,
                                          "lat": 27.7, "lon": 85.3, "tz": "Asia/Kathmandu"})
    assert r2.status_code == 422


def test_prashna_rejects_oversized_question():
    r = client.post("/api/prashna", json={"number": 42, "question": "q" * 5000,
                                          "place_id": "kathmandu"})
    assert r.status_code == 422


def test_places_rejects_oversized_query():
    r = client.get("/api/places", params={"q": "k" * 500})
    assert r.status_code == 422


def test_security_headers_present():
    r = client.get("/health")
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert r.headers["X-Frame-Options"] == "SAMEORIGIN"
    assert r.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"


def test_rate_limit_trips_on_heavy_endpoints(monkeypatch):
    import main as main_module
    monkeypatch.setenv("VEDIC_RL_LIMIT", "2")
    main_module._RL_BUCKETS.clear()
    payload = {**SAMPLE}
    assert client.post("/api/kundali", json=payload).status_code == 200
    assert client.post("/api/kundali", json=payload).status_code == 200
    r = client.post("/api/kundali", json=payload)
    assert r.status_code == 429
    assert r.json()["detail"].startswith("rate limit")
    # /health is exempt and still answers.
    assert client.get("/health").status_code == 200
    main_module._RL_BUCKETS.clear()


def test_rl_is_heavy_covers_every_compute_endpoint():
    # Every unauthenticated endpoint that runs compute_kundali /
    # compute_match / a WeasyPrint render must be rate-limited.
    import main as main_module
    heavy = main_module._rl_is_heavy
    for method, path in [
        ("POST", "/api/kundali"), ("POST", "/api/complete-report"),
        ("POST", "/api/match"), ("POST", "/api/prashna"),
        ("POST", "/api/life-areas"), ("POST", "/api/ask-astrologer"),
        ("POST", "/api/life-questions/some-id/answer"),
        ("GET", "/api/report.pdf"), ("GET", "/api/complete-report.pdf"),
        # Multi-day compute GETs: a 31-day muhurta range costs ~2s, a
        # full panchang/bs month ~1s — as heavy as a kundali.
        ("GET", "/api/muhurta"), ("GET", "/api/panchang-month"),
        ("GET", "/api/bs-month"),
        # HEAD on a heavy GET must not bypass the limiter.
        ("HEAD", "/api/report.pdf"), ("HEAD", "/api/panchang-month"),
    ]:
        assert heavy(method, path), (method, path)
    for method, path in [
        ("GET", "/health"), ("HEAD", "/health"),
        ("GET", "/api/places"), ("GET", "/api/panchang"),
        ("GET", "/api/panchang-detail"), ("GET", "/api/horoscope"),
        ("GET", "/api/life-questions"), ("GET", "/api/life-questions/some-id"),
        ("POST", "/api/unknown"),
    ]:
        assert not heavy(method, path), (method, path)


def test_rate_limit_trips_on_month_and_muhurta_endpoints(monkeypatch):
    # The month/muhurta GETs were not rate-limited although they cost
    # ~1-2s each (a full month of panchang, a 31-day muhurta range) —
    # one client could saturate the single free-tier worker exactly as
    # the un-limited kundali endpoints could before the 11-05 fix.
    import main as main_module
    monkeypatch.setenv("VEDIC_RL_LIMIT", "1")
    main_module._RL_BUCKETS.clear()
    assert client.get("/api/muhurta",
                      params={"date_from": "2026-11-01", "date_to": "2026-11-02",
                              "place_id": "kathmandu"}).status_code == 200
    r = client.get("/api/panchang-month",
                   params={"year": 2026, "month": 11, "place_id": "kathmandu"})
    assert r.status_code == 429
    assert r.headers["Retry-After"] == "60"
    main_module._RL_BUCKETS.clear()


def test_rate_limit_trips_on_newly_covered_endpoints(monkeypatch):
    import main as main_module
    monkeypatch.setenv("VEDIC_RL_LIMIT", "1")
    main_module._RL_BUCKETS.clear()
    assert client.post("/api/complete-report", json={**SAMPLE}).status_code == 200
    r = client.post("/api/life-areas", json={**SAMPLE})
    assert r.status_code == 429
    assert r.headers["Retry-After"] == "60"
    # The 429 itself carries the security headers.
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert r.headers["X-Frame-Options"] == "SAMEORIGIN"
    main_module._RL_BUCKETS.clear()


def test_rate_limit_key_is_last_xff_entry_not_first(monkeypatch):
    # Render appends the real client IP as the LAST X-Forwarded-For
    # entry; the first entry is client-controlled. Keying on the first
    # entry let an attacker rotate it per request for a fresh bucket
    # (verified live: 3 requests, limit 2, all 200). Rotating the
    # spoofed prefix while the appended IP stays constant must trip it.
    import main as main_module
    monkeypatch.setenv("VEDIC_RL_LIMIT", "2")
    main_module._RL_BUCKETS.clear()
    payload = {**SAMPLE}
    assert client.post("/api/kundali", json=payload,
                       headers={"X-Forwarded-For": "10.0.0.1, 9.9.9.9"}).status_code == 200
    assert client.post("/api/kundali", json=payload,
                       headers={"X-Forwarded-For": "10.0.0.2, 9.9.9.9"}).status_code == 200
    r = client.post("/api/kundali", json=payload,
                    headers={"X-Forwarded-For": "10.0.0.3, 9.9.9.9"})
    assert r.status_code == 429
    main_module._RL_BUCKETS.clear()


def test_rate_limit_xff_spoof_cannot_frame_victim(monkeypatch):
    # An attacker sending the victim's IP as the (spoofable) first entry
    # must not fill the victim's bucket: Render appends the attacker's
    # real IP last, so the attacker only ever fills their own bucket.
    import main as main_module
    monkeypatch.setenv("VEDIC_RL_LIMIT", "2")
    main_module._RL_BUCKETS.clear()
    payload = {**SAMPLE}
    for _ in range(2):
        assert client.post("/api/kundali", json=payload,
                           headers={"X-Forwarded-For": "8.8.8.8, 1.2.3.4"}).status_code == 200
    assert client.post("/api/kundali", json=payload,
                       headers={"X-Forwarded-For": "8.8.8.8, 1.2.3.4"}).status_code == 429
    # The victim's own request (Render delivers it as a single entry)
    # still answers — it keys on a different bucket.
    assert client.post("/api/kundali", json=payload,
                       headers={"X-Forwarded-For": "8.8.8.8"}).status_code == 200
    main_module._RL_BUCKETS.clear()


def test_oversized_request_body_is_413(monkeypatch):
    # Starlette has no default body-size limit; a 70 KiB body used to be
    # accepted and computed. The cap is 64 KiB, Content-Length and
    # chunked alike, and the 413 carries the security headers.
    import main as main_module
    monkeypatch.setenv("VEDIC_RL_LIMIT", "1000")
    main_module._RL_BUCKETS.clear()
    big = {**SAMPLE, "junk": "x" * (70 * 1024)}
    r = client.post("/api/kundali", json=big)
    assert r.status_code == 413
    assert "64 KiB" in r.json()["detail"]
    assert r.headers["X-Content-Type-Options"] == "nosniff"

    def chunks():
        yield b'{"dob": "1998-05-14", "tob": "06:30", "place_id": "kathmandu", "junk": "'
        yield b"x" * (70 * 1024)
        yield b'"}'
    r = client.post("/api/kundali", content=chunks(),
                    headers={"Content-Type": "application/json"})
    assert r.status_code == 413
    # Just under the cap still computes — and the middleware's cached
    # body reaches the endpoint intact (full bundle, not an empty body).
    ok = {**SAMPLE, "junk": "x" * (60 * 1024)}
    r = client.post("/api/kundali", json=ok)
    assert r.status_code == 200
    assert "lagna" in r.json() and "planets" in r.json()
    main_module._RL_BUCKETS.clear()


def test_ask_astrologer_question_length_capped(monkeypatch):
    # The raw-dict path has no pydantic model, so unlike PrashnaInput's
    # question (max_length=500) this field was unbounded — a 5.6k-char
    # question was accepted live. The cap is 2000 characters.
    import main as main_module
    monkeypatch.setenv("VEDIC_RL_LIMIT", "1000")
    main_module._RL_BUCKETS.clear()
    r = client.post("/api/ask-astrologer",
                    json={"question": "Will I get a job? " * 400, "birth": {**SAMPLE}})
    assert r.status_code == 400
    assert "2000" in r.json()["detail"]
    r = client.post("/api/ask-astrologer",
                    json={"question": "x" * 1999, "birth": {**SAMPLE}})
    assert r.status_code == 200
    main_module._RL_BUCKETS.clear()


def test_oversized_date_and_name_params_rejected():
    r = client.get("/api/bs", params={"date": "2" * 500})
    assert r.status_code == 422
    r = client.get("/api/muhurta", params={"date_from": "2" * 500})
    assert r.status_code == 422
    r = client.get("/api/report.pdf", params={
        "dob": "1998-05-14", "tob": "06:30", "place_id": "kathmandu",
        "name": "n" * 500})
    assert r.status_code == 422
    r = client.post("/api/prashna", json={
        "number": 42, "question": "q", "place_name": "p" * 500,
        "place_id": "kathmandu"})
    assert r.status_code == 422


def _muhurta_params(**over):
    params = {"date_from": "2026-11-15", "date_to": "2026-11-15",
              "place_id": "kathmandu"}
    params.update(over)
    return params


def test_muhurta_unknown_activity_is_400_not_marriage_fallback():
    # The module silently falls back to "marriage" for unknown names while
    # echoing the caller's value — a typo got marriage scores labelled
    # as the typo. The API must reject it instead.
    r = client.get("/api/muhurta", params=_muhurta_params(activity="wedding"))
    assert r.status_code == 400
    assert "wedding" in r.json()["detail"]
    r = client.get("/api/muhurta", params=_muhurta_params(activity="MARRIAGE"))
    assert r.status_code == 400
    r = client.get("/api/muhurta", params=_muhurta_params(activity="travel"))
    assert r.status_code == 200
    assert r.json()["activity"] == "travel"


def test_muhurta_birth_sign_nakshatra_bounds_are_422_not_500():
    # birth_moon_sign=99 used to reach chandrabala's SIGNS_EN[99] and 500;
    # -1 silently wrapped to Pisces via Python negative indexing.
    for bad in (99, 12, -1):
        r = client.get("/api/muhurta", params=_muhurta_params(birth_moon_sign=bad))
        assert r.status_code == 422, bad
    for bad in (99, 27, -1):
        r = client.get("/api/muhurta", params=_muhurta_params(birth_nakshatra=bad))
        assert r.status_code == 422, bad
    # Boundary values still work.
    r = client.get("/api/muhurta", params=_muhurta_params(
        birth_moon_sign=11, birth_nakshatra=26))
    assert r.status_code == 200


def test_out_of_range_dates_are_400_not_500():
    # No .se1 ephemeris files ship with this deployment, so the
    # built-in Moshier data ends around AD 3000; past that, swe
    # raised swisseph.Error, which main.py did not convert — every
    # one of these answered 500 instead of 400.
    r = client.post("/api/kundali", json={**SAMPLE, "dob": "4000-01-01"})
    assert r.status_code == 400, r.text[:120]
    r = client.get("/api/panchang", params={"date": "4000-01-01", "place_id": "kathmandu"})
    assert r.status_code == 400, r.text[:120]
    r = client.get("/api/panchang-detail", params={"date": "4000-01-01", "place_id": "kathmandu"})
    assert r.status_code == 400, r.text[:120]
    r = client.get("/api/horoscope", params={"sign": 0, "date": "4000-01-01"})
    assert r.status_code == 400, r.text[:120]
    # The span arithmetic itself overflowed for Dec 9999 (weekly +6d and
    # monthly +32d both run past datetime.max) before any ephemeris call.
    r = client.get("/api/horoscope", params={"sign": 0, "span": "monthly", "date": "9999-12-15"})
    assert r.status_code == 400, r.text[:120]
    r = client.get("/api/horoscope", params={"sign": 0, "span": "weekly", "date": "9999-12-30"})
    assert r.status_code == 400, r.text[:120]
    r = client.get("/api/muhurta", params=_muhurta_params(date_from="4000-01-01", date_to="4000-01-01"))
    assert r.status_code == 400, r.text[:120]
    for year, month in ((1, 1), (9999, 12), (4000, 6)):
        r = client.get("/api/panchang-month",
                       params={"year": year, "month": month, "place_id": "kathmandu"})
        assert r.status_code == 400, (year, month, r.text[:120])
    # In-range dates still work.
    r = client.get("/api/panchang-month",
                   params={"year": 2026, "month": 11, "place_id": "kathmandu"})
    assert r.status_code == 200


def test_ask_astrologer_prashna_place_is_validated_not_500():
    # The prashna-mode place dict is raw JSON: it skipped the pydantic
    # validators, so an out-of-range lat/lon or unknown tz reached the
    # ephemeris and surfaced as a 500.
    base = {"question": "Will I get the job?", "prashna_number": 42}
    bad_places = [
        {"lat": 999, "lon": 85.3, "tz": "Asia/Kathmandu"},
        {"lat": 27.7, "lon": 999, "tz": "Asia/Kathmandu"},
        {"lat": 27.7, "lon": 85.3, "tz": "Mars/Olympus"},
        {"lat": "abc", "lon": 85.3, "tz": "Asia/Kathmandu"},
        {"lat": True, "lon": 85.3, "tz": "Asia/Kathmandu"},
        {"lat": 27.7, "lon": 85.3, "tz": 42},
    ]
    for place in bad_places:
        r = client.post("/api/ask-astrologer", json={**base, "place": place})
        assert r.status_code == 422, place
    r = client.post("/api/ask-astrologer", json={
        **base, "place": {"lat": 27.7, "lon": 85.3, "tz": "Asia/Kathmandu"}})
    assert r.status_code == 200
    assert r.json()["source"] == "prashna"


# ---------------- main.py error-branch coverage ---------------------------
# (2026-11-17 coverage run: these branches were the bulk of main.py's
# remaining 40 missed lines — endpoint ValueError->400 conversions,
# validator rejections, and the rate-limiter's bucket shed.)

def test_rl_is_heavy_rejects_other_methods():
    import main as main_module

    assert main_module._rl_is_heavy("PUT", "/api/kundali") is False
    assert main_module._rl_is_heavy("DELETE", "/api/kundali") is False
    assert main_module._rl_is_heavy("HEAD", "/api/kundali") is True


def test_rl_limit_invalid_env_falls_back_to_60(monkeypatch):
    import main as main_module

    monkeypatch.setenv("VEDIC_RL_LIMIT", "not-a-number")
    assert main_module._rl_limit() == 60
    monkeypatch.setenv("VEDIC_RL_LIMIT", "0")
    assert main_module._rl_limit() == 1  # max(1, ...) floor


def test_rl_bucket_shed_caps_map():
    # Fill past the 8192-bucket cap with stale (empty) buckets; one more
    # allowed request must shed the 4096 stalest instead of growing forever.
    import main as main_module
    from collections import deque

    saved = dict(main_module._RL_BUCKETS)
    try:
        main_module._RL_BUCKETS.clear()
        for i in range(8193):
            main_module._RL_BUCKETS[f"key-{i}"] = deque()
        assert main_module._rl_allowed("fresh-key") is True
        assert len(main_module._RL_BUCKETS) == 8193 - 4096 + 1
        assert "fresh-key" in main_module._RL_BUCKETS
    finally:
        main_module._RL_BUCKETS.clear()
        main_module._RL_BUCKETS.update(saved)


def test_prashna_input_field_validators_are_422():
    base = {"number": 42, "question": "Will I get the job?",
            "lat": 27.7, "lon": 85.3, "tz": "Asia/Kathmandu"}
    for bad in ({"lat": 91}, {"lat": -91}, {"lon": 200}, {"lon": -181},
                {"tz": "Bad/Zone"}):
        r = client.post("/api/prashna", json={**base, **bad})
        assert r.status_code == 422, bad


def test_prashna_unknown_place_is_400_not_500():
    r = client.post("/api/prashna", json={
        "number": 42, "question": "Will I get the job?",
        "place_id": "no-such-place"})
    assert r.status_code == 400


def test_complete_report_out_of_range_date_is_400(monkeypatch):
    monkeypatch.setenv("VEDIC_RL_LIMIT", "1000")
    r = client.post("/api/complete-report",
                    json={**SAMPLE, "dob": "4000-01-01"})
    assert r.status_code == 400


def test_match_out_of_range_date_is_400(monkeypatch):
    monkeypatch.setenv("VEDIC_RL_LIMIT", "1000")
    r = client.post("/api/match", json={
        "groom": {**SAMPLE, "dob": "4000-01-01"}, "bride": SAMPLE})
    assert r.status_code == 400


def test_ask_astrologer_birth_value_error_is_400(monkeypatch):
    monkeypatch.setenv("VEDIC_RL_LIMIT", "1000")
    r = client.post("/api/ask-astrologer", json={
        "question": "Will I get a promotion?",
        "birth": {**SAMPLE, "dob": "4000-01-01"}})
    assert r.status_code == 400


def test_places_skips_global_hit_near_a_local_entry(monkeypatch):
    from astro import geocode

    geocode._cache.clear()
    monkeypatch.setattr(geocode, "_fetch_open_meteo", lambda q: {"results": [{
        "name": "Kathmandu City", "latitude": 27.72, "longitude": 85.32,
        "country": "Nepal", "timezone": "Asia/Kathmandu"}]})
    r = client.get("/api/places", params={"q": "kathmandu"})
    names = [p["name"] for p in r.json()["places"]]
    assert "Kathmandu City" not in names
    assert names.count("Kathmandu") == 1


def test_tz_lookup_no_timezone_is_422(monkeypatch):
    from astro import geocode

    # timezonefinder answers an Etc/GMT zone for every ocean point, so the
    # None branch is pinned by stubbing the lookup rather than by coords.
    monkeypatch.setattr(geocode, "timezone_at", lambda lat, lon: None)
    r = client.get("/api/tz", params={"lat": 0, "lon": -160})
    assert r.status_code == 422


def test_bs_convert_bad_inputs_are_400():
    assert client.get("/api/bs", params={"bs": "2083-13-40"}).status_code == 400
    assert client.get("/api/bs", params={"bs": "not-a-date"}).status_code == 400
    assert client.get("/api/bs", params={"date": "garbage"}).status_code == 400


def test_bs_convert_ad_to_bs_success():
    r = client.get("/api/bs", params={"date": "2026-11-04"})
    assert r.status_code == 200
    assert r.json()["iso"] == "2083-07-18"


def test_non_dict_body_rejected_direct_call():
    # FastAPI validates `body: dict` before the handler runs, so a JSON
    # array reaches the endpoint as a 422 — these guards are only reachable
    # by calling the handler directly. Pinned here so the defensive
    # branches stay covered if the signature ever loosens.
    import main as main_module
    from fastapi import HTTPException

    for fn, args in ((main_module.ask_astrologer, ([1, 2],)),
                     (main_module.life_question_answer,
                      ("marriage_timing", [1, 2]))):
        try:
            fn(*args)
        except HTTPException as e:
            assert e.status_code == 400
        else:
            raise AssertionError(f"{fn.__name__} accepted a non-dict body")


def test_horoscope_bad_date_is_400():
    r = client.get("/api/horoscope", params={"sign": 3, "date": "garbage"})
    assert r.status_code == 400


def test_muhurta_defaults_birth_moon_sign_from_natal_chart(monkeypatch):
    monkeypatch.setenv("VEDIC_RL_LIMIT", "1000")
    r = client.get("/api/muhurta", params={
        "date_from": "2026-11-20", "date_to": "2026-11-21",
        "activity": "marriage", "place_id": "kathmandu",
        "birth_dob": "1998-05-14", "birth_tob": "06:30",
        "birth_place_id": "kathmandu"})
    assert r.status_code == 200


def test_report_pdf_out_of_range_date_is_400(monkeypatch):
    monkeypatch.setenv("VEDIC_RL_LIMIT", "1000")
    r = client.get("/api/report.pdf", params={
        "dob": "4000-01-01", "tob": "06:30", "place_id": "kathmandu"})
    assert r.status_code == 400


def test_kundali_birth_over_120_years_ago_returns_200(monkeypatch):
    # A birth in 1900 is 126 years before today: the old single-cycle
    # Vimshottari tree ended ~2020, `current` was None and the chart
    # 500'd. The 120-year sequence repeats, so the tree now spans two
    # cycles and the current dasha resolves.
    import datetime as _dt

    monkeypatch.setenv("VEDIC_RL_LIMIT", "1000")
    r = client.post("/api/kundali", json={**SAMPLE, "dob": "1900-01-01"})
    assert r.status_code == 200
    dasha = r.json()["dasha"]
    assert len(dasha["mahadashas"]) == 18
    cur = dasha["current"]
    assert cur is not None
    today = _dt.date.today().isoformat()
    assert cur["mahadasha"]["start"] <= today < cur["mahadasha"]["end"]


def test_kundali_year1_birth_is_400_not_500(monkeypatch):
    # The dasha tree's first period starts before year 1: a
    # supported-range 400, not an OverflowError 500. (The muhurta
    # birth path and the PDFs raise the same way; the engine-level
    # cases are pinned in test_worldclass2.)
    monkeypatch.setenv("VEDIC_RL_LIMIT", "1000")
    r = client.post("/api/kundali", json={**SAMPLE, "dob": "0001-01-01"})
    assert r.status_code == 400
    assert "outside the supported range" in r.json()["detail"]


def test_prashna_number_bool_is_422():
    # `{"number": true}` coerced to horary number 1; a JSON boolean
    # must never silently become a chart number. Model-level: the
    # endpoint is rate-limited, so pin the validation without HTTP.
    from pydantic import ValidationError

    from main import PrashnaInput

    with pytest.raises(ValidationError):
        PrashnaInput(number=True, place_id="kathmandu")
    assert PrashnaInput(number=5, place_id="kathmandu").number == 5


def test_kundali_bool_coords_are_422():
    # Same bool-coercion hole on the chart path: `{"lat": true}`
    # silently became latitude 1.0. The ask-astrologer raw-dict path
    # already rejects bools; the pydantic models must agree.
    # Model-level: the endpoint is rate-limited, so pin the
    # validation without HTTP.
    from pydantic import ValidationError

    from main import BirthInput

    for bad in ({"lat": True}, {"lon": True}):
        with pytest.raises(ValidationError):
            BirthInput(**{**SAMPLE, "place_id": None, "lat": 27.7,
                          "lon": 85.3, "tz": "Asia/Kathmandu", **bad})
    assert BirthInput(**SAMPLE).lat is None


def test_complete_report_pdf_out_of_range_date_is_400(monkeypatch):
    monkeypatch.setenv("VEDIC_RL_LIMIT", "1000")
    r = client.get("/api/complete-report.pdf", params={
        "dob": "4000-01-01", "tob": "06:30", "place_id": "kathmandu"})
    assert r.status_code == 400


def test_complete_report_pdf_render_failure_is_500(monkeypatch):
    from astro import complete_pdf

    monkeypatch.setenv("VEDIC_RL_LIMIT", "1000")
    monkeypatch.setattr(
        complete_pdf, "render_complete_pdf",
        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("no fonts")))
    r = client.get("/api/complete-report.pdf", params={
        "dob": "1998-05-14", "tob": "06:30", "place_id": "kathmandu"})
    assert r.status_code == 500


def test_index_and_service_worker_serve():
    r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    r = client.get("/sw.js")
    assert r.status_code == 200
    assert "javascript" in r.headers["content-type"]
