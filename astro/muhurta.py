"""Muhurta finder — auspicious timing from classical day divisions.

For each civil day at a place this module computes:
  * Panchang at sunrise (tithi, nakshatra, yoga, karana, vaara).
  * Choghadiya: the day and the night each split into 8 segments with
    rotating lords (Amrit / Shubh / Labh / Char = favourable;
    Rog / Kaal / Udveg = unfavourable). Tables follow the standard
    published weekday rotations.
  * Rahu Kaal: the day's 8th-part segment ruled by weekday
    (Mon 2, Tue 7, Wed 5, Thu 6, Fri 4, Sat 3, Sun 8).
  * Abhijit: the middle muhurta of the day (8th of 15 day-muhurtas),
    traditionally avoided on Wednesdays (flagged, not hidden).
  * Hora: planetary hours in Chaldean order (Saturn, Jupiter, Mars,
    Sun, Venus, Mercury, Moon), beginning with the weekday lord at
    sunrise; 12 day horas and 12 night horas.
  * A day score for a chosen activity: tithi class (Rikta tithis
    4/9/14/19/24/29 are avoided for beginnings), Moon-nakshatra
    suitability for the activity (standard published lists), and
    optional Tara Bala when the querent's birth nakshatra is given
    (taras 2/4/6/8/9 favourable; 1/3/5/7 unfavourable).

Method note (shown in the UI): this is classical guidance, not a
pandit's full muhurta — a full election also weighs Chandra Bala,
Panchaka, the Lagna at the moment, and the querent's dasha. Lists
vary slightly between traditions; the ones used here are the widely
published standard sets.
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from .ephemeris import sunrise_sunset
from .names import NAKSHATRAS_EN, NAKSHATRAS_NE
from .panchang import panchang_at

# Weekday order: Python weekday() Mon=0..Sun=6; tables below are Sun-first.
_DAY_CHOGHADIYA = {
    # Sunday, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday
    0: ["Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg"],
    1: ["Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Char", "Labh", "Amrit"],
    2: ["Rog", "Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog"],
    3: ["Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Char", "Labh"],
    4: ["Shubh", "Rog", "Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh"],
    5: ["Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Char"],
    6: ["Kaal", "Shubh", "Rog", "Udveg", "Char", "Labh", "Amrit", "Kaal"],
}
_NIGHT_CHOGHADIYA = {
    0: ["Shubh", "Amrit", "Char", "Rog", "Kaal", "Labh", "Udveg", "Shubh"],
    1: ["Char", "Rog", "Kaal", "Labh", "Udveg", "Shubh", "Amrit", "Char"],
    2: ["Kaal", "Labh", "Udveg", "Shubh", "Amrit", "Char", "Rog", "Kaal"],
    3: ["Udveg", "Shubh", "Amrit", "Char", "Rog", "Kaal", "Labh", "Udveg"],
    4: ["Amrit", "Char", "Rog", "Kaal", "Labh", "Udveg", "Shubh", "Amrit"],
    5: ["Rog", "Kaal", "Labh", "Udveg", "Shubh", "Amrit", "Char", "Rog"],
    6: ["Labh", "Udveg", "Shubh", "Amrit", "Char", "Rog", "Kaal", "Labh"],
}
GOOD_CHOGHADIYA = {"Amrit", "Shubh", "Labh", "Char"}
# Rahu Kaal segment (1-based) within the day's 8 segments, by weekday Sun-first.
_RAHU_KAAL_SEGMENT = {0: 8, 1: 2, 2: 7, 3: 5, 4: 6, 5: 4, 6: 3}
# Chaldean order for Hora; day starts with the weekday lord.
_CHALDEAN = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
_WEEKDAY_LORD_SUNFIRST = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

# Nakshatra indices (0=Ashwini). Standard published suitability lists.
ACTIVITIES = {
    "marriage": {
        "en": "Marriage", "ne": "विवाह",
        "good_nakshatras": [3, 5, 9, 11, 12, 14, 16, 18, 21, 25, 26],
    },
    "travel": {
        "en": "Travel", "ne": "यात्रा",
        "good_nakshatras": [0, 5, 6, 7, 12, 16, 21, 22, 26],
    },
    "business": {
        "en": "Business / trade", "ne": "व्यापार",
        "good_nakshatras": [0, 3, 5, 6, 7, 12, 13, 14, 16, 21, 22, 26],
    },
    "house": {
        "en": "House construction", "ne": "गृह निर्माण",
        "good_nakshatras": [3, 5, 13, 12, 16, 21, 22, 23, 25, 26],
    },
    "education": {
        "en": "Education / Vidyarambha", "ne": "विद्यारम्भ",
        "good_nakshatras": [0, 6, 7, 12, 13, 14, 21, 22, 23, 26],
    },
    "job": {
        "en": "Starting a job", "ne": "नोकरी सुरु",
        "good_nakshatras": [7, 12, 13, 16, 21, 26],
    },
    "vehicle": {
        "en": "Buying a vehicle", "ne": "वाहन खरिद",
        "good_nakshatras": [0, 3, 5, 7, 12, 13, 16, 21, 26],
    },
    "naming": {
        "en": "Naming ceremony", "ne": "नामकरण",
        "good_nakshatras": [0, 3, 5, 6, 7, 12, 13, 16, 21, 22, 26],
    },
}


def _sunfirst_weekday(d: date) -> int:
    """0=Sunday .. 6=Saturday."""
    return (d.weekday() + 1) % 7


def _segments(start: datetime, end: datetime, n: int, lords: list[str]) -> list[dict]:
    span = (end - start) / n
    out = []
    for i in range(n):
        s = start + span * i
        e = start + span * (i + 1)
        out.append({
            "index": i + 1, "lord": lords[i],
            "good": lords[i] in GOOD_CHOGHADIYA,
            "start": s.isoformat(), "end": e.isoformat(),
        })
    return out


def _tithi_class(tithi_index: int) -> str:
    # Cycle of 5 over 30 tithis: Nanda, Bhadra, Jaya, Rikta, Purna.
    return ["Nanda", "Bhadra", "Jaya", "Rikta", "Purna"][(tithi_index % 5)]


def day_muhurta(day: date, lat: float, lon: float, tz_name: str,
                 activity: str = "marriage", birth_nakshatra: int | None = None) -> dict:
    """Full Muhurta detail for one civil day."""
    tz = ZoneInfo(tz_name)
    rise, set_ = sunrise_sunset(day, lat, lon, tz_name)
    if rise is None or set_ is None:
        rise = datetime.combine(day, time(6, 0), tzinfo=tz)
        set_ = datetime.combine(day, time(18, 0), tzinfo=tz)
    next_rise, _ = sunrise_sunset(day + timedelta(days=1), lat, lon, tz_name)
    if next_rise is None:
        next_rise = datetime.combine(day + timedelta(days=1), time(6, 0), tzinfo=tz)

    wd = _sunfirst_weekday(day)
    day_segs = _segments(rise, set_, 8, _DAY_CHOGHADIYA[wd])
    night_segs = _segments(set_, next_rise, 8, _NIGHT_CHOGHADIYA[wd])
    rahu_idx = _RAHU_KAAL_SEGMENT[wd]
    rahu = day_segs[rahu_idx - 1]
    for s in day_segs:
        s["rahu_kaal"] = (s["index"] == rahu_idx)

    # Abhijit: 8th of 15 day-muhurtas.
    muhurta_len = (set_ - rise) / 15
    abh_start = rise + muhurta_len * 7
    abh_end = rise + muhurta_len * 8

    # Hora: 24 hours from sunrise in Chaldean order, day lord first.
    start_lord = _WEEKDAY_LORD_SUNFIRST[wd]
    i0 = _CHALDEAN.index(start_lord)
    hora_lords = [_CHALDEAN[(i0 + k) % 7] for k in range(24)]
    horas = []
    day_hora_len = (set_ - rise) / 12
    night_hora_len = (next_rise - set_) / 12
    for k in range(12):
        horas.append({"index": k + 1, "part": "day", "lord": hora_lords[k],
                      "start": (rise + day_hora_len * k).isoformat(),
                      "end": (rise + day_hora_len * (k + 1)).isoformat()})
    for k in range(12):
        horas.append({"index": k + 13, "part": "night", "lord": hora_lords[12 + k],
                      "start": (set_ + night_hora_len * k).isoformat(),
                      "end": (set_ + night_hora_len * (k + 1)).isoformat()})

    p = panchang_at(rise, lat, lon, tz_name)
    act = ACTIVITIES.get(activity, ACTIVITIES["marriage"])
    nak = p["nakshatra_index"]
    tithi = p["tithi_index"]
    tclass = _tithi_class(tithi)

    score = 0
    factors: list[dict] = []
    if tclass == "Rikta":
        score -= 2
        factors.append({"en": "Rikta tithi — traditionally avoided for beginnings",
                        "ne": "रिक्ता तिथि — सुरुवातका लागि परम्परागत रूपमा बेवास्ता गरिन्छ", "points": -2})
    elif tclass in ("Nanda", "Jaya", "Purna"):
        score += 1
        factors.append({"en": f"{tclass} tithi — favourable for beginnings",
                        "ne": f"{tclass} तिथि — सुरुवातका लागि शुभ", "points": 1})
    if nak in act["good_nakshatras"]:
        score += 2
        factors.append({"en": f"Moon in {NAKSHATRAS_EN[nak]} — auspicious for {act['en'].lower()}",
                        "ne": f"चन्द्र {NAKSHATRAS_NE[nak]} मा — {act['ne']} का लागि शुभ", "points": 2})
    else:
        factors.append({"en": f"Moon in {NAKSHATRAS_EN[nak]} — not on the preferred list for {act['en'].lower()}",
                        "ne": f"चन्द्र {NAKSHATRAS_NE[nak]} मा — {act['ne']} का लागि रुचाइएको सूचीमा छैन", "points": 0})
    tara = None
    if birth_nakshatra is not None:
        tara = (nak - birth_nakshatra) % 9 + 1
        if tara in (2, 4, 6, 8, 9):
            score += 2
            factors.append({"en": f"Tara Bala {tara} — favourable", "ne": f"ताराबल {tara} — शुभ", "points": 2})
        else:
            score -= 2
            factors.append({"en": f"Tara Bala {tara} — unfavourable", "ne": f"ताराबल {tara} — अशुभ", "points": -2})
    if wd == 3:  # Wednesday
        factors.append({"en": "Abhijit muhurta is traditionally avoided on Wednesdays",
                        "ne": "बुधबार अभिजित् मुहूर्त परम्परागत रूपमा बेवास्ता गरिन्छ", "points": 0})

    grade = "Excellent" if score >= 4 else "Good" if score >= 2 else "Average" if score >= 0 else "Avoid"
    grade_ne = {"Excellent": "उत्तम", "Good": "राम्रो", "Average": "मध्यम", "Avoid": "बेवास्ता गर्नुहोस्"}[grade]
    good_windows = [s for s in day_segs if s["good"] and not s["rahu_kaal"]]

    return {
        "date": day.isoformat(),
        "weekday": day.weekday(),
        "weekday_lord": start_lord,
        "sunrise": rise.isoformat(), "sunset": set_.isoformat(),
        "panchang": p,
        "tithi_class": tclass,
        "nakshatra_en": NAKSHATRAS_EN[nak], "nakshatra_ne": NAKSHATRAS_NE[nak],
        "choghadiya_day": day_segs, "choghadiya_night": night_segs,
        "rahu_kaal": {"start": rahu["start"], "end": rahu["end"]},
        "abhijit": {"start": abh_start.isoformat(), "end": abh_end.isoformat(),
                    "wednesday_note": wd == 3},
        "hora": horas,
        "activity": activity, "score": score, "grade": grade, "grade_ne": grade_ne,
        "factors": factors, "tara": tara,
        "good_windows": [{"start": s["start"], "end": s["end"], "lord": s["lord"]} for s in good_windows],
    }


def muhurta_range(date_from: date, date_to: date, lat: float, lon: float,
                  tz_name: str, activity: str = "marriage",
                  birth_nakshatra: int | None = None) -> dict:
    """Score every day in [date_from, date_to] (max 31 days)."""
    if (date_to - date_from).days > 30 or date_to < date_from:
        raise ValueError("date range must be 1–31 days")
    days = []
    d = date_from
    while d <= date_to:
        days.append(day_muhurta(d, lat, lon, tz_name, activity, birth_nakshatra))
        d += timedelta(days=1)
    ranked = sorted(days, key=lambda x: (-x["score"], x["date"]))
    return {"activity": activity, "days": days, "best": ranked[:5]}
