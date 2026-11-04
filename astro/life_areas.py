"""Life Areas analysis — the whole chart, area by area.

analyse(bundle) reads a compute_kundali() bundle (a prashna horary
result is also tolerated: its planet rows carry the house in their KP
chain and its cusps carry the sign) and returns one dict per life
area. Every sentence is templated from the chart's ACTUAL placements:
a planet in one of the area's houses, the lord of an area house, a
planet aspecting an area house, or the running dasha lords. An empty
house is said to be empty and read from its lord instead — never
papered over with generic filler.

Classical rules used (documented, no new ephemeris):

* Houses per area — see AREAS below (fixed, classical).
* House lords: the lord of the sign on the house cusp (SIGN_LORDS
  from astro.names), falling back to whole-sign counting from Lagna.
* Graha Drishti (classical aspects, computed from houses because the
  bundle carries no aspect table): every planet aspects the 7th house
  from itself; Mars also the 4th and 8th, Jupiter also the 5th and
  9th, Saturn also the 3rd and 10th. Rahu/Ketu aspect the 7th only.
* Planet nature (classical): benefic Jupiter, Venus, Moon, Mercury;
  malefic Saturn, Mars, Rahu, Ketu; the Sun is a "cruel" planet —
  strong and demanding rather than gentle.
* Dasha: the current Vimshottari Mahadasha/Antardasha lords from the
  bundle's dasha["current"] (raw trees under dasha_tree["current"]
  are also accepted), with the houses each lord signifies per the
  bundle's KP house_significators / planet_signified_houses.

All output is probability guidance, never a certainty, and the health
area never diagnoses: see the disclaimer handling in ai_astrologer,
which always adds a see-a-clinician line to health answers.
"""

from __future__ import annotations

from .names import PLANET_NE, SIGNS_EN, SIGNS_NE, SIGN_LORDS

PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus",
           "Saturn", "Rahu", "Ketu"]

BENEFIC = {"Jupiter", "Venus", "Moon", "Mercury"}
MALEFIC = {"Saturn", "Mars", "Rahu", "Ketu"}
# Sun: cruel (strong/demanding), neither benefic nor malefic here.
NATURE = {p: ("benefic" if p in BENEFIC else "malefic" if p in MALEFIC
               else "cruel") for p in PLANETS}

# Classical Graha Drishti: extra aspects beyond the universal 7th.
_SPECIAL_ASPECTS = {
    "Mars": (4, 8),
    "Jupiter": (5, 9),
    "Saturn": (3, 10),
}

# Planet character phrases, used in effect sentences.
_NATURE_EN = {
    "Sun": "authority and drive", "Moon": "sensitivity and fluctuation",
    "Mars": "energy and urgency", "Mercury": "analysis and adaptability",
    "Jupiter": "growth and wisdom", "Venus": "ease and harmony",
    "Saturn": "discipline and delay", "Rahu": "ambition and unpredictability",
    "Ketu": "detachment and introspection",
}
_NATURE_NE = {
    "Sun": "अधिकार र ऊर्जा", "Moon": "संवेदनशीलता र उतारचढाव",
    "Mars": "ऊर्जा र हतार", "Mercury": "विश्लेषण र अनुकूलन",
    "Jupiter": "वृद्धि र ज्ञान", "Venus": "सहजता र सामञ्जस्य",
    "Saturn": "अनुशासन र ढिलाइ", "Rahu": "महत्त्वाकाङ्क्षा र अप्रत्याशितता",
    "Ketu": "विरक्ति र आत्मचिन्तन",
}

_HOUSE_MEANING_EN = {
    1: "self, body and nature", 2: "wealth and family",
    3: "courage and short travel", 4: "home and mother",
    5: "intelligence and children", 6: "service and disease",
    7: "partnership and marriage", 8: "obstacles and longevity",
    9: "fortune and higher learning", 10: "career and status",
    11: "gains and fulfilment", 12: "loss, foreign residence and hospitals",
}
_HOUSE_MEANING_NE = {
    1: "आत्मा, शरीर र स्वभाव", 2: "धन र परिवार",
    3: "साहस र छोटो यात्रा", 4: "घर र आमा",
    5: "बुद्धि र सन्तान", 6: "सेवा र रोग",
    7: "साझेदारी र विवाह", 8: "बाधा र आयु",
    9: "भाग्य र उच्च शिक्षा", 10: "करियर र प्रतिष्ठा",
    11: "लाभ र इच्छापूर्ति", 12: "हानि, विदेश बसोबास र अस्पताल",
}

# area_id -> (houses, title_en, title_ne, concern_en, concern_ne)
AREAS = {
    "personality": ([1], "Personality", "व्यक्तित्व",
                    "self, body, nature and vitality",
                    "आत्मा, शरीर, स्वभाव र जीवनशक्ति"),
    "career": ([10, 6, 7], "Career", "करियर",
               "profession, service and business",
               "पेशा, सेवा र व्यवसाय"),
    "finance": ([2, 11, 5], "Finance & Wealth", "वित्त र सम्पत्ति",
                "income, gains and savings",
                "आम्दानी, लाभ र बचत"),
    "marriage": ([7, 2, 11, 5], "Marriage & Relationships",
                 "विवाह र सम्बन्ध",
                 "partnership, marriage and the link to children",
                 "साझेदारी, विवाह र सन्तानसँगको सम्बन्ध"),
    "health": ([1, 6, 8, 12], "Health", "स्वास्थ्य",
               "vitality, disease, chronic conditions and hospitalisation",
               "जीवनशक्ति, रोग, दीर्घरोग र अस्पताल भर्ना"),
    "education": ([4, 5, 9], "Education", "शिक्षा",
                  "basic learning, intelligence and higher study",
                  "आधारभूत सिकाइ, बुद्धि र उच्च अध्ययन"),
    "family_home": ([2, 4], "Family & Home", "परिवार र घर",
                    "family, home, mother and property",
                    "परिवार, घर, आमा र सम्पत्ति"),
    "foreign": ([9, 12, 3], "Foreign Travel & Settlement",
                "विदेश यात्रा र बसोबास",
                "long travel, foreign residence and short travel",
                "लामो यात्रा, विदेश बसोबास र छोटो यात्रा"),
}

AREA_ORDER = ["personality", "career", "finance", "marriage",
              "health", "education", "family_home", "foreign"]


def _ordinal_en(h: int) -> str:
    suf = {1: "st", 2: "nd", 3: "rd"}.get(h, "th")
    return f"{h}{suf}"


def _house_of_sign(sign: int, lagna_sign: int) -> int:
    return (sign - lagna_sign) % 12 + 1


def aspected_houses(planet: str, house: int) -> list[int]:
    """Classical Graha Drishti from a planet's house (1..12)."""
    out = {((house + 5) % 12) + 1}  # 7th from itself
    for offset in _SPECIAL_ASPECTS.get(planet, ()):
        out.add(((house + offset - 2) % 12) + 1)
    return sorted(out)


def _get(d: dict, *keys):
    for k in keys:
        if isinstance(d, dict) and d.get(k) is not None:
            return d[k]
    return None


def _planet_rows(bundle: dict) -> list[dict]:
    rows = []
    for row in (bundle or {}).get("planets") or []:
        house = row.get("house")
        if house is None:
            house = (row.get("kp") or {}).get("house")
        if house is None:
            continue
        rows.append({
            "planet": row["planet"],
            "sign": row.get("sign"),
            "sign_en": row.get("sign_en") or (
                SIGNS_EN[row["sign"]] if row.get("sign") is not None else ""),
            "sign_ne": row.get("sign_ne") or (
                SIGNS_NE[row["sign"]] if row.get("sign") is not None else ""),
            "house": int(house),
            "nakshatra_en": row.get("nakshatra_en"),
            "nakshatra_ne": row.get("nakshatra_ne"),
        })
    return rows


def _lagna_sign(bundle: dict) -> int | None:
    lagna = (bundle or {}).get("lagna") or {}
    if lagna.get("sign") is not None:
        return int(lagna["sign"])
    cusps = (bundle or {}).get("house_cusps") or (bundle or {}).get("cusps") or []
    if cusps and cusps[0].get("sign") is not None:
        return int(cusps[0]["sign"])
    return None


def _cusp_signs(bundle: dict) -> list[int]:
    """Sign index on each house cusp (1..12), or [] if unavailable."""
    cusps = (bundle or {}).get("house_cusps") or (bundle or {}).get("cusps") or []
    signs = []
    for c in cusps[:12]:
        if isinstance(c, dict) and c.get("sign") is not None:
            signs.append(int(c["sign"]))
    if len(signs) == 12:
        return signs
    lagna = _lagna_sign(bundle)
    if lagna is None:
        return []
    return [(lagna + h) % 12 for h in range(12)]


def house_lords(bundle: dict) -> dict[int, str]:
    """house (1..12) -> ruling planet, from cusp signs."""
    signs = _cusp_signs(bundle)
    if not signs:
        return {}
    return {h + 1: SIGN_LORDS[signs[h]] for h in range(12)}


def _signified_map(bundle: dict) -> dict[str, list[int]]:
    kp = (bundle or {}).get("kp") or {}
    signified = kp.get("planet_signified_houses")
    if signified:
        return {p: [int(h) for h in hs] for p, hs in signified.items()}
    # Prashna horary: invert house_significators' significator_order.
    house_sig = kp.get("house_significators") or (bundle or {}).get("house_significators") or {}
    out: dict[str, list[int]] = {}
    for house, sig in house_sig.items():
        for planet in (sig or {}).get("significator_order") or []:
            out.setdefault(planet, []).append(int(house))
    return {p: sorted(set(hs)) for p, hs in out.items()}


def _house_significators(bundle: dict) -> dict:
    kp = (bundle or {}).get("kp") or {}
    return kp.get("house_significators") or (bundle or {}).get("house_significators") or {}


def _dasha_current(bundle: dict) -> dict | None:
    dasha = (bundle or {}).get("dasha") or (bundle or {}).get("dasha_tree") or {}
    current = dasha.get("current") if isinstance(dasha, dict) else None
    if not current:
        return None

    def _lord(period) -> str | None:
        if isinstance(period, dict):
            return period.get("lord")
        return getattr(period, "lord", None)

    def _span(period) -> dict | None:
        if isinstance(period, dict) and period.get("start"):
            return {"start": str(period["start"])[:10],
                    "end": str(period["end"])[:10] if period.get("end") else None}
        return None

    return {
        "mahadasha_lord": _lord(current.get("mahadasha")),
        "antardasha_lord": _lord(current.get("antardasha")),
        "mahadasha_period": _span(current.get("mahadasha")),
        "antardasha_period": _span(current.get("antardasha")),
    }


def _effect_in(planet: str, house: int, concern_en: str, concern_ne: str):
    en = (f"{planet} in the {_ordinal_en(house)} house brings "
          f"{_NATURE_EN[planet]} to {concern_en}.")
    ne = (f"{_ordinal_en(house)} भावमा {PLANET_NE[planet]} ले "
          f"{concern_ne}मा {_NATURE_NE[planet]} ल्याउँछ।")
    return en, ne


def _effect_lord(planet: str, house: int, concern_en: str, concern_ne: str):
    en = (f"{planet} rules the {_ordinal_en(house)} house, so "
          f"{concern_en} is shaped by {_NATURE_EN[planet]}.")
    ne = (f"{PLANET_NE[planet]} {_ordinal_en(house)} भावको स्वामी भएकाले "
          f"{concern_ne} {_NATURE_NE[planet]}बाट प्रभावित हुन्छ।")
    return en, ne


def _effect_aspect(planet: str, house: int, concern_en: str, concern_ne: str):
    en = (f"{planet} aspects the {_ordinal_en(house)} house, lending "
          f"{_NATURE_EN[planet]} to {concern_en} from a distance.")
    ne = (f"{PLANET_NE[planet]}ले {_ordinal_en(house)} भावलाई दृष्टि दिएकाले "
          f"{concern_ne}मा {_NATURE_NE[planet]} पर्छ।")
    return en, ne


def analyse(bundle: dict) -> list[dict]:
    """Return the 8 life-area readings for a kundali bundle."""
    rows = _planet_rows(bundle)
    by_planet = {r["planet"]: r for r in rows}
    lords = house_lords(bundle)
    signified = _signified_map(bundle)
    dasha = _dasha_current(bundle)
    house_sig = _house_significators(bundle)

    # Planet -> houses it aspects (classical Drishti, from its house).
    aspects_of = {p: aspected_houses(p, by_planet[p]["house"])
                  for p in PLANETS if p in by_planet}

    out = []
    for area_id in AREA_ORDER:
        houses, title_en, title_ne, concern_en, concern_ne = AREAS[area_id]
        houses = list(houses)
        area_lords = {h: lords[h] for h in houses if h in lords}
        planets_in = {}
        for r in rows:
            if r["house"] in houses:
                entry = {"sign_en": r["sign_en"], "sign_ne": r["sign_ne"],
                         "house": r["house"]}
                if r.get("nakshatra_en"):
                    entry["nakshatra_en"] = r["nakshatra_en"]
                if r.get("nakshatra_ne"):
                    entry["nakshatra_ne"] = r["nakshatra_ne"]
                planets_in[r["planet"]] = entry
        planets_aspecting = {}
        for p, asp in aspects_of.items():
            hit = [h for h in asp if h in houses]
            if hit:
                planets_aspecting[p] = hit

        # Influence score: placement 3, lordship 2, aspect 1,
        # benefic +0.5 (malefic/cruel 0) — deterministic, planet order
        # breaks ties. Strongest = top 3 with a one-line effect each.
        scored = []
        for p in PLANETS:
            score = 0.0
            mode = None
            if p in planets_in:
                score += 3
                mode = "in"
            ruled = [h for h in houses if area_lords.get(h) == p]
            if ruled:
                score += 2
                mode = mode or "lord"
            if p in planets_aspecting:
                score += 1
                mode = mode or "aspect"
            if score <= 0:
                continue
            if NATURE[p] == "benefic":
                score += 0.5
            scored.append((score, p, mode, ruled))
        scored.sort(key=lambda t: (-t[0], PLANETS.index(t[1])))
        strongest = []
        for _score, p, mode, ruled in scored[:3]:
            if mode == "in":
                en, ne = _effect_in(p, by_planet[p]["house"], concern_en, concern_ne)
            elif mode == "lord":
                en, ne = _effect_lord(p, ruled[0], concern_en, concern_ne)
            else:
                en, ne = _effect_aspect(p, planets_aspecting[p][0], concern_en, concern_ne)
            strongest.append({"planet": p, "planet_ne": PLANET_NE[p],
                              "effect_en": en, "effect_ne": ne})

        # Dasha influence: which of the area's houses each running
        # lord signifies per the KP tables.
        if dasha:
            md_sig = signified.get(dasha["mahadasha_lord"], []) if dasha["mahadasha_lord"] else []
            ad_sig = signified.get(dasha["antardasha_lord"], []) if dasha["antardasha_lord"] else []
            dasha_influence = {
                "mahadasha_lord": dasha["mahadasha_lord"],
                "antardasha_lord": dasha["antardasha_lord"],
                "mahadasha_period": dasha["mahadasha_period"],
                "antardasha_period": dasha["antardasha_period"],
                "mahadasha_signifies": md_sig,
                "antardasha_signifies": ad_sig,
                "mahadasha_signifies_area_houses": [h for h in md_sig if h in houses],
                "antardasha_signifies_area_houses": [h for h in ad_sig if h in houses],
            }
        else:
            dasha_influence = {
                "mahadasha_lord": None, "antardasha_lord": None,
                "mahadasha_period": None, "antardasha_period": None,
                "mahadasha_signifies": [], "antardasha_signifies": [],
                "mahadasha_signifies_area_houses": [],
                "antardasha_signifies_area_houses": [],
            }

        # Reading: one sentence per area house (placement, or the
        # lord when empty), plus dasha and strongest-planet lines.
        en_lines = [f"For {title_en}, the chart looks at house(s) "
                    f"{', '.join(str(h) for h in houses)} "
                    f"({'; '.join(_HOUSE_MEANING_EN[h] for h in houses)})."]
        ne_lines = [f"{title_ne}का लागि कुण्डलीले "
                    f"{', '.join(str(h) for h in houses)} भाव "
                    f"({' ; '.join(_HOUSE_MEANING_NE[h] for h in houses)}) हेर्छ।"]
        for h in houses:
            occupants = [p for p, v in planets_in.items() if v["house"] == h]
            if occupants:
                for p in occupants:
                    en, ne = _effect_in(p, h, concern_en, concern_ne)
                    en_lines.append(en)
                    ne_lines.append(ne)
            else:
                lord = area_lords.get(h)
                if lord and lord in by_planet:
                    lr = by_planet[lord]
                    en_lines.append(
                        f"The {_ordinal_en(h)} house is empty, so its lord "
                        f"{lord} — placed in the {_ordinal_en(lr['house'])} house "
                        f"in {lr['sign_en']} — carries the reading for "
                        f"{_HOUSE_MEANING_EN[h]}.")
                    ne_lines.append(
                        f"{_ordinal_en(h)} भाव खाली छ, त्यसैले यसको स्वामी "
                        f"{PLANET_NE[lord]} — {lr['sign_ne']}मा "
                        f"{_ordinal_en(lr['house'])} भावमा रहेको — ले "
                        f"{_HOUSE_MEANING_NE[h]}को फल दिन्छ।")
                elif lord:
                    en_lines.append(
                        f"The {_ordinal_en(h)} house is empty, so its lord "
                        f"{lord} carries the reading for {_HOUSE_MEANING_EN[h]}.")
                    ne_lines.append(
                        f"{_ordinal_en(h)} भाव खाली छ, त्यसैले यसको स्वामी "
                        f"{PLANET_NE[lord]}ले {_HOUSE_MEANING_NE[h]}को फल दिन्छ।")
        if area_id == "personality":
            # Classical extra: Moon (mind) and Sun (vitality) placements.
            for p in ("Moon", "Sun"):
                if p in by_planet:
                    r = by_planet[p]
                    en_lines.append(
                        f"{p} sits in the {_ordinal_en(r['house'])} house "
                        f"in {r['sign_en']}, colouring temperament and vitality.")
                    ne_lines.append(
                        f"{PLANET_NE[p]} {r['sign_ne']}मा "
                        f"{_ordinal_en(r['house'])} भावमा रहेकाले स्वभाव र "
                        f"जीवनशक्तिमा प्रभाव पर्छ।")
        if dasha and dasha["mahadasha_lord"]:
            md_hits = dasha_influence["mahadasha_signifies_area_houses"]
            ad_hits = dasha_influence["antardasha_signifies_area_houses"]
            en_lines.append(
                f"The running {dasha['mahadasha_lord']} Mahadasha and "
                f"{dasha['antardasha_lord']} Antardasha touch this area "
                f"through houses {md_hits or 'none'} and {ad_hits or 'none'} "
                f"respectively — a period influence, not a fixed event.")
            ne_lines.append(
                f"चलिरहेको {PLANET_NE[dasha['mahadasha_lord']]} महादशा र "
                f"{PLANET_NE[dasha['antardasha_lord']]} अन्तर्दशाले यस क्षेत्रलाई "
                f"क्रमशः {md_hits or 'कुनै होइन'} र {ad_hits or 'कुनै होइन'} "
                f"भावमार्फत छुन्छ — यो अवधिको प्रभाव हो, निश्चित घटना होइन।")
        if strongest:
            names_en = ", ".join(s["planet"] for s in strongest)
            names_ne = ", ".join(s["planet_ne"] for s in strongest)
            en_lines.append(
                f"The most influential planets here are {names_en}; "
                f"their combined tone leans "
                f"{'supportive' if any(NATURE[s['planet']] == 'benefic' for s in strongest) else 'demanding'} "
                f"for {concern_en}, as probability guidance only.")
            ne_lines.append(
                f"यहाँ सबैभन्दा प्रभावशाली ग्रह {names_ne} हुन्; तिनको संयुक्त "
                f"स्वर {concern_ne}का लागि "
                f"{'सहयोगी' if any(NATURE[s['planet']] == 'benefic' for s in strongest) else 'कठिन'} "
                f"देखिन्छ — यो सम्भावना-आधारित मार्गदर्शन मात्र हो।")

        out.append({
            "id": area_id,
            "title_en": title_en, "title_ne": title_ne,
            "houses": houses,
            "house_lords": area_lords,
            "planets_in": planets_in,
            "planets_aspecting": planets_aspecting,
            "strongest": strongest,
            "dasha_influence": dasha_influence,
            "reading_en": " ".join(en_lines),
            "reading_ne": " ".join(ne_lines),
        })
    return out
