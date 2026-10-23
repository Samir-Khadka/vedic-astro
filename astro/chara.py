"""Jaimini Chara dasha — the sign dasha, K. N. Rao's method.

Rules (as published by K. N. Rao and implemented in Jagannatha Hora;
cross-verified 2026-10-23 against PyJHora's KN Rao implementation and
its built-in published example — Chennai, 1996-12-07 10:34, durations
10/12/4/12/9/9/9/6/5/4/3/11 for Capricorn..Aquarius, reproduced exactly
by the test-suite golden):

* Sequence starts at the Lagna sign and runs zodiacally, UNLESS the
  9th sign from the Lagna is an even-footed (samapada) sign — Cancer,
  Leo, Virgo, Capricorn, Aquarius, Pisces — in which case it runs
  anti-zodiacally.
* Duration of a sign = inclusive zodiacal count between the sign and
  its lord, minus 1 (a count of 1 gives 12 years). The count runs from
  the sign to the lord for odd-footed (vishamapada) signs — Aries,
  Taurus, Gemini, Libra, Scorpio, Sagittarius — and from the lord to
  the sign for even-footed signs. Scorpio and Aquarius use the
  stronger of their two Jaimini co-lords (see jaimini.stronger_co_lord).
* Add 1 year when the lord is exalted in its placed sign, subtract 1
  when it is debilitated (Rao's sutra-based adjustment).
* Periods run in whole years from the birth moment; the app-wide
  365.25-day year is used (PyJHora's sidereal-year option shifts start
  dates by a few days per decade; durations are identical).
* Antardashas of the running period divide it into 12 equal parts in
  the same sign order as the main sequence (the KN Rao convention).
"""
from __future__ import annotations

from datetime import datetime

from .charts import dignity
from .dasha import _days
from .jaimini import sign_lord_jaimini
from .names import SIGNS_EN, SIGNS_NE

EVEN_FOOTED = {3, 4, 5, 9, 10, 11}   # samapada signs
ODD_FOOTED = {0, 1, 2, 6, 7, 8}      # vishamapada signs


def _count_rasis(a: int, b: int) -> int:
    return (b - a) % 12 + 1


def chara_duration(planets: dict, sign: int) -> int:
    """Years of one sign's Chara period for this chart (KN Rao rules)."""
    lord = sign_lord_jaimini(planets, sign)
    lord_sign = planets[lord]["sign"]
    if sign in EVEN_FOOTED:
        count = _count_rasis(lord_sign, sign)
    else:
        count = _count_rasis(sign, lord_sign)
    years = count - 1
    if years <= 0:
        years = 12
    d = dignity(lord, lord_sign)
    if d == "exalted":
        years += 1
    elif d == "debilitated":
        years -= 1
    return years


def chara_sequence(lagna_sign: int) -> tuple[list[int], bool]:
    """The 12 signs in dasha order, and whether the sequence is forward."""
    ninth = (lagna_sign + 8) % 12
    forward = ninth not in EVEN_FOOTED
    if forward:
        return [(lagna_sign + i) % 12 for i in range(12)], True
    return [(lagna_sign - i) % 12 for i in range(12)], False


def chara_periods(birth_dt: datetime, planets: dict, lagna_sign: int,
                  now: datetime | None = None, cycles: int = 2) -> dict:
    seq, forward = chara_sequence(lagna_sign)
    periods = []
    cursor = birth_dt
    for _ in range(cycles):
        for sign in seq:
            years = chara_duration(planets, sign)
            end = cursor + _days(float(years))
            periods.append({
                "sign": sign,
                "sign_en": SIGNS_EN[sign], "sign_ne": SIGNS_NE[sign],
                "lord": sign_lord_jaimini(planets, sign),
                "start": cursor, "end": end, "years": years,
            })
            cursor = end
    at = now or datetime.now(birth_dt.tzinfo)
    current = next((p for p in periods if p["start"] <= at < p["end"]), None)

    antardashas = []
    if current is not None:
        step = (current["end"] - current["start"]) / 12
        a_cursor = current["start"]
        for k in range(12):
            # Bhuktis begin at the period sign itself and follow the
            # main sequence direction (KN Rao convention).
            s = (current["sign"] + k) % 12 if forward else (current["sign"] - k) % 12
            a_end = a_cursor + step
            antardashas.append({
                "sign": s, "sign_en": SIGNS_EN[s], "sign_ne": SIGNS_NE[s],
                "start": a_cursor, "end": a_end,
            })
            a_cursor = a_end
    return {
        "direction": "forward" if forward else "reverse",
        "periods": periods,
        "current": current,
        "current_antardashas": antardashas,
    }
