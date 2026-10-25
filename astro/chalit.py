"""Bhava Chalit — the house-placement chart (Sripathi method).

In the whole-sign Rashi chart a planet belongs to the house of its sign.
Bhava Chalit asks a different question: where does the planet fall
relative to the actual house cusps? Under the Sripathi convention each
house is centred on its Placidus cusp, so house *i* spans from the
midpoint of cusps *i-1* and *i* to the midpoint of cusps *i* and
*i+1*. A planet near a cusp can therefore sit in a different Chalit
house than its Rashi house — the classic reason a "strong" placement
sometimes fails to deliver, and the first thing a practitioner checks
when a Rashi reading does not match life.

Method note: Placidus cusps come from the engine (the same cusps KP
uses). Midpoint arithmetic wraps at 0°/360°. This module is pure:
it takes longitudes and cusps and returns the Chalit assignment.
"""
from __future__ import annotations


def _mid(a: float, b: float) -> float:
    """Midpoint of a→b along the zodiac (short-way, wrapping)."""
    return (a + ((b - a) % 360.0) / 2.0) % 360.0


def house_boundaries(cusps: list[float]) -> list[float]:
    """12 Chalit boundaries: boundary[i] opens house i+1.

    boundary[i] = midpoint of cusp[i-1] and cusp[i] (cusp[i] is the
    centre of house i+1). Boundaries tile the zodiac in order.
    """
    if len(cusps) != 12:
        raise ValueError("need 12 cusps")
    return [_mid(cusps[(i - 1) % 12], cusps[i]) for i in range(12)]


def chalit_house(longitude: float, boundaries: list[float]) -> int:
    """House (1..12) whose boundary span contains `longitude`."""
    lon = longitude % 360.0
    for i in range(12):
        start = boundaries[i]
        end = boundaries[(i + 1) % 12]
        if (lon - start) % 360.0 < (end - start) % 360.0:
            return i + 1
    return 1


def bhava_chalit(planets: dict, cusps: list[float], lagna_sign: int) -> dict:
    """Chalit assignment for every body, with Rashi-house comparison.

    Returns {boundaries: [deg], houses: {body: {chalit_house, rashi_house,
    sign, shifted}}, shifted: [bodies whose Chalit house != Rashi house]}.
    """
    from .charts import house_of

    boundaries = house_boundaries(cusps)
    houses: dict[str, dict] = {}
    shifted: list[str] = []
    for name, p in planets.items():
        rashi_house = house_of(p["sign"], lagna_sign)
        ch = chalit_house(p["longitude"], boundaries)
        houses[name] = {
            "chalit_house": ch,
            "rashi_house": rashi_house,
            "sign": p["sign"],
            "shifted": ch != rashi_house,
        }
        if ch != rashi_house:
            shifted.append(name)
    return {
        "boundaries": [round(b, 3) for b in boundaries],
        "houses": houses,
        "shifted": shifted,
    }
