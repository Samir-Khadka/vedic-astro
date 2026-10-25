"""Nakshatra deep-dive — Nava Tara, Tarabala, Chandrabala, Avasthas.

Rules implemented (our own wording of the published tables):

* Nava Tara: the 27 nakshatras counted cyclically from the natal
  Moon nakshatra fall into nine Taras — 1 Janma, 2 Sampat, 3 Vipat,
  4 Kshema, 5 Pratyak, 6 Sadhana, 7 Naidhana, 8 Mitra, 9 Parama
  Mitra — repeating in three cycles (paryayas) of nine. Taras
  Vipat (3), Pratyak (5) and Naidhana (7) are caution Taras; the
  other six are favourable. Classical nuance kept: in the second
  cycle the evil is said to be halved, in the third negligible —
  but the caution flag is still shown, because the tradition also
  advises avoiding Vipat and Naidhana stars for important
  undertakings even in the third cycle.
* Tarabala for a day: the day's Moon nakshatra counted from the
  natal Moon nakshatra, reduced mod 9 to its Tara.
* Chandrabala: the transit Moon's sign counted from the natal Moon
  sign (Janma Rashi). Favourable positions: 1, 3, 6, 7, 10, 11.
  Neutral: 2, 5, and 9 (the 9th is the position the sources split
  on — one tradition calls it mildly unfavourable, the classical
  Muhurta text lists it among the strong; neutral is the
  defensible middle and the split is noted). Avoid: 4, 8, 12 —
  the 8th is Ashtama Chandra, the hardest position.
* Avasthas (BPHS ch. 45, Balaadi + Jagratadi):
  - Balaadi: each sign is split into five 6-degree parts. In odd
    signs the order is Bala, Kumara, Yuva, Vriddha, Mrita; in even
    signs it reverses (Mrita, Vriddha, Yuva, Kumara, Bala).
    Result strength: Bala 1/4, Kumara 1/2, Yuva full, Vriddha
    minimal, Mrita none. (Vriddha is also called Proudha in some
    texts.)
  - Jagratadi: a planet in its own or exaltation sign is Jagrat
    (awake, full results); in a friendly or neutral sign Swapna
    (dreaming, medium results); in an enemy's sign or debilitation
    Sushupti (sleeping, no results). Rahu and Ketu have no
    own/exaltation/friendship table here, so their Jagratadi is
    reported as indeterminate (Swapna by default, flagged).
"""
from __future__ import annotations

from .names import (
    EXALTATION, FRIENDSHIP, NAKSHATRAS_EN, NAKSHATRAS_NE, OWN_SIGNS,
    PLANET_NE, SIGNS_EN, SIGNS_NE, SIGN_LORDS,
)

TARA_EN = ["Janma", "Sampat", "Vipata", "Kshema", "Pratyak",
           "Sadhana", "Naidhana", "Mitra", "Parama Mitra"]
# "Vipata" is the common transliteration; Vipat is used in readings.
TARA_NE = ["जन्म", "सम्पत्", "विपत्", "क्षेम", "प्रत्यक्",
           "साधन", "नैधन", "मित्र", "परम मित्र"]
CAUTION_TARAS = {3, 5, 7}

CHANDRA_FAVOURABLE = {1, 3, 6, 7, 10, 11}
CHANDRA_NEUTRAL = {2, 5, 9}
CHANDRA_AVOID = {4, 8, 12}

_BALAADI_ODD = ["Bala", "Kumara", "Yuva", "Vriddha", "Mrita"]
_BALAADI_NE = {"Bala": "बाल", "Kumara": "कुमार", "Yuva": "युवा",
               "Vriddha": "वृद्ध", "Mrita": "मृत"}
_BALAADI_STRENGTH = {"Bala": 0.25, "Kumara": 0.5, "Yuva": 1.0,
                     "Vriddha": 0.1, "Mrita": 0.0}
_JAGRAT_NE = {"Jagrat": "जाग्रत्", "Swapna": "स्वप्न", "Sushupti": "सुषुप्ति"}


def _bi(en: str, ne: str) -> dict:
    return {"en": en, "ne": ne}


def tara_of(natal_nak: int, day_nak: int) -> dict:
    """Tara of `day_nak` counted from `natal_nak` (1-based count, mod 9)."""
    count = (day_nak - natal_nak) % 27 + 1
    tara = (count - 1) % 9 + 1
    cycle = (count - 1) // 9 + 1
    name = TARA_EN[tara - 1]
    if tara in CAUTION_TARAS:
        verdict = "caution"
        strength_note = ("full caution" if cycle == 1 else
                         "half strength (2nd cycle)" if cycle == 2 else
                         "negligible by cycle, still flagged")
    else:
        verdict = "favourable"
        strength_note = "favourable"
    return {
        "count": count, "cycle": cycle,
        "tara": tara, "tara_en": name, "tara_ne": TARA_NE[tara - 1],
        "verdict": verdict, "strength_note": strength_note,
    }


def nava_tara(natal_nak: int) -> dict:
    """All 27 nakshatras with their Tara relative to the natal Moon star."""
    rows = []
    for nak in range(27):
        t = tara_of(natal_nak, nak)
        rows.append({
            "nakshatra": nak,
            "nakshatra_en": NAKSHATRAS_EN[nak],
            "nakshatra_ne": NAKSHATRAS_NE[nak],
            **t,
        })
    return {
        "natal_nakshatra": natal_nak,
        "natal_nakshatra_en": NAKSHATRAS_EN[natal_nak],
        "natal_nakshatra_ne": NAKSHATRAS_NE[natal_nak],
        "taras": rows,
        "caution_stars": [r["nakshatra_en"] for r in rows if r["verdict"] == "caution"],
    }


def chandrabala(natal_moon_sign: int, transit_moon_sign: int) -> dict:
    """Chandra Bala: transit Moon sign counted from the natal Moon sign."""
    pos = (transit_moon_sign - natal_moon_sign) % 12 + 1
    if pos in CHANDRA_FAVOURABLE:
        verdict = "favourable"
    elif pos in CHANDRA_NEUTRAL:
        verdict = "neutral"
    else:
        verdict = "avoid"
    note = ""
    if pos == 8:
        note = "Ashtama Chandra — the position texts warn about hardest."
    if pos == 9:
        note = ("Sources split on the 9th: one tradition calls it mildly "
                "unfavourable, the classical Muhurta text lists it among "
                "the strong; scored neutral here.")
    return {
        "natal_moon_sign": natal_moon_sign,
        "natal_moon_sign_en": SIGNS_EN[natal_moon_sign],
        "natal_moon_sign_ne": SIGNS_NE[natal_moon_sign],
        "transit_moon_sign": transit_moon_sign,
        "transit_moon_sign_en": SIGNS_EN[transit_moon_sign],
        "transit_moon_sign_ne": SIGNS_NE[transit_moon_sign],
        "position": pos, "verdict": verdict, "note": note,
    }


def _sign_relation(planet: str, sign: int) -> str:
    """own / exalted / debilitated / friend / enemy / neutral / unknown."""
    if planet in ("Rahu", "Ketu"):
        return "unknown"
    if planet in OWN_SIGNS and sign in OWN_SIGNS[planet]:
        return "own"
    if planet in EXALTATION:
        ex = EXALTATION[planet][0]
        if sign == ex:
            return "exalted"
        if sign == (ex + 6) % 12:
            return "debilitated"
    lord = SIGN_LORDS[sign]
    friends, _neutral, enemies = FRIENDSHIP[planet]
    if lord in friends:
        return "friend"
    if lord in enemies:
        return "enemy"
    return "neutral"


def avastha(planet: str, sign: int, degree_in_sign: float) -> dict:
    """Balaadi + Jagratadi avasthas for one planet."""
    idx = min(4, int(degree_in_sign // 6.0))
    odd = sign % 2 == 0  # Aries (0) is the 1st, odd, sign
    bala = _BALAADI_ODD[idx] if odd else _BALAADI_ODD[4 - idx]
    relation = _sign_relation(planet, sign)
    if relation in ("own", "exalted"):
        jagrat = "Jagrat"
    elif relation in ("enemy", "debilitated"):
        jagrat = "Sushupti"
    else:
        jagrat = "Swapna"
    return {
        "planet": planet, "planet_ne": PLANET_NE[planet],
        "sign": sign, "sign_en": SIGNS_EN[sign], "sign_ne": SIGNS_NE[sign],
        "degree_in_sign": round(degree_in_sign, 3),
        "balaadi": bala, "balaadi_ne": _BALAADI_NE[bala],
        "balaadi_strength": _BALAADI_STRENGTH[bala],
        "sign_relation": relation,
        "jagratadi": jagrat, "jagratadi_ne": _JAGRAT_NE[jagrat],
        "reading": _bi(
            f"{planet} in {SIGNS_EN[sign]} at {degree_in_sign:.1f} deg is in {bala} avastha "
            f"({int(_BALAADI_STRENGTH[bala] * 100)}% of its results) and {jagrat} avastha "
            f"({relation} sign).",
            f"{PLANET_NE[planet]} {SIGNS_NE[sign]} मा {degree_in_sign:.1f} डिग्रीमा {_BALAADI_NE[bala]} अवस्थामा "
            f"(फलको {int(_BALAADI_STRENGTH[bala] * 100)}%) र {_JAGRAT_NE[jagrat]} अवस्थामा छ ({relation} राशि)।"),
    }


def avasthas_for_chart(planets: dict) -> dict:
    """Avasthas for all nine grahas of a chart."""
    rows = []
    for name in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"):
        if name not in planets:
            continue
        rows.append(avastha(name, planets[name]["sign"], planets[name]["degree_in_sign"]))
    return {
        "planets": rows,
        "method_note": _bi(
            "Balaadi: 6-degree parts, order reversed in even signs (BPHS ch. 45). "
            "Jagratadi: own/exalted = Jagrat, friendly/neutral = Swapna, enemy/debilitated = Sushupti. "
            "Rahu/Ketu Jagratadi is indeterminate (no classical dignity table) and shown as Swapna.",
            "बालादि: ६-डिग्री भाग, सम राशिमा क्रम उल्टो (BPHS अध्याय ४५)। "
            "जाग्रतादि: स्व/उच्च = जाग्रत्, मित्र/सम = स्वप्न, शत्रु/नीच = सुषुप्ति। "
            "राहु/केतुको जाग्रतादि अनिश्चित छ (कुनै शास्त्रीय बल तालिका छैन) र स्वप्नका रूपमा देखाइएको छ।"),
    }
