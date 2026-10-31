"""Ashtakavarga — benefic point (bindu) system.

BENEFIC[planet][contributor] = the houses (1-based, counted from the
contributor's own sign position) in which the contributor donates a bindu
to `planet`. Contributors are the 7 grahas plus the Lagna. Tables follow
the standard BPHS scheme; each planet's total bindus are constant
(Sun 48, Moon 49, Mars 39, Mercury 54, Jupiter 56, Venus 52, Saturn 39),
making the Sarvashtakavarga total 337 — a useful internal check.

Reductions (for Shodhya Pinda): Trikona Shodhana first, then
Ekadhipatya Shodhana — the order cannot be reversed (BPHS/Phaladeepika).
Shodhya Pinda = Rasi Pinda + Graha Pinda (Brihat Jataka):
  Rasi Pinda  = sum over signs of shodhita bindus x Rasi Gunakara
  Graha Pinda = sum over the 7 planets of (shodhita bindus in the sign
                each planet occupies) x that planet's Graha Gunakara
Gunakaras: Rasi — Aries 7, Taurus 10, Gemini 8, Cancer 4, Leo 10,
Virgo 5, Libra 7, Scorpio 8, Sagittarius 9, Capricorn 5, Aquarius 4,
Pisces 10. Graha — Sun 5, Moon 5, Mars 8, Mercury 5, Jupiter 10,
Venus 7, Saturn 5.
"""
from __future__ import annotations

from .names import PLANETS_7

_CONTRIBUTORS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Lagna"]

BENEFIC: dict[str, dict[str, list[int]]] = {
    "Sun": {
        "Sun": [1, 2, 4, 7, 8, 9, 10, 11], "Moon": [3, 6, 10, 11],
        "Mars": [1, 2, 4, 7, 8, 9, 10, 11], "Mercury": [3, 5, 6, 9, 10, 11, 12],
        "Jupiter": [5, 6, 9, 11], "Venus": [6, 7, 12],
        "Saturn": [1, 2, 4, 7, 8, 9, 10, 11], "Lagna": [3, 4, 6, 10, 11, 12],
    },
    "Moon": {
        "Sun": [3, 6, 7, 8, 10, 11], "Moon": [1, 3, 6, 7, 10, 11],
        "Mars": [2, 3, 5, 6, 9, 10, 11], "Mercury": [1, 3, 4, 5, 7, 8, 10, 11],
        "Jupiter": [1, 4, 7, 8, 10, 11, 12], "Venus": [3, 4, 5, 7, 9, 10, 11],
        "Saturn": [3, 5, 6, 11], "Lagna": [3, 6, 10, 11],
    },
    "Mars": {
        "Sun": [3, 5, 6, 10, 11], "Moon": [3, 6, 11],
        "Mars": [1, 2, 4, 7, 8, 10, 11], "Mercury": [3, 5, 6, 11],
        "Jupiter": [6, 10, 11, 12], "Venus": [6, 8, 11, 12],
        "Saturn": [1, 4, 7, 8, 9, 10, 11], "Lagna": [1, 3, 6, 10, 11],
    },
    "Mercury": {
        "Sun": [5, 6, 9, 11, 12], "Moon": [2, 4, 6, 8, 10, 11],
        "Mars": [1, 2, 4, 7, 8, 9, 10, 11], "Mercury": [1, 3, 5, 6, 9, 10, 11, 12],
        "Jupiter": [6, 8, 11, 12], "Venus": [1, 2, 3, 4, 5, 8, 9, 11],
        "Saturn": [1, 2, 4, 7, 8, 9, 10, 11], "Lagna": [1, 2, 4, 6, 8, 10, 11],
    },
    "Jupiter": {
        "Sun": [1, 2, 3, 4, 7, 8, 9, 10, 11], "Moon": [2, 5, 7, 9, 11],
        "Mars": [1, 2, 4, 7, 8, 10, 11], "Mercury": [1, 2, 4, 5, 6, 9, 10, 11],
        "Jupiter": [1, 2, 3, 4, 7, 8, 10, 11], "Venus": [2, 5, 6, 9, 10, 11],
        "Saturn": [3, 5, 6, 12], "Lagna": [1, 2, 4, 5, 6, 7, 9, 10, 11],
    },
    "Venus": {
        "Sun": [8, 11, 12], "Moon": [1, 2, 3, 4, 5, 8, 9, 11, 12],
        "Mars": [3, 5, 6, 9, 11, 12], "Mercury": [3, 5, 6, 9, 11],
        "Jupiter": [5, 8, 9, 10, 11], "Venus": [1, 2, 3, 4, 5, 8, 9, 10, 11],
        "Saturn": [3, 4, 5, 8, 9, 10, 11], "Lagna": [1, 2, 3, 4, 5, 8, 9, 11],
    },
    "Saturn": {
        "Sun": [1, 2, 4, 7, 8, 10, 11], "Moon": [3, 6, 11],
        "Mars": [3, 5, 6, 10, 11, 12], "Mercury": [6, 8, 9, 10, 11, 12],
        "Jupiter": [5, 6, 11, 12], "Venus": [6, 11, 12],
        "Saturn": [3, 5, 6, 11], "Lagna": [1, 3, 4, 6, 10, 11],
    },
}


def compute_ashtakavarga(planets: dict, lagna_sign: int) -> dict:
    """{planet: [bindus per sign 0..11]} plus 'Sarvashtakavarga' row."""
    signs = {name: p["sign"] for name, p in planets.items()}
    signs["Lagna"] = lagna_sign
    out: dict[str, list[int]] = {}
    for planet, table in BENEFIC.items():
        bindus = [0] * 12
        for contributor, houses in table.items():
            base = signs[contributor]
            for h in houses:
                bindus[(base + h - 1) % 12] += 1
        out[planet] = bindus
    sarva = [sum(out[p][s] for p in BENEFIC) for s in range(12)]
    out["Sarvashtakavarga"] = sarva
    return out


# ---------------------------------------------------------------------------
# Shodhana (reductions) and Shodhya Pinda
# ---------------------------------------------------------------------------
_RASI_GUNAKARA = [7, 10, 8, 4, 10, 5, 7, 8, 9, 5, 4, 10]  # Aries..Pisces
_GRAHA_GUNAKARA = {"Sun": 5, "Moon": 5, "Mars": 8, "Mercury": 5,
                   "Jupiter": 10, "Venus": 7, "Saturn": 5}
# Signs owned by one planet (Sun/Leo and Moon/Cancer own a single sign:
# no Ekadhipatya reduction there).
_DUAL_SIGNS = {"Mars": (0, 7), "Mercury": (2, 5), "Jupiter": (8, 11),
               "Venus": (1, 6), "Saturn": (9, 10)}


def trikona_shodhana(bindus: list[int]) -> list[int]:
    """Trikona (first) reduction on a 12-sign BAV row.

    Per trikona group (1-5-9, 2-6-10, 3-7-11, 4-8-12): all three equal
    -> all zero; two are zero -> the third becomes zero; any one zero ->
    no change; otherwise subtract the lowest from all three.
    """
    out = list(bindus)
    for a, b, c in ((0, 4, 8), (1, 5, 9), (2, 6, 10), (3, 7, 11)):
        vals = (out[a], out[b], out[c])
        if vals[0] == vals[1] == vals[2]:
            out[a] = out[b] = out[c] = 0
        elif sum(1 for v in vals if v == 0) == 2:
            out[a] = out[b] = out[c] = 0
        elif 0 in vals:
            continue
        else:
            m = min(vals)
            out[a] -= m
            out[b] -= m
            out[c] -= m
    return out


def ekadhipatya_shodhana(bindus: list[int], planet: str, planet_sign: int) -> list[int]:
    """Ekadhipatya (second) reduction on a trikona-reduced BAV row.

    For the two signs owned by `planet`:
    - planet occupies one of its own signs (occ, other): if occ >= other
      the other's bindus are destroyed; else the other is reduced to
      the occupied sign's level;
    - planet in neither sign: a zero anywhere -> no change; equal
      figures -> both destroyed; else the larger is reduced to the
      smaller.
    """
    out = list(bindus)
    pair = _DUAL_SIGNS.get(planet)
    if pair is None:
        return out
    s1, s2 = pair
    b1, b2 = out[s1], out[s2]
    if planet_sign == s1 or planet_sign == s2:
        occ, other = (s1, s2) if planet_sign == s1 else (s2, s1)
        if out[occ] >= out[other]:
            out[other] = 0
        else:
            out[other] = out[occ]
    else:
        if b1 == 0 or b2 == 0:
            pass
        elif b1 == b2:
            out[s1] = out[s2] = 0
        elif b1 > b2:
            out[s1] = b2
        else:
            out[s2] = b1
    return out


def shodhya_pinda(bindus: list[int], planet: str, planet_signs: dict[str, int]) -> dict:
    """Shodhya Pinda of one planet's BAV row.

    Applies Trikona then Ekadhipatya Shodhana, then:
      rasi_pinda  = sum(shodhita[s] x Rasi Gunakara[s])
      graha_pinda = sum over the 7 planets of shodhita[sign of planet]
                    x that planet's Graha Gunakara
    shodhya_pinda = rasi_pinda + graha_pinda.
    """
    reduced = ekadhipatya_shodhana(trikona_shodhana(bindus), planet,
                                   planet_signs[planet])
    rasi_pinda = sum(b * g for b, g in zip(reduced, _RASI_GUNAKARA))
    graha_pinda = sum(reduced[planet_signs[q]] * _GRAHA_GUNAKARA[q]
                      for q in PLANETS_7)
    return {
        "reduced_bindus": reduced,
        "rasi_pinda": rasi_pinda,
        "graha_pinda": graha_pinda,
        "shodhya_pinda": rasi_pinda + graha_pinda,
    }


def compute_shodhya_pindas(bav: dict, planets: dict) -> dict:
    """{planet: shodhya_pinda(...)} for the 7 BAV rows."""
    planet_signs = {name: p["sign"] for name, p in planets.items()}
    return {p: shodhya_pinda(bav[p], p, planet_signs) for p in BENEFIC}
