"""Structured interpretation report built ONLY from computed chart facts:
dasha lords' lordship/placement/dignity, strong & weak planets, slow-planet
transits from the Moon sign, and house-lord based thematic sections.
Every sentence is emitted in English and Nepali.
"""
from __future__ import annotations

from .charts import dignity, house_lords, house_of
from .names import (
    HOUSE_NAMES_EN, HOUSE_NAMES_NE, HOUSE_THEMES_EN, HOUSE_THEMES_NE,
    NATURAL_BENEFICS, NATURAL_MALEFICS, PLANET_NE, SIGNS_EN, SIGNS_NE,
)


def _bi(en: str, ne: str) -> dict:
    return {"en": en, "ne": ne}


def _placement_fact(planet: str, planets: dict, lagna_sign: int, lords: dict) -> dict:
    """One bilingual factual statement about a planet's placement+lordship."""
    p = planets[planet]
    h = house_of(p["sign"], lagna_sign)
    ruled = [hh for hh, lp in lords.items() if lp == planet]
    dig = dignity(planet, p["sign"])
    en_bits, ne_bits = [], []
    if ruled:
        en_bits.append(
            f"{planet} rules your " + " and ".join(f"{HOUSE_NAMES_EN[x-1]} house" for x in ruled)
        )
        ne_bits.append(
            f"{PLANET_NE[planet]} तपाईंको " + " र ".join(f"{HOUSE_NAMES_NE[x-1]} भाव" for x in ruled) + "को स्वामी हो"
        )
    en_bits.append(f"it is placed in the {HOUSE_NAMES_EN[h-1]} house ({HOUSE_THEMES_EN[h]}) in {SIGNS_EN[p['sign']]}")
    ne_bits.append(f"यो {HOUSE_NAMES_NE[h-1]} भावमा ({HOUSE_THEMES_NE[h]}) {SIGNS_NE[p['sign']]} राशिमा बसेको छ")
    if dig == "exalted":
        en_bits.append("it is exalted, which strengthens its results")
        ne_bits.append("यो उच्च राशिमा छ, जसले यसको फल बलियो बनाउँछ")
    elif dig == "debilitated":
        en_bits.append("it is debilitated, which weakens and delays its results")
        ne_bits.append("यो नीच राशिमा छ, जसले यसको फल कमजोर र ढिलो बनाउँछ")
    elif dig == "own":
        en_bits.append("it sits in its own sign, giving steady, self-reliant results")
        ne_bits.append("यो आफ्नै राशिमा छ, जसले स्थिर र आत्मनिर्भर फल दिन्छ")
    return _bi("; ".join(en_bits) + ".", "; ".join(ne_bits) + "।")


def generate_predictions(ctx: dict) -> dict:
    planets = ctx["planets"]
    lagna_sign = ctx["lagna_sign"]
    lords = house_lords(lagna_sign)
    combust = ctx["combust"]
    dasha = ctx["dasha"]
    d9 = ctx["charts"]["D9"]

    sections: dict[str, list[dict]] = {}

    # ---- Current dasha period ------------------------------------------------
    cur = dasha.get("current")
    period_facts: list[dict] = []
    if cur and cur.get("antardasha"):
        md, ad = cur["mahadasha"], cur["antardasha"]
        period_facts.append(_bi(
            f"You are running {md['lord']} Mahadasha and {ad['lord']} Antardasha "
            f"(Antardasha until {ad['end'].date().isoformat()}).",
            f"हाल तपाईंको {PLANET_NE[md['lord']]} महादशा र {PLANET_NE[ad['lord']]} अन्तर्दशा "
            f"चलिरहेको छ (अन्तर्दशा {ad['end'].date().isoformat()} सम्म)।",
        ))
        period_facts.append(_placement_fact(md["lord"], planets, lagna_sign, lords))
        if ad["lord"] != md["lord"]:
            period_facts.append(_placement_fact(ad["lord"], planets, lagna_sign, lords))
        for lord in {md["lord"], ad["lord"]}:
            nature = "benefic" if lord in NATURAL_BENEFICS else ("malefic" if lord in NATURAL_MALEFICS else "neutral")
            if nature == "benefic":
                period_facts.append(_bi(
                    f"{lord} is a natural benefic, so this period tends to bring support and growth when its house themes are pursued sincerely.",
                    f"{PLANET_NE[lord]} नैसर्गिक शुभ ग्रह हो, त्यसैले यसको भाव-विषयमा इमानदारीपूर्वक लाग्दा यो अवधिले साथ र प्रगति दिने गर्छ।",
                ))
            elif nature == "malefic":
                period_facts.append(_bi(
                    f"{lord} is a natural malefic, so this period rewards discipline and patience; avoid shortcuts in its house themes.",
                    f"{PLANET_NE[lord]} नैसर्गिक पाप ग्रह हो, त्यसैले यो अवधिले अनुशासन र धैर्यलाई फल दिन्छ; यसका भाव-विषयमा छोटो बाटो नलिनुहोस्।",
                ))
    sections["current_period"] = period_facts

    # ---- Strong & weak planets ----------------------------------------------
    strength_facts: list[dict] = []
    for name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        p = planets[name]
        dig = dignity(name, p["sign"])
        vargottama = d9.get(name) == p["sign"]
        if dig in ("exalted", "own") or vargottama:
            why_en = "exalted" if dig == "exalted" else ("in its own sign" if dig == "own" else "vargottama (same sign in D1 and Navamsa)")
            why_ne = "उच्च राशिमा" if dig == "exalted" else ("आफ्नै राशिमा" if dig == "own" else "वर्गोत्तम (लग्न र नवांश दुवैमा एउटै राशि)")
            strength_facts.append(_bi(
                f"{name} is a source of strength in this chart — {why_en}.",
                f"{PLANET_NE[name]} यस कुण्डलीको बलियो पक्ष हो — {why_ne}।",
            ))
        if dig == "debilitated":
            strength_facts.append(_bi(
                f"{name} is debilitated in {SIGNS_EN[p['sign']]}; its significations need conscious effort and remedies of patience.",
                f"{PLANET_NE[name]} {SIGNS_NE[p['sign']]} राशिमा नीच छ; यसका विषयमा सचेत प्रयास र धैर्य आवश्यक छ।",
            ))
        if combust.get(name):
            strength_facts.append(_bi(
                f"{name} is combust (close to the Sun), so its results can feel overshadowed early in life and improve with maturity.",
                f"{PLANET_NE[name]} अस्त छ (सूर्यको नजिक), त्यसैले यसको फल सुरुमा ओझेलमा पर्न सक्छ र उमेरसँगै सुध्रँदै जान्छ।",
            ))
    sections["strengths"] = strength_facts

    # ---- Transits (gochar) from the Moon sign --------------------------------
    moon_sign = planets["Moon"]["sign"]
    transit_facts: list[dict] = []
    for tp in ("Saturn", "Jupiter", "Rahu"):
        tsign = ctx["transit_signs"][tp]
        rel = (tsign - moon_sign) % 12 + 1
        good = rel in (3, 6, 10, 11) if tp == "Saturn" else (rel in (2, 5, 7, 9, 11) if tp == "Jupiter" else rel in (3, 6, 10, 11))
        tone_en = "generally supportive" if good else "demanding of extra effort"
        tone_ne = "सामान्यतया सहयोगी" if good else "थप मेहनत माग्ने"
        transit_facts.append(_bi(
            f"Transiting {tp} is in {SIGNS_EN[tsign]}, the {HOUSE_NAMES_EN[rel-1]} sign from your Moon sign — a {tone_en} transit.",
            f"गोचरको {PLANET_NE[tp]} {SIGNS_NE[tsign]} राशिमा छ, जुन तपाईंको चन्द्र राशिबाट {HOUSE_NAMES_NE[rel-1]} स्थान हो — यो {tone_ne} गोचर हो।",
        ))
    ss = ctx["sade_sati"]
    if ss["active"]:
        transit_facts.append(_bi(
            f"You are currently in Saturn Sade Sati ({ss['phase']} phase): a period of karmic review around the Moon sign.",
            f"हाल तपाईं शनि साढेसातीको अवधिमा हुनुहुन्छ ({ss['phase']} चरण): चन्द्र राशिको वरिपरि कर्मको पुनरावलोकन हुने समय।",
        ))
    sections["transits"] = transit_facts

    # ---- Thematic sections from house lords -----------------------------------
    def theme(house_nums: list[int], extra_planets: list[str]) -> list[dict]:
        facts: list[dict] = []
        seen = set()
        for h in house_nums:
            lord = lords[h]
            if lord not in seen:
                facts.append(_placement_fact(lord, planets, lagna_sign, lords))
                seen.add(lord)
        for p in extra_planets:
            h = house_of(planets[p]["sign"], lagna_sign)
            facts.append(_bi(
                f"{p} occupies the {HOUSE_NAMES_EN[h-1]} house in {SIGNS_EN[planets[p]['sign']]}, directly influencing this area of life.",
                f"{PLANET_NE[p]} {HOUSE_NAMES_NE[h-1]} भावमा {SIGNS_NE[planets[p]['sign']]} राशिमा बसेको छ, जसले जीवनको यस क्षेत्रलाई प्रत्यक्ष प्रभावित गर्छ।",
            ))
        return facts

    occupants10 = [n for n, p in planets.items() if house_of(p["sign"], lagna_sign) == 10]
    occupants7 = [n for n, p in planets.items() if house_of(p["sign"], lagna_sign) == 7]
    sections["career"] = theme([10], occupants10)
    sections["wealth"] = theme([2, 11], [])
    sections["relationships"] = theme([7], occupants7)
    sections["health"] = theme([1, 6, 8], [])

    return sections


# ---------------------------------------------------------------------------
# Dasha-phala — an interpretation for every Mahadasha, and for every
# Antardasha of the currently running Mahadasha, built from the same
# placement facts as the rest of the report.
# ---------------------------------------------------------------------------
def _nature_line(lord: str) -> dict:
    if lord in NATURAL_BENEFICS:
        return _bi(
            f"As a natural benefic, {lord}'s periods tend to support growth, goodwill and steady gains when pursued sincerely.",
            f"नैसर्गिक शुभ ग्रहका रूपमा, {PLANET_NE[lord]}को अवधिले इमानदारीपूर्वक लाग्दा प्रगति, सद्भाव र स्थिर लाभलाई साथ दिन्छ।",
        )
    if lord in NATURAL_MALEFICS:
        return _bi(
            f"As a natural malefic, {lord}'s periods test discipline and patience; results come through sustained effort rather than shortcuts.",
            f"नैसर्गिक पाप ग्रहका रूपमा, {PLANET_NE[lord]}को अवधिले अनुशासन र धैर्यको परीक्षा लिन्छ; फल छोटो बाटोभन्दा निरन्तर मेहनतबाट आउँछ।",
        )
    return _bi(
        f"{lord}'s periods are mixed in tone and take their colour from the planets it is joined with and aspected by.",
        f"{PLANET_NE[lord]}को अवधि मिश्रित हुन्छ र यसले सँगै बसेका तथा दृष्टि दिने ग्रहहरूको रङ लिन्छ।",
    )


def dasha_phala(tree: dict, planets: dict, lagna_sign: int) -> list[dict]:
    lords = house_lords(lagna_sign)
    cur = tree.get("current")
    cur_md_start = cur["mahadasha"]["start"] if cur else None
    out = []
    for md in tree["mahadashas"]:
        entry = {
            "lord": md["lord"],
            "start": md["start"].date().isoformat(),
            "end": md["end"].date().isoformat(),
            "summary": [
                _placement_fact(md["lord"], planets, lagna_sign, lords),
                _nature_line(md["lord"]),
            ],
        }
        if cur_md_start is not None and md["start"] == cur_md_start:
            ads = []
            for ad in md["antardashas"]:
                facts = [_placement_fact(ad["lord"], planets, lagna_sign, lords)]
                if ad["lord"] == md["lord"]:
                    facts.append(_bi(
                        f"The Antardasha lord is the same as the Mahadasha lord, so the themes of {md['lord']} run undiluted through this sub-period.",
                        f"अन्तर्दशा स्वामी र महादशा स्वामी एउटै भएकाले {PLANET_NE[md['lord']]}का विषय यस उप-अवधिमा अविरल रूपमा चल्छन्।",
                    ))
                else:
                    facts.append(_nature_line(ad["lord"]))
                ads.append({
                    "lord": ad["lord"],
                    "start": ad["start"].date().isoformat(),
                    "end": ad["end"].date().isoformat(),
                    "summary": facts,
                })
            entry["antardashas"] = ads
        out.append(entry)
    return out
