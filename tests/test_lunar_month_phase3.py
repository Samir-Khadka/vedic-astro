"""Phase 3 A1: Amanta lunar month + Grahapravesh scoring on it."""
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from astro.muhurta import day_muhurta
from astro.panchang import LUNAR_MONTHS_EN, lunar_month_at

TZ = "Asia/Kathmandu"
LAT, LON = 27.7172, 85.324


def _month_on(day):
    m = datetime.combine(day, datetime.min.time()).replace(tzinfo=ZoneInfo(TZ))
    return lunar_month_at(m, LAT, LON, TZ)


def test_month_names_in_order():
    # 2026: months step by exactly one at each Amavasya boundary.
    prev, bad = None, []
    d = date(2026, 1, 1)
    while d <= date(2026, 12, 31):
        idx = _month_on(d)["lunar_month_index"]
        assert 1 <= idx <= 12
        if prev is not None and idx != prev and idx != (prev % 12) + 1:
            bad.append((d, prev, idx))
        prev = idx
        d += timedelta(days=1)
    assert not bad


def test_known_months_2026():
    assert _month_on(date(2026, 5, 17))["lunar_month_en"] == "Vaishakha"
    assert _month_on(date(2026, 6, 15))["lunar_month_en"] == "Jyeshtha"
    assert _month_on(date(2026, 8, 15))["lunar_month_en"] == "Shravana"
    assert _month_on(date(2026, 2, 15))["lunar_month_en"] == "Pausha"
    assert LUNAR_MONTHS_EN[10] == "Magha" and LUNAR_MONTHS_EN[11] == "Phalguna"


def test_grahapravesh_lunar_month_scored():
    # Vaishakha (allowed) vs Shravana (not allowed), same activity.
    for day, want in [(date(2026, 5, 20), 2), (date(2026, 8, 20), -2)]:
        res = day_muhurta(day, LAT, LON, TZ, activity="grahapravesh")
        lunar = [f for f in res["factors"] if "Lunar month" in f["en"]]
        assert len(lunar) == 1, res["factors"]
        assert lunar[0]["points"] == want
        assert "चान्द्रमास" in lunar[0]["ne"]


def test_other_activities_unaffected():
    res = day_muhurta(date(2026, 5, 20), LAT, LON, TZ, activity="marriage")
    assert not [f for f in res["factors"] if "Lunar month" in f["en"]]
