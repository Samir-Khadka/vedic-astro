"""Day-detail endpoint tests: GET /api/panchang-detail.

Values are asserted against our own engine (daily_panchang, ephemeris),
never against any printed patro: the reference MD the user supplied is a
design reference only, and its Surya-Siddhanta times legitimately differ
from Swiss-Ephemeris/Lahiri times by up to a couple of hours.
"""
import re

import swisseph as swe
from fastapi.testclient import TestClient

from astro import ayanamsa as ayanamsa_module
from astro.ephemeris import planet_longitudes, sun_moon_longitudes, to_julian_day
from astro.panchang import day_detail, panchang_at, ritu_ayana
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

import main as main_module

client = TestClient(main_module.app)
PLACE = {"place_id": "kathmandu"}
DAY = date(2026, 11, 4)
LAT, LON, TZ = 27.7172, 85.3240, "Asia/Kathmandu"


def _detail():
    r = client.get("/api/panchang-detail", params={"date": "2026-11-04", **PLACE})
    assert r.status_code == 200, r.text
    return r.json()


def test_detail_has_all_fields_and_agrees_with_daily():
    d = _detail()
    for key in ("date", "weekday", "bs", "sunrise", "sunset", "moonrise",
                "moonset", "paksha", "tithi_index", "tithi_transitions",
                "nakshatra_index", "nakshatra_transitions", "yoga_index",
                "yoga_transitions", "karana", "karana_transitions",
                "moon_sign", "sun_sign", "ritu_en", "ritu_ne",
                "ayana_en", "ayana_ne", "planets", "place"):
        assert key in d, key
    # Base values agree with the sunrise evaluation used by /api/panchang.
    r = client.get("/api/panchang", params={"date": "2026-11-04", **PLACE})
    assert r.status_code == 200
    p = r.json()
    assert d["sunrise"] == p["sunrise"] and d["sunset"] == p["sunset"]
    assert d["tithi_index"] == p["tithi_index"]
    assert d["nakshatra_index"] == p["nakshatra_index"]
    assert d["yoga_index"] == p["yoga_index"]
    assert d["karana"] == p["karana"]
    assert d["paksha"] == p["paksha"]
    assert d["bs"]["year"] == 2083 and d["bs"]["month"] == 7 and d["bs"]["day"] == 18


def test_transitions_are_ordered_and_real():
    d = _detail()
    rise = datetime.fromisoformat(d["sunrise"])
    for key, to_key in (("tithi_transitions", "to_index"),
                        ("nakshatra_transitions", "to_index"),
                        ("yoga_transitions", "to_index"),
                        ("karana_transitions", "to_name")):
        times = [datetime.fromisoformat(t["at"]) for t in d[key]]
        assert times == sorted(times), key
        assert all(t > rise for t in times), key
        assert all(to_key in t for t in d[key]), key
        assert len(times) <= 4, key
    # Tithi transition advances the index by exactly one (mod 30).
    for t in d["tithi_transitions"]:
        assert t["to_index"] == (d["tithi_index"] + 1) % 30
    # Karana transitions advance through real karana names.
    assert d["karana_transitions"], "karana changes twice a day; expect some"
    assert all(isinstance(t["to_name"], str) and t["to_name"] for t in d["karana_transitions"])


def test_moonrise_moonset_inside_civil_day():
    d = _detail()
    for key in ("moonrise", "moonset"):
        assert d[key] is not None, key
        dt = datetime.fromisoformat(d[key])
        assert dt.date() == DAY, (key, dt)
    assert d["moonrise"] < d["moonset"]


def test_planets_sidereal_and_in_range():
    d = _detail()
    names = [p["name"] for p in d["planets"]]
    assert names == ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus",
                     "Saturn", "Rahu", "Ketu"]
    for p in d["planets"]:
        assert 0 <= p["longitude"] < 360
        assert 0 <= p["sign"] <= 11
        assert 0 <= p["degree"] < 30 and 0 <= p["minute"] < 60 and 0 <= p["second"] < 60
        assert re.fullmatch(r"\d+:\d+:\d+:\d+", p["dms"])
        assert p["dms"].split(":")[0] == str(p["sign"])
    # Sidereal check, independent of the app's own sidereal path: tropical
    # Sun minus the Lahiri ayanamsa must equal the reported sidereal Sun.
    ayanamsa_module.ensure_ayanamsa()
    rise = datetime.fromisoformat(d["sunrise"])
    jd = to_julian_day(rise)
    trop, _ = swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH)
    ay = swe.get_ayanamsa_ut(jd)
    sun = next(p for p in d["planets"] if p["name"] == "Sun")
    assert abs(((trop[0] - ay) % 360) - sun["longitude"]) < 0.01


def test_planets_match_engine_at_sunrise():
    d = _detail()
    rise = datetime.fromisoformat(d["sunrise"])
    eng = planet_longitudes(to_julian_day(rise))
    for p in d["planets"]:
        assert abs(eng[p["name"]]["longitude"] - p["longitude"]) < 1e-9
        assert eng[p["name"]]["sign"] == p["sign"]


def test_ritu_ayana_rules():
    # Rule checks on sign indices, not dates: Tula (6) -> Sharad/Dakshinayana.
    assert ritu_ayana(6) == {"ritu_en": "Sharad", "ritu_ne": "शरद्",
                             "ayana_en": "Dakshinayana", "ayana_ne": "दक्षिणायण"}
    assert ritu_ayana(9)["ayana_en"] == "Uttarayana"   # Makara
    assert ritu_ayana(0)["ritu_en"] == "Vasant"        # Mesha
    assert ritu_ayana(11)["ritu_en"] == "Vasant"       # Meena
    assert ritu_ayana(3)["ritu_en"] == "Varsha"        # Karka
    d = _detail()
    assert d["ritu_en"] == ritu_ayana(d["sun_sign"])["ritu_en"]
    assert d["ayana_en"] == ritu_ayana(d["sun_sign"])["ayana_en"]


def test_detail_400_on_bad_date():
    r = client.get("/api/panchang-detail", params={"date": "not-a-date", **PLACE})
    assert r.status_code == 400
    r = client.get("/api/panchang-detail", params={"date": "2026-13-40", **PLACE})
    assert r.status_code == 400


def test_detail_outside_bs_range_still_works():
    # AD dates outside the BS table (before 1943) get bs=None, not an error.
    r = client.get("/api/panchang-detail", params={"date": "1900-01-01", **PLACE})
    assert r.status_code == 200
    assert r.json()["bs"] is None
    assert r.json()["sunrise"] is not None
