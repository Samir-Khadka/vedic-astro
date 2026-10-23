"""Lal Kitab layer — the chart read the Lal Kitab way:

* Fixed khanas: khana 1 is Aries for everyone (the Kaal Purush frame);
  a planet's Lal Kitab house is simply its sign number.
* Pakka ghar (permanent houses): Sun 1; Moon 4; Mars 3, 8; Mercury 6, 7;
  Jupiter 2, 5, 9, 12; Venus 7; Saturn 8, 10, 11; Rahu 12; Ketu 6
  (published table, e.g. Paramarsh's Lal Kitab guide).
* Soya / jagta (sleeping / awake): a planet is awake if it sits in one of
  its pakka ghars, or if its 7th-khana drishti falls on another planet;
  a planet that aspects no planet and is not in its pakka ghar is soya
  (sleeping) — its results stay confined to its own khana.
* Sleeping houses: the published house-by-house conditions (a khana
  sleeps when it is empty and its linked khanas are also empty).
* Rin (debts): the formation rules with unambiguous published sources
  are implemented for Pitri, Swa and Matri Rin; all nine classical Rin
  are returned with their traditional collective remedies (Times of
  India / Lal Kitab remedy literature), the remaining six marked as
  reference-only because their formation rules are stated inconsistently
  across published sources.
* A short bilingual indication for every planet in its khana, written in
  the Lal Kitab manner (planet nature x khana theme + a classical note
  for the famous placements).
"""
from __future__ import annotations

from .names import HOUSE_THEMES_EN, HOUSE_THEMES_NE, PLANET_NE, SIGNS_EN, SIGNS_NE

PAKKA_GHAR = {
    "Sun": [1], "Moon": [4], "Mars": [3, 8], "Mercury": [6, 7],
    "Jupiter": [2, 5, 9, 12], "Venus": [7], "Saturn": [8, 10, 11],
    "Rahu": [12], "Ketu": [6],
}

# Sleeping-house conditions: khana -> (must be empty, extra checks as
# (other khana must be empty) / (planet must not be in khana)).
_SLEEP_RULES = {
    1: ("self",), 2: ("self", "empty:8", "notin:Saturn:6"),
    3: ("self", "notin:Mercury:9"), 4: ("self",), 5: ("self",),
    6: ("self", "empty:2", "notin:Mercury:12"), 7: ("self", "empty:1"),
    8: ("self",), 9: ("self", "empty:3", "empty:5"),
    10: ("self", "empty:4"), 11: ("self", "empty:3"),
    12: ("self", "empty:6", "empty:8"),
}

_RIN_ALL = [
    ("Pitri Rin", "पितृ ऋण", "Jupiter / the ancestors",
     "Collect an equal amount from all blood relatives and donate it to a temple on the same day; care for any temple or Peepal tree near the ancestral home.",
     "सबै रगतका नातेदारबाट बराबर रकम सङ्कलन गरी त्यही दिन मन्दिरमा दान गर्नुहोस्; पैत्रिक घर नजिकको मन्दिर वा पीपलको रूखको हेरचाह गर्नुहोस्।"),
    ("Swa Rin", "स्व ऋण", "Sun / the self",
     "Collect equal contributions from blood relatives and perform a Homa (Yagya).",
     "रगतका नातेदारबाट बराबर योगदान सङ्कलन गरी होम (यज्ञ) गर्नुहोस्।"),
    ("Matri Rin", "मातृ ऋण", "Moon / the mother",
     "Collect an equal weight of silver from each family member and immerse it in flowing river water.",
     "प्रत्येक परिवारका सदस्यबाट बराबर तौलको चाँदी सङ्कलन गरी बग्ने नदीको पानीमा बगाउनुहोस्।"),
    ("Bhratri Rin", "भ्रातृ ऋण", "Mars / brothers",
     "Collect equal contributions from relatives and donate medicines or funds to a charitable hospital.",
     "नातेदारबाट बराबर योगदान सङ्कलन गरी परोपकारी अस्पतालमा औषधि वा रकम दान गर्नुहोस्।"),
    ("Stree Rin", "स्त्री ऋण", "Venus / women",
     "Feed 100 cows with green fodder on a single day, funded by equal family contributions.",
     "परिवारको बराबर योगदानबाट एकै दिन १०० वटा गाईलाई हरियो घाँस खुवाउनुहोस्।"),
    ("Kanya Rin", "कन्या ऋण", "Mercury / daughters & sisters",
     "Burn yellow cowries to ash and immerse the ash in flowing water the same day.",
     "पहेंला कौडा जलाएर खरानी बनाई त्यही दिन बग्ने पानीमा बगाउनुहोस्।"),
    ("Zulm Rin", "जुल्म ऋण", "Saturn / cruelty to the helpless",
     "Feed 100 labourers, or feed fish in a pond, on a single day with family contributions.",
     "परिवारको योगदानबाट एकै दिन १०० जना मजदुरलाई खाना खुवाउनुहोस्, वा पोखरीमा माछालाई खुवाउनुहोस्।"),
    ("Ajanma Rin", "अजन्म ऋण", "Rahu / the unborn",
     "Collect one coconut from each family member and immerse them in flowing water the same day.",
     "प्रत्येक परिवारका सदस्यबाट एक-एक नरिवल सङ्कलन गरी त्यही दिन बग्ने पानीमा बगाउनुहोस्।"),
    ("Kudrati Rin", "कुदरती ऋण", "Ketu / nature & animals",
     "Feed 100 dogs with sweet rice (kheer) on a single day, funded by family contributions.",
     "परिवारको योगदानबाट एकै दिन १०० वटा कुकुरलाई खिर खुवाउनुहोस्।"),
]


def _rin_detected(name: str, khana_of: dict[str, int]) -> bool | None:
    """Formation rules with clear published sources; None = reference only."""
    if name == "Pitri Rin":
        return any(khana_of[p] in (2, 5, 9, 12) for p in ("Rahu", "Venus", "Mercury"))
    if name == "Swa Rin":
        return any(khana_of[p] == 5 for p in ("Venus", "Rahu", "Ketu", "Saturn"))
    if name == "Matri Rin":
        return khana_of["Ketu"] == 4
    return None


# Famous placements with a specific classical flavour (planet, khana).
_CLASSICAL_NOTES = {
    ("Saturn", 10): ("Saturn in the 10th khana is a Lal Kitab strength — slow but unstoppable rise in career.",
                     "दशौँ खानामा शनि लाल किताबको बल हो — पेशामा ढिलो तर अडिग उन्नति।"),
    ("Saturn", 2): ("Saturn in the 2nd khana is read carefully for wealth and family speech.",
                    "दोस्रो खानाको शनिलाई धन र पारिवारिक वाणीका लागि होसियारीपूर्वक हेरिन्छ।"),
    ("Moon", 6): ("Moon in the 6th khana is a classic Lal Kitab caution — keep silver and avoid lending milk/water at night in the traditional telling.",
                  "छैटौँ खानाको चन्द्रमा लाल किताबको शास्त्रीय सावधानी हो — परम्परागत भनाइमा चाँदी राख्नुहोस् र राती दूध/पानी सापटी नदिनुहोस्।"),
    ("Sun", 1): ("Sun in its own pakka ghar (1st khana) — authority and self-reliance are emphasised.",
                 "सूर्य आफ्नै पक्का घरमा (पहिलो खाना) — अधिकार र आत्मनिर्भरता जोड दिइन्छ।"),
    ("Jupiter", 9): ("Jupiter in the 9th khana (a pakka ghar) — the chart is called protected; elders' blessings carry weight.",
                     "नवौँ खानामा बृहस्पति (पक्का घर) — कुण्डली सुरक्षित मानिन्छ; ठूलाबडाको आशीर्वादले वजन राख्छ।"),
    ("Rahu", 3): ("Rahu in the 3rd khana is considered bold and resourceful in Lal Kitab.",
                  "तेस्रो खानाको राहुलाई लाल किताबमा साहसी र युक्तिवान् मानिन्छ।"),
    ("Ketu", 12): ("Ketu in the 12th khana is read as spiritually inclined expenditure.",
                   "बाह्रौँ खानाको केतुलाई आध्यात्मिक झुकावयुक्त खर्चका रूपमा हेरिन्छ।"),
}

_PLANET_NATURE = {
    "Sun": ("authority, father and self-respect", "अधिकार, पिता र आत्मसम्मान"),
    "Moon": ("mind, mother and emotional flow", "मन, आमा र भावनात्मक प्रवाह"),
    "Mars": ("energy, courage and siblings", "ऊर्जा, साहस र दाजुभाइ-दिदीबहिनी"),
    "Mercury": ("speech, trade and calculation", "वाणी, व्यापार र हिसाब"),
    "Jupiter": ("wisdom, elders and dharma", "ज्ञान, ठूलाबडा र धर्म"),
    "Venus": ("comfort, marriage and luxury", "सुख, विवाह र विलासिता"),
    "Saturn": ("labour, patience and karmic dues", "श्रम, धैर्य र कर्मको हिसाब"),
    "Rahu": ("ambition, the foreign and sudden rise", "महत्त्वाकाङ्क्षा, विदेश र आकस्मिक उन्नति"),
    "Ketu": ("detachment, intuition and the past", "वैराग्य, अन्तर्ज्ञान र अतीत"),
}


def lal_kitab(planets: dict) -> dict:
    """planets: the ephemeris planet dict (sign per planet)."""
    khana_of = {name: p["sign"] + 1 for name, p in planets.items()}
    occupants: dict[int, list[str]] = {k: [] for k in range(1, 13)}
    for name, k in khana_of.items():
        occupants[k].append(name)

    planet_rows = []
    for name in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"):
        k = khana_of[name]
        in_pakka = k in PAKKA_GHAR[name]
        seventh = occupants[(k + 5) % 12 + 1]  # khana 7th from k
        jagta = in_pakka or len([q for q in seventh if q != name]) > 0
        nature_en, nature_ne = _PLANET_NATURE[name]
        note = _CLASSICAL_NOTES.get((name, k))
        reading_en = (f"In the Lal Kitab frame, {name} in khana {k} ({SIGNS_EN[k-1]}) brings its themes of "
                      f"{nature_en} into the matters of the {k}th khana ({HOUSE_THEMES_EN[k]}).")
        reading_ne = (f"लाल किताबको ढाँचामा, {PLANET_NE[name]} खाना {k} ({SIGNS_NE[k-1]}) मा हुँदा यसका विषय — "
                      f"{nature_ne} — {k}औँ खानाका मामिलामा ({HOUSE_THEMES_NE[k]}) ल्याउँछ।")
        if note:
            reading_en += " " + note[0]
            reading_ne += " " + note[1]
        if not jagta:
            reading_en += " The planet is soya (sleeping): its results stay confined to this khana until awakened."
            reading_ne += " यो ग्रह सोया (सुतेको) छ: यसको जागरण नभएसम्म फल यही खानामा सीमित रहन्छ।"
        planet_rows.append({
            "planet": name, "khana": k,
            "sign_en": SIGNS_EN[k - 1], "sign_ne": SIGNS_NE[k - 1],
            "pakka_ghar": PAKKA_GHAR[name], "in_pakka_ghar": in_pakka,
            "state": "jagta" if jagta else "soya",
            "reading": {"en": reading_en, "ne": reading_ne},
        })

    sleeping_houses = []
    for k, rules in _SLEEP_RULES.items():
        if occupants[k]:
            continue
        asleep = True
        for rule in rules[1:]:
            if rule.startswith("empty:"):
                if occupants[int(rule.split(":")[1])]:
                    asleep = False
            elif rule.startswith("notin:"):
                _tag, pl, kh = rule.split(":")
                if khana_of[pl] == int(kh):
                    asleep = False
        if asleep:
            sleeping_houses.append(k)

    rin = []
    for name_en, name_ne, planet_label, rem_en, rem_ne in _RIN_ALL:
        detected = _rin_detected(name_en, khana_of)
        rin.append({
            "name": {"en": name_en, "ne": name_ne},
            "associated": planet_label,
            "detected": detected,  # True/False, or None = shown for reference
            "remedy": {"en": rem_en, "ne": rem_ne},
        })

    return {
        "chart": {str(k): v for k, v in occupants.items()},
        "planets": planet_rows,
        "sleeping_houses": sleeping_houses,
        "rin": rin,
    }
