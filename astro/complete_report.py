"""Complete Kundali Report — one report in the legacy table-of-contents order.

The order follows the Kundli Chakra report contents the user provided
(Title page, Planet Position, Birth Details, Sayan charts, Moon/Navamsa,
Chalit-Bhava, Shodash Varga, Karaka/Avastha/Tara, Sudarshan, aspects,
Upagrahas/Arudha, Vimsopak Bala, Ashtakavarga, Shad/Bhava Bala, Sarvato
Bhadra, Vimshottari, Yogini, Dasha Phal, Varshphal, General Predictions,
Effects of Planets, Nakshatra Phal, Sade-Sati, Manglik, Kaalsarp,
Ratna-Mantra, Yantra).

Data policy: every numeric value comes from the kundali bundle produced
by astro/engine.py compute_kundali — nothing is invented. Sections whose
computation does not exist yet in the engine are present with
``available: False`` and an honest note, so the frontend can show them
as "coming soon" instead of the report silently dropping them.
Predictive text is traditional probability guidance, never a
deterministic medical, legal or financial claim; the title section
carries that disclaimer in both languages.
"""

from __future__ import annotations

from .aspects import (
    aspecting_planets,
    aspected_signs,
    houses_aspected_by,
    planets_aspected_by,
)
from .charts import house_of
from .names import NAKSHATRAS_EN, NAKSHATRAS_NE, PLANETS, PLANET_NE, SIGNS_EN, SIGNS_NE
from .report import BEEJ_MANTRA, PLANET_NUMBER, RUDRAKSHA

DISCLAIMER = {
    "en": (
        "Traditional astrological guidance, offered as probability — not as "
        "certain fact. For health questions consult a clinician, for legal "
        "or financial decisions consult a qualified professional."
    ),
    "ne": (
        "परम्परागत ज्योतिषीय मार्गदर्शन सम्भावनाको रूपमा मात्र हो — निश्चित "
        "तथ्य होइन। स्वास्थ्यका प्रश्नका लागि चिकित्सकसँग, कानुनी वा आर्थिक "
        "निर्णयका लागि योग्य विज्ञसँग परामर्श गर्नुहोस्।"
    ),
}

# Classical Navagraha jaap (recitation) counts — the traditional numbers
# used for planetary propitiation (e.g. Surya 7,000; Shani 23,000).
JAAP_COUNT = {
    "Sun": 7000, "Moon": 11000, "Mars": 10000, "Mercury": 9000,
    "Jupiter": 19000, "Venus": 16000, "Saturn": 23000,
    "Rahu": 18000, "Ketu": 17000,
}

# Yantra associations: the traditional yantra name per planet plus its
# numerological number (already used by the engine's numerology tables).
# No magic-square grid is included — grids vary by tradition, so the
# report names the yantra and its associations rather than printing a
# grid it cannot source.
YANTRA_NE = {
    "Sun": "सूर्य यन्त्र", "Moon": "चन्द्र यन्त्र", "Mars": "मंगल यन्त्र",
    "Mercury": "बुध यन्त्र", "Jupiter": "गुरु यन्त्र", "Venus": "शुक्र यन्त्र",
    "Saturn": "शनि यन्त्र", "Rahu": "राहु यन्त्र", "Ketu": "केतु यन्त्र",
}


def _sec(sid, title_en, title_ne, data, available=True, note=None):
    sec = {"id": sid, "title_en": title_en, "title_ne": title_ne,
           "available": available, "data": data}
    if note is not None:
        sec["note"] = note
    return sec


def _planet_signs(bundle):
    """{planet: sign} rebuilt from the bundle's planet rows."""
    return {row["planet"]: {"sign": row["sign"]} for row in bundle.get("planets", [])}


def _sayan_positions(bundle):
    """Tropical (Sayana) positions = sidereal longitude + ayanamsa.

    Requires bundle['ayanamsa_value'] (degrees at birth, added by the
    engine); without it the section reports itself unavailable.
    """
    aya = bundle.get("ayanamsa_value")
    if aya is None:
        return None
    out = []
    for row in bundle.get("planets", []):
        lon = (row["longitude"] + aya) % 360.0
        sign = int(lon // 30)
        out.append({
            "planet": row["planet"], "planet_ne": row.get("name_ne") or PLANET_NE[row["planet"]],
            "longitude": round(lon, 4), "sign": sign,
            "sign_en": SIGNS_EN[sign], "sign_ne": SIGNS_NE[sign],
            "degree_in_sign": round(lon % 30.0, 3),
        })
    lagna = bundle.get("lagna", {})
    lagna_lon = (lagna.get("longitude", 0.0) + aya) % 360.0
    lagna_sign = int(lagna_lon // 30)
    out.append({
        "planet": "Lagna", "planet_ne": "लग्न", "longitude": round(lagna_lon, 4),
        "sign": lagna_sign, "sign_en": SIGNS_EN[lagna_sign],
        "sign_ne": SIGNS_NE[lagna_sign], "degree_in_sign": round(lagna_lon % 30.0, 3),
    })
    return out


def _ratna_mantra(bundle):
    """Per-planet Ratna-Mantra: gem + mantra + jaap + how to wear.

    Gem/metal/finger/day come from the bundle's gemstone guide; beej
    mantra and Rudraksha from the engine's traditional tables.
    """
    gems = {g["planet"]: g for g in (bundle.get("report", {}).get("gemstones", {}).get("planets", []))}
    out = []
    for planet in PLANETS:
        gem = gems.get(planet, {})
        stone = gem.get("stone", {})
        metal = gem.get("metal", {})
        finger = gem.get("finger", {})
        day = gem.get("day", {})
        mantra_ne, mantra_tr = BEEJ_MANTRA[planet]
        mukhi, rud_en, rud_ne = RUDRAKSHA[planet]
        out.append({
            "planet": planet, "planet_ne": PLANET_NE[planet],
            "introduction": {
                "en": f"Ratna-Mantra for {planet}: the traditional gem, mantra and "
                      f"worship for strengthening this graha.",
                "ne": f"{PLANET_NE[planet]}को रत्न-मन्त्र: यस ग्रहलाई बलियो बनाउने "
                      f"परम्परागत रत्न, मन्त्र र पूजा।",
            },
            "suggestion": {
                "en": f"Wear {stone.get('en', '')} set in {metal.get('en', '')} on the "
                      f"{finger.get('en', '')}, on a {day.get('en', '')}.",
                "ne": f"{day.get('ne', '')}का दिन {metal.get('ne', '')}मा जडित "
                      f"{stone.get('ne', '')} {finger.get('ne', '')}मा धारण गर्नुहोस्।",
            },
            "gemstone": stone, "metal": metal, "finger": finger, "day": day,
            "weight": gem.get("weight_ratti"),
            "rudraksha": {"en": rud_en, "ne": rud_ne, "mukhi": mukhi},
            "beej_mantra": {"ne": mantra_ne, "transliteration": mantra_tr},
            "jaap_count": JAAP_COUNT[planet],
            "how_to_wear": {
                "en": "Wear after purification and mantra recitation on the planet's "
                      "weekday, as advised by a trusted astrologer; the stone "
                      "should be natural and undamaged.",
                "ne": "ग्रहको बारमा शुद्धीकरण र मन्त्र जपपछि, विश्वसनीय ज्योतिषीको "
                      "सल्लाहमा धारण गर्नुहोस्; रत्न प्राकृतिक र क्षतिरहित हुनुपर्छ।",
            },
        })
    return out


def _yantra(bundle):
    """Per-planet Yantra: traditional name, number, weekday, metal, mantra."""
    gems = {g["planet"]: g for g in (bundle.get("report", {}).get("gemstones", {}).get("planets", []))}
    out = []
    for planet in PLANETS:
        gem = gems.get(planet, {})
        mantra_ne, mantra_tr = BEEJ_MANTRA[planet]
        out.append({
            "planet": planet, "planet_ne": PLANET_NE[planet],
            "yantra_en": f"{planet} Yantra", "yantra_ne": YANTRA_NE[planet],
            "number": PLANET_NUMBER[planet],
            "day": gem.get("day", {}), "metal": gem.get("metal", {}),
            "beej_mantra": {"ne": mantra_ne, "transliteration": mantra_tr},
            "guidance": {
                "en": "Traditionally energised on the planet's weekday with its beej "
                      "mantra and kept in the place of worship. Guidance only.",
                "ne": "परम्परागत रूपमा ग्रहको बारमा बीज मन्त्रसहित ऊर्जावान बनाइ पूजा "
                      "स्थानमा राखिन्छ। यो मार्गदर्शन मात्र हो।",
            },
        })
    return out


def build_complete_report(bundle):
    """Assemble the complete report from a compute_kundali bundle.

    The function never crashes on missing optional keys: ``.get`` with
    defaults is used throughout, and genuinely unavailable sections are
    flagged rather than fabricated.
    """
    b = bundle or {}
    birth = b.get("birth", {})
    lagna = b.get("lagna", {})
    planets = b.get("planets", [])
    charts = b.get("charts", {})
    doshas = b.get("doshas", {})
    report = b.get("report", {})
    strength = b.get("strength", {})
    deep = b.get("deep_report", {})
    panchang = b.get("panchang_at_birth", {})
    nak_deep = b.get("nakshatra_deep", {})
    moon_row = next((p for p in planets if p["planet"] == "Moon"), {})

    sayan = _sayan_positions(b)
    signs = _planet_signs(b)
    lagna_sign = lagna.get("sign", 0)

    # Aspects (Parashari graha drishti), computed from bundle signs.
    aspects_planets = []
    for planet in PLANETS:
        if planet not in signs:
            continue
        aspects_planets.append({
            "planet": planet, "planet_ne": PLANET_NE[planet],
            "aspected_signs": [
                {"sign": s, "sign_en": SIGNS_EN[s], "sign_ne": SIGNS_NE[s]}
                for s in aspected_signs(planet, signs)
            ],
            "aspected_houses": houses_aspected_by(planet, signs, lagna_sign),
            "aspected_planets": planets_aspected_by(planet, signs),
        })
    aspects_bhava = []
    for house in range(1, 13):
        sign = (lagna_sign + house - 1) % 12
        aspects_bhava.append({
            "house": house, "sign": sign,
            "sign_en": SIGNS_EN[sign], "sign_ne": SIGNS_NE[sign],
            "aspecting_planets": aspecting_planets(sign, signs),
        })
    aspects_cusps = []
    for cusp in b.get("house_cusps", []):
        sign = cusp.get("sign", 0)
        aspects_cusps.append({
            "cusp": cusp.get("cusp"), "longitude": cusp.get("longitude"),
            "sign": sign, "sign_en": SIGNS_EN[sign], "sign_ne": SIGNS_NE[sign],
            "degree_in_sign": cusp.get("degree_in_sign"),
            "aspecting_planets": aspecting_planets(sign, signs),
        })

    # Shodash Varga table: planet rows x 16 divisional charts.
    varga_names = list(charts.keys())
    shodash_table = [
        {"planet": row["planet"], "planet_ne": row.get("name_ne") or PLANET_NE[row["planet"]],
         "signs": {v: charts[v].get(row["planet"]) for v in varga_names}}
        for row in planets
    ]

    # Varshphal: prefer the 10-year extended set, fall back to the 3-year set.
    varshphal = b.get("varshphal_extended") or report.get("varshphal", [])
    varshphal_years = []
    for year_entry in varshphal:
        chart_map = {"Lagna": year_entry.get("varsha_lagna", {}).get("sign")}
        for p in year_entry.get("planets", []):
            chart_map[p["planet"]] = p["sign"]
        varshphal_years.append({**year_entry, "chart": chart_map})

    sections = [
        _sec("title", "Title Page", "शीर्षक पृष्ठ", {
            "name": b.get("name", ""), "birth": birth, "lagna": lagna,
            "moon": moon_row,
            "moon_nakshatra": {
                "en": moon_row.get("nakshatra_en"), "ne": moon_row.get("nakshatra_ne"),
                "pada": moon_row.get("pada"),
            },
            "ayanamsa": b.get("ayanamsa", {}),
            "house_system": b.get("house_system", {}),
            "disclaimer": DISCLAIMER,
        }),
        _sec("planet_position", "Planet Position", "ग्रह स्थिति", {
            "planets": planets, "lagna": lagna,
        }),
        _sec("birth_details", "Birth Details", "जन्म विवरण", {
            "birth": birth, "panchang_at_birth": panchang,
            "name_letters": b.get("name_letters"),
        }),
        _sec("sayan_charts", "Sayan Position-Charts", "सायन स्थिति-चार्ट", {
            "ayanamsa_value": b.get("ayanamsa_value"),
            "positions": sayan,
        }, available=sayan is not None, note=None if sayan is not None else {
            "en": "Sayana positions need the ayanamsa value at birth, which older bundles lack.",
            "ne": "सायन स्थितिका लागि जन्मकालीन अयनांश मान चाहिन्छ, जुन पुराना बन्डलमा छैन।",
        }),
        _sec("moon_navamsa", "Moon and Navamsa Chart", "चन्द्र र नवांश चार्ट", {
            "d1": charts.get("D1"), "d9": charts.get("D9"),
            "moon": moon_row, "lagna": lagna,
        }),
        _sec("chalit_bhava", "Chalit Chart — Bhava Spasht", "चलित चार्ट — भाव स्पष्ट", {
            "house_cusps": b.get("house_cusps", []),
            "bhava_chalit": b.get("bhava_chalit", {}),
        }),
        _sec("shodash_varga", "Shodash Varga 1 & 2", "षोडश वर्ग १ र २", {
            "part_1": {v: charts[v] for v in varga_names[:8]},
            "part_2": {v: charts[v] for v in varga_names[8:]},
            "vargas": varga_names,
        }),
        _sec("shodash_varga_table", "Shodash Varga Table", "षोडश वर्ग तालिका", {
            "vargas": varga_names, "rows": shodash_table,
        }),
        _sec("karaka_avastha_tara", "Karaka, Avastha, Tara Chakra", "कारक, अवस्था, तारा चक्र", {
            "karakas": b.get("karakas", {}),
            "avasthas": nak_deep.get("avasthas", {}),
            "nava_tara": nak_deep.get("nava_tara", {}),
            "tarabala_today": nak_deep.get("tarabala_today"),
            "chandrabala_today": nak_deep.get("chandrabala_today"),
        }),
        _sec("sudarshan", "Sudarshan Chakra", "सुदर्शन चक्र", {
            "sudarshana": b.get("sudarshana", {}),
        }),
        _sec("aspects_planets", "Aspects on Planets", "ग्रहहरूमाथि दृष्टि", {
            "aspects": aspects_planets,
        }),
        _sec("aspects_bhava", "Aspects on Bhava Middle", "भाव मध्यमाथि दृष्टि", {
            "houses": aspects_bhava,
        }),
        _sec("aspects_cusps", "Aspects on Cusps", "भाव सन्धिमाथि दृष्टि", {
            "cusps": aspects_cusps,
        }, available=bool(aspects_cusps), note=None if aspects_cusps else {
            "en": "No house cusps in this bundle, so cusp aspects cannot be listed.",
            "ne": "यस बन्डलमा भाव सन्धि छैन, त्यसैले सन्धिमाथि दृष्टि देखाउन सकिँदैन।",
        }),
        _sec("upagrahas_arudha", "Upagrahas & Arudha", "उपग्रह र आरूढ", {
            "upagrahas": b.get("upagrahas", {}),
            "arudha_lagna": b.get("special_lagnas", {}).get("arudha_lagna"),
            "upapada": b.get("special_lagnas", {}).get("upapada"),
            "chandra_lagna": b.get("special_lagnas", {}).get("chandra_lagna"),
            "classical_lagnas": b.get("classical_lagnas"),
            "arudha_padas": b.get("arudha_padas"),
        }),
        _sec("vimsopak_bala", "Vimsopak Bala — Shadvarga, Saptavarga, Dashavarga",
             "विंशोपक बल — षड्वर्ग, सप्तवर्ग, दशवर्ग", {
                 "vimshopaka": strength.get("vimshopaka", {}),
             }),
        _sec("ashtakavarga", "Ashtak Varga & Sarvashtak Varga",
             "अष्टक वर्ग र सर्वाष्टक वर्ग", {
                 "per_planet": b.get("ashtakavarga", {}),
                 "sarvashtakavarga": (b.get("ashtakavarga", {}) or {}).get("Sarvashtakavarga"),
                 "shodhya_pindas": b.get("shodhya_pindas", {}),
                 "gochar_reading": b.get("ashtakavarga_gochar"),
             }),
        _sec("shad_bhava_bala", "Shad Bala & Bhava Bala", "षड्बल र भाव बल", {
            "shadbala": strength.get("shadbala", {}),
            "bhava_bala": strength.get("bhava_bala", {}),
            "bhava_bala_note": strength.get("bhava_bala_note", {}),
        }),
        _sec("sarvato_bhadra", "Sarvato Bhadra Chakra", "सर्वतोभद्र चक्र", {
            "sarvatobhadra": b.get("sarvatobhadra", {}),
        }),
        _sec("vimshottari", "Vimshottari Dasha — Mahadasha, Antar, Pratyantar, Sookshma",
             "विंशोत्तरी दशा — महादशा, अन्तर, प्रत्यन्तर, सूक्ष्म", {
                 "mahadashas": b.get("dasha", {}).get("mahadashas", []),
                 "current": b.get("dasha", {}).get("current"),
                 "balance_years": b.get("dasha", {}).get("balance_years"),
                 "dasha_pravesh": b.get("dasha_pravesh"),
             }),
        _sec("yogini", "Yogini Dasha", "योगिनी दशा", {
            "yogini": b.get("yogini", {}),
        }),
        _sec("aaditya_lagnam", "Aaditya & Lagnam Dasha", "आदित्य र लग्नम् दशा", {
            "aaditya": None, "lagnam": None,
        }, available=False, note={
            "en": "Aaditya and Lagnam dashas are not computed by the engine yet; "
                  "the section is reserved in the contents order.",
            "ne": "आदित्य र लग्नम् दशा इन्जिनले अहिलेसम्म गणना गर्दैन; यो खण्ड "
                  "सूचीको क्रममा सुरक्षित राखिएको छ।",
        }),
        _sec("dasha_phala", "Dasha Phal", "दशा फल", {
            "dasha_phala": b.get("dasha_phala", []),
            "deep_dive": deep.get("dasha_deep_dive"),
        }, note={
            "en": "Dasha results are traditional probability guidance, not certainties.",
            "ne": "दशा फल परम्परागत सम्भावना-आधारित मार्गदर्शन मात्र हो, निश्चितता होइन।",
        }),
        _sec("varshphal", "Varshphal — Positions, Predictions & Charts",
             "वर्षफल — स्थिति, भविष्यवाणी र चार्ट", {
                 "years": varshphal_years, "count": len(varshphal_years),
             }, note={
                 "en": "Annual predictions are traditional probability guidance.",
                 "ne": "वार्षिक भविष्यवाणी परम्परागत सम्भावना-आधारित मार्गदर्शन हो।",
             }),
        _sec("general_predictions", "General Predictions", "सामान्य भविष्यवाणी", {
            "chapters": report.get("chapters", {}),
            "predictions": b.get("predictions", {}),
            "favourable_periods": report.get("favourable_periods", []),
            "year_ahead": report.get("year_ahead", []),
        }, note={
            "en": "General predictions are traditional probability guidance.",
            "ne": "सामान्य भविष्यवाणी परम्परागत सम्भावना-आधारित मार्गदर्शन हो।",
        }),
        _sec("effects_of_planets", "Effects of Planets", "ग्रहहरूको प्रभाव", {
            "planet_chapters": deep.get("planet_chapters", []),
            "house_chapters": deep.get("house_chapters", []),
            "divisional_chapters": deep.get("divisional_chapters", []),
        }, note={
            "en": "Planetary effects are traditional probability guidance.",
            "ne": "ग्रह प्रभाव परम्परागत सम्भावना-आधारित मार्गदर्शन हो।",
        }),
        _sec("nakshatra_phal", "Nakshatra Phal", "नक्षत्र फल", {
            "moon_nakshatra": {
                "en": moon_row.get("nakshatra_en"), "ne": moon_row.get("nakshatra_ne"),
                "pada": moon_row.get("pada"),
            },
            "nava_tara": nak_deep.get("nava_tara", {}),
            "avasthas": nak_deep.get("avasthas", {}),
            "name_letters": b.get("name_letters"),
            "ishta_devta": b.get("ishta_devta"),
        }),
        _sec("sade_sati", "Sade-Sati — Introduction, Periods & Remedies",
             "साढे साती — परिचय, अवधि र उपाय", {
                 "current": doshas.get("sade_sati", {}),
                 "lifetime": b.get("sade_sati_lifetime", {}),
                 "remedies": (report.get("remedies", {}).get("dosha_remedies", [])),
             }, note={
                 "en": "Sade-Sati periods are traditional timing guidance, not a "
                      "prediction of harm; remedies are devotional practice.",
                 "ne": "साढे साती अवधि परम्परागत समय-मार्गदर्शन मात्र हो, हानिको "
                      "निश्चित भविष्यवाणी होइन; उपाय भक्ति अभ्यास हुन्।",
             }),
        _sec("manglik", "Manglik Dosha — Introduction & Result",
             "माङ्गलिक दोष — परिचय र परिणाम", {
                 "manglik": doshas.get("manglik", {}),
             }, note={
                 "en": "Manglik assessment is traditional matching guidance, not a "
                      "deterministic statement about marriage.",
                 "ne": "माङ्गलिक मूल्याङ्कन परम्परागत मेल मार्गदर्शन मात्र हो, विवाहबारे "
                      "निश्चित कथन होइन।",
             }),
        _sec("kaalsarp", "Kaalsarp Yoga", "कालसर्प योग", {
            "kaal_sarp": doshas.get("kaal_sarp", {}),
        }),
        _sec("ratna_mantra", "Ratna-Mantra — Introduction, Suggestion, Jaap & How to Wear",
             "रत्न-मन्त्र — परिचय, सुझाव, जप र धारण विधि", {
                 "per_planet": _ratna_mantra(b),
                 "remedies": report.get("remedies", {}),
             }),
        _sec("yantra", "Yantra — Sun to Ketu", "यन्त्र — सूर्यदेखि केतुसम्म", {
            "per_planet": _yantra(b),
        }),
    ]

    return {
        "title": {
            "name": b.get("name", ""),
            "birth": birth,
            "disclaimer": DISCLAIMER,
        },
        "sections": sections,
        "section_ids": [s["id"] for s in sections],
    }
