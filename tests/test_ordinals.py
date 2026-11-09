"""Regression tests for English ordinals in generated text.

Same bug class as the 2026-11-01 Dhana-yoga "2th" fix: several modules
built ordinals with a bare f"{n}th", printing "1th house", "2th house",
"3th khana" and "2th house" in user-facing English. All English
ordinals now go through astro.names.ordinal_en; these tests pin the
helper and every site that used to print the broken form.
"""
from __future__ import annotations

import re
from datetime import date

import pytest
from fastapi.testclient import TestClient

from astro.argala import argala_for_house
from astro.horoscope import horoscope
from astro.kp_events import kp_event_analysis
from astro.lalkitab import lal_kitab
from astro.names import ordinal_en
from main import app

_BAD = re.compile(r"\b[123]th\b")  # "1th"/"2th"/"3th" are never correct

_PLANET_HOUSES = {
    "Sun": 1, "Moon": 5, "Mars": 7, "Mercury": 2, "Jupiter": 3,
    "Venus": 4, "Saturn": 6, "Rahu": 9, "Ketu": 10,
}


def test_ordinal_en():
    cases = {
        1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 10: "10th",
        11: "11th", 12: "12th", 13: "13th", 21: "21st", 22: "22nd",
        23: "23rd", 101: "101st", 111: "111th", 112: "112th",
    }
    for n, want in cases.items():
        assert ordinal_en(n) == want, f"ordinal_en({n})"


def test_horoscope_summary_ordinals():
    # Moon sign Virgo on 2026-11-09: transit Moon sits in the 2nd house
    # from it, which used to print "2th house".
    out = horoscope(5, "daily", date(2026, 11, 9), "Asia/Kathmandu")
    summary = out["summary"]["en"]
    assert "2nd house" in summary
    assert not _BAD.search(summary), summary


def test_horoscope_summary_ordinals_via_api():
    client = TestClient(app)
    resp = client.get("/api/horoscope",
                      params={"sign": 5, "span": "daily",
                              "date": "2026-11-09", "tz": "Asia/Kathmandu"})
    assert resp.status_code == 200
    summary = resp.json()["summary"]["en"]
    assert "2nd house" in summary
    assert not _BAD.search(summary), summary


def test_argala_readings_ordinals():
    for house in range(1, 13):
        reading = argala_for_house(house, _PLANET_HOUSES)["reading"]["en"]
        assert f"{ordinal_en(house)} house" in reading, reading
        assert not _BAD.search(reading), reading


def test_lal_kitab_readings_ordinals():
    # One planet per khana 1..9 covers khanas 1, 2 and 3 (the broken ones).
    planets = {p: {"sign": s} for p, s in
               [("Sun", 0), ("Moon", 1), ("Mars", 2), ("Mercury", 3),
                ("Jupiter", 4), ("Venus", 5), ("Saturn", 6),
                ("Rahu", 7), ("Ketu", 8)]}
    rows = lal_kitab(planets)["planets"]
    assert len(rows) == 9
    for row in rows:
        reading = row["reading"]["en"]
        k = row["khana"]
        assert f"{ordinal_en(k)} khana" in reading, reading
        assert not _BAD.search(reading), reading


def test_kp_event_summary_ordinals():
    # Minimal KP/dasha/transit inputs; primaries span 2, 4, 5, 7, 10, 12.
    cusps = [{"house": h, "sub_lord": "Jupiter"} for h in range(1, 13)]
    kp = {
        "planet_signified_houses": {p: [2, 5, 7, 11] for p in
                                    ("Sun", "Moon", "Mars", "Mercury", "Jupiter",
                                     "Venus", "Saturn", "Rahu", "Ketu")},
        "cusps": cusps,
    }
    dasha_tree = {"current": {"mahadasha": {"lord": "Jupiter"},
                              "antardasha": {"lord": "Venus"}}}
    out = kp_event_analysis(kp, dasha_tree, {"Jupiter": 4, "Saturn": 6}, 0)
    primaries = {"marriage": 7, "career": 10, "wealth": 2, "children": 5,
                 "education": 4, "foreign": 12, "property": 4}
    for key, primary in primaries.items():
        summary = out[key]["summary"]["en"]
        assert f"{ordinal_en(primary)} house" in summary, (key, summary)
        assert not _BAD.search(summary), (key, summary)


def test_kundali_bundle_has_no_broken_ordinals():
    """Whole-bundle sweep: argala + lal kitab + KP event texts ship here."""
    client = TestClient(app)
    resp = client.post("/api/kundali", json={
        "dob": "1998-05-14", "tob": "06:30", "place_id": "kathmandu",
    })
    assert resp.status_code == 200
    bad = _BAD.findall(resp.text)
    assert bad == [], f"broken ordinals in bundle: {bad[:5]}"
