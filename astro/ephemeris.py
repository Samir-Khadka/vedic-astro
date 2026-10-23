"""Ephemeris layer — Swiss Ephemeris with Lahiri (Chitrapaksha) ayanamsa.

Every higher-level module consumes the plain-dict structures produced here,
so the astronomy lives in exactly one place.
"""
from __future__ import annotations

from datetime import date, datetime, time, timezone
from zoneinfo import ZoneInfo

import swisseph as swe

from .names import NAKSHATRA_SPAN

swe.set_sid_mode(swe.SIDM_LAHIRI)


def _ensure_lahiri() -> None:
    """Re-assert the Lahiri sidereal mode in the CALLING thread.

    pyswisseph keeps the sidereal mode in thread-local state: the
    module-level set_sid_mode() above only affects the thread that
    imports this module. FastAPI/uvicorn serve sync endpoints from a
    threadpool, and those worker threads default to Fagan-Bradley —
    which silently shifted every production longitude by -0.8832 deg
    (found live 2026-10-23: worker-thread ayanamsa 24.7175 vs Lahiri
    23.8342). Every public entry point below therefore re-asserts the
    mode before computing; all swe calls in the codebase funnel
    through this module, so this covers every code path.
    """
    swe.set_sid_mode(swe.SIDM_LAHIRI)


def ayanamsa_ut(jd: float) -> float:
    """Lahiri ayanamsa (degrees) at Julian day `jd` (UT), mode-safe."""
    _ensure_lahiri()
    return swe.get_ayanamsa_ut(jd)

_FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
_SWE_PLANETS = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER, "Venus": swe.VENUS, "Saturn": swe.SATURN,
}


def to_julian_day(local_dt: datetime) -> float:
    """Julian day (UT) for a timezone-aware local datetime."""
    ut = local_dt.astimezone(timezone.utc)
    hour = ut.hour + ut.minute / 60.0 + ut.second / 3600.0 + ut.microsecond / 3.6e9
    return swe.julday(ut.year, ut.month, ut.day, hour)


def make_local_datetime(dob: date, tob: time, tz_name: str) -> datetime:
    return datetime.combine(dob, tob, tzinfo=ZoneInfo(tz_name))


def nakshatra_of(longitude: float) -> tuple[int, int]:
    """Return (nakshatra index 0..26, pada 1..4) for a sidereal longitude."""
    lon = longitude % 360.0
    idx = int(lon // NAKSHATRA_SPAN)
    pada = int((lon - idx * NAKSHATRA_SPAN) // (NAKSHATRA_SPAN / 4.0)) + 1
    return idx, pada


def sign_of(longitude: float) -> int:
    return int((longitude % 360.0) // 30.0)


def degree_in_sign(longitude: float) -> float:
    return (longitude % 360.0) % 30.0


def planet_longitudes(jd: float) -> dict[str, dict]:
    """Sidereal longitudes and speeds for the 9 grahas at Julian day `jd`."""
    _ensure_lahiri()
    out: dict[str, dict] = {}
    for name, pid in _SWE_PLANETS.items():
        res, _ret = swe.calc_ut(jd, pid, _FLAGS)
        lon, speed = res[0], res[3]
        nak, pada = nakshatra_of(lon)
        out[name] = {
            "longitude": lon % 360.0,
            "sign": sign_of(lon),
            "degree_in_sign": degree_in_sign(lon),
            "nakshatra": nak,
            "pada": pada,
            "retrograde": speed < 0,
            "speed": speed,
        }
    # Rahu = TRUE node (the convention Hamro Patro and Jagannatha Hora
    # print, i.e. what Nepali janma-patris use); Ketu is exactly opposite.
    res, _ret = swe.calc_ut(jd, swe.TRUE_NODE, _FLAGS)
    rahu_lon = res[0] % 360.0
    for name, lon in (("Rahu", rahu_lon), ("Ketu", (rahu_lon + 180.0) % 360.0)):
        nak, pada = nakshatra_of(lon)
        out[name] = {
            "longitude": lon,
            "sign": sign_of(lon),
            "degree_in_sign": degree_in_sign(lon),
            "nakshatra": nak,
            "pada": pada,
            "retrograde": True,  # nodes move retrograde by nature
            "speed": res[3] if name == "Rahu" else -res[3],
        }
    return out


def ascendant(jd: float, lat: float, lon: float, house_system: bytes = b"W") -> float:
    """Sidereal ascendant longitude. house_system b'W' whole-sign use (only
    the ascendant point matters); b'P' Placidus for KP cusps."""
    _ensure_lahiri()
    _cusps, ascmc = swe.houses_ex(jd, lat, lon, house_system, swe.FLG_SIDEREAL)
    return ascmc[0] % 360.0


def placidus_cusps(jd: float, lat: float, lon: float) -> list[float]:
    """Sidereal Placidus house cusp longitudes (12), used by KP."""
    _ensure_lahiri()
    cusps, _ascmc = swe.houses_ex(jd, lat, lon, b"P", swe.FLG_SIDEREAL)
    return [c % 360.0 for c in cusps]


def _rise_trans(jd_start: float, lat: float, lon: float, rsmi: int) -> float | None:
    _ensure_lahiri()
    try:
        ret, tret = swe.rise_trans(jd_start, swe.SUN, rsmi, (lon, lat, 0.0), 0.0, 0.0)
        if ret == 0:
            return tret[0]
    except swe.Error:
        pass
    return None


def sunrise_sunset(local_date: date, lat: float, lon: float, tz_name: str) -> tuple[datetime | None, datetime | None]:
    """Local sunrise and sunset datetimes for a civil date at a place."""
    tz = ZoneInfo(tz_name)
    local_midnight = datetime.combine(local_date, time(0, 0), tzinfo=tz)
    jd0 = to_julian_day(local_midnight)
    rise_jd = _rise_trans(jd0, lat, lon, swe.CALC_RISE | swe.BIT_DISC_CENTER)
    set_jd = _rise_trans(jd0, lat, lon, swe.CALC_SET | swe.BIT_DISC_CENTER)

    def to_local(jd: float | None) -> datetime | None:
        if jd is None:
            return None
        y, m, d, h = swe.revjul(jd)
        hh = int(h)
        mm = int((h - hh) * 60)
        ss = int(round((((h - hh) * 60) - mm) * 60))
        if ss == 60:
            ss = 0
            mm += 1
        utc_dt = datetime(y, m, d, hh, mm, ss, tzinfo=timezone.utc)
        return utc_dt.astimezone(tz)

    return to_local(rise_jd), to_local(set_jd)


def sun_moon_longitudes(jd: float) -> tuple[float, float]:
    _ensure_lahiri()
    sun, _ = swe.calc_ut(jd, swe.SUN, _FLAGS)
    moon, _ = swe.calc_ut(jd, swe.MOON, _FLAGS)
    return sun[0] % 360.0, moon[0] % 360.0
