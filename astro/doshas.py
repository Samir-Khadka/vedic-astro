"""Dosha detection: Manglik, Kaal Sarp, Sade Sati, Pitra.

Rules are deliberately the widely documented simple forms; each result
carries the rule that fired so the output never overstates its basis.
"""
from __future__ import annotations

from .charts import house_of

_MANGLIK_HOUSES_LAGNA = {1, 2, 4, 7, 8, 12}
_MANGLIK_HOUSES_MOON_VENUS = {1, 4, 7, 8, 12}

KAAL_SARP_TYPES = {
    1: "Anant", 2: "Kulik", 3: "Vasuki", 4: "Shankhpal", 5: "Padma",
    6: "Mahapadma", 7: "Takshak", 8: "Karkotak", 9: "Shankhchud",
    10: "Ghatak", 11: "Vishdhar", 12: "Sheshnag",
}


def manglik(planets: dict, lagna_sign: int) -> dict:
    mars = planets["Mars"]
    from_lagna = house_of(mars["sign"], lagna_sign) in _MANGLIK_HOUSES_LAGNA
    from_moon = house_of(mars["sign"], planets["Moon"]["sign"]) in _MANGLIK_HOUSES_MOON_VENUS
    from_venus = house_of(mars["sign"], planets["Venus"]["sign"]) in _MANGLIK_HOUSES_MOON_VENUS
    present = from_lagna or from_moon or from_venus

    cancellations = []
    if mars["sign"] in (0, 7):
        cancellations.append("Mars is in its own sign (Aries/Scorpio)")
    if mars["sign"] == 9:
        cancellations.append("Mars is exalted in Capricorn")
    if mars["sign"] in (8, 11):
        cancellations.append("Mars is in a sign of Jupiter (Sagittarius/Pisces)")
    jup = planets["Jupiter"]
    # Jupiter's special aspects fall 5th, 7th and 9th from itself.
    if (mars["sign"] - jup["sign"]) % 12 in (4, 6, 8) or mars["sign"] == jup["sign"]:
        cancellations.append("Jupiter aspects or conjoins Mars")

    strength = "none"
    if present:
        hits = sum([from_lagna, from_moon, from_venus])
        strength = "strong" if hits >= 2 else "mild"
        if cancellations:
            strength = "cancelled" if hits == 1 else "reduced"
    return {
        "present": present,
        "from_lagna": from_lagna,
        "from_moon": from_moon,
        "from_venus": from_venus,
        "strength": strength,
        "cancellations": cancellations,
    }


def kaal_sarp(planets: dict, lagna_sign: int) -> dict:
    """All seven grahas hemmed on one side of the Rahu–Ketu axis."""
    rahu = planets["Rahu"]["longitude"]
    ketu = planets["Ketu"]["longitude"]

    def side(lon: float) -> float:
        return (lon - rahu) % 360.0

    bodies = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    offsets = [side(planets[b]["longitude"]) for b in bodies]
    # Hemmed if every body lies within the Rahu->Ketu arc (0..180) or every
    # body lies within the Ketu->Rahu arc (180..360).
    all_forward = all(0.0 < o < 180.0 for o in offsets)
    all_backward = all(180.0 < o < 360.0 for o in offsets)
    present = all_forward or all_backward
    rahu_house = house_of(planets["Rahu"]["sign"], lagna_sign)
    return {
        "present": present,
        "type": KAAL_SARP_TYPES[rahu_house] if present else None,
        "rahu_house": rahu_house,
        "direction": "Rahu-to-Ketu" if all_forward else ("Ketu-to-Rahu" if all_backward else None),
    }


def sade_sati(natal_moon_sign: int, transit_saturn_sign: int) -> dict:
    rel = (transit_saturn_sign - natal_moon_sign) % 12  # 0 = over Moon sign
    if rel == 11:
        phase, active = "first (rising)", True
    elif rel == 0:
        phase, active = "second (peak)", True
    elif rel == 1:
        phase, active = "third (setting)", True
    else:
        phase, active = None, False
    dhaiya = rel in (3, 7)  # Saturn 4th or 8th from Moon: Kantaka / Ashtama
    return {
        "active": active,
        "phase": phase,
        "dhaiya": dhaiya,
        "saturn_sign": transit_saturn_sign,
        "moon_sign": natal_moon_sign,
    }


def pitra(planets: dict, lagna_sign: int) -> dict:
    """Simple documented Pitra patterns (9th house / Sun afflictions)."""
    patterns = []
    house9_sign = (lagna_sign + 8) % 12
    sun, rahu, ketu = planets["Sun"], planets["Rahu"], planets["Ketu"]
    if rahu["sign"] == house9_sign or ketu["sign"] == house9_sign:
        patterns.append("Rahu/Ketu placed in the 9th house of father and dharma")
    same_sign_nodes = sun["sign"] in (rahu["sign"], ketu["sign"])
    if same_sign_nodes:
        patterns.append("Sun conjoins Rahu/Ketu (eclipse affliction to the father significator)")
    ninth_lord_sign = None
    from .names import SIGN_LORDS
    ninth_lord = SIGN_LORDS[house9_sign]
    if planets[ninth_lord]["sign"] in (rahu["sign"], ketu["sign"]):
        patterns.append("The 9th lord conjoins Rahu/Ketu")
        ninth_lord_sign = planets[ninth_lord]["sign"]
    return {"present": len(patterns) > 0, "patterns": patterns}
