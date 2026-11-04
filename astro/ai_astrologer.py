"""AI Astrologer — plain-language answers from a real chart.

No external service and no LLM is ever called: a question is
classified by keyword scoring into one of the 8 life areas (see
astro/life_areas.py), and the answer is assembled from that chart's
actual placements, KP significations and running dasha. Everything is
probability guidance, never a certainty, and never an exact date.

Scoring for the birth-chart verdict (documented exactly, as required):

* prime houses = the area's own houses (life_areas.AREAS).
* supporting houses = houses that are 2nd, 5th, 9th or 11th counted
  from the area's PRIMARY house (the first house in its list),
  excluding any prime house.
* negating houses = the 12th house from EACH prime house
  (i.e. prime - 1, wrapped to 1..12).

Checked lords are scored with astro.life_answers._score_evidence
(prime +2, supporting +1, negating -2; band favourable >= 4,
unfavourable <= -2, else mixed, none = unclear) — the same helper the
Life Question answers use, but with AREA houses, never with any
question-specific prime list from life_answers. For prashna charts the
checked lords are the ruling planets plus the cuspal sub lords of the
prime houses, with houses signified inverted from the horary's
house_significators (the same inversion life_answers uses).

Out of scope, detected FIRST (before classification):

* death / mortality questions — astrology must not predict death;
* lottery / gambling exact-win questions;
* exact-date demands ("exact date of marriage" and equivalents) —
  a legitimate timing question ("when will I marry?") is NOT refused:
  it gets a dasha-based period, never a date.

For out-of-scope questions build_answer() returns a refusal object
with a plain explanation of what astrology can and cannot say, plus
the closest legitimate area when the question contains one. For a
question that matches no area at all it returns a graceful fallback
listing the 8 areas, and fabricates no answer.
"""

from __future__ import annotations

import re
import unicodedata

from .life_areas import AREAS, AREA_ORDER, PLANETS, NATURE, analyse, aspected_houses, house_lords
from .names import PLANET_NE, SIGNS_EN, SIGNS_NE

try:
    from .life_answers import _score_evidence
except Exception:  # pragma: no cover - mirror if the import ever fails
    def _score_evidence(q: dict, checks: list) -> dict:
        def _class_of(h: int) -> str:
            if h in (q.get("prime_houses") or []):
                return "prime"
            if h in (q.get("supporting_houses") or []):
                return "supporting"
            if h in (q.get("negating_houses") or []):
                return "negating"
            return "other"

        evidence, prime_hits = [], 0
        supporting_hits = negating_hits = score = 0
        for c in checks:
            houses = []
            for h in sorted(set(c.get("houses") or [])):
                cls = _class_of(h)
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
            evidence.append({"role_en": c["role_en"],
                             "role_ne": c.get("role_ne") or c["role_en"],
                             "planet": c["planet"], "planet_ne": PLANET_NE.get(c["planet"], c["planet"]),
                             "houses": houses})
        if not evidence or (prime_hits == 0 and negating_hits == 0):
            band, reason = "unclear", "no_prime_or_negating_signification"
        elif score >= 4:
            band, reason = "favourable", None
        elif score <= -2:
            band, reason = "unfavourable", None
        else:
            band, reason = "mixed", None
        return {"band": band, "score": score, "prime_hits": prime_hits,
                "supporting_hits": supporting_hits,
                "negating_hits": negating_hits, "evidence": evidence,
                "reason": reason}

try:
    from .life_questions import DISCLAIMER_EN, DISCLAIMER_NE
except Exception:  # pragma: no cover
    DISCLAIMER_EN = ("Guidance only, not a guaranteed outcome. "
                     "Health entries are not medical advice — see a clinician. "
                     "For legal or financial decisions, consult a qualified professional.")
    DISCLAIMER_NE = ("यो मार्गदर्शन मात्र हो, निश्चित परिणाम होइन। "
                     "स्वास्थ्यसम्बन्धी प्रविष्टिहरू चिकित्सकीय सल्लाह होइनन् — चिकित्सकसँग परामर्श गर्नुहोस्। "
                     "कानुनी वा आर्थिक निर्णयका लागि योग्य विशेषज्ञसँग परामर्श गर्नुहोस्।")

# ---------------------------------------------------------------------------
# Classification keywords: 10+ per area per language.
# ---------------------------------------------------------------------------
KEYWORDS = {
    "personality": {
        "en": ["personality", "nature", "character", "temperament",
               "behaviour", "behavior", "myself", "self", "appearance",
               "confidence", "attitude", "disposition"],
        "ne": ["स्वभाव", "व्यक्तित्व", "चरित्र", "प्रकृति", "आचरण",
               "व्यवहार", "आफू", "रूप", "आत्मविश्वास", "मनोवृत्ति",
               "बानी", "आत्म"],
    },
    "career": {
        "en": ["career", "job", "profession", "promotion", "business",
               "work", "employment", "office", "boss", "service",
               "trade", "shop", "occupation"],
        "ne": ["करियर", "जागिर", "पेशा", "पदोन्नति", "व्यवसाय", "काम",
               "रोजगार", "कार्यालय", "हाकिम", "सेवा", "व्यापार",
               "पसल", "नोकरी"],
    },
    "finance": {
        "en": ["money", "wealth", "income", "finance", "financial",
               "savings", "gains", "profit", "property", "investment",
               "loan", "debt", "rich", "salary", "earnings"],
        "ne": ["पैसा", "सम्पत्ति", "धन", "आम्दानी", "वित्त", "बचत",
               "लाभ", "नाफा", "लगानी", "ऋण", "कमाइ", "धनी",
               "आर्थिक", "तलब"],
    },
    "health": {
        "en": ["health", "disease", "illness", "sickness", "hospital",
               "chronic", "pain", "body", "medicine", "treatment",
               "doctor", "recovery", "ailment"],
        "ne": ["स्वास्थ्य", "रोग", "बिरामी", "अस्पताल", "दीर्घरोग",
               "पीडा", "शरीर", "औषधि", "उपचार", "चिकित्सक", "निको",
               "व्याधि", "अस्वस्थ"],
    },
    "marriage": {
        "en": ["marriage", "marry", "married", "partner", "relationship", "spouse",
               "husband", "wife", "wedding", "love", "divorce",
               "engagement", "bride", "groom"],
        "ne": ["विवाह", "जीवनसाथी", "श्रीमान्", "श्रीमती", "जोडी",
               "सम्बन्ध", "प्रेम", "दाम्पत्य", "विवाहविच्छेद", "सगाई",
               "दुलहा", "दुलही", "विवाह"],
    },
    "education": {
        "en": ["education", "study", "exam", "examination", "school",
               "college", "university", "degree", "learning", "student",
               "admission", "academic"],
        "ne": ["पढाइ", "शिक्षा", "परीक्षा", "विद्यालय", "कलेज",
               "विश्वविद्यालय", "डिग्री", "अध्ययन", "विद्यार्थी",
               "भर्ना", "सिकाइ", "शैक्षिक"],
    },
    "family_home": {
        "en": ["family", "home", "house", "mother", "property", "land",
               "parents", "father", "household", "residence", "domestic"],
        "ne": ["परिवार", "घर", "आमा", "सम्पत्ति", "जग्गा", "बुबा",
               "आमाबुबा", "घरपरिवार", "माइती", "आवास", "परिवारजन"],
    },
    "foreign": {
        "en": ["foreign", "abroad", "visa", "travel", "settlement",
               "overseas", "migration", "passport", "journey", "trip",
               "emigration", "settle abroad"],
        "ne": ["विदेश", "भिसा", "यात्रा", "बसोबास", "प्रवास", "राहदानी",
               "परदेश", "आप्रवासन", "घुमघाम", "विदेशी", "विदेशिने",
               "बसाइँ"],
    },
}

# ---------------------------------------------------------------------------
# Out-of-scope detection (runs before classification).
# ---------------------------------------------------------------------------
_DEATH_EN = re.compile(r"\b(die|dies|dying|death|dead|mortality|lifespan)\b")
_DEATH_NE = ("मर्छु", "मर्न", "मृत्यु", "मरेर", "मर्ने", "मर्नेछु")
_LOTTERY_EN = re.compile(r"\blottery\b|\bgambling\b|\bcasino\b")
_LOTTERY_NE = ("लटरी", "जुवा")
_EXACT_DATE_EN = re.compile(
    r"\bexact date\b|\bexact day\b|\bprecise date\b|\bspecific date\b")
_EXACT_DATE_NE = ("ठ्याक्कै मिति", "निश्चित मिति", "ठ्याक्कै कहिले",
                  "कुन मितिमा ठ्याक्कै")

_OUT_OF_SCOPE_TEXT = {
    "death": (
        "Astrology does not predict death or lifespan. A chart can speak "
        "about vitality, health periods and the strength of the life-force "
        "houses, but the timing or manner of death is outside what "
        "astrology can honestly say.",
        "ज्योतिषले मृत्यु वा आयुको भविष्यवाणी गर्दैन। कुण्डलीले जीवनशक्ति, "
        "स्वास्थ्य अवधि र आयु-भावको बलको बारेमा बोल्न सक्छ, तर मृत्युको "
        "समय वा तरिका ज्योतिषले इमानदारीपूर्वक भन्न सक्ने कुरा होइन।",
    ),
    "lottery": (
        "Astrology cannot promise a lottery or gambling win. It can speak "
        "about general periods of gain or speculation caution from the "
        "wealth houses, but never about a specific ticket, draw or win.",
        "ज्योतिषले लटरी वा जुवामा जित्ने ग्यारेन्टी दिन सक्दैन। यसले सम्पत्ति "
        "भावबाट लाभ वा अनुमानगत सावधानीको सामान्य अवधिको बारेमा बोल्न सक्छ, "
        "तर कुनै खास टिकट, नतिजा वा जितको बारेमा कहिल्यै भन्न सक्दैन।",
    ),
    "exact_date": (
        "Astrology does not give exact dates for life events. What it can "
        "offer is a dasha-based period — a window of time when the chart "
        "leans supportive — framed as probability, not a fixed date.",
        "ज्योतिषले जीवनका घटनाका लागि ठ्याक्कै मिति दिँदैन। यसले दिन सक्ने "
        "कुरा दशा-आधारित अवधि हो — कुण्डलीले समर्थन गर्ने समयको खिड्की — "
        "जुन सम्भावनाको रूपमा प्रस्तुत गरिन्छ, निश्चित मितिको रूपमा होइन।",
    ),
}


def _normalise(text: str) -> str:
    text = unicodedata.normalize("NFC", text or "")
    text = text.lower()
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _scores(question_text: str) -> dict[str, int]:
    q = _normalise(question_text)
    scores: dict[str, int] = {}
    for area_id, langs in KEYWORDS.items():
        total = 0
        for kw in langs["en"]:
            total += len(re.findall(r"\b" + re.escape(kw) + r"\b", q))
        for kw in langs["ne"]:
            total += q.count(kw)
        scores[area_id] = total
    return scores


def classify(question_text: str):
    """-> (area_id, second_area_id_or_None, confidence).

    Score = keyword hits (word-boundary for English, substring for
    Nepali, after case/whitespace normalisation). The second area is
    returned only when it scores >= 50% of the top score. No area
    scores -> (None, None, 0.0).
    """
    scores = _scores(question_text)
    ranked = sorted(scores.items(), key=lambda kv: (-kv[1], AREA_ORDER.index(kv[0])))
    top_id, top = ranked[0]
    if top <= 0:
        return None, None, 0.0
    second_id, second = ranked[1]
    if second > 0 and second * 2 >= top:
        confidence = round(top / (top + second), 3)
        return top_id, second_id, confidence
    return top_id, None, 1.0


def detect_out_of_scope(question_text: str) -> dict | None:
    """Return refusal info for death/lottery/exact-date questions."""
    q = _normalise(question_text)
    if _DEATH_EN.search(q) or any(w in q for w in _DEATH_NE):
        kind = "death"
    elif _LOTTERY_EN.search(q) or any(w in q for w in _LOTTERY_NE):
        kind = "lottery"
    elif _EXACT_DATE_EN.search(q) or any(w in q for w in _EXACT_DATE_NE):
        kind = "exact_date"
    else:
        return None
    en, ne = _OUT_OF_SCOPE_TEXT[kind]
    return {"kind": kind, "explanation_en": en, "explanation_ne": ne}


def _area_house_sets(area_id: str) -> tuple[list[int], list[int], list[int]]:
    """(prime, supporting, negating) houses for an area.

    Supporting = 2nd/5th/9th/11th from the primary house; negating =
    12th from each prime house. See the module docstring.
    """
    prime = list(AREAS[area_id][0])
    primary = prime[0]
    supporting = []
    for rel in (2, 5, 9, 11):
        h = ((primary + rel - 2) % 12) + 1
        if h not in prime and h not in supporting:
            supporting.append(h)
    negating = []
    for h in prime:
        n = ((h - 2) % 12) + 1
        if n not in prime and n not in negating:
            negating.append(n)
    return prime, sorted(supporting), sorted(negating)


def _signified_map(chart: dict) -> dict[str, list[int]]:
    kp = (chart or {}).get("kp") or {}
    signified = kp.get("planet_signified_houses")
    if signified:
        return {p: [int(h) for h in hs] for p, hs in signified.items()}
    house_sig = kp.get("house_significators") or chart.get("house_significators") or {}
    out: dict[str, list[int]] = {}
    for house, sig in house_sig.items():
        for planet in (sig or {}).get("significator_order") or []:
            out.setdefault(planet, []).append(int(house))
    return {p: sorted(set(hs)) for p, hs in out.items()}


def _house_significators(chart: dict) -> dict:
    kp = (chart or {}).get("kp") or {}
    return kp.get("house_significators") or chart.get("house_significators") or {}


def _planet_rows(chart: dict) -> list[dict]:
    rows = []
    for row in (chart or {}).get("planets") or []:
        house = row.get("house")
        if house is None:
            house = (row.get("kp") or {}).get("house")
        if house is None:
            continue
        rows.append({
            "planet": row["planet"],
            "sign_en": row.get("sign_en") or (
                SIGNS_EN[row["sign"]] if row.get("sign") is not None else ""),
            "sign_ne": row.get("sign_ne") or (
                SIGNS_NE[row["sign"]] if row.get("sign") is not None else ""),
            "house": int(house),
        })
    return rows


def _lagna_sign(chart: dict) -> int | None:
    lagna = (chart or {}).get("lagna") or {}
    if lagna.get("sign") is not None:
        return int(lagna["sign"])
    return None


def _transit_houses(chart: dict) -> dict[str, int]:
    """Transiting planet -> whole-sign house from Lagna (birth only)."""
    lagna = _lagna_sign(chart)
    if lagna is None:
        return {}
    transits = chart.get("transits_now") or {}
    out = {}
    for planet, info in transits.items():
        sign = info.get("sign") if isinstance(info, dict) else info
        if sign is not None:
            out[planet] = (int(sign) - lagna) % 12 + 1
    return out


def _disclaimer(area_id: str) -> tuple[str, str]:
    en, ne = DISCLAIMER_EN, DISCLAIMER_NE
    if area_id == "health":
        en += (" This is not medical advice or a diagnosis. "
               "For any health concern, see a clinician promptly.")
        ne += (" यो चिकित्सकीय सल्लाह वा निदान होइन। "
               "कुनै पनि स्वास्थ्य समस्याका लागि तुरुन्त चिकित्सकसँग परामर्श गर्नुहोस्।")
    elif area_id == "finance":
        en += (" For financial decisions, consult a qualified financial adviser; "
               "never risk money you cannot afford to lose on speculation.")
        ne += (" आर्थिक निर्णयका लागि योग्य वित्तीय सल्लाहकारसँग परामर्श गर्नुहोस्; "
               "अनुमानमा गुमाउन नसकिने पैसा कहिल्यै जोखिममा नपार्नुहोस्।")
    elif area_id == "marriage":
        en += (" For legal matters arising from a relationship, consult a lawyer; "
               "relationship decisions should never rest on astrology alone.")
        ne += (" सम्बन्धबाट उत्पन्न कानुनी मामिलाका लागि वकिलसँग परामर्श गर्नुहोस्; "
               "सम्बन्धसम्बन्धी निर्णय कहिल्यै ज्योतिषमा मात्र भर पर्नु हुँदैन।")
    return en, ne


def _suggestions() -> list[dict]:
    return [{"id": a, "title_en": AREAS[a][1], "title_ne": AREAS[a][2]}
            for a in AREA_ORDER]


def _ordinal_en(h: int) -> str:
    return f"{h}{'st' if h == 1 else 'nd' if h == 2 else 'rd' if h == 3 else 'th'}"


def build_answer(question_text: str, bundle_or_horary: dict, lang: str = "en") -> dict:
    """Build the full answer dict for one question + one chart.

    lang is validated by the endpoint ("en"|"ne"); both languages are
    returned in every field regardless, and lang is echoed back.
    """
    question = (question_text or "").strip()
    if not question:
        raise ValueError("question must not be empty")
    lang = lang if lang in ("en", "ne") else "en"
    is_prashna = isinstance(bundle_or_horary, dict) and "ruling_planets" in bundle_or_horary

    # --- Out of scope first -------------------------------------------
    oos = detect_out_of_scope(question)
    if oos:
        closest, _second, _conf = classify(question)
        area = None
        if closest:
            area = {"id": closest, "title_en": AREAS[closest][1],
                    "title_ne": AREAS[closest][2]}
        dis_en, dis_ne = _disclaimer(closest) if closest else (DISCLAIMER_EN, DISCLAIMER_NE)
        return {
            "refusal": True, "kind": oos["kind"],
            "reason_en": oos["explanation_en"], "reason_ne": oos["explanation_ne"],
            "explanation_en": oos["explanation_en"],
            "explanation_ne": oos["explanation_ne"],
            "area_id": closest, "second_area_id": None, "confidence": 0.0,
            "area_title_en": area["title_en"] if area else None,
            "area_title_ne": area["title_ne"] if area else None,
            "direct_answer_en": oos["explanation_en"],
            "direct_answer_ne": oos["explanation_ne"],
            "planet_table": [], "supporting": [], "challenging": [],
            "timing_en": "", "timing_ne": "",
            "disclaimer_en": dis_en, "disclaimer_ne": dis_ne,
            "suggestions": _suggestions(), "lang": lang,
            "source_note": "prashna" if is_prashna else "birth",
        }

    # --- Classification -------------------------------------------------
    area_id, second_id, confidence = classify(question)
    if area_id is None:
        return {
            "fallback": True,
            "area_id": None, "second_area_id": None, "confidence": 0.0,
            "area_title_en": None, "area_title_ne": None,
            "direct_answer_en": (
                "I could not map this question to one of the 8 life areas "
                "this astrologer covers, so I will not guess an answer. "
                "Please ask about one of the areas below."),
            "direct_answer_ne": (
                "यो प्रश्नलाई यस ज्योतिषले समेट्ने ८ जीवन क्षेत्रमध्ये कुनैमा "
                "मिलाउन सकिएन, त्यसैले अनुमानित उत्तर दिइँदैन। कृपया तलका "
                "क्षेत्रमध्ये कुनै एकबारे सोध्नुहोस्।"),
            "planet_table": [], "supporting": [], "challenging": [],
            "timing_en": "", "timing_ne": "",
            "disclaimer_en": DISCLAIMER_EN, "disclaimer_ne": DISCLAIMER_NE,
            "suggestions": _suggestions(), "lang": lang,
            "source_note": "prashna" if is_prashna else "birth",
        }

    houses, title_en, title_ne, concern_en, concern_ne = AREAS[area_id]
    houses = list(houses)
    chart = bundle_or_horary or {}
    areas = analyse(chart)
    area = next(a for a in areas if a["id"] == area_id)
    rows = _planet_rows(chart)
    by_planet = {r["planet"]: r for r in rows}
    lords = house_lords(chart)
    signified = _signified_map(chart)
    house_sig = _house_significators(chart)

    # --- KP scoring ------------------------------------------------------
    prime, supporting_h, negating_h = _area_house_sets(area_id)
    q = {"id": f"area:{area_id}", "prime_houses": prime,
         "supporting_houses": supporting_h, "negating_houses": negating_h}
    checks = []
    if is_prashna:
        for rp in chart.get("ruling_planets") or []:
            planet = rp.get("planet")
            if planet:
                checks.append({"role_en": rp.get("role") or "Ruling planet",
                               "role_ne": rp.get("role_ne") or rp.get("role") or "रूलिङ ग्रह",
                               "planet": planet, "houses": signified.get(planet, [])})
    else:
        kp_planets = ((chart.get("kp") or {}).get("planets") or {})
        dasha = area["dasha_influence"]
        for lord, role_en, role_ne in (
            (dasha.get("mahadasha_lord"), "Current Mahadasha lord", "हालको महादशा स्वामी"),
            (dasha.get("antardasha_lord"), "Current Antardasha lord", "हालको अन्तर्दशा स्वामी"),
        ):
            if lord:
                checks.append({"role_en": role_en, "role_ne": role_ne,
                               "planet": lord, "houses": signified.get(lord, [])})
        moon = kp_planets.get("Moon") or {}
        for key, role_en, role_ne in (
            ("star_lord", "Moon star lord", "चन्द्र नक्षत्र स्वामी"),
            ("sub_lord", "Moon sub lord", "चन्द्र उपस्वामी"),
        ):
            planet = moon.get(key)
            if planet:
                checks.append({"role_en": role_en, "role_ne": role_ne,
                               "planet": planet, "houses": signified.get(planet, [])})
    for h in prime:
        sig = house_sig.get(h) or house_sig.get(str(h)) or {}
        csl = sig.get("cuspal_sub_lord")
        if csl:
            checks.append({"role_en": f"{_ordinal_en(h)} house cuspal sub lord",
                           "role_ne": f"{h}औँ भावको सन्धि उपस्वामी",
                           "planet": csl, "houses": signified.get(csl, [])})
    scored = _score_evidence(q, checks)
    band = scored["band"]

    # --- Direct answer (probability-framed) ------------------------------
    band_phrase = {
        "favourable": ("leans favourable", "अनुकूल देखिन्छ"),
        "unfavourable": ("leans unfavourable", "प्रतिकूल देखिन्छ"),
        "mixed": ("looks mixed", "मिश्रित देखिन्छ"),
        "unclear": ("does not speak clearly", "स्पष्ट बोल्दैन"),
    }[band]
    direct_en = (
        f"The chart {band_phrase[0]} for {concern_en} (score "
        f"{scored['score']}). This is probability guidance, not a certainty — "
        f"the strongest influences are noted below.")
    direct_ne = (
        f"कुण्डलीले {concern_ne}का लागि {band_phrase[1]} (अङ्क "
        f"{scored['score']})। यो सम्भावना-आधारित मार्गदर्शन हो, निश्चितता होइन — "
        f"सबैभन्दा बलिया प्रभावहरू तल उल्लेख छन्।")

    # --- Planet table: in, rules, or aspects the area's houses ----------
    planet_table = []
    for p in PLANETS:
        if p not in by_planet:
            continue
        row = by_planet[p]
        in_area = row["house"] in houses
        ruled = [h for h in houses if lords.get(h) == p]
        asp_all = aspected_houses(p, row["house"])
        asp_area = [h for h in asp_all if h in houses]
        if not (in_area or ruled or asp_area):
            continue
        if in_area:
            effect_en = (f"{p} sits in the {_ordinal_en(row['house'])} house, "
                         f"bringing {'support' if NATURE[p] == 'benefic' else 'pressure' if NATURE[p] == 'malefic' else 'drive'} "
                         f"to {concern_en}.")
            effect_ne = (f"{PLANET_NE[p]} {_ordinal_en(row['house'])} भावमा रहेकाले "
                         f"{concern_ne}मा "
                         f"{'समर्थन' if NATURE[p] == 'benefic' else 'दबाब' if NATURE[p] == 'malefic' else 'ऊर्जा'} दिन्छ।")
            placement = "in"
        elif ruled:
            effect_en = (f"{p} rules the {_ordinal_en(ruled[0])} house, so "
                         f"{concern_en} follows {p}'s condition in this chart.")
            effect_ne = (f"{PLANET_NE[p]} {_ordinal_en(ruled[0])} भावको स्वामी भएकाले "
                         f"{concern_ne} यस कुण्डलीमा {PLANET_NE[p]}को अवस्थाअनुसार चल्छ।")
            placement = "rules"
        else:
            effect_en = (f"{p} aspects the {_ordinal_en(asp_area[0])} house, "
                         f"influencing {concern_en} from a distance.")
            effect_ne = (f"{PLANET_NE[p]}ले {_ordinal_en(asp_area[0])} भावलाई दृष्टि दिएकाले "
                         f"{concern_ne}मा टाढाबाट प्रभाव पर्छ।")
            placement = "aspects"
        planet_table.append({
            "planet": p, "planet_ne": PLANET_NE[p],
            "sign_en": row["sign_en"], "sign_ne": row["sign_ne"],
            "house": row["house"], "rules": ruled, "aspects": asp_all,
            "placement": placement, "effect_en": effect_en, "effect_ne": effect_ne,
        })

    # --- Supporting / challenging lines ----------------------------------
    supporting, challenging = [], []
    for row in planet_table:
        p = row["planet"]
        line_en = f"{p}: {row['effect_en']}"
        line_ne = f"{PLANET_NE[p]}: {row['effect_ne']}"
        if NATURE[p] == "benefic":
            supporting.append({"en": line_en, "ne": line_ne})
        elif NATURE[p] == "malefic":
            challenging.append({"en": line_en, "ne": line_ne})
    dasha = area["dasha_influence"]
    for lord, hits, label_en, label_ne in (
        (dasha.get("mahadasha_lord"), dasha.get("mahadasha_signifies_area_houses"),
         "Mahadasha lord", "महादशा स्वामी"),
        (dasha.get("antardasha_lord"), dasha.get("antardasha_signifies_area_houses"),
         "Antardasha lord", "अन्तर्दशा स्वामी"),
    ):
        if lord and hits:
            supporting.append({
                "en": f"{label_en} {lord} signifies area house(s) {hits}, supporting {concern_en}.",
                "ne": f"{label_ne} {PLANET_NE[lord]}ले क्षेत्रको {hits} भाव सङ्केत गर्छ, जसले {concern_ne}लाई समर्थन गर्छ।"})
    for ev in scored["evidence"]:
        for h in ev["houses"]:
            if h["class"] == "negating":
                challenging.append({
                    "en": f"{ev['role_en']} {ev['planet']} signifies the negating "
                          f"{_ordinal_en(h['house'])} house, weighing against {concern_en}.",
                    "ne": f"{ev['role_ne']} {PLANET_NE[ev['planet']]}ले नकार्ने "
                          f"{_ordinal_en(h['house'])} भाव सङ्केत गर्छ, जसले {concern_ne}लाई कमजोर बनाउँछ।"})

    # --- Timing: dasha periods + transits, never exact dates -------------
    if is_prashna:
        rp_names = ", ".join(
            f"{rp.get('planet')} ({rp.get('role')})"
            for rp in chart.get("ruling_planets") or [] if rp.get("planet"))
        timing_en = (
            f"Prashna timing is read from the ruling planets ({rp_names or 'unavailable'}) "
            f"and their signification of houses {houses} — a period indication, not a date. "
            f"A prashna chart carries no birth dasha.")
        timing_ne = (
            f"प्रश्न समय रूलिङ ग्रहहरू ({rp_names or 'उपलब्ध छैन'}) र तिनले "
            f"{houses} भावको सङ्केतबाट पढिन्छ — यो अवधिको सङ्केत हो, मिति होइन। "
            f"प्रश्न कुण्डलीमा जन्म दशा हुँदैन।")
    else:
        md, ad = dasha.get("mahadasha_lord"), dasha.get("antardasha_lord")
        md_span = dasha.get("mahadasha_period") or {}
        ad_span = dasha.get("antardasha_period") or {}
        timing_en = (
            f"Running Vimshottari: {md} Mahadasha "
            f"({md_span.get('start')} to {md_span.get('end')}) and {ad} Antardasha "
            f"({ad_span.get('start')} to {ad_span.get('end')}). "
            f"{md} signifies area house(s) {dasha.get('mahadasha_signifies_area_houses') or 'none'}; "
            f"{ad} signifies area house(s) {dasha.get('antardasha_signifies_area_houses') or 'none'}. "
            f"Read these as periods when the chart leans one way or the other, never as exact dates.")
        timing_ne = (
            f"चलिरहेको विम्शोत्तरी: {PLANET_NE[md] if md else ''} महादशा "
            f"({md_span.get('start')} देखि {md_span.get('end')}) र "
            f"{PLANET_NE[ad] if ad else ''} अन्तर्दशा "
            f"({ad_span.get('start')} देखि {ad_span.get('end')})। "
            f"{PLANET_NE[md] if md else ''}ले क्षेत्रको {dasha.get('mahadasha_signifies_area_houses') or 'कुनै होइन'} भाव सङ्केत गर्छ; "
            f"{PLANET_NE[ad] if ad else ''}ले {dasha.get('antardasha_signifies_area_houses') or 'कुनै होइन'} भाव सङ्केत गर्छ। "
            f"यी अवधिका रूपमा पढ्नुहोस्, ठ्याक्कै मितिका रूपमा होइन।")
        transit_houses = _transit_houses(chart)
        touching = {p: h for p, h in transit_houses.items() if h in houses}
        if touching:
            bits_en = ", ".join(f"{p} transiting the {_ordinal_en(h)} house" for p, h in touching.items())
            bits_ne = ", ".join(f"{PLANET_NE[p]} {_ordinal_en(h)} भावमा गोचर" for p, h in touching.items())
            timing_en += f" Currently: {bits_en}."
            timing_ne += f" हाल: {bits_ne}।"

    dis_en, dis_ne = _disclaimer(area_id)
    return {
        "area_id": area_id, "second_area_id": second_id, "confidence": confidence,
        "area_title_en": title_en, "area_title_ne": title_ne,
        "direct_answer_en": direct_en, "direct_answer_ne": direct_ne,
        "planet_table": planet_table, "supporting": supporting,
        "challenging": challenging, "timing_en": timing_en, "timing_ne": timing_ne,
        "disclaimer_en": dis_en, "disclaimer_ne": dis_ne,
        "band": band, "score": scored["score"], "evidence": scored["evidence"],
        "life_area": area, "lang": lang,
        "source_note": "prashna" if is_prashna else "birth",
    }
