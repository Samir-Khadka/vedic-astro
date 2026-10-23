"""Premium report layer — mirrors what the top paid services sell
(Clickastro In-depth / AstroSage Brihat Kundli style chapters), but every
statement is generated from the same computed engine facts.

Includes:
  * Multi-chapter life report (personality, career, finance, marriage,
    health, education, family/home, foreign settlement)
  * 10-year forecast driven by Mahadasha/Antardasha + slow transits
  * Varshphal (simplified annual chart: solar-return Lagna, Muntha,
    year lord) for the current and next two years
  * Remedies: gemstones (life/lucky/fortune stones), Rudraksha, beej
    mantra for the most afflicted planet, dosha-specific remedies
  * Lucky attributes from the Moon-sign lord
"""
from __future__ import annotations

from datetime import datetime, timedelta

from . import ephemeris
from .charts import dignity, house_lords, house_of
from .names import (
    HOUSE_NAMES_EN, HOUSE_NAMES_NE, HOUSE_THEMES_EN, HOUSE_THEMES_NE,
    NAKSHATRAS_EN, NAKSHATRAS_NE,
    NATURAL_BENEFICS, NATURAL_MALEFICS, PLANET_NE, SIGNS_EN, SIGNS_NE,
    SIGN_LORDS,
)
from .predictions import _bi, _placement_fact

# ---------------------------------------------------------------------------
# Classical remedy tables
# ---------------------------------------------------------------------------
GEMSTONES = {
    "Sun": ("Ruby", "माणिक", "Gold", "सुन", "Ring finger", "कान्छी औंला", "Sunday", "आइतबार", "5 ratti"),
    "Moon": ("Pearl", "मोती", "Silver", "चाँदी", "Little finger", "कान्छी औंला", "Monday", "सोमबार", "5 ratti"),
    "Mars": ("Red Coral", "मुँगा", "Gold/Copper", "सुन/तामा", "Ring finger", "साहिंली औंला", "Tuesday", "मङ्गलबार", "6 ratti"),
    "Mercury": ("Emerald", "पन्ना", "Gold", "सुन", "Little finger", "कान्छी औंला", "Wednesday", "बुधबार", "5 ratti"),
    "Jupiter": ("Yellow Sapphire", "पुखराज", "Gold", "सुन", "Index finger", "चोर औंला", "Thursday", "बिहीबार", "5 ratti"),
    "Venus": ("Diamond", "हीरा", "Platinum/Silver", "प्लाटिनम/चाँदी", "Middle finger", "माझी औंला", "Friday", "शुक्रबार", "4 ratti"),
    "Saturn": ("Blue Sapphire", "नीलम", "Silver/Panchdhatu", "चाँदी/पञ्चधातु", "Middle finger", "माझी औंला", "Saturday", "शनिबार", "5 ratti"),
    "Rahu": ("Hessonite", "गोमेद", "Silver", "चाँदी", "Middle finger", "माझी औंला", "Saturday", "शनिबार", "5 ratti"),
    "Ketu": ("Cat's Eye", "लहसुनिया", "Silver", "चाँदी", "Middle finger", "माझी औंला", "Tuesday", "मङ्गलबार", "5 ratti"),
}
# (stone_en, stone_ne, metal_en, metal_ne, finger_en, finger_ne, day_en, day_ne, weight)

RUDRAKSHA = {  # planet: (mukhi, en, ne)
    "Sun": (1, "One Mukhi Rudraksha", "एकमुखी रुद्राक्ष"),
    "Moon": (2, "Two Mukhi Rudraksha", "दुईमुखी रुद्राक्ष"),
    "Mars": (3, "Three Mukhi Rudraksha", "तीनमुखी रुद्राक्ष"),
    "Mercury": (4, "Four Mukhi Rudraksha", "चारमुखी रुद्राक्ष"),
    "Jupiter": (5, "Five Mukhi Rudraksha", "पाँचमुखी रुद्राक्ष"),
    "Venus": (6, "Six Mukhi Rudraksha", "छमुखी रुद्राक्ष"),
    "Saturn": (7, "Seven Mukhi Rudraksha", "सातमुखी रुद्राक्ष"),
    "Rahu": (8, "Eight Mukhi Rudraksha", "आठमुखी रुद्राक्ष"),
    "Ketu": (9, "Nine Mukhi Rudraksha", "नौमुखी रुद्राक्ष"),
}
BEEJ_MANTRA = {
    "Sun": ("ॐ ह्रां ह्रीं ह्रौं सः सूर्याय नमः", "Om Hram Hrim Hraum Sah Suryaya Namah"),
    "Moon": ("ॐ श्रां श्रीं श्रौं सः चन्द्रमसे नमः", "Om Shram Shrim Shraum Sah Chandramase Namah"),
    "Mars": ("ॐ क्रां क्रीं क्रौं सः भौमाय नमः", "Om Kram Krim Kraum Sah Bhaumaya Namah"),
    "Mercury": ("ॐ ब्रां ब्रीं ब्रौं सः बुधाय नमः", "Om Bram Brim Braum Sah Budhaya Namah"),
    "Jupiter": ("ॐ ग्रां ग्रीं ग्रौं सः गुरवे नमः", "Om Gram Grim Graum Sah Gurave Namah"),
    "Venus": ("ॐ द्रां द्रीं द्रौं सः शुक्राय नमः", "Om Dram Drim Draum Sah Shukraya Namah"),
    "Saturn": ("ॐ प्रां प्रीं प्रौं सः शनये नमः", "Om Pram Prim Praum Sah Shanaye Namah"),
    "Rahu": ("ॐ भ्रां भ्रीं भ्रौं सः राहवे नमः", "Om Bhram Bhrim Bhraum Sah Rahave Namah"),
    "Ketu": ("ॐ स्रां स्रीं स्रौं सः केतवे नमः", "Om Sram Srim Sraum Sah Ketave Namah"),
}
PLANET_NUMBER = {"Sun": 1, "Moon": 2, "Jupiter": 3, "Rahu": 4, "Mercury": 5, "Venus": 6, "Ketu": 7, "Saturn": 8, "Mars": 9}
PLANET_COLOUR = {
    "Sun": ("Orange / Gold", "सुन्तला / सुनौलो"), "Moon": ("White", "सेतो"),
    "Mars": ("Red", "रातो"), "Mercury": ("Green", "हरियो"),
    "Jupiter": ("Yellow", "पहेंलो"), "Venus": ("White / Pink", "सेतो / गुलाबी"),
    "Saturn": ("Dark Blue", "गाढा नीलो"), "Rahu": ("Smoky Grey", "धूवाँसे खैरो"),
    "Ketu": ("Grey", "खैरो"),
}
PLANET_DAY = {
    "Sun": ("Sunday", "आइतबार"), "Moon": ("Monday", "सोमबार"), "Mars": ("Tuesday", "मङ्गलबार"),
    "Mercury": ("Wednesday", "बुधबार"), "Jupiter": ("Thursday", "बिहीबार"),
    "Venus": ("Friday", "शुक्रबार"), "Saturn": ("Saturday", "शनिबार"),
    "Rahu": ("Saturday", "शनिबार"), "Ketu": ("Tuesday", "मङ्गलबार"),
}
PLANET_DEITY = {
    "Sun": ("Surya / Lord Rama", "सूर्य / श्रीराम"), "Moon": ("Lord Shiva", "भगवान शिव"),
    "Mars": ("Lord Hanuman", "हनुमान"), "Mercury": ("Lord Vishnu", "भगवान विष्णु"),
    "Jupiter": ("Lord Vishnu", "भगवान विष्णु"), "Venus": ("Goddess Lakshmi", "देवी लक्ष्मी"),
    "Saturn": ("Lord Shani / Hanuman", "शनि देव / हनुमान"), "Rahu": ("Goddess Durga", "देवी दुर्गा"),
    "Ketu": ("Lord Ganesha", "भगवान गणेश"),
}


def _gem_entry(planet: str, role_en: str, role_ne: str) -> dict:
    s_en, s_ne, m_en, m_ne, f_en, f_ne, d_en, d_ne, w = GEMSTONES[planet]
    return {
        "role": _bi(role_en, role_ne), "for_planet": planet,
        "stone": _bi(s_en, s_ne), "metal": _bi(m_en, m_ne),
        "finger": _bi(f_en, f_ne), "day": _bi(d_en, d_ne), "weight": w,
    }


def _most_afflicted(planets: dict, lagna_sign: int, combust: dict) -> str:
    best, best_score = "Saturn", -1
    for name in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
        score = 0
        if dignity(name, planets[name]["sign"]) == "debilitated":
            score += 3
        if combust.get(name):
            score += 2
        if house_of(planets[name]["sign"], lagna_sign) in (6, 8, 12):
            score += 1
        if score > best_score:
            best, best_score = name, score
    return best


def remedies(ctx: dict) -> dict:
    planets, lagna_sign = ctx["planets"], ctx["lagna_sign"]
    lords = house_lords(lagna_sign)
    moon_lord = SIGN_LORDS[planets["Moon"]["sign"]]
    gems = [
        _gem_entry(lords[1], "Life stone (Lagna lord)", "जीवन रत्न (लग्न स्वामी)"),
        _gem_entry(moon_lord, "Lucky stone (Moon-sign lord)", "भाग्य रत्न (चन्द्र राशि स्वामी)"),
        _gem_entry(lords[9], "Fortune stone (9th lord)", "भाग्येश रत्न (नवम भाव स्वामी)"),
    ]
    weak = _most_afflicted(planets, lagna_sign, ctx["combust"])
    mukhi, r_en, r_ne = RUDRAKSHA[weak]
    mantra_ne, mantra_tr = BEEJ_MANTRA[weak]

    dosha_rems = []
    d = ctx["doshas"]
    if d["manglik"]["present"] and d["manglik"]["strength"] != "cancelled":
        dosha_rems.append({
            "dosha": _bi("Manglik Dosha", "माङ्गलिक दोष"),
            "items": [
                _bi("Recite Hanuman Chalisa on Tuesdays and offer red flowers to Lord Hanuman.",
                    "मङ्गलबार हनुमान चालीसा पाठ गर्नुहोस् र हनुमानलाई रातो फूल अर्पण गर्नुहोस्।"),
                _bi("Donate red lentils, jaggery and wheat on Tuesdays.",
                    "मङ्गलबार रातो दाल, सक्खर र गहुँ दान गर्नुहोस्।"),
                _bi("Traditional guidance suggests marriage after 28 or matching with another Manglik partner.",
                    "परम्परागत सुझावअनुसार २८ वर्षपछि विवाह गर्नु वा अर्का माङ्गलिकसँग मेल खानु उपयुक्त हुन्छ।"),
            ],
        })
    if d["kaal_sarp"]["present"]:
        dosha_rems.append({
            "dosha": _bi("Kaal Sarp Dosha", "काल सर्प दोष"),
            "items": [
                _bi("Chant the Mahamrityunjaya mantra 108 times daily, especially on Mondays.",
                    "विशेष गरी सोमबार महामृत्युञ्जय मन्त्र दैनिक १०८ पटक जप गर्नुहोस्।"),
                _bi("Perform Rudrabhishek on Maha Shivaratri or during Shravan month.",
                    "महाशिवरात्रि वा श्रावण महिनामा रुद्राभिषेक गर्नुहोस्।"),
                _bi("Donate a pair of silver snake idols in a Shiva temple on Nag Panchami.",
                    "नाग पञ्चमीमा शिव मन्दिरमा चाँदीका नागको जोडी दान गर्नुहोस्।"),
            ],
        })
    if d["sade_sati"]["active"]:
        dosha_rems.append({
            "dosha": _bi("Saturn Sade Sati", "शनि साढेसाती"),
            "items": [
                _bi("Light a mustard-oil lamp under a Peepal tree on Saturday evenings.",
                    "शनिबार साँझ पीपलको रूखमुनि तोरीको तेलको दियो बाल्नुहोस्।"),
                _bi("Chant 'Om Sham Shanicharaya Namah' 108 times on Saturdays.",
                    "शनिबार 'ॐ शं शनिचराय नमः' १०८ पटक जप गर्नुहोस्।"),
                _bi("Serve the elderly and the poor; avoid alcohol and leather gifts on Saturdays.",
                    "बुजुर्ग र गरिबको सेवा गर्नुहोस्; शनिबार मदिरा र छालाका वस्तुबाट टाढा रहनुहोस्।"),
            ],
        })
    if d["pitra"]["present"]:
        dosha_rems.append({
            "dosha": _bi("Pitra Dosha", "पितृ दोष"),
            "items": [
                _bi("Offer water and sesame (tarpan) to ancestors on Amavasya.",
                    "औंसीमा पितृहरूलाई जल र तिलको तर्पण दिनुहोस्।"),
                _bi("Feed crows, cows and the needy on Saturdays and during Pitru Paksha.",
                    "शनिबार र पितृ पक्षमा काग, गाई र गरिबलाई खाना खुवाउनुहोस्।"),
                _bi("Plant and nurture a Peepal tree.",
                    "पीपलको रूख रोपेर हेरचाह गर्नुहोस्।"),
            ],
        })

    return {
        "gemstones": gems,
        "rudraksha": {
            "for_planet": weak,
            "recommendation": _bi(r_en, r_ne),
            "reason": _bi(
                f"{weak} is the most afflicted planet in this chart by the classical checks (debilitation, combustion, dusthana placement).",
                f"शास्त्रीय परीक्षणहरू (नीच, अस्त, दुष्टस्थान) अनुसार {PLANET_NE[weak]} यस कुण्डलीमा सबैभन्दा पीडित ग्रह हो।",
            ),
        },
        "mantra": {
            "for_planet": weak,
            "beej_ne": mantra_ne,
            "transliteration": mantra_tr,
            "instruction": _bi(
                "Chant 108 times daily at sunrise for one full mandala (40 days).",
                "४० दिन (एक मण्डल) सम्म दैनिक सूर्योदयमा १०८ पटक जप गर्नुहोस्।",
            ),
        },
        "dosha_remedies": dosha_rems,
    }


def lucky_attributes(ctx: dict) -> dict:
    moon_lord = SIGN_LORDS[ctx["planets"]["Moon"]["sign"]]
    num = PLANET_NUMBER[moon_lord]
    col_en, col_ne = PLANET_COLOUR[moon_lord]
    day_en, day_ne = PLANET_DAY[moon_lord]
    de_en, de_ne = PLANET_DEITY[moon_lord]
    dev_digits = str(num).translate(str.maketrans("0123456789", "०१२३४५६७८९"))
    return {
        "based_on": _bi("the lord of your Moon sign", "तपाईंको चन्द्र राशिको स्वामी"),
        "number": {"en": str(num), "ne": dev_digits},
        "colour": _bi(col_en, col_ne),
        "day": _bi(day_en, day_ne),
        "deity": _bi(de_en, de_ne),
        "direction_planet": moon_lord,
    }


# ---------------------------------------------------------------------------
# Chapters
# ---------------------------------------------------------------------------
def chapters(ctx: dict) -> dict:
    planets, lagna_sign = ctx["planets"], ctx["lagna_sign"]
    lords = house_lords(lagna_sign)
    d9 = ctx["charts"]["D9"]
    d10 = ctx["charts"]["D10"]
    karakas = ctx["karakas"]

    def occupants(house: int) -> list[str]:
        return [n for n, p in planets.items() if house_of(p["sign"], lagna_sign) == house]

    out: dict[str, list[dict]] = {}

    # Personality
    facts = [
        _bi(
            f"Your ascendant (Lagna) is {SIGNS_EN[lagna_sign]} and the Moon is in {SIGNS_EN[planets['Moon']['sign']]} "
            f"in {NAKSHATRAS_EN[planets['Moon']['nakshatra']]} nakshatra — together they shape temperament and emotional style.",
            f"तपाईंको लग्न {SIGNS_NE[lagna_sign]} हो र चन्द्रमा {SIGNS_NE[planets['Moon']['sign']]} राशिमा "
            f"{NAKSHATRAS_NE[planets['Moon']['nakshatra']]} नक्षत्रमा छ — यिनले स्वभाव र भावनात्मक शैली निर्धारण गर्छन्।",
        ),
        _placement_fact(lords[1], planets, lagna_sign, lords),
        _placement_fact(karakas["Atmakaraka"], planets, lagna_sign, lords),
    ]
    out["personality"] = facts

    # Career
    facts = [_placement_fact(lords[10], planets, lagna_sign, lords)]
    for p in occupants(10):
        facts.append(_placement_fact(p, planets, lagna_sign, lords))
    facts.append(_bi(
        f"In the Dashamsa (D10, career chart) the Lagna is {SIGNS_EN[d10['Lagna']]} and the D10 10th lord is "
        f"{SIGN_LORDS[(d10['Lagna'] + 9) % 12]} — a key confirmation for professional direction.",
        f"दशमांश (D10, पेशाको कुण्डली) मा लग्न {SIGNS_NE[d10['Lagna']]} छ र D10 को दशम स्वामी "
        f"{PLANET_NE[SIGN_LORDS[(d10['Lagna'] + 9) % 12]]} हो — यो पेशागत दिशाको महत्त्वपूर्ण पुष्टि हो।",
    ))
    out["career"] = facts

    # Finance
    facts = ctx["predictions"]["wealth"]
    dhana = [y for y in ctx["yogas"] if y["name"].startswith("Dhana")]
    for y in dhana:
        facts = facts + [_bi(f"Dhana yoga is present: {y['basis']}.", f"धन योग उपस्थित छ: {y['basis']}।")]
    out["finance"] = facts

    # Marriage & relationships
    facts = ctx["predictions"]["relationships"] + [
        _bi(
            f"In the Navamsa (D9, marriage chart) the Lagna is {SIGNS_EN[d9['Lagna']]}, and Venus — the significator of "
            f"marriage — is in {SIGNS_EN[planets['Venus']['sign']]} in the D1 chart.",
            f"नवांश (D9, विवाहको कुण्डली) मा लग्न {SIGNS_NE[d9['Lagna']]} छ, र विवाहको कारक शुक्र D1 मा "
            f"{SIGNS_NE[planets['Venus']['sign']]} राशिमा छ।",
        )
    ]
    out["marriage"] = facts

    # Health
    out["health"] = ctx["predictions"]["health"]

    # Education
    facts = [_placement_fact(lords[4], planets, lagna_sign, lords),
             _placement_fact(lords[5], planets, lagna_sign, lords),
             _placement_fact("Mercury", planets, lagna_sign, lords),
             _placement_fact("Jupiter", planets, lagna_sign, lords)]
    out["education"] = facts

    # Family & home
    facts = [_placement_fact(lords[4], planets, lagna_sign, lords),
             _placement_fact(lords[2], planets, lagna_sign, lords),
             _placement_fact("Moon", planets, lagna_sign, lords)]
    out["family"] = facts

    # Foreign travel / settlement
    facts = [_placement_fact(lords[12], planets, lagna_sign, lords),
             _placement_fact(lords[9], planets, lagna_sign, lords),
             _placement_fact("Rahu", planets, lagna_sign, lords)]
    for p in occupants(12):
        facts.append(_placement_fact(p, planets, lagna_sign, lords))
    out["foreign"] = facts

    return out


# ---------------------------------------------------------------------------
# 10-year forecast
# ---------------------------------------------------------------------------
def _period_at(tree: dict, at: datetime):
    for md in tree["mahadashas"]:
        if md["start"] <= at < md["end"]:
            for ad in md["antardashas"]:
                if ad["start"] <= at < ad["end"]:
                    return md, ad
            return md, None
    return None, None


def forecast(ctx: dict, years: int = 10) -> list[dict]:
    planets, lagna_sign = ctx["planets"], ctx["lagna_sign"]
    lords = house_lords(lagna_sign)
    now = ctx["now"]
    out = []
    for i in range(years):
        year = now.year + i
        mid = datetime(year, 7, 1, tzinfo=now.tzinfo)
        md, ad = _period_at(ctx["dasha_tree"], mid)
        if md is None:
            continue
        lord = md["lord"]
        h = house_of(planets[lord]["sign"], lagna_sign)
        ruled = [hh for hh, lp in lords.items() if lp == lord]
        nature = "supportive" if lord in NATURAL_BENEFICS else ("testing" if lord in NATURAL_MALEFICS else "mixed")
        nature_ne = "सहयोगी" if nature == "supportive" else ("परीक्षणशील" if nature == "testing" else "मिश्रित")
        ad_txt_en = f" with {ad['lord']} Antardasha in focus" if ad else ""
        ad_txt_ne = f", {PLANET_NE[ad['lord']]} अन्तर्दशाको प्रभावसहित" if ad else ""
        out.append({
            "year": year,
            "mahadasha": lord,
            "antardasha": ad["lord"] if ad else None,
            "summary": _bi(
                f"{year} runs under {lord} Mahadasha{ad_txt_en}. {lord} sits in your {HOUSE_NAMES_EN[h-1]} house "
                f"({HOUSE_THEMES_EN[h]}) and rules house(s) {', '.join(str(x) for x in ruled)} — a {nature} year for those themes.",
                f"{year} {PLANET_NE[lord]} महादशामा पर्छ{ad_txt_ne}। {PLANET_NE[lord]} तपाईंको {HOUSE_NAMES_NE[h-1]} भावमा "
                f"({HOUSE_THEMES_NE[h]}) छ र भाव {', '.join(str(x) for x in ruled)} को स्वामी हो — ती विषयका लागि {nature_ne} वर्ष।",
            ),
        })
    return out


# ---------------------------------------------------------------------------
# Varshphal (simplified annual chart)
#
# Method (documented simplification of the Tajika annual system):
#   * Solar return = the moment the transiting Sun returns to its exact
#     natal sidereal longitude in the target year (Newton-refined).
#   * Varshphal Lagna = ascendant at that moment for the birth place.
#   * Muntha = natal Lagna sign advanced one sign per completed year.
#   * Year lord = lord of the Varshphal Lagna sign (one of the classical
#     Panchadhikari officers; the full five-officer election is out of
#     scope for this simplified version).
# ---------------------------------------------------------------------------
def _solar_return_jd(natal_sun_lon: float, guess_jd: float) -> float:
    jd = guess_jd
    for _ in range(6):
        sun, _moon = ephemeris.sun_moon_longitudes(jd)
        diff = (natal_sun_lon - sun + 180.0) % 360.0 - 180.0
        jd += diff / 0.9856  # mean solar motion, degrees/day
        if abs(diff) < 1e-5:
            break
    return jd


def varshphal(ctx: dict, years_ahead: int = 3) -> list[dict]:
    birth_dt: datetime = ctx["birth_dt"]
    place = ctx["place"]
    natal_sun = ctx["planets"]["Sun"]["longitude"]
    lagna_sign = ctx["lagna_sign"]
    now: datetime = ctx["now"]
    out = []
    for i in range(years_ahead):
        year = now.year + i
        age = year - birth_dt.year
        if age < 0:
            continue
        # Guess: this year's birthday (local), then refine to the return.
        try:
            guess_local = birth_dt.replace(year=year)
        except ValueError:  # Feb 29 birthdays
            guess_local = birth_dt.replace(year=year, day=28)
        jd_ret = _solar_return_jd(natal_sun, ephemeris.to_julian_day(guess_local))
        v_lagna_lon = ephemeris.ascendant(jd_ret, place["lat"], place["lon"], b"W")
        v_lagna_sign = int(v_lagna_lon // 30.0)
        ret_planets = ephemeris.planet_longitudes(jd_ret)
        muntha_sign = (lagna_sign + age) % 12
        muntha_house = house_of(muntha_sign, v_lagna_sign)
        year_lord = SIGN_LORDS[v_lagna_sign]
        yl_house = house_of(ret_planets[year_lord]["sign"], v_lagna_sign)
        md, ad = _period_at(ctx["dasha_tree"], guess_local)
        out.append({
            "year": year,
            "age": age,
            "varsha_lagna": {"sign": v_lagna_sign, "sign_en": SIGNS_EN[v_lagna_sign], "sign_ne": SIGNS_NE[v_lagna_sign]},
            "muntha": {
                "sign": muntha_sign, "sign_en": SIGNS_EN[muntha_sign], "sign_ne": SIGNS_NE[muntha_sign],
                "house": muntha_house,
            },
            "year_lord": year_lord,
            "reading": _bi(
                f"Annual Lagna {SIGNS_EN[v_lagna_sign]}; year lord {year_lord} is placed in the {HOUSE_NAMES_EN[yl_house-1]} house "
                f"of the annual chart. Muntha is in the {HOUSE_NAMES_EN[muntha_house-1]} house ({HOUSE_THEMES_EN[muntha_house]}), "
                f"focusing the year's experiences there."
                + (f" The year runs mainly under {md['lord']} Mahadasha." if md else ""),
                f"वार्षिक लग्न {SIGNS_NE[v_lagna_sign]}; वर्ष स्वामी {PLANET_NE[year_lord]} वार्षिक कुण्डलीको {HOUSE_NAMES_NE[yl_house-1]} भावमा छ। "
                f"मुन्था {HOUSE_NAMES_NE[muntha_house-1]} भावमा ({HOUSE_THEMES_NE[muntha_house]}) छ, जसले वर्षको अनुभव त्यहाँ केन्द्रित गर्छ।"
                + (f" यो वर्ष मुख्यतः {PLANET_NE[md['lord']]} महादशामा चल्छ।" if md else ""),
            ),
        })
    return out


def generate_premium_report(ctx: dict) -> dict:
    return {
        "chapters": chapters(ctx),
        "favourable_periods": forecast(ctx, years=10),
        "varshphal": varshphal(ctx, years_ahead=3),
        "remedies": remedies(ctx),
        "lucky": lucky_attributes(ctx),
    }
