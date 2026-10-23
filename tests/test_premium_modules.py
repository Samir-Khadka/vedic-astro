"""Tests for transits, Lal Kitab, KP Prashna, Yogini/Tribhagi dashas,
name letters and numerology — invariants + published/reference values."""
from datetime import date, datetime
from zoneinfo import ZoneInfo

from astro import dasha as dasha_module, ephemeris, lalkitab, naming, numerology, prashna, transits

KTZ = ZoneInfo("Asia/Kathmandu")
KTM = {"name": "Kathmandu", "country": "Nepal", "lat": 27.7172, "lon": 85.3240, "tz": "Asia/Kathmandu"}
SAMPLE_MOON_LON = 236.7822  # Jyeshtha pada 4 (pinned sample chart)


# ---------------------------------------------------------------------------
def test_next_ingress_saturn_to_aries_2027():
    jd = ephemeris.to_julian_day(datetime(2026, 10, 23, 12, 0, tzinfo=KTZ))
    ing = transits.next_ingress("Saturn", jd)
    assert ing["from_sign"] == 11  # Saturn in Pisces through 2025-2027
    assert ing["to_sign"] == 0     # enters Aries in mid-2027
    assert "2027-05-01" <= ing["date"] <= "2027-07-15"


def test_ingress_bracketing():
    jd = ephemeris.to_julian_day(datetime(2026, 10, 23, 12, 0, tzinfo=KTZ))
    ing = transits.next_ingress("Sun", jd)
    # Sun's next ingress is into Scorpio (sign 7) within ~3 weeks.
    assert ing["to_sign"] == 7
    y, m, d = (int(x) for x in ing["date"].split("-"))
    jd_date = ephemeris.to_julian_day(datetime(y, m, d, 12, 0, tzinfo=KTZ))
    assert ephemeris.planet_longitudes(jd_date + 1.0)["Sun"]["sign"] == 7
    assert ephemeris.planet_longitudes(jd_date - 2.0)["Sun"]["sign"] == 6


def test_transit_table_shape():
    jd = ephemeris.to_julian_day(datetime(2026, 10, 23, 12, 0, tzinfo=KTZ))
    table = transits.transit_table(jd, moon_sign=7)
    assert len(table["ingress"]) == 6
    for row in table["ingress"]:
        assert 1 <= row["house_from_moon"] <= 12
        assert row["next_sign"] != row["current_sign"]


# ---------------------------------------------------------------------------
def _sample_planets():
    birth_dt = ephemeris.make_local_datetime(date(1998, 5, 14), __import__("datetime").time(6, 30), "Asia/Kathmandu")
    return ephemeris.planet_longitudes(ephemeris.to_julian_day(birth_dt))


def test_lal_kitab_structure():
    lk = lalkitab.lal_kitab(_sample_planets())
    all_placed = [p for ps in lk["chart"].values() for p in ps]
    assert sorted(all_placed) == sorted(["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"])
    by_name = {r["planet"]: r for r in lk["planets"]}
    # Sample: Sun in Aries -> khana 1, which is the Sun's pakka ghar.
    assert by_name["Sun"]["khana"] == 1 and by_name["Sun"]["in_pakka_ghar"] is True
    assert by_name["Sun"]["state"] == "jagta"
    # Moon in Scorpio -> khana 8.
    assert by_name["Moon"]["khana"] == 8
    for r in lk["planets"]:
        assert r["state"] in ("jagta", "soya")
        assert r["reading"]["en"] and r["reading"]["ne"]
    assert all(1 <= k <= 12 for k in lk["sleeping_houses"])


def test_lal_kitab_rin_rules():
    lk = lalkitab.lal_kitab(_sample_planets())
    assert len(lk["rin"]) == 9
    by_name = {r["name"]["en"]: r for r in lk["rin"]}
    # Matri Rin fires iff Ketu is in khana 4 — recompute from the chart.
    ketu_khana = next(r["khana"] for r in lk["planets"] if r["planet"] == "Ketu")
    assert by_name["Matri Rin"]["detected"] == (ketu_khana == 4)
    for r in lk["rin"]:
        assert r["detected"] in (True, False, None)
        assert r["remedy"]["en"] and r["remedy"]["ne"]


# ---------------------------------------------------------------------------
def test_prashna_reproducible_and_in_sub():
    moment = datetime(2026, 10, 23, 15, 0, tzinfo=KTZ)
    a = prashna.horary(100, KTM, moment, "Will it work?")
    b = prashna.horary(100, KTM, moment, "Will it work?")
    assert abs(a["lagna"]["longitude"] - b["lagna"]["longitude"]) < 0.01
    assert a["chart"] == b["chart"]
    # The horary Lagna sits inside sub #100's arc.
    assert a["sub"]["start_longitude"] - 0.01 <= a["lagna"]["longitude"] < a["sub"]["end_longitude"] + 0.01
    assert len(a["ruling_planets"]) == 7
    assert len(a["cusps"]) == 12
    assert a["question"] == "Will it work?"


def test_prashna_first_and_last_numbers():
    moment = datetime(2026, 10, 23, 15, 0, tzinfo=KTZ)
    first = prashna.horary(1, KTM, moment)
    assert first["sub"]["start_longitude"] == 0.0
    assert first["lagna"]["longitude"] < first["sub"]["end_longitude"]
    last = prashna.horary(249, KTM, moment)
    assert last["sub"]["end_longitude"] <= 360.0
    assert last["lagna"]["longitude"] >= last["sub"]["start_longitude"] - 0.01


def test_prashna_sub_table_tiles_zodiac():
    subs = prashna.sub_table()
    assert len(subs) == 249
    assert subs[0]["start"] == 0.0
    assert abs(subs[-1]["end"] - 360.0) < 1e-6
    for a, b in zip(subs, subs[1:]):
        assert abs(a["end"] - b["start"]) < 1e-9


# ---------------------------------------------------------------------------
def test_yogini_sample():
    birth = datetime(1998, 5, 14, 6, 30, tzinfo=KTZ)
    y = dasha_module.yogini_periods(birth, SAMPLE_MOON_LON, birth)
    # Jyeshtha (idx 17): (17+3) mod 8 = 4 -> Bhadrika (Mercury, 5 years).
    assert y["current"]["name"] == "Bhadrika" and y["current"]["planet"] == "Mercury"
    assert abs(y["balance_years"] - 1.2068) < 0.01
    periods = y["periods"]
    for a, b in zip(periods, periods[1:]):
        assert a["end"] == b["start"]
    assert abs(sum(p["years"] for p in periods[:8]) - 36.0) < 1e-9


def test_tribhagi_sample():
    birth = datetime(1998, 5, 14, 6, 30, tzinfo=KTZ)
    t = dasha_module.tribhagi_periods(birth, SAMPLE_MOON_LON, birth)
    # Vimshottari balance 4.1027 y -> Tribhagi balance a third of that.
    assert abs(t["balance_years"] - 4.1027 / 3.0) < 0.01
    assert t["current"]["lord"] == "Mercury"
    assert abs(sum(p["years"] for p in t["periods"]) - 120.0) < 1e-6


def test_name_letters():
    # Jyeshtha pada 4 -> Yu / यू (the pinned sample chart's Moon).
    nl = naming.name_letters(17, 4)
    assert nl["syllable_en"] == "Yu" and nl["syllable_ne"] == "यू"
    assert len(nl["options"]) == 4
    assert naming.name_letters(0, 1)["syllable_en"] == "Chu"
    # Whole table is complete: 27 nakshatras x 4 padas.
    assert len(naming.SYLLABLES) == 27 and all(len(s) == 4 for s in naming.SYLLABLES)


def test_numerology_arithmetic():
    n = numerology.numerology(date(1998, 5, 14))
    assert n["moolank"]["value"] == 5 and n["moolank"]["ruler"] == "Mercury"   # 14 -> 5
    assert n["bhagyank"]["value"] == 1 and n["bhagyank"]["ruler"] == "Sun"     # 19980514 -> 37 -> 1
    n2 = numerology.numerology(date(2000, 12, 31))
    assert n2["moolank"]["value"] == 4   # 31 -> 4
    assert n2["bhagyank"]["value"] == 9  # 20001231 -> 9
    for entry in (n["moolank"], n["bhagyank"]):
        assert entry["trait"]["en"] and entry["trait"]["ne"]
