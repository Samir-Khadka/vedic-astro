"""Phase 1 Muhurta extension: new ceremonies, facing, EN+NE."""
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from astro import muhurta as muhurta_module
from astro.ephemeris import sunrise_sunset
from astro.panchang import panchang_at
from main import app

KTM = {"lat": 27.7172, "lon": 85.3240, "tz_name": "Asia/Kathmandu"}
client = TestClient(app)

NEW_ACTIVITIES = [
    "grahapravesh", "shop_opening", "bride_entry",
    "partner_selection", "vehicle_ceremony", "planting", "first_ploughing",
]


def test_new_activities_bilingual_and_valid():
    for key in NEW_ACTIVITIES:
        act = muhurta_module.ACTIVITIES[key]
        assert act["en"] and act["ne"], key
        assert all(0 <= n <= 26 for n in act["good_nakshatras"]), key
        for wd in act.get("allowed_weekdays", []):
            assert 0 <= wd <= 6
        for ti in act.get("allowed_tithis", []):
            assert 1 <= ti <= 30


def test_grahapravesh_facing_lists_partition_general():
    act = muhurta_module.ACTIVITIES["grahapravesh"]
    parts = []
    for facing in ("east", "west", "south", "north"):
        parts.extend(act["facing_nakshatras"][facing])
    assert sorted(parts) == sorted(act["good_nakshatras"])
    assert muhurta_module.effective_nakshatras("grahapravesh", "east") == [3, 4]
    assert muhurta_module.effective_nakshatras("grahapravesh", "any") == act["good_nakshatras"]


def test_invalid_facing_rejected():
    with pytest.raises(ValueError):
        muhurta_module.day_muhurta(date(2026, 10, 26), **KTM, activity="grahapravesh", facing="up")
    r = client.get("/api/muhurta", params={
        "date_from": "2026-10-26", "date_to": "2026-10-28",
        "activity": "grahapravesh", "facing": "up", "place_id": "kathmandu"})
    assert r.status_code == 400


def _find_day_with_nakshatra(target_nak):
    from zoneinfo import ZoneInfo
    from datetime import datetime, time
    d = date(2026, 10, 26)
    for _ in range(60):
        rise, _set = sunrise_sunset(d, KTM["lat"], KTM["lon"], KTM["tz_name"])
        moment = rise or datetime.combine(d, time(6, 0), tzinfo=ZoneInfo(KTM["tz_name"]))
        if panchang_at(moment, KTM["lat"], KTM["lon"], KTM["tz_name"])["nakshatra_index"] == target_nak:
            return d
        d += timedelta(days=1)
    raise AssertionError(f"no day with nakshatra {target_nak} in scan")


def test_grahapravesh_facing_changes_nakshatra_factor():
    # Rohini (index 3) is East-facing only in the legacy split.
    d = _find_day_with_nakshatra(3)
    east = muhurta_module.day_muhurta(d, **KTM, activity="grahapravesh", facing="east")
    west = muhurta_module.day_muhurta(d, **KTM, activity="grahapravesh", facing="west")
    assert east["facing"] == "east" and west["facing"] == "west"
    assert any("Rohini" in f["en"] or "रोहिणी" in f["ne"] for f in east["factors"])
    # East gets the +2 nakshatra factor; West does not.
    assert any(f["points"] == 2 and "Moon in" in f["en"] for f in east["factors"])
    assert not any(f["points"] == 2 and "Moon in" in f["en"] for f in west["factors"])


def test_new_activity_factors_are_bilingual():
    d = muhurta_module.day_muhurta(date(2026, 10, 26), **KTM, activity="shop_opening")
    assert d["activity"] == "shop_opening"
    for f in d["factors"]:
        assert f["en"] and f["ne"]
    # Grahapravesh now scores the lunar month (Phase 3 A1): Oct 26 2026
    # is in Ashwin, which is not on the preferred list, so -2.
    g = muhurta_module.day_muhurta(date(2026, 10, 26), **KTM, activity="grahapravesh")
    assert any("Lunar month" in f["en"] and f["points"] == -2 for f in g["factors"])


def test_muhurta_extension_endpoint():
    r = client.get("/api/muhurta", params={
        "date_from": "2026-10-26", "date_to": "2026-11-01",
        "activity": "grahapravesh", "facing": "east", "place_id": "kathmandu"})
    assert r.status_code == 200
    body = r.json()
    assert body["activity"] == "grahapravesh" and body["facing"] == "east"
    assert len(body["days"]) == 7
    r2 = client.get("/api/muhurta", params={
        "date_from": "2026-10-26", "date_to": "2026-10-28",
        "activity": "shop_opening", "place_id": "kathmandu"})
    assert r2.status_code == 200 and r2.json()["activity"] == "shop_opening"
