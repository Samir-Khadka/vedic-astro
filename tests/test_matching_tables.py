"""Classical-table pins for astro/matching.py (Ashtakoota Guna Milan).

The tables were previously verified only by reading; these tests pin them
against the published standard tables so a future edit cannot silently
shift a score.

- Graha Maitri: the full 7x7 lord matrix (5/4/3/1/0.5/0 scale).
  2026-11-23: friend-enemy was 0 (published 1) and neutral-enemy was 1
  (published 0.5) — 14 of 49 pairs wrong.
- Vashya: the 5-group matrix and the sign-group assignment.
- Yoni / Gana / Tara / Bhakoot / Varna / Nadi: spot checks + totals.
"""
from astro.matching import (
    GANA_MATRIX, VARNA_OF_SIGN, VASHYA_MATRIX, VASHYA_OF_SIGN,
    _bhakoot_points, _maitri_points, _tara_points, _yoni_points,
    guna_milan,
)

PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

# Published Graha Maitri matrix, rows/cols in PLANETS order
# (astroveeda.in / anytimeastro.com — identical tables).
MAITRI_MATRIX = {
    "Sun":     [5, 5, 5, 4, 5, 0, 0],
    "Moon":    [5, 5, 4, 1, 4, 0.5, 0.5],
    "Mars":    [5, 4, 5, 0.5, 5, 3, 0.5],
    "Mercury": [4, 1, 0.5, 5, 0.5, 5, 4],
    "Jupiter": [5, 4, 5, 0.5, 5, 0.5, 3],
    "Venus":   [0, 0.5, 3, 5, 0.5, 5, 5],
    "Saturn":  [0, 0.5, 0.5, 4, 3, 5, 5],
}


def test_maitri_full_matrix():
    for i, groom in enumerate(PLANETS):
        for j, bride in enumerate(PLANETS):
            assert _maitri_points(groom, bride) == MAITRI_MATRIX[groom][j], (
                f"{groom} vs {bride}")


def test_maitri_mixed_cases():
    # Friend-enemy: Moon sees Mercury as friend, Mercury sees Moon as enemy.
    assert _maitri_points("Moon", "Mercury") == 1.0
    # Neutral-enemy: Mars sees Mercury as enemy, Mercury sees Mars as neutral.
    assert _maitri_points("Mars", "Mercury") == 0.5
    # Same lord and mutual friends are full marks.
    assert _maitri_points("Sun", "Sun") == 5.0
    assert _maitri_points("Sun", "Moon") == 5.0


def test_vashya_groups_cover_all_signs():
    assert set(VASHYA_OF_SIGN) == set(range(12))
    assert VASHYA_OF_SIGN[2] == "Manav"      # Gemini
    assert VASHYA_OF_SIGN[8] == "Manav"      # Sagittarius (the archer)
    assert VASHYA_OF_SIGN[3] == "Jalchar"    # Cancer
    assert VASHYA_OF_SIGN[0] == "Chatushpad"  # Aries
    assert VASHYA_OF_SIGN[4] == "Vanchar"    # Leo
    assert VASHYA_OF_SIGN[7] == "Keet"       # Scorpio
    # Same group is 2, cross-group follows the published matrix.
    assert VASHYA_MATRIX["Manav"][1] == 2
    assert VASHYA_MATRIX["Manav"][0] == 0    # Manav vs Chatushpad
    assert VASHYA_MATRIX["Chatushpad"][1] == 0
    assert VASHYA_MATRIX["Keet"][4] == 2


def test_yoni_points():
    assert _yoni_points("Horse", "Horse") == 4.0
    assert _yoni_points("Horse", "Buffalo") == 0.0   # extreme enemies
    assert _yoni_points("Dog", "Cat") == 1.0         # enemies
    assert _yoni_points("Cow", "Horse") == 3.0       # friendly
    assert _yoni_points("Horse", "Dog") == 2.0       # neutral


def test_gana_matrix():
    assert GANA_MATRIX["Deva"]["Deva"] == 6
    assert GANA_MATRIX["Deva"]["Manushya"] == 5
    assert GANA_MATRIX["Deva"]["Rakshasa"] == 1
    assert GANA_MATRIX["Manushya"]["Rakshasa"] == 0
    assert GANA_MATRIX["Rakshasa"]["Rakshasa"] == 6


def test_tara_points_both_ways():
    # Same nakshatra: both directions favourable (counts 1 and 1).
    assert _tara_points(0, 0) == 3.0
    # Ashwini (0) -> Bharani (1): counts 2 and 27 -> both favourable.
    assert _tara_points(0, 1) == 3.0
    # A 3rd-tara (Vipat) one way only: 0 -> 2 counts 3 (bad) / 26 (good).
    assert _tara_points(0, 2) == 1.5


def test_bhakoot_dosha_pairs():
    # Dosha pairs are relative positions: 6-8 (b = g+5), 9-5 (b = g+8),
    # 12-2 (b = g+11), each both ways.
    for g, b in [(0, 5), (5, 0), (0, 8), (8, 0), (0, 11), (11, 0)]:
        assert _bhakoot_points(g, b) == 0.0, (g, b)
    assert _bhakoot_points(0, 0) == 7.0
    assert _bhakoot_points(0, 2) == 7.0  # 3rd-11th: not a dosha pair


def test_guna_milan_total_is_sum_and_max_36():
    groom = {"moon_sign": 0, "moon_nakshatra": 0}   # Aries / Ashwini
    bride = {"moon_sign": 0, "moon_nakshatra": 0}
    r = guna_milan(groom, bride)
    assert r["max"] == 36
    assert r["total"] == sum(p["score"] for p in r["breakdown"])
    assert r["nadi_dosha"] is True  # same nakshatra -> same Nadi
    assert r["total"] <= 36


def test_guna_milan_varna_direction():
    # Groom Brahmin (Cancer) + bride Shudra (Gemini): full Varna point.
    r = guna_milan({"moon_sign": 3, "moon_nakshatra": 0},
                   {"moon_sign": 2, "moon_nakshatra": 0})
    varna = next(p for p in r["breakdown"] if p["koota"] == "Varna")
    assert varna["score"] == 1.0
    # Reversed: groom Shudra + bride Brahmin scores 0.
    r2 = guna_milan({"moon_sign": 2, "moon_nakshatra": 0},
                    {"moon_sign": 3, "moon_nakshatra": 0})
    varna2 = next(p for p in r2["breakdown"] if p["koota"] == "Varna")
    assert varna2["score"] == 0.0
    assert VARNA_OF_SIGN[3] == 0 and VARNA_OF_SIGN[2] == 3
