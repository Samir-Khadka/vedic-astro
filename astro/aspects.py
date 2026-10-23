"""Parashari graha drishti (whole-sign planetary aspects).

Every planet aspects the 7th sign from its own. Mars additionally
aspects the 4th and 8th, Jupiter the 5th and 9th, Saturn the 3rd and
10th. The nodes are given the 7th aspect only — the conservative
Parashari reading (some schools extend Rahu to the 5th/9th/12th; we do
not, and say so where it matters). Aspects here are sign-to-sign: a
planet aspects every planet in an aspected sign and the house whose
sign that is.
"""
from __future__ import annotations

from .charts import house_of

_SPECIAL = {
    "Mars": (4, 7, 8),
    "Jupiter": (5, 7, 9),
    "Saturn": (3, 7, 10),
}
_DEFAULT = (7,)


def aspect_offsets(planet: str) -> tuple[int, ...]:
    """House offsets (1-based, from the planet's own sign) it aspects."""
    return _SPECIAL.get(planet, _DEFAULT)


def aspected_signs(planet: str, planets: dict) -> list[int]:
    own = planets[planet]["sign"]
    return [(own + off - 1) % 12 for off in aspect_offsets(planet)]


def planets_aspected_by(planet: str, planets: dict) -> list[str]:
    signs = set(aspected_signs(planet, planets))
    return [q for q in planets if q != planet and planets[q]["sign"] in signs]


def aspecting_planets(target_sign: int, planets: dict,
                      exclude: str | None = None) -> list[str]:
    """Planets whose graha drishti falls on `target_sign`."""
    out = []
    for q in planets:
        if q == exclude:
            continue
        if target_sign in aspected_signs(q, planets):
            out.append(q)
    return out


def houses_aspected_by(planet: str, planets: dict, lagna_sign: int) -> list[int]:
    return sorted(house_of(s, lagna_sign) for s in aspected_signs(planet, planets))


def conjunct_planets(planet: str, planets: dict) -> list[str]:
    own = planets[planet]["sign"]
    return [q for q in planets if q != planet and planets[q]["sign"] == own]


def relation_between(a_sign: int, b_sign: int) -> str:
    """Positional relation of sign b counted from sign a, classified the
    way dasha interpretation uses it: kendra / trikona / dusthana /
    upachaya / other."""
    rel = (b_sign - a_sign) % 12 + 1
    if rel in (1, 4, 7, 10):
        return "kendra"
    if rel in (5, 9):
        return "trikona"
    if rel in (6, 8, 12):
        return "dusthana"
    if rel in (3, 11):
        return "upachaya"
    return "2nd/11th" if rel in (2, 11) else "other"
