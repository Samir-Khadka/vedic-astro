"""Jaimini Argala — planetary intervention on each house.

Classical rules implemented (our own wording):

* A planet gives ARGALA (support, intervention) to a house when it
  stands in the 2nd, 4th or 11th house counted from that house.
  Planets in the 12th, 10th or 3rd house from it give VIRODHARGALA
  (obstruction) instead.
* Extended rule: planets in the 5th from a house also give Argala,
  and planets in the 9th from it obstruct that 5th-house Argala.
* Ketu reversal: Ketu's intervention is counted backwards — Ketu in
  the 12th, 10th or 3rd from a house gives Argala, Ketu in the 2nd,
  4th or 11th obstructs, and Ketu in the 9th gives the extended
  Argala (obstructed by the 5th). Rahu is NOT reversed.
* Three-or-more malefics in the 3rd from a house turn that 3rd-house
  placement from obstruction into a (malefic) Argala.
* Strength comparison: Argala prevails when the supporting planets
  outnumber the obstructing ones; otherwise the house is obstructed.
  A house with neither is simply un-aspected by Argala.

Houses are whole-sign houses counted from the Lagna, consistent
with the rest of the engine.
"""
from __future__ import annotations

from .charts import house_of
from .names import HOUSE_THEMES_EN, HOUSE_THEMES_NE, PLANET_NE

MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}
PLANETS_9 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

_ARGALA = {2, 4, 11}
_VIRODH = {12, 10, 3}


def _bi(en: str, ne: str) -> dict:
    return {"en": en, "ne": ne}


def argala_for_house(house: int, planet_houses: dict[str, int]) -> dict:
    """Argala analysis for one house (1..12 from Lagna).

    `planet_houses`: planet -> house number (1..12) from Lagna.
    """
    argala: list[dict] = []
    virodh: list[dict] = []

    def offset(planet: str) -> int:
        return (planet_houses[planet] - house) % 12 + 1

    for planet in PLANETS_9:
        if planet not in planet_houses:
            continue
        off = offset(planet)
        if planet == "Ketu":
            # Reversed: 12/10/3 support, 2/4/11 obstruct, 9 extends.
            if off in _VIRODH:
                argala.append({"planet": planet, "from_house": off, "ketu_reversed": True})
            elif off in _ARGALA:
                virodh.append({"planet": planet, "from_house": off, "ketu_reversed": True})
            elif off == 9:
                argala.append({"planet": planet, "from_house": off, "ketu_reversed": True, "extended": True})
            elif off == 5:
                virodh.append({"planet": planet, "from_house": off, "ketu_reversed": True, "extended": True})
        else:
            if off in _ARGALA:
                argala.append({"planet": planet, "from_house": off})
            elif off in _VIRODH:
                virodh.append({"planet": planet, "from_house": off})
            elif off == 5:
                argala.append({"planet": planet, "from_house": off, "extended": True})
            elif off == 9:
                virodh.append({"planet": planet, "from_house": off, "extended": True})

    # Three-or-more malefics in the 3rd from the house: malefic Argala.
    third_malefics = [v for v in virodh
                      if v["from_house"] == 3 and v["planet"] in MALEFICS
                      and not v.get("ketu_reversed")]
    malefic_argala = False
    if len(third_malefics) >= 3:
        malefic_argala = True
        for v in third_malefics:
            virodh.remove(v)
            argala.append({**v, "malefic_argala": True})

    if argala and len(argala) > len(virodh):
        verdict = "argala"
    elif virodh:
        # Obstruction holds when obstructers match or outnumber supporters.
        verdict = "obstructed"
    else:
        verdict = "none"

    def _names(rows: list[dict]) -> list[str]:
        return [r["planet"] for r in rows]

    theme_en, theme_ne = HOUSE_THEMES_EN[house], HOUSE_THEMES_NE[house]
    if verdict == "argala":
        reading = _bi(
            f"Argala prevails for the {house}th house ({theme_en}): {', '.join(_names(argala))} intervene in its favour.",
            f"{house}औँ भाव ({theme_ne}) का लागि अर्गला प्रबल छ: {', '.join(_names(argala))} ले यसको पक्षमा हस्तक्षेप गर्छन्।")
    elif verdict == "obstructed":
        reading = _bi(
            f"The {house}th house ({theme_en}) is obstructed: {', '.join(_names(virodh))} stand against its Argala.",
            f"{house}औँ भाव ({theme_ne}) अवरुद्ध छ: {', '.join(_names(virodh))} यसको अर्गलाको विरुद्धमा उभिएका छन्।")
    else:
        reading = _bi(
            f"No Argala or obstruction touches the {house}th house ({theme_en}).",
            f"{house}औँ भाव ({theme_ne}) मा कुनै अर्गला वा अवरोध छैन।")
    return {
        "house": house,
        "theme": _bi(theme_en, theme_ne),
        "argala": argala, "virodhargala": virodh,
        "malefic_argala_in_3rd": malefic_argala,
        "verdict": verdict,
        "reading": reading,
    }


def argala_full(planets: dict, lagna_sign: int) -> dict:
    """Argala for all 12 houses + the per-planet view.

    `planets`: ephemeris dict (needs sign per planet).
    """
    planet_houses = {p: house_of(planets[p]["sign"], lagna_sign)
                     for p in PLANETS_9 if p in planets}
    by_house = [argala_for_house(h, planet_houses) for h in range(1, 13)]
    by_planet: dict[str, dict] = {}
    for planet in PLANETS_9:
        if planet not in planet_houses:
            continue
        supports, obstructs = [], []
        for row in by_house:
            if any(r["planet"] == planet for r in row["argala"]):
                supports.append(row["house"])
            if any(r["planet"] == planet for r in row["virodhargala"]):
                obstructs.append(row["house"])
        by_planet[planet] = {
            "planet_ne": PLANET_NE[planet],
            "house": planet_houses[planet],
            "argala_to_houses": supports,
            "obstructs_houses": obstructs,
        }
    prevailing = sum(1 for r in by_house if r["verdict"] == "argala")
    obstructed = sum(1 for r in by_house if r["verdict"] == "obstructed")
    return {
        "by_house": by_house,
        "by_planet": by_planet,
        "prevailing_count": prevailing,
        "obstructed_count": obstructed,
        "method_note": _bi(
            "Argala from the 2nd/4th/11th (5th extended); obstruction from the 12th/10th/3rd (9th against the 5th); Ketu reversed; 3+ malefics in the 3rd give malefic Argala.",
            "दोस्रो/चौथो/एघारौँबाट अर्गला (पाँचौँ विस्तारित); बाह्रौँ/दशौँ/तेस्रोबाट विरोधर्गला (पाँचौँविरुद्ध नवौँ); केतु उल्टो; तेस्रोमा ३+ पापग्रहले पाप अर्गला दिन्छन्।"),
    }
