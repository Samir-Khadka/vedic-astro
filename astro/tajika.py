"""Tajika (annual-chart) system — yogas, Sahams and the Panchadhikari
Year-Lord election, computed from the Varshphal (solar-return) chart.

Sources and method notes (our own wording of the published rules):

* Tajika aspects are the five classical aspects — conjunction 0 deg,
  60 deg, 90 deg, 120 deg and 180 deg — judged within an orb. The
  classical Deeptamsa (orb) differs per planet; this implementation
  uses one documented simplification, an 8-degree orb for every
  aspect, so every result is reproducible.
* Ithasala: the faster of two planets is APPLYING toward an aspect
  with the slower one (the angular distance to the aspect shrinks
  over the next day). Isharpha/Eesarpha: the faster planet is
  SEPARATING from the aspect (distance grows). Applying vs
  separating is judged by linear extrapolation of the two planets'
  signed daily speeds — this handles retrograde motion correctly.
* Nakta (translation of light): two planets with no mutual aspect,
  but a third planet faster than both aspects both of them.
* Yamaya (collection of light): two planets with no mutual aspect,
  but both are in Ithasala (applying) with one common slower planet.
* Manau: an Ithasala spoiled because Mars or Saturn falls within
  orb of an aspect to the faster (light-giving) planet.
* Kambula / Gairi-Kambula: the simplified Moon reading — the Moon in
  Ithasala is Kambula (fortune), the Moon in Isharpha is Gairi-Kambula
  (unfavourable circumstances). Flagged as simplified: the full
  classical Kambula doctrine has further conditions.
* Ikbala: all seven visible planets in kendra (1, 4, 7, 10) or
  panaphara (2, 5, 8, 11) houses of the annual chart, none in
  apoklima (3, 6, 9, 12). Induvara: all seven in apoklimas.
  Only the seven visible grahas are used for Tajika yogas; Rahu and
  Ketu have no Tajika aspect role in this implementation.
* Sahams (annual-chart sensitive points, formula A - B + Lagna):
  Punya (fortune) — day chart: Moon - Sun + Lagna; night chart:
  Sun - Moon + Lagna. Vivaha (marriage): Venus - Saturn + Lagna
  (day and night alike). Yasas (fame): Jupiter - Punya + Lagna.
  Mahatmya (greatness): Punya - Mars + Lagna. Some traditions add
  one sign (+30 deg) to derived Sahams when the third point does not
  lie between the other two; this implementation uses the direct
  formula and says so.
* Panchadhikari (five-officer) Year-Lord election (Tajika Neelakanthi
  ch. 4 as published in modern guides): the five candidates are the
  lords of (1) the natal Lagna, (2) the Muntha, (3) the Varsha Lagna,
  (4) the day or night (lord of the Sun's sign at the return if the
  return falls in daytime, else lord of the Moon's sign), and (5) the
  triplicity of the Varsha Lagna's sign (Dorothean day/night table).
  Only candidates forming a Tajika aspect to the Varsha Lagna degree
  qualify; among qualifiers the highest simplified Pancha Vargeeya
  Bala wins (dignity points + house points — a transparent
  approximation of the classical five-fold strength, which in full
  needs the divisional charts). If no candidate aspects the Lagna,
  the classical default applies: the Muntha lord is the Year Lord.
"""
from __future__ import annotations

from .charts import house_of
from .names import (
    HOUSE_NAMES_EN, HOUSE_NAMES_NE, HOUSE_THEMES_EN, HOUSE_THEMES_NE,
    PLANET_NE, SIGNS_EN, SIGNS_NE, SIGN_LORDS,
)

ORB = 8.0
ASPECTS = (0.0, 60.0, 90.0, 120.0, 180.0)
GRAHAS_7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
KENDRA = {1, 4, 7, 10}
PANAPHARA = {2, 5, 8, 11}
APOKLIMA = {3, 6, 9, 12}

# Dorothean triplicity lords: element -> (day lord, night lord).
_TRIPLICITY = {
    "fire": ("Sun", "Jupiter"),
    "earth": ("Venus", "Moon"),
    "air": ("Saturn", "Mercury"),
    "water": ("Mars", "Moon"),
}
_ELEMENT_OF_SIGN = {
    0: "fire", 4: "fire", 8: "fire",
    1: "earth", 5: "earth", 9: "earth",
    2: "air", 6: "air", 10: "air",
    3: "water", 7: "water", 11: "water",
}
_DIGNITY_POINTS = {"exalted": 20, "own": 15, "neutral": 7, "debilitated": 2}


def _bi(en: str, ne: str) -> dict:
    return {"en": en, "ne": ne}


def _aspect_distance(lon_a: float, lon_b: float) -> tuple[float, float]:
    """(distance to the nearest Tajika aspect angle, that angle)."""
    sep = abs((lon_a - lon_b) % 360.0)
    sep = min(sep, 360.0 - sep)
    angle = min(ASPECTS, key=lambda a: abs(sep - a))
    return abs(sep - angle), angle


def _in_aspect(lon_a: float, lon_b: float) -> bool:
    return _aspect_distance(lon_a, lon_b)[0] <= ORB


def _applying(faster_lon: float, faster_speed: float,
              slower_lon: float, slower_speed: float) -> bool:
    """True if the faster planet moves TOWARD the aspect with the slower
    planet over the next day (linear extrapolation of signed speeds)."""
    d0, _ = _aspect_distance(faster_lon, slower_lon)
    d1, _ = _aspect_distance(faster_lon + faster_speed, slower_lon + slower_speed)
    return d1 < d0


def _dignity(planet: str, sign: int) -> str:
    from .names import EXALTATION, OWN_SIGNS

    if planet in EXALTATION:
        ex = EXALTATION[planet][0]
        if sign == ex:
            return "exalted"
        if sign == (ex + 6) % 12:
            return "debilitated"
    if planet in OWN_SIGNS and sign in OWN_SIGNS[planet]:
        return "own"
    return "neutral"


def _house_points(house: int) -> int:
    if house in KENDRA:
        pts = 10
    elif house in (5, 9):
        pts = 8
    elif house in (2, 8, 11):
        pts = 5
    else:
        pts = 2
    if house in (6, 8, 12):
        pts = max(0, pts - 3)
    return pts


def tajika_yogas(planets: dict, varsha_lagna_sign: int) -> dict:
    """Pair yogas + chart patterns for one annual chart.

    `planets`: ephemeris dict (needs longitude + speed per planet).
    """
    p7 = {p: planets[p] for p in GRAHAS_7 if p in planets}
    houses = {p: house_of(p7[p]["sign"], varsha_lagna_sign) for p in p7}
    pairs: list[dict] = []
    ithasala_pairs: list[tuple[str, str]] = []  # (faster, slower)
    isharpha_pairs: list[tuple[str, str]] = []

    names = list(p7)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            if not _in_aspect(p7[a]["longitude"], p7[b]["longitude"]):
                continue
            fa, fb = (a, b) if abs(p7[a]["speed"]) >= abs(p7[b]["speed"]) else (b, a)
            if _applying(p7[fa]["longitude"], p7[fa]["speed"],
                         p7[fb]["longitude"], p7[fb]["speed"]):
                ithasala_pairs.append((fa, fb))
                pairs.append({
                    "yoga": "Ithasala", "yoga_ne": "इत्थसाल",
                    "planets": [fa, fb],
                    "favourable": True,
                    "reading": _bi(
                        f"{fa} (faster) applies to {fb} — the matter signified by this pair comes to fulfilment in the year.",
                        f"{fa} (छिटो) ले {fb} तर्फ गमन गर्छ — यस जोडीले देखाएको कुरा वर्षभित्र पूरा हुन्छ।"),
                })
            else:
                isharpha_pairs.append((fa, fb))
                pairs.append({
                    "yoga": "Isharpha", "yoga_ne": "ईसरफ",
                    "planets": [fa, fb],
                    "favourable": False,
                    "reading": _bi(
                        f"{fa} (faster) separates from {fb} — the chance signified by this pair slips away in the year.",
                        f"{fa} (छिटो) {fb} बाट टाढिन्छ — यस जोडीले देखाएको अवसर वर्षमा चिप्लिन्छ।"),
                })

    # Nakta: no mutual aspect, but a faster planet aspects both.
    # Yamaya: no mutual aspect, but both apply to one common slower planet.
    ithasala_set = {frozenset(p) for p in ithasala_pairs}
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            if _in_aspect(p7[a]["longitude"], p7[b]["longitude"]):
                continue
            for c in names:
                if c in (a, b):
                    continue
                if (abs(p7[c]["speed"]) > abs(p7[a]["speed"])
                        and abs(p7[c]["speed"]) > abs(p7[b]["speed"])
                        and _in_aspect(p7[c]["longitude"], p7[a]["longitude"])
                        and _in_aspect(p7[c]["longitude"], p7[b]["longitude"])):
                    pairs.append({
                        "yoga": "Nakta", "yoga_ne": "नक्त",
                        "planets": [a, b], "via": c,
                        "favourable": True,
                        "reading": _bi(
                            f"{a} and {b} do not aspect each other, but faster {c} aspects both — the result comes through a third person.",
                            f"{a} र {b} ले एक-अर्कालाई दृष्टि दिँदैनन्, तर छिटो {c} ले दुवैलाई दृष्टि दिन्छ — परिणाम तेस्रो व्यक्तिमार्फत आउँछ।"),
                    })
                    break
            for c in names:
                if c in (a, b):
                    continue
                if (abs(p7[c]["speed"]) < abs(p7[a]["speed"])
                        and abs(p7[c]["speed"]) < abs(p7[b]["speed"])
                        and frozenset((a, c)) in ithasala_set
                        and frozenset((b, c)) in ithasala_set):
                    pairs.append({
                        "yoga": "Yamaya", "yoga_ne": "यमया",
                        "planets": [a, b], "via": c,
                        "favourable": True,
                        "reading": _bi(
                            f"{a} and {b} both apply to slower {c} — light is collected through a third person; fulfilment needs patience.",
                            f"{a} र {b} दुवैले ढिलो {c} तर्फ गमन गर्छन् — तेस्रो व्यक्तिमार्फत ज्योति सङ्कलन हुन्छ; पूर्तिका लागि धैर्य चाहिन्छ।"),
                    })
                    break

    # Manau: an Ithasala spoiled by Mars/Saturn aspecting the faster planet.
    for fa, fb in ithasala_pairs:
        for malefic in ("Mars", "Saturn"):
            if malefic in (fa, fb):
                continue
            if malefic in p7 and _in_aspect(p7[malefic]["longitude"], p7[fa]["longitude"]):
                pairs.append({
                    "yoga": "Manau", "yoga_ne": "मनऊ",
                    "planets": [fa, fb], "spoiler": malefic,
                    "favourable": False,
                    "reading": _bi(
                        f"The Ithasala of {fa}–{fb} is spoiled by {malefic} within orb of {fa} — prohibition, delay or opposition from rivals.",
                        f"{fa}–{fb} को इत्थसाल {malefic} ले {fa} को कक्षभित्र रहेर बिगारेको छ — रोक, ढिलाइ वा प्रतिद्वन्द्वीबाट विरोध।"),
                })
                break

    # Kambula / Gairi-Kambula: the simplified Moon reading.
    moon_pairs = [p for p in pairs if "Moon" in p["planets"] and p["yoga"] in ("Ithasala", "Isharpha")]
    for p in moon_pairs:
        other = p["planets"][0] if p["planets"][1] == "Moon" else p["planets"][1]
        if p["yoga"] == "Ithasala":
            pairs.append({
                "yoga": "Kambula", "yoga_ne": "कम्बूल",
                "planets": ["Moon", other], "favourable": True, "simplified": True,
                "reading": _bi(
                    f"Moon in Ithasala with {other} — Kambula (simplified Moon reading): fortune supports the year's undertaking.",
                    f"चन्द्र {other} सँग इत्थसालमा — कम्बूल (सरलीकृत चन्द्र पठन): वर्षको काममा भाग्यले साथ दिन्छ।"),
            })
        else:
            pairs.append({
                "yoga": "Gairi-Kambula", "yoga_ne": "गैरिकम्बूल",
                "planets": ["Moon", other], "favourable": False, "simplified": True,
                "reading": _bi(
                    f"Moon in Isharpha with {other} — Gairi-Kambula (simplified Moon reading): circumstances run against the undertaking.",
                    f"चन्द्र {other} सँग ईसरफमा — गैरिकम्बूल (सरलीकृत चन्द्र पठन): परिस्थिति कामको विपरीत चल्छ।"),
            })

    # Chart-wide patterns.
    patterns: list[dict] = []
    if all(h in KENDRA | PANAPHARA for h in houses.values()):
        patterns.append({
            "pattern": "Ikbala", "pattern_ne": "इक्बाल", "favourable": True,
            "reading": _bi(
                "All seven planets stand in kendra or panaphara houses of the annual chart — a favourable year, wealth and support.",
                "सातै ग्रह वार्षिक कुण्डलीको केन्द्र वा पणफर भावमा छन् — शुभ वर्ष, धन र सहयोग।"),
        })
    if all(h in APOKLIMA for h in houses.values()):
        patterns.append({
            "pattern": "Induvara", "pattern_ne": "इन्दुवार", "favourable": False,
            "reading": _bi(
                "All seven planets stand in apoklima houses of the annual chart — an unfavourable year: disappointments and worries.",
                "सातै ग्रह वार्षिक कुण्डलीको आपोक्लिम भावमा छन् — अशुभ वर्ष: निराशा र चिन्ता।"),
        })

    fav = sum(1 for p in pairs if p["favourable"])
    unfav = sum(1 for p in pairs if not p["favourable"])
    return {
        "pairs": pairs, "patterns": patterns,
        "favourable_count": fav, "unfavourable_count": unfav,
        "orb_degrees": ORB,
        "method_note": _bi(
            "Tajika aspects judged within a documented 8-degree orb (classical Deeptamsa varies by planet); seven visible grahas only.",
            "ताजिक दृष्टि दस्तावेज गरिएको ८ डिग्रीको कक्षभित्र जाँचिएको छ (शास्त्रीय दीप्तांश ग्रहअनुसार फरक हुन्छ); सात दृश्य ग्रह मात्र।"),
    }


def saham_points(annual_planets: dict, varsha_lagna_lon: float,
                 varsha_lagna_sign: int, is_day: bool) -> dict:
    """The four principal Sahams of the annual chart (see module notes)."""
    lon = {p: annual_planets[p]["longitude"] for p in annual_planets}
    lagna = varsha_lagna_lon % 360.0
    if is_day:
        punya = (lon["Moon"] - lon["Sun"] + lagna) % 360.0
    else:
        punya = (lon["Sun"] - lon["Moon"] + lagna) % 360.0
    raw = {
        "Punya": punya,
        "Vivaha": (lon["Venus"] - lon["Saturn"] + lagna) % 360.0,
        "Yasas": (lon["Jupiter"] - punya + lagna) % 360.0,
        "Mahatmya": (punya - lon["Mars"] + lagna) % 360.0,
    }
    meanings = {
        "Punya": ("fortune and name", "भाग्य र नाम"),
        "Vivaha": ("marriage", "विवाह"),
        "Yasas": ("fame", "यश"),
        "Mahatmya": ("greatness and rank", "महानता र पद"),
    }
    out = {}
    for name, s_lon in raw.items():
        sign = int(s_lon // 30.0)
        lord = SIGN_LORDS[sign]
        house = house_of(sign, varsha_lagna_sign)
        dig = _dignity(lord, sign)
        if dig in ("exalted", "own"):
            strength = "strong"
        elif dig == "debilitated" or house in (6, 8, 12):
            strength = "weak"
        else:
            strength = "moderate"
        mean_en, mean_ne = meanings[name]
        out[name] = {
            "longitude": round(s_lon, 3),
            "sign": sign, "sign_en": SIGNS_EN[sign], "sign_ne": SIGNS_NE[sign],
            "degree_in_sign": round(s_lon % 30.0, 3),
            "lord": lord, "lord_ne": PLANET_NE[lord],
            "house": house, "house_theme": _bi(HOUSE_THEMES_EN[house], HOUSE_THEMES_NE[house]),
            "dignity": dig, "strength": strength,
            "reading": _bi(
                f"{name} Saham ({mean_en}) falls in {SIGNS_EN[sign]}, in the {HOUSE_NAMES_EN[house - 1]} house of the annual chart — {strength} by its lord's dignity and placement.",
                f"{name} सहम ({mean_ne}) {SIGNS_NE[sign]} मा, वार्षिक कुण्डलीको {HOUSE_NAMES_NE[house - 1]} भावमा छ — स्वामीको बल र स्थितिअनुसार {strength}।"),
        }
    return out


def panchadhikari(natal_lagna_sign: int, muntha_sign: int,
                  varsha_lagna_sign: int, varsha_lagna_lon: float,
                  annual_planets: dict, is_day: bool) -> dict:
    """The five-officer Year-Lord election (see module notes)."""
    sun_sign = annual_planets["Sun"]["sign"]
    moon_sign = annual_planets["Moon"]["sign"]
    dina_ratri = SIGN_LORDS[sun_sign] if is_day else SIGN_LORDS[moon_sign]
    tri_day, tri_night = _TRIPLICITY[_ELEMENT_OF_SIGN[varsha_lagna_sign]]
    tri_lord = tri_day if is_day else tri_night
    officers = [
        ("Natal Lagna lord", "जन्म लग्न स्वामी", SIGN_LORDS[natal_lagna_sign]),
        ("Muntha lord", "मुन्था स्वामी", SIGN_LORDS[muntha_sign]),
        ("Varsha Lagna lord", "वर्ष लग्न स्वामी", SIGN_LORDS[varsha_lagna_sign]),
        ("Dina-Ratri lord", "दिन-रात्रि स्वामी", dina_ratri),
        ("Triplicity lord", "त्रिराशि स्वामी", tri_lord),
    ]
    candidates = []
    for title_en, title_ne, planet in officers:
        p = annual_planets[planet]
        house = house_of(p["sign"], varsha_lagna_sign)
        dig = _dignity(planet, p["sign"])
        qualifies = _in_aspect(p["longitude"], varsha_lagna_lon % 360.0)
        score = _DIGNITY_POINTS[dig] + _house_points(house) if qualifies else 0
        candidates.append({
            "officer": _bi(title_en, title_ne),
            "planet": planet, "planet_ne": PLANET_NE[planet],
            "aspects_lagna": qualifies,
            "dignity": dig, "house": house,
            "score": score,
        })
    qualified = [c for c in candidates if c["aspects_lagna"]]
    if qualified:
        winner = max(qualified, key=lambda c: (c["score"], -candidates.index(c)))
        fallback = False
    else:
        winner = next(c for c in candidates if c["officer"]["en"] == "Muntha lord")
        fallback = True
    return {
        "candidates": candidates,
        "year_lord": winner["planet"],
        "year_lord_ne": winner["planet_ne"],
        "year_lord_officer": winner["officer"],
        "fallback_to_muntha": fallback,
        "reading": _bi(
            (f"The Panchadhikari election makes {winner['planet']} the Year Lord"
             + (" (no officer aspected the Varsha Lagna, so the classical default — the Muntha lord — applies)."
                if fallback else
                f" ({winner['officer']['en']}, strongest of the officers aspecting the Varsha Lagna).")),
            (f"पञ्चाधिकारी निर्वाचनले {winner['planet_ne']} लाई वर्ष स्वामी बनाउँछ"
             + (" (कुनै अधिकारीले वर्ष लग्नलाई दृष्टि दिएनन्, त्यसैले शास्त्रीय पूर्वनिर्धारित — मुन्था स्वामी — लागू हुन्छ)।"
                if fallback else
                f" ({winner['officer']['ne']}, वर्ष लग्नलाई दृष्टि दिने अधिकारीहरूमध्ये बलियो)।")),
        ),
    }
