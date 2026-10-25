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

Muhurta v2 (personalised election) adds, on top of the day score:
  * Chandra Bala — the day Moon's sign counted from the querent's
    natal Moon sign (favourable 1/3/6/7/10/11, neutral 2/5/9,
    avoid 4/8/12; the 9th is the position sources split on).
  * Panchaka — the Moon in the last two padas of Dhanishta or in
    Shatabhisha, Purva Bhadrapada, Uttara Bhadrapada or Revati.
    The day's Panchaka type comes from the classical remainder
    rule (tithi + weekday + nakshatra + election Lagna, divided
    by 9): remainders 1 Mrithyu, 2 Agni, 4 Raja, 6 Chora, 8 Roga
    are unfavourable; 3, 5, 7 or 0 are good. The remainder rule is
    traditionally a death/funeral-timing rule; it is used here to
    TYPE the day's Panchaka and is labelled as such.
  * Lagna strength at the elected moment — the first good
    Choghadiya window's start (Abhijit midpoint if there is none):
    Lagna lord dignity, benefics vs malefics in the Lagna sign,
    and the Moon's house from the Lagna.
  * Dasha suitability — the querent's running Vimshottari
    Mahadasha at the election day: favourable if its lord is a
    natural benefic or the Lagna lord, unfavourable if debilitated
    or placed in a dusthana (6/8/12) at birth.
The four are combined with the day score into one election score
with every factor's reasoning shown. This is computation, not a
pandit's consultation.
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from . import ephemeris
from .ephemeris import sunrise_sunset
from .names import (
    EXALTATION, NAKSHATRAS_EN, NAKSHATRAS_NE, NATURAL_BENEFICS,
    NATURAL_MALEFICS, OWN_SIGNS, SIGNS_EN, SIGNS_NE, SIGN_LORDS,
)
from .nakshatra import chandrabala as _chandrabala
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


_PANCHAKA_NAKSHATRAS = {23, 24, 25, 26}  # Shatabhisha .. Revati
_PANCHAKA_TYPE = {1: "Mrithyu", 2: "Agni", 4: "Raja", 6: "Chora", 8: "Roga"}
_PANCHAKA_TYPE_NE = {1: "मृत्यु", 2: "अग्नि", 4: "राजा", 6: "चोर", 8: "रोग"}


def panchaka_check(day: date, lat: float, lon: float, tz_name: str) -> dict:
    """Panchaka state for a civil day (Moon at sunrise).

    Active when the Moon is in the last two padas of Dhanishta or in
    Shatabhisha / Purva Bhadrapada / Uttara Bhadrapada / Revati.
    The type uses the classical remainder rule with the sunrise
    Lagna as the election Lagna (see module notes).
    """
    tz = ZoneInfo(tz_name)
    rise, _set = sunrise_sunset(day, lat, lon, tz_name)
    moment = rise or datetime.combine(day, time(6, 0), tzinfo=tz)
    p = panchang_at(moment, lat, lon, tz_name)
    nak, pada = p["nakshatra_index"], p["nakshatra_pada"]
    active = nak in _PANCHAKA_NAKSHATRAS or (nak == 22 and pada in (3, 4))
    lagna_sign = int(ephemeris.ascendant(ephemeris.to_julian_day(moment), lat, lon, b"W") // 30.0)
    total = (p["tithi_index"] + 1) + (_sunfirst_weekday(day) + 1) + (nak + 1) + (lagna_sign + 1)
    rem = total % 9
    ptype = _PANCHAKA_TYPE.get(rem)
    return {
        "active": active,
        "nakshatra": nak, "nakshatra_en": NAKSHATRAS_EN[nak], "nakshatra_ne": NAKSHATRAS_NE[nak],
        "pada": pada,
        "type": ptype, "type_ne": _PANCHAKA_TYPE_NE.get(rem),
        "remainder": rem,
        "unfavourable": active and ptype is not None,
        "note": {
            "en": ("Panchaka days traditionally bar house roofing, bed-making, fuel storage, "
                   "southward travel and funerals without Shanti rites."),
            "ne": ("पञ्चकका दिनमा परम्परागत रूपमा घरको छाना, खाट बनाउने, इन्धन भण्डारण, "
                   "दक्षिण यात्रा र शान्ति-विधिबिना अन्त्येष्टि गर्नु हुँदैन।"),
        },
    }


def _dignity_simple(planet: str, sign: int) -> str:
    if planet in EXALTATION:
        ex = EXALTATION[planet][0]
        if sign == ex:
            return "exalted"
        if sign == (ex + 6) % 12:
            return "debilitated"
    if planet in OWN_SIGNS and sign in OWN_SIGNS[planet]:
        return "own"
    return "neutral"


def lagna_strength_at(moment: datetime, lat: float, lon: float, tz_name: str) -> dict:
    """Lagna strength at an elected moment."""
    jd = ephemeris.to_julian_day(moment)
    lagna_lon = ephemeris.ascendant(jd, lat, lon, b"W")
    lagna_sign = int(lagna_lon // 30.0)
    lord = SIGN_LORDS[lagna_sign]
    planets = ephemeris.planet_longitudes(jd)
    lord_sign = planets[lord]["sign"]
    lord_dig = _dignity_simple(lord, lord_sign)
    in_lagna = [p for p in planets if planets[p]["sign"] == lagna_sign]
    benefics = [p for p in in_lagna if p in NATURAL_BENEFICS]
    malefics = [p for p in in_lagna if p in NATURAL_MALEFICS]
    moon_house = (planets["Moon"]["sign"] - lagna_sign) % 12 + 1
    if lord_dig in ("exalted", "own") and not malefics:
        verdict, points = "strong", 2
    elif lord_dig == "debilitated" or len(malefics) >= 2 or moon_house in (6, 8, 12):
        verdict, points = "weak", -2
    else:
        verdict, points = "moderate", 0
    return {
        "moment": moment.isoformat(),
        "lagna_sign": lagna_sign, "lagna_sign_en": SIGNS_EN[lagna_sign],
        "lagna_sign_ne": SIGNS_NE[lagna_sign],
        "lagna_lord": lord, "lagna_lord_dignity": lord_dig,
        "planets_in_lagna": in_lagna, "benefics_in_lagna": benefics,
        "malefics_in_lagna": malefics, "moon_house_from_lagna": moon_house,
        "verdict": verdict, "points": points,
    }


def dasha_suitability(dasha_tree: dict, at: datetime,
                      natal_planets: dict, natal_lagna_sign: int) -> dict | None:
    """Running Vimshottari MD at `at`, judged for an election."""
    from .charts import house_of
    from .dasha import period_at

    md, ad = period_at(dasha_tree, at)
    if md is None:
        return None
    lord = md["lord"]
    lord_sign = natal_planets[lord]["sign"]
    lord_dig = _dignity_simple(lord, lord_sign)
    lord_house = house_of(lord_sign, natal_lagna_sign)
    if lord in NATURAL_BENEFICS or lord == SIGN_LORDS[natal_lagna_sign]:
        verdict, points = "favourable", 1
    elif lord_dig == "debilitated" or lord_house in (6, 8, 12):
        verdict, points = "unfavourable", -1
    else:
        verdict, points = "neutral", 0
    return {
        "mahadasha_lord": lord, "antardasha_lord": ad["lord"] if ad else None,
        "mahadasha_start": md["start"].date().isoformat(),
        "mahadasha_end": md["end"].date().isoformat(),
        "lord_dignity": lord_dig, "lord_house_from_lagna": lord_house,
        "verdict": verdict, "points": points,
    }


def day_muhurta(day: date, lat: float, lon: float, tz_name: str,
                 activity: str = "marriage", birth_nakshatra: int | None = None,
                 birth_moon_sign: int | None = None,
                 dasha_tree: dict | None = None,
                 natal_planets: dict | None = None,
                 natal_lagna_sign: int | None = None) -> dict:
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

    # ---- Muhurta v2: personalised election factors ----
    election_factors: list[dict] = []
    election_score = score
    # Chandra Bala (needs the querent's natal Moon sign).
    cb = None
    if birth_moon_sign is not None:
        _sun, moon_lon = ephemeris.sun_moon_longitudes(ephemeris.to_julian_day(rise))
        cb = _chandrabala(birth_moon_sign, int(moon_lon // 30.0))
        pts = {"favourable": 2, "neutral": 0, "avoid": -2}[cb["verdict"]]
        election_score += pts
        election_factors.append({
            "en": f"Chandra Bala {cb['position']} ({cb['verdict']}) — Moon in {cb['transit_moon_sign_en']} from natal {cb['natal_moon_sign_en']}",
            "ne": f"चन्द्रबल {cb['position']} ({cb['verdict']}) — चन्द्र {cb['transit_moon_sign_ne']} मा, जन्म {cb['natal_moon_sign_ne']} बाट",
            "points": pts})
    # Panchaka (always computed).
    pk = panchaka_check(day, lat, lon, tz_name)
    if pk["active"]:
        pts = -3 if activity == "house" else -2
        election_score += pts
        election_factors.append({
            "en": f"Panchaka active (Moon in {pk['nakshatra_en']})" +
                  (f" — {pk['type']} Panchaka" if pk["type"] else " — type favourable by remainder rule"),
            "ne": f"पञ्चक सक्रिय छ (चन्द्र {pk['nakshatra_ne']} मा)" +
                  (f" — {pk['type_ne']} पञ्चक" if pk["type"] else " — शेष नियमअनुसार प्रकार शुभ"),
            "points": pts})
    else:
        election_factors.append({
            "en": "No Panchaka on this day",
            "ne": "यस दिन पञ्चक छैन", "points": 0})
    # Lagna strength at the elected moment.
    if good_windows:
        elected_moment = datetime.fromisoformat(good_windows[0]["start"])
    else:
        elected_moment = abh_start + (abh_end - abh_start) / 2
    ls = lagna_strength_at(elected_moment, lat, lon, tz_name)
    election_score += ls["points"]
    election_factors.append({
        "en": f"Elected-moment Lagna {ls['lagna_sign_en']} (lord {ls['lagna_lord']}, {ls['lagna_lord_dignity']}) — {ls['verdict']}",
        "ne": f"निर्वाचित क्षणको लग्न {ls['lagna_sign_ne']} (स्वामी {ls['lagna_lord']}, {ls['lagna_lord_dignity']}) — {ls['verdict']}",
        "points": ls["points"]})
    # Dasha suitability (needs the querent's birth chart).
    ds = None
    if dasha_tree is not None and natal_planets is not None and natal_lagna_sign is not None:
        ds = dasha_suitability(dasha_tree, elected_moment, natal_planets, natal_lagna_sign)
        if ds is not None:
            election_score += ds["points"]
            election_factors.append({
                "en": f"Dasha at election: {ds['mahadasha_lord']} Mahadasha ({ds['verdict']})",
                "ne": f"निर्वाचनमा दशा: {ds['mahadasha_lord']} महादशा ({ds['verdict']})",
                "points": ds["points"]})
    egrade = ("Excellent" if election_score >= 6 else "Good" if election_score >= 3
              else "Average" if election_score >= 0 else "Avoid")
    egrade_ne = {"Excellent": "उत्तम", "Good": "राम्रो", "Average": "मध्यम", "Avoid": "बेवास्ता गर्नुहोस्"}[egrade]

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
        "election_score": election_score, "election_grade": egrade, "election_grade_ne": egrade_ne,
        "election_factors": election_factors,
        "chandra_bala": cb, "panchaka": pk, "lagna_strength": ls, "dasha_suitability": ds,
    }


def muhurta_range(date_from: date, date_to: date, lat: float, lon: float,
                  tz_name: str, activity: str = "marriage",
                  birth_nakshatra: int | None = None,
                  birth_moon_sign: int | None = None,
                  dasha_tree: dict | None = None,
                  natal_planets: dict | None = None,
                  natal_lagna_sign: int | None = None) -> dict:
    """Score every day in [date_from, date_to] (max 31 days).

    `best` keeps the original day-score ranking (backward compatible);
    `best_election` ranks by the personalised election score.
    """
    if (date_to - date_from).days > 30 or date_to < date_from:
        raise ValueError("date range must be 1–31 days")
    days = []
    d = date_from
    while d <= date_to:
        days.append(day_muhurta(d, lat, lon, tz_name, activity, birth_nakshatra,
                                birth_moon_sign, dasha_tree, natal_planets, natal_lagna_sign))
        d += timedelta(days=1)
    ranked = sorted(days, key=lambda x: (-x["score"], x["date"]))
    ranked_election = sorted(days, key=lambda x: (-x["election_score"], x["date"]))
    return {"activity": activity, "days": days, "best": ranked[:5],
            "best_election": ranked_election[:5]}
