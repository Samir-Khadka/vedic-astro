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


def prev_ingress(planet: str, jd_from: float, max_days: float = 1200.0) -> dict:
    """The most recent sign ingress of `planet` at or before `jd_from` —
    i.e. when it entered the sign it occupies at `jd_from`."""
    start_sign = _sign_at(planet, jd_from)
    step = _STEP_DAYS[planet]
    hi = jd_from
    lo = jd_from - step
    while _sign_at(planet, lo) == start_sign:
        hi = lo
        lo -= step
        if jd_from - lo > max_days:
            raise ValueError(f"no previous ingress found for {planet}")
    # Bisect: sign at lo != start_sign, sign at hi == start_sign.
    for _ in range(48):
        mid = (lo + hi) / 2.0
        if _sign_at(planet, mid) == start_sign:
            hi = mid
        else:
            lo = mid
        if hi - lo < 0.002:
            break
    return {
        "planet": planet,
        "from_sign": _sign_at(planet, lo),
        "to_sign": start_sign,
        "date": _jd_to_date(hi),
        "jd": hi,
    }


def ingress_jd(planet: str, jd_from: float) -> float:
    """JD of the next ingress of `planet` after `jd_from` (bisected)."""
    start_sign = _sign_at(planet, jd_from)
    step = _STEP_DAYS[planet]
    lo = jd_from
    hi = jd_from + step
    while _sign_at(planet, hi) == start_sign:
        lo = hi
        hi += step
        if hi - jd_from > 4000:
            raise ValueError(f"no ingress found for {planet}")
    for _ in range(48):
        mid = (lo + hi) / 2.0
        if _sign_at(planet, mid) == start_sign:
            lo = mid
        else:
            hi = mid
        if hi - lo < 0.002:
            break
    return hi


def ingress_chain(planet: str, jd_from: float, jd_to: float) -> list[dict]:
    """Every ingress of `planet` in (jd_from, jd_to], chronological:
    [{planet, from_sign, to_sign, date}]."""
    out = []
    cursor = jd_from
    while cursor < jd_to:
        njd = ingress_jd(planet, cursor)
        if njd > jd_to:
            break
        out.append({
            "planet": planet,
            "from_sign": _sign_at(planet, njd - 0.01),
            "to_sign": _sign_at(planet, njd + 0.01),
            "date": _jd_to_date(njd),
        })
        cursor = njd + 1.0
    return out


def saturn_moon_span(moon_sign: int, jd_now: float) -> dict | None:
    """Boundary ingress dates of Saturn's passage over the three signs
    around the Moon sign (the Sade Sati span): when Saturn entered /
    will enter moon-1, moon, moon+1 and moon+2.

    Computed only when Saturn is in the span or one sign before it;
    otherwise None. Retrograde re-entries are resolved to the FIRST
    entry into moon-1 and the FINAL exit into moon+2 going forward
    from now for future boundaries — patros print the span this way.
    """
    cur = _sign_at("Saturn", jd_now)
    rel = (cur - moon_sign) % 12
    if rel not in (10, 11, 0, 1):
        return None
    targets = [(moon_sign - 1) % 12, moon_sign, (moon_sign + 1) % 12, (moon_sign + 2) % 12]
    found: dict[int, float] = {}
    # Backwards: entry dates for targets at or before now.
    back_jd = jd_now
    for _ in range(6):
        if all(t in found for t in targets):
            break
        ing = prev_ingress("Saturn", back_jd)
        if ing["to_sign"] in targets and ing["to_sign"] not in found:
            found[ing["to_sign"]] = ing["jd"]
        back_jd = ing["jd"] - 1.0
        if jd_now - back_jd > 3650:
            break
    # Forwards: entry dates for the targets still ahead.
    fwd_jd = jd_now
    for _ in range(8):
        if all(t in found for t in targets):
            break
        njd = ingress_jd("Saturn", fwd_jd)
        nsign = _sign_at("Saturn", njd + 0.01)
        if nsign in targets and nsign not in found:
            found[nsign] = njd
        fwd_jd = njd + 1.0
    if not all(t in found for t in targets):
        return None
    return {
        "start": _jd_to_date(found[targets[0]]),         # Saturn enters moon-1
        "peak_start": _jd_to_date(found[targets[1]]),    # enters the Moon sign
        "setting_start": _jd_to_date(found[targets[2]]),  # enters moon+1
        "end": _jd_to_date(found[targets[3]]),           # enters moon+2: over
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


# Graha-drishti offsets used for double-transit activation: a transiting
# planet activates its own sign plus the signs it aspects.
_DT_OFFSETS = {"Saturn": (0, 2, 6, 9), "Jupiter": (0, 4, 6, 8)}


def double_transit(jd_now: float) -> dict:
    """Signs jointly activated by transiting Saturn and Jupiter (the
    classical double transit used for event timing)."""
    signs_now = ephemeris.planet_longitudes(jd_now)
    activated: dict[str, set[int]] = {}
    for planet, offsets in _DT_OFFSETS.items():
        base = signs_now[planet]["sign"]
        activated[planet] = {(base + o) % 12 for o in offsets}
    joint = sorted(activated["Saturn"] & activated["Jupiter"])
    return {
        "saturn_sign": signs_now["Saturn"]["sign"],
        "jupiter_sign": signs_now["Jupiter"]["sign"],
        "joint_signs": joint,
    }
