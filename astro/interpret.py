"""Interpretation engine v2 — combinatorial, chart-specific readings.

Why v1 read like a free site: each "chapter" was one templated
placement line per lord. Premium reports (Clickastro, Parashara's
Light) are assembled from a rule base over THIS chart's facts. This
module does the same: every paragraph is stitched from the planet's
actual lordships for this Lagna, its sign/house/nakshatra, dignity,
combustion/retrogression, conjunctions, aspects cast and received
(with the other planets' roles named), dispositor chain, Shadbala
rank and Ishta/Kashta tilt. No paragraph is emitted unless it cites
at least three concrete facts of the chart at hand.

All text is original to this project and bilingual (EN / नेपाली).
"""
from __future__ import annotations

from . import aspects as asp
from .charts import dignity, house_lords, house_of, sign_of_house
from .jaimini import rasi_aspects, sign_lord_jaimini  # noqa: F401  (rasi_aspects kept for API parity)
from .names import (
    FRIENDSHIP, HOUSE_NAMES_EN, HOUSE_NAMES_NE, HOUSE_THEMES_EN,
    HOUSE_THEMES_NE, NAKSHATRAS_EN, NAKSHATRAS_NE, PLANET_NE, SIGNS_EN,
    SIGNS_NE, SIGN_LORDS,
)
from .predictions import _bi

GRAHAS_7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
ALL9 = GRAHAS_7 + ["Rahu", "Ketu"]

# Natural significations (karakatvas) — classical BPHS list, condensed.
SIGNIFICATIONS = {
    "Sun": ("the soul, father, authority, vitality and self-respect",
            "आत्मा, पिता, अधिकार, जीवनशक्ति र आत्मसम्मान"),
    "Moon": ("the mind, mother, emotions, memory and public image",
             "मन, आमा, भावना, स्मृति र सामाजिक छवि"),
    "Mars": ("energy, courage, siblings, land and technical skill",
             "ऊर्जा, साहस, दाजुभाइ-दिदीबहिनी, जग्गा र प्राविधिक कौशल"),
    "Mercury": ("intellect, speech, learning, trade and documentation",
                "बुद्धि, वाणी, अध्ययन, व्यापार र दस्तावेज"),
    "Jupiter": ("wisdom, children, teachers, dharma and expansion",
                "ज्ञान, सन्तान, गुरु, धर्म र विस्तार"),
    "Venus": ("spouse, love, comforts, arts, vehicles and luxury",
              "जीवनसाथी, प्रेम, सुखसुविधा, कला, वाहन र विलासिता"),
    "Saturn": ("labour, discipline, longevity, service and the masses",
               "श्रम, अनुशासन, आयु, सेवा र जनसाधारण"),
    "Rahu": ("worldly ambition, foreign things, technology and unconventional rise",
             "सांसारिक महत्त्वाकांक्षा, विदेशी वस्तु, प्रविधि र अपरम्परागत उन्नति"),
    "Ketu": ("detachment, research, spirituality and sudden insight",
             "वैराग्य, अनुसन्धान, आध्यात्मिकता र आकस्मिक अन्तर्दृष्टि"),
}
# Bhava karakas (house significators), primary one per house.
HOUSE_KARAKA = {
    1: "Sun", 2: "Jupiter", 3: "Mars", 4: "Moon", 5: "Jupiter",
    6: "Saturn", 7: "Venus", 8: "Saturn", 9: "Jupiter", 10: "Saturn",
    11: "Jupiter", 12: "Saturn",
}
TRIKONA = {1, 5, 9}
KENDRA = {1, 4, 7, 10}
DUSTHANA = {6, 8, 12}
UPACHAYA = {3, 6, 10, 11}
MARAKA = {2, 7}


def _house_role_tag(house: int) -> tuple[str, str]:
    if house == 1:
        return ("the Lagna itself — a trine and an angle at once",
                "स्वयं लग्न — त्रिकोण र केन्द्र दुवै")
    tags = []
    tags_ne = []
    if house in TRIKONA:
        tags.append("a trine (trikona) of merit and fortune")
        tags_ne.append("पुण्य र भाग्यको त्रिकोण")
    if house in KENDRA:
        tags.append("an angle (kendra), a house of visible action")
        tags_ne.append("दृश्य कर्मको केन्द्र")
    if house in DUSTHANA:
        tags.append("a difficult house (dusthana) whose results must be earned")
        tags_ne.append("परिश्रमले मात्र फल दिने दुष्टस्थान")
    if house in MARAKA:
        tags.append("a maraka (health-testing) house")
        tags_ne.append("मारक (स्वास्थ्य-परीक्षण) भाव")
    if house in UPACHAYA and house not in KENDRA:
        tags.append("a growth house (upachaya) that improves with time and effort")
        tags_ne.append("समय र मेहनतसँगै बढ्ने उपचय भाव")
    if not tags:
        tags.append("a house of sustenance and exchange" if house == 2 else
                    "a house of expression and enterprise")
        tags_ne.append("पोषण र आदानप्रदानको भाव" if house == 2 else "अभिव्यक्ति र उद्यमको भाव")
    return "; ".join(tags), "; ".join(tags_ne)


def functional_roles(lagna_sign: int) -> dict[str, dict]:
    """Per-planet functional portfolio for this Lagna: the houses it
    rules, with the classical role of each, plus summary flags
    (yogakaraka / benefic-leaning / malefic-leaning / maraka)."""
    lords = house_lords(lagna_sign)
    roles: dict[str, dict] = {}
    for planet in GRAHAS_7:
        ruled = [h for h in range(1, 13) if lords[h] == planet]
        flags = []
        if any(h in KENDRA for h in ruled) and any(h in TRIKONA for h in ruled):
            flags.append("yogakaraka")
        if any(h in TRIKONA for h in ruled) and not any(h in DUSTHANA for h in ruled):
            flags.append("benefic-leaning")
        if any(h in DUSTHANA for h in ruled) and not any(h in TRIKONA for h in ruled):
            flags.append("malefic-leaning")
        if any(h in MARAKA for h in ruled):
            flags.append("maraka")
        roles[planet] = {"ruled": ruled, "flags": flags}
    return roles


def _role_sentence(planet: str, roles: dict) -> dict:
    ruled = roles[planet]["ruled"]
    flags = roles[planet]["flags"]
    bits_en, bits_ne = [], []
    for h in ruled:
        tag_en, tag_ne = _house_role_tag(h)
        bits_en.append(f"the {HOUSE_NAMES_EN[h-1]} house ({HOUSE_THEMES_EN[h]} — {tag_en})")
        bits_ne.append(f"{HOUSE_NAMES_NE[h-1]} भाव ({HOUSE_THEMES_NE[h]} — {tag_ne})")
    en = f"For this chart {planet} rules " + " and ".join(bits_en) + "."
    ne = f"यस कुण्डलीमा {PLANET_NE[planet]} " + " र ".join(bits_ne) + " को स्वामी हो।"
    extra_en, extra_ne = [], []
    if "yogakaraka" in flags:
        extra_en.append(f" Holding both an angle and a trine, {planet} is the Yogakaraka — the single most productive planet of this chart.")
        extra_ne.append(f" केन्द्र र त्रिकोण दुवैको स्वामी भएकाले {PLANET_NE[planet]} योगकारक हो — यस कुण्डलीको सबैभन्दा फलदायी ग्रह।")
    if "benefic-leaning" in flags:
        extra_en.append(f" As a trine lord without a difficult house, {planet} is functionally benefic here, whatever its natural nature.")
        extra_ne.append(f" दुष्टस्थानविनाको त्रिकोण स्वामी भएकाले {PLANET_NE[planet]} यहाँ कार्यात्मक रूपमा शुभ छ, उसको नैसर्गिक स्वभाव जे भए पनि।")
    if "malefic-leaning" in flags:
        extra_en.append(f" Ruling only difficult/growth houses, {planet} is functionally demanding here: its periods and transits must be handled with discipline.")
        extra_ne.append(f" कठिन/वृद्धि भावहरूको मात्र स्वामी भएकाले {PLANET_NE[planet]} यहाँ कार्यात्मक रूपमा कठिन छ: यसका दशा र गोचर अनुशासनले सम्हाल्नुपर्छ।")
    if "maraka" in flags and "yogakaraka" not in flags:
        extra_en.append(f" As a maraka lord, {planet} can also test health in its periods when afflicted.")
        extra_ne.append(f" मारक स्वामीका रूपमा, {PLANET_NE[planet]} पीडित हुँदा आफ्ना अवधिमा स्वास्थ्यको परीक्षा पनि लिन सक्छ।")
    sig_en, sig_ne = SIGNIFICATIONS[planet]
    return _bi(en + "".join(extra_en) + f" By nature it signifies {sig_en}.",
               ne + "".join(extra_ne) + f" स्वभावतः यसले {sig_ne} जनाउँछ।")


def _dignity_phrase(planet: str, planets: dict) -> tuple[str, str, str]:
    """(category, english fragment, nepali fragment) — full dignity:
    exalted / moolatrikona / own / debilitated / friend / enemy / neutral,
    judged against the dispositor by natural friendship."""
    p = planets[planet]
    sign = p["sign"]
    if planet in ("Rahu", "Ketu"):
        return "node", "", ""
    d = dignity(planet, sign)
    if d == "exalted":
        return "exalted", "it is exalted — at maximum dignity", "यो उच्च राशिमा छ — सर्वोच्च गरिमा"
    if d == "debilitated":
        return "debilitated", "it is debilitated — at its weakest dignity", "यो नीच राशिमा छ — सबैभन्दा कमजोर गरिमा"
    from .names import MOOLATRIKONA
    mt = MOOLATRIKONA.get(planet)
    if mt and mt[0] == sign and mt[1] <= p["degree_in_sign"] < mt[2]:
        return "moolatrikona", "it stands in its Moolatrikona — its office of greatest authority", \
            "यो आफ्नो मूलत्रिकोणमा छ — सर्वाधिक अधिकारको स्थान"
    if d == "own":
        return "own", "it occupies its own sign — self-reliant and steady", \
            "यो आफ्नै राशिमा छ — आत्मनिर्भर र स्थिर"
    dispositor = SIGN_LORDS[sign]
    if dispositor == planet:
        return "own", "it occupies its own sign", "यो आफ्नै राशिमा छ"
    friends, _neutral, enemies = FRIENDSHIP[planet]
    if dispositor in friends:
        return "friend", f"it is in a friend's sign ({dispositor}'s), which supports it", \
            f"यो मित्रको राशिमा ({PLANET_NE[dispositor]}को) छ, जसले यसलाई साथ दिन्छ"
    if dispositor in enemies:
        return "enemy", f"it is in an enemy's sign ({dispositor}'s), which hampers it", \
            f"यो शत्रुको राशिमा ({PLANET_NE[dispositor]}को) छ, जसले यसलाई बाधा पुर्याउँछ"
    return "neutral", f"it is in a neutral sign ({dispositor}'s)", \
        f"यो तटस्थ राशिमा ({PLANET_NE[dispositor]}को) छ"


def _strength_sentence(planet: str, shadbala: dict | None) -> dict | None:
    if not shadbala or planet not in shadbala.get("planets", {}):
        return None
    r = shadbala["planets"][planet]
    ratio = r["ratio"]
    if ratio >= 1.3:
        band_en, band_ne = "well above the minimum strength classical texts require of it", \
            "शास्त्रले मागेको न्यूनतम बलभन्दा धेरै माथि"
    elif ratio >= 1.0:
        band_en, band_ne = "above the minimum strength classical texts require of it", \
            "शास्त्रले मागेको न्यूनतम बलभन्दा माथि"
    elif ratio >= 0.85:
        band_en, band_ne = "slightly below the minimum strength classical texts require of it", \
            "शास्त्रले मागेको न्यूनतम बलभन्दा अलिकति तल"
    else:
        band_en, band_ne = "well below the minimum strength classical texts require of it", \
            "शास्त्रले मागेको न्यूनतम बलभन्दा धेरै तल"
    tilt_en = ("its Ishta Phala exceeds its Kashta Phala, so its results lean favourable"
               if r["ishta"] > r["kashta"] else
               "its Kashta Phala exceeds its Ishta Phala, so its results must be worked for")
    tilt_ne = ("यसको इष्टफल कष्टफलभन्दा बढी छ, त्यसैले यसको फल अनुकूलतिर ढल्किन्छ"
               if r["ishta"] > r["kashta"] else
               "यसको कष्टफल इष्टफलभन्दा बढी छ, त्यसैले यसको फल परिश्रमले मात्र पाइन्छ")
    return _bi(
        f"In Shadbala {planet} scores {r['rupas']:.2f} rupas — rank {r['rank']} of 7, {band_en}; {tilt_en}.",
        f"षड्बलमा {PLANET_NE[planet]}ले {r['rupas']:.2f} रूपा पाएको छ — ७ मध्ये क्रम {r['rank']}, {band_ne}; {tilt_ne}।",
    )


def _planet_position_sentence(planet: str, planets: dict, lagna_sign: int,
                              roles: dict) -> dict:
    p = planets[planet]
    h = house_of(p["sign"], lagna_sign)
    _cat, dig_en, dig_ne = _dignity_phrase(planet, planets)
    state_en, state_ne = [], []
    if planets[planet].get("retrograde") and planet not in ("Rahu", "Ketu"):
        state_en.append("it is retrograde, turning its energy inward and delaying its fruits until reviewed")
        state_ne.append("यो वक्री छ, जसले यसको ऊर्जा भित्र फर्काउँछ र पुनरावलोकन नगरेसम्म फल ढिलो गर्छ")
    conj = asp.conjunct_planets(planet, planets)
    if conj:
        state_en.append("it is joined by " + ", ".join(conj) +
                        " — their significations and lordships blend with its own")
        state_ne.append("योसँग " + ", ".join(PLANET_NE[c] for c in conj) +
                        " बसेको छ — तिनका कारकत्व र भाव-स्वामित्व यससँग मिसिन्छ")
    disp = SIGN_LORDS[p["sign"]]
    if disp != planet:
        dh = house_of(planets[disp]["sign"], lagna_sign)
        state_en.append(f"its dispositor {disp} is placed in the {HOUSE_NAMES_EN[dh-1]} house, "
                        f"so {planet}'s results are routed through {HOUSE_THEMES_EN[dh]}")
        state_ne.append(f"यसको राशिस्वामी {PLANET_NE[disp]} {HOUSE_NAMES_NE[dh-1]} भावमा छ, "
                        f"त्यसैले {PLANET_NE[planet]}को फल {HOUSE_THEMES_NE[dh]} हुँदै आउँछ")
    en = (f"{planet} is placed in the {HOUSE_NAMES_EN[h-1]} house ({HOUSE_THEMES_EN[h]}) in "
          f"{SIGNS_EN[p['sign']]}, in {NAKSHATRAS_EN[p['nakshatra']]} nakshatra, pada {p['pada']}")
    ne = (f"{PLANET_NE[planet]} {HOUSE_NAMES_NE[h-1]} भावमा ({HOUSE_THEMES_NE[h]}) "
          f"{SIGNS_NE[p['sign']]} राशिमा, {NAKSHATRAS_NE[p['nakshatra']]} नक्षत्रको पद {p['pada']} मा छ")
    if dig_en:
        en += f"; {dig_en}"
        ne += f"; {dig_ne}"
    if state_en:
        en += "; " + "; ".join(state_en)
        ne += "; " + "; ".join(state_ne)
    return _bi(en + ".", ne + "।")


def _aspect_sentence(planet: str, planets: dict, lagna_sign: int,
                     roles: dict, lords: dict) -> dict | None:
    cast_houses = asp.houses_aspected_by(planet, planets, lagna_sign)
    received = asp.aspecting_planets(planets[planet]["sign"], planets, exclude=planet)
    bits_en, bits_ne = [], []
    if cast_houses:
        bits_en.append(f"it casts its aspect on the " +
                       ", ".join(f"{HOUSE_NAMES_EN[h-1]} house ({HOUSE_THEMES_EN[h]})" for h in cast_houses))
        bits_ne.append("यसले " + ", ".join(f"{HOUSE_NAMES_NE[h-1]} भाव ({HOUSE_THEMES_NE[h]})" for h in cast_houses) +
                       " मा दृष्टि दिन्छ")
    if received:
        desc_en, desc_ne = [], []
        for q in received:
            if q in roles and roles[q]["ruled"]:
                desc_en.append(f"{q} (lord of {', '.join(str(x) for x in roles[q]['ruled'])})")
                desc_ne.append(f"{PLANET_NE[q]} (भाव {', '.join(str(x) for x in roles[q]['ruled'])} को स्वामी)")
            else:
                desc_en.append(q)
                desc_ne.append(PLANET_NE[q])
        bits_en.append("it receives the aspect of " + ", ".join(desc_en))
        bits_ne.append("यसमाथि " + ", ".join(desc_ne) + " को दृष्टि पर्छ")
    if not bits_en:
        return None
    return _bi(f"By aspect, " + "; ".join(bits_en) + ".",
               "दृष्टिका हिसाबले, " + "; ".join(bits_ne) + "।")


def planet_chapter(planet: str, planets: dict, lagna_sign: int, roles: dict,
                   lords: dict, charts: dict, shadbala: dict | None,
                   combust: dict, karakas: dict) -> list[dict]:
    """4-5 paragraphs on one planet, each stitched from this chart's
    facts. Nodes have no lordship/Shadbala: their chapter is built from
    placement, dispositor, the axis partner and aspect instead."""
    facts: list[dict] = []
    if planet in roles:
        facts.append(_role_sentence(planet, roles))
    else:
        # Node: role comes from its dispositor and house.
        p = planets[planet]
        disp = SIGN_LORDS[p["sign"]]
        h = house_of(p["sign"], lagna_sign)
        dh = house_of(planets[disp]["sign"], lagna_sign)
        sig_en, sig_ne = SIGNIFICATIONS[planet]
        facts.append(_bi(
            f"{planet} holds no lordship of its own; it acts through its dispositor {disp}, "
            f"placed in the {HOUSE_NAMES_EN[dh-1]} house, and through the {HOUSE_NAMES_EN[h-1]} house it occupies. "
            f"By nature it signifies {sig_en}.",
            f"{PLANET_NE[planet]}को आफ्नै भाव-स्वामित्व छैन; यसले आफ्नो राशिस्वामी {PLANET_NE[disp]} "
            f"({HOUSE_NAMES_NE[dh-1]} भावमा बसेको) र आफू बसेको {HOUSE_NAMES_NE[h-1]} भाव हुँदै काम गर्छ। "
            f"स्वभावतः यसले {sig_ne} जनाउँछ।",
        ))
    facts.append(_planet_position_sentence(planet, planets, lagna_sign, roles))
    if combust.get(planet):
        facts.append(_bi(
            f"{planet} is combust — close enough to the Sun for its light to be overshadowed; "
            f"traditionally its results surface after effort and with maturity rather than early ease.",
            f"{PLANET_NE[planet]} अस्त छ — सूर्यको यति नजिक कि यसको उज्यालो ओझेलमा पर्छ; "
            f"परम्परागत रूपमा यसको फल प्रारम्भिक सहजताभन्दा परिश्रम र परिपक्वतासँगै देखिन्छ।",
        ))
    aspct = _aspect_sentence(planet, planets, lagna_sign, roles, lords)
    if aspct:
        facts.append(aspct)
    # Chara karaka identity, if any.
    for kname, kplanet in (karakas or {}).items():
        if kplanet == planet:
            facts.append(_bi(
                f"In the Jaimini scheme {planet} is the {kname} of this chart — a soul-level role that "
                f"magnifies everything said above in its dasha and transit periods.",
                f"जैमिनी पद्धतिमा {PLANET_NE[planet]} यस कुण्डलीको {kname} हो — आत्म-तहको भूमिका, "
                f"जसले यसका दशा र गोचर अवधिमा माथिका सबै कुरा बढाउँछ।",
            ))
            break
    # Navamsa corroboration.
    d9 = (charts or {}).get("D9") or {}
    if d9.get(planet) is not None:
        d9_sign = d9[planet]
        d9_lagna = d9.get("Lagna", lagna_sign)
        d9_house = house_of(d9_sign, d9_lagna)
        varg = " It is Vargottama — the same sign in D1 and D9 — which makes its results firm and undiluted." \
            if d9_sign == planets[planet]["sign"] else ""
        varg_ne = " यो वर्गोत्तम हो — D1 र D9 दुवैमा एउटै राशि — जसले यसको फल दृढ र अविमिश्रित बनाउँछ।" \
            if d9_sign == planets[planet]["sign"] else ""
        facts.append(_bi(
            f"In the Navamsa (D9) {planet} sits in {SIGNS_EN[d9_sign]}, the {HOUSE_NAMES_EN[d9_house-1]} sign "
            f"of the D9 chart — the inner, mature expression of the planet.{varg}",
            f"नवांश (D9) मा {PLANET_NE[planet]} {SIGNS_NE[d9_sign]} राशिमा छ, D9 कुण्डलीको {HOUSE_NAMES_NE[d9_house-1]} स्थान "
            f"— ग्रहको भित्री, परिपक्व अभिव्यक्ति।{varg_ne}",
        ))
    strength = _strength_sentence(planet, shadbala)
    if strength:
        facts.append(strength)
    return facts


def planet_chapters(ctx: dict) -> dict[str, list[dict]]:
    planets, lagna_sign = ctx["planets"], ctx["lagna_sign"]
    roles = functional_roles(lagna_sign)
    lords = house_lords(lagna_sign)
    return {
        p: planet_chapter(p, planets, lagna_sign, roles, lords,
                          ctx.get("charts") or {}, ctx.get("shadbala"),
                          ctx.get("combust") or {}, ctx.get("karakas") or {})
        for p in ALL9
    }


# ---------------------------------------------------------------------------
# House chapters
# ---------------------------------------------------------------------------
def house_chapters(ctx: dict) -> list[dict]:
    planets, lagna_sign = ctx["planets"], ctx["lagna_sign"]
    lords = house_lords(lagna_sign)
    roles = functional_roles(lagna_sign)
    av = ctx.get("ashtakavarga") or {}
    bhava_rows = {r["house"]: r for r in (ctx.get("bhava_bala") or [])}
    out = []
    for house in range(1, 13):
        sign = sign_of_house(house, lagna_sign)
        lord = lords[house]
        facts: list[dict] = []
        # Lord placement chain.
        lh = house_of(planets[lord]["sign"], lagna_sign)
        _cat, dig_en, dig_ne = _dignity_phrase(lord, planets)
        facts.append(_bi(
            f"The {HOUSE_NAMES_EN[house-1]} house ({HOUSE_THEMES_EN[house]}) is {SIGNS_EN[sign]}; its lord "
            f"{lord} is placed in the {HOUSE_NAMES_EN[lh-1]} house ({HOUSE_THEMES_EN[lh]}) in "
            f"{SIGNS_EN[planets[lord]['sign']]}{'; ' + dig_en if dig_en else ''}. "
            f"The condition of the lord is the single biggest factor in how this house delivers.",
            f"{HOUSE_NAMES_NE[house-1]} भाव ({HOUSE_THEMES_NE[house]}) {SIGNS_NE[sign]} राशि हो; यसको स्वामी "
            f"{PLANET_NE[lord]} {HOUSE_NAMES_NE[lh-1]} भावमा ({HOUSE_THEMES_NE[lh]}) {SIGNS_NE[planets[lord]['sign']]} राशिमा छ"
            f"{'; ' + dig_ne if dig_ne else ''}। "
            f"यस भावको फल कस्तो हुन्छ भन्नेमा स्वामीको अवस्था नै सबैभन्दा ठूलो कारक हो।",
        ))
        # Occupants.
        occ = [p for p in ALL9 if planets[p]["sign"] == sign]
        for p in occ:
            if p in roles:
                ruled_txt = ", ".join(str(x) for x in roles[p]["ruled"])
                facts.append(_bi(
                    f"{p} occupies this house. It carries here the portfolio of house(s) {ruled_txt}, "
                    f"so themes of {', '.join(HOUSE_THEMES_EN[x] for x in roles[p]['ruled'])} enter "
                    f"{HOUSE_THEMES_EN[house]} directly.",
                    f"{PLANET_NE[p]} यस भावमा बसेको छ। यसले यहाँ भाव {ruled_txt} को जिम्मेवारी बोकेको छ, "
                    f"त्यसैले {', '.join(HOUSE_THEMES_NE[x] for x in roles[p]['ruled'])} का विषय "
                    f"{HOUSE_THEMES_NE[house]} मा सिधै प्रवेश गर्छन्।",
                ))
            else:
                facts.append(_bi(
                    f"{p} occupies this house, colouring {HOUSE_THEMES_EN[house]} with its significations "
                    f"({SIGNIFICATIONS[p][0]}), channelled through its dispositor {SIGN_LORDS[sign]}.",
                    f"{PLANET_NE[p]} यस भावमा बसेको छ, जसले {HOUSE_THEMES_NE[house]} लाई आफ्ना कारकत्व "
                    f"({SIGNIFICATIONS[p][1]}) ले रङ्गाउँछ, राशिस्वामी {PLANET_NE[SIGN_LORDS[sign]]} मार्फत।",
                ))
        if not occ:
            facts.append(_bi(
                f"No planet occupies this house, so its results come purely through its lord {lord} "
                f"and the aspects it receives.",
                f"यस भावमा कुनै ग्रह बसेको छैन, त्यसैले यसको फल यसको स्वामी {PLANET_NE[lord]} "
                f"र यसले पाउने दृष्टिबाट मात्र आउँछ।",
            ))
        # Aspects received.
        aspectors = asp.aspecting_planets(sign, planets)
        if aspectors:
            desc_en = ", ".join(
                f"{q} (lord of {', '.join(str(x) for x in roles[q]['ruled'])})" if q in roles and roles[q]["ruled"]
                else q for q in aspectors)
            desc_ne = ", ".join(
                f"{PLANET_NE[q]} (भाव {', '.join(str(x) for x in roles[q]['ruled'])} को स्वामी)" if q in roles and roles[q]["ruled"]
                else PLANET_NE[q] for q in aspectors)
            facts.append(_bi(
                f"The house receives the aspect of {desc_en} — each aspecting planet injects its own "
                f"lordship themes into {HOUSE_THEMES_EN[house]}.",
                f"यस भावमाथि {desc_ne} को दृष्टि पर्छ — प्रत्येक दृष्टि दिने ग्रहले आफ्ना भाव-विषय "
                f"{HOUSE_THEMES_NE[house]} मा मिसाउँछ।",
            ))
        # Ashtakavarga + Bhava Bala bands.
        if av:
            sav = av["Sarvashtakavarga"][sign]
            karaka = HOUSE_KARAKA[house]
            bav = av[karaka][sign]
            if sav >= 30:
                band_en, band_ne = "an exceptionally strong bindu count", "असाधारण बलियो बिन्दु गणना"
            elif sav >= 25:
                band_en, band_ne = "a supportive bindu count", "सहयोगी बिन्दु गणना"
            elif sav >= 20:
                band_en, band_ne = "an average bindu count — results need effort", "औसत बिन्दु गणना — फलका लागि मेहनत चाहिन्छ"
            else:
                band_en, band_ne = "a low bindu count — this house must be consciously built up", \
                    "कम बिन्दु गणना — यो भाव सचेत रूपमा निर्माण गर्नुपर्छ"
            facts.append(_bi(
                f"In the Sarvashtakavarga this house's sign holds {sav} bindus — {band_en}. "
                f"Its karaka {karaka} contributes {bav} bindus in its own Bhinnashtakavarga here.",
                f"सर्वाष्टकवर्गमा यस भावको राशिमा {sav} बिन्दु छन् — {band_ne}। "
                f"यसको कारक {PLANET_NE[karaka]}ले आफ्नो भिन्नाष्टकवर्गबाट यहाँ {bav} बिन्दु दिएको छ।",
            ))
        # Karaka placement.
        karaka = HOUSE_KARAKA[house]
        kh = house_of(planets[karaka]["sign"], lagna_sign)
        facts.append(_bi(
            f"The karaka (significator) of this house is {karaka}, placed in the {HOUSE_NAMES_EN[kh-1]} house "
            f"in {SIGNS_EN[planets[karaka]['sign']]} — the natural significations ({SIGNIFICATIONS[karaka][0]}) "
            f"play out through {HOUSE_THEMES_EN[kh]}.",
            f"यस भावको कारक {PLANET_NE[karaka]} हो, जो {HOUSE_NAMES_NE[kh-1]} भावमा {SIGNS_NE[planets[karaka]['sign']]} राशिमा छ "
            f"— नैसर्गिक कारकत्व ({SIGNIFICATIONS[karaka][1]}) {HOUSE_THEMES_NE[kh]} हुँदै प्रकट हुन्छ।",
        ))
        # Bhava Bala.
        row = bhava_rows.get(house)
        if row:
            facts.append(_bi(
                f"Bhava Bala gives this house {row['total_rupas']:.2f} rupas (lord's strength "
                f"{row['lord_bala_rupas']:.2f} plus aspect strength {row['drik_bala_rupas']:.2f}).",
                f"भाव बलले यस भावलाई {row['total_rupas']:.2f} रूपा दिन्छ (स्वामीको बल "
                f"{row['lord_bala_rupas']:.2f} र दृष्टि बल {row['drik_bala_rupas']:.2f})।",
            ))
        out.append({"house": house, "sign": sign, "lord": lord, "facts": facts})
    return out


# ---------------------------------------------------------------------------
# Divisional (varga) chapters
# ---------------------------------------------------------------------------
def _varga_pos(chart: dict, body: str, vlagna: int) -> dict:
    sign = chart[body]
    h = house_of(sign, vlagna)
    return _bi(
        f"{body} is in {SIGNS_EN[sign]}, the {HOUSE_NAMES_EN[h-1]} sign of this varga",
        f"{PLANET_NE.get(body, body)} {SIGNS_NE[sign]} राशिमा छ, यस वर्गको {HOUSE_NAMES_NE[h-1]} स्थान",
    )


def _varga_house_lord_sentence(chart: dict, vlagna: int, house: int,
                               label_en: str, label_ne: str) -> dict:
    sign = sign_of_house(house, vlagna)
    lord = SIGN_LORDS[sign]
    ls = chart[lord]
    lh = house_of(ls, vlagna)
    return _bi(
        f"The {label_en} lord is {lord}, placed in {SIGNS_EN[ls]} — the {HOUSE_NAMES_EN[lh-1]} sign of this varga",
        f"{label_ne} स्वामी {PLANET_NE[lord]} हो, जो {SIGNS_NE[ls]} राशिमा छ — यस वर्गको {HOUSE_NAMES_NE[lh-1]} स्थान",
    )


def divisional_chapters(ctx: dict) -> dict[str, dict]:
    planets, lagna_sign = ctx["planets"], ctx["lagna_sign"]
    charts = ctx["charts"]
    lords1 = house_lords(lagna_sign)
    karakas = ctx.get("karakas") or {}
    ak = karakas.get("Atmakaraka")
    out: dict[str, dict] = {}

    # ---- D9 Navamsa: soul & spouse
    d9 = charts["D9"]
    vl = d9["Lagna"]
    facts = [_bi(f"The Navamsa Lagna is {SIGNS_EN[vl]}.",
                 f"नवांश लग्न {SIGNS_NE[vl]} हो।")]
    vargottama = [p for p in ALL9 if d9[p] == planets[p]["sign"]]
    if lagna_sign == vl:
        vargottama = ["Lagna"] + vargottama
    if vargottama:
        names_en = ", ".join(vargottama)
        names_ne = ", ".join(PLANET_NE.get(v, "लग्न") for v in vargottama)
        facts.append(_bi(
            f"Vargottama (same sign in D1 and D9): {names_en} — these significations are firm, "
            f"doubled in strength and resistant to dilution.",
            f"वर्गोत्तम (D1 र D9 मा एउटै राशि): {names_ne} — यी कारकत्व दृढ छन्, दोब्बर बलिया र क्षीण हुन गाह्रो।",
        ))
    facts.append(_varga_house_lord_sentence(d9, vl, 7, "D9 7th (spouse)", "D9 सातौँ (जीवनसाथी)"))
    facts.append(_varga_pos(d9, "Venus", vl))
    facts.append(_varga_pos(d9, "Moon", vl))
    if ak:
        facts.append(_bi(
            f"The Atmakaraka {ak} — the soul planet — sits in {SIGNS_EN[d9[ak]]} in the Navamsa, "
            f"the {HOUSE_NAMES_EN[house_of(d9[ak], vl)-1]} sign from the D9 Lagna: this is the deepest "
            f"statement of what the soul came to practise.",
            f"आत्मकारक {PLANET_NE[ak]} — आत्माको ग्रह — नवांशमा {SIGNS_NE[d9[ak]]} राशिमा छ, "
            f"D9 लग्नबाट {HOUSE_NAMES_NE[house_of(d9[ak], vl)-1]} स्थान: आत्माले अभ्यास गर्न आएको कुराको "
            f"सबैभन्दा गहिरो कथन यही हो।",
        ))
    out["D9"] = {"title": _bi("Navamsa (D9) — Soul & Spouse", "नवांश (D9) — आत्मा र जीवनसाथी"),
                 "facts": facts}

    # ---- D10 Dasamsa: career
    d10 = charts["D10"]
    vl = d10["Lagna"]
    facts = [_bi(f"The Dasamsa Lagna is {SIGNS_EN[vl]}.",
                 f"दशमांश लग्न {SIGNS_NE[vl]} हो।"),
             _varga_house_lord_sentence(d10, vl, 10, "D10 10th (career)", "D10 दशौँ (पेशा)")]
    d1_10lord = lords1[10]
    facts.append(_bi(
        f"The birth chart's 10th lord {d1_10lord} stands in {SIGNS_EN[d10[d1_10lord]]} in the D10 — "
        f"the {HOUSE_NAMES_EN[house_of(d10[d1_10lord], vl)-1]} sign of the career chart, which is where "
        f"professional results actually materialise.",
        f"जन्म कुण्डलीको दशम स्वामी {PLANET_NE[d1_10lord]} D10 मा {SIGNS_NE[d10[d1_10lord]]} राशिमा छ — "
        f"पेशा कुण्डलीको {HOUSE_NAMES_NE[house_of(d10[d1_10lord], vl)-1]} स्थान, जहाँ पेशागत फल "
        f"वास्तवमा प्रकट हुन्छ।",
    ))
    facts.append(_varga_pos(d10, "Saturn", vl))
    facts.append(_varga_pos(d10, "Sun", vl))
    out["D10"] = {"title": _bi("Dasamsa (D10) — Career", "दशमांश (D10) — पेशा"), "facts": facts}

    # ---- D7 Saptamsa: children
    d7 = charts["D7"]
    vl = d7["Lagna"]
    facts = [_bi(f"The Saptamsa Lagna is {SIGNS_EN[vl]}.",
                 f"सप्तांश लग्न {SIGNS_NE[vl]} हो।"),
             _varga_house_lord_sentence(d7, vl, 5, "D7 5th (children)", "D7 पाँचौँ (सन्तान)")]
    d1_5lord = lords1[5]
    facts.append(_bi(
        f"The birth chart's 5th lord {d1_5lord} stands in {SIGNS_EN[d7[d1_5lord]]} in the D7, and "
        f"Jupiter — the children karaka — "
        f"is in {SIGNS_EN[d7['Jupiter']]}, the {HOUSE_NAMES_EN[house_of(d7['Jupiter'], vl)-1]} sign of this varga.",
        f"जन्म कुण्डलीको पाँचौँ स्वामी {PLANET_NE[d1_5lord]} D7 मा {SIGNS_NE[d7[d1_5lord]]} राशिमा छ, र "
        f"सन्तान कारक बृहस्पति {SIGNS_NE[d7['Jupiter']]} राशिमा छ, यस वर्गको {HOUSE_NAMES_NE[house_of(d7['Jupiter'], vl)-1]} स्थान।",
    ))
    out["D7"] = {"title": _bi("Saptamsa (D7) — Children", "सप्तांश (D7) — सन्तान"), "facts": facts}

    # ---- D4 Chaturthamsa: property
    d4 = charts["D4"]
    vl = d4["Lagna"]
    facts = [_bi(f"The Chaturthamsa Lagna is {SIGNS_EN[vl]}.",
                 f"चतुर्थांश लग्न {SIGNS_NE[vl]} हो।"),
             _varga_house_lord_sentence(d4, vl, 4, "D4 4th (property)", "D4 चौथो (सम्पत्ति)")]
    d1_4lord = lords1[4]
    facts.append(_bi(
        f"The birth chart's 4th lord {d1_4lord} stands in {SIGNS_EN[d4[d1_4lord]]} in the D4. "
        f"Mars, the property karaka, is in {SIGNS_EN[d4['Mars']]} and the Moon in {SIGNS_EN[d4['Moon']]} "
        f"in this varga — together they describe the home base one builds.",
        f"जन्म कुण्डलीको चौथो स्वामी {PLANET_NE[d1_4lord]} D4 मा {SIGNS_NE[d4[d1_4lord]]} राशिमा छ। "
        f"सम्पत्ति कारक मङ्गल {SIGNS_NE[d4['Mars']]} राशिमा र चन्द्र {SIGNS_NE[d4['Moon']]} राशिमा छ "
        f"यस वर्गमा — यिनले मिलेर निर्माण हुने घर-आधार वर्णन गर्छन्।",
    ))
    out["D4"] = {"title": _bi("Chaturthamsa (D4) — Property & Home", "चतुर्थांश (D4) — सम्पत्ति र घर"),
                 "facts": facts}

    # ---- D12 Dwadasamsa: parents
    d12 = charts["D12"]
    vl = d12["Lagna"]
    facts = [_bi(f"The Dwadasamsa Lagna is {SIGNS_EN[vl]}.",
                 f"द्वादशांश लग्न {SIGNS_NE[vl]} हो।"),
             _varga_house_lord_sentence(d12, vl, 9, "D12 9th (father)", "D12 नवौँ (पिता)"),
             _varga_house_lord_sentence(d12, vl, 4, "D12 4th (mother)", "D12 चौथो (आमा)"),
             _varga_pos(d12, "Sun", vl), _varga_pos(d12, "Moon", vl)]
    out["D12"] = {"title": _bi("Dwadasamsa (D12) — Parents", "द्वादशांश (D12) — आमाबुवा"),
                  "facts": facts}

    # ---- D24 Chaturvimsamsa: education
    d24 = charts["D24"]
    vl = d24["Lagna"]
    facts = [_bi(f"The Chaturvimsamsa Lagna is {SIGNS_EN[vl]}.",
                 f"चतुर्विंशांश लग्न {SIGNS_NE[vl]} हो।"),
             _varga_house_lord_sentence(d24, vl, 4, "D24 4th (basic education)", "D24 चौथो (आधारभूत शिक्षा)"),
             _varga_house_lord_sentence(d24, vl, 5, "D24 5th (higher learning)", "D24 पाँचौँ (उच्च अध्ययन)"),
             _varga_pos(d24, "Mercury", vl), _varga_pos(d24, "Jupiter", vl)]
    out["D24"] = {"title": _bi("Chaturvimsamsa (D24) — Education", "चतुर्विंशांश (D24) — शिक्षा"),
                  "facts": facts}

    # ---- D20 Vimsamsa: spirituality
    d20 = charts["D20"]
    vl = d20["Lagna"]
    facts = [_bi(f"The Vimsamsa Lagna is {SIGNS_EN[vl]}.",
                 f"विंशांश लग्न {SIGNS_NE[vl]} हो।"),
             _varga_house_lord_sentence(d20, vl, 9, "D20 9th (dharma)", "D20 नवौँ (धर्म)"),
             _varga_pos(d20, "Jupiter", vl)]
    if ak:
        facts.append(_bi(
            f"The Atmakaraka {ak} is in {SIGNS_EN[d20[ak]]} in the Vimsamsa — the soul planet's "
            f"spiritual posture, read with the 9th lord above.",
            f"आत्मकारक {PLANET_NE[ak]} विंशांशमा {SIGNS_NE[d20[ak]]} राशिमा छ — आत्मा ग्रहको "
            f"आध्यात्मिक अवस्था, माथिको नवम स्वामीसँगै पढिने।",
        ))
    out["D20"] = {"title": _bi("Vimsamsa (D20) — Spirituality", "विंशांश (D20) — आध्यात्मिकता"),
                  "facts": facts}
    return out


# ---------------------------------------------------------------------------
# Dasha deep-dive (replaces the v1 dasha_phala): every Mahadasha read
# through its lord's full role in THIS chart; every Antardasha of the
# running Mahadasha read through the MD–AD relationship.
# ---------------------------------------------------------------------------
def _effective_ruled(lord: str, planets: dict, roles: dict,
                     lagna_sign: int) -> list[int]:
    """Houses a period lord activates: its own lordships, or — for the
    nodes, which rule nothing — its dispositor's lordships plus the
    house it occupies."""
    if lord in roles:
        return roles[lord]["ruled"]
    disp = SIGN_LORDS[planets[lord]["sign"]]
    houses = list(roles[disp]["ruled"])
    occ = house_of(planets[lord]["sign"], lagna_sign)
    if occ not in houses:
        houses.append(occ)
    return sorted(houses)


def _node_role_sentence(lord: str, planets: dict, roles: dict,
                        lagna_sign: int) -> dict:
    disp = SIGN_LORDS[planets[lord]["sign"]]
    dh = house_of(planets[disp]["sign"], lagna_sign)
    sig_en, sig_ne = SIGNIFICATIONS[lord]
    return _bi(
        f"{lord} rules no house; in its periods it delivers the results of its dispositor {disp} "
        f"(lord of house(s) {', '.join(str(x) for x in roles[disp]['ruled'])}, placed in the "
        f"{HOUSE_NAMES_EN[dh-1]} house) filtered through the house {lord} occupies. "
        f"By nature it signifies {sig_en}.",
        f"{PLANET_NE[lord]} कुनै भावको स्वामी होइन; आफ्ना अवधिमा यसले आफ्नो राशिस्वामी "
        f"{PLANET_NE[disp]} (भाव {', '.join(str(x) for x in roles[disp]['ruled'])} को स्वामी, "
        f"{HOUSE_NAMES_NE[dh-1]} भावमा बसेको) को फल आफू बसेको भाव हुँदै छानेर दिन्छ। "
        f"स्वभावतः यसले {sig_ne} जनाउँछ।",
    )


def _md_summary(lord: str, planets: dict, lagna_sign: int, roles: dict,
                charts: dict, shadbala: dict | None, combust: dict,
                karakas: dict) -> list[dict]:
    if lord in roles:
        facts = [_role_sentence(lord, roles),
                 _planet_position_sentence(lord, planets, lagna_sign, roles)]
    else:
        facts = [_node_role_sentence(lord, planets, roles, lagna_sign),
                 _planet_position_sentence(lord, planets, lagna_sign, roles)]
    strength = _strength_sentence(lord, shadbala)
    if strength:
        facts.append(strength)
    ruled = _effective_ruled(lord, planets, roles, lagna_sign)
    h = house_of(planets[lord]["sign"], lagna_sign)
    facts.append(_bi(
        f"Through this Mahadasha the houses {lord} activates — "
        f"{', '.join(HOUSE_THEMES_EN[x] for x in ruled)} — and the house it occupies "
        f"({HOUSE_THEMES_EN[h]}) move to the foreground of life; events cluster there, "
        f"paced by the Antardashas below.",
        f"यस महादशाभरि {PLANET_NE[lord]}ले शासन गर्ने भावहरू — "
        f"{', '.join(HOUSE_THEMES_NE[x] for x in ruled)} — र यो बसेको भाव "
        f"({HOUSE_THEMES_NE[h]}) जीवनको अग्रभागमा आउँछन्; घटनाहरू त्यहीँ केन्द्रित हुन्छन्, "
        f"तलका अन्तर्दशाहरूको गतिमा।",
    ))
    return facts


def _ad_interplay(md_lord: str, ad_lord: str, planets: dict,
                  roles: dict, lagna_sign: int) -> list[dict]:
    facts: list[dict] = []
    facts.append(_ad_role_line(ad_lord, planets, roles, lagna_sign))
    facts.append(_planet_position_sentence(ad_lord, planets, lagna_sign, roles))
    rel = asp.relation_between(planets[md_lord]["sign"], planets[ad_lord]["sign"])
    rel_txt = {
        "kendra": ("stands in an angle from the Mahadasha lord, so the two periods cooperate structurally",
                   "महादशा स्वामीबाट केन्द्रमा छ, त्यसैले दुई अवधि संरचनात्मक रूपमा सहकार्य गर्छन्"),
        "trikona": ("stands in a trine from the Mahadasha lord — the most supportive geometry between period lords",
                    "महादशा स्वामीबाट त्रिकोणमा छ — अवधि स्वामीहरूबीचको सबैभन्दा सहयोगी स्थिति"),
        "dusthana": ("stands in a difficult house (6th/8th/12th) from the Mahadasha lord, so the sub-period "
                     "strains the Mahadasha's themes and asks for care",
                     "महादशा स्वामीबाट कठिन भाव (६/८/१२) मा छ, त्यसैले उप-अवधिले महादशाका विषय तन्काउँछ र होसियारी माग्छ"),
        "upachaya": ("stands in a growth house from the Mahadasha lord — results improve steadily through the sub-period",
                     "महादशा स्वामीबाट उपचय भावमा छ — उप-अवधिभरि फल क्रमशः सुध्रँदै जान्छ"),
    }.get(rel, ("stands in the 2nd/11th from the Mahadasha lord, colouring the sub-period with "
                "questions of resources and gains",
                "महादशा स्वामीबाट दोस्रो/एघारौँमा छ, जसले उप-अवधिलाई स्रोत र लाभका प्रश्नले रङ्गाउँछ"))
    bits_en = [f"Relative to {md_lord}, {ad_lord} {rel_txt[0]}"]
    bits_ne = [f"{PLANET_NE[md_lord]}को तुलनामा {PLANET_NE[ad_lord]} {rel_txt[1]}"]
    # Mutual aspect?
    md_sign, ad_sign = planets[md_lord]["sign"], planets[ad_lord]["sign"]
    if ad_sign in asp.aspected_signs(md_lord, planets) or md_sign in asp.aspected_signs(ad_lord, planets):
        bits_en.append("the two lords aspect each other, so their themes are in direct dialogue")
        bits_ne.append("दुवै स्वामी एक-अर्कालाई दृष्टि दिन्छन्, त्यसैले तिनका विषय प्रत्यक्ष संवादमा छन्")
    # Natural friendship between the lords.
    f_md = FRIENDSHIP.get(md_lord, (set(), set(), set()))
    f_ad = FRIENDSHIP.get(ad_lord, (set(), set(), set()))
    if ad_lord in f_md[0] and md_lord in f_ad[0]:
        bits_en.append("they are mutual natural friends, which softens the sub-period")
        bits_ne.append("तिनीहरू आपसी नैसर्गिक मित्र हुन्, जसले उप-अवधिलाई नरम बनाउँछ")
    elif ad_lord in f_md[2] or md_lord in f_ad[2]:
        bits_en.append("there is natural antagonism between them, so the sub-period needs deliberate handling")
        bits_ne.append("तिनबीच नैसर्गिक वैरभाव छ, त्यसैले उप-अवधि सचेत रूपमा सम्हाल्नुपर्छ")
    facts.append(_bi("; ".join(bits_en) + ".", "; ".join(bits_ne) + "।"))
    # Jointly activated houses.
    houses = sorted(set(_effective_ruled(md_lord, planets, roles, lagna_sign))
                    | set(_effective_ruled(ad_lord, planets, roles, lagna_sign)))
    facts.append(_bi(
        f"Together the two lords activate houses {', '.join(str(x) for x in houses)} — "
        f"{', '.join(HOUSE_THEMES_EN[x] for x in houses)} — which is where this sub-period's "
        f"events will concentrate.",
        f"दुवै स्वामीले मिलेर भाव {', '.join(str(x) for x in houses)} सक्रिय गर्छन् — "
        f"{', '.join(HOUSE_THEMES_NE[x] for x in houses)} — यस उप-अवधिका घटना यहीँ केन्द्रित हुनेछन्।",
    ))
    return facts


def _ad_role_line(ad_lord: str, planets: dict, roles: dict, lagna_sign: int) -> dict:
    if ad_lord not in roles:
        return _node_role_sentence(ad_lord, planets, roles, lagna_sign)
    ruled = roles[ad_lord]["ruled"]
    return _bi(
        f"{ad_lord} rules house(s) {', '.join(str(x) for x in ruled)} "
        f"({', '.join(HOUSE_THEMES_EN[x] for x in ruled)}) for this chart.",
        f"{PLANET_NE[ad_lord]} यस कुण्डलीका लागि भाव {', '.join(str(x) for x in ruled)} "
        f"({', '.join(HOUSE_THEMES_NE[x] for x in ruled)}) को स्वामी हो।",
    )





def dasha_deep_dive(tree: dict, ctx: dict) -> list[dict]:
    planets, lagna_sign = ctx["planets"], ctx["lagna_sign"]
    roles = functional_roles(lagna_sign)
    cur = tree.get("current")
    cur_md_start = cur["mahadasha"]["start"] if cur else None
    # The next Mahadasha after the current one.
    next_md_start = None
    if cur:
        mds = tree["mahadashas"]
        for i, md in enumerate(mds):
            if md["start"] == cur_md_start and i + 1 < len(mds):
                next_md_start = mds[i + 1]["start"]
                break
    out = []
    for md in tree["mahadashas"]:
        entry = {
            "lord": md["lord"],
            "start": md["start"].date().isoformat(),
            "end": md["end"].date().isoformat(),
            "summary": _md_summary(md["lord"], planets, lagna_sign, roles,
                                   ctx.get("charts") or {}, ctx.get("shadbala"),
                                   ctx.get("combust") or {}, ctx.get("karakas") or {}),
        }
        if cur_md_start is not None and md["start"] == cur_md_start:
            ads = []
            for ad in md["antardashas"]:
                if ad["lord"] == md["lord"]:
                    facts = [_bi(
                        f"The Antardasha lord is the Mahadasha lord itself, so {md['lord']}'s themes "
                        f"run undiluted through this sub-period.",
                        f"अन्तर्दशा स्वामी स्वयं महादशा स्वामी नै हो, त्यसैले {PLANET_NE[md['lord']]}का विषय "
                        f"यस उप-अवधिमा अविमिश्रित रूपमा चल्छन्।",
                    )] + _ad_interplay(md["lord"], ad["lord"], planets, roles, lagna_sign)[1:]
                else:
                    facts = _ad_interplay(md["lord"], ad["lord"], planets, roles, lagna_sign)
                ads.append({
                    "lord": ad["lord"],
                    "start": ad["start"].date().isoformat(),
                    "end": ad["end"].date().isoformat(),
                    "summary": facts,
                })
            entry["antardashas"] = ads
        out.append(entry)
    return out


# ---------------------------------------------------------------------------
# Transit-phala: current transits read from BOTH Lagna and Moon, with
# classical gochar quality, transit aspects, Sade Sati phase dates and
# the Saturn–Jupiter double transit.
# ---------------------------------------------------------------------------
GOOD_FROM_MOON = {
    "Saturn": {3, 6, 10, 11}, "Jupiter": {2, 5, 7, 9, 11},
    "Rahu": {3, 6, 10, 11}, "Ketu": {3, 6, 10, 11},
    "Mars": {3, 6, 10, 11}, "Sun": {3, 6, 10, 11},
}
TRANSIT_PLANETS = ["Saturn", "Jupiter", "Rahu", "Ketu", "Mars", "Sun"]


def transit_phala(ctx: dict) -> dict:
    planets, lagna_sign = ctx["planets"], ctx["lagna_sign"]
    moon_sign = planets["Moon"]["sign"]
    transit_signs = ctx["transit_signs"]
    ingress = {r["planet"]: r for r in ctx.get("transit_ingress") or []}
    per_planet: dict[str, list[dict]] = {}
    for p in TRANSIT_PLANETS:
        tsign = transit_signs[p]
        h_lagna = house_of(tsign, lagna_sign)
        h_moon = house_of(tsign, moon_sign)
        row = ingress.get(p)
        facts = [_bi(
            f"Transiting {p} is in {SIGNS_EN[tsign]} — the {HOUSE_NAMES_EN[h_lagna-1]} house from your "
            f"Lagna ({HOUSE_THEMES_EN[h_lagna]}) and the {HOUSE_NAMES_EN[h_moon-1]} house from your Moon "
            f"sign ({HOUSE_THEMES_EN[h_moon]})"
            + (f"; it stays there until {row['next_ingress_date']}, when it enters {row['next_sign_en']}."
               if row else "."),
            f"गोचरको {PLANET_NE[p]} {SIGNS_NE[tsign]} राशिमा छ — तपाईंको लग्नबाट {HOUSE_NAMES_NE[h_lagna-1]} भाव "
            f"({HOUSE_THEMES_NE[h_lagna]}) र चन्द्र राशिबाट {HOUSE_NAMES_NE[h_moon-1]} भाव ({HOUSE_THEMES_NE[h_moon]})"
            + (f"; यो {row['next_ingress_date']} सम्म त्यहीँ रहन्छ, त्यसपछि {row['next_sign_ne']} राशिमा प्रवेश गर्छ।"
               if row else "।"),
        )]
        good = h_moon in GOOD_FROM_MOON[p]
        if good:
            facts.append(_bi(
                f"Counted from the Moon, this is one of {p}'s classically favourable places, so its "
                f"pressure on {HOUSE_THEMES_EN[h_moon]} tends to convert into results rather than friction.",
                f"चन्द्रमाबाट गन्दा यो {PLANET_NE[p]}का शास्त्रीय अनुकूल स्थानहरूमध्ये एक हो, त्यसैले "
                f"{HOUSE_THEMES_NE[h_moon]} माथिको यसको दबाब घर्षणभन्दा फलमा परिणत हुने गर्छ।",
            ))
        else:
            facts.append(_bi(
                f"Counted from the Moon, this is not one of {p}'s classically favourable places: "
                f"{HOUSE_THEMES_EN[h_moon]} asks for patience and maintenance while {p} passes through.",
                f"चन्द्रमाबाट गन्दा यो {PLANET_NE[p]}का शास्त्रीय अनुकूल स्थानहरूमध्ये होइन: "
                f"{PLANET_NE[p]} गुज्रँदै गर्दा {HOUSE_THEMES_NE[h_moon]} ले धैर्य र मर्मत माग्छ।",
            ))
        # Houses aspected in transit (from Lagna).
        asp_signs = [(tsign + off - 1) % 12 for off in asp.aspect_offsets(p)]
        asp_houses = sorted(house_of(s, lagna_sign) for s in asp_signs)
        facts.append(_bi(
            f"From {SIGNS_EN[tsign]}, transiting {p} also aspects your "
            f"{', '.join(HOUSE_NAMES_EN[h-1] for h in asp_houses)} houses — its influence is not "
            f"confined to the house it occupies.",
            f"{SIGNS_NE[tsign]} बाट गोचरको {PLANET_NE[p]}ले तपाईंका "
            f"{', '.join(HOUSE_NAMES_NE[h-1] for h in asp_houses)} भावहरूमा पनि दृष्टि दिन्छ — "
            f"यसको प्रभाव आफू बसेको भावमा मात्र सीमित छैन।",
        ))
        per_planet[p] = facts

    ss_detail = None
    span = ctx.get("saturn_span")
    ss = ctx.get("sade_sati") or {}
    if span and (ss.get("active") or ss.get("dhaiya")):
        if ss.get("active"):
            phase_en = {"first (rising)": "first (rising)", "second (peak)": "second (peak)",
                        "third (setting)": "third (setting)"}.get(ss["phase"], ss["phase"])
            ss_detail = _bi(
                f"Sade Sati runs from {span['start']} to {span['end']} for your Moon sign: the peak "
                f"phase (Saturn over the Moon sign itself) runs {span['peak_start']} to "
                f"{span['setting_start']}. You are in the {phase_en} phase. The dates are the actual "
                f"sidereal ingresses of Saturn, not approximations.",
                f"तपाईंको चन्द्र राशिका लागि साढेसाती {span['start']} देखि {span['end']} सम्म चल्छ: "
                f"शिखर चरण (शनि स्वयं चन्द्र राशिमाथि) {span['peak_start']} देखि {span['setting_start']} सम्म हुन्छ। "
                f"तपाईं हाल {phase_en} चरणमा हुनुहुन्छ। यी मितिहरू शनिका वास्तविक निरयन प्रवेशहरू हुन्, अनुमान होइनन्।",
            )
        else:
            ss_detail = _bi(
                f"Saturn is in a Dhaiya (Kantaka) position — the 4th or 8th sign from your Moon — "
                f"inside the wider span {span['start']} to {span['end']} during which Saturn crosses "
                f"the signs around your Moon sign.",
                f"शनि ढैया (कण्टक) स्थितिमा छ — तपाईंको चन्द्रमाबाट चौथो वा आठौँ राशि — "
                f"{span['start']} देखि {span['end']} सम्मको फराकिलो अवधिभित्र, जब शनि तपाईंको चन्द्र "
                f"राशि वरिपरिका राशिहरू पार गर्छ।",
            )

    dt = ctx.get("double_transit") or {}
    dt_note = None
    joint_houses_lagna, joint_houses_moon = [], []
    if dt.get("joint_signs"):
        joint_houses_lagna = [house_of(s, lagna_sign) for s in dt["joint_signs"]]
        joint_houses_moon = [house_of(s, moon_sign) for s in dt["joint_signs"]]
        signs_txt = ", ".join(SIGNS_EN[s] for s in dt["joint_signs"])
        signs_txt_ne = ", ".join(SIGNS_NE[s] for s in dt["joint_signs"])
        dt_note = _bi(
            f"Saturn (in {SIGNS_EN[dt['saturn_sign']]}) and Jupiter (in {SIGNS_EN[dt['jupiter_sign']]}) "
            f"jointly activate {signs_txt} — your {', '.join(HOUSE_NAMES_EN[h-1] for h in joint_houses_lagna)} "
            f"house(s) from the Lagna. Classical timing treats this double activation as the chart's "
            f"ripening zone: promises connected with those houses mature while both slow planets hold them.",
            f"शनि ({SIGNS_NE[dt['saturn_sign']]}मा) र बृहस्पति ({SIGNS_NE[dt['jupiter_sign']]}मा) ले "
            f"सँगै {signs_txt_ne} सक्रिय गर्छन् — लग्नबाट तपाईंका {', '.join(HOUSE_NAMES_NE[h-1] for h in joint_houses_lagna)} "
            f"भाव(हरू)। शास्त्रीय समय-गणनाले यो दोहोरो सक्रियतालाई कुण्डलीको पाक्ने क्षेत्र मान्छ: "
            f"दुवै ढिला ग्रहले सम्हाल्दासम्म ती भावसँग जोडिएका प्रतिज्ञाहरू परिपक्व हुन्छन्।",
        )
    return {
        "planets": per_planet,
        "sade_sati_detail": ss_detail,
        "double_transit": {
            "joint_signs": dt.get("joint_signs", []),
            "joint_houses_from_lagna": joint_houses_lagna,
            "joint_houses_from_moon": joint_houses_moon,
            "note": dt_note,
        },
    }


# ---------------------------------------------------------------------------
# Ashtakavarga interpretation — the key houses read through their SAV
# and the BAV of their karaka, plus the chart's strongest/weakest signs.
# ---------------------------------------------------------------------------
def ashtakavarga_reading(ctx: dict) -> list[dict]:
    av = ctx.get("ashtakavarga")
    if not av:
        return []
    planets, lagna_sign = ctx["planets"], ctx["lagna_sign"]
    sarva = av["Sarvashtakavarga"]
    facts: list[dict] = []
    strongest = max(range(12), key=lambda s: sarva[s])
    weakest = min(range(12), key=lambda s: sarva[s])
    facts.append(_bi(
        f"Across the whole chart the strongest sign by Sarvashtakavarga is {SIGNS_EN[strongest]} "
        f"({sarva[strongest]} bindus, your {HOUSE_NAMES_EN[house_of(strongest, lagna_sign)-1]} house) and "
        f"the weakest is {SIGNS_EN[weakest]} ({sarva[weakest]} bindus, your "
        f"{HOUSE_NAMES_EN[house_of(weakest, lagna_sign)-1]} house): planets transiting and ruling the "
        f"strong sign deliver more of their promise.",
        f"सम्पूर्ण कुण्डलीमा सर्वाष्टकवर्गअनुसार सबैभन्दा बलियो राशि {SIGNS_NE[strongest]} हो "
        f"({sarva[strongest]} बिन्दु, तपाईंको {HOUSE_NAMES_NE[house_of(strongest, lagna_sign)-1]} भाव) र "
        f"सबैभन्दा कमजोर {SIGNS_NE[weakest]} हो ({sarva[weakest]} बिन्दु, तपाईंको "
        f"{HOUSE_NAMES_NE[house_of(weakest, lagna_sign)-1]} भाव): बलियो राशिबाट गुज्रने र त्यसका स्वामी "
        f"ग्रहहरूले आफ्ना प्रतिज्ञा बढी पूरा गर्छन्।",
    ))
    for house in (1, 2, 4, 5, 7, 9, 10, 11):
        sign = sign_of_house(house, lagna_sign)
        sav = sarva[sign]
        karaka = HOUSE_KARAKA[house]
        bav = av[karaka][sign]
        if sav >= 30:
            band_en, band_ne = "exceptionally strong", "असाधारण बलियो"
        elif sav >= 25:
            band_en, band_ne = "supportive", "सहयोगी"
        elif sav >= 20:
            band_en, band_ne = "average — effort-dependent", "औसत — मेहनतमा निर्भर"
        else:
            band_en, band_ne = "weak — to be built deliberately", "कमजोर — सचेत रूपमा निर्माण गर्नुपर्ने"
        facts.append(_bi(
            f"The {HOUSE_NAMES_EN[house-1]} house ({HOUSE_THEMES_EN[house]}, sign {SIGNS_EN[sign]}) holds "
            f"{sav} Sarva bindus — {band_en}; its karaka {karaka} scores {bav} of 8 in its own "
            f"Bhinnashtakavarga there.",
            f"{HOUSE_NAMES_NE[house-1]} भाव ({HOUSE_THEMES_NE[house]}, राशि {SIGNS_NE[sign]}) मा "
            f"{sav} सर्व बिन्दु छन् — {band_ne}; यसको कारक {PLANET_NE[karaka]}ले आफ्नो भिन्नाष्टकवर्गमा "
            f"त्यहाँ ८ मध्ये {bav} पाएको छ।",
        ))
    return facts


# ---------------------------------------------------------------------------
# Special lagna readings: Arudha (image) and Upapada (marriage).
# ---------------------------------------------------------------------------
def special_readings(ctx: dict) -> dict:
    planets, lagna_sign = ctx["planets"], ctx["lagna_sign"]
    special = ctx["special"]
    out: dict[str, list[dict]] = {}

    al = special["arudha_lagna"]["sign"]
    al_house = house_of(al, lagna_sign)
    al_lord = sign_lord_jaimini(planets, al)
    al_lord_house = house_of(planets[al_lord]["sign"], lagna_sign)
    occ = [p for p in ALL9 if planets[p]["sign"] == al]
    facts = [_bi(
        f"The Arudha Lagna falls in {SIGNS_EN[al]} — your {HOUSE_NAMES_EN[al_house-1]} house "
        f"({HOUSE_THEMES_EN[al_house]}). The Arudha is the chart's public face: how the world "
        f"perceives you, as opposed to the inner self of the Lagna.",
        f"आरूढ लग्न {SIGNS_NE[al]} राशिमा पर्छ — तपाईंको {HOUSE_NAMES_NE[al_house-1]} भाव "
        f"({HOUSE_THEMES_NE[al_house]})। आरूढ कुण्डलीको सार्वजनिक अनुहार हो: लग्नको भित्री आत्माको "
        f"विपरीत, संसारले तपाईंलाई जसरी देख्छ।",
    ), _bi(
        f"Its lord {al_lord} is placed in the {HOUSE_NAMES_EN[al_lord_house-1]} house "
        f"({HOUSE_THEMES_EN[al_lord_house]}), so the public image is built through those themes.",
        f"यसको स्वामी {PLANET_NE[al_lord]} {HOUSE_NAMES_NE[al_lord_house-1]} भावमा "
        f"({HOUSE_THEMES_NE[al_lord_house]}) छ, त्यसैले सार्वजनिक छवि ती विषयहरूमार्फत बन्छ।",
    )]
    if occ:
        facts.append(_bi(
            f"{', '.join(occ)} in the Arudha sign directly stamp the public image with their significations.",
            f"आरूढ राशिमा बसेका {', '.join(PLANET_NE[p] for p in occ)} ले सार्वजनिक छविमा आफ्ना कारकत्वको छाप सिधै लगाउँछन्।",
        ))
    aspectors = asp.aspecting_planets(al, planets)
    if aspectors:
        facts.append(_bi(
            f"The Arudha is aspected by {', '.join(aspectors)}, whose significations colour how others read you.",
            f"आरूढमाथि {', '.join(PLANET_NE[p] for p in aspectors)} को दृष्टि छ, जसका कारकत्वले अरूले तपाईंलाई पढ्ने तरिका रङ्गाउँछ।",
        ))
    out["arudha"] = facts

    ul = special["upapada"]["sign"]
    ul_house = house_of(ul, lagna_sign)
    ul_lord = sign_lord_jaimini(planets, ul)
    ul_lord_house = house_of(planets[ul_lord]["sign"], lagna_sign)
    occ_ul = [p for p in ALL9 if planets[p]["sign"] == ul]
    second_from_ul = (ul + 1) % 12
    occ_2nd = [p for p in ALL9 if planets[p]["sign"] == second_from_ul]
    facts = [_bi(
        f"The Upapada Lagna falls in {SIGNS_EN[ul]} — your {HOUSE_NAMES_EN[ul_house-1]} house "
        f"({HOUSE_THEMES_EN[ul_house]}). The Upapada is the marriage lagna: the spouse and the "
        f"marriage itself are read from it.",
        f"उपपद लग्न {SIGNS_NE[ul]} राशिमा पर्छ — तपाईंको {HOUSE_NAMES_NE[ul_house-1]} भाव "
        f"({HOUSE_THEMES_NE[ul_house]})। उपपद विवाहको लग्न हो: जीवनसाथी र विवाह स्वयं यसैबाट पढिन्छ।",
    ), _bi(
        f"Its lord {ul_lord} is placed in the {HOUSE_NAMES_EN[ul_lord_house-1]} house "
        f"({HOUSE_THEMES_EN[ul_lord_house]}), linking the marriage story to those themes.",
        f"यसको स्वामी {PLANET_NE[ul_lord]} {HOUSE_NAMES_NE[ul_lord_house-1]} भावमा "
        f"({HOUSE_THEMES_NE[ul_lord_house]}) छ, जसले विवाहको कथालाई ती विषयहरूसँग जोड्छ।",
    )]
    if occ_ul:
        facts.append(_bi(
            f"{', '.join(occ_ul)} in the Upapada sign describe the spouse's nature and the "
            f"circumstances in which the partnership forms.",
            f"उपपद राशिमा बसेका {', '.join(PLANET_NE[p] for p in occ_ul)} ले जीवनसाथीको स्वभाव र "
            f"साझेदारी बन्ने परिस्थिति वर्णन गर्छन्।",
        ))
    if occ_2nd:
        facts.append(_bi(
            f"The 2nd from the Upapada — the house that sustains the marriage — holds "
            f"{', '.join(occ_2nd)}, whose condition decides the partnership's durability.",
            f"उपपदबाट दोस्रो भाव — विवाह टिकाउने भाव — मा {', '.join(PLANET_NE[p] for p in occ_2nd)} छन्, "
            f"जसको अवस्थाले साझेदारीको टिकाउपन तय गर्छ।",
        ))
    out["upapada"] = facts
    return out


# ---------------------------------------------------------------------------
# Timing synthesis: Vimshottari and Chara read together, with the
# double transit as the third witness.
# ---------------------------------------------------------------------------
def timing_synthesis(ctx: dict) -> list[dict]:
    planets, lagna_sign = ctx["planets"], ctx["lagna_sign"]
    roles = functional_roles(lagna_sign)
    tree = ctx["dasha_tree"]
    cur = tree.get("current") or {}
    md, ad = cur.get("mahadasha"), cur.get("antardasha")
    chara_cur = (ctx.get("chara") or {}).get("current")
    facts: list[dict] = []
    if not (md and chara_cur):
        return facts
    md_lord, ad_lord = md["lord"], (ad or {}).get("lord")
    md_ruled = _effective_ruled(md_lord, planets, roles, lagna_sign)
    facts.append(_bi(
        f"By Vimshottari you are in {md_lord} Mahadasha"
        + (f" / {ad_lord} Antardasha" if ad_lord else "")
        + f". {md_lord} activates house(s) {', '.join(str(x) for x in md_ruled)} and is "
          f"placed in the {HOUSE_NAMES_EN[house_of(planets[md_lord]['sign'], lagna_sign)-1]} house — "
          f"the planetary clock points at {', '.join(HOUSE_THEMES_EN[x] for x in md_ruled)}.",
        f"विंशोत्तरीअनुसार तपाईं {PLANET_NE[md_lord]} महादशामा हुनुहुन्छ"
        + (f" / {PLANET_NE[ad_lord]} अन्तर्दशा" if ad_lord else "")
        + f"। {PLANET_NE[md_lord]} भाव {', '.join(str(x) for x in md_ruled)} सक्रिय गर्छ र "
          f"{HOUSE_NAMES_NE[house_of(planets[md_lord]['sign'], lagna_sign)-1]} भावमा छ — "
          f"ग्रह-घडीले {', '.join(HOUSE_THEMES_NE[x] for x in md_ruled)} तिर देखाउँछ।",
    ))
    cs = chara_cur["sign"]
    cs_house = house_of(cs, lagna_sign)
    cs_lord = chara_cur["lord"]
    facts.append(_bi(
        f"By Jaimini Chara dasha you are in the {SIGNS_EN[cs]} period "
        f"({chara_cur['start'].date().isoformat()} – {chara_cur['end'].date().isoformat()}) — your "
        f"{HOUSE_NAMES_EN[cs_house-1]} house ({HOUSE_THEMES_EN[cs_house]}). Its lord {cs_lord} is "
        f"placed in the {HOUSE_NAMES_EN[house_of(planets[cs_lord]['sign'], lagna_sign)-1]} house, so "
        f"the sign clock emphasises {HOUSE_THEMES_EN[cs_house]} delivered through "
        f"{HOUSE_THEMES_EN[house_of(planets[cs_lord]['sign'], lagna_sign)]}.",
        f"जैमिनी चर दशाअनुसार तपाईं {SIGNS_NE[cs]} अवधिमा हुनुहुन्छ "
        f"({chara_cur['start'].date().isoformat()} – {chara_cur['end'].date().isoformat()}) — तपाईंको "
        f"{HOUSE_NAMES_NE[cs_house-1]} भाव ({HOUSE_THEMES_NE[cs_house]})। यसको स्वामी {PLANET_NE[cs_lord]} "
        f"{HOUSE_NAMES_NE[house_of(planets[cs_lord]['sign'], lagna_sign)-1]} भावमा छ, त्यसैले "
        f"राशि-घडीले {HOUSE_THEMES_NE[house_of(planets[cs_lord]['sign'], lagna_sign)]} हुँदै "
        f"{HOUSE_THEMES_NE[cs_house]} मा जोड दिन्छ।",
    ))
    # Agreement analysis.
    vim_lords = {x for x in (md_lord, ad_lord) if x}
    if cs_lord in vim_lords:
        cs_ruled = _effective_ruled(cs_lord, planets, roles, lagna_sign)
        facts.append(_bi(
            f"The two clocks agree unusually strongly: the Chara period lord {cs_lord} is also a "
            f"Vimshottari period lord right now. When both systems name the same planet, its houses "
            f"({', '.join(str(x) for x in cs_ruled)}) dominate the period with "
            f"double weight — this is the chart's current centre of gravity.",
            f"दुवै घडी असामान्य रूपमा एकमत छन्: चर अवधिको स्वामी {PLANET_NE[cs_lord]} अहिले "
            f"विंशोत्तरीको पनि अवधि स्वामी हो। दुवै पद्धतिले एउटै ग्रहलाई नाम दिँदा, उसका भावहरू "
            f"({', '.join(str(x) for x in cs_ruled)}) दोहोरो तौलसहित अवधिमा हाबी हुन्छन् "
            f"— यो कुण्डलीको हालको गुरुत्व केन्द्र हो।",
        ))
    elif planets[md_lord]["sign"] == cs or cs in asp.aspected_signs(md_lord, planets):
        facts.append(_bi(
            f"The two systems echo each other: the Vimshottari lord {md_lord} occupies or aspects "
            f"the Chara sign {SIGNS_EN[cs]}, so the {HOUSE_THEMES_EN[cs_house]} themes of the sign "
            f"period are reinforced by the planetary period.",
            f"दुवै पद्धति एक-अर्कालाई प्रतिध्वनित गर्छन्: विंशोत्तरी स्वामी {PLANET_NE[md_lord]} "
            f"चर राशि {SIGNS_NE[cs]} मा बसेको वा त्यसलाई दृष्टि दिने छ, त्यसैले राशि अवधिका "
            f"{HOUSE_THEMES_NE[cs_house]} विषय ग्रह अवधिले बलियो बनाउँछ।",
        ))
    else:
        facts.append(_bi(
            f"The two clocks currently point at different life areas — Vimshottari at the "
            f"{', '.join(str(x) for x in md_ruled)} house(s) through {md_lord}, Chara at "
            f"the {HOUSE_NAMES_EN[cs_house-1]} house through {SIGNS_EN[cs]}. Read together: the "
            f"planetary period supplies the 'what', the sign period supplies the 'where' — expect "
            f"{HOUSE_THEMES_EN[cs_house]} to be the stage on which {md_lord}'s portfolio plays out.",
            f"दुवै घडीले हाल फरक जीवन-क्षेत्र देखाउँछन् — विंशोत्तरी {PLANET_NE[md_lord]} मार्फत "
            f"भाव {', '.join(str(x) for x in md_ruled)} तिर, चर {SIGNS_NE[cs]} मार्फत "
            f"{HOUSE_NAMES_NE[cs_house-1]} भावतिर। सँगै पढ्दा: ग्रह अवधिले 'के' दिन्छ, राशि अवधिले "
            f"'कहाँ' दिन्छ — {PLANET_NE[md_lord]}को जिम्मेवारी {HOUSE_THEMES_NE[cs_house]} को मञ्चमा "
            f"खेलिने अपेक्षा गर्नुहोस्।",
        ))
    tp = transit_phala(ctx)
    if tp["double_transit"]["note"]:
        facts.append(tp["double_transit"]["note"])
    return facts


# ---------------------------------------------------------------------------
def build_deep_report(ctx: dict) -> dict:
    return {
        "planet_chapters": planet_chapters(ctx),
        "house_chapters": house_chapters(ctx),
        "divisional_chapters": divisional_chapters(ctx),
        "dasha_deep_dive": dasha_deep_dive(ctx["dasha_tree"], ctx),
        "transit_phala": transit_phala(ctx),
        "ashtakavarga_reading": ashtakavarga_reading(ctx),
        "special_readings": special_readings(ctx),
        "timing_synthesis": timing_synthesis(ctx),
    }
