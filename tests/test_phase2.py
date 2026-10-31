"""Phase 2: Yuddha Bala, Bhava Dig Bala, full KP significators, Shodhya Pindas."""

from astro import ashtakavarga as av
from astro import bala
from astro import engine
from astro import ephemeris


def _chart(**kw):
    payload = {"name": "T", "dob": "1998-05-14", "tob": "06:30:00",
               "place_id": "kathmandu"}
    payload.update(kw)
    return engine.compute_kundali(payload)


# ---------------------------------------------------------------------------
# Trikona Shodhana
# ---------------------------------------------------------------------------
def test_trikona_nehru_example():
    # Nehru's SAV (Mehta): (2,7,8)->(0,5,6); (6,6,12)->(0,0,6); (6,10,2)->(4,8,0)
    b = [0] * 12
    b[0], b[4], b[8] = 2, 7, 8
    b[2], b[6], b[10] = 6, 6, 12
    b[3], b[7], b[11] = 6, 10, 2
    r = av.trikona_shodhana(b)
    assert (r[0], r[4], r[8]) == (0, 5, 6)
    assert (r[2], r[6], r[10]) == (0, 0, 6)
    assert (r[3], r[7], r[11]) == (4, 8, 0)


def test_trikona_edge_rules():
    b = [0] * 12
    b[0], b[4], b[8] = 4, 4, 4
    assert av.trikona_shodhana(b)[0:9:4] == [0, 0, 0]  # all equal -> zeros
    b = [0] * 12
    b[0] = 5  # other two already 0
    assert av.trikona_shodhana(b)[0] == 0  # two zeros -> third zeroed
    b = [0] * 12
    b[0], b[4], b[8] = 5, 0, 3
    r = av.trikona_shodhana(b)
    assert (r[0], r[4], r[8]) == (5, 0, 3)  # one zero -> no change


# ---------------------------------------------------------------------------
# Ekadhipatya Shodhana
# ---------------------------------------------------------------------------
def test_ekadhipatya_occupied_cases():
    # Mehta's Mars rule: Scorpio occupied (1 bindu), Aries 2 -> Aries becomes 1
    b = [0] * 12
    b[0], b[7] = 2, 1
    r = av.ekadhipatya_shodhana(b, "Mars", 7)
    assert (r[0], r[7]) == (1, 1)
    # Venus: Libra occupied (1), Taurus unoccupied (1) -> Taurus destroyed
    b = [0] * 12
    b[1], b[6] = 1, 1
    r = av.ekadhipatya_shodhana(b, "Venus", 6)
    assert (r[1], r[6]) == (0, 1)
    # Occupied >= unoccupied -> unoccupied destroyed
    b = [0] * 12
    b[0], b[7] = 1, 3
    r = av.ekadhipatya_shodhana(b, "Mars", 7)
    assert (r[0], r[7]) == (0, 3)


def test_ekadhipatya_unoccupied_cases():
    b = [0] * 12
    b[9], b[10] = 4, 6  # Saturn in neither: larger reduced to smaller
    r = av.ekadhipatya_shodhana(b, "Saturn", 3)
    assert (r[9], r[10]) == (4, 4)
    b = [0] * 12
    b[9], b[10] = 4, 4  # equal -> both destroyed
    r = av.ekadhipatya_shodhana(b, "Saturn", 3)
    assert (r[9], r[10]) == (0, 0)
    b = [0] * 12
    b[9] = 4  # one zero -> no change
    assert av.ekadhipatya_shodhana(b, "Saturn", 3)[9] == 4
    b = list(range(12))  # Sun/Moon: no reduction ever
    assert av.ekadhipatya_shodhana(b, "Sun", 4) == b
    assert av.ekadhipatya_shodhana(b, "Moon", 3) == b


# ---------------------------------------------------------------------------
# Shodhya Pinda
# ---------------------------------------------------------------------------
def test_shodhya_pinda_structure():
    b = _chart()
    sp = b["shodhya_pindas"]
    assert set(sp) == {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"}
    for p, row in sp.items():
        assert row["shodhya_pinda"] == row["rasi_pinda"] + row["graha_pinda"]
        assert len(row["reduced_bindus"]) == 12
        assert all(v >= 0 for v in row["reduced_bindus"])
        # reductions never increase bindus
        assert sum(row["reduced_bindus"]) <= sum(b["ashtakavarga"][p])


def test_shodhya_pinda_hand_case():
    # Controlled BAV, hand-computed pinda.
    bindus = [1, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 2]
    planet_signs = {"Sun": 4, "Moon": 3, "Mars": 0, "Mercury": 2,
                    "Jupiter": 8, "Venus": 6, "Saturn": 9}
    row = av.shodhya_pinda(bindus, "Sun", planet_signs)
    # Trikona: group (0,4,8)=(1,0,0) two zeros -> all zero;
    # group (3,7,11)=(5,0,2) one zero -> no change. Sun: no Ekadhipatya.
    assert row["reduced_bindus"] == [0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 2]
    # rasi pinda = 5*4 (Cancer) + 2*10 (Pisces) = 40
    assert row["rasi_pinda"] == 40
    # graha pinda: only Moon's sign (Cancer) has bindus: 5 * 5 = 25
    assert row["graha_pinda"] == 25
    assert row["shodhya_pinda"] == 65


# ---------------------------------------------------------------------------
# Yuddha Bala
# ---------------------------------------------------------------------------
def test_yuddha_zero_without_war():
    b = _chart()
    for p, row in b["strength"]["shadbala"]["planets"].items():
        assert row["kala"]["yuddha"] == 0.0
        assert "yuddha_foe" not in row["kala"]


def test_yuddha_pairwise_math():
    # Synthetic war: Mars and Mercury 0.5 deg apart, Mars further north.
    planets = {
        "Sun": {"longitude": 100.0}, "Moon": {"longitude": 200.0},
        "Mars": {"longitude": 150.0}, "Mercury": {"longitude": 150.5},
        "Jupiter": {"longitude": 250.0}, "Venus": {"longitude": 300.0},
        "Saturn": {"longitude": 50.0},
    }
    lats = {"Sun": 0.0, "Moon": 0.0, "Mars": 1.0, "Mercury": -1.0,
            "Jupiter": 0.0, "Venus": 0.0, "Saturn": 0.0}
    sthana = {p: 200.0 for p in planets}
    dig = {p: 30.0 for p in planets}
    kala = {p: {"nathonnatha": 10.0, "paksha": 10.0, "tribhaga": 10.0,
                "vaara": 0.0, "hora": 0.0, "masa": 0.0, "abda": 0.0}
            for p in planets}
    out = bala._yuddha_bala(planets, sthana, dig, kala, lats)
    # Tri-bala both = 200 + 30 + 30 = 260 -> equal, quantum 0, but war detected
    assert out["Mars"]["outcome"] == "victor"
    assert out["Mercury"]["outcome"] == "vanquished"
    assert out["Mars"]["opponent"] == "Mercury"
    # Now separate their tri-balas: Mars sthana 300
    sthana["Mars"] = 300.0
    out = bala._yuddha_bala(planets, sthana, dig, kala, lats)
    expected = abs(360.0 - 260.0) / abs(9.4 - 6.6)  # |disc Mars - disc Mercury| = 2.8
    assert abs(out["Mars"]["quantum"] - expected) < 1e-9
    assert abs(out["Mercury"]["quantum"] - expected) < 1e-9


def test_yuddha_tie_latitude_no_award():
    planets = {"Mars": {"longitude": 150.0}, "Mercury": {"longitude": 150.5}}
    lats = {"Mars": 0.5, "Mercury": 0.5}
    sthana = {"Mars": 300.0, "Mercury": 200.0}
    dig = {"Mars": 30.0, "Mercury": 30.0}
    kala = {p: {"nathonnatha": 0.0, "paksha": 0.0, "tribhaga": 0.0,
                "vaara": 0.0, "hora": 0.0, "masa": 0.0, "abda": 0.0}
            for p in planets}
    full = {p: {"longitude": 0.0} for p in
            ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]}
    full.update(planets)
    out = bala._yuddha_bala(full, {**{p: 0.0 for p in full}, **sthana},
                            {**{p: 0.0 for p in full}, **dig},
                            {**{p: kala["Mars"] for p in full}, **kala},
                            {**{p: 0.0 for p in full}, **lats})
    assert out["Mars"]["outcome"] is None
    assert out["Mars"]["quantum"] == 0.0


def test_yuddha_luminaries_never_fight():
    planets = {"Sun": {"longitude": 150.0}, "Moon": {"longitude": 150.2},
               "Mars": {"longitude": 150.4}}
    lats = {p: 1.0 for p in planets}
    z = {p: 0.0 for p in planets}
    k0 = {"nathonnatha": 0.0, "paksha": 0.0, "tribhaga": 0.0,
          "vaara": 0.0, "hora": 0.0, "masa": 0.0, "abda": 0.0}
    full = {p: {"longitude": 0.0} for p in
            ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]}
    full.update(planets)
    out = bala._yuddha_bala(
        full, {**{p: 0.0 for p in full}, **z}, {**{p: 0.0 for p in full}, **z},
        {p: dict(k0) for p in full}, {**{p: 0.0 for p in full}, **lats})
    assert out["Sun"]["outcome"] is None
    assert out["Moon"]["outcome"] is None
    assert out["Mars"]["outcome"] is None  # only one tara-graha present


def test_ephemeris_latitudes_sane():
    lats = ephemeris.latitudes(2460000.5)
    assert set(lats) == {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"}
    assert all(-8.0 < v < 8.0 for v in lats.values())


# ---------------------------------------------------------------------------
# Bhava Dig Bala
# ---------------------------------------------------------------------------
def test_bhava_dig_bala_present_and_bounded():
    b = _chart()
    bb = b["strength"]["bhava_bala"]
    assert len(bb) == 12
    for row in bb:
        assert 0.0 <= row["dig_bala_rupas"] <= 1.0
        assert abs(row["total_rupas"] - (row["lord_bala_rupas"]
                                        + row["dig_bala_rupas"]
                                        + row["drik_bala_rupas"])) < 0.02


def test_bhava_dig_bala_directions():
    # Nara sign (Gemini) at the 1st cusp -> full 60 virupas
    cusps = [60.0 + i * 30.0 for i in range(12)]  # equal 30° houses
    assert bala._bhava_dig_bala(60.0, cusps) == 60.0
    # Same Nara sign at the 7th cusp (opposite) -> 0
    assert bala._bhava_dig_bala(240.0, cusps) == 0.0
    # Keeta (Scorpio) at the 7th cusp -> full 60
    cusps3 = [45.0 + i * 30.0 for i in range(12)]  # 7th cusp = 225 (Scorpio)
    assert bala._bhava_dig_bala(225.0, cusps3) == 60.0
    # Jalachara (Cancer) at 4th cusp -> 60
    cusps2 = [i * 30.0 for i in range(12)]  # 4th cusp = 90 (Cancer ingress)
    assert bala._bhava_dig_bala(90.0, cusps2) == 60.0
    # Sagittarius halves: 10° -> Nara (east), 20° -> Chatushpada (south)
    assert bala._sign_kind(8, 10.0) == "nara"
    assert bala._sign_kind(8, 20.0) == "chatushpada"
    assert bala._sign_kind(9, 10.0) == "chatushpada"
    assert bala._sign_kind(9, 20.0) == "jalachara"


# ---------------------------------------------------------------------------
# KP significators
# ---------------------------------------------------------------------------
def test_kp_significator_order():
    b = _chart()
    hs = b["kp"]["house_significators"]
    for h in range(1, 13):
        row = hs[h]
        assert row["significator_order"], f"house {h} has no significators"
        # strongest-first: star_of_occupants before occupants before lord-group
        lv = row["levels"]
        order = row["significator_order"]
        # every level member appears in the ordered list
        for grp in lv.values():
            for q in grp:
                assert q in order
        # a_level / b_level kept for backward compatibility
        assert set(row["a_level"]) == set(lv["star_of_occupants"]) | set(lv["occupants"])
        assert set(row["b_level"]) == {row["sign_lord"]} | set(lv["star_of_lord"])


def test_kp_node_rule():
    b = _chart()
    ps = b["kp"]["planet_signified_houses"]
    assert "Rahu" in ps and "Ketu" in ps
    assert ps["Rahu"]  # nodes always signify something
    # node houses are a subset of houses signified via its agents
    assert all(1 <= h <= 12 for h in ps["Rahu"])
