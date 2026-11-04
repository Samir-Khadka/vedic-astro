"""BS month calendar endpoint: /api/bs-month and /api/bs-month-length."""
from datetime import date

from fastapi.testclient import TestClient

from astro.bs_calendar import ad_to_bs, bs_to_ad
from main import app

client = TestClient(app)


def test_bs_month_anchor_month():
    # BS 2000-01: 30 days, starting at the anchor AD 1943-04-14.
    r = client.get("/api/bs-month", params={"bs_year": 2000, "bs_month": 1, "place_id": "kathmandu"})
    assert r.status_code == 200
    body = r.json()
    assert body["bs_year"] == 2000 and body["bs_month"] == 1
    assert body["month_length"] == 30 and len(body["days"]) == 30
    first, last = body["days"][0], body["days"][-1]
    assert first["bs"] == "2000-01-01" and first["ad"] == "1943-04-14"
    assert first["weekday"] == date(1943, 4, 14).weekday()
    assert last["bs"] == "2000-01-30" and last["ad"] == "1943-05-13"
    for d in body["days"]:
        assert 0 <= d["tithi_index"] <= 29 and 0 <= d["nakshatra_index"] <= 27
        assert d["bs_day"] == int(d["bs"].split("-")[2])


def test_bs_month_32_day_month_and_current_month():
    # 2083 Ashadh (month 3) has 32 days; 2083 Kartik (month 7) has 30.
    r = client.get("/api/bs-month", params={"bs_year": 2083, "bs_month": 3, "place_id": "kathmandu"})
    assert r.status_code == 200 and r.json()["month_length"] == 32
    assert len(r.json()["days"]) == 32
    r = client.get("/api/bs-month", params={"bs_year": 2083, "bs_month": 7, "place_id": "kathmandu"})
    assert r.status_code == 200
    days = r.json()["days"]
    assert r.json()["month_length"] == 30 and len(days) == 30
    # Known mapping: 2083-07-18 = AD 2026-11-04.
    assert days[17]["bs"] == "2083-07-18" and days[17]["ad"] == "2026-11-04"
    assert days[0]["ad"] == "2026-10-18"
    # Every BS day's AD date round-trips back to the same BS date.
    for d in days:
        bs = ad_to_bs(date.fromisoformat(d["ad"]))
        assert bs["iso"] == d["bs"]


def test_bs_month_round_trip_several():
    for (y, m, day) in [(2000, 2, 15), (2050, 5, 29), (2083, 12, 30), (2090, 1, 1)]:
        ad = bs_to_ad(y, m, day)
        r = client.get("/api/bs-month", params={"bs_year": y, "bs_month": m, "place_id": "kathmandu"})
        assert r.status_code == 200
        got = r.json()["days"][day - 1]
        assert got["bs"] == f"{y}-{m:02d}-{day:02d}" and got["ad"] == ad.isoformat()


def test_bs_month_bad_params_are_400():
    for params in [{"bs_year": 1999, "bs_month": 1}, {"bs_year": 2091, "bs_month": 1},
                   {"bs_year": 2083, "bs_month": 0}, {"bs_year": 2083, "bs_month": 13}]:
        r = client.get("/api/bs-month", params=params)
        assert r.status_code == 400, params


def test_bs_month_length():
    r = client.get("/api/bs-month-length", params={"bs_year": 2083, "bs_month": 3, "place_id": "kathmandu"})
    assert r.status_code == 200 and r.json()["month_length"] == 32
    r = client.get("/api/bs-month-length", params={"bs_year": 2083, "bs_month": 8})
    assert r.status_code == 200 and r.json()["month_length"] == 29
    for params in [{"bs_year": 1999, "bs_month": 1}, {"bs_year": 2083, "bs_month": 13}]:
        assert client.get("/api/bs-month-length", params=params).status_code == 400
