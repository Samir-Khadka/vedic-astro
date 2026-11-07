"""Direct tests for the three classical modules that had zero coverage:
astro/tajika.py (annual-chart Tajika yogas, Sahams, Panchadhikari),
astro/porutham.py (South Indian Dashakoota matching) and
astro/argala.py (Jaimini Argala).

Every expectation below was hand-computed from the rules stated in
each module's docstring and cross-checked by running the code.
"""
import pytest

from astro import argala as argala_mod
from astro import porutham as porutham_mod
from astro import tajika as tajika_mod


def _pl(lon, sign, speed=1.0):
    return {"longitude": lon, "speed": speed, "sign": sign}


# ---------------------------------------------------------------------------
# Tajika: aspect geometry + applying/separating
# ---------------------------------------------------------------------------

def test_aspect_distance_basics():
    assert tajika_mod._aspect_distance(10.0, 70.0) == (0.0, 60.0)   # exact sextile
    assert tajika_mod._aspect_distance(10.0, 100.0) == (0.0, 90.0)  # exact square
    assert tajika_mod._aspect_distance(10.0, 75.0)[0] == pytest.approx(5.0)
    assert tajika_mod._aspect_distance(10.0, 80.0)[0] == pytest.approx(10.0)
    assert tajika_mod._in_aspect(10.0, 75.0) is True    # 5 deg inside the 8-deg orb
    assert tajika_mod._in_aspect(10.0, 80.0) is False   # 10 deg outside it


def test_applying_fast_moon_must_not_overshoot():
    # REGRESSION: the Moon at 10 deg moving +13/day toward Jupiter at 75
    # perfects the 60-deg sextile in ~0.4 days, so it is APPLYING.
    # The old full-day extrapolation carried it through the aspect and
    # misread the pair as separating (Isharpha + Gairi-Kambula).
    assert tajika_mod._applying(10.0, 13.0, 75.0, 0.1) is True
    # 7 deg short: the old code got this one right; keep it applying.
    assert tajika_mod._applying(10.0, 13.0, 77.0, 0.1) is True
    # Separating: the sextile already perfected (sep 55 and shrinking).
    assert tajika_mod._applying(10.0, 13.0, 65.0, 0.1) is False
    # At the exact aspect any movement is separation (standing convention).
    assert tajika_mod._applying(10.0, 13.0, 70.0, 0.1) is False
    # Retrograde faster planet moving toward the aspect still applies.
    assert tajika_mod._applying(100.0, -1.0, 35.0, 0.1) is True
    assert tajika_mod._applying(100.0, -1.0, 45.0, 0.1) is False


def _ithasala_chart():
    """Moon applies to Jupiter; Mars aspects the Moon (Manau spoiler)."""
    return {
        "Sun": _pl(200.0, 6, 1.0), "Moon": _pl(10.0, 0, 13.0),
        "Mars": _pl(100.0, 3, 0.5), "Mercury": _pl(250.0, 8, 1.5),
        "Jupiter": _pl(75.0, 2, 0.1), "Venus": _pl(300.0, 10, 1.2),
        "Saturn": _pl(330.0, 11, 0.05),
    }


def test_tajika_ithasala_kambula_manau():
    y = tajika_mod.tajika_yogas(_ithasala_chart(), 0)
    by_pair = {}
    for p in y["pairs"]:
        by_pair.setdefault((p["yoga"], tuple(p["planets"])), p)
    assert ("Ithasala", ("Moon", "Jupiter")) in by_pair
    assert by_pair[("Ithasala", ("Moon", "Jupiter"))]["favourable"] is True
    # Moon in Ithasala -> Kambula (fortune); Mars spoils it -> Manau.
    assert ("Kambula", ("Moon", "Jupiter")) in by_pair
    manau = by_pair[("Manau", ("Moon", "Jupiter"))]
    assert manau["spoiler"] == "Mars"
    assert manau["favourable"] is False
    # The other two Moon pairs separate -> Gairi-Kambula, no Kambula.
    kambula = [p for p in y["pairs"] if p["yoga"] == "Kambula"]
    gairi = [p for p in y["pairs"] if p["yoga"] == "Gairi-Kambula"]
    assert len(kambula) == 1 and len(gairi) == 2
    assert y["orb_degrees"] == 8.0


def test_tajika_nakta_via_faster_planet():
    pl = {
        "Sun": _pl(200.0, 6, 1.0), "Moon": _pl(10.0, 0, 13.0),
        "Mars": _pl(150.0, 5, 0.5), "Mercury": _pl(100.0, 3, 1.5),
        "Jupiter": _pl(70.0, 2, 0.1), "Venus": _pl(250.0, 8, 1.2),
        "Saturn": _pl(300.0, 10, 0.05),
    }
    y = tajika_mod.tajika_yogas(pl, 0)
    nakta = {(tuple(p["planets"]), p["via"]) for p in y["pairs"] if p["yoga"] == "Nakta"}
    # Mercury-Jupiter and Mercury-Venus do not aspect each other, but the
    # faster Moon aspects both.
    assert (("Mercury", "Jupiter"), "Moon") in nakta
    assert (("Mercury", "Venus"), "Moon") in nakta


def test_tajika_yamaya_via_common_slower_planet():
    pl = {
        "Sun": _pl(200.0, 6, 1.0), "Moon": _pl(35.0, 1, 13.0),
        "Mars": _pl(250.0, 8, 0.5), "Mercury": _pl(185.0, 6, 1.5),
        "Jupiter": _pl(100.0, 3, 0.1), "Venus": _pl(300.0, 10, 1.2),
        "Saturn": _pl(330.0, 11, 0.05),
    }
    y = tajika_mod.tajika_yogas(pl, 0)
    yamaya = [p for p in y["pairs"] if p["yoga"] == "Yamaya"]
    assert len(yamaya) == 1
    assert yamaya[0]["planets"] == ["Moon", "Mercury"]
    assert yamaya[0]["via"] == "Jupiter"
    # Both legs must themselves be Ithasala (this failed before the
    # _applying fix: the Moon leg read as Isharpha, so no Yamaya fired).
    ithasala = {tuple(p["planets"]) for p in y["pairs"] if p["yoga"] == "Ithasala"}
    assert ("Moon", "Jupiter") in ithasala
    assert ("Mercury", "Jupiter") in ithasala


def test_tajika_ikbala_and_induvara():
    kendra = {
        "Sun": _pl(5.0, 0, 1.0), "Moon": _pl(40.0, 1, 13.0),
        "Mars": _pl(100.0, 3, 0.5), "Mercury": _pl(130.0, 4, 1.5),
        "Jupiter": _pl(190.0, 6, 0.1), "Venus": _pl(220.0, 7, 1.2),
        "Saturn": _pl(280.0, 9, 0.05),
    }
    assert [p["pattern"] for p in tajika_mod.tajika_yogas(kendra, 0)["patterns"]] == ["Ikbala"]
    apoklima = {
        "Sun": _pl(70.0, 2, 1.0), "Moon": _pl(160.0, 5, 13.0),
        "Mars": _pl(250.0, 8, 0.5), "Mercury": _pl(340.0, 11, 1.5),
        "Jupiter": _pl(75.0, 2, 0.1), "Venus": _pl(165.0, 5, 1.2),
        "Saturn": _pl(255.0, 8, 0.05),
    }
    assert [p["pattern"] for p in tajika_mod.tajika_yogas(apoklima, 0)["patterns"]] == ["Induvara"]


def test_saham_points_day_and_night():
    pl = {
        "Sun": _pl(200.0, 6, 1.0), "Moon": _pl(10.0, 0, 13.0),
        "Mars": _pl(150.0, 5, 0.5), "Mercury": _pl(100.0, 3, 1.5),
        "Jupiter": _pl(70.0, 2, 0.1), "Venus": _pl(250.0, 8, 1.2),
        "Saturn": _pl(300.0, 10, 0.05),
    }
    day = tajika_mod.saham_points(pl, 100.0, 3, True)
    # Day Punya = Moon - Sun + Lagna = 10 - 200 + 100 = 270 (Capricorn).
    assert day["Punya"]["longitude"] == 270.0
    assert day["Punya"]["sign_en"] == "Capricorn" and day["Punya"]["lord"] == "Saturn"
    assert day["Punya"]["house"] == 7 and day["Punya"]["strength"] == "strong"
    # Vivaha = Venus - Saturn + Lagna = 50 (Taurus); Yasas = 260
    # (Sagittarius); Mahatmya = Punya - Mars + Lagna = 220 (Scorpio).
    assert day["Vivaha"]["longitude"] == 50.0 and day["Vivaha"]["sign_en"] == "Taurus"
    assert day["Yasas"]["longitude"] == 260.0 and day["Yasas"]["sign_en"] == "Sagittarius"
    assert day["Mahatmya"]["longitude"] == 220.0 and day["Mahatmya"]["sign_en"] == "Scorpio"
    # Night Punya flips to Sun - Moon + Lagna = 290 (Capricorn, 20 deg in).
    night = tajika_mod.saham_points(pl, 100.0, 3, False)
    assert night["Punya"]["longitude"] == 290.0
    assert night["Punya"]["degree_in_sign"] == 20.0


def _panch_chart():
    # Sun in Libra (sign 6) makes Venus the Dina-Ratri lord; Venus in
    # Libra is own-sign + kendra, tying Mars at 25.
    return {
        "Sun": _pl(200.0, 6, 1.0), "Moon": _pl(210.0, 7, 13.0),
        "Mars": _pl(10.0, 0, 0.5), "Mercury": _pl(140.0, 4, 1.5),
        "Jupiter": _pl(300.0, 10, 0.1), "Venus": _pl(190.0, 6, 1.2),
        "Saturn": _pl(320.0, 10, 0.05),
    }


def test_panchadhikari_tie_breaks_to_earliest_officer():
    # Mars (natal Lagna lord, own + kendra = 25) ties Venus
    # (Dina-Ratri lord, own + kendra = 25); earliest officer wins.
    p = tajika_mod.panchadhikari(0, 4, 0, 10.0, _panch_chart(), True)
    assert p["year_lord"] == "Mars"
    assert p["fallback_to_muntha"] is False
    scores = {c["officer"]["en"]: c["score"] for c in p["candidates"]}
    assert scores["Natal Lagna lord"] == 25
    assert scores["Dina-Ratri lord"] == 25
    assert len(p["candidates"]) == 5


def test_panchadhikari_falls_back_to_muntha_lord():
    pl = _panch_chart()
    pl["Mars"] = _pl(45.0, 1, 0.5)    # 35 deg off the Lagna: no aspect
    pl["Sun"] = _pl(200.0, 6, 1.0)    # 10 deg off the 180 aspect: no aspect
    pl["Venus"] = _pl(45.0, 1, 1.2)   # Dina-Ratri lord (Sun in Libra): no aspect
    p = tajika_mod.panchadhikari(0, 4, 0, 10.0, pl, True)
    assert p["fallback_to_muntha"] is True
    assert p["year_lord"] == "Sun"  # Muntha (Leo) lord
    assert all(c["score"] == 0 for c in p["candidates"])


# ---------------------------------------------------------------------------
# Porutham: 36-point Dashakoota
# ---------------------------------------------------------------------------

def _porutham_scores(result):
    return [p["score"] for p in result["breakdown"]]


def test_porutham_hand_computed_total():
    # Groom Ashwini/Aries, bride Bharani/Aries.
    r = porutham_mod.porutham(
        {"moon_sign": 0, "moon_nakshatra": 0},
        {"moon_sign": 0, "moon_nakshatra": 1},
    )
    assert r["max"] == 36
    assert sum(p["max"] for p in r["breakdown"]) == 36
    # Dina 3, Gana 3 (Deva-Manushya), Mahendra 0, Sthree Deergha 0,
    # Yoni 3 (Horse-Elephant friends), Rasi 7, Rasyadhipati 5 (both Mars),
    # Vasya 0, Rajju 5, Vedha 2.
    assert _porutham_scores(r) == [3.0, 3.0, 0.0, 0.0, 3.0, 7.0, 5.0, 0.0, 5.0, 2.0]
    assert r["total"] == 28.0
    assert r["verdict_en"] == "Excellent match"
    assert r["rajju_dosha"] is False and r["vedha_present"] is False


def test_porutham_rajju_dosha_overrides_total():
    r = porutham_mod.porutham(
        {"moon_sign": 0, "moon_nakshatra": 0},
        {"moon_sign": 0, "moon_nakshatra": 0},
    )
    assert r["rajju_dosha"] is True
    assert r["total"] == 25.0  # would otherwise be "Acceptable"
    assert r["verdict_en"].startswith("Rajju Dosha")


def test_porutham_vedha_and_yoni_tiers():
    # Ashwini-Jyeshtha is a Vedha pair.
    r = porutham_mod.porutham(
        {"moon_sign": 0, "moon_nakshatra": 0},
        {"moon_sign": 7, "moon_nakshatra": 17},
    )
    assert r["vedha_present"] is True
    assert [p["score"] for p in r["breakdown"] if p["porutham"] == "Vedha"] == [0.0]
    # Bitter enemies (Horse-Buffalo) score 0; mild enemies
    # (Serpent-Rat: Rohini vs Magha) score 1.
    bitter = porutham_mod.porutham(
        {"moon_sign": 0, "moon_nakshatra": 0},
        {"moon_sign": 5, "moon_nakshatra": 12},
    )
    assert [p["score"] for p in bitter["breakdown"] if p["porutham"] == "Yoni"] == [0.0]
    mild = porutham_mod.porutham(
        {"moon_sign": 1, "moon_nakshatra": 3},
        {"moon_sign": 4, "moon_nakshatra": 9},
    )
    assert [p["score"] for p in mild["breakdown"] if p["porutham"] == "Yoni"] == [1.0]


def test_porutham_vasya_directions():
    # Pisces controls Capricorn: groom Pisces / bride Capricorn = full.
    full = porutham_mod.porutham(
        {"moon_sign": 11, "moon_nakshatra": 26},
        {"moon_sign": 9, "moon_nakshatra": 20},
    )
    assert [p["score"] for p in full["breakdown"] if p["porutham"] == "Vasya"] == [2.0]
    # Reverse direction alone = half.
    half = porutham_mod.porutham(
        {"moon_sign": 9, "moon_nakshatra": 20},
        {"moon_sign": 11, "moon_nakshatra": 26},
    )
    assert [p["score"] for p in half["breakdown"] if p["porutham"] == "Vasya"] == [1.0]


def test_porutham_failing_factors():
    # Dina fails when the bride-to-groom count leaves remainder 3:
    # groom Ashwini (0), bride Uttara Bhadrapada (25) -> count 3.
    dina = porutham_mod.porutham(
        {"moon_sign": 0, "moon_nakshatra": 0},
        {"moon_sign": 11, "moon_nakshatra": 25},
    )
    assert [p["score"] for p in dina["breakdown"] if p["porutham"] == "Dina"] == [0.0]
    # Gana fails when Rakshasa mixes with another group.
    gana = porutham_mod.porutham(
        {"moon_sign": 0, "moon_nakshatra": 0},
        {"moon_sign": 1, "moon_nakshatra": 2},
    )
    assert [p["score"] for p in gana["breakdown"] if p["porutham"] == "Gana"] == [0.0]
    # Rasi fails at the 6th: groom Aries from bride Libra.
    rasi = porutham_mod.porutham(
        {"moon_sign": 0, "moon_nakshatra": 0},
        {"moon_sign": 7, "moon_nakshatra": 13},
    )
    assert [p["score"] for p in rasi["breakdown"] if p["porutham"] == "Rasi"] == [0.0]


def test_porutham_tables_cover_all_nakshatras():
    assert set(porutham_mod.GANA_OF_NAK) == set(range(27))
    assert set(porutham_mod.RAJJU_OF_NAK) == set(range(27))
    assert all(list(porutham_mod.GANA_OF_NAK.values()).count(g) == 9
               for g in ("Deva", "Manushya", "Rakshasa"))
    # Thirteen Vedha pairs; Chitra (13) neither gives nor receives Vedha.
    assert len(porutham_mod.VEDHA_PAIRS) == 13
    assert not any(13 in pair for pair in porutham_mod.VEDHA_PAIRS)


# ---------------------------------------------------------------------------
# Argala: Jaimini intervention
# ---------------------------------------------------------------------------

def test_argala_basic_verdicts():
    # Jupiter (2nd) + Mars (4th) support the Lagna against Saturn (12th).
    row = argala_mod.argala_for_house(1, {"Jupiter": 2, "Mars": 4, "Saturn": 12})
    assert row["verdict"] == "argala"
    assert [r["planet"] for r in row["argala"]] == ["Mars", "Jupiter"]
    assert [r["planet"] for r in row["virodhargala"]] == ["Saturn"]
    # A lone obstructor obstructs; equal numbers still obstruct.
    assert argala_mod.argala_for_house(1, {"Saturn": 12})["verdict"] == "obstructed"
    assert argala_mod.argala_for_house(1, {"Jupiter": 2, "Saturn": 12})["verdict"] == "obstructed"
    # A planet in the house itself (offset 1) neither supports nor obstructs.
    assert argala_mod.argala_for_house(1, {"Jupiter": 1})["verdict"] == "none"


def test_argala_ketu_reversal_and_extended():
    # Ketu is counted backwards: 3rd supports, 2nd obstructs.
    assert argala_mod.argala_for_house(1, {"Ketu": 3})["verdict"] == "argala"
    assert argala_mod.argala_for_house(1, {"Ketu": 2})["verdict"] == "obstructed"
    ketu9 = argala_mod.argala_for_house(1, {"Ketu": 9})
    assert ketu9["verdict"] == "argala"
    assert ketu9["argala"][0]["extended"] is True
    assert ketu9["argala"][0]["ketu_reversed"] is True
    ketu5 = argala_mod.argala_for_house(1, {"Ketu": 5})
    assert ketu5["verdict"] == "obstructed"
    assert ketu5["virodhargala"][0]["extended"] is True
    # Normal extended rule: 5th supports, 9th obstructs.
    assert argala_mod.argala_for_house(1, {"Venus": 5})["argala"][0]["extended"] is True
    assert argala_mod.argala_for_house(1, {"Venus": 9})["virodhargala"][0]["extended"] is True
    # Rahu is NOT reversed: 3rd obstructs.
    assert argala_mod.argala_for_house(1, {"Rahu": 3})["verdict"] == "obstructed"


def test_argala_three_malefics_in_3rd():
    row = argala_mod.argala_for_house(1, {"Sun": 3, "Mars": 3, "Saturn": 3})
    assert row["malefic_argala_in_3rd"] is True
    assert row["verdict"] == "argala"
    assert row["virodhargala"] == []
    # Two malefics are not enough.
    row2 = argala_mod.argala_for_house(1, {"Sun": 3, "Mars": 3})
    assert row2["malefic_argala_in_3rd"] is False
    assert row2["verdict"] == "obstructed"


def test_argala_full_counts_and_planet_view():
    planets = {p: {"sign": s} for p, s in
               {"Sun": 0, "Moon": 1, "Mars": 3, "Mercury": 4, "Jupiter": 2,
                "Venus": 7, "Saturn": 11, "Rahu": 5, "Ketu": 8}.items()}
    full = argala_mod.argala_full(planets, 0)
    assert len(full["by_house"]) == 12
    assert (full["prevailing_count"] + full["obstructed_count"]
            + sum(1 for r in full["by_house"] if r["verdict"] == "none")) == 12
    # Jupiter sits in the 3rd house; it gives Argala to houses 2, 5, 11, 12.
    jup = full["by_planet"]["Jupiter"]
    assert jup["house"] == 3
    assert jup["argala_to_houses"] == [2, 5, 11, 12]
