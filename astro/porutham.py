"""Dashakoota / Porutham — the South Indian 10-factor matching system.

Computed from the two partners' Moon nakshatras and Moon signs, as a
second matching system alongside the North Indian Ashtakoota Guna
Milan. Scoring uses the widely published 36-point weighting
(Dina 3, Gana 4, Yoni 4, Rasi 7, Rasyadhipati 5, Rajju 5, Vedha 2,
Vashya 2, Mahendra 2, Sthree Deergha 2); 18+ is the traditional
acceptance threshold. Variants exist for several factors and are
noted where they matter — the chosen rule is always stated.

Rules implemented (our own wording of the published tables):

* Dina: count the groom's nakshatra from the bride's; divide by 9.
  Remainders 3, 5, 7 fail; the rest pass.
* Gana: Deva / Manushya / Rakshasa groups of nine nakshatras each.
  Same group passes fully; a Deva–Manushya pair passes well;
  any pair mixing Rakshasa with another group fails. (Some texts
  grade the Deva–Manushya direction; this implementation scores
  the pair without direction and says so.)
* Mahendra: count the bride's nakshatra from the groom's; counts
  4, 7, 10, 13, 16, 19, 22, 25 pass.
* Sthree Deergha: count the bride's nakshatra from the groom's;
  more than 13 passes. (Some traditions require more than 15, or
  count the other direction — noted, not silently adopted.)
* Yoni: the 14-animal table (mongoose belongs to Uttara Ashadha
  alone). Five tiers after Muhurta Chintamani: same animal 4,
  friend pair 3 (horse–elephant, elephant–cow), neutral 2, mild
  enemy 1 (serpent–rat), bitter enemy 0 (the seven sworn pairs:
  horse–buffalo, elephant–lion, goat–monkey, serpent–mongoose,
  dog–deer, cat–rat, cow–tiger). Some lists count serpent–rat
  among the bitter pairs; the five-tier reading is used here.
* Rasi: the groom's Moon sign counted from the bride's; 6th, 8th
  or 12th fails, the rest pass. (A stricter tradition requires
  the same sign or the 7th; noted.)
* Rasyadhipati (Graha Maitri): the two Moon-sign lords' natural
  relationship — same lord or mutual friends 5, friend–neutral 4,
  neutral–neutral 3, neutral–enemy 1, friend–enemy or mutual
  enemies 0. This mirrors the Ashtakoota Graha Maitri scoring.
* Vasya: the classical control table (Aries: Leo, Scorpio;
  Taurus: Cancer, Libra; Gemini: Virgo; Cancer: Scorpio,
  Sagittarius; Leo: Libra; Virgo: Pisces; Libra: Virgo,
  Capricorn; Scorpio: Cancer; Sagittarius: Pisces; Capricorn:
  Aries, Aquarius; Aquarius: Aries; Pisces: Capricorn). The
  bride's sign vasya to the groom's scores full; the reverse
  direction alone scores half. Vasya tables vary by tradition.
* Rajju: five body groups — Siro (Mrigashira, Chitra, Dhanishta),
  Kanta (Rohini, Ardra, Hasta, Swati, Shravana, Shatabhisha),
  Udara (Krittika, Punarvasu, Uttara Phalguni, Vishakha, Uttara
  Ashadha, Purva Bhadrapada), Kati (Bharani, Pushya, Purva
  Phalguni, Anuradha, Purva Ashadha, Uttara Bhadrapada), Pada
  (Ashwini, Ashlesha, Magha, Jyeshtha, Mula, Revati). Same group
  = Rajju Dosha, the most serious flag: it is reported even when
  the total passes, because classical authorities treat it as a
  deal-breaker unless precise cancellations apply.
* Vedha: thirteen piercing pairs (Ashwini–Jyeshtha,
  Bharani–Anuradha, Krittika–Vishakha, Rohini–Swati,
  Ardra–Shravana, Punarvasu–Uttara Ashadha, Pushya–Purva Ashadha,
  Ashlesha–Mula, Magha–Revati, Purva Phalguni–Uttara Bhadrapada,
  Uttara Phalguni–Purva Bhadrapada, Hasta–Shatabhisha,
  Mrigashira–Dhanishta). Chitra neither gives nor receives Vedha.
  A pair fails; anything else passes.
"""
from __future__ import annotations

from .matching import YONI_EXTREME_ENEMIES, YONI_OF_NAKSHATRA
from .names import (
    FRIENDSHIP, NAKSHATRAS_EN, NAKSHATRAS_NE, PLANET_NE, SIGNS_EN, SIGNS_NE,
    SIGN_LORDS,
)

GANA_OF_NAK = {}
for _nak in (0, 4, 6, 7, 12, 14, 16, 21, 26):
    GANA_OF_NAK[_nak] = "Deva"
for _nak in (1, 3, 5, 10, 11, 19, 20, 24, 25):
    GANA_OF_NAK[_nak] = "Manushya"
for _nak in (2, 8, 9, 13, 15, 17, 18, 22, 23):
    GANA_OF_NAK[_nak] = "Rakshasa"
GANA_NE = {"Deva": "देव", "Manushya": "मनुष्य", "Rakshasa": "राक्षस"}

RAJJU_OF_NAK = {}
for _nak in (4, 13, 22):
    RAJJU_OF_NAK[_nak] = "Siro"
for _nak in (3, 5, 12, 14, 21, 23):
    RAJJU_OF_NAK[_nak] = "Kanta"
for _nak in (2, 6, 11, 15, 20, 24):
    RAJJU_OF_NAK[_nak] = "Udara"
for _nak in (1, 7, 10, 16, 19, 25):
    RAJJU_OF_NAK[_nak] = "Kati"
for _nak in (0, 8, 9, 17, 18, 26):
    RAJJU_OF_NAK[_nak] = "Pada"
RAJJU_NE = {"Siro": "शिरो", "Kanta": "कण्ठ", "Udara": "उदर", "Kati": "कटि", "Pada": "पाद"}
RAJJU_EFFECT_EN = {
    "Siro": "husband's longevity", "Kanta": "wife's longevity",
    "Udara": "progeny", "Kati": "wealth", "Pada": "travel and stability",
}
RAJJU_EFFECT_NE = {
    "Siro": "पति आयु", "Kanta": "पत्नी आयु",
    "Udara": "सन्तान", "Kati": "धन", "Pada": "यात्रा र स्थिरता",
}

VEDHA_PAIRS = {
    frozenset(p) for p in [
        (0, 17), (1, 16), (2, 15), (3, 14), (5, 21), (6, 20), (7, 19),
        (8, 18), (9, 26), (10, 25), (11, 24), (12, 23), (4, 22),
    ]
}

# Vasya control table: sign -> set of signs it controls.
VASYA = {
    0: {4, 7}, 1: {3, 6}, 2: {5}, 3: {7, 8}, 4: {6}, 5: {11},
    6: {5, 9}, 7: {3}, 8: {11}, 9: {0, 10}, 10: {0}, 11: {9},
}

_YONI_FRIENDS = {frozenset(p) for p in [("Horse", "Elephant"), ("Elephant", "Cow")]}
_YONI_MILD_ENEMY = frozenset(("Serpent", "Rat"))
YONI_NE = {
    "Horse": "घोडा", "Elephant": "हात्ती", "Goat": "बाख्रा", "Serpent": "सर्प",
    "Dog": "कुकुर", "Cat": "बिरालो", "Rat": "मुसा", "Cow": "गाई",
    "Buffalo": "भैंसी", "Tiger": "बाघ", "Deer": "मृग", "Monkey": "बाँदर",
    "Mongoose": "नेवला", "Lion": "सिंह",
}


def _bi(en: str, ne: str) -> dict:
    return {"en": en, "ne": ne}


def _count(frm: int, to: int, mod: int) -> int:
    return (to - frm) % mod + 1


def _lord_relation(a: str, b: str) -> str:
    if a == b:
        return "friend"
    friends, _neutral, enemies = FRIENDSHIP[a]
    if b in friends:
        return "friend"
    if b in enemies:
        return "enemy"
    return "neutral"


def _maitri_points(groom_lord: str, bride_lord: str) -> float:
    if groom_lord == bride_lord:
        return 5.0
    r1 = _lord_relation(groom_lord, bride_lord)
    r2 = _lord_relation(bride_lord, groom_lord)
    combo = frozenset((r1, r2))
    if combo == frozenset(("friend",)):
        return 5.0
    if combo == frozenset(("friend", "neutral")):
        return 4.0
    if combo == frozenset(("neutral",)):
        return 3.0
    if combo == frozenset(("neutral", "enemy")):
        return 1.0
    return 0.0


def _yoni_points(a: str, b: str) -> float:
    if a == b:
        return 4.0
    pair = frozenset((a, b))
    if pair in YONI_EXTREME_ENEMIES:
        return 0.0
    if pair == _YONI_MILD_ENEMY:
        return 1.0
    if pair in _YONI_FRIENDS:
        return 3.0
    return 2.0


def porutham(groom: dict, bride: dict) -> dict:
    """groom/bride: {'moon_sign': int, 'moon_nakshatra': int}.

    Convention: the groom is counted first where a rule has a
    direction (Mahendra, Sthree Deergha count the bride's star from
    the groom's; Dina counts the groom's star from the bride's).
    """
    gs, bs = groom["moon_sign"], bride["moon_sign"]
    gn, bn = groom["moon_nakshatra"], bride["moon_nakshatra"]
    parts = []

    def _part(name, name_ne, maximum, score, detail_en, detail_ne):
        parts.append({
            "porutham": name, "porutham_ne": name_ne, "max": maximum,
            "score": score,
            "detail": _bi(detail_en, detail_ne),
            "passed": score >= maximum / 2.0,
        })

    # Dina: groom's star from bride's, mod 9.
    dina_count = _count(bn, gn, 27)
    dina_pass = dina_count % 9 not in (3, 5, 7)
    _part("Dina", "दिन", 3, 3.0 if dina_pass else 0.0,
          f"Count bride to groom: {dina_count} (remainder {dina_count % 9}) — " +
          ("passes" if dina_pass else "fails (remainder 3, 5 or 7)"),
          f"दुलहीबाट दुलहासम्म गणना: {dina_count} (शेष {dina_count % 9}) — " +
          ("उत्तीर्ण" if dina_pass else "अनुत्तीर्ण (शेष ३, ५ वा ७)"))

    # Gana.
    gg, bg = GANA_OF_NAK[gn], GANA_OF_NAK[bn]
    if gg == bg:
        gana_score = 4.0
    elif {gg, bg} == {"Deva", "Manushya"}:
        gana_score = 3.0
    else:
        gana_score = 0.0
    _part("Gana", "गण", 4, gana_score,
          f"Groom {gg}, bride {bg}",
          f"दुलहा {GANA_NE[gg]}, दुलही {GANA_NE[bg]}")

    # Mahendra: bride's star from groom's.
    mah_count = _count(gn, bn, 27)
    mah_pass = mah_count in (4, 7, 10, 13, 16, 19, 22, 25)
    _part("Mahendra", "महेन्द्र", 2, 2.0 if mah_pass else 0.0,
          f"Count groom to bride: {mah_count} — " +
          ("one of 4/7/10/13/16/19/22/25" if mah_pass else "not a Mahendra count"),
          f"दुलहाबाट दुलहीसम्म गणना: {mah_count} — " +
          ("४/७/१०/१३/१६/१९/२२/२५ मध्ये एक" if mah_pass else "महेन्द्र गणना होइन"))

    # Sthree Deergha: bride's star from groom's, more than 13.
    sd_pass = mah_count > 13
    _part("Sthree Deergha", "स्त्री दीर्घ", 2, 2.0 if sd_pass else 0.0,
          f"Count groom to bride: {mah_count} — " +
          ("more than 13" if sd_pass else "13 or fewer"),
          f"दुलहाबाट दुलहीसम्म गणना: {mah_count} — " +
          ("१३ भन्दा बढी" if sd_pass else "१३ वा कम"))

    # Yoni.
    gy, by = YONI_OF_NAKSHATRA[gn], YONI_OF_NAKSHATRA[bn]
    yoni_score = _yoni_points(gy, by)
    _part("Yoni", "योनि", 4, yoni_score,
          f"Groom {gy}, bride {by}",
          f"दुलहा {YONI_NE[gy]}, दुलही {YONI_NE[by]}")

    # Rasi: groom's sign from bride's; 6/8/12 fail.
    rasi_count = _count(bs, gs, 12)
    rasi_pass = rasi_count not in (6, 8, 12)
    _part("Rasi", "राशि", 7, 7.0 if rasi_pass else 0.0,
          f"Groom's Moon sign {SIGNS_EN[gs]} is {rasi_count} from bride's {SIGNS_EN[bs]} — " +
          ("passes" if rasi_pass else "fails (6th, 8th or 12th)"),
          f"दुलहाको चन्द्र राशि {SIGNS_NE[gs]} दुलहीको {SIGNS_NE[bs]} बाट {rasi_count}औँ — " +
          ("उत्तीर्ण" if rasi_pass else "अनुत्तीर्ण (६, ८ वा १२औँ)"))

    # Rasyadhipati: Moon-sign lords' friendship.
    gl, bl = SIGN_LORDS[gs], SIGN_LORDS[bs]
    mai_score = _maitri_points(gl, bl)
    _part("Rasyadhipati", "राश्यधिपति", 5, mai_score,
          f"Moon-sign lords: groom {gl}, bride {bl}",
          f"चन्द्र राशि स्वामी: दुलहा {PLANET_NE[gl]}, दुलही {PLANET_NE[bl]}")

    # Vasya: bride's sign controlled by groom's sign = full.
    if bs in VASYA[gs]:
        vasya_score = 2.0
        vasya_note = f"{SIGNS_EN[bs]} is vasya to {SIGNS_EN[gs]}"
        vasya_note_ne = f"{SIGNS_NE[bs]} {SIGNS_NE[gs]} को वश्यमा छ"
    elif gs in VASYA[bs]:
        vasya_score = 1.0
        vasya_note = f"only the reverse direction holds ({SIGNS_EN[gs]} vasya to {SIGNS_EN[bs]})"
        vasya_note_ne = f"केवल उल्टो दिशा मिल्छ ({SIGNS_NE[gs]} {SIGNS_NE[bs]} को वश्यमा छ)"
    else:
        vasya_score = 0.0
        vasya_note = "no Vasya in either direction"
        vasya_note_ne = "कुनै दिशामा वश्य छैन"
    _part("Vasya", "वश्य", 2, vasya_score, vasya_note, vasya_note_ne)

    # Rajju.
    gr, br = RAJJU_OF_NAK[gn], RAJJU_OF_NAK[bn]
    rajju_dosha = gr == br
    _part("Rajju", "रज्जु", 5, 0.0 if rajju_dosha else 5.0,
          (f"Both in {gr} Rajju — Rajju Dosha, affecting {RAJJU_EFFECT_EN[gr]}"
           if rajju_dosha else f"Groom {gr}, bride {br} — different Rajjus"),
          (f"दुवै {RAJJU_NE[gr]} रज्जुमा — रज्जु दोष, {RAJJU_EFFECT_NE[gr]} मा असर"
           if rajju_dosha else f"दुलहा {RAJJU_NE[gr]}, दुलही {RAJJU_NE[br]} — फरक रज्जु"))

    # Vedha.
    vedha = frozenset((gn, bn)) in VEDHA_PAIRS
    _part("Vedha", "वेध", 2, 0.0 if vedha else 2.0,
          (f"{NAKSHATRAS_EN[gn]}–{NAKSHATRAS_EN[bn]} is a Vedha pair"
           if vedha else "No Vedha between the birth stars"),
          (f"{NAKSHATRAS_NE[gn]}–{NAKSHATRAS_NE[bn]} वेध जोडी हो"
           if vedha else "जन्म नक्षत्रबीच वेध छैन"))

    total = sum(p["score"] for p in parts)
    if rajju_dosha:
        verdict_en = "Rajju Dosha — classical authorities treat this as a deal-breaker despite the total"
        verdict_ne = "रज्जु दोष — कुल अङ्क जेसुकै भए पनि शास्त्रीय अधिकारीहरूले यसलाई निर्णायक बाधा मान्छन्"
    elif total >= 28:
        verdict_en, verdict_ne = "Excellent match", "उत्कृष्ट मेल"
    elif total >= 18:
        verdict_en, verdict_ne = "Acceptable match (traditional threshold 18)", "स्वीकार्य मेल (परम्परागत सीमा १८)"
    else:
        verdict_en, verdict_ne = "Below the traditional threshold of 18", "परम्परागत १८ अङ्कको सीमाभन्दा तल"
    return {
        "total": total, "max": 36, "breakdown": parts,
        "verdict_en": verdict_en, "verdict_ne": verdict_ne,
        "rajju_dosha": rajju_dosha,
        "vedha_present": vedha,
        "groom": {
            "moon_sign_en": SIGNS_EN[gs], "moon_sign_ne": SIGNS_NE[gs],
            "nakshatra_en": NAKSHATRAS_EN[gn], "nakshatra_ne": NAKSHATRAS_NE[gn],
            "gana": gg, "rajju": gr, "yoni": gy,
        },
        "bride": {
            "moon_sign_en": SIGNS_EN[bs], "moon_sign_ne": SIGNS_NE[bs],
            "nakshatra_en": NAKSHATRAS_EN[bn], "nakshatra_ne": NAKSHATRAS_NE[bn],
            "gana": bg, "rajju": br, "yoni": by,
        },
        "method_note": _bi(
            "36-point South Indian weighting; direction conventions and the stricter Rasi variant are documented in the module notes.",
            "३६-अङ्कीय दक्षिण भारतीय भार; दिशा-परम्परा र कडा राशि-विकल्प मोड्युल टिप्पणीमा दस्तावेज छन्।"),
    }
