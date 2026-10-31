"""Phase 3 dashas: Narayana, Shodshottari, Mudda, Kalachakra."""
from datetime import datetime, timezone

from astro import dasha_phase3 as p3
from astro.names import SIGNS_EN


def _planets(**overrides):
    """Minimal planets dict: sign + degree_in_sign + longitude."""
    base = {}
    for i, name in enumerate(["Sun", "Moon", "Mars", "Mercury", "Jupiter",
                              "Venus", "Saturn", "Rahu", "Ketu"]):
        sign, deg = overrides.get(name, (i % 12, 10.0))
        base[name] = {"sign": sign, "degree_in_sign": deg,
                      "longitude": sign * 30.0 + deg}
    return base


# ---------------------------------------------------------------------------
# Narayana: Padha Krama sequences (published examples)
# ---------------------------------------------------------------------------

def test_padha_krama_movable():
    assert [SIGNS_EN[s] for s in p3._padha_krama_sequence(0, True)] == [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra",
        "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    assert [SIGNS_EN[s] for s in p3._padha_krama_sequence(3, False)] == [
        "Cancer", "Gemini", "Taurus", "Aries", "Pisces", "Aquarius",
        "Capricorn", "Sagittarius", "Scorpio", "Libra", "Virgo", "Leo"]


def test_padha_krama_fixed():
    seq = [SIGNS_EN[s] for s in p3._padha_krama_sequence(4, True)]
    assert seq[:5] == ["Leo", "Capricorn", "Gemini", "Scorpio", "Aries"]
    assert len(set(seq)) == 12
    seq = [SIGNS_EN[s] for s in p3._padha_krama_sequence(1, False)]
    assert seq[:6] == ["Taurus", "Sagittarius", "Cancer", "Aquarius",
                       "Virgo", "Aries"]
    assert len(set(seq)) == 12


def test_padha_krama_dual():
    seq = [SIGNS_EN[s] for s in p3._padha_krama_sequence(5, True)]
    assert seq[:8] == ["Virgo", "Capricorn", "Taurus", "Gemini", "Libra",
                       "Aquarius", "Pisces", "Cancer"]
    assert len(set(seq)) == 12
    seq = [SIGNS_EN[s] for s in p3._padha_krama_sequence(2, False)]
    assert seq[:8] == ["Gemini", "Aquarius", "Libra", "Virgo", "Taurus",
                       "Capricorn", "Sagittarius", "Leo"]
    assert len(set(seq)) == 12


def test_narayana_duration_rules():
    # Lord in own sign -> 12 years. Mars in Aries, dasha of Aries.
    planets = _planets(Mars=(0, 10.0))
    assert p3.narayana_duration(planets, 0) == 12
    # Aries dasha, Mars in Gemini (forward count 3) -> 2 years.
    planets = _planets(Mars=(2, 10.0))
    assert p3.narayana_duration(planets, 0) == 2
    # Mercury in Virgo (exalted+own): Virgo dasha -> 12, no bonus.
    planets = _planets(Mercury=(5, 10.0))
    assert p3.narayana_duration(planets, 5) == 12
    # Gemini dasha, Mercury in Virgo: count 4 -> 3 years, and the
    # Mercury-in-Virgo exception means NO exaltation +1 either.
    assert p3.narayana_duration(planets, 2) == 3


def test_narayana_second_cycle_is_12_minus():
    birth = datetime(2000, 1, 1, tzinfo=timezone.utc)
    planets = _planets()
    n = p3.narayana_periods(birth, planets, 0, "Sun")
    assert len(n["mahadashas"]) == 24
    first = [m["years"] for m in n["mahadashas"][:12]]
    second = [m["years"] for m in n["mahadashas"][12:]]
    assert all(abs(a + b - 12.0) < 1e-9 for a, b in zip(first, second))
    # Antardashas: 12 equal parts.
    md = n["mahadashas"][0]
    assert len(md["antardashas"]) == 12
    assert abs(sum(a["years"] for a in md["antardashas"]) - md["years"]) < 1e-9


def test_stronger_sign_atmakaraka_wins():
    planets = _planets(Sun=(0, 20.0))  # Atmakaraka in Aries
    assert p3.stronger_sign(planets, 0, 6, "Sun") == 0
    assert p3.stronger_sign(planets, 6, 0, "Sun") == 0


def test_stronger_sign_more_planets():
    planets = _planets(Sun=(0, 5.0), Moon=(0, 6.0), Mars=(6, 7.0),
                       Saturn=(9, 10.0))
    # Aries has 2, Libra has 1 -> Aries stronger.
    # (Atmakaraka Rahu sits in neither sign, so rule 1 is neutral.)
    assert p3.stronger_sign(planets, 0, 6, "Rahu") == 0


# ---------------------------------------------------------------------------
# Shodshottari
# ---------------------------------------------------------------------------

def test_shodshottari_seed_pushya():
    birth = datetime(2000, 1, 1, tzinfo=timezone.utc)
    # Pushya = index 7 -> Sun.
    st = p3.shodshottari_tree(birth, 100.0)
    assert st["mahadashas"][0]["lord"] == "Sun"
    # Ashwini = index 0 -> Ketu.
    st = p3.shodshottari_tree(birth, 5.0)
    assert st["mahadashas"][0]["lord"] == "Ketu"
    # Full cycle = 116 years, lords cycle from the starting lord.
    total = sum(m["years"] for m in st["mahadashas"])
    assert abs(total - 116.0) < 1e-9
    i0 = p3.SHODSHOTTARI_SEQUENCE.index("Ketu")
    expect = [p3.SHODSHOTTARI_SEQUENCE[(i0 + k) % 8] for k in range(8)]
    assert [m["lord"] for m in st["mahadashas"]] == expect


def test_shodshottari_applicability():
    # Aries 5 deg = Sun's hora; Shukla -> applies.
    ap = p3.shodshottari_applicability(0, 5.0, "Shukla")
    assert ap["applies"] and ap["hora_lord"] == "Sun"
    # Same but Krishna -> not.
    ap = p3.shodshottari_applicability(0, 5.0, "Krishna")
    assert not ap["applies"]
    # Taurus 5 deg = Moon's hora; Krishna -> applies.
    ap = p3.shodshottari_applicability(1, 5.0, "Krishna")
    assert ap["applies"] and ap["hora_lord"] == "Moon"


# ---------------------------------------------------------------------------
# Mudda
# ---------------------------------------------------------------------------

def test_mudda_rajiv_gandhi_formula():
    # (completed 40 + nakshatra 11 - 2) = 49; 49 % 9 = 4 -> Rahu.
    r = (40 + 11 - 2) % 9
    assert r == 4
    assert p3.MUDDA_SEQUENCE[r - 1] == "Rahu"
    # Durations sum to 360 ritual days.
    assert sum(p3.MUDDA_DAYS_360.values()) == 360


def test_mudda_structure():
    birth = datetime(1990, 1, 1, tzinfo=timezone.utc)
    md = p3.mudda_dasha(birth, 100.0, 280.0,
                        now=datetime(2020, 6, 1, tzinfo=timezone.utc))
    assert len(md["periods"]) == 9
    # Antardashas: 9 per MD, first is the MD planet, sums to MD days.
    for per in md["periods"]:
        assert len(per["antardashas"]) == 9
        assert per["antardashas"][0]["planet"] == per["planet"]
        total = sum(a["days"] for a in per["antardashas"])
        assert abs(total - per["days"]) < 1e-6


# ---------------------------------------------------------------------------
# Kalachakra
# ---------------------------------------------------------------------------

def test_kalachakra_table_sums():
    for group, padas in p3._KC_TABLE.items():
        for pada, (seq, param) in padas.items():
            total = sum(p3._KALACHAKRA_SIGN_YEARS[s] for s in seq)
            assert total == param, (group, pada)
            assert len(seq) == 9


def test_kalachakra_deha_jiva_match_sjc_table():
    expected = {
        "savya-right": {1: (0, 8), 2: (9, 2), 3: (1, 2), 4: (3, 11)},
        "savya-left": {1: (7, 11), 2: (10, 5), 3: (6, 5), 4: (3, 8)},
        "apasavya-left": {1: (8, 3), 2: (5, 6), 3: (5, 10), 4: (11, 7)},
        "apasavya-right": {1: (11, 3), 2: (2, 1), 3: (2, 9), 4: (8, 0)},
    }
    for group, padas in p3._KC_TABLE.items():
        for pada, (seq, _) in padas.items():
            assert p3._kc_deha_jiva(group, seq) == expected[group][pada]


def test_kalachakra_groups_cover_27():
    all_nak = sorted(list(p3._KC_SAVYA_RIGHT) + list(p3._KC_SAVYA_LEFT) +
                     list(p3._KC_APASAVYA_LEFT) + list(p3._KC_APASAVYA_RIGHT))
    assert all_nak == list(range(27))


def test_kalachakra_shatabhisha_example():
    # SJC: Moon Aquarius 19d58'49" -> Shatabhisha pada-4, opens Aries.
    birth = datetime(2000, 1, 1, tzinfo=timezone.utc)
    kc = p3.kalachakra_tree(birth, 319.98, now=birth)
    assert kc["birth_group"] == "apasavya-right"
    assert kc["birth_pada"] == 4
    assert kc["mahadashas"][0]["sign"] == 0  # Aries
    assert kc["mahadashas"][0]["years"] < 1.0
    assert kc["deha"] == 8 and kc["jiva"] == 0  # Sg / Ar


def test_kalachakra_antar_proportions():
    birth = datetime(2000, 1, 1, tzinfo=timezone.utc)
    kc = p3.kalachakra_tree(birth, 100.0, now=birth)
    md = kc["mahadashas"][0]
    assert len(md["antardashas"]) == 9
    total = sum(a["years"] for a in md["antardashas"])
    assert abs(total - md["years"]) < 1e-9
