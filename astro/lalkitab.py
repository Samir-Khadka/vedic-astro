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
* Rin (debts): formation rules are implemented for eight of the nine
  classical Rin from the best-attested published rules (multiple
  sources agreeing): Pitri, Swa, Matri, Stree, Bhratri, Kanya, Zulm
  and Ajanma. Kudrati Rin has no formation rule in the sources
  found and stays reference-only, flagged as such — a guess is never
  presented as certain. A tenth variant, Daiviya Rin (Moon or Mars
  in the 6th khana), appears in some lists and is noted in the docs
  but not added to the canonical nine.
* Teva types: Andha (10th khana vacant, or mutual-enemy planets
  together in it), Adha Andha / Rataundhi (Sun in 4th + Saturn in
  7th), Dharmi (Jupiter + Saturn together in any khana, or Saturn
  in 11th, or Rahu/Ketu in 4th, or Rahu/Ketu conjunct the Moon —
  one published reading; a stricter reading requires the Saturn
  condition AND the Rahu/Ketu condition together, and the variance
  is documented), Nabaligh (kendra khanas vacant or holding only
  Mercury, Saturn, Rahu or Ketu — the child's chart, dormant
  until age 12).
* Lal Kitab dasha: the 35-year cycle from the published Lal Kitab
  dasha literature (Arun Sanhita 1952 ed., p. 10, as cited in the
  Lal Kitab grammar notes): Jupiter 6, Sun 2, Moon 1, Venus 3,
  Mars 6, Mercury 2, Saturn 6, Rahu 6, Ketu 3 = 35 years, repeating.
  Each Mahadasha holds three equal Antardashas; the Antar order
  (previous, self, next in the cycle) is generalised from the
  single published example (Jupiter MD: Ketu, Jupiter, Sun) and
  flagged low-confidence. The cycle's START point is disputed in
  the literature (the book itself gives none; scholars propose
  conflicting rules) — this implementation anchors the first cycle
  at birth with Jupiter, the first planet of the published
  sequence, and marks all LK dasha dates indicative.
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
    ("Bhratri Rin", "भ्रातृ ऋण", "Mercury/Venus / brothers & relatives",
     "Collect equal contributions from relatives and donate medicines or funds to a charitable hospital.",
     "नातेदारबाट बराबर योगदान सङ्कलन गरी परोपकारी अस्पतालमा औषधि वा रकम दान गर्नुहोस्।"),
    ("Stree Rin", "स्त्री ऋण", "Venus / women",
     "Feed 100 cows with green fodder on a single day, funded by equal family contributions.",
     "परिवारको बराबर योगदानबाट एकै दिन १०० वटा गाईलाई हरियो घाँस खुवाउनुहोस्।"),
    ("Kanya Rin", "कन्या ऋण", "Mercury / daughters & sisters",
     "Burn yellow cowries to ash and immerse the ash in flowing water the same day.",
     "पहेंला कौडा जलाएर खरानी बनाई त्यही दिन बग्ने पानीमा बगाउनुहोस्।"),
    ("Zulm Rin", "जुल्म ऋण", "Sun/Moon/Mars / cruelty to the helpless",
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
    """Formation rules with clear published sources; None = reference only.

    Stree / Bhratri / Kanya / Zulm / Ajanma rules are the
    best-attested published forms (two independent remedy sources
    agreeing); where sources disagree on the associated planet
    (Zulm's remedy is sometimes tied to Saturn), the formation
    rule — not the remedy association — is what is implemented.
    """
    if name == "Pitri Rin":
        return any(khana_of[p] in (2, 5, 9, 12) for p in ("Rahu", "Venus", "Mercury"))
    if name == "Swa Rin":
        return any(khana_of[p] == 5 for p in ("Venus", "Rahu", "Ketu", "Saturn"))
    if name == "Matri Rin":
        return khana_of["Ketu"] == 4
    if name == "Stree Rin":
        return any(khana_of[p] in (2, 7) for p in ("Sun", "Moon", "Rahu"))
    if name == "Bhratri Rin":
        return any(khana_of[p] in (1, 8) for p in ("Mercury", "Venus"))
    if name == "Kanya Rin":
        return khana_of["Mercury"] in (3, 6)
    if name == "Zulm Rin":
        return any(khana_of[p] in (10, 12) for p in ("Sun", "Moon", "Mars"))
    if name == "Ajanma Rin":
        return any(khana_of[p] == 12 for p in ("Sun", "Venus", "Mars"))
    return None  # Kudrati Rin: no formation rule verified in sources found


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
            "confidence": "attested" if detected is not None else "reference",
            "remedy": {"en": rem_en, "ne": rem_ne},
        })

    return {
        "chart": {str(k): v for k, v in occupants.items()},
        "planets": planet_rows,
        "sleeping_houses": sleeping_houses,
        "rin": rin,
        "teva": teva_types(khana_of),
    }


# ---------------------------------------------------------------------------
# Teva (chart) types
# ---------------------------------------------------------------------------
# Mutual-enemy pairs among the visible planets (both directions enemy
# in the classical natural-relationship table; the Moon has no
# enemies, so Moon pairs never count here).
_MUTUAL_ENEMIES = {
    frozenset(p) for p in [("Sun", "Saturn"), ("Sun", "Venus")]
}
_KENDRA_KHANAS = (1, 4, 7, 10)

_TEVA_REMEDIES = {
    "Andha": ("Feed 10 blind persons.",
              "१० जना दृष्टिविहीन व्यक्तिलाई खाना खुवाउनुहोस्।"),
    "Adha Andha": ("Let milk or river water flow in brass vessels; avoid alcohol and late-night ventures.",
                   "पीतलको भाँडामा दूध वा नदीको पानी बगाउनुहोस्; मदिरा र राति अबेरका कामबाट जोगिनुहोस्।"),
    "Dharmi": ("No remedy is prescribed for a Dharmi Teva — the chart is considered protected by dharma.",
               "धार्मिक टेवाका लागि कुनै उपाय तोकिएको छैन — कुण्डली धर्मद्वारा सुरक्षित मानिन्छ।"),
    "Nabaligh": ("The chart is dormant until age 12; the khanas are said to activate year by year after that.",
                 "कुण्डली १२ वर्षको उमेरसम्म निष्क्रिय रहन्छ; त्यसपछि खानाहरू वर्षैपिच्छे सक्रिय हुन्छन् भनिन्छ।"),
}


def teva_types(khana_of: dict[str, int]) -> dict:
    """Which Teva types this chart matches, with the formation met."""
    occupants: dict[int, list[str]] = {k: [] for k in range(1, 13)}
    for name, k in khana_of.items():
        occupants[k].append(name)
    matched = []

    # Andha: 10th khana vacant, or mutual enemies together in it,
    # or a node together with Sun/Moon in it.
    tenth = occupants[10]
    andha_reason = None
    if not tenth:
        andha_reason = "the 10th khana is entirely vacant"
    else:
        for i in range(len(tenth)):
            for j in range(i + 1, len(tenth)):
                pair = frozenset((tenth[i], tenth[j]))
                if pair in _MUTUAL_ENEMIES or (
                        ("Rahu" in pair or "Ketu" in pair)
                        and ("Sun" in pair or "Moon" in pair)):
                    andha_reason = f"{tenth[i]} and {tenth[j]} sit together in the 10th khana"
                    break
            if andha_reason:
                break
    if andha_reason:
        matched.append({"type": "Andha", "type_ne": "अन्धा टेवा",
                        "formation": andha_reason,
                        "reading": {"en": "Blind Teva — career instability is the classical reading.",
                                    "ne": "अन्धा टेवा — पेशामा अस्थिरता शास्त्रीय पठन हो।"}})
    # Adha Andha (half-blind / Rataundhi): Sun in 4th + Saturn in 7th.
    if khana_of["Sun"] == 4 and khana_of["Saturn"] == 7:
        matched.append({"type": "Adha Andha", "type_ne": "अर्ध-अन्धा टेवा",
                        "formation": "Sun in the 4th khana and Saturn in the 7th khana",
                        "reading": {"en": "Half-blind Teva — mental and domestic unrest in the classical reading.",
                                    "ne": "अर्ध-अन्धा टेवा — मानसिक र घरेलु अशान्ति शास्त्रीय पठन हो।"}})
    # Dharmi: Jupiter+Saturn together anywhere, or Saturn in 11th, or
    # Rahu/Ketu in 4th, or Rahu/Ketu conjunct the Moon (OR-reading).
    dharmi_reason = None
    for k, occ in occupants.items():
        if "Jupiter" in occ and "Saturn" in occ:
            dharmi_reason = f"Jupiter and Saturn together in khana {k}"
            break
    if dharmi_reason is None and khana_of["Saturn"] == 11:
        dharmi_reason = "Saturn in the 11th khana"
    if dharmi_reason is None and khana_of["Rahu"] == 4:
        dharmi_reason = "Rahu in the 4th khana"
    if dharmi_reason is None and khana_of["Ketu"] == 4:
        dharmi_reason = "Ketu in the 4th khana"
    if dharmi_reason is None and khana_of["Rahu"] == khana_of["Moon"]:
        dharmi_reason = "Rahu conjunct the Moon"
    if dharmi_reason is None and khana_of["Ketu"] == khana_of["Moon"]:
        dharmi_reason = "Ketu conjunct the Moon"
    if dharmi_reason:
        matched.append({"type": "Dharmi", "type_ne": "धार्मिक टेवा",
                        "formation": dharmi_reason,
                        "reading": {"en": "Dharmi Teva — the chart is considered protected; its native is traditionally said to prosper by righteous conduct.",
                                    "ne": "धार्मिक टेवा — कुण्डली सुरक्षित मानिन्छ; जातकले धर्मपूर्ण आचरणले उन्नति गर्ने परम्परागत भनाइ छ।"}})
    # Nabaligh: kendras vacant or holding only Mercury, Saturn, Rahu, Ketu.
    dormant_ok = True
    for k in _KENDRA_KHANAS:
        if any(p not in ("Mercury", "Saturn", "Rahu", "Ketu") for p in occupants[k]):
            dormant_ok = False
            break
    if dormant_ok:
        matched.append({"type": "Nabaligh", "type_ne": "नाबालिग टेवा",
                        "formation": "kendra khanas (1, 4, 7, 10) are vacant or hold only Mercury, Saturn, Rahu or Ketu",
                        "reading": {"en": "Minor's Teva — the child's destiny is dormant until age 12.",
                                    "ne": "नाबालिग टेवा — बच्चाको भाग्य १२ वर्षको उमेरसम्म निष्क्रिय रहन्छ।"}})
    for m in matched:
        rem_en, rem_ne = _TEVA_REMEDIES[m["type"]]
        m["remedy"] = {"en": rem_en, "ne": rem_ne}
    return {
        "matched": matched,
        "variance_note": {
            "en": ("Dharmi Teva sources vary: one reading lists the Saturn and Rahu/Ketu "
                   "conditions as alternatives (used here); a stricter verse reading "
                   "requires both a Saturn condition AND a Rahu/Ketu condition together."),
            "ne": ("धार्मिक टेवाका स्रोतहरू फरक छन्: एउटा पठनले शनि र राहु/केतु शर्तहरूलाई विकल्पका रूपमा लिन्छ (यहाँ प्रयोग गरिएको); "
                   "कडा श्लोक-पठनले शनि शर्त र राहु/केतु शर्त दुवै सँगै चाहिन्छ।"),
        },
    }


# ---------------------------------------------------------------------------
# Lal Kitab 35-year dasha cycle (see module notes on the start rule).
# ---------------------------------------------------------------------------
LK_DASHA_SEQUENCE = [
    ("Jupiter", 6), ("Sun", 2), ("Moon", 1), ("Venus", 3), ("Mars", 6),
    ("Mercury", 2), ("Saturn", 6), ("Rahu", 6), ("Ketu", 3),
]
LK_DASHA_CYCLE_YEARS = 35


def lal_kitab_dasha(birth_dt, now=None, cycles: int = 3) -> dict:
    """The repeating 35-year Lal Kitab dasha, anchored at birth with
    Jupiter (the first planet of the published sequence). Each MD
    holds three equal Antardashas in (previous, self, next) cycle
    order — generalised from the single published Jupiter example,
    so the Antar order is low-confidence and the whole cycle's
    dates are indicative while the start rule is disputed."""
    from datetime import datetime, timedelta

    YEAR_DAYS = 365.25
    at = now or datetime.now(birth_dt.tzinfo)
    periods = []
    cursor = birth_dt
    n = len(LK_DASHA_SEQUENCE)
    for k in range(cycles * n):
        planet, years = LK_DASHA_SEQUENCE[k % n]
        end = cursor + timedelta(days=years * YEAR_DAYS)
        antars = []
        prev_p = LK_DASHA_SEQUENCE[(k - 1) % n][0]
        next_p = LK_DASHA_SEQUENCE[(k + 1) % n][0]
        sub = cursor
        for ap in (prev_p, planet, next_p):
            sub_end = sub + timedelta(days=years * YEAR_DAYS / 3.0)
            antars.append({"planet": ap, "start": sub, "end": sub_end,
                           "years": round(years / 3.0, 3)})
            sub = sub_end
        periods.append({"planet": planet, "start": cursor, "end": end,
                        "years": float(years), "antardashas": antars})
        cursor = end
    current = next((p for p in periods if p["start"] <= at < p["end"]), None)
    current_antar = None
    if current is not None:
        current_antar = next(
            (a for a in current["antardashas"] if a["start"] <= at < a["end"]), None)

    def _ser(p):
        return {"planet": p["planet"], "start": p["start"].date().isoformat(),
                "end": p["end"].date().isoformat(), "years": p["years"]}

    return {
        "cycle_years": LK_DASHA_CYCLE_YEARS,
        "sequence": [{"planet": p, "years": y} for p, y in LK_DASHA_SEQUENCE],
        "periods": [{**_ser(p), "antardashas": [
            {"planet": a["planet"], "start": a["start"].date().isoformat(),
             "end": a["end"].date().isoformat(), "years": a["years"]}
            for a in p["antardashas"]]} for p in periods],
        "current": (
            {**_ser(current),
             "antardasha": ({"planet": current_antar["planet"],
                             "start": current_antar["start"].date().isoformat(),
                             "end": current_antar["end"].date().isoformat()}
                            if current_antar else None)}
            if current else None),
        "confidence": "low",
        "method_note": {
            "en": ("35-year cycle verified from the published Lal Kitab dasha literature; "
                   "the start rule is disputed (the book gives none), so this implementation "
                   "anchors the first cycle at birth with Jupiter and all dates are indicative. "
                   "Antar order (previous, self, next) is generalised from the single published "
                   "Jupiter example."),
            "ne": ("३५-वर्षीय चक्र प्रकाशित लाल किताब दशा साहित्यबाट प्रमाणित छ; "
                   "सुरुको नियम विवादित छ (पुस्तकले कुनै दिँदैन), त्यसैले यो कार्यान्वयनले पहिलो चक्र जन्ममा बृहस्पतिबाट सुरु गर्छ र सबै मितिहरू सूचक मात्र हुन्। "
                   "अन्तर क्रम (अघिल्लो, आफू, पछिल्लो) एकल प्रकाशित बृहस्पति उदाहरणबाट सामान्यीकरण गरिएको हो।"),
        },
    }
