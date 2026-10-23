"""Engine tests: golden values, first-principles invariants, and
cross-checks against raw Swiss Ephemeris calls made independently here."""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import swisseph as swe

from astro import charts, dasha as dasha_module, engine, ephemeris, kp as kp_module
from astro.matching import guna_milan
from astro.names import DASHA_SEQUENCE, DASHA_YEARS

SAMPLE = {"name": "Sample", "dob": "1998-05-14", "tob": "06:30:00", "place_id": "kathmandu"}


def test_sample_chart_cross_checked_with_raw_swe():
    """Engine wiring (timezone conversion + Lahiri sidereal) verified by an
    independent raw swisseph computation in this test."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    # 1998-05-14 06:30 +0545 == 00:45 UTC
    jd = swe.julday(1998, 5, 14, 0.75)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    sun = swe.calc_ut(jd, swe.SUN, flags)[0][0] % 360
    moon = swe.calc_ut(jd, swe.MOON, flags)[0][0] % 360
    _cusps, ascmc = swe.houses_ex(jd, 27.7172, 85.3240, b"W", swe.FLG_SIDEREAL)

    bundle = engine.compute_kundali(SAMPLE)
    by_name = {p["planet"]: p for p in bundle["planets"]}
    assert by_name["Sun"]["sign"] == int(sun // 30)
    assert by_name["Moon"]["sign"] == int(moon // 30)
    assert bundle["lagna"]["sign"] == int(ascmc[0] % 360 // 30)
    # Golden anchors for this chart (verified against the raw call above):
    assert bundle["lagna"]["sign_en"] == "Taurus"
    assert by_name["Sun"]["sign_en"] == "Aries"
    assert by_name["Moon"]["nakshatra_en"] == "Jyeshtha"
    assert abs(by_name["Sun"]["longitude"] - sun) < 0.01


def test_nakshatra_and_pada_boundaries():
    assert ephemeris.nakshatra_of(0.0) == (0, 1)          # Ashwini pada 1
    assert ephemeris.nakshatra_of(3.34) == (0, 2)         # second pada
    assert ephemeris.nakshatra_of(13.34) == (1, 1)        # Bharani begins
    assert ephemeris.nakshatra_of(359.99) == (26, 4)      # Revati last pada


def test_varga_d9_d10():
    # Aries 10.5 deg: movable sign, navamsa part 3 -> Cancer (3)
    assert charts.varga_sign("D9", 0, 10.5) == 3
    # Aries 9.9 deg: navamsa part 2 -> Gemini (2)
    assert charts.varga_sign("D9", 0, 9.9) == 2
    # Taurus 15 deg: Dasamsa even sign starts 9th (Capricorn 9), part 5 -> Gemini (2)
    assert charts.varga_sign("D10", 1, 15.0) == 2
    # Leo 0 deg in D9: fixed sign starts from 9th (Aries 0), part 0 -> Aries
    assert charts.varga_sign("D9", 4, 0.5) == 0
    assert charts.varga_sign("D1", 7, 22.0) == 7


def test_kp_sub_lord_math():
    chain0 = kp_module.kp_chain(0.0)
    assert chain0 == {"sign_lord": "Mars", "star_lord": "Ketu",
                      "sub_lord": "Ketu", "sub_sub_lord": "Ketu"}
    # 10 deg Aries: Ashwini; subs end at Saturn span 9.333-11.444 deg.
    chain10 = kp_module.kp_chain(10.0)
    assert chain10["star_lord"] == "Ketu"
    assert chain10["sub_lord"] == "Saturn"
    assert chain10["sub_sub_lord"] == "Ketu"
    # Sub divisions tile the full circle: every sampled longitude resolves.
    valid = set(DASHA_SEQUENCE)
    lon = 0.0
    while lon < 360.0:
        c = kp_module.kp_chain(lon)
        assert c["star_lord"] in valid and c["sub_lord"] in valid and c["sub_sub_lord"] in valid
        lon += 0.37


def test_dasha_invariants():
    tz = ZoneInfo("Asia/Kathmandu")
    birth = datetime(1998, 5, 14, 6, 30, tzinfo=tz)
    bundle = engine.compute_kundali(SAMPLE)
    moon_lon = next(p["longitude"] for p in bundle["planets"] if p["planet"] == "Moon")
    now = birth + timedelta(days=3650)
    tree = dasha_module.vimshottari_tree(birth, moon_lon, now)
    mds = tree["mahadashas"]
    assert len(mds) == 9
    assert abs(sum(m["years"] for m in mds) - 120.0) < 1e-6
    seq = [m["lord"] for m in mds]
    start_idx = DASHA_SEQUENCE.index(seq[0])
    assert seq == [DASHA_SEQUENCE[(start_idx + i) % 9] for i in range(9)]
    # Contiguity: each period starts where the previous ended.
    for a, b in zip(mds, mds[1:]):
        assert a["end"] == b["start"]
    # Antardashas tile their mahadasha.
    for md in mds:
        ads = md["antardashas"]
        assert len(ads) == 9 and ads[0]["start"] == md["start"] and ads[-1]["end"] == md["end"]
    # Current-period containment.
    cur = tree["current"]
    assert cur is not None and cur["mahadasha"]["start"] <= now < cur["mahadasha"]["end"]
    assert cur["antardasha"]["start"] <= now < cur["antardasha"]["end"]


def test_dasha_balance_edges():
    tz = ZoneInfo("Asia/Kathmandu")
    birth = datetime(2000, 1, 1, 0, 0, tzinfo=tz)
    # Moon at exact start of Ashwini -> full Ketu balance of 7 years.
    tree = dasha_module.vimshottari_tree(birth, 0.0, birth)
    assert abs(tree["balance_years"] - DASHA_YEARS["Ketu"]) < 1e-9
    # Half-way through Ashwini -> half the Ketu period remains.
    tree2 = dasha_module.vimshottari_tree(birth, 360.0 / 27.0 / 2.0, birth)
    assert abs(tree2["balance_years"] - 3.5) < 1e-6


def test_ashtakavarga_totals():
    bundle = engine.compute_kundali(SAMPLE)
    av = bundle["ashtakavarga"]
    expected = {"Sun": 48, "Moon": 49, "Mars": 39, "Mercury": 54,
                "Jupiter": 56, "Venus": 52, "Saturn": 39}
    for planet, total in expected.items():
        assert sum(av[planet]) == total, planet
    assert sum(av["Sarvashtakavarga"]) == 337
    for s in range(12):
        assert av["Sarvashtakavarga"][s] == sum(av[p][s] for p in expected)


def test_matching_golden_rohini_pair():
    """Both partners Moon in Taurus / Rohini — hand-computed total 28/36:
    Varna 1, Vashya 2, Tara 3, Yoni 4, Maitri 5, Gana 6, Bhakoot 7, Nadi 0."""
    person = {"moon_sign": 1, "moon_nakshatra": 3}
    result = guna_milan(person, dict(person))
    scores = {row["koota"]: row["score"] for row in result["breakdown"]}
    assert scores == {"Varna": 1, "Vashya": 2, "Tara": 3, "Yoni": 4,
                      "Graha Maitri": 5, "Gana": 6, "Bhakoot": 7, "Nadi": 0}
    assert result["total"] == 28
    assert result["nadi_dosha"] is True


def test_matching_bounds():
    a = {"moon_sign": 0, "moon_nakshatra": 0}
    b = {"moon_sign": 6, "moon_nakshatra": 14}
    result = guna_milan(a, b)
    assert 0 <= result["total"] <= 36
    assert len(result["breakdown"]) == 8
