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

from datetime import date, datetime, time, timedelta
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


# Ritu (season) and ayana from the sidereal Sun sign, classical mapping:
# two signs per ritu; Uttarayana while the Sun travels Makara -> Mithuna
# (signs 9..2), Dakshinayana while it travels Karka -> Dhanus (3..8).
_RITU = [
    ("Vasant", "वसन्त"), ("Grishma", "ग्रीष्म"), ("Varsha", "वर्षा"),
    ("Sharad", "शरद्"), ("Hemant", "हेमन्त"), ("Shishir", "शिशिर"),
]
_RITU_SIGN = {11: 0, 0: 0, 1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3,
              7: 4, 8: 4, 9: 5, 10: 5}


def ritu_ayana(sun_sign: int) -> dict:
    """Ritu + ayana names for a sidereal Sun sign index 0..11."""
    ritu_en, ritu_ne = _RITU[_RITU_SIGN[sun_sign % 12]]
    if sun_sign % 12 in (9, 10, 11, 0, 1, 2):
        ayana_en, ayana_ne = "Uttarayana", "उत्तरायण"
    else:
        ayana_en, ayana_ne = "Dakshinayana", "दक्षिणायण"
    return {"ritu_en": ritu_en, "ritu_ne": ritu_ne,
            "ayana_en": ayana_en, "ayana_ne": ayana_ne}


def _limb_indices(sun: float, moon: float) -> tuple[int, int, int, str]:
    """(tithi, nakshatra, yoga, karana) for sidereal Sun/Moon longitudes."""
    elong = (moon - sun) % 360.0
    nak_idx, _pada = nakshatra_of(moon)
    yoga_idx = int(((sun + moon) % 360.0) // (360.0 / 27.0))
    return (int(elong // 12.0), nak_idx, yoga_idx,
            karana_of(int(elong // 6.0)))


def day_detail(day: date, lat: float, lon: float, tz_name: str) -> dict:
    """Full patro day detail for one civil date, all values computed here.

    Base values are evaluated at sunrise (classical convention, same as
    daily_panchang); transitions are found by stepping the ephemeris in
    10-minute steps from sunrise to the next sunrise and bisecting each
    index change to ~1 minute. A transition is reported only when actually
    found — nothing is guessed. Planet positions are sidereal (Lahiri),
    at sunrise, in sign:degree:minute:second form. Moonrise/moonset are
    the events falling inside the civil day, or None when there is none.
    The BS date is None outside the BS table's range (the AD detail
    still works there).
    """
    from .ephemeris import moon_rise_set, planet_longitudes

    tz = ZoneInfo(tz_name)
    rise, set_ = sunrise_sunset(day, lat, lon, tz_name)
    base = rise if rise is not None else datetime.combine(day, time(6, 0), tzinfo=tz)
    next_rise, _next_set = sunrise_sunset(day + timedelta(days=1), lat, lon, tz_name)
    end = next_rise if next_rise is not None else base + timedelta(days=1)
    p = panchang_at(base, lat, lon, tz_name)
    sun, moon = sun_moon_longitudes(to_julian_day(base))
    sun_sign = int(sun // 30.0)
    moon_sign = int(moon // 30.0)

    # Step once, deriving all four limbs from the same Sun/Moon pair.
    step = timedelta(minutes=10)
    cur = _limb_indices(sun, moon)
    transitions = {"tithi": [], "nakshatra": [], "yoga": [], "karana": []}
    keys = ("tithi", "nakshatra", "yoga", "karana")

    def indices_at(moment: datetime) -> tuple[int, int, int, str]:
        s, m = sun_moon_longitudes(to_julian_day(moment))
        return _limb_indices(s, m)

    t = base + step
    while t <= end:
        nxt = indices_at(t)
        if nxt != cur:
            for ki, key in enumerate(keys):
                if nxt[ki] == cur[ki]:
                    continue
                # Bisect the change inside (t - step, t] to ~1 minute.
                lo, hi = t - step, t
                while (hi - lo) > timedelta(minutes=1):
                    mid = lo + (hi - lo) / 2
                    if indices_at(mid)[ki] == cur[ki]:
                        lo = mid
                    else:
                        hi = mid
                trans = {"at": hi.isoformat(), "next_day": hi.date() != day}
                if key == "karana":
                    trans["to_name"] = nxt[ki]
                else:
                    trans["to_index"] = nxt[ki]
                transitions[key].append(trans)
            cur = nxt
        t += step

    moonrise, moonset = moon_rise_set(day, lat, lon, tz_name)
    try:
        from .bs_calendar import ad_to_bs
        bs = ad_to_bs(day)
    except ValueError:
        bs = None
    planets = []
    for name in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus",
                 "Saturn", "Rahu", "Ketu"):
        pl = planet_longitudes(to_julian_day(base))[name]
        deg_total = pl["degree_in_sign"]
        d = int(deg_total)
        mnt = int((deg_total - d) * 60)
        sec = int(round(((deg_total - d) * 60 - mnt) * 60))
        if sec == 60:
            sec, mnt = 0, mnt + 1
        if mnt == 60:
            mnt, d = 0, d + 1
        planets.append({
            "name": name, "sign": pl["sign"], "degree": d,
            "minute": mnt, "second": sec,
            "dms": f"{pl['sign']}:{d}:{mnt}:{sec}",
            "longitude": pl["longitude"],
        })
    out = {
        "date": day.isoformat(),
        "weekday": day.weekday(),
        "bs": bs,
        "sunrise": rise.isoformat() if rise else None,
        "sunset": set_.isoformat() if set_ else None,
        "moonrise": moonrise.isoformat() if moonrise else None,
        "moonset": moonset.isoformat() if moonset else None,
        "paksha": p["paksha"],
        "tithi_index": p["tithi_index"],
        "tithi_transitions": transitions["tithi"],
        "nakshatra_index": p["nakshatra_index"],
        "nakshatra_pada": p["nakshatra_pada"],
        "nakshatra_transitions": transitions["nakshatra"],
        "yoga_index": p["yoga_index"],
        "yoga_transitions": transitions["yoga"],
        "karana": p["karana"],
        "karana_transitions": transitions["karana"],
        "moon_sign": moon_sign,
        "sun_sign": sun_sign,
        "planets": planets,
    }
    out.update(ritu_ayana(sun_sign))
    return out
