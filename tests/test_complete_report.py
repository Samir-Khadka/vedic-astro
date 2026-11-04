"""Tests for the Complete Kundali Report (legacy table-of-contents order)."""

from fastapi.testclient import TestClient

from astro import complete_report as cr
from astro import engine

SAMPLE = {"name": "Test", "dob": "1990-05-15", "tob": "08:30", "place_id": "kathmandu"}

EXPECTED_ORDER = [
    "title", "planet_position", "birth_details", "sayan_charts",
    "moon_navamsa", "chalit_bhava", "shodash_varga", "shodash_varga_table",
    "karaka_avastha_tara", "sudarshan", "aspects_planets", "aspects_bhava",
    "aspects_cusps", "upagrahas_arudha", "vimsopak_bala", "ashtakavarga",
    "shad_bhava_bala", "sarvato_bhadra", "vimshottari", "yogini",
    "aaditya_lagnam", "dasha_phala", "varshphal", "general_predictions",
    "effects_of_planets", "nakshatra_phal", "sade_sati", "manglik",
    "kaalsarp", "ratna_mantra", "yantra",
]


def _bundle():
    return engine.compute_kundali(SAMPLE)


def test_section_order_matches_legacy_order():
    report = cr.build_complete_report(_bundle())
    assert report["section_ids"] == EXPECTED_ORDER


def test_every_section_present_for_sample_birth():
    report = cr.build_complete_report(_bundle())
    by_id = {s["id"]: s for s in report["sections"]}
    for sid in EXPECTED_ORDER:
        assert sid in by_id, f"missing section {sid}"
        assert by_id[sid]["title_en"] and by_id[sid]["title_ne"]


def test_title_carries_birth_and_disclaimer():
    report = cr.build_complete_report(_bundle())
    title = report["sections"][0]["data"]
    assert title["birth"]["date"] == "1990-05-15"
    assert title["birth"]["bs_date"]  # Bikram Sambat date present
    assert title["birth"]["sunrise"] and title["birth"]["sunset"]
    assert "probability" in title["disclaimer"]["en"].lower()


def test_planet_position_and_sayan_match_bundle():
    bundle = _bundle()
    report = cr.build_complete_report(bundle)
    by_id = {s["id"]: s for s in report["sections"]}
    assert len(by_id["planet_position"]["data"]["planets"]) == 9
    sayan = by_id["sayan_charts"]["data"]
    assert sayan["positions"] is not None
    # Sayana Sun = sidereal Sun + ayanamsa (mod 360).
    sun_sid = next(p for p in bundle["planets"] if p["planet"] == "Sun")
    sun_say = next(p for p in sayan["positions"] if p["planet"] == "Sun")
    assert abs(((sun_sid["longitude"] + bundle["ayanamsa_value"]) % 360)
               - sun_say["longitude"]) < 0.01


def test_shodash_varga_covers_16_charts():
    report = cr.build_complete_report(_bundle())
    by_id = {s["id"]: s for s in report["sections"]}
    table = by_id["shodash_varga_table"]["data"]
    assert len(table["vargas"]) == 16
    assert len(table["rows"]) == 9
    assert table["rows"][0]["signs"]["D1"] is not None
    assert table["rows"][0]["signs"]["D9"] is not None


def test_aspects_computed_from_bundle():
    report = cr.build_complete_report(_bundle())
    by_id = {s["id"]: s for s in report["sections"]}
    aspects = by_id["aspects_planets"]["data"]["aspects"]
    assert len(aspects) == 9
    mars = next(a for a in aspects if a["planet"] == "Mars")
    assert len(mars["aspected_houses"]) == 3  # 4th, 7th, 8th
    assert len(by_id["aspects_bhava"]["data"]["houses"]) == 12
    assert len(by_id["aspects_cusps"]["data"]["cusps"]) == 12


def test_vimshottari_has_all_levels_and_current():
    report = cr.build_complete_report(_bundle())
    by_id = {s["id"]: s for s in report["sections"]}
    vim = by_id["vimshottari"]["data"]
    assert vim["current"]["mahadasha"]["lord"]
    assert vim["current"]["antardasha"]["lord"]
    first_md = vim["mahadashas"][0]
    assert first_md["antardashas"]
    # Pratyantar subdivisions exist on full antardashas (the balance
    # antardasha at birth is truncated and carries none).
    assert any("pratyantardashas" in ad for md in vim["mahadashas"]
               for ad in md["antardashas"])
    assert vim["current"]["pratyantardasha"]["lord"]
    assert vim["current"]["sookshma"]["lord"]


def test_yogini_and_dasha_phala_present():
    report = cr.build_complete_report(_bundle())
    by_id = {s["id"]: s for s in report["sections"]}
    assert by_id["yogini"]["data"]["yogini"]["current"] is not None
    assert len(by_id["dasha_phala"]["data"]["dasha_phala"]) == 9


def test_varshphal_covers_at_least_10_years_with_positions():
    report = cr.build_complete_report(_bundle())
    by_id = {s["id"]: s for s in report["sections"]}
    years = by_id["varshphal"]["data"]["years"]
    assert len(years) >= 10
    assert years[0]["planets"]  # annual-chart positions present
    assert years[0]["chart"]["Lagna"] is not None
    assert years[0]["reading"]


def test_ratna_mantra_and_yantra_cover_all_planets():
    report = cr.build_complete_report(_bundle())
    by_id = {s["id"]: s for s in report["sections"]}
    ratna = by_id["ratna_mantra"]["data"]["per_planet"]
    assert [r["planet"] for r in ratna] == [
        "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    for r in ratna:
        assert r["gemstone"] and r["beej_mantra"]["ne"] and r["jaap_count"] > 0
        assert r["how_to_wear"]["en"]
    yantra = by_id["yantra"]["data"]["per_planet"]
    assert len(yantra) == 9
    assert all(y["yantra_en"] and y["number"] for y in yantra)


def test_unavailable_sections_flagged_not_fabricated():
    report = cr.build_complete_report(_bundle())
    by_id = {s["id"]: s for s in report["sections"]}
    aad = by_id["aaditya_lagnam"]
    assert aad["available"] is False
    assert aad["data"]["aaditya"] is None


def test_no_crash_on_minimal_bundle():
    # A bundle missing every optional key must still assemble all sections.
    report = cr.build_complete_report({})
    assert report["section_ids"] == EXPECTED_ORDER
    by_id = {s["id"]: s for s in report["sections"]}
    assert by_id["sayan_charts"]["available"] is False
    assert by_id["varshphal"]["data"]["years"] == []


def test_api_endpoint_returns_ordered_report():
    from main import app

    client = TestClient(app)
    resp = client.post("/api/complete-report", json=SAMPLE)
    assert resp.status_code == 200
    data = resp.json()
    assert data["section_ids"] == EXPECTED_ORDER
    assert len(data["sections"]) == len(EXPECTED_ORDER)
    resp_bad = client.post("/api/complete-report", json={"dob": "1990-05-15"})
    assert resp_bad.status_code in (400, 422)
