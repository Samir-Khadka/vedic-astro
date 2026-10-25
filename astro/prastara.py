"""Prastara Ashtakavarga — the 8×12 bindu grids behind the totals.

The Sarvashtakavarga total (337) is the headline, but practitioners
read the Prastara: for each planet P, an 8-row grid (contributors =
7 grahas + Lagna) over the 12 signs, where a cell is 1 when that
contributor donates a bindu to P in that sign (same BENEFIC tables as
compute_ashtakavarga). Column sums reproduce P's BAV exactly.

Two classical reductions (Shodhana, BPHS) are then applied to each
planet's BAV, in order:
  1. Trikona Shodhana — in each triad of signs (1,5,9), (2,6,10),
     (3,7,11), (4,8,12) counted from the planet's own sign position:
     if all three houses hold bindus, subtract the smallest of the
     three from all three; if any is zero, no reduction.
  2. Ekadhipatya Shodhana — for each pair of signs ruled by one
     planet: if one of the pair is empty, the other's bindus are
     removed entirely; if both hold bindus, subtract the smaller
     from the larger (the smaller becomes zero).
The reduced totals are what the classical texts carry into prediction
(they are always <= the unreduced totals). Reduction rules vary
slightly between schools; the version here is the widely published
BPHS form and is documented as such wherever it is displayed.
"""
from __future__ import annotations

from .ashtakavarga import BENEFIC

CONTRIBUTORS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Lagna"]

# Sign pairs sharing one lord (Ekadhipatya): Aries/Scorpio Mars,
# Taurus/Libra Venus, Gemini/Virgo Mercury, Cancer/Leo (no pair —
# Moon and Sun rule one sign each), Sagittarius/Pisces Jupiter,
# Capricorn/Aquarius Saturn.
EKADHIPATYA_PAIRS = [(0, 7), (1, 6), (2, 5), (8, 11), (9, 10)]

# Triads counted in houses from the planet's own sign: (1,5,9),
# (2,6,10), (3,7,11), (4,8,12) — as sign offsets from the planet.
TRIKONA_TRIADS = [(0, 4, 8), (1, 5, 9), (2, 6, 10), (3, 7, 11)]


def prastara_grid(planet: str, signs: dict[str, int]) -> dict[str, list[int]]:
    """{contributor: [0/1 per sign 0..11]} for `planet`'s BAV."""
    table = BENEFIC[planet]
    grid: dict[str, list[int]] = {}
    for contributor, houses in table.items():
        row = [0] * 12
        base = signs[contributor]
        for h in houses:
            row[(base + h - 1) % 12] = 1
        grid[contributor] = row
    return grid


def _trikona_reduce(bav: list[int], planet_sign: int) -> list[int]:
    out = list(bav)
    for triad in TRIKONA_TRIADS:
        idx = [(planet_sign + off) % 12 for off in triad]
        vals = [out[i] for i in idx]
        if all(v > 0 for v in vals):
            m = min(vals)
            for i in idx:
                out[i] -= m
    return out


def _ekadhipatya_reduce(bav: list[int]) -> list[int]:
    out = list(bav)
    for a, b in EKADHIPATYA_PAIRS:
        if out[a] == 0 or out[b] == 0:
            out[a] = 0
            out[b] = 0
        else:
            m = min(out[a], out[b])
            out[a] -= m
            out[b] -= m
    return out


def prastara(planets: dict, lagna_sign: int) -> dict:
    """Full Prastara bundle: grids, unreduced and reduced BAV per planet.

    Returns {planet: {grid, bav, reduced, reduced_total}, ...} for the
    7 grahas, plus 'Sarvashtakavarga' reduced totals per sign.
    """
    signs = {name: p["sign"] for name, p in planets.items()}
    signs["Lagna"] = lagna_sign
    out: dict = {}
    for planet in BENEFIC:
        grid = prastara_grid(planet, signs)
        bav = [sum(grid[c][s] for c in CONTRIBUTORS) for s in range(12)]
        reduced = _ekadhipatya_reduce(_trikona_reduce(bav, signs[planet]))
        out[planet] = {
            "grid": grid,
            "bav": bav,
            "reduced": reduced,
            "reduced_total": sum(reduced),
        }
    out["Sarvashtakavarga_reduced"] = [
        sum(out[p]["reduced"][s] for p in BENEFIC) for s in range(12)
    ]
    return out
