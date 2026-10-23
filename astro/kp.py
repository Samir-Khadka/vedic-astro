"""KP (Krishnamurti Paddhati) layer.

KP refines each nakshatra into 9 unequal 'subs' whose widths are proportional
to the Vimshottari dasha years (lord years / 120 of the nakshatra span), and
each sub again into 9 sub-subs. A body's sign lord / star lord / sub lord /
sub-sub lord chain is the core KP judgement tool.
"""
from __future__ import annotations

from .names import (
    DASHA_SEQUENCE, DASHA_YEARS, NAKSHATRA_LORDS, NAKSHATRA_SPAN, SIGN_LORDS,
)

_SEQ = DASHA_SEQUENCE


def _lords_at(longitude: float) -> tuple[str, str, str, str]:
    """(star lord, sub lord, sub-sub lord) for a sidereal longitude."""
    lon = longitude % 360.0
    nak_idx = int(lon // NAKSHATRA_SPAN)
    star_lord = NAKSHATRA_LORDS[nak_idx]
    pos_in_nak = lon - nak_idx * NAKSHATRA_SPAN

    # Walk the sub divisions of this nakshatra.
    i0 = _SEQ.index(star_lord)
    cursor = 0.0
    sub_lord = star_lord
    sub_start = 0.0
    sub_span = NAKSHATRA_SPAN
    for k in range(9):
        lord = _SEQ[(i0 + k) % 9]
        span = NAKSHATRA_SPAN * DASHA_YEARS[lord] / 120.0
        if cursor + span > pos_in_nak or k == 8:
            sub_lord, sub_start, sub_span = lord, cursor, span
            break
        cursor += span

    # Walk the sub-sub divisions inside the sub.
    pos_in_sub = pos_in_nak - sub_start
    j0 = _SEQ.index(sub_lord)
    cursor = 0.0
    sub_sub_lord = sub_lord
    for k in range(9):
        lord = _SEQ[(j0 + k) % 9]
        span = sub_span * DASHA_YEARS[lord] / 120.0
        if cursor + span > pos_in_sub or k == 8:
            sub_sub_lord = lord
            break
        cursor += span
    return star_lord, sub_lord, sub_sub_lord


def kp_chain(longitude: float) -> dict:
    """Full KP lord chain for any longitude (planet or cusp)."""
    star, sub, sub_sub = _lords_at(longitude)
    sign = int((longitude % 360.0) // 30.0)
    return {
        "sign_lord": SIGN_LORDS[sign],
        "star_lord": star,
        "sub_lord": sub,
        "sub_sub_lord": sub_sub,
    }


def _house_of_longitude(lon: float, cusps: list[float]) -> int:
    """KP house (1..12): which Placidus cusp interval contains `lon`."""
    for i in range(12):
        start = cusps[i]
        end = cusps[(i + 1) % 12]
        span = (end - start) % 360.0
        if (lon - start) % 360.0 < span:
            return i + 1
    return 1


def kp_tables(planets: dict, cusps: list[float]) -> dict:
    """Planet chains, cuspal sub lord table, and house significators.

    Significator scheme (simplified classical KP):
      A-level: planets occupying the house and planets in their star
      B-level: the cusp's sign lord and planets in the sign lord's star
    The cuspal sub lord is listed per house as the final arbiter.
    """
    planet_rows = {}
    houses_by_planet = {}
    for name, p in planets.items():
        row = kp_chain(p["longitude"])
        row["house"] = _house_of_longitude(p["longitude"], cusps)
        planet_rows[name] = row
        houses_by_planet[name] = row["house"]

    # Which houses' cusp signs does each planet rule?
    ruled: dict[str, list[int]] = {name: [] for name in planets}
    for h in range(12):
        lord = SIGN_LORDS[int(cusps[h] // 30.0)]
        ruled[lord].append(h + 1)

    cusp_rows = []
    for h in range(12):
        chain = kp_chain(cusps[h])
        cusp_rows.append({
            "house": h + 1,
            "longitude": cusps[h],
            "sign": int(cusps[h] // 30.0),
            **chain,
        })

    # Star-lord lookup used by significator chains.
    def in_star_of(planet: str) -> list[str]:
        return [n for n, p in planets.items() if NAKSHATRA_LORDS[p["nakshatra"]] == planet]

    house_significators = {}
    for h in range(1, 13):
        occupants = [n for n, r in planet_rows.items() if r["house"] == h]
        cusp_lord = SIGN_LORDS[int(cusps[h - 1] // 30.0)]
        a_level = sorted(set(occupants) | {q for p in occupants for q in in_star_of(p)})
        b_level = sorted({cusp_lord} | set(in_star_of(cusp_lord)))
        house_significators[h] = {
            "occupants": occupants,
            "sign_lord": cusp_lord,
            "cuspal_sub_lord": cusp_rows[h - 1]["sub_lord"],
            "a_level": a_level,
            "b_level": b_level,
        }

    # Houses each planet signifies: occupied + ruled + via star lord
    planet_signified = {}
    for name, p in planets.items():
        houses = {houses_by_planet[name]} | set(ruled[name])
        star_lord = NAKSHATRA_LORDS[p["nakshatra"]]
        houses |= {houses_by_planet[star_lord]} | set(ruled[star_lord])
        planet_signified[name] = sorted(houses)

    return {
        "planets": planet_rows,
        "cusps": cusp_rows,
        "house_significators": house_significators,
        "planet_signified_houses": planet_signified,
    }
