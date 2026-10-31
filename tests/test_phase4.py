"""Phase 4: Sarvatobhadra Chakra, dasha pravesh, transit calendar,
ephemeris tables, favourable periods."""
from datetime import datetime, timezone

from astro import phase4 as p4


# ---------------------------------------------------------------------------
# Sarvatobhadra grid
# ---------------------------------------------------------------------------

def test_nakshatra_positions_cover_28():
    assert len(p4._SBC_NAK_POS) == 28
    assert len(set(p4._SBC_NAK_POS.values())) == 28
    # Krittika at north-east (top of east side).
    assert p4._SBC_NAK_POS["Krittika"] == (1, 8)
    # Bharani last on the north side.
    assert p4._SBC_NAK_POS["Bharani"] == (0, 7)
    # Abhijit between Uttarashadha and Shravana on the west.
    assert p4._SBC_NAK_POS["Abhijit"] == (2, 0)


def test_vedha_punarvasu_matches_pvr_example():
    """PVR's worked example: Saturn in Punarvasu.

    West line: h, Cn, au, Bhadra(+Mon/Wed), am, Sc, y, Moola.
    NW line: k, Ta, Ar, d, Poorva Bhadrapada.
    SW line: d(alveolar), m, Uttara Phalguni.
    We check the nakshatra/rasi/tithi endpoints, which are unambiguous.
    """
    cells = p4.vedha_cells("Punarvasu")
    # West line endpoints and rasis.
    assert (5, 0) in cells   # Moola (west border)
    assert (5, 6) in cells   # Cancer
    assert (5, 2) in cells   # Scorpio
    assert (5, 4) in cells   # Bhadra + Mon/Wed (core)
    # NW line.
    assert (3, 6) in cells   # Taurus
    assert (2, 5) in cells   # Aries
    assert (0, 3) in cells   # Poorva Bhadrapada (north border)
    # SW line.
    assert (8, 5) in cells   # Uttara Phalguni (south border)


def test_vedha_lines_are_three():
    for nak in ("Krittika", "Magha", "Anuradha", "Dhanishta",
                "Abhijit", "Bharani"):
        lines = p4.vedha_lines(nak)
        assert len(lines) == 3, nak
        # Every line starts at the nakshatra's own cell.
        for line in lines:
            assert line[0] == p4._SBC_NAK_POS[nak]


def test_nakshatra_28_abhijit():
    # Capricorn 8 deg = inside Abhijit (6d40m - 10d53m).
    assert p4.nakshatra_28(278.0, "Uttara Ashadha") == "Abhijit"
    assert p4.nakshatra_28(278.0, "Shravana") == "Abhijit"
    # Outside Abhijit -> normal mapping.
    assert p4.nakshatra_28(10.0, "Ashwini") == "Ashwini"
    assert p4.nakshatra_28(40.0, "Rohini") == "Rohini"


def test_tithi_group():
    assert p4.tithi_group(1) == "Nanda"
    assert p4.tithi_group(8) == "Jaya"
    assert p4.tithi_group(15) == "Purna"
    assert p4.tithi_group(30) == "Purna"


def test_sarvatobhadra_summary_structure():
    natal = {
        "moon_nakshatra_27": "Jyeshtha", "moon_longitude": 230.0,
        "lagna_rasi_en": "Scorpio", "tithi": 8, "weekday_en": "Thursday",
    }
    transits = {
        p: {"nakshatra_27": "Punarvasu", "longitude": 95.0}
        for p in ("Sun", "Moon", "Mars", "Mercury", "Jupiter",
                  "Venus", "Saturn", "Rahu", "Ketu")
    }
    sbc = p4.sarvatobhadra(natal, transits)
    assert sbc["natal_points"]["janma_nakshatra_28"] == "Jyeshtha"
    assert sbc["natal_points"]["tithi_group"] == "Jaya"
    assert set(sbc["summary"]) == {"janma_nakshatra", "lagna_rasi",
                                   "tithi", "weekday"}
    assert len(sbc["planets"]) == 9
    # Nature classification.
    by_planet = {pl["planet"]: pl for pl in sbc["planets"]}
    assert by_planet["Jupiter"]["nature"] == "benefic"
    assert by_planet["Saturn"]["nature"] == "malefic"


# ---------------------------------------------------------------------------
# Dasha pravesh
# ---------------------------------------------------------------------------

def test_dasha_pravesh():
    birth = datetime(1998, 5, 14, 6, 30, tzinfo=timezone.utc)
    start = datetime(2020, 1, 1, tzinfo=timezone.utc)
    dp = p4.dasha_pravesh(birth, start, 27.7, 85.3)
    assert dp["dasha_start"] == "2020-01-01"
    assert len(dp["planets"]) == 9
    assert dp["lagna"]["sign_en"] in (
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces")


# ---------------------------------------------------------------------------
# Transit calendar / ephemeris / favourable periods
# ---------------------------------------------------------------------------

def test_transit_calendar():
    cal = p4.transit_calendar(datetime(2026, 10, 31, tzinfo=timezone.utc), 3)
    assert cal["months"] == 3
    assert len(cal["events"]) > 0
    dates = [e["date"] for e in cal["events"]]
    assert dates == sorted(dates)


def test_ephemeris_table():
    eph = p4.ephemeris_table(2026, 11)
    assert eph["year"] == 2026 and eph["month"] == 11
    assert len(eph["rows"]) == 30
    assert eph["rows"][0]["Sun"]["sign_en"] in (
        "Libra", "Scorpio", "Sagittarius")


def test_favourable_periods():
    from astro.dasha import vimshottari_tree
    birth = datetime(1998, 5, 14, 6, 30, tzinfo=timezone.utc)
    tree = vimshottari_tree(birth, 230.0)
    fp = p4.favourable_periods(
        birth, 16, tree, now=datetime(2026, 10, 31, tzinfo=timezone.utc))
    assert len(fp["days"]) == 30
    assert 0 <= fp["good_days"] <= 30
    assert all(1 <= d["tara"] <= 9 for d in fp["days"])
