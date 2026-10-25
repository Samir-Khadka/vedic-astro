"""Gap-closure program: goldens/invariants for Tajika, Argala,
Ashtottari, Nakshatra deep-dive, Porutham, Lal Kitab completion,
lifetime Sade Sati, gemstone guide and Muhurta v2."""
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from fastapi.testclient import TestClient

from astro import (
    argala as argala_module,
    dasha as dasha_module,
    ephemeris,
    lalkitab as lk_module,
    muhurta as muhurta_module,
    nakshatra as nak_module,
    porutham as porutham_module,
    tajika as tajika_module,
    transits as transits_module,
)
from astro.engine import compute_kundali, compute_match
from astro import pdf as pdf_module
from main import app

client = TestClient(app)
SAMPLE = {"name": "Sample", "dob": "1998-05-14", "tob": "06:30", "place_id": "kathmandu"}
KTM = dict(lat=27.7172, lon=85.3240, tz_name="Asia/Kathmandu")

_bundle = None


def _sample_bundle():
    global _bundle
    if _bundle is None:
        _bundle = compute_kundali(dict(SAMPLE))
    return _bundle


def _sample_planets():
    place = {"lat": 27.7172, "lon": 85.3240, "tz": "Asia/Kathmandu"}
    dt = ephemeris.make_local_datetime(date(1998, 5, 14), time(6, 30), place["tz"])
    jd = ephemeris.to_julian_day(dt)
    return ephemeris.planet_longitudes(jd), jd


# ---------------------------------------------------------------- Tajika
def _synth_planet(lon, speed):
    return {"longitude": lon, "sign": int(lon // 30.0), "degree_in_sign": lon % 30.0,
            "speed": speed, "nakshatra": 0, "pada": 1, "retrograde": speed < 0}


def test_tajika_ithasala_vs_isharpha_by_motion():
    # Jupiter (faster) behind Saturn, closing: Ithasala.
    # Jupiter ahead of Saturn, opening: Isharpha.
    planets = {
        "Jupiter": _synth_planet(100.0, 0.20), "Saturn": _synth_planet(105.0, 0.05),
        "Sun": _synth_planet(200.0, 1.0), "Moon": _synth_planet(250.0, 13.0),
        "Mars": _synth_planet(300.0, 0.5), "Mercury": _synth_planet(20.0, 1.2),
        "Venus": _synth_planet(150.0, 1.1),
    }
    out = tajika_module.tajika_yogas(planets, 0)
    ith = [p for p in out["pairs"] if p["yoga"] == "Ithasala" and set(p["planets"]) == {"Jupiter", "Saturn"}]
    assert len(ith) == 1 and ith[0]["planets"][0] == "Jupiter"
    planets["Jupiter"] = _synth_planet(106.0, 0.20)
    out = tajika_module.tajika_yogas(planets, 0)
    ish = [p for p in out["pairs"] if p["yoga"] == "Isharpha" and set(p["planets"]) == {"Jupiter", "Saturn"}]
    assert len(ish) == 1


def test_tajika_nakta_yamaya_manau():
    # Nakta: A=0deg, B=130deg (no mutual aspect), C=65deg faster aspects both.
    planets = {
        "Sun": _synth_planet(0.0, 0.1), "Mars": _synth_planet(130.0, 0.1),
        "Moon": _synth_planet(65.0, 1.0), "Mercury": _synth_planet(200.0, 1.0),
        "Jupiter": _synth_planet(260.0, 0.2), "Venus": _synth_planet(300.0, 1.1),
        "Saturn": _synth_planet(340.0, 0.05),
    }
    out = tajika_module.tajika_yogas(planets, 0)
    nak = [p for p in out["pairs"] if p["yoga"] == "Nakta" and set(p["planets"]) == {"Sun", "Mars"}]
    assert len(nak) == 1 and nak[0]["via"] == "Moon"
    # Yamaya: A=58deg, B=158deg retrograde, C=60deg slow; both apply to C.
    planets = {
        "Sun": _synth_planet(58.0, 1.0), "Mars": _synth_planet(158.0, -1.0),
        "Moon": _synth_planet(60.0, 0.1), "Mercury": _synth_planet(200.0, 1.0),
        "Jupiter": _synth_planet(260.0, 0.2), "Venus": _synth_planet(300.0, 1.1),
        "Saturn": _synth_planet(340.0, 0.05),
    }
    out = tajika_module.tajika_yogas(planets, 0)
    yam = [p for p in out["pairs"] if p["yoga"] == "Yamaya" and set(p["planets"]) == {"Sun", "Mars"}]
    assert len(yam) == 1 and yam[0]["via"] == "Moon"
    # Manau: Ithasala Jupiter-Saturn spoiled by Mars within orb of Jupiter.
    planets = {
        "Jupiter": _synth_planet(100.0, 0.20), "Saturn": _synth_planet(105.0, 0.05),
        "Mars": _synth_planet(101.0, 0.5), "Sun": _synth_planet(200.0, 1.0),
        "Moon": _synth_planet(250.0, 13.0), "Mercury": _synth_planet(20.0, 1.2),
        "Venus": _synth_planet(150.0, 1.1),
    }
    out = tajika_module.tajika_yogas(planets, 0)
    man = [p for p in out["pairs"] if p["yoga"] == "Manau" and set(p["planets"]) == {"Jupiter", "Saturn"}]
    assert len(man) == 1 and man[0]["spoiler"] == "Mars"


def test_tajika_ikbala_induvara():
    def chart(signs):
        return {p: _synth_planet(s * 30.0 + 5.0, 0.5)
                for p, s in zip(tajika_module.GRAHAS_7, signs)}
    # Lagna Aries: houses = sign+1. Kendra/panaphara only -> Ikbala.
    out = tajika_module.tajika_yogas(chart([0, 1, 3, 4, 6, 7, 9]), 0)
    assert [p["pattern"] for p in out["patterns"]] == ["Ikbala"]
    # Apoklima only -> Induvara.
    out = tajika_module.tajika_yogas(chart([2, 5, 8, 11, 2, 5, 8]), 0)
    assert [p["pattern"] for p in out["patterns"]] == ["Induvara"]


def test_tajika_sahams_day_formula():
    planets = {
        "Sun": _synth_planet(100.0, 1.0), "Moon": _synth_planet(200.0, 13.0),
        "Venus": _synth_planet(50.0, 1.1), "Saturn": _synth_planet(300.0, 0.05),
        "Jupiter": _synth_planet(10.0, 0.2), "Mars": _synth_planet(20.0, 0.5),
        "Mercury": _synth_planet(80.0, 1.2),
    }
    s = tajika_module.saham_points(planets, 0.0, 0, True)
    assert s["Punya"]["sign"] == 3 and abs(s["Punya"]["longitude"] - 100.0) < 1e-9
    assert s["Vivaha"]["sign"] == 3 and abs(s["Vivaha"]["longitude"] - 110.0) < 1e-9
    assert s["Yasas"]["sign"] == 9 and abs(s["Yasas"]["longitude"] - 270.0) < 1e-9
    assert s["Mahatmya"]["sign"] == 2 and abs(s["Mahatmya"]["longitude"] - 80.0) < 1e-9
    s_night = tajika_module.saham_points(planets, 0.0, 0, False)
    assert abs(s_night["Punya"]["longitude"] - 260.0) < 1e-9  # Sun-Moon+Lagna


def test_tajika_panchadhikari_and_fallback():
    # Varsha Lagna 0deg Aries; only Venus (natal Lagna lord) and Sun
    # (triplicity lord, day) aspect the Lagna; Venus scores higher.
    planets = {
        "Venus": _synth_planet(5.0, 1.1), "Mercury": _synth_planet(100.0, 1.2),
        "Mars": _synth_planet(200.0, 0.5), "Moon": _synth_planet(50.0, 13.0),
        "Sun": _synth_planet(300.0, 1.0), "Jupiter": _synth_planet(150.0, 0.2),
        "Saturn": _synth_planet(250.0, 0.05),
    }
    p = tajika_module.panchadhikari(1, 2, 0, 0.0, planets, True)
    assert p["year_lord"] == "Venus" and not p["fallback_to_muntha"]
    qualified = {c["planet"] for c in p["candidates"] if c["aspects_lagna"]}
    assert qualified == {"Venus", "Sun"}
    # Nobody aspects -> Muntha lord default.
    far = {k: _synth_planet(100.0 + i * 30.0, 0.5) for i, k in enumerate(
        ["Venus", "Mercury", "Mars", "Moon", "Sun", "Jupiter", "Saturn"])}
    p2 = tajika_module.panchadhikari(1, 2, 0, 0.0, far, True)
    assert p2["fallback_to_muntha"] and p2["year_lord"] == "Mercury"


# ---------------------------------------------------------------- Argala
def _houses(planets_signs):
    return {p: ((s - 0) % 12) + 1 for p, s in planets_signs.items()}


def test_argala_house1_and_ketu_reversal():
    ph = _houses({"Sun": 1, "Moon": 3, "Mars": 10, "Mercury": 11, "Jupiter": 9,
                  "Venus": 2, "Saturn": 0, "Rahu": 4, "Ketu": 5})
    h1 = argala_module.argala_for_house(1, ph)
    assert {a["planet"] for a in h1["argala"]} == {"Sun", "Moon", "Mars", "Rahu"}
    assert {v["planet"] for v in h1["virodhargala"]} == {"Mercury", "Jupiter", "Venus"}
    assert h1["verdict"] == "argala"  # 4 supporters > 3 obstructers
    # Ketu in house 6: for house 7 it is 12th-from -> reversed Argala.
    assert any(a["planet"] == "Ketu" for a in argala_module.argala_for_house(7, ph)["argala"])
    # For house 5 it is 2nd-from -> reversed obstruction.
    assert any(v["planet"] == "Ketu" for v in argala_module.argala_for_house(5, ph)["virodhargala"])


def test_argala_three_malefics_in_3rd():
    ph = _houses({"Sun": 2, "Mars": 2, "Saturn": 2, "Moon": 0, "Mercury": 5,
                  "Jupiter": 6, "Venus": 7, "Rahu": 8, "Ketu": 9})
    h1 = argala_module.argala_for_house(1, ph)
    assert h1["malefic_argala_in_3rd"] is True
    assert {"Sun", "Mars", "Saturn"} <= {a["planet"] for a in h1["argala"]}
    assert not any(v["planet"] in ("Sun", "Mars", "Saturn") for v in h1["virodhargala"])


def test_argala_full_sample_counts():
    b = _sample_bundle()
    arg = b["argala"]
    assert len(arg["by_house"]) == 12
    assert arg["prevailing_count"] + arg["obstructed_count"] <= 12
    assert all(p in arg["by_planet"] for p in ("Sun", "Moon", "Ketu"))


# ---------------------------------------------------------------- Ashtottari
def test_ashtottari_sums_and_blocks_cover():
    assert sum(dasha_module.ASHTOTTARI_YEARS.values()) == 108
    covered = [n for _lord, blocks in dasha_module.ASHTOTTARI_BLOCKS for n in blocks]
    assert sorted(covered) == list(range(27))
    assert "Ketu" not in dasha_module.ASHTOTTARI_SEQUENCE
    # Abhijit division: Capricorn 6deg40m-10deg53m20s -> Saturn.
    d = dasha_module.ashtottari_division(276.9)
    assert d["division"] == "Abhijit" and d["lord"] == "Saturn"
    # Rohini -> Venus block; Jyeshtha -> Mercury block.
    assert dasha_module.ashtottari_division(48.0)["lord"] == "Venus"
    assert dasha_module.ashtottari_division(236.78)["lord"] == "Mercury"


def test_ashtottari_sample_tree_and_antis():
    planets, _jd = _sample_planets()
    birth_dt = ephemeris.make_local_datetime(date(1998, 5, 14), time(6, 30), "Asia/Kathmandu")
    tree = dasha_module.ashtottari_tree(birth_dt, planets["Moon"]["longitude"],
                                        datetime.now(ZoneInfo("Asia/Kathmandu")))
    assert tree["mahadashas"][0]["lord"] == "Mercury"
    assert abs(tree["balance_years"] - 4.11) < 0.05
    for md in tree["mahadashas"]:
        assert abs(sum(a["years"] for a in md["antardashas"]) - md["years"]) < 1e-6
    cur = tree["current"]
    assert cur and cur["mahadasha"]["start"] <= cur["at"] < cur["mahadasha"]["end"]
    b = _sample_bundle()
    assert b["ashtottari"]["cycle_years"] == 108
    assert b["ashtottari"]["current"]["mahadasha"]["lord"] == cur["mahadasha"]["lord"]


def test_ashtottari_applicability_both_ways():
    planets = {p: {"sign": 0} for p in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")}
    planets["Rahu"] = {"sign": 3}
    planets["Mars"] = {"sign": 0}  # Lagna lord (Aries) in Aries
    ok = dasha_module.ashtottari_applicability(planets, 0, True, "Krishna")
    assert ok["rahu_condition"] is True and ok["day_night_paksha_condition"] is True and ok["applies"] is True
    bad = dasha_module.ashtottari_applicability(planets, 0, True, "Shukla")
    assert bad["day_night_paksha_condition"] is False and bad["applies"] is False


# ---------------------------------------------------------------- Nakshatra deep-dive
def test_nava_tara_and_tarabala():
    # Natal Jyeshtha (17): Bharani count 12 -> tara 3 Vipat, cycle 2, caution.
    t = nak_module.tara_of(17, 1)
    assert (t["count"], t["tara"], t["tara_en"], t["verdict"], t["cycle"]) == (12, 3, "Vipata", "caution", 2)
    nt = nak_module.nava_tara(17)
    assert len(nt["taras"]) == 27
    assert sum(1 for r in nt["taras"] if r["verdict"] == "caution") == 9
    assert nt["taras"][17]["tara"] == 1  # Janma to itself


def test_chandrabala_positions():
    assert nak_module.chandrabala(7, 11)["position"] == 5
    assert nak_module.chandrabala(7, 11)["verdict"] == "neutral"
    assert nak_module.chandrabala(7, 2)["position"] == 8
    assert nak_module.chandrabala(7, 2)["verdict"] == "avoid"
    assert nak_module.chandrabala(7, 7)["verdict"] == "favourable"


def test_avasthas_sample_and_rules():
    av = nak_module.avastha("Sun", 0, 29.21)
    assert av["balaadi"] == "Mrita" and av["jagratadi"] == "Jagrat"
    av2 = nak_module.avastha("Moon", 7, 26.78)
    assert av2["balaadi"] == "Bala" and av2["jagratadi"] == "Sushupti"
    assert nak_module.avastha("Mars", 4, 15.0)["balaadi"] == "Yuva"
    b = _sample_bundle()
    assert len(b["nakshatra_deep"]["avasthas"]["planets"]) == 9


# ---------------------------------------------------------------- Porutham
def test_porutham_hand_computed_pairs():
    # Groom Ashwini (Horse/Deva/Pada, Aries) + bride Jyeshtha (Deer/Rakshasa/Pada, Scorpio).
    p = porutham_module.porutham({"moon_sign": 0, "moon_nakshatra": 0},
                                 {"moon_sign": 7, "moon_nakshatra": 17})
    by = {r["porutham"]: r["score"] for r in p["breakdown"]}
    assert by == {"Dina": 3.0, "Gana": 0.0, "Mahendra": 0.0, "Sthree Deergha": 2.0,
                  "Yoni": 2.0, "Rasi": 0.0, "Rasyadhipati": 5.0, "Vasya": 2.0,
                  "Rajju": 0.0, "Vedha": 0.0}
    assert p["total"] == 14.0 and p["rajju_dosha"] is True and p["vedha_present"] is True
    # Groom Rohini (Serpent/Manushya/Kanta, Taurus) + bride Uttara Phalguni (Cow/Manushya/Udara, Leo).
    p2 = porutham_module.porutham({"moon_sign": 1, "moon_nakshatra": 3},
                                  {"moon_sign": 4, "moon_nakshatra": 11})
    assert p2["total"] == 23.0 and p2["rajju_dosha"] is False and p2["vedha_present"] is False
    assert sum(r["score"] for r in p2["breakdown"]) == p2["total"]
    assert p2["max"] == 36


def test_porutham_via_match_endpoint():
    r = client.post("/api/match", json={
        "groom": {"dob": "1998-05-14", "tob": "06:30", "place_id": "kathmandu"},
        "bride": {"dob": "2000-01-01", "tob": "10:00", "place_id": "kathmandu"}})
    assert r.status_code == 200
    po = r.json()["porutham"]
    assert po["total"] == sum(x["score"] for x in po["breakdown"])
    assert len(po["breakdown"]) == 10


# ---------------------------------------------------------------- Lal Kitab
def test_lal_kitab_rin_detection():
    khana = {"Sun": 2, "Moon": 7, "Rahu": 2, "Mercury": 1, "Venus": 12,
             "Mars": 10, "Jupiter": 9, "Saturn": 8, "Ketu": 3}
    assert lk_module._rin_detected("Stree Rin", khana) is True
    assert lk_module._rin_detected("Bhratri Rin", khana) is True
    assert lk_module._rin_detected("Zulm Rin", khana) is True
    assert lk_module._rin_detected("Ajanma Rin", khana) is True
    khana2 = dict(khana, Mercury=3)
    assert lk_module._rin_detected("Kanya Rin", khana2) is True
    assert lk_module._rin_detected("Kudrati Rin", khana) is None
    b = _sample_bundle()
    assert sum(1 for r in b["lal_kitab"]["rin"] if r["detected"] is not None) == 8


def test_lal_kitab_teva_types():
    khana = {"Sun": 4, "Saturn": 7, "Moon": 1, "Mars": 2, "Mercury": 3,
             "Jupiter": 5, "Venus": 6, "Rahu": 8, "Ketu": 9}
    # 10th khana vacant -> Andha; Sun 4 + Saturn 7 -> Adha Andha.
    types = {m["type"] for m in lk_module.teva_types(khana)["matched"]}
    assert {"Andha", "Adha Andha"} <= types
    khana2 = dict(khana, Saturn=11, Sun=1)
    assert "Dharmi" in {m["type"] for m in lk_module.teva_types(khana2)["matched"]}
    # Nabaligh: kendras hold only Mercury/Saturn/Rahu/Ketu (or empty).
    khana3 = {"Sun": 2, "Moon": 3, "Mars": 5, "Mercury": 1, "Jupiter": 6,
              "Venus": 8, "Saturn": 4, "Rahu": 7, "Ketu": 10}
    assert "Nabaligh" in {m["type"] for m in lk_module.teva_types(khana3)["matched"]}


def test_lal_kitab_dasha_cycle():
    assert sum(y for _p, y in lk_module.LK_DASHA_SEQUENCE) == 35
    birth_dt = ephemeris.make_local_datetime(date(1998, 5, 14), time(6, 30), "Asia/Kathmandu")
    d = lk_module.lal_kitab_dasha(birth_dt, datetime.now(ZoneInfo("Asia/Kathmandu")))
    assert d["cycle_years"] == 35
    for p in d["periods"]:
        assert abs(sum(a["years"] for a in p["antardashas"]) - p["years"]) < 0.01
    for a, b_ in zip(d["periods"], d["periods"][1:]):
        assert a["end"] == b_["start"]
    assert d["current"]["planet"] == "Rahu"


# ---------------------------------------------------------------- Sade Sati lifetime
def test_sade_sati_lifetime_golden():
    planets, jd = _sample_planets()
    now = datetime.now(ZoneInfo("Asia/Kathmandu"))
    lt = transits_module.sade_sati_lifetime(planets["Moon"]["sign"], jd,
                                            ephemeris.to_julian_day(now))
    assert lt["count"] == 3
    first = lt["periods"][0]
    assert (first["start"], first["peak_start"], first["setting_start"], first["end"]) == (
        "2011-11-15", "2014-11-02", "2017-01-26", "2020-01-24")
    assert first["status"] == "past" and lt["periods"][1]["status"] == "future"
    for p in lt["periods"]:
        assert p["start"] <= p["peak_start"] <= p["setting_start"] <= p["end"]
    b = _sample_bundle()
    assert b["sade_sati_lifetime"]["count"] == 3


# ---------------------------------------------------------------- Vimshottari depth
def test_vimshottari_sookshma_prana_chain():
    b = _sample_bundle()
    cur = b["dasha"]["current"]
    assert cur["sookshma"] is not None and cur["prana"] is not None
    assert cur["pratyantardasha"]["start"] <= cur["sookshma"]["start"] < cur["pratyantardasha"]["end"]
    assert cur["sookshma"]["start"] <= cur["prana"]["start"] < cur["sookshma"]["end"]


# ---------------------------------------------------------------- Gemstones
def test_gemstone_guide_all_planets_and_caution():
    b = _sample_bundle()
    g = b["report"]["gemstones"]
    assert len(g["planets"]) == 9
    by = {e["planet"]: e for e in g["planets"]}
    assert by["Sun"]["stone"]["en"] == "Ruby" and by["Saturn"]["rudraksha"]["mukhi"] == 7
    assert by["Sun"]["weight_carat_approx"].startswith("~4.")
    dusthana_flagged = [e for e in g["planets"] if e["caution"]]
    assert dusthana_flagged  # at least one dusthana lord exists in the sample chart


# ---------------------------------------------------------------- Muhurta v2
def test_panchaka_flag_consistent_with_panchang():
    # A day whose Moon is in Revati must be Panchaka; check the rule
    # against the panchang itself rather than a memorised date.
    from astro.ephemeris import sunrise_sunset
    from astro.panchang import panchang_at
    found = None
    d = date(2026, 10, 26)
    for _ in range(40):
        pk = muhurta_module.panchaka_check(d, **KTM)
        rise, _set = sunrise_sunset(d, KTM["lat"], KTM["lon"], KTM["tz_name"])
        moment = rise or datetime.combine(d, time(6, 0), tzinfo=ZoneInfo("Asia/Kathmandu"))
        p = panchang_at(moment, KTM["lat"], KTM["lon"], KTM["tz_name"])
        expect = p["nakshatra_index"] in (23, 24, 25, 26) or (
            p["nakshatra_index"] == 22 and p["nakshatra_pada"] in (3, 4))
        assert pk["active"] == expect
        if pk["active"]:
            found = (d, pk)
            break
        d += timedelta(days=1)
    assert found is not None
    assert found[1]["type"] in (None, "Mrithyu", "Agni", "Raja", "Chora", "Roga")


def test_muhurta_v2_election_factors():
    d = muhurta_module.day_muhurta(date(2026, 10, 26), **KTM, birth_moon_sign=7)
    assert d["chandra_bala"] is not None
    assert d["election_score"] == (d["score"] + sum(f["points"] for f in d["election_factors"]))
    assert d["panchaka"]["active"] in (True, False)
    assert d["lagna_strength"]["verdict"] in ("strong", "moderate", "weak")
    r = muhurta_module.muhurta_range(date(2026, 10, 26), date(2026, 11, 1), **KTM,
                                     birth_moon_sign=7)
    scores = [x["election_score"] for x in r["best_election"]]
    assert scores == sorted(scores, reverse=True)


def test_muhurta_endpoint_personalised():
    r = client.get("/api/muhurta", params={
        "date_from": "2026-10-26", "date_to": "2026-11-01", "activity": "marriage",
        "place_id": "kathmandu", "birth_moon_sign": 7,
        "birth_dob": "1998-05-14", "birth_tob": "06:30", "birth_place_id": "kathmandu"})
    assert r.status_code == 200
    body = r.json()
    assert len(body["best_election"]) == 5
    assert all(x["dasha_suitability"] for x in body["days"])
    assert all(x["chandra_bala"] for x in body["days"])


# ---------------------------------------------------------------- Bundle + PDF
def test_bundle_new_keys_present():
    b = _sample_bundle()
    for key in ("argala", "nakshatra_deep", "ashtottari", "ashtottari_applicability",
                "sade_sati_lifetime", "lal_kitab_dasha"):
        assert key in b, key
    assert b["report"]["varshphal"][0]["tajika"]["pairs"]
    assert b["report"]["varshphal"][0]["panchadhikari"]["year_lord"]
    assert set(b["report"]["varshphal"][0]["sahams"]) == {"Punya", "Vivaha", "Yasas", "Mahatmya"}


def test_pdf_has_new_sections_both_languages():
    b = _sample_bundle()
    titles = {
        "en": ("Ashtottari Dasha", "Lifetime Sade Sati", "Gemstone & Rudraksha Guide",
               "Lal Kitab Dasha", "Panchadhikari Year Lord"),
        "ne": ("अष्टोत्तरी दशा", "आजीवन साढेसाती", "रत्न र रुद्राक्ष",
               "लाल किताब दशा", "पञ्चाधिकारी वर्ष स्वामी"),
    }
    for lang, lang_titles in titles.items():
        html = pdf_module.build_html(b, lang=lang)
        for anchor in ("id='argala'", "id='nakshatra'") + lang_titles:
            assert anchor in html, (lang, anchor)
