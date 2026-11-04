"""Life Question answers — a real verdict WITH a chart.

The Life Questions library used to stop at guidance: prime / supporting /
negating houses, a significator, and what to check. Its buttons only
scrolled to the kundali or prashna form, so no question ever got an
answer. This module closes that gap.

Method (traditional KP horary, explained — never a black box):
for the question's prime / supporting / negating houses, look at which
houses are signified by a small set of checked lords and score them:

* prime house signified: +2
* supporting house signified: +1
* negating house signified: -2

Bands from the total score and the prime/negating counts:

* no prime and no negating signification at all -> "unclear"
  (the chart does not speak to this question)
* score >= 4 -> "favourable"
* score <= -2 -> "unfavourable"
* anything else -> "mixed"

Checked lords, birth chart: current Vimshottari Mahadasha and
Antardasha lords, the Moon's star lord and sub lord, the natural
significator planet, and the cuspal sub lord of each prime house.
Checked lords, prashna: the ruling planets at the question moment
(day lord, ascendant sign/star/sub lords, Moon sign/star/sub lords),
plus the cuspal sub lords of the prime houses. Houses signified by a
planet come from the engine's own KP tables (birth: planet_signified_houses;
prashna: inverted from house_significators' significator_order).

This is traditional probability guidance, never a certain verdict.
Every answer carries the library's probability framing, and sensitive
questions (child sex indication, pregnancy difficulty, relationship
strain, legal trouble, court outcomes, serious health periods) carry
their medical/legal disclaimers. If the chart data cannot support an
evaluation, the answer is "unclear" with a reason — never an invented
verdict.
"""

from __future__ import annotations

from .life_questions import DISCLAIMER_EN, DISCLAIMER_NE
from .names import PLANET_NE

# Questions whose answers must never read as deterministic medical,
# legal or personal claims (see life_questions.py docstring).
SENSITIVE_IDS = {
    "children_sex_indication",
    "children_pregnancy_difficulty",
    "marriage_relationship_strain",
    "litigation_legal_trouble",
    "litigation_court_outcome",
    "health_serious_periods",
}

SENSITIVE_EXTRA_EN = (
    " This is probability guidance only, not a diagnosis, a legal "
    "prediction, or a claim about any person. For health questions see a "
    "clinician; for legal questions see a lawyer."
)
SENSITIVE_EXTRA_NE = (
    " यो सम्भावना-आधारित मार्गदर्शन मात्र हो, निदान, कानुनी भविष्यवाणी "
    "वा कुनै व्यक्तिबारेको दाबी होइन। स्वास्थ्यका प्रश्नका लागि चिकित्सकसँग, "
    "कानुनी प्रश्नका लागि वकिलसँग परामर्श गर्नुहोस्।"
)

BAND_LABELS = {
    "favourable": ("Favourable indication", "अनुकूल सङ्केत"),
    "mixed": ("Mixed indication", "मिश्रित सङ्केत"),
    "unfavourable": ("Unfavourable indication", "प्रतिकूल सङ्केत"),
    "unclear": ("Unclear — chart does not speak to this question", "अस्पष्ट — कुण्डलीले यस प्रश्नमा बोल्दैन"),
}

EXPLAIN_EN = (
    "Checked lords were scored against the question's houses: a prime "
    "house signified counts +2, a supporting house +1, a negating house "
    "-2. The band follows the total: 4 or more is favourable, -2 or less "
    "is unfavourable, anything in between is mixed; with no prime and no "
    "negating signification the answer is unclear."
)
EXPLAIN_NE = (
    "जाँचिएका स्वामीहरूलाई प्रश्नका भावसँग दाँजियो: प्रमुख भावको सङ्केत "
    "+२, समर्थन गर्ने भावको +१, नकार्ने भावको -२। कुल अङ्क ४ वा बढी भए "
    "अनुकूल, -२ वा कम भए प्रतिकूल, बीचमा भए मिश्रित; प्रमुख र नकार्ने "
    "कुनै पनि सङ्केत नभए उत्तर अस्पष्ट हुन्छ।"
)



def _ordinal(h: int) -> str:
    if h in (1, 21, 31):
        suf = "st"
    elif h in (2, 22):
        suf = "nd"
    elif h in (3, 23):
        suf = "rd"
    else:
        suf = "th"
    return f"{h}{suf}"

def _class_of(house: int, q: dict) -> str:
    if house in (q.get("prime_houses") or []):
        return "prime"
    if house in (q.get("supporting_houses") or []):
        return "supporting"
    if house in (q.get("negating_houses") or []):
        return "negating"
    return "other"


def _score_evidence(q: dict, checks: list) -> dict:
    """checks: [{role_en, role_ne, planet, houses:[int]}].

    Returns the band, score, per-class hit counts and the evidence
    table (each checked lord, the houses it signifies, each house's
    class for this question).
    """
    evidence = []
    prime_hits = supporting_hits = negating_hits = 0
    score = 0
    for c in checks:
        houses = []
        for h in sorted(set(c.get("houses") or [])):
            cls = _class_of(h, q)
            houses.append({"house": h, "class": cls})
            if cls == "prime":
                prime_hits += 1
                score += 2
            elif cls == "supporting":
                supporting_hits += 1
                score += 1
            elif cls == "negating":
                negating_hits += 1
                score -= 2
        evidence.append({
            "role_en": c["role_en"], "role_ne": c.get("role_ne") or c["role_en"],
            "planet": c["planet"], "planet_ne": PLANET_NE.get(c["planet"], c["planet"]),
            "houses": houses,
        })
    if not evidence:
        band, reason = "unclear", "no_checked_lords"
    elif prime_hits == 0 and negating_hits == 0:
        band, reason = "unclear", "no_prime_or_negating_signification"
    elif score >= 4:
        band, reason = "favourable", None
    elif score <= -2:
        band, reason = "unfavourable", None
    else:
        band, reason = "mixed", None
    return {
        "band": band, "score": score,
        "prime_hits": prime_hits, "supporting_hits": supporting_hits,
        "negating_hits": negating_hits, "evidence": evidence,
        "reason": reason,
    }


def _finalise(q: dict, source: str, scored: dict) -> dict:
    band = scored["band"]
    label_en, label_ne = BAND_LABELS[band]
    disclaimer_en = DISCLAIMER_EN
    disclaimer_ne = DISCLAIMER_NE
    if q["id"] in SENSITIVE_IDS:
        disclaimer_en += SENSITIVE_EXTRA_EN
        disclaimer_ne += SENSITIVE_EXTRA_NE
    out = {
        "question_id": q["id"],
        "question_en": q["question_en"], "question_ne": q["question_ne"],
        "source": source,
        "band": band, "band_en": label_en, "band_ne": label_ne,
        "score": scored["score"],
        "prime_hits": scored["prime_hits"],
        "supporting_hits": scored["supporting_hits"],
        "negating_hits": scored["negating_hits"],
        "evidence": scored["evidence"],
        "explanation_en": EXPLAIN_EN, "explanation_ne": EXPLAIN_NE,
        "disclaimer_en": disclaimer_en, "disclaimer_ne": disclaimer_ne,
    }
    if scored.get("reason"):
        out["reason"] = scored["reason"]
    return out


def answer_from_birth(q: dict, bundle: dict) -> dict:
    """Answer a question from a compute_kundali bundle."""
    kp = (bundle or {}).get("kp") or {}
    signified = kp.get("planet_signified_houses") or {}
    kp_planets = kp.get("planets") or {}
    house_sig = kp.get("house_significators") or {}
    if not signified or not kp_planets:
        return _finalise(q, "birth", _score_evidence(q, []))
    checks = []
    current = ((bundle.get("dasha") or {}).get("current") or {})
    md = (current.get("mahadasha") or {}).get("lord")
    ad = (current.get("antardasha") or {}).get("lord")
    if md:
        checks.append({"role_en": "Current Mahadasha lord",
                       "role_ne": "हालको महादशा स्वामी",
                       "planet": md, "houses": signified.get(md, [])})
    if ad:
        checks.append({"role_en": "Current Antardasha lord",
                       "role_ne": "हालको अन्तर्दशा स्वामी",
                       "planet": ad, "houses": signified.get(ad, [])})
    moon = kp_planets.get("Moon") or {}
    for key, role_en, role_ne in (
        ("star_lord", "Moon star lord", "चन्द्र नक्षत्र स्वामी"),
        ("sub_lord", "Moon sub lord", "चन्द्र उपस्वामी"),
    ):
        planet = moon.get(key)
        if planet:
            checks.append({"role_en": role_en, "role_ne": role_ne,
                           "planet": planet, "houses": signified.get(planet, [])})
    sig = q.get("significator_en")
    if sig in signified:
        checks.append({"role_en": "Natural significator",
                       "role_ne": "प्राकृतिक कारक",
                       "planet": sig, "houses": signified.get(sig, [])})
    for h in q.get("prime_houses") or []:
        csl = ((house_sig.get(h) or house_sig.get(str(h))) or {}).get("cuspal_sub_lord")
        if csl:
            checks.append({"role_en": f"{_ordinal(h)} house cuspal sub lord",
                           "role_ne": f"{h}औँ भावको सन्धि उपस्वामी",
                           "planet": csl, "houses": signified.get(csl, [])})
    return _finalise(q, "birth", _score_evidence(q, checks))


def answer_from_prashna(q: dict, horary: dict) -> dict:
    """Answer a question from a prashna.horary() result."""
    house_sig = (horary or {}).get("house_significators") or {}
    if not house_sig:
        return _finalise(q, "prashna", _score_evidence(q, []))
    # Invert house significators: planet -> houses it signifies
    # (via the KP significator order of each house).
    signified: dict = {}
    for house, sig in house_sig.items():
        house = int(house)
        for planet in sig.get("significator_order") or []:
            signified.setdefault(planet, []).append(int(house))
    checks = []
    for rp in horary.get("ruling_planets") or []:
        planet = rp.get("planet")
        if planet:
            checks.append({"role_en": rp.get("role") or "Ruling planet",
                           "role_ne": rp.get("role_ne") or rp.get("role") or "रूलिङ ग्रह",
                           "planet": planet, "houses": signified.get(planet, [])})
    for h in q.get("prime_houses") or []:
        csl = ((house_sig.get(h) or house_sig.get(str(h))) or {}).get("cuspal_sub_lord")
        if csl:
            checks.append({"role_en": f"{_ordinal(h)} house cuspal sub lord",
                           "role_ne": f"{h}औँ भावको सन्धि उपस्वामी",
                           "planet": csl, "houses": signified.get(csl, [])})
    return _finalise(q, "prashna", _score_evidence(q, checks))
