"""Transits (Gochar) — current signs of the grahas plus the next sign
ingress (pravesh) dates for the slow movers, computed by bracketing the
sign change in Julian days and bisecting on the sidereal longitude.

Dates are the UTC calendar dates on which the ingress occurs (transits
are global events; the exact local time varies by longitude, so the
table reports dates, matching how patros print them).
"""
from __future__ import annotations

from datetime import datetime, timezone

from . import ephemeris
from .names import SIGNS_EN, SIGNS_NE

_STEP_DAYS = {
    "Saturn": 10.0, "Jupiter": 5.0, "Rahu": 5.0, "Ketu": 5.0,
    "Mars": 2.0, "Sun": 1.0, "Venus": 1.0, "Mercury": 1.0, "Moon": 0.25,
}
INGRESS_PLANETS = ["Saturn", "Jupiter", "Rahu", "Ketu", "Mars", "Sun"]


def _sign_at(planet: str, jd: float) -> int:
    return ephemeris.planet_longitudes(jd)[planet]["sign"]


def _jd_to_date(jd: float) -> str:
    return ephemeris.jd_to_date_str(jd)


def next_ingress(planet: str, jd_from: float, max_days: float = 900.0) -> dict:
    """Next moment after `jd_from` at which `planet` changes sign."""
    start_sign = _sign_at(planet, jd_from)
    step = _STEP_DAYS[planet]
    lo = jd_from
    hi = jd_from + step
    while _sign_at(planet, hi) == start_sign:
        lo = hi
        hi += step
        if hi - jd_from > max_days:
            raise ValueError(f"no ingress found for {planet}")
    # Bisect: sign at lo == start_sign, sign at hi != start_sign.
    for _ in range(48):
        mid = (lo + hi) / 2.0
        if _sign_at(planet, mid) == start_sign:
            lo = mid
        else:
            hi = mid
        if hi - lo < 0.002:
            break
    return {
        "planet": planet,
        "from_sign": start_sign,
        "to_sign": _sign_at(planet, hi),
        "date": _jd_to_date(hi),
    }


def transit_table(now_jd: float, moon_sign: int) -> dict:
    """Current transit signs + next ingresses, with each slow planet's
    house counted from the natal Moon sign."""
    planets_now = ephemeris.planet_longitudes(now_jd)
    rows = []
    for p in INGRESS_PLANETS:
        ing = next_ingress(p, now_jd)
        cur_sign = planets_now[p]["sign"]
        rows.append({
            "planet": p,
            "current_sign": cur_sign,
            "current_sign_en": SIGNS_EN[cur_sign],
            "current_sign_ne": SIGNS_NE[cur_sign],
            "house_from_moon": (cur_sign - moon_sign) % 12 + 1,
            "next_ingress_date": ing["date"],
            "next_sign": ing["to_sign"],
            "next_sign_en": SIGNS_EN[ing["to_sign"]],
            "next_sign_ne": SIGNS_NE[ing["to_sign"]],
        })
    return {"ingress": rows}
