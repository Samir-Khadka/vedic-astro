"""Shadbala / Bhava Bala / Vimshopaka tests: published anchor values,
hand-computed golden values for the pinned sample chart, and invariants."""
from datetime import date, time

from astro import bala, charts as charts_module, ephemeris
from astro.names import PLANETS_7

SAMPLE_DATE, SAMPLE_TIME = date(1998, 5, 14), time(6, 30)
LAT, LON, TZ = 27.7172, 85.3240, "Asia/Kathmandu"


def _sample():
    birth_dt = ephemeris.make_local_datetime(SAMPLE_DATE, SAMPLE_TIME, TZ)
    jd = ephemeris.to_julian_day(birth_dt)
    planets = ephemeris.planet_longitudes(jd)
    lagna_lon = ephemeris.ascendant(jd, LAT, LON, b"W")
    cusps = ephemeris.placidus_cusps(jd, LAT, LON)
    charts = {v: charts_module.build_chart(planets, lagna_lon, v) for v in charts_module.VARGAS}
    return birth_dt, jd, planets, int(lagna_lon // 30), cusps, charts


def test_sputa_drishti_anchors():
    # B. V. Raman's published sputa-drishti anchor points.
    assert bala.sputa_drishti(0) == 0
    assert bala.sputa_drishti(30) == 0
    assert bala.sputa_drishti(60) == 15
    assert bala.sputa_drishti(90) == 45
    assert bala.sputa_drishti(120) == 30
    assert bala.sputa_drishti(150) == 0
    assert bala.sputa_drishti(180) == 60
    assert bala.sputa_drishti(240) == 30
    assert bala.sputa_drishti(300) == 0
    assert bala.sputa_drishti(359) == 0
    # Never out of range anywhere.
    t = 0.0
    while t < 360.0:
        assert 0.0 <= bala.sputa_drishti(t) <= 60.0
        t += 0.7


def test_dignity_categories():
    signs = {p: 0 for p in PLANETS_7}
    # Sun at 10 deg Aries: deep exaltation.
    assert bala.dignity_category("Sun", 0, signs, 10.0) == "exalted"
    # Sun at 10 deg Leo: moolatrikona (0-20 deg).
    assert bala.dignity_category("Sun", 4, signs, 10.0) == "moolatrikona"
    # Moon at 2 deg Taurus: exaltation zone; at 10 deg: moolatrikona.
    assert bala.dignity_category("Moon", 1, signs, 2.0) == "exalted"
    assert bala.dignity_category("Moon", 1, signs, 10.0) == "moolatrikona"
    # Mars in Libra (Venus's sign): Venus is Mars's natural neutral.
    # Venus in Aries is 7th from Libra -> temporary enemy -> compound enemy.
    signs2 = dict(signs, Venus=0)
    assert bala.dignity_category("Mars", 6, signs2) == "enemy"
    # Venus in Cancer is 10th from Libra -> temporary friend -> friend.
    signs3 = dict(signs, Venus=3)
    assert bala.dignity_category("Mars", 6, signs3) == "friend"


def test_shadbala_sample_golden_and_invariants():
    birth_dt, jd, planets, lagna_sign, cusps, charts = _sample()
    result = bala.shadbala(planets, lagna_sign, cusps, charts, birth_dt, LAT, LON, TZ, jd)
    rows = result["planets"]

    # Hand-computed golden: sample Sun at 29.2098 deg Aries, deepest
    # debilitation point 190 deg -> distance 160.79 -> /3 = 53.6 virupas.
    assert abs(rows["Sun"]["sthana"]["uccha"] - 53.6) < 0.15

    # 1998-05-14 was a Thursday and birth (06:30) is after sunrise,
    # so the vaara lord must be Jupiter.
    assert result["kala_lords"]["vaara_lord"] == "Jupiter"
    assert rows["Jupiter"]["kala"]["vaara"] == 45.0

    for p in PLANETS_7:
        r = rows[p]
        s = r["sthana"]
        assert 0.0 <= s["uccha"] <= 60.0
        assert 0.0 <= s["saptavargaja"] <= 7 * 45.0
        assert s["ojayugma"] in (0.0, 15.0, 30.0)
        assert s["kendradi"] in (15.0, 30.0, 60.0)
        assert s["drekkana"] in (0.0, 15.0)
        assert 0.0 <= r["dig"] <= 60.0
        assert r["naisargika"] == bala.NAISARGIKA[p]
        assert 0.0 <= r["ishta"] <= 60.0 and 0.0 <= r["kashta"] <= 60.0
        # Ishta^2 ~= Uccha x Cheshta (definition), allowing rounding.
        assert abs(r["ishta"] ** 2 - s["uccha"] * r["cheshta"]) < 2.0
        assert abs(r["rupas"] - r["total_virupas"] / 60.0) < 0.02
        assert abs(r["ratio"] - r["rupas"] / r["min_rupas"]) < 0.02
    ranks = sorted(r["rank"] for r in rows.values())
    assert ranks == [1, 2, 3, 4, 5, 6, 7]
    assert rows[result["strongest"]]["rank"] == 1
    assert rows[result["weakest"]]["rank"] == 7


def test_bhava_bala_sample():
    birth_dt, jd, planets, lagna_sign, cusps, charts = _sample()
    sb = bala.shadbala(planets, lagna_sign, cusps, charts, birth_dt, LAT, LON, TZ, jd)
    bb = bala.bhava_bala(planets, lagna_sign, cusps, sb)
    assert len(bb) == 12
    for row in bb:
        assert row["lord"] in PLANETS_7
        assert abs(row["total_rupas"] - (row["lord_bala_rupas"] + row["dig_bala_rupas"]
                                        + row["drik_bala_rupas"])) < 0.02
        # House 1 lord == Lagna lord (Venus for Taurus Lagna).
        if row["house"] == 1:
            assert row["lord"] == "Venus"


def test_vimshopaka_bounds():
    _b, _jd, planets, _lagna, _cusps, charts = _sample()
    vs = bala.vimshopaka(planets, charts)
    assert set(vs.keys()) == set(PLANETS_7)
    for p in PLANETS_7:
        for scheme in ("shadvarga", "saptavarga", "shodashavarga"):
            assert 0.0 <= vs[p][scheme] <= 20.0
