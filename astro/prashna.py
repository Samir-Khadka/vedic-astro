"""KP Horary (Prashna) — the 1-249 number chart.

The querent picks a number from 1 to 249. The zodiac is divided into 249
KP sub-divisions (each nakshatra split into 9 subs proportional to the
Vimshottari years, numbered sequentially from the start of Ashwini). The
horary Lagna is placed at the START of the sub corresponding to the
number, at the querent's place; the chart is the sky at the moment near
the query time when the ascendant actually reaches that degree, so all
cusps and planetary positions are astronomically consistent.

Ruling Planets are taken at the query moment itself: the weekday lord,
and the sign/star/sub lords of the ascendant and of the Moon.
"""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from . import ephemeris, kp as kp_module
from .names import (
    DASHA_SEQUENCE, DASHA_YEARS, NAKSHATRA_SPAN, PLANET_NE, SIGNS_EN, SIGNS_NE,
    VAARA_LORDS,
)


def sub_table() -> list[dict]:
    """The 249 KP subs in zodiac order with their longitude arcs.

    27 nakshatras x 9 subs = 243 base segments; the 6 segments that
    straddle a sign boundary (at 30, 90, 150, 210, 270 and 330 degrees)
    are each counted as two subs — the classical KP count of 249."""
    base = []
    for nak in range(27):
        star_lord = DASHA_SEQUENCE[nak % 9]
        i0 = DASHA_SEQUENCE.index(star_lord)
        cursor = nak * NAKSHATRA_SPAN
        for k in range(9):
            lord = DASHA_SEQUENCE[(i0 + k) % 9]
            span = NAKSHATRA_SPAN * DASHA_YEARS[lord] / 120.0
            base.append({"start": cursor, "end": cursor + span,
                         "star_lord": star_lord, "sub_lord": lord})
            cursor += span
    out = []
    for seg in base:
        pieces = [seg]
        boundary = (int(seg["start"] // 30.0) + 1) * 30.0
        if seg["start"] + 1e-9 < boundary < seg["end"] - 1e-9:
            pieces = [
                {**seg, "end": boundary},
                {**seg, "start": boundary},
            ]
        for piece in pieces:
            out.append({
                "number": len(out) + 1,
                "start": piece["start"], "end": piece["end"],
                "star_lord": piece["star_lord"], "sub_lord": piece["sub_lord"],
                "sign": int(piece["start"] // 30.0),
            })
    return out


_SUBS = sub_table()


def _solve_ascendant_jd(target_lon: float, jd_guess: float, lat: float, lon: float) -> float:
    """Find the Julian day nearest `jd_guess` at which the sidereal
    ascendant equals `target_lon` (bisection on the travel distance)."""
    step = 1.0 / 48.0  # 30 minutes

    def travel(jd: float) -> float:
        asc = ephemeris.ascendant(jd, lat, lon, b"W")
        return (target_lon - asc) % 360.0

    lo = jd_guess - 0.5
    prev_jd, prev_g = lo, travel(lo)
    bracket = None
    jd = lo
    while jd < jd_guess + 0.5:
        jd += step
        g = travel(jd)
        if prev_g < 180.0 and g > 180.0:
            bracket = (prev_jd, jd)  # crossing lies inside
            break
        prev_jd, prev_g = jd, g
    if bracket is None:
        raise ValueError("could not resolve horary ascendant")
    a, b = bracket
    for _ in range(60):
        mid = (a + b) / 2.0
        if travel(mid) < 180.0:
            a = mid  # ascendant has not reached the target yet
        else:
            b = mid
        if b - a < 1e-6:
            break
    return (a + b) / 2.0


def horary(number: int, place: dict, moment: datetime, question: str = "") -> dict:
    if not 1 <= number <= 249:
        raise ValueError("horary number must be between 1 and 249")
    lat, lon, tz_name = place["lat"], place["lon"], place["tz"]
    sub = _SUBS[number - 1]
    target = sub["start"]

    jd_moment = ephemeris.to_julian_day(moment)
    jd_chart = _solve_ascendant_jd(target, jd_moment, lat, lon)
    chart_dt_utc = ephemeris.jd_to_utc_datetime(jd_chart)
    chart_dt_local = chart_dt_utc.astimezone(ZoneInfo(tz_name))

    planets = ephemeris.planet_longitudes(jd_chart)
    lagna_lon = ephemeris.ascendant(jd_chart, lat, lon, b"W")
    cusps = ephemeris.placidus_cusps(jd_chart, lat, lon)
    tables = kp_module.kp_tables(planets, cusps)

    chart_map = {"Lagna": int(lagna_lon // 30.0)}
    for name, p in planets.items():
        chart_map[name] = p["sign"]

    # Ruling planets at the query moment.
    jd_now = jd_moment
    asc_now = ephemeris.ascendant(jd_now, lat, lon, b"W")
    planets_now = ephemeris.planet_longitudes(jd_now)
    asc_chain = kp_module.kp_chain(asc_now)
    moon_chain = kp_module.kp_chain(planets_now["Moon"]["longitude"])
    local_now = moment.astimezone(ZoneInfo(tz_name))
    # Sunrise-based vaara: before sunrise, the previous weekday rules.
    rise, _set = ephemeris.sunrise_sunset(local_now.date(), lat, lon, tz_name)
    weekday = local_now.weekday()
    if rise and local_now < rise:
        weekday = (weekday - 1) % 7
    day_lord = VAARA_LORDS[weekday]

    ruling = [
        {"role": "Day lord", "role_ne": "वार स्वामी", "planet": day_lord},
        {"role": "Ascendant sign lord", "role_ne": "लग्न राशि स्वामी", "planet": asc_chain["sign_lord"]},
        {"role": "Ascendant star lord", "role_ne": "लग्न नक्षत्र स्वामी", "planet": asc_chain["star_lord"]},
        {"role": "Ascendant sub lord", "role_ne": "लग्न उपस्वामी", "planet": asc_chain["sub_lord"]},
        {"role": "Moon sign lord", "role_ne": "चन्द्र राशि स्वामी", "planet": moon_chain["sign_lord"]},
        {"role": "Moon star lord", "role_ne": "चन्द्र नक्षत्र स्वामी", "planet": moon_chain["star_lord"]},
        {"role": "Moon sub lord", "role_ne": "चन्द्र उपस्वामी", "planet": moon_chain["sub_lord"]},
    ]
    for r in ruling:
        r["planet_ne"] = PLANET_NE[r["planet"]]

    planet_rows = []
    for name in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"):
        p = planets[name]
        planet_rows.append({
            "planet": name, "name_ne": PLANET_NE[name],
            "sign": p["sign"], "sign_en": SIGNS_EN[p["sign"]], "sign_ne": SIGNS_NE[p["sign"]],
            "degree_in_sign": round(p["degree_in_sign"], 3),
            "retrograde": p["retrograde"], "kp": tables["planets"][name],
        })

    return {
        "number": number,
        "question": question,
        "sub": {
            "star_lord": sub["star_lord"], "sub_lord": sub["sub_lord"],
            "start_longitude": round(sub["start"], 4), "end_longitude": round(sub["end"], 4),
            "sign_en": SIGNS_EN[sub["sign"]], "sign_ne": SIGNS_NE[sub["sign"]],
        },
        "chart_moment_local": chart_dt_local.isoformat(),
        "lagna": {
            "longitude": round(lagna_lon, 4), "sign": int(lagna_lon // 30.0),
            "sign_en": SIGNS_EN[int(lagna_lon // 30.0)], "sign_ne": SIGNS_NE[int(lagna_lon // 30.0)],
            "degree_in_sign": round(lagna_lon % 30.0, 3),
        },
        "chart": chart_map,
        "planets": planet_rows,
        "cusps": [
            {**c, "longitude": round(c["longitude"], 4),
             "sign_en": SIGNS_EN[c["sign"]], "sign_ne": SIGNS_NE[c["sign"]]}
            for c in tables["cusps"]
        ],
        "house_significators": tables["house_significators"],
        "ruling_planets": ruling,
        "place": place,
    }
