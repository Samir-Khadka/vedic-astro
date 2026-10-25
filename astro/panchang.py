"""Panchang — the five limbs of the Vedic day: tithi, nakshatra, yoga,
karana and vaara, computed at local sunrise (the classical convention)."""
from __future__ import annotations

from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from .ephemeris import nakshatra_of, sunrise_sunset, sun_moon_longitudes, to_julian_day

_MOVABLE = ["Bava", "Balava", "Kaulava", "Taitila", "Garaja", "Vanija", "Vishti"]


def karana_of(half_tithi_index: int) -> str:
    """Karana name for half-tithi index 0..59 across the lunar month."""
    h = half_tithi_index % 60
    if h == 0:
        return "Kimstughna"
    if h == 57:
        return "Shakuni"
    if h == 58:
        return "Chatushpada"
    if h == 59:
        return "Naga"
    return _MOVABLE[(h - 1) % 7]


def panchang_at(moment: datetime, lat: float, lon: float, tz_name: str) -> dict:
    jd = to_julian_day(moment)
    sun, moon = sun_moon_longitudes(jd)
    elong = (moon - sun) % 360.0
    tithi_idx = int(elong // 12.0)  # 0..29
    half_idx = int(elong // 6.0)    # 0..59
    nak_idx, pada = nakshatra_of(moon)
    yoga_idx = int(((sun + moon) % 360.0) // (360.0 / 27.0))
    return {
        "tithi_index": tithi_idx,
        "paksha": "Shukla" if tithi_idx < 15 else "Krishna",
        "nakshatra_index": nak_idx,
        "nakshatra_pada": pada,
        "yoga_index": yoga_idx,
        "karana": karana_of(half_idx),
        "weekday": moment.weekday(),
    }


def daily_panchang(day: date, lat: float, lon: float, tz_name: str) -> dict:
    """Panchang for a civil date, evaluated at that day's sunrise."""
    rise, set_ = sunrise_sunset(day, lat, lon, tz_name)
    tz = ZoneInfo(tz_name)
    if rise is not None:
        moment = rise
    else:  # polar fallback: local 6 AM
        moment = datetime.combine(day, time(6, 0), tzinfo=tz)
    p = panchang_at(moment, lat, lon, tz_name)
    p["date"] = day.isoformat()
    p["sunrise"] = rise.isoformat() if rise else None
    p["sunset"] = set_.isoformat() if set_ else None
    return p


def month_panchang(year: int, month: int, lat: float, lon: float, tz_name: str) -> dict:
    """Panchang for every day of a calendar month, with markers.

    Markers are computed, not looked up: Ekadashi (tithi 11/26),
    Purnima (15), Amavasya (30), and Sankranti (the Sun's sign
    changes vs the previous day). Festival dates that depend on
    regional calendars (Dashain, Tihar, etc.) are NOT guessed here —
    only these astronomical markers are shown.
    """
    from datetime import timedelta

    from .ephemeris import sun_moon_longitudes, to_julian_day

    first = date(year, month, 1)
    nxt = (first + timedelta(days=32)).replace(day=1)
    days = []
    prev_sun_sign = None
    d = first
    while d < nxt:
        p = daily_panchang(d, lat, lon, tz_name)
        sun, _moon = sun_moon_longitudes(to_julian_day(
            datetime.combine(d, time(12, 0), tzinfo=ZoneInfo(tz_name))))
        sun_sign = int(sun // 30.0)
        markers = []
        if p["tithi_index"] in (10, 25):
            markers.append("Ekadashi")
        if p["tithi_index"] == 14:
            markers.append("Purnima")
        if p["tithi_index"] == 29:
            markers.append("Amavasya")
        if prev_sun_sign is not None and sun_sign != prev_sun_sign:
            markers.append("Sankranti")
        p["sun_sign"] = sun_sign
        p["markers"] = markers
        days.append(p)
        prev_sun_sign = sun_sign
        d += timedelta(days=1)
    return {"year": year, "month": month, "days": days}
