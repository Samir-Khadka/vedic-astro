"""Regression tests: Dasha Sandhi on-day boundary + gemstone finger translations.

- 2026-11-23: _dasha_sandhi excluded a dasha change falling exactly on the
  marriage day (boundary.date() != marriage_day), so the strongest case —
  a change ON the wedding day — was silently dropped and the "nearest"
  hit reported was a different, farther boundary.
- 2026-11-23: GEMSTONES listed the Sun's Ruby on the "Ring finger" in
  English but "कान्छी औंला" (little finger) in Nepali; the ring finger
  is "साहिंली औंला".
"""
from datetime import date, datetime, time

from astro import dasha as dasha_module
from astro import ephemeris, report as report_module
from astro.complete_report import _ratna_mantra
from astro.engine import _dasha_sandhi, compute_kundali

SAMPLE = {"name": "Sample", "dob": "1998-05-14", "tob": "06:30", "place_id": "kathmandu"}


def _sample_person():
    from astro.engine import resolve_place

    place = resolve_place(dict(SAMPLE))
    birth_dt = ephemeris.make_local_datetime(
        date(1998, 5, 14), time(6, 30), place["tz"])
    jd = ephemeris.to_julian_day(birth_dt)
    planets = ephemeris.planet_longitudes(jd)
    return {"birth_dt": birth_dt, "moon_lon": planets["Moon"]["longitude"],
            "tz": place["tz"]}, birth_dt, planets["Moon"]["longitude"]


def test_dasha_sandhi_flags_change_on_the_wedding_day():
    person, birth_dt, moon_lon = _sample_person()
    tree = dasha_module.vimshottari_tree(
        birth_dt, moon_lon, datetime(2027, 1, 1, tzinfo=birth_dt.tzinfo))
    # Second mahadasha starts 2002-06-20 (Mercury ends, Ketu starts).
    boundary = tree["mahadashas"][1]["start"].date()
    assert boundary == date(2002, 6, 20)
    result = _dasha_sandhi(person, boundary)
    assert result["in_window"] is True
    assert result["nearest"]["days_away"] == 0
    assert result["nearest"]["date"] == "2002-06-20"
    assert result["nearest"]["level"] == "Mahadasha"
    # The same-day change is the nearest hit, not a farther boundary.
    assert all(h["days_away"] >= 0 for h in result["all_in_window"])
    assert result["all_in_window"][0]["days_away"] == 0


def test_dasha_sandhi_antardasha_change_on_the_day():
    person, birth_dt, moon_lon = _sample_person()
    tree = dasha_module.vimshottari_tree(
        birth_dt, moon_lon, datetime(2027, 1, 1, tzinfo=birth_dt.tzinfo))
    # An Antardasha boundary with no Mahadasha boundary on the same day.
    ad_start = tree["mahadashas"][0]["antardashas"][1]["start"].date()
    md_starts = {md["start"].date() for md in tree["mahadashas"]}
    md_ends = {md["end"].date() for md in tree["mahadashas"]}
    assert ad_start not in md_starts and ad_start not in md_ends
    result = _dasha_sandhi(person, ad_start)
    assert result["in_window"] is True
    assert result["nearest"]["days_away"] == 0
    assert result["nearest"]["level"] == "Antardasha"


def test_dasha_sandhi_quiet_date_has_no_hit():
    person, birth_dt, moon_lon = _sample_person()
    tree = dasha_module.vimshottari_tree(
        birth_dt, moon_lon, datetime(2027, 1, 1, tzinfo=birth_dt.tzinfo))
    boundaries = set()
    for md in tree["mahadashas"]:
        boundaries.add(md["start"].date())
        boundaries.add(md["end"].date())
        for ad in md["antardashas"]:
            boundaries.add(ad["start"].date())
            boundaries.add(ad["end"].date())
    # Find a date provably >180 days from every MD/AD boundary (from the
    # tree itself, not from the function under test).
    from datetime import timedelta

    candidate = date(2015, 1, 1)
    while min(abs((b - candidate).days) for b in boundaries) <= 180:
        candidate += timedelta(days=30)
    assert min(abs((b - candidate).days) for b in boundaries) > 180
    result = _dasha_sandhi(person, candidate)
    assert result["in_window"] is False
    assert result["nearest"] is None
    assert result["all_in_window"] == []


def test_gemstone_finger_translations_match_english():
    expected = {
        "Ring finger": "साहिंली औंला",
        "Little finger": "कान्छी औंला",
        "Middle finger": "माझी औंला",
        "Index finger": "चोर औंला",
    }
    for planet, row in report_module.GEMSTONES.items():
        finger_en, finger_ne = row[4], row[5]
        assert finger_ne == expected[finger_en], (
            f"{planet}: {finger_en!r} must translate to {expected[finger_en]!r}, "
            f"got {finger_ne!r}")
    assert report_module.GEMSTONES["Sun"][4] == "Ring finger"
    assert report_module.GEMSTONES["Sun"][5] == "साहिंली औंला"


def test_ratna_mantra_sun_suggestion_uses_ring_finger_nepali():
    bundle = compute_kundali(dict(SAMPLE))
    per_planet = _ratna_mantra(bundle)
    sun = next(p for p in per_planet if p["planet"] == "Sun")
    assert sun["finger"]["en"] == "Ring finger"
    assert sun["finger"]["ne"] == "साहिंली औंला"
    assert "साहिंली औंलामा" in sun["suggestion"]["ne"]
    assert "कान्छी औंलामा" not in sun["suggestion"]["ne"]
