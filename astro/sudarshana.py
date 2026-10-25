"""Sudarshana Chakra — Lagna + Moon + Sun rings of the D1 chart.

The classical Sudarshana Chakra reads the same chart three times: once
from the Lagna, once from the Moon sign (Chandra Lagna) and once from
the Sun sign (Surya Lagna). A planet's house is counted from each of
the three reference signs. When a planet occupies the same relative
house in two or three rings, the classical reading is that its results
are confirmed and repeat through life; when the three rings disagree
sharply, the planet's results vary by domain (self / mind / soul).

This is the Lagna+Moon+Sun concentric form (not a D1+D9 composite,
which some modern tools also label "Sudarshana" — that composite is
a different view and is not what this module computes).
"""
from __future__ import annotations

from .charts import house_of


def sudarshana(planets: dict, lagna_sign: int) -> dict:
    """Per-planet houses in the three rings + confirmation list."""
    moon_sign = planets["Moon"]["sign"]
    sun_sign = planets["Sun"]["sign"]
    rings = {"lagna": lagna_sign, "moon": moon_sign, "sun": sun_sign}
    per_planet: dict[str, dict] = {}
    confirmed: list[dict] = []
    for name, p in planets.items():
        h_lagna = house_of(p["sign"], lagna_sign)
        h_moon = house_of(p["sign"], moon_sign)
        h_sun = house_of(p["sign"], sun_sign)
        agree = len({h_lagna, h_moon, h_sun})
        level = "triple" if agree == 1 else "double" if agree == 2 else "varied"
        per_planet[name] = {
            "sign": p["sign"], "lagna_house": h_lagna,
            "moon_house": h_moon, "sun_house": h_sun, "agreement": level,
        }
        if level in ("triple", "double"):
            # The repeated house value (mode of the three).
            vals = [h_lagna, h_moon, h_sun]
            repeated = max(set(vals), key=vals.count)
            confirmed.append({"planet": name, "house": repeated, "level": level})
    return {
        "rings": rings,
        "planets": per_planet,
        "confirmed": confirmed,
    }
