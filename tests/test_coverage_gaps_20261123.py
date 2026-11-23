"""Coverage-gap tests for the 2026-11-17 gaps (engine/report/muhurta).

Pins reachable branches that the suite had never exercised, each verified
against an independently computed fact (not just the code's own output).
"""
from datetime import date, datetime, time

import pytest
from zoneinfo import ZoneInfo

from astro import dasha as dasha_module
from astro import ephemeris
from astro import muhurta as muhurta_module
from astro import report as report_module
from astro.engine import compute_kundali, compute_match

KTM = ZoneInfo("Asia/Kathmandu")
LAT, LON = 27.7172, 85.3240


def _birth(dob, tob="06:30"):
    y, m, d = map(int, dob.split("-"))
    hh, mm = map(int, tob.split(":"))
    return ephemeris.make_local_datetime(date(y, m, d), time(hh, mm), "Asia/Kathmandu")


def _planets_lagna(dob):
    dt = _birth(dob)
    jd = ephemeris.to_julian_day(dt)
    planets = ephemeris.planet_longitudes(jd)
    lagna = int(ephemeris.ascendant(jd, LAT, LON, b"W") // 30)
    return dt, planets, lagna


# ---------------------------------------------------------------- report.py
def test_remedies_include_manglik_when_present_and_not_cancelled():
    bundle = compute_kundali(
        {"dob": "2010-10-10", "tob": "06:30", "place_id": "kathmandu"})
    assert bundle["doshas"]["manglik"]["present"] is True
    assert bundle["doshas"]["manglik"]["strength"] == "strong"
    names = [r["dosha"]["en"] for r in bundle["report"]["remedies"]["dosha_remedies"]]
    assert "Manglik Dosha" in names


def test_varshphal_feb29_birth_uses_feb28_in_non_leap_year():
    bundle = compute_kundali(
        {"dob": "2000-02-29", "tob": "06:30", "place_id": "kathmandu"},
        now=datetime(2027, 6, 1, tzinfo=KTM))
    years = {v["year"]: v for v in bundle["varshphal_extended"]}
    v27 = years[2027]
    assert v27["age"] == 27
    ret = datetime.fromisoformat(v27["solar_return"])
    # Non-leap year: the Feb-29 guess falls back to Feb 28, and the
    # refined solar return lands within ~a day of it — never a crash.
    assert abs((ret.date() - date(2027, 2, 28)).days) <= 2
    assert years[2028]["age"] == 28  # leap year: the real Feb 29 path


def test_year_ahead_flags_mahadasha_start_within_12_months():
    birth_dt, planets, _lagna = _planets_lagna("1998-05-14")
    now = datetime(2028, 7, 1, tzinfo=KTM)
    tree = dasha_module.vimshottari_tree(
        birth_dt, planets["Moon"]["longitude"], now)
    ctx = {"planets": planets, "now": now,
           "transit_ingress": [], "dasha_tree": tree}
    facts = report_module.year_ahead(ctx)
    md_facts = [f["en"] for f in facts if "Mahadasha" in f["en"]]
    # Sun Mahadasha starts 2029-06-20, inside the 12-month horizon.
    assert any("2029-06-20" in f and "Sun" in f for f in md_facts)


# ---------------------------------------------------------------- muhurta.py
def test_lagna_strength_strong_verdict():
    ls = muhurta_module.lagna_strength_at(
        datetime(2026, 11, 23, 6, 0, tzinfo=KTM), LAT, LON, "Asia/Kathmandu")
    assert ls["verdict"] == "strong" and ls["points"] == 2
    assert ls["lagna_sign_en"] == "Libra"
    assert ls["lagna_lord"] == "Venus" and ls["lagna_lord_dignity"] == "own"
    assert ls["malefics_in_lagna"] == []


def test_day_muhurta_amavasya_tithi_not_on_grahapravesh_list():
    # 2026-01-18 is Amavasya (tithi 30) at a Kathmandu sunrise; Grahapravesh
    # allows tithis 1-29 only.
    day = muhurta_module.day_muhurta(
        date(2026, 1, 18), LAT, LON, "Asia/Kathmandu", activity="grahapravesh")
    assert day["panchang"]["tithi_index"] == 29
    bad = [f for f in day["factors"] if f["points"] == -2 and "Tithi 30" in f["en"]]
    assert bad, day["factors"]


def test_day_muhurta_tara_bala_unfavourable():
    # 2026-01-18 sunrise nakshatra is Mula (19); birth nakshatra 17 gives
    # Tara (19-17)%9+1 = 3 (Vipat) — unfavourable.
    day = muhurta_module.day_muhurta(
        date(2026, 1, 18), LAT, LON, "Asia/Kathmandu",
        activity="marriage", birth_nakshatra=17)
    assert day["tara"] == 3
    bad = [f for f in day["factors"] if "Tara Bala 3" in f["en"]]
    assert bad and bad[0]["points"] == -2


def test_dasha_suitability_branches():
    birth_dt, planets, lagna = _planets_lagna("1998-05-14")
    tree = dasha_module.vimshottari_tree(
        birth_dt, planets["Moon"]["longitude"], datetime.now(KTM))
    # Ketu MD (2002-2009): Ketu sits in the 10th, neutral dignity, not a
    # benefic and not the Lagna lord -> neutral.
    neutral = muhurta_module.dasha_suitability(
        tree, datetime(2005, 1, 1, 12, 0, tzinfo=KTM), planets, lagna)
    assert neutral["mahadasha_lord"] == "Ketu"
    assert neutral["verdict"] == "neutral" and neutral["points"] == 0
    # Saturn MD (2086-2105): Saturn is debilitated in the 12th -> unfavourable.
    bad = muhurta_module.dasha_suitability(
        tree, datetime(2090, 1, 1, 12, 0, tzinfo=KTM), planets, lagna)
    assert bad["mahadasha_lord"] == "Saturn"
    assert bad["verdict"] == "unfavourable" and bad["points"] == -1
    assert bad["lord_dignity"] == "debilitated" and bad["lord_house_from_lagna"] == 12
    # Outside the tree entirely (year 2300): no running dasha -> None.
    assert muhurta_module.dasha_suitability(
        tree, datetime(2300, 1, 1, 12, 0, tzinfo=KTM), planets, lagna) is None


# ---------------------------------------------------------------- engine.py
def test_phase5_failure_degrades_to_none_not_500(monkeypatch):
    from astro import phase5 as phase5_module

    def _boom(*_a, **_k):
        raise RuntimeError("phase5 boom")

    for name in ("dasha_consensus", "yoga_fructification",
                 "ashtakavarga_gochar", "arudha_padas"):
        monkeypatch.setattr(phase5_module, name, _boom)
    bundle = compute_kundali(
        {"dob": "1998-05-14", "tob": "06:30", "place_id": "kathmandu"})
    assert bundle["dasha_consensus"] is None
    assert bundle["yoga_fructification"] is None
    assert bundle["ashtakavarga_gochar"] is None
    assert bundle["arudha_padas"] is None
    # The rest of the bundle still builds.
    assert bundle["lagna"]["sign_en"] and len(bundle["planets"]) == 9


def _match_payload(dob):
    return {"dob": dob, "tob": "06:30", "place_id": "kathmandu"}


def test_match_neither_manglik_note():
    r = compute_match(_match_payload("1999-01-05"), _match_payload("1992-06-06"))
    assert r["groom"]["manglik"]["present"] is False
    assert r["bride"]["manglik"]["present"] is False
    assert r["manglik_note"]["en"] == "Neither partner is Manglik."


def test_match_papasamya_uneven_flag():
    r = compute_match(_match_payload("2000-02-29"), _match_payload("2001-11-11"))
    assert r["papasamya"]["verdict"] == "Uneven"
    assert r["papasamya"]["difference"] == 4
    assert "Papasamya is uneven" in r["combined_verdict"]["en"]


def test_match_modest_combined_verdict():
    r = compute_match(_match_payload("1998-05-14"), _match_payload("1995-07-20"))
    assert r["total"] < 18
    assert r["papasamya"]["verdict"] == "Balanced"
    assert r["bhava_milan"]["verdict"] == "Mixed"
    assert r["combined_verdict"]["en"].startswith("Modest match")
