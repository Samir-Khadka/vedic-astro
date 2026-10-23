"""Planetary and house strength — Shadbala, Bhava Bala, Ishta/Kashta
Phala and Vimshopaka Bala, following Brihat Parashara Hora Shastra ch. 27
and the standard published conventions built on it.

Conventions used (all documented because professional tools differ in
details, and totals legitimately vary between schools):

* Sputa Drishti (for Drik Bala) uses the BPHS anchor points published in
  B. V. Raman's Graha & Bhava Bala tables: 30°->0, 60°->15, 90°->45,
  120°->30, 150°->0, 180°->60, then declining to 0 at 300°, piecewise
  linear between anchors. Special aspects of Mars (4th/8th), Jupiter
  (5th/9th) and Saturn (3rd/10th) add a contribution peaking at 60 on the
  exact aspect degree. Drik Bala = (benefic aspects - malefic aspects)/4.
* Cheshta Bala uses the Saravali eight-fold motion classification
  (Vakra 60, Anuvakra 30, Vikala 15, Mandatara 15, Manda 30, Sama 7.5,
  Chara 45, Atichara 30) from the planet's apparent speed relative to its
  mean speed; sign-boundary crossings are detected by sampling the
  ephemeris at the linearly extrapolated crossing time. Per BPHS, the
  Sun's Cheshta Bala is its (undoubled) Ayana Bala and the Moon's is its
  Paksha Bala.
* Ayana Bala: (24 +/- declination)/48 x 60 -- plus for Sun, Mars, Jupiter,
  Venus; minus for Moon and Saturn; Mercury uses |declination|. The Sun's
  Ayana Bala is doubled (BPHS rule).
* Kala Bala sub-lords: Abda (year lord) 15, Masa (month lord) 30, Vaara
  (weekday lord) 45, Hora lord 60 virupas, each given only to that lord.
  Month/year lords are the weekday lords of the days the current solar
  month / solar year began (Sun's last sign ingress / Aries ingress),
  the standard published method. Yuddha (planetary war) Bala is not
  computed (it is 0 in the great majority of charts and its diameter
  rules vary by school); this is stated in the output.
* Bhava Bala = Bhavadhipati Bala (the house lord's total Shadbala, in
  rupas) + Drik Bala on the house cusp. The classical Dig Bala of houses
  is omitted: it is defined over bhava-madhya geometry whose published
  formulations disagree, while our houses are whole-sign. The omission
  is flagged in the output.
"""
from __future__ import annotations

import math
from datetime import timedelta

from . import ephemeris
from .charts import house_of
from .names import (
    EXALTATION, FRIENDSHIP, MOOLATRIKONA, PLANETS_7, SIGN_LORDS, VAARA_LORDS,
)

NAISARGIKA = {
    "Sun": 60.0, "Moon": 51.43, "Venus": 42.86, "Jupiter": 34.29,
    "Mercury": 25.71, "Mars": 17.14, "Saturn": 8.57,
}
MIN_RUPAS = {
    "Sun": 5.0, "Moon": 6.0, "Mars": 5.0, "Mercury": 7.0,
    "Jupiter": 6.5, "Venus": 5.5, "Saturn": 5.0,
}
SAPTA_VARGAS = ["D1", "D2", "D3", "D7", "D9", "D12", "D30"]
_SAPTA_VALUES = {
    "exalted": 45.0, "moolatrikona": 45.0, "own": 30.0, "great_friend": 22.5,
    "friend": 15.0, "neutral": 7.5, "enemy": 3.75, "great_enemy": 1.875,
    "debilitated": 1.875,
}
_VIMSHOPAKA_FRACTIONS = {
    "exalted": 1.0, "moolatrikona": 0.9, "own": 0.8, "great_friend": 0.7,
    "friend": 0.6, "neutral": 0.5, "enemy": 0.3, "great_enemy": 0.2,
    "debilitated": 0.1,
}
VIMSHOPAKA_SCHEMES = {
    "shadvarga": {"D1": 6.0, "D2": 2.0, "D3": 4.0, "D9": 5.0, "D12": 2.0, "D30": 1.0},
    "saptavarga": {"D1": 5.0, "D2": 2.0, "D3": 3.0, "D7": 2.5, "D9": 4.5, "D12": 2.0, "D30": 1.0},
    "shodashavarga": {
        "D1": 3.5, "D2": 1.0, "D3": 1.0, "D4": 0.5, "D7": 0.5, "D9": 3.0,
        "D10": 0.5, "D12": 0.5, "D16": 0.5, "D20": 0.5, "D24": 0.5,
        "D27": 1.0, "D30": 1.0, "D40": 1.0, "D45": 1.0, "D60": 4.0,
    },
}
_BENEFICS = {"Moon", "Mercury", "Jupiter", "Venus"}
_MALEFICS = {"Sun", "Mars", "Saturn"}
_AVG_SPEED = {"Mars": 0.524, "Mercury": 0.9856, "Jupiter": 0.0831, "Venus": 0.9856, "Saturn": 0.0335}
_HORA_ORDER = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]
# Dig Bala zero-points: the cusp (0-based index) where the planet scores 0.
_DIG_ZERO_CUSP = {"Sun": 3, "Mars": 3, "Moon": 9, "Venus": 9, "Jupiter": 6, "Mercury": 6, "Saturn": 0}
_SPECIAL_ASPECTS = {"Mars": (90.0, 210.0), "Jupiter": (120.0, 240.0), "Saturn": (60.0, 270.0)}


def _ang_dist(a: float, b: float) -> float:
    d = abs((a - b) % 360.0)
    return min(d, 360.0 - d)


# ---------------------------------------------------------------------------
# Dignity categories (natural + temporal = compound / panchadha maitri)
# ---------------------------------------------------------------------------
def _natural_relation(planet: str, other: str) -> str:
    if planet == other:
        return "self"
    friends, _neutral, enemies = FRIENDSHIP[planet]
    if other in friends:
        return "friend"
    if other in enemies:
        return "enemy"
    return "neutral"


def dignity_category(planet: str, sign: int, chart_signs: dict[str, int],
                     degree_in_sign: float | None = None) -> str:
    """Compound dignity of `planet` in `sign` within one varga chart.
    `chart_signs` maps every planet to its sign in that varga (for the
    temporal-friendship leg). Moolatrikona is judged only when the exact
    degree is supplied (the D1 chart)."""
    if sign == EXALTATION[planet][0]:
        # Moon's exaltation zone is only the first 3 degrees of Taurus.
        if planet == "Moon" and degree_in_sign is not None and degree_in_sign > 3.0:
            pass  # falls through to the moolatrikona check below
        else:
            return "exalted"
    if sign == (EXALTATION[planet][0] + 6) % 12:
        return "debilitated"
    if degree_in_sign is not None:
        m_sign, m_from, m_to = MOOLATRIKONA[planet]
        if sign == m_sign and m_from <= degree_in_sign < m_to:
            return "moolatrikona"
    lord = SIGN_LORDS[sign]
    if lord == planet:
        return "own"
    nat = _natural_relation(planet, lord)
    lord_sign = chart_signs.get(lord)
    if lord_sign is None:
        return {"friend": "friend", "enemy": "enemy"}.get(nat, "neutral")
    rel = (lord_sign - sign) % 12 + 1  # lord's house counted from the planet
    temp_friend = rel in (2, 3, 4, 10, 11, 12)
    if nat == "friend" and temp_friend:
        return "great_friend"
    if nat == "enemy" and not temp_friend:
        return "great_enemy"
    if nat == "neutral":
        return "friend" if temp_friend else "enemy"
    return "neutral"  # friend+temporary-enemy or enemy+temporary-friend


# ---------------------------------------------------------------------------
# Drik Bala (sputa drishti)
# ---------------------------------------------------------------------------
def sputa_drishti(theta: float) -> float:
    """Aspect value (0..60 virupas) at forward angular distance `theta`."""
    t = theta % 360.0
    if t < 30.0 or t >= 300.0:
        return 0.0
    if t < 60.0:
        return (t - 30.0) / 2.0
    if t < 90.0:
        return 15.0 + (t - 60.0)
    if t < 120.0:
        return 45.0 - (t - 90.0) / 2.0
    if t < 150.0:
        return 30.0 - (t - 120.0)
    if t < 180.0:
        return (t - 150.0) * 2.0
    return 60.0 - (t - 180.0) / 2.0


def drishti_value(from_planet: str, from_lon: float, to_lon: float) -> float:
    theta = (to_lon - from_lon) % 360.0
    v = sputa_drishti(theta)
    for special in _SPECIAL_ASPECTS.get(from_planet, ()):
        d = _ang_dist(theta, special)
        v = max(v, max(0.0, 60.0 - 2.0 * d))
    return v


def _drik_net(target_lon: float, planets: dict, exclude: str | None = None) -> float:
    total = 0.0
    for q in PLANETS_7:
        if q == exclude:
            continue
        v = drishti_value(q, planets[q]["longitude"], target_lon)
        if q in _BENEFICS:
            total += v
        elif q in _MALEFICS:
            total -= v
    return total / 4.0


# ---------------------------------------------------------------------------
# Kala Bala context: vaara day, day/night split, ingress lords
# ---------------------------------------------------------------------------
def _vaara_context(birth_dt, lat: float, lon: float, tz_name: str) -> dict:
    from datetime import time as _time

    def rise_set(d):
        rise, set_ = ephemeris.sunrise_sunset(d, lat, lon, tz_name)
        if rise is None:  # polar fallback: 06:00 / 18:00 civil
            from zoneinfo import ZoneInfo
            tz = ZoneInfo(tz_name)
            rise = birth_dt.__class__.combine(d, _time(6, 0), tzinfo=tz)
            set_ = birth_dt.__class__.combine(d, _time(18, 0), tzinfo=tz)
        return rise, set_

    d = birth_dt.date()
    rise, set_ = rise_set(d)
    if birth_dt < rise:
        prev = d - timedelta(days=1)
        rise_p, set_p = rise_set(prev)
        rise_next = rise
        return {"vaara_date": prev, "is_day": False, "sunrise": rise_p,
                "sunset": set_p, "span_start": set_p, "span_end": rise_next}
    if birth_dt < set_:
        return {"vaara_date": d, "is_day": True, "sunrise": rise,
                "sunset": set_, "span_start": rise, "span_end": set_}
    nxt = d + timedelta(days=1)
    rise_n, _ = rise_set(nxt)
    return {"vaara_date": d, "is_day": False, "sunrise": rise,
            "sunset": set_, "span_start": set_, "span_end": rise_n}


def _ingress_weekday_lord(boundary_lon: float, jd_birth: float, lat: float,
                          lon: float, tz_name: str, max_back_days: float) -> str:
    """Weekday lord of the (sunrise-based) day on which the Sun last
    crossed `boundary_lon` before `jd_birth`."""
    lo, hi = jd_birth - max_back_days, jd_birth

    def g(jd: float) -> float:
        sun, _m = ephemeris.sun_moon_longitudes(jd)
        v = (sun - boundary_lon) % 360.0
        return v - 360.0 if v > 180.0 else v

    for _ in range(60):
        mid = (lo + hi) / 2.0
        if g(mid) < 0:
            lo = mid
        else:
            hi = mid
    from zoneinfo import ZoneInfo
    utc_dt = ephemeris.jd_to_utc_datetime(hi)
    local = utc_dt.astimezone(ZoneInfo(tz_name))
    rise, _s = ephemeris.sunrise_sunset(local.date(), lat, lon, tz_name)
    vaara_date = local.date() - timedelta(days=1) if (rise and local < rise) else local.date()
    return VAARA_LORDS[vaara_date.weekday()]


def _kala_bala(planets: dict, birth_dt, lat: float, lon: float, tz_name: str,
               jd: float, decls: dict) -> tuple[dict, dict]:
    ctx = _vaara_context(birth_dt, lat, lon, tz_name)
    span = (ctx["span_end"] - ctx["span_start"]).total_seconds()
    frac = (birth_dt - ctx["span_start"]).total_seconds() / span if span > 0 else 0.0
    frac = min(max(frac, 0.0), 1.0)

    nathonnatha = {}
    for p in PLANETS_7:
        if p == "Mercury":
            nathonnatha[p] = 60.0
        elif p in ("Sun", "Jupiter", "Venus"):
            nathonnatha[p] = (frac if ctx["is_day"] else 1.0 - frac) * 60.0
        else:  # Moon, Mars, Saturn
            nathonnatha[p] = ((1.0 - frac) if ctx["is_day"] else frac) * 60.0

    elong = (planets["Moon"]["longitude"] - planets["Sun"]["longitude"]) % 360.0
    arc = elong if elong <= 180.0 else 360.0 - elong
    paksha = {}
    for p in PLANETS_7:
        paksha[p] = arc / 3.0 if p in _BENEFICS else 60.0 - arc / 3.0

    third = min(int(frac * 3), 2)
    tribhaga_lords = (["Mercury", "Sun", "Saturn"] if ctx["is_day"]
                      else ["Moon", "Venus", "Mars"])
    tribhaga = {p: 0.0 for p in PLANETS_7}
    tribhaga[tribhaga_lords[third]] = 60.0
    tribhaga["Jupiter"] = 60.0  # Jupiter receives Tribhaga Bala always

    vaara_lord = VAARA_LORDS[ctx["vaara_date"].weekday()]
    if ctx["is_day"]:
        hora_idx = int(frac * 12)
    else:
        hora_idx = 12 + int(frac * 12)
    hora_lord = _HORA_ORDER[(_HORA_ORDER.index(vaara_lord) + hora_idx) % 7]

    sun_lon = planets["Sun"]["longitude"]
    masa_lord = _ingress_weekday_lord((sun_lon // 30.0) * 30.0, jd, lat, lon, tz_name, 40.0)
    abda_lord = _ingress_weekday_lord(0.0, jd, lat, lon, tz_name, 380.0)
    lord_points = {"vaara": (vaara_lord, 45.0), "hora": (hora_lord, 60.0),
                   "masa": (masa_lord, 30.0), "abda": (abda_lord, 15.0)}

    ayana = {}
    for p in PLANETS_7:
        decl = decls[p]
        if p in ("Sun", "Mars", "Jupiter", "Venus"):
            v = (24.0 + decl) / 48.0 * 60.0
        elif p in ("Moon", "Saturn"):
            v = (24.0 - decl) / 48.0 * 60.0
        else:  # Mercury
            v = (24.0 + abs(decl)) / 48.0 * 60.0
        ayana[p] = v * 2.0 if p == "Sun" else v

    kala = {}
    for p in PLANETS_7:
        total = nathonnatha[p] + paksha[p] + tribhaga[p] + ayana[p]
        detail = {"nathonnatha": round(nathonnatha[p], 2), "paksha": round(paksha[p], 2),
                  "tribhaga": round(tribhaga[p], 2), "ayana": round(ayana[p], 2),
                  "vaara": 0.0, "hora": 0.0, "masa": 0.0, "abda": 0.0, "yuddha": 0.0}
        for key, (lord, pts) in lord_points.items():
            if lord == p:
                detail[key] = pts
                total += pts
        detail["total"] = round(total, 2)
        kala[p] = detail
    return kala, {"vaara_lord": vaara_lord, "hora_lord": hora_lord,
                  "masa_lord": masa_lord, "abda_lord": abda_lord,
                  "ayana_raw": ayana, "paksha": paksha}


# ---------------------------------------------------------------------------
# Cheshta Bala (Saravali motion classes)
# ---------------------------------------------------------------------------
def _crosses_sign_boundary(planet: str, jd: float, direction: int) -> bool:
    now = ephemeris.planet_longitudes(jd)[planet]
    speed = now["speed"]
    if (direction > 0 and speed <= 0) or (direction < 0 and speed >= 0):
        return False
    deg = now["degree_in_sign"]
    days = ((30.0 - deg) if direction > 0 else deg) / abs(speed)
    if days > 200.0:
        return False
    later = ephemeris.planet_longitudes(jd + days * 1.05)[planet]
    return later["sign"] != now["sign"]


def _cheshta(planet: str, planets: dict, jd: float, ayana_raw: float, paksha: float) -> float:
    if planet == "Sun":
        return min(max(ayana_raw / 2.0, 0.0), 60.0)  # undoubled Ayana Bala
    if planet == "Moon":
        return paksha
    speed = planets[planet]["speed"]
    if speed < 0:
        return 30.0 if _crosses_sign_boundary(planet, jd, -1) else 60.0
    ratio = abs(speed) / _AVG_SPEED[planet]
    if ratio < 0.10:
        return 15.0   # Vikala (near-stationary)
    if ratio < 0.50:
        return 15.0   # Mandatara (very slow)
    if ratio < 1.00:
        return 30.0   # Manda (slow)
    if ratio < 1.50:
        return 7.5    # Sama (average)
    return 30.0 if _crosses_sign_boundary(planet, jd, +1) else 45.0  # Atichara / Chara


# ---------------------------------------------------------------------------
# Shadbala proper
# ---------------------------------------------------------------------------
def shadbala(planets: dict, lagna_sign: int, cusps: list[float], charts: dict,
             birth_dt, lat: float, lon: float, tz_name: str, jd: float) -> dict:
    decls = ephemeris.declinations(jd)
    kala, kala_meta = _kala_bala(planets, birth_dt, lat, lon, tz_name, jd, decls)

    rows: dict[str, dict] = {}
    for p in PLANETS_7:
        pl = planets[p]
        # --- Sthana Bala ---
        ex_sign, ex_deg = EXALTATION[p][0], EXALTATION[p][1]
        debil_lon = (ex_sign * 30.0 + ex_deg + 180.0) % 360.0
        uccha = _ang_dist(pl["longitude"], debil_lon) / 3.0

        sapta = 0.0
        for v in SAPTA_VARGAS:
            chart_signs = {q: charts[v][q] for q in PLANETS_7}
            deg = pl["degree_in_sign"] if v == "D1" else None
            sapta += _SAPTA_VALUES[dignity_category(p, charts[v][p], chart_signs, deg)]

        d9_sign = charts["D9"][p]
        odd_d1 = pl["sign"] % 2 == 0  # sign index 0 = Aries = 1st (odd) sign
        odd_d9 = d9_sign % 2 == 0
        if p in ("Moon", "Venus"):
            ojayugma = (0.0 if odd_d1 else 15.0) + (0.0 if odd_d9 else 15.0)
        else:
            ojayugma = (15.0 if odd_d1 else 0.0) + (15.0 if odd_d9 else 0.0)

        house = house_of(pl["sign"], lagna_sign)
        kendradi = 60.0 if house in (1, 4, 7, 10) else (30.0 if house in (2, 5, 8, 11) else 15.0)

        drek = int(pl["degree_in_sign"] // 10.0)
        drekkana = 15.0 if ((p in ("Sun", "Mars", "Jupiter") and drek == 0)
                            or (p in ("Moon", "Venus") and drek == 1)
                            or (p in ("Mercury", "Saturn") and drek == 2)) else 0.0

        sthana = uccha + sapta + ojayugma + kendradi + drekkana

        # --- Dig Bala ---
        dig = (180.0 - _ang_dist(pl["longitude"], cusps[_DIG_ZERO_CUSP[p]])) / 3.0

        # --- Cheshta / Naisargika / Drik ---
        cheshta = _cheshta(p, planets, jd, kala_meta["ayana_raw"][p], kala_meta["paksha"][p])
        naisargika = NAISARGIKA[p]
        drik = _drik_net(pl["longitude"], planets, exclude=p)

        total = sthana + dig + kala[p]["total"] + cheshta + naisargika + drik
        rows[p] = {
            "sthana": {"uccha": round(uccha, 2), "saptavargaja": round(sapta, 2),
                       "ojayugma": round(ojayugma, 2), "kendradi": round(kendradi, 2),
                       "drekkana": round(drekkana, 2), "total": round(sthana, 2)},
            "dig": round(dig, 2),
            "kala": kala[p],
            "cheshta": round(cheshta, 2),
            "naisargika": naisargika,
            "drik": round(drik, 2),
            "total_virupas": round(total, 2),
            "rupas": round(total / 60.0, 2),
            "min_rupas": MIN_RUPAS[p],
            "ratio": round(total / 60.0 / MIN_RUPAS[p], 2),
            "ishta": round(math.sqrt(max(uccha, 0.0) * max(cheshta, 0.0)), 2),
            "kashta": round(math.sqrt(max(60.0 - uccha, 0.0) * max(60.0 - cheshta, 0.0)), 2),
        }

    ranked = sorted(PLANETS_7, key=lambda q: rows[q]["rupas"], reverse=True)
    for i, p in enumerate(ranked):
        rows[p]["rank"] = i + 1
    return {
        "planets": rows,
        "kala_lords": {k: kala_meta[k] for k in ("vaara_lord", "hora_lord", "masa_lord", "abda_lord")},
        "strongest": ranked[0],
        "weakest": ranked[-1],
    }


def bhava_bala(planets: dict, lagna_sign: int, cusps: list[float], shadbala_rows: dict) -> list[dict]:
    """Per-house strength: house lord's Shadbala + Drik Bala on the cusp.
    (Dig Bala of houses omitted — see module docstring.)"""
    rows = shadbala_rows["planets"] if "planets" in shadbala_rows else shadbala_rows
    out = []
    for h in range(1, 13):
        sign = (lagna_sign + h - 1) % 12
        lord = SIGN_LORDS[sign]
        lord_rupas = rows[lord]["rupas"]
        drik_rupas = _drik_net(cusps[h - 1], planets) / 60.0
        out.append({
            "house": h, "sign": sign, "lord": lord,
            "lord_bala_rupas": lord_rupas,
            "drik_bala_rupas": round(drik_rupas, 2),
            "total_rupas": round(lord_rupas + drik_rupas, 2),
        })
    return out


def vimshopaka(planets: dict, charts: dict) -> dict:
    out: dict[str, dict] = {}
    for p in PLANETS_7:
        entry = {}
        for scheme, weights in VIMSHOPAKA_SCHEMES.items():
            total = 0.0
            for varga, weight in weights.items():
                chart_signs = {q: charts[varga][q] for q in PLANETS_7}
                deg = planets[p]["degree_in_sign"] if varga == "D1" else None
                cat = dignity_category(p, charts[varga][p], chart_signs, deg)
                total += weight * _VIMSHOPAKA_FRACTIONS[cat]
            entry[scheme] = round(total, 2)
        out[p] = entry
    return out
