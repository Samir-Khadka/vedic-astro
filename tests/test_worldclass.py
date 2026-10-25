"""World-class program: goldens/invariants for the new P0 modules."""
from datetime import date, datetime, timedelta

from fastapi.testclient import TestClient

from astro import (
    ashtakavarga as av_module,
    chalit as chalit_module,
    ephemeris,
    horoscope as horoscope_module,
    kp as kp_module,
    kp_events as kp_events_module,
    muhurta as muhurta_module,
    panchang as panchang_module,
    prastara as prastara_module,
    sudarshana as sudarshana_module,
)
from astro import dasha as dasha_module
from astro.engine import compute_kundali, compute_match
from main import app

client = TestClient(app)
SAMPLE = {"name": "Sample", "dob": "1998-05-14", "tob": "06:30", "place_id": "kathmandu"}
KTM = dict(lat=27.7172, lon=85.3240, tz_name="Asia/Kathmandu")


def _sample_bundle():
    return compute_kundali(dict(SAMPLE))


def _sample_planets_cusps():
    from zoneinfo import ZoneInfo

    from astro.engine import resolve_place

    place = resolve_place(dict(SAMPLE))
    dt = ephemeris.make_local_datetime(date(1998, 5, 14), datetime.strptime("06:30", "%H:%M").time(), place["tz"])
    jd = ephemeris.to_julian_day(dt)
    planets = ephemeris.planet_longitudes(jd)
    cusps = ephemeris.placidus_cusps(jd, place["lat"], place["lon"])
    lagna_sign = int(ephemeris.ascendant(jd, place["lat"], place["lon"], b"W") // 30.0)
    return planets, cusps, lagna_sign


# ---------------------------------------------------------------- Bhava Chalit
def test_chalit_boundaries_are_cusp_midpoints_and_tile():
    _planets, cusps, _lagna = _sample_planets_cusps()
    bounds = chalit_module.house_boundaries(cusps)
    assert len(bounds) == 12
    # Boundary 0 = midpoint of cusp 11 and cusp 0.
    expect = (cusps[11] + ((cusps[0] - cusps[11]) % 360.0) / 2.0) % 360.0
    assert abs(bounds[0] - expect) < 1e-9
    # Sorted boundaries tile the zodiac.
    s = sorted(bounds)
    gaps = [ (s[(i + 1) % 12] - s[i]) % 360.0 for i in range(12) ]
    assert abs(sum(gaps) - 360.0) < 1e-6
    # Every planet lands in exactly one house.
    for lon in (0.0, 90.0, 359.9):
        assert 1 <= chalit_module.chalit_house(lon, bounds) <= 12


def test_chalit_bundle_keys_and_shift_flag():
    b = _sample_bundle()
    ch = b["bhava_chalit"]
    assert set(ch["houses"].keys()) == {"Sun", "Moon", "Mars", "Mercury", "Jupiter",
                                        "Venus", "Saturn", "Rahu", "Ketu"}
    for name, row in ch["houses"].items():
        assert row["shifted"] == (row["chalit_house"] != row["rashi_house"])
        assert row["shifted"] == (name in ch["shifted"])


# ---------------------------------------------------------------- Prastara
def test_prastara_grids_reproduce_bav_and_reductions_shrink():
    planets, _cusps, lagna = _sample_planets_cusps()
    bav = av_module.compute_ashtakavarga(planets, lagna)
    pr = prastara_module.prastara(planets, lagna)
    for planet in av_module.BENEFIC:
        grid = pr[planet]["grid"]
        assert set(grid.keys()) == set(prastara_module.CONTRIBUTORS)
        for s in range(12):
            col = sum(grid[c][s] for c in prastara_module.CONTRIBUTORS)
            assert col == bav[planet][s], (planet, s)
        assert pr[planet]["reduced_total"] <= sum(bav[planet])
        assert all(v >= 0 for v in pr[planet]["reduced"])
    sarva_red = pr["Sarvashtakavarga_reduced"]
    for s in range(12):
        assert sarva_red[s] == sum(pr[p]["reduced"][s] for p in av_module.BENEFIC)


def test_prastara_reduction_rules_unit():
    # Trikona: all three non-zero -> min subtracted from each.
    bav = [0] * 12
    bav[0], bav[4], bav[8] = 5, 3, 4
    out = prastara_module._trikona_reduce(bav, 0)
    assert (out[0], out[4], out[8]) == (2, 0, 1)
    # Trikona with a zero -> untouched.
    bav2 = [0] * 12
    bav2[0], bav2[4], bav2[8] = 5, 0, 4
    assert prastara_module._trikona_reduce(bav2, 0) == bav2
    # Ekadhipatya: one empty -> both zeroed; both full -> smaller subtracted.
    bav3 = [0] * 12
    bav3[0], bav3[7] = 4, 0
    assert prastara_module._ekadhipatya_reduce(bav3)[0] == 0
    bav4 = [0] * 12
    bav4[0], bav4[7] = 5, 3
    out4 = prastara_module._ekadhipatya_reduce(bav4)
    assert (out4[0], out4[7]) == (2, 0)


# ---------------------------------------------------------------- Muhurta
def test_muhurta_rahu_kaal_segment_by_weekday():
    # 2026-10-26 is a Monday (weekday Sun-first index 1 -> segment 2).
    monday = date(2026, 10, 26)
    assert monday.weekday() == 0
    d = muhurta_module.day_muhurta(monday, **KTM)
    assert d["choghadiya_day"][1]["rahu_kaal"] is True
    assert sum(1 for s in d["choghadiya_day"] if s["rahu_kaal"]) == 1
    # Sunday -> segment 8.
    sunday = date(2026, 11, 1)
    d2 = muhurta_module.day_muhurta(sunday, **KTM)
    assert d2["choghadiya_day"][7]["rahu_kaal"] is True


def test_muhurta_abhijit_contains_midday_and_segments_tile():
    d = muhurta_module.day_muhurta(date(2026, 10, 26), **KTM)
    rise = datetime.fromisoformat(d["sunrise"])
    set_ = datetime.fromisoformat(d["sunset"])
    abh_s = datetime.fromisoformat(d["abhijit"]["start"])
    abh_e = datetime.fromisoformat(d["abhijit"]["end"])
    midday = rise + (set_ - rise) / 2
    assert abh_s <= midday <= abh_e
    # Day choghadiya tiles rise->set exactly.
    segs = d["choghadiya_day"]
    assert datetime.fromisoformat(segs[0]["start"]) == rise
    assert datetime.fromisoformat(segs[-1]["end"]) == set_
    assert all(s["good"] == (s["lord"] in muhurta_module.GOOD_CHOGHADIYA) for s in segs)
    # Good windows never overlap the Rahu Kaal window.
    rk = (d["rahu_kaal"]["start"], d["rahu_kaal"]["end"])
    assert all((w["start"], w["end"]) != rk for w in d["good_windows"])
    assert all(w["lord"] in muhurta_module.GOOD_CHOGHADIYA for w in d["good_windows"])
    # 24 horas, day lord first (Monday -> Moon).
    assert len(d["hora"]) == 24 and d["hora"][0]["lord"] == "Moon"
    # Range guard.
    try:
        muhurta_module.muhurta_range(date(2026, 10, 1), date(2026, 11, 5), **KTM)
    except ValueError:
        pass
    else:
        raise AssertionError("expected range guard")


def test_muhurta_endpoint_and_best_days():
    r = client.get("/api/muhurta", params={
        "date_from": "2026-10-26", "date_to": "2026-11-01",
        "activity": "marriage", "place_id": "kathmandu"})
    assert r.status_code == 200
    body = r.json()
    assert len(body["days"]) == 7 and len(body["best"]) == 5
    assert body["best"][0]["score"] >= body["best"][-1]["score"]
    assert all("rahu_kaal" in d and "abhijit" in d for d in body["days"])


# ---------------------------------------------------------------- Horoscope
def test_horoscope_houses_and_ratings():
    h = horoscope_module.horoscope(7, "daily", date(2026, 10, 25), "Asia/Kathmandu")
    assert h["moon_sign"] == 7 and set(h["areas"].keys()) == {"career", "finance", "relationships", "health"}
    for area in h["areas"].values():
        assert area["rating"] in ("Favourable", "Mixed", "Careful")
        assert area["text"]["en"] and area["text"]["ne"]
    # House arithmetic: house = (transit sign - Moon sign) mod 12 + 1.
    assert h["transits"]["Moon"]["house"] == (h["transits"]["Moon"]["sign"] - 7) % 12 + 1
    # Weekly journey covers the week; monthly ingresses sorted.
    w = horoscope_module.horoscope(7, "weekly", date(2026, 10, 25), "Asia/Kathmandu")
    assert w["start"] == "2026-10-25" and w["end"] == "2026-10-31"
    assert w["moon_journey"] and w["moon_journey"][0]["date"] == "2026-10-25"
    m = horoscope_module.horoscope(7, "monthly", date(2026, 11, 10), "Asia/Kathmandu")
    dates = [i["date"] for i in m["ingresses"]]
    assert dates == sorted(dates)


def test_horoscope_endpoint():
    r = client.get("/api/horoscope", params={"sign": 7, "span": "daily", "date": "2026-10-25"})
    assert r.status_code == 200 and r.json()["moon_sign_en"] == "Scorpio"
    r2 = client.get("/api/horoscope", params={"sign": 12, "span": "daily"})
    assert r2.status_code == 422


# ---------------------------------------------------------------- KP events
def test_kp_events_structure_and_negating_rule():
    b = _sample_bundle()
    ev = b["kp_events"]
    assert set(ev.keys()) == {"marriage", "career", "wealth", "children", "education", "foreign", "property"}
    assert ev["marriage"]["negating"] == [1, 6, 10]  # 12th-from {2,7,11}
    for row in ev.values():
        assert row["verdict"] in ("Promised", "Mixed", "Weak", "Not indicated")
        assert row["summary"]["en"] and row["summary"]["ne"]
        assert row["cuspal_sub_lord"] in ("Sun", "Moon", "Mars", "Mercury", "Jupiter",
                                          "Venus", "Saturn", "Rahu", "Ketu")


def test_kp_events_verdict_logic_unit():
    # Synthetic KP: marriage 7th cusp sub lord signifies 2,7,11 -> Promised.
    from astro.names import SIGN_LORDS

    cusps = []
    for h in range(1, 13):
        cusps.append({"house": h, "longitude": (h - 1) * 30.0, "sign": (h - 1) % 12,
                      "sign_lord": SIGN_LORDS[(h - 1) % 12], "star_lord": "Sun",
                      "sub_lord": "Jupiter" if h == 7 else "Sun", "sub_sub_lord": "Sun"})
    kp = {"cusps": cusps,
          "planet_signified_houses": {"Jupiter": [2, 7, 11], "Sun": [1], "Moon": [1],
                                      "Mars": [1], "Mercury": [1], "Venus": [1],
                                      "Saturn": [1], "Rahu": [1], "Ketu": [1]}}
    tree = {"current": {"mahadasha": {"lord": "Sun"}, "antardasha": {"lord": "Sun"}}}
    out = kp_events_module.kp_event_analysis(kp, tree, {"Jupiter": 0, "Saturn": 0}, 0)
    assert out["marriage"]["verdict"] == "Promised"
    assert out["marriage"]["dasha_support"] is False


# ---------------------------------------------------------------- Sudarshana
def test_sudarshana_triple_agreement_unit():
    planets = {p: {"sign": 0, "longitude": 10.0} for p in
               ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu")}
    s = sudarshana_module.sudarshana(planets, 0)
    assert s["rings"] == {"lagna": 0, "moon": 0, "sun": 0}
    assert all(v["agreement"] == "triple" for v in s["planets"].values())
    assert len(s["confirmed"]) == 9
    # Divergent rings -> varied (Moon/Sun in different signs from Lagna).
    planets["Moon"] = {"sign": 1, "longitude": 40.0}
    planets["Sun"] = {"sign": 2, "longitude": 70.0}
    planets["Mars"] = {"sign": 3, "longitude": 100.0}
    s2 = sudarshana_module.sudarshana(planets, 0)
    assert s2["planets"]["Mars"]["agreement"] == "varied"


def test_bundle_has_worldclass_keys():
    b = _sample_bundle()
    for key in ("bhava_chalit", "prastara", "kp_events", "sudarshana"):
        assert key in b, key


# ---------------------------------------------------------------- Month panchang
def test_month_panchang_markers():
    m = panchang_module.month_panchang(2026, 10, **KTM)
    assert len(m["days"]) == 31
    for d in m["days"]:
        if "Ekadashi" in d["markers"]:
            assert d["tithi_index"] in (10, 25)
        if "Purnima" in d["markers"]:
            assert d["tithi_index"] == 14
        if "Amavasya" in d["markers"]:
            assert d["tithi_index"] == 29
    assert any("Sankranti" in d["markers"] for d in m["days"])
    r = client.get("/api/panchang-month", params={"year": 2026, "month": 10, "place_id": "kathmandu"})
    assert r.status_code == 200 and len(r.json()["days"]) == 31


# ---------------------------------------------------------------- Match extension
def test_match_extension_sections():
    a = dict(SAMPLE)
    bb = {"name": "B", "dob": "1999-01-05", "tob": "08:15", "place_id": "kathmandu"}
    r = client.post("/api/match", json={"groom": a, "bride": bb, "marriage_date": "2027-02-14"})
    assert r.status_code == 200
    body = r.json()
    for key in ("papasamya", "bhava_milan", "dasha_sandhi", "combined_verdict"):
        assert key in body, key
    assert body["papasamya"]["groom"]["total"] == sum(body["papasamya"]["groom"]["per_reference"].values())
    assert body["bhava_milan"]["verdict"] in ("Harmonious", "Mixed", "Challenging")
    assert body["combined_verdict"]["en"] and body["combined_verdict"]["ne"]
    # Dasha sandhi: pick a real MD boundary from groom's tree, 5 days before it.
    # (Build the tree exactly as the engine does — tz-aware birth moment.)
    from zoneinfo import ZoneInfo

    from astro.engine import resolve_place

    _place = resolve_place(dict(SAMPLE))
    _birth = ephemeris.make_local_datetime(
        date(1998, 5, 14), datetime.strptime("06:30", "%H:%M").time(), _place["tz"])
    _moon_lon = ephemeris.planet_longitudes(ephemeris.to_julian_day(_birth))["Moon"]["longitude"]
    tree = dasha_module.vimshottari_tree(
        _birth, _moon_lon, datetime(2027, 1, 1, tzinfo=ZoneInfo("Asia/Kathmandu")))
    boundary = tree["mahadashas"][1]["start"].date()
    mdate = (boundary - timedelta(days=5)).isoformat()
    r2 = client.post("/api/match", json={"groom": a, "bride": bb, "marriage_date": mdate})
    assert r2.json()["dasha_sandhi"]["groom"]["in_window"] is True


def test_pdf_contains_worldclass_sections():
    from astro.pdf import build_html

    html_en = build_html(_sample_bundle(), lang="en")
    for section in ("Bhava Chalit", "Prastara Ashtakavarga", "KP Event Analysis", "Sudarshana Chakra"):
        assert section in html_en, section
    html_ne = build_html(_sample_bundle(), lang="ne")
    for section in ("भाव चलित", "प्रस्तार अष्टकवर्ग", "KP घटना विश्लेषण", "सुदर्शन चक्र"):
        assert section in html_ne, section
