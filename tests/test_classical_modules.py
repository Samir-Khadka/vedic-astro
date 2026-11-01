"""Coverage for the classical computation modules that previously had no
direct tests: yogas, aspects, prastara, sudarshana, chalit, nakshatra and
kp_events. Each test pins a classical invariant or a documented rule so a
future refactor cannot silently change the astrology."""
from __future__ import annotations

import pytest

from astro import aspects as asp
from astro import chalit as cha
from astro import kp_events as kpe
from astro import nakshatra as nak
from astro import prastara as pra
from astro import sudarshana as sud
from astro import yogas as yog
from astro.charts import house_of


def _planets(**overrides):
    """Nine-graha fixture; every planet defaults to Aries (0)."""
    base = {p: {"sign": 0} for p in
            ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu")}
    for name, sign in overrides.items():
        base[name]["sign"] = sign
    return base


# ---------------------------------------------------------------- yogas

class TestDetectYogas:
    def test_ruuchaka_mahapurusha(self):
        # Mars in Aries (own) in a kendra from an Aries lagna.
        ys = yog.detect_yogas(_planets(Mars=0), 0)
        assert any("Ruchaka" in y["name"] for y in ys)

    def test_no_mahapurusha_when_not_kendra(self):
        # Mars in Aries but in the 2nd house from a Taurus lagna.
        ys = yog.detect_yogas(_planets(Mars=0), 1)
        assert not any("Ruchaka" in y["name"] for y in ys)

    def test_gajakesari(self):
        # Jupiter in the 4th from the Moon.
        ys = yog.detect_yogas(_planets(Moon=5, Jupiter=8), 0)
        assert any(y["name"] == "Gajakesari Yoga" for y in ys)

    def test_budha_aditya(self):
        ys = yog.detect_yogas(_planets(Sun=3, Mercury=3), 0)
        assert any(y["name"] == "Budha-Aditya Yoga" for y in ys)

    def test_chandra_mangala_conjunction(self):
        ys = yog.detect_yogas(_planets(Moon=0, Mars=0), 0)
        assert any(y["name"] == "Chandra-Mangala Yoga" for y in ys)

    def test_chandra_mangala_mutual_kendra(self):
        ys = yog.detect_yogas(_planets(Moon=0, Mars=3), 0)
        assert any(y["name"] == "Chandra-Mangala Yoga" for y in ys)

    def test_kemadruma_isolated_moon(self):
        # No other graha in 2/12/kendra from the Moon (sign 5).
        p = _planets(Moon=5, Sun=0, Mars=1, Mercury=3, Jupiter=7,
                     Venus=9, Saturn=10)
        ys = yog.detect_yogas(p, 0)
        assert any(y["name"] == "Kemadruma Yoga" for y in ys)

    def test_kemadruma_cancelled_by_kendra_planet(self):
        # Venus in the 4th from the Moon cancels the isolation.
        p = _planets(Moon=5, Sun=0, Mars=1, Mercury=3, Jupiter=7,
                     Venus=8, Saturn=10)
        ys = yog.detect_yogas(p, 0)
        assert not any(y["name"] == "Kemadruma Yoga" for y in ys)

    def test_dhana_same_lord(self):
        # Pisces lagna: Mars rules both the 2nd and the 9th.
        ys = yog.detect_yogas(_planets(), 11)
        assert any(y["name"] == "Dhana Yoga" and "rules both the 2nd and 9th houses" in y["basis"]
                   for y in ys)

    def test_dhana_conjunction(self):
        # Aries lagna: 2nd lord Venus conjoins 5th lord Sun.
        ys = yog.detect_yogas(_planets(Venus=3, Sun=3), 0)
        assert any(y["name"] == "Dhana Yoga" and "conjoins" in y["basis"] for y in ys)

    def test_dhana_parivartana(self):
        # Aries lagna: Venus (2nd lord) in Leo, Sun (5th lord) in Taurus.
        ys = yog.detect_yogas(_planets(Venus=4, Sun=1), 0)
        assert any(y["name"] == "Dhana Yoga" and "Exchange" in y["basis"] for y in ys)

    def test_raj_yoga_conjunction(self):
        # Aries lagna: kendra lord Venus conjoins trikona lord Sun.
        ys = yog.detect_yogas(_planets(Venus=3, Sun=3), 0)
        assert any(y["name"] == "Raj Yoga" and "conjoins" in y["basis"] for y in ys)

    def test_raj_yoga_parivartana_through_second_ruled_house(self):
        # Taurus lagna: Sun (4th lord) in Virgo, Mercury (5th lord) in
        # Leo. Virgo is Mercury's SECOND ruled sign (Gemini is first),
        # so the old first-house-only check missed this exchange.
        p = _planets(Sun=5, Mercury=4, Moon=0, Mars=0, Jupiter=0,
                     Venus=0, Saturn=0)
        ys = yog.detect_yogas(p, 1)
        assert any(y["name"] == "Raj Yoga" and "Exchange" in y["basis"] for y in ys)

    def test_no_duplicate_yogas(self):
        p = _planets(Sun=3, Moon=0, Mars=0, Mercury=3, Jupiter=8,
                     Venus=3, Saturn=9)
        ys = yog.detect_yogas(p, 0)
        keys = [(y["name"], y["basis"]) for y in ys]
        assert len(keys) == len(set(keys))


# ---------------------------------------------------------------- aspects

class TestAspects:
    def test_special_aspect_offsets(self):
        assert asp.aspect_offsets("Mars") == (4, 7, 8)
        assert asp.aspect_offsets("Jupiter") == (5, 7, 9)
        assert asp.aspect_offsets("Saturn") == (3, 7, 10)

    def test_default_seventh_aspect(self):
        for p in ("Sun", "Moon", "Mercury", "Venus", "Rahu", "Ketu"):
            assert asp.aspect_offsets(p) == (7,)

    def test_aspected_signs_mars(self):
        p = _planets(Mars=0)
        assert asp.aspected_signs("Mars", p) == [3, 6, 7]

    def test_planets_aspected_by(self):
        p = _planets(Jupiter=2, Mars=8, Venus=10)
        hit = asp.planets_aspected_by("Jupiter", p)
        # Jupiter at sign 2 aspects 6, 8, 10.
        assert set(hit) == {"Mars", "Venus"}

    def test_aspecting_planets(self):
        p = {"Saturn": {"sign": 0}, "Moon": {"sign": 2}}
        # Saturn at 0 aspects 2, 6, 9; Moon at 2 aspects 8.
        assert asp.aspecting_planets(2, p) == ["Saturn"]
        assert asp.aspecting_planets(8, p) == ["Moon"]
        assert asp.aspecting_planets(5, p, exclude="Saturn") == []

    def test_conjunct_planets(self):
        p = _planets(Sun=4, Mercury=4, Moon=5)
        assert asp.conjunct_planets("Sun", p) == ["Mercury"]

    def test_houses_aspected_by(self):
        p = _planets(Jupiter=2)
        # Jupiter aspects signs 6, 8, 10 -> houses 7, 9, 11 from Aries.
        assert asp.houses_aspected_by("Jupiter", p, 0) == [7, 9, 11]

    def test_relation_between_all_positions(self):
        expected = {
            1: "kendra", 2: "2nd", 3: "upachaya", 4: "kendra",
            5: "trikona", 6: "dusthana", 7: "kendra", 8: "dusthana",
            9: "trikona", 10: "kendra", 11: "upachaya", 12: "dusthana",
        }
        for rel, want in expected.items():
            got = asp.relation_between(0, (rel - 1) % 12)
            assert got == want, f"rel {rel}: got {got}, want {want}"


# ---------------------------------------------------------------- prastara

class TestPrastara:
    def _chart(self):
        planets = {p: {"sign": s} for p, s in
                   zip(("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"),
                       (4, 3, 0, 5, 8, 1, 9))}
        return pra.prastara(planets, 0)

    def test_column_sums_reproduce_bav(self):
        out = self._chart()
        for planet in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
            grid, bav = out[planet]["grid"], out[planet]["bav"]
            for s in range(12):
                assert sum(grid[c][s] for c in pra.CONTRIBUTORS) == bav[s]

    def test_sarvashtakavarga_total_is_337(self):
        out = self._chart()
        total = sum(sum(out[p]["bav"]) for p in
                    ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"))
        assert total == 337

    def test_reductions_never_increase(self):
        out = self._chart()
        for planet in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
            bav, red = out[planet]["bav"], out[planet]["reduced"]
            assert all(r <= b for r, b in zip(red, bav))
            assert out[planet]["reduced_total"] == sum(red)

    def test_sav_reduced_is_column_sum(self):
        out = self._chart()
        for s in range(12):
            expect = sum(out[p]["reduced"][s] for p in
                         ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"))
            assert out["Sarvashtakavarga_reduced"][s] == expect

    def test_trikona_reduce_subtracts_minimum(self):
        bav = [0] * 12
        bav[0], bav[4], bav[8] = 5, 3, 4  # triad (1,5,9) from own sign
        red = pra._trikona_reduce(bav, 0)
        assert (red[0], red[4], red[8]) == (2, 0, 1)

    def test_trikona_reduce_skips_zero_triad(self):
        bav = [0] * 12
        bav[0], bav[4] = 5, 3  # third of the triad is zero: no reduction
        red = pra._trikona_reduce(bav, 0)
        assert (red[0], red[4], red[8]) == (5, 3, 0)

    def test_ekadhipatya_reduce_zeroes_empty_pair(self):
        bav = [0] * 12
        bav[0] = 6  # Aries occupied, Scorpio (7) empty -> both zeroed
        red = pra._ekadhipatya_reduce(bav)
        assert red[0] == 0 and red[7] == 0

    def test_ekadhipatya_reduce_subtracts_smaller(self):
        bav = [0] * 12
        bav[0], bav[7] = 6, 4
        red = pra._ekadhipatya_reduce(bav)
        assert (red[0], red[7]) == (2, 0)


# ---------------------------------------------------------------- sudarshana

class TestSudarshana:
    def test_houses_match_house_of(self):
        p = _planets(Sun=4, Moon=3, Mars=0, Jupiter=8)
        out = sud.sudarshana(p, 0)
        assert out["rings"] == {"lagna": 0, "moon": 3, "sun": 4}
        for name, row in out["planets"].items():
            assert row["lagna_house"] == house_of(p[name]["sign"], 0)
            assert row["moon_house"] == house_of(p[name]["sign"], 3)
            assert row["sun_house"] == house_of(p[name]["sign"], 4)

    def test_triple_agreement_when_rings_coincide(self):
        p = _planets(Sun=4, Moon=4, Mars=7)
        out = sud.sudarshana(p, 4)
        for row in out["planets"].values():
            assert row["agreement"] == "triple"
        assert len(out["confirmed"]) == len(p)

    def test_confirmed_lists_repeated_house(self):
        # Lagna 0, Moon 0, Sun 6: a planet in sign 0 is in house 1 from
        # lagna and moon but house 7 from the sun -> double, house 1.
        p = _planets(Moon=0, Sun=6, Mars=0)
        out = sud.sudarshana(p, 0)
        mars = next(c for c in out["confirmed"] if c["planet"] == "Mars")
        assert mars == {"planet": "Mars", "house": 1, "level": "double"}

    def test_varied_when_rings_disagree(self):
        p = _planets(Moon=3, Sun=6, Mars=0)
        out = sud.sudarshana(p, 1)
        mars = out["planets"]["Mars"]
        assert mars["agreement"] == "varied"
        assert not any(c["planet"] == "Mars" for c in out["confirmed"])


# ---------------------------------------------------------------- chalit

class TestChalit:
    def test_boundaries_need_12_cusps(self):
        with pytest.raises(ValueError):
            cha.house_boundaries([0.0] * 11)

    def test_uniform_cusps_give_midpoint_boundaries(self):
        cusps = [i * 30.0 for i in range(12)]
        bounds = cha.house_boundaries(cusps)
        # boundary[i] = midpoint of cusp[i-1] and cusp[i]; the first one
        # wraps: midpoint(330, 0) = 345.
        assert bounds == [345.0] + [15.0 + i * 30.0 for i in range(11)]

    def test_longitudes_partition_the_zodiac(self):
        cusps = [i * 30.0 for i in range(12)]
        bounds = cha.house_boundaries(cusps)
        seen = {cha.chalit_house(float(d), bounds) for d in range(0, 360, 5)}
        assert seen == set(range(1, 13))

    def test_planet_near_cusp_can_shift_house(self):
        # Cusp 0 at 28 deg: the midpoint boundary opens house 1 at 29,
        # so a planet at 0 deg falls in house 12, not house 1.
        cusps = [28.0 + i * 30.0 for i in range(12)]
        bounds = cha.house_boundaries(cusps)
        assert cha.chalit_house(0.0, bounds) == 12
        assert cha.chalit_house(29.5, bounds) == 1

    def test_bhava_chalit_reports_rashi_comparison(self):
        # Uniform cusps: house 1 spans 345 -> 15 deg, house 2 spans 15 -> 45.
        planets = {"Sun": {"sign": 0, "longitude": 20.0},
                   "Mars": {"sign": 0, "longitude": 10.0}}
        cusps = [i * 30.0 for i in range(12)]
        out = cha.bhava_chalit(planets, cusps, 0)
        assert out["houses"]["Sun"]["rashi_house"] == 1
        assert out["houses"]["Sun"]["chalit_house"] == 2
        assert out["houses"]["Sun"]["shifted"] is True
        assert "Sun" in out["shifted"]
        assert out["houses"]["Mars"]["chalit_house"] == 1
        assert out["houses"]["Mars"]["shifted"] is False


# ---------------------------------------------------------------- nakshatra

class TestNakshatra:
    def test_tara_first_cycle(self):
        t = nak.tara_of(0, 0)
        assert (t["count"], t["tara"], t["cycle"]) == (1, 1, 1)
        assert t["tara_en"] == "Janma" and t["verdict"] == "favourable"

    def test_tara_caution(self):
        t = nak.tara_of(0, 2)  # count 3 -> Vipata
        assert t["tara"] == 3 and t["verdict"] == "caution"
        assert t["strength_note"] == "full caution"

    def test_tara_second_cycle(self):
        t = nak.tara_of(0, 9)  # count 10 -> Janma again, cycle 2
        assert (t["tara"], t["cycle"]) == (1, 2)

    def test_tara_last_count(self):
        t = nak.tara_of(0, 26)  # count 27 -> Parama Mitra, cycle 3
        assert (t["count"], t["tara"], t["cycle"]) == (27, 9, 3)
        assert t["verdict"] == "favourable"

    def test_nava_tara_covers_27_stars(self):
        nt = nak.nava_tara(5)
        assert len(nt["taras"]) == 27
        # Ashwini (0) counted from Magha (5): count 23 -> tara 5, cycle 3.
        first = nt["taras"][0]
        assert (first["count"], first["tara"], first["cycle"]) == (23, 5, 3)

    def test_chandrabala_positions(self):
        assert nak.chandrabala(3, 3)["verdict"] == "favourable"   # 1st
        assert nak.chandrabala(3, 4)["verdict"] == "neutral"      # 2nd
        assert nak.chandrabala(3, 10)["verdict"] == "avoid"       # 8th: Ashtama
        assert nak.chandrabala(3, 11)["verdict"] == "neutral"     # 9th: split sources
        assert nak.chandrabala(3, 2)["verdict"] == "avoid"        # 12th

    def test_avastha_balaadi_odd_sign(self):
        a = nak.avastha("Sun", 4, 3.0)   # Leo, first 6-degree part
        assert a["balaadi"] == "Bala" and a["balaadi_strength"] == 0.25
        assert a["jagratadi"] == "Jagrat"  # Sun in own sign

    def test_avastha_balaadi_even_sign_reversed(self):
        a = nak.avastha("Moon", 1, 3.0)  # Taurus, first part -> Mrita
        assert a["balaadi"] == "Mrita" and a["balaadi_strength"] == 0.0

    def test_avastha_balaadi_last_part(self):
        a = nak.avastha("Sun", 4, 27.0)
        assert a["balaadi"] == "Mrita"

    def test_avastha_enemy_sign_sleeps(self):
        # Saturn in Leo: the Sun (lord) is Saturn's enemy -> Sushupti.
        a = nak.avastha("Saturn", 4, 10.0)
        assert a["sign_relation"] == "enemy" and a["jagratadi"] == "Sushupti"

    def test_avastha_debilitated_sleeps(self):
        # Saturn in Aries is debilitated (exaltation Libra - 6 signs).
        a = nak.avastha("Saturn", 0, 10.0)
        assert a["sign_relation"] == "debilitated" and a["jagratadi"] == "Sushupti"

    def test_avastha_nodes_indeterminate(self):
        a = nak.avastha("Rahu", 0, 10.0)
        assert a["sign_relation"] == "unknown" and a["jagratadi"] == "Swapna"

    def test_avasthas_for_chart_covers_nine(self):
        planets = {p: {"sign": 0, "degree_in_sign": 10.0} for p in
                   ("Sun", "Moon", "Mars", "Mercury", "Jupiter",
                    "Venus", "Saturn", "Rahu", "Ketu")}
        out = nak.avasthas_for_chart(planets)
        assert len(out["planets"]) == 9


# ---------------------------------------------------------------- kp_events

class TestKpEvents:
    def _kp(self, sub_lords, sig):
        cusps = [{"house": h, "sub_lord": sub_lords.get(h, "Saturn")}
                 for h in (2, 4, 5, 7, 10, 12)]
        return {"planet_signified_houses": sig, "cusps": cusps}

    def _dasha(self):
        return {"current": {"mahadasha": {"lord": "Jupiter"},
                            "antardasha": {"lord": "Venus"}}}

    def test_negating_houses_textbook(self):
        assert kpe._negating([2, 7, 11]) == [1, 6, 10]

    def test_negating_excludes_favourable_overlap(self):
        assert kpe._negating([2, 6, 10, 11]) == [1, 5, 9]

    def test_verdict_promised(self):
        kp = self._kp({7: "Venus"}, {"Venus": [2, 7, 11]})
        out = kpe.kp_event_analysis(kp, self._dasha(),
                                    {"Jupiter": 0, "Saturn": 0}, 0)
        assert out["marriage"]["verdict"] == "Promised"
        assert out["marriage"]["fav_hits"] == [2, 7, 11]

    def test_verdict_mixed(self):
        kp = self._kp({7: "Venus"}, {"Venus": [2, 6, 7]})
        out = kpe.kp_event_analysis(kp, self._dasha(),
                                    {"Jupiter": 0, "Saturn": 0}, 0)
        assert out["marriage"]["verdict"] == "Mixed"

    def test_verdict_not_indicated(self):
        kp = self._kp({7: "Venus"}, {"Venus": [6]})
        out = kpe.kp_event_analysis(kp, self._dasha(),
                                    {"Jupiter": 0, "Saturn": 0}, 0)
        assert out["marriage"]["verdict"] == "Not indicated"

    def test_verdict_weak(self):
        kp = self._kp({7: "Venus"}, {"Venus": [3]})
        out = kpe.kp_event_analysis(kp, self._dasha(),
                                    {"Jupiter": 0, "Saturn": 0}, 0)
        assert out["marriage"]["verdict"] == "Weak"

    def test_dasha_support(self):
        kp = self._kp({7: "Venus"}, {"Venus": [2, 7], "Jupiter": [11]})
        out = kpe.kp_event_analysis(kp, self._dasha(),
                                    {"Jupiter": 0, "Saturn": 0}, 0)
        assert out["marriage"]["dasha_support"] is True
        assert out["marriage"]["dasha_hits"] == [
            {"lord": "Jupiter", "houses": [11]},
            {"lord": "Venus", "houses": [2, 7]},
        ]

    def test_transit_support(self):
        # Lagna Aries: Jupiter transiting sign 6 sits in the 7th house.
        kp = self._kp({7: "Venus"}, {"Venus": [2]})
        out = kpe.kp_event_analysis(kp, self._dasha(),
                                    {"Jupiter": 6, "Saturn": 0}, 0)
        assert out["marriage"]["transit_hits"] == {"Jupiter": 7}
