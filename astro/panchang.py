"""Panchang — the five limbs of the Vedic day: tithi, nakshatra, yoga,
karana and vaara, computed at local sunrise (the classical convention),
plus the lunar month (Maas).

Lunar-month convention (documented, not hidden): Amanta. A lunar month
runs from one Amavasya (new moon) to the next. It is named from the
sidereal Sun sign at the Purnima (full moon) inside it — Mesha -> Chaitra,
Vrishabha -> Vaishakha, and so on — which is the same naming as the
classical Purnima-nakshatra rule (the full Moon opposite a Mesha Sun
sits in Chitra, opposite a Vrishabha Sun in Vishakha, etc.). The Sun-sign
form is used because the Moon can cross a nakshatra boundary on Purnima
day itself, which would otherwise name the month off by one. Under the
Purnimanta convention used in parts of North India the same
Krishna-paksha days carry the *next* month's name, so a Krishna-paksha
date's month differs by one between conventions; Shukla-paksha months
agree. The API therefore always reports the convention alongside the
month. Adhik Maas (an extra month with no Sankranti) is not
distinguished in this version.
"""
from __future__ import annotations

from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from .ephemeris import nakshatra_of, sunrise_sunset, sun_moon_longitudes, to_julian_day

_MOVABLE = ["Bava", "Balava", "Kaulava", "Taitila", "Garaja", "Vanija", "Vishti"]

LUNAR_MONTHS_EN = ["Chaitra", "Vaishakha", "Jyeshtha", "Ashadha", "Shravana",
                   "Bhadrapada", "Ashwin", "Kartika", "Margashirsha", "Pausha",
                   "Magha", "Phalguna"]
LUNAR_MONTHS_NE = ["चैत्र", "वैशाख", "ज्येष्ठ", "आषाढ", "श्रावण",
                   "भाद्र", "आश्विन", "कार्तिक", "मार्गशीर्ष", "पौष",
                   "माघ", "फाल्गुन"]
def _noon_sky(day, tz_name):
    """(tithi_index, nakshatra_index, sun_sign) at local noon on `day`."""
    tz = ZoneInfo(tz_name)
    moment = datetime.combine(day, time(12, 0), tzinfo=tz)
    sun, moon = sun_moon_longitudes(to_julian_day(moment))
    elong = (moon - sun) % 360.0
    nak_idx, _pada = nakshatra_of(moon)
    return int(elong // 12.0), nak_idx, int(sun // 30.0)


def lunar_month_at(moment: datetime, lat: float, lon: float, tz_name: str) -> dict:
    """Amanta lunar month containing `moment`'s civil day.

    Finds the enclosing Amavasya-to-Amavasya interval, then names the
    month from the Purnima nakshatra inside it. If that nakshatra is
    unexpectedly outside the classical map, falls back to the Sun's
    sign at the closing Amavasya (Mesha -> Chaitra, etc.), which names
    the same month in the normal case.
    """
    from datetime import timedelta

    base = moment.date()
    # Amanta month starts on Shukla Pratipada: the first day whose noon
    # tithi is 0 after a Krishna Chaturdashi/Amavasya (28 or 29). A tithi
    # can be skipped at noon sampling, so the boundary is the wrap
    # itself, not a noon tithi of exactly 29.
    def _is_month_start(d):
        prev = _noon_sky(d - timedelta(days=1), tz_name)[0]
        return _noon_sky(d, tz_name)[0] == 0 and prev >= 28
    month_start = None
    for k in range(0, 33):
        d = base - timedelta(days=k)
        if _is_month_start(d):
            month_start = d
            break
    month_end = None
    for k in range(1, 33):
        d = base + timedelta(days=k)
        if _is_month_start(d):
            month_end = d - timedelta(days=1)
            break
    if month_start is None or month_end is None:
        raise ValueError("could not bracket the lunar month")
    purnima_nak = None
    d = month_start
    while d <= month_end:
        tithi, nak, _sun = _noon_sky(d, tz_name)
        if tithi == 14:
            # Nakshatra at the exact Purnima moment, not at noon: the
            # Moon can cross a nakshatra boundary on Purnima day, and
            # noon sampling would then name the wrong month. Bisect
            # the elongation (168 -> 192 deg across the day) to 180.
            tz = ZoneInfo(tz_name)
            lo = datetime.combine(d - timedelta(days=1), time(12, 0), tzinfo=tz)
            hi = datetime.combine(d + timedelta(days=1), time(12, 0), tzinfo=tz)
            def _elong_at(m):
                s_, m_ = sun_moon_longitudes(to_julian_day(m))
                return (m_ - s_) % 360.0
            for _ in range(24):
                mid = lo + (hi - lo) / 2
                if _elong_at(mid) < 180.0:
                    lo = mid
                else:
                    hi = mid
            purnima_sun, m_lon = sun_moon_longitudes(to_julian_day(hi))
            purnima_nak, _pada = nakshatra_of(m_lon)
            break
        d += timedelta(days=1)
    if "purnima_sun" not in locals():
        # A short Purnima tithi can be skipped at noon sampling (no day
        # with tithi 14). Find the 180-degree elongation crossing in
        # the month instead and take the Sun there.
        tz = ZoneInfo(tz_name)
        def _elong_at(m):
            s_, m_ = sun_moon_longitudes(to_julian_day(m))
            return (m_ - s_) % 360.0
        lo = hi = None
        d = month_start
        while d <= month_end:
            a = _elong_at(datetime.combine(d, time(12, 0), tzinfo=tz))
            b = _elong_at(datetime.combine(d + timedelta(days=1), time(12, 0), tzinfo=tz))
            if a < 180.0 <= b:
                lo = datetime.combine(d, time(12, 0), tzinfo=tz)
                hi = datetime.combine(d + timedelta(days=1), time(12, 0), tzinfo=tz)
                break
            d += timedelta(days=1)
        if lo is None:
            raise ValueError("could not locate Purnima in the lunar month")
        for _ in range(24):
            mid = lo + (hi - lo) / 2
            if _elong_at(mid) < 180.0:
                lo = mid
            else:
                hi = mid
        purnima_sun, _m_lon = sun_moon_longitudes(to_julian_day(hi))
        purnima_nak, _pada = nakshatra_of(_m_lon)
    # Name from the sidereal Sun sign at the exact Purnima moment
    # (0=Mesha -> Chaitra, 1=Vrishabha -> Vaishakha, ...).
    idx = int(purnima_sun // 30.0) + 1
    return {
        "lunar_month_index": idx,
        "lunar_month_en": LUNAR_MONTHS_EN[idx - 1],
        "lunar_month_ne": LUNAR_MONTHS_NE[idx - 1],
        "lunar_month_convention": "amanta",
        "purnima_nakshatra_index": purnima_nak,
    }


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
    lm = lunar_month_at(moment, lat, lon, tz_name)
    return {
        "tithi_index": tithi_idx,
        "paksha": "Shukla" if tithi_idx < 15 else "Krishna",
        "nakshatra_index": nak_idx,
        "nakshatra_pada": pada,
        "yoga_index": yoga_idx,
        "karana": karana_of(half_idx),
        "weekday": moment.weekday(),
        "lunar_month_index": lm["lunar_month_index"],
        "lunar_month_en": lm["lunar_month_en"],
        "lunar_month_ne": lm["lunar_month_ne"],
        "lunar_month_convention": lm["lunar_month_convention"],
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
