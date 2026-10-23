"""Ashtakoota Guna Milan — the 36-point North Indian compatibility system.

Computed from the Moon's sign and nakshatra of both partners. Tables are the
classical published ones; the Vashya and Yoni schemes use their standard
simplified group forms (documented in-line).
"""
from __future__ import annotations

# --- Varna (1): spiritual grade by Moon sign element -------------------------
# Brahmin (water) > Kshatriya (fire) > Vaishya (earth) > Shudra (air)
VARNA_OF_SIGN = {
    3: 0, 7: 0, 11: 0,      # Cancer, Scorpio, Pisces — Brahmin
    0: 1, 4: 1, 8: 1,       # Aries, Leo, Sagittarius — Kshatriya
    1: 2, 5: 2, 9: 2,       # Taurus, Virgo, Capricorn — Vaishya
    2: 3, 6: 3, 10: 3,      # Gemini, Libra, Aquarius — Shudra
}
VARNA_NAMES = ["Brahmin", "Kshatriya", "Vaishya", "Shudra"]

# --- Vashya (2): sign groups -------------------------------------------------
# Manav (human), Jalchar (water), Chatushpad (quadruped), Vanchar (wild), Keet (insect)
VASHYA_OF_SIGN = {
    2: "Manav", 5: "Manav", 6: "Manav", 10: "Manav", 8: "Manav",
    3: "Jalchar", 11: "Jalchar", 9: "Jalchar",
    0: "Chatushpad", 1: "Chatushpad",
    4: "Vanchar",
    7: "Keet",
}
# Points matrix [groom group][bride group] — classical compatibility table.
_VG = ["Chatushpad", "Manav", "Jalchar", "Vanchar", "Keet"]
VASHYA_MATRIX = {
    "Chatushpad": [2, 0, 1, 1, 1],
    "Manav": [0, 2, 1, 0, 1],
    "Jalchar": [1, 1, 2, 1, 1],
    "Vanchar": [1, 0, 1, 2, 1],
    "Keet": [1, 1, 1, 1, 2],
}

# --- Yoni (4): animal of the nakshatra --------------------------------------
YONI_OF_NAKSHATRA = [
    "Horse", "Elephant", "Goat", "Serpent", "Serpent", "Dog", "Cat",
    "Goat", "Cat", "Rat", "Rat", "Cow", "Buffalo", "Tiger", "Buffalo",
    "Tiger", "Deer", "Deer", "Dog", "Monkey", "Mongoose", "Monkey",
    "Lion", "Horse", "Lion", "Cow", "Elephant",
]
YONI_EXTREME_ENEMIES = {
    frozenset(p) for p in [
        ("Horse", "Buffalo"), ("Elephant", "Lion"), ("Goat", "Monkey"),
        ("Serpent", "Mongoose"), ("Dog", "Deer"), ("Cat", "Rat"), ("Cow", "Tiger"),
    ]
}
YONI_ENEMIES = {
    frozenset(p) for p in [("Dog", "Cat"), ("Serpent", "Rat"), ("Tiger", "Deer"), ("Lion", "Deer")]
}


def _yoni_points(a: str, b: str) -> float:
    if a == b:
        return 4.0
    pair = frozenset((a, b))
    if pair in YONI_EXTREME_ENEMIES:
        return 0.0
    if pair in YONI_ENEMIES:
        return 1.0
    return 3.0 if len(pair) == 2 and _yoni_friendly(a, b) else 2.0


def _yoni_friendly(a: str, b: str) -> bool:
    friendly = {
        frozenset(p) for p in [("Cow", "Horse"), ("Elephant", "Cow"), ("Deer", "Cow"), ("Monkey", "Rat")]
    }
    return frozenset((a, b)) in friendly


# --- Gana (6) ----------------------------------------------------------------
_GANA = {
    "Deva": {"Ashwini", "Mrigashira", "Punarvasu", "Pushya", "Hasta", "Swati", "Anuradha", "Shravana", "Revati"},
    "Manushya": {"Bharani", "Rohini", "Ardra", "Purva Phalguni", "Uttara Phalguni", "Purva Ashadha", "Uttara Ashadha", "Purva Bhadrapada", "Uttara Bhadrapada"},
    "Rakshasa": {"Krittika", "Ashlesha", "Magha", "Chitra", "Vishakha", "Jyeshtha", "Mula", "Dhanishta", "Shatabhisha"},
}
GANA_MATRIX = {  # [groom][bride]
    "Deva": {"Deva": 6, "Manushya": 5, "Rakshasa": 1},
    "Manushya": {"Deva": 6, "Manushya": 6, "Rakshasa": 0},
    "Rakshasa": {"Deva": 1, "Manushya": 0, "Rakshasa": 6},
}

# --- Nadi (8) -----------------------------------------------------------------
NADI_OF_NAKSHATRA = [
    "Aadi", "Madhya", "Antya", "Antya", "Madhya", "Aadi",
    "Aadi", "Madhya", "Antya", "Antya", "Madhya", "Aadi",
    "Aadi", "Madhya", "Antya", "Antya", "Madhya", "Aadi",
    "Aadi", "Madhya", "Antya", "Antya", "Madhya", "Aadi",
    "Aadi", "Madhya", "Antya",
]

# --- Graha Maitri (5) ----------------------------------------------------------
from .names import FRIENDSHIP, SIGN_LORDS  # noqa: E402


def _relation(a: str, b: str) -> str:
    if a == b:
        return "friend"
    friends, neutral, enemies = FRIENDSHIP[a]
    if b in friends:
        return "friend"
    if b in enemies:
        return "enemy"
    return "neutral"


def _maitri_points(groom_lord: str, bride_lord: str) -> float:
    if groom_lord == bride_lord:
        return 5.0
    r1 = _relation(groom_lord, bride_lord)
    r2 = _relation(bride_lord, groom_lord)
    combo = frozenset((r1, r2))
    if combo == frozenset(("friend",)):
        return 5.0
    if combo == frozenset(("friend", "neutral")):
        return 4.0
    if combo == frozenset(("neutral",)):
        return 3.0
    if combo == frozenset(("friend", "enemy")):
        return 0.0
    if combo == frozenset(("neutral", "enemy")):
        return 1.0
    return 0.0  # enemy / enemy


def _tara_points(groom_nak: int, bride_nak: int) -> float:
    def ok(frm: int, to: int) -> bool:
        count = (to - frm) % 27 + 1
        return count % 9 not in (3, 5, 7)
    g = ok(bride_nak, groom_nak)
    b = ok(groom_nak, bride_nak)
    return (1.5 if g else 0.0) + (1.5 if b else 0.0)


def _bhakoot_points(groom_sign: int, bride_sign: int) -> float:
    rel_g = (bride_sign - groom_sign) % 12 + 1   # bride's sign counted from groom's
    rel_b = (groom_sign - bride_sign) % 12 + 1
    if (rel_g, rel_b) in {(6, 8), (8, 6), (9, 5), (5, 9), (12, 2), (2, 12)}:
        return 0.0
    return 7.0


def guna_milan(groom: dict, bride: dict) -> dict:
    """groom/bride: {'moon_sign': int, 'moon_nakshatra': int}"""
    gs, bs = groom["moon_sign"], bride["moon_sign"]
    gn, bn = groom["moon_nakshatra"], bride["moon_nakshatra"]

    varna = 1.0 if VARNA_OF_SIGN[gs] <= VARNA_OF_SIGN[bs] else 0.0
    vashya = float(VASHYA_MATRIX[VASHYA_OF_SIGN[gs]][_VG.index(VASHYA_OF_SIGN[bs])])
    tara = _tara_points(gn, bn)
    yoni = _yoni_points(YONI_OF_NAKSHATRA[gn], YONI_OF_NAKSHATRA[bn])
    maitri = _maitri_points(SIGN_LORDS[gs], SIGN_LORDS[bs])
    from .names import NAKSHATRAS_EN
    gana_g = next(g for g, s in _GANA.items() if NAKSHATRAS_EN[gn] in s)
    gana_b = next(g for g, s in _GANA.items() if NAKSHATRAS_EN[bn] in s)
    gana = float(GANA_MATRIX[gana_g][gana_b])
    bhakoot = _bhakoot_points(gs, bs)
    nadi_same = NADI_OF_NAKSHATRA[gn] == NADI_OF_NAKSHATRA[bn]
    nadi = 0.0 if nadi_same else 8.0

    parts = [
        {"koota": "Varna", "max": 1, "score": varna,
         "detail": f"Groom {VARNA_NAMES[VARNA_OF_SIGN[gs]]}, bride {VARNA_NAMES[VARNA_OF_SIGN[bs]]}"},
        {"koota": "Vashya", "max": 2, "score": vashya,
         "detail": f"Groom {VASHYA_OF_SIGN[gs]}, bride {VASHYA_OF_SIGN[bs]}"},
        {"koota": "Tara", "max": 3, "score": tara,
         "detail": "Birth-star compatibility counted both ways"},
        {"koota": "Yoni", "max": 4, "score": yoni,
         "detail": f"Groom {YONI_OF_NAKSHATRA[gn]}, bride {YONI_OF_NAKSHATRA[bn]}"},
        {"koota": "Graha Maitri", "max": 5, "score": maitri,
         "detail": f"Moon-sign lords: groom {SIGN_LORDS[gs]}, bride {SIGN_LORDS[bs]}"},
        {"koota": "Gana", "max": 6, "score": gana,
         "detail": f"Groom {gana_g}, bride {gana_b}"},
        {"koota": "Bhakoot", "max": 7, "score": bhakoot,
         "detail": "Moon-sign relative positions (6-8 / 9-5 / 2-12 are dosha pairs)"},
        {"koota": "Nadi", "max": 8, "score": nadi,
         "detail": f"Groom {NADI_OF_NAKSHATRA[gn]}, bride {NADI_OF_NAKSHATRA[bn]}"
                   + (" — same Nadi (Nadi dosha)" if nadi_same else "")},
    ]
    total = sum(p["score"] for p in parts)
    if total >= 32:
        verdict_en, verdict_ne = "Excellent match", "उत्कृष्ट मेल"
    elif total >= 25:
        verdict_en, verdict_ne = "Good match", "राम्रो मेल"
    elif total >= 18:
        verdict_en, verdict_ne = "Acceptable match (average)", "स्वीकार्य मेल (मध्यम)"
    else:
        verdict_en, verdict_ne = "Below the traditional threshold of 18", "परम्परागत १८ अङ्कको सीमाभन्दा तल"
    return {
        "total": total, "max": 36, "breakdown": parts,
        "verdict_en": verdict_en, "verdict_ne": verdict_ne,
        "nadi_dosha": nadi_same,
    }
