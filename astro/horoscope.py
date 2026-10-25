"""Rashi Phal — daily / weekly / monthly Moon-sign horoscope.

Unlike generic sun-sign columns, this is computed from real transits:
each planet's current sign is counted as a house from the reader's
Moon sign (Chandra Lagna), and each life area is rated from which
planets sit in its favourable or difficult houses. The text always
names the actual planets and houses behind the rating, so two signs
never read alike on the same day.

Area rules (houses counted from the Moon sign):
  career:        favourable Jupiter/Sun in 1/5/9/10/11; difficult Saturn/Mars in 6/8/12
  finance:       favourable Jupiter/Venus in 2/5/9/11; difficult Saturn/Rahu in 8/12
  relationships: favourable Venus/Moon in 1/5/7/11; difficult Mars/Saturn in 7/8/12
  health:        favourable Sun/Moon in 1/5/9; difficult Saturn/Mars in 1/6/8/12
Weekly spans use the slow movers at the week start plus the Moon's
sign journey through the week; monthly spans add the month's real
ingress dates (Saturn/Jupiter/Rahu/Mars/Sun).
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from . import ephemeris, transits as transits_module
from .names import PLANET_NE, SIGNS_EN, SIGNS_NE

_AREAS = {
    "career": {
        "en": "Career", "ne": "पेशा",
        "fav": {"Jupiter": {1, 5, 9, 10, 11}, "Sun": {1, 10, 11}, "Mercury": {1, 10, 11}},
        "diff": {"Saturn": {6, 8, 12}, "Mars": {6, 8, 12}},
    },
    "finance": {
        "en": "Finance", "ne": "धन",
        "fav": {"Jupiter": {2, 5, 9, 11}, "Venus": {2, 5, 11}},
        "diff": {"Saturn": {8, 12}, "Rahu": {8, 12}},
    },
    "relationships": {
        "en": "Relationships", "ne": "सम्बन्ध",
        "fav": {"Venus": {1, 5, 7, 11}, "Moon": {1, 5, 7}},
        "diff": {"Mars": {7, 8, 12}, "Saturn": {7, 8, 12}},
    },
    "health": {
        "en": "Health", "ne": "स्वास्थ्य",
        "fav": {"Sun": {1, 5, 9}, "Moon": {1, 5, 9}},
        "diff": {"Saturn": {1, 6, 8, 12}, "Mars": {1, 6, 8, 12}},
    },
}
_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]


def _house_of(sign: int, moon_sign: int) -> int:
    return (sign - moon_sign) % 12 + 1


def _transit_houses(jd: float, moon_sign: int) -> dict[str, dict]:
    planets = ephemeris.planet_longitudes(jd)
    return {
        p: {"sign": planets[p]["sign"],
            "house": _house_of(planets[p]["sign"], moon_sign)}
        for p in _PLANETS
    }


def _rate_area(area: str, houses: dict[str, dict]) -> dict:
    rules = _AREAS[area]
    score = 0
    good, bad = [], []
    for planet, fav_houses in rules["fav"].items():
        if houses[planet]["house"] in fav_houses:
            score += 1
            good.append(planet)
    for planet, diff_houses in rules["diff"].items():
        if houses[planet]["house"] in diff_houses:
            score -= 1
            bad.append(planet)
    rating = "Favourable" if score >= 1 else "Careful" if score < 0 else "Mixed"
    rating_ne = {"Favourable": "शुभ", "Careful": "सावधानी", "Mixed": "मिश्रित"}[rating]
    if good and not bad:
        en = f"{' and '.join(good)} support this area from strong houses — use the momentum."
        ne = f"{' र '.join(PLANET_NE[g] for g in good)} ले यस क्षेत्रलाई बलिया भावबाट साथ दिइरहेका छन् — यो गतिलाई उपयोग गर्नुहोस्।"
    elif bad and not good:
        en = f"{' and '.join(bad)} press on this area — keep plans modest and double-check details."
        ne = f"{' र '.join(PLANET_NE[b] for b in bad)} ले यस क्षेत्रमा दबाब दिइरहेका छन् — योजनाहरू सामान्य राख्नुहोस् र विवरण दोहोर्याएर जाँच गर्नुहोस्।"
    elif good and bad:
        en = f"{' and '.join(good)} help, while {' and '.join(bad)} drag — progress comes with one friction to manage."
        ne = f"{' र '.join(PLANET_NE[g] for g in good)} ले सहयोग गर्छन् भने {' र '.join(PLANET_NE[b] for b in bad)} ले अड्चन ल्याउँछन् — एउटा व्यवस्थापन गर्नुपर्ने घर्षणसहित प्रगति हुन्छ।"
    else:
        en = "No strong planetary push either way — a steady, ordinary stretch for this area."
        ne = "यस क्षेत्रमा कुनै बलियो ग्रहिय दबाब छैन — सामान्य, स्थिर अवधि।"
    return {"rating": rating, "rating_ne": rating_ne, "score": score,
            "supporting": good, "pressing": bad, "text": {"en": en, "ne": ne}}


def horoscope(moon_sign: int, span: str, ref_day: date, tz_name: str) -> dict:
    """Horoscope for `moon_sign` over `span` starting at `ref_day`."""
    if span not in ("daily", "weekly", "monthly"):
        raise ValueError("span must be daily, weekly or monthly")
    tz = ZoneInfo(tz_name)
    if span == "daily":
        start, end = ref_day, ref_day
    elif span == "weekly":
        start, end = ref_day, ref_day + timedelta(days=6)
    else:
        start = ref_day.replace(day=1)
        end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    def jd_noon(d: date) -> float:
        return ephemeris.to_julian_day(datetime.combine(d, time(12, 0), tzinfo=tz))

    houses = _transit_houses(jd_noon(start), moon_sign)
    areas = {a: _rate_area(a, houses) for a in _AREAS}
    transits = {
        p: {"sign": h["sign"], "sign_en": SIGNS_EN[h["sign"]], "sign_ne": SIGNS_NE[h["sign"]],
            "house": h["house"]}
        for p, h in houses.items()
    }

    extra: dict = {}
    if span == "weekly":
        journey = []
        d = start
        while d <= end:
            s = ephemeris.planet_longitudes(jd_noon(d))["Moon"]["sign"]
            if not journey or journey[-1]["sign"] != s:
                journey.append({"date": d.isoformat(), "sign": s,
                                "sign_en": SIGNS_EN[s], "sign_ne": SIGNS_NE[s]})
            d += timedelta(days=1)
        extra["moon_journey"] = journey
    if span == "monthly":
        ingresses = []
        for p in ("Saturn", "Jupiter", "Rahu", "Mars", "Sun"):
            for ing in transits_module.ingress_chain(p, jd_noon(start), jd_noon(end)):
                ingresses.append({"planet": p, "date": ing["date"],
                                  "to_sign": ing["to_sign"],
                                  "to_sign_en": SIGNS_EN[ing["to_sign"]],
                                  "to_sign_ne": SIGNS_NE[ing["to_sign"]]})
        extra["ingresses"] = sorted(ingresses, key=lambda x: x["date"])

    moon_house = houses["Moon"]["house"]
    summary_en = (f"With the Moon in your {moon_house}th house from your Moon sign and "
                  f"Jupiter in the {houses['Jupiter']['house']}th, the {span} rhythm is set "
                  f"by the Moon's movement and the slow planets' houses.")
    summary_ne = (f"चन्द्र तपाईंको चन्द्र राशिबाट {moon_house}औं भावमा र बृहस्पति "
                  f"{houses['Jupiter']['house']}औं भावमा रहेकाले {span} को लय चन्द्रमाको गति र "
                  f"मन्द ग्रहहरूको भावले निर्धारण गर्छ।")
    return {
        "moon_sign": moon_sign,
        "moon_sign_en": SIGNS_EN[moon_sign], "moon_sign_ne": SIGNS_NE[moon_sign],
        "span": span, "start": start.isoformat(), "end": end.isoformat(),
        "transits": transits, "areas": areas,
        "summary": {"en": summary_en, "ne": summary_ne}, **extra,
    }
