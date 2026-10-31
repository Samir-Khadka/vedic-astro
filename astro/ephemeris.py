"""Ephemeris layer — Swiss Ephemeris with selectable ayanamsa.

Every higher-level module consumes the plain-dict structures produced here,
so the astronomy lives in exactly one place. The ayanamsa (Lahiri default;
Raman / Krishnamurti / Yukteshwar selectable) is held thread-safely in
astro.ayanamsa and re-asserted in every public entry point, because
pyswisseph keeps the sidereal mode in thread-local state (see the
2026-10-23 worker-thread ayanamsa bug: Fagan-Bradley silently shifted
production longitudes by -0.8832 deg).
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

import swisseph as swe

from . import ayanamsa as ayanamsa_module
from .names import NAKSHATRA_SPAN

_ensure_ayanamsa = ayanamsa_module.ensure_ayanamsa

# House systems for the bhava cusps. KP always uses Placidus (doctrinal),
# so placidus_cusps() stays as the dedicated KP entry point.
HOUSE_SYSTEMS: dict[str, tuple[str, bytes]] = {
    "placidus": ("Placidus", b"P"),
    "equal": ("Equal house", b"E"),
    "whole": ("Whole sign", b"W"),
    "sripati": ("Sripati", b"S"),
}
DEFAULT_HOUSE_SYSTEM = "placidus"


def validate_house_system(name: str | None) -> str:
    key = (name or DEFAULT_HOUSE_SYSTEM).strip().lower()
    if key not in HOUSE_SYSTEMS:
        raise ValueError(
            f"Unknown house system '{name}'. Supported: {', '.join(sorted(HOUSE_SYSTEMS))}."
        )
    return key


def ayanamsa_ut(jd: float) -> float:
    """Ayanamsa (degrees) at Julian day `jd` (UT) under the current mode."""
    return ayanamsa_module.ayanamsa_value_ut(jd)

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
    _ensure_ayanamsa()
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
    _ensure_ayanamsa()
    _cusps, ascmc = swe.houses_ex(jd, lat, lon, house_system, swe.FLG_SIDEREAL)
    return ascmc[0] % 360.0


def placidus_cusps(jd: float, lat: float, lon: float) -> list[float]:
    """Sidereal Placidus house cusp longitudes (12). KP always uses these."""
    return house_cusps(jd, lat, lon, "placidus")


def house_cusps(jd: float, lat: float, lon: float, system: str = "placidus") -> list[float]:
    """Sidereal house cusp longitudes (12) under the chosen house system."""
    _ensure_ayanamsa()
    key = validate_house_system(system)
    flag = HOUSE_SYSTEMS[key][1]
    cusps, _ascmc = swe.houses_ex(jd, lat, lon, flag, swe.FLG_SIDEREAL)
    return [c % 360.0 for c in cusps]


def _rise_trans(jd_start: float, lat: float, lon: float, rsmi: int) -> float | None:
    _ensure_ayanamsa()
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
        # Timedelta arithmetic normalises every rollover (seconds -> 60
        # flipping the minute to 60, minute -> 60 flipping the hour, hour
        # -> 24 flipping the day), which the manual hh/mm/ss split above
        # could not: a revjul hour like 23.9999976... raised
        # "ValueError: minute must be in 0..59".
        return jd_to_utc_datetime(jd).astimezone(tz)

    return to_local(rise_jd), to_local(set_jd)


def sun_moon_longitudes(jd: float) -> tuple[float, float]:
    _ensure_ayanamsa()
    sun, _ = swe.calc_ut(jd, swe.SUN, _FLAGS)
    moon, _ = swe.calc_ut(jd, swe.MOON, _FLAGS)
    return sun[0] % 360.0, moon[0] % 360.0


def declinations(jd: float) -> dict[str, float]:
    """Equatorial declination (degrees, +north) of the 7 grahas at `jd`.

    Needed for Ayana Bala. Declination is a tropical/equatorial quantity,
    so no ayanamsa is involved; the sidereal flag is harmless here.
    """
    _ensure_ayanamsa()
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_EQUATORIAL
    out: dict[str, float] = {}
    for name, pid in _SWE_PLANETS.items():
        res, _ret = swe.calc_ut(jd, pid, flags)
        out[name] = res[1]
    return out


def planet_longitude_at(name: str, jd: float) -> float:
    """Sidereal longitude of one graha at an arbitrary Julian day."""
    return planet_longitudes(jd)[name]["longitude"]


def jd_to_utc_datetime(jd: float) -> datetime:
    """Timezone-aware UTC datetime for a Julian day."""
    y, m, d, h = swe.revjul(jd)
    base = datetime(y, m, d, tzinfo=timezone.utc)
    return base + timedelta(hours=h)


def jd_to_date_str(jd: float) -> str:
    dt = jd_to_utc_datetime(jd)
    return dt.date().isoformat()
