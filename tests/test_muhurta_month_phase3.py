"""Phase 3 Part C1: Muhurta month view needs no new backend — a calendar
month is at most 31 days, which already fits /api/muhurta's 1–31 day
limit. These tests pin that contract for the month view's exact
requests (full 31-day month, February, and an out-of-range month)."""
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)
KTM = {"lat": 27.7172, "lon": 85.3240, "tz": "Asia/Kathmandu"}
GRADES = {"Excellent", "Good", "Average", "Avoid"}


def test_full_31_day_month_returns_every_day_with_grades():
    res = client.get("/api/muhurta", params={
        "date_from": "2026-12-01", "date_to": "2026-12-31",
        "activity": "marriage", **KTM,
    })
    assert res.status_code == 200, res.text
    data = res.json()
    assert len(data["days"]) == 31
    assert [d["date"] for d in data["days"]] == [f"2026-12-{d:02d}" for d in range(1, 32)]
    for d in data["days"]:
        assert d["grade"] in GRADES and d["grade_ne"]
        assert isinstance(d["election_score"], int)


def test_february_month_view_range():
    res = client.get("/api/muhurta", params={
        "date_from": "2027-02-01", "date_to": "2027-02-28",
        "activity": "travel", **KTM,
    })
    assert res.status_code == 200, res.text
    assert len(res.json()["days"]) == 28


def test_range_over_31_days_still_rejected():
    res = client.get("/api/muhurta", params={
        "date_from": "2026-11-01", "date_to": "2026-12-15",
        "activity": "marriage", **KTM,
    })
    assert res.status_code == 400
