"""Divisional (varga) charts and chart-fact helpers.

The varga formulas implemented here are the standard Parashari ones.
D1/D9/D10 are the workhorses and are exact; the remaining vargas use the
widely published BPHS counting rules.
"""
from __future__ import annotations

from .names import (
    COMBUSTION_ORB, EXALTATION, OWN_SIGNS, SIGN_LORDS,
)

VARGAS = ["D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12", "D16", "D20", "D24", "D27", "D30", "D60"]


def _navamsa(sign: int, deg: float) -> int:
    part = int(deg // (30.0 / 9.0))
    if sign % 3 == 0:        # movable: count from the sign itself
        start = sign
    elif sign % 3 == 1:      # fixed: count from the 9th sign
        start = (sign + 8) % 12
    else:                    # dual: count from the 5th sign
        start = (sign + 4) % 12
    return (start + part) % 12


def varga_sign(varga: str, sign: int, deg: float) -> int:
    """Sign (0..11) occupied in divisional chart `varga` for a body at
    `deg` degrees inside natal `sign`."""
    if varga == "D1":
        return sign
    if varga == "D2":  # Hora: halves -> Cancer (3) / Leo (4)
        first_half = deg < 15.0
        if sign % 2 == 0:  # odd sign: 1st half Leo, 2nd half Cancer
            return 4 if first_half else 3
        return 3 if first_half else 4
    if varga == "D3":  # Drekkana
        return (sign + 4 * int(deg // 10.0)) % 12
    if varga == "D4":  # Chaturthamsa
        return (sign + 3 * int(deg // 7.5)) % 12
    if varga == "D7":  # Saptamsa
        part = int(deg // (30.0 / 7.0))
        start = sign if sign % 2 == 0 else (sign + 6) % 12
        return (start + part) % 12
    if varga == "D9":
        return _navamsa(sign, deg)
    if varga == "D10":  # Dasamsa
        part = int(deg // 3.0)
        start = sign if sign % 2 == 0 else (sign + 8) % 12
        return (start + part) % 12
    if varga == "D12":  # Dwadasamsa
        return (sign + int(deg // 2.5)) % 12
    if varga == "D16":  # Shodasamsa
        part = int(deg // (30.0 / 16.0))
        start = {0: 0, 1: 4, 2: 8}[sign % 3]  # movable Aries, fixed Leo, dual Sagittarius
        return (start + part) % 12
    if varga == "D20":  # Vimsamsa
        part = int(deg // 1.5)
        start = {0: 0, 1: 8, 2: 4}[sign % 3]  # movable Aries, fixed Sagittarius, dual Leo
        return (start + part) % 12
    if varga == "D24":  # Chaturvimsamsa
        part = int(deg // 1.25)
        start = 4 if sign % 2 == 0 else 3  # odd signs from Leo, even from Cancer
        return (start + part) % 12
    if varga == "D27":  # Bhamsa / Nakshatramsa
        part = int(deg // (30.0 / 27.0))
        start = {0: 0, 1: 3, 2: 6, 3: 9}[sign % 4]  # fire Aries, earth Cancer, air Libra, water Capricorn
        return (start + part) % 12
    if varga == "D30":  # Trimsamsa — unequal Parashari divisions
        if sign % 2 == 0:  # odd sign
            if deg < 5: return 0
            if deg < 10: return 10
            if deg < 18: return 8
            if deg < 25: return 2
            return 6
        if deg < 5: return 1
        if deg < 12: return 5
        if deg < 20: return 11
        if deg < 25: return 9
        return 7
    if varga == "D60":  # Shashtiamsa
        return (sign + int(deg // 0.5)) % 12
    raise ValueError(f"unknown varga {varga}")


def build_chart(planets: dict, lagna_lon: float, varga: str) -> dict:
    """Return {body: sign} for one varga, plus 'Lagna'."""
    lagna_sign = int(lagna_lon // 30.0)
    lagna_deg = lagna_lon % 30.0
    chart = {"Lagna": varga_sign(varga, lagna_sign, lagna_deg)}
    for name, p in planets.items():
        chart[name] = varga_sign(varga, p["sign"], p["degree_in_sign"])
    return chart


def house_of(sign: int, lagna_sign: int) -> int:
    """Whole-sign house (1..12) of a sign counted from the Lagna sign."""
    return (sign - lagna_sign) % 12 + 1


def sign_of_house(house: int, lagna_sign: int) -> int:
    return (lagna_sign + house - 1) % 12


def house_lords(lagna_sign: int) -> dict[int, str]:
    """{house: ruling planet} for whole-sign houses from Lagna."""
    return {h: SIGN_LORDS[sign_of_house(h, lagna_sign)] for h in range(1, 13)}


def dignity(planet: str, sign: int) -> str:
    """exalted / debilitated / own / moolatrikona-adjacent / neutral."""
    if planet in EXALTATION:
        ex_sign = EXALTATION[planet][0]
        if sign == ex_sign:
            return "exalted"
        if sign == (ex_sign + 6) % 12:
            return "debilitated"
    if planet in OWN_SIGNS and sign in OWN_SIGNS[planet]:
        return "own"
    return "neutral"


def angular_distance(a: float, b: float) -> float:
    d = abs((a - b) % 360.0)
    return min(d, 360.0 - d)


def combustions(planets: dict) -> dict[str, bool]:
    """{planet: True if combust} for the six star-planets + nodes False."""
    sun_lon = planets["Sun"]["longitude"]
    out = {}
    for name, orb in COMBUSTION_ORB.items():
        out[name] = angular_distance(planets[name]["longitude"], sun_lon) <= orb
    return out


def jaimini_karakas(planets: dict) -> dict[str, str]:
    """Chara karakas (7-planet scheme) by degree-in-sign, descending.
    Returns {karaka name: planet}."""
    names = [
        "Atmakaraka", "Amatyakaraka", "Bhratrikaraka", "Matrikaraka",
        "Putrakaraka", "Gnatikaraka", "Darakaraka",
    ]
    ordered = sorted(
        ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"),
        key=lambda p: planets[p]["degree_in_sign"],
        reverse=True,
    )
    return {names[i]: ordered[i] for i in range(7)}
