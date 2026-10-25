"""Vimshottari dasha — the 120-year Moon-nakshatra based timing system.

Dates are computed with a 365.25-day year (the convention used by the
mainstream tools). Every period is a [start, end) interval of calendar
dates anchored at the birth datetime.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from .names import DASHA_SEQUENCE, DASHA_YEARS, NAKSHATRA_LORDS, NAKSHATRA_SPAN

YEAR_DAYS = 365.25


def _days(years: float) -> timedelta:
    return timedelta(days=years * YEAR_DAYS)


def _subdivide_years(start: datetime, total_years: float, first_lord: str,
                     sequence: list[str], years_map: dict, cycle_years: float) -> list[dict]:
    """Split a period into len(sequence) sub-periods beginning with
    `first_lord`, each proportional to its lord's years in the cycle."""
    i0 = sequence.index(first_lord)
    periods = []
    cursor = start
    for k in range(len(sequence)):
        lord = sequence[(i0 + k) % len(sequence)]
        years = total_years * years_map[lord] / cycle_years
        end = cursor + _days(years)
        periods.append({"lord": lord, "start": cursor, "end": end, "years": years})
        cursor = end
    return periods


def _subdivide(start: datetime, total_years: float, first_lord: str) -> list[dict]:
    """Split a period of `total_years` into 9 sub-periods beginning with
    `first_lord`, each proportional to its lord's Vimshottari years."""
    return _subdivide_years(start, total_years, first_lord,
                            DASHA_SEQUENCE, DASHA_YEARS, 120.0)


def period_at(tree: dict, at: datetime):
    """(MD, AD) running at `at` in a Vimshottari-style tree."""
    for md in tree["mahadashas"]:
        if md["start"] <= at < md["end"]:
            for ad in md["antardashas"]:
                if ad["start"] <= at < ad["end"]:
                    return md, ad
            return md, None
    return None, None


def vimshottari_tree(birth_dt: datetime, moon_longitude: float, now: datetime | None = None) -> dict:
    """Full mahadasha tree with antardashas; pratyantardashas for the
    currently running antardasha. Returns current MD/AD/PD resolution too."""
    nak_idx = int((moon_longitude % 360.0) // NAKSHATRA_SPAN)
    first_lord = NAKSHATRA_LORDS[nak_idx]
    traversed = ((moon_longitude % 360.0) - nak_idx * NAKSHATRA_SPAN) / NAKSHATRA_SPAN
    balance_years = (1.0 - traversed) * DASHA_YEARS[first_lord]

    i0 = DASHA_SEQUENCE.index(first_lord)
    mahadashas = []
    # The first mahadasha virtually began before birth; subdividing from its
    # true start keeps antardasha boundaries correct (the native is born
    # part-way through one of them). Intervals are true [start, end) ranges.
    cursor = birth_dt - _days(traversed * DASHA_YEARS[first_lord])
    for k in range(9):
        lord = DASHA_SEQUENCE[(i0 + k) % 9]
        years = float(DASHA_YEARS[lord])
        end = cursor + _days(years)
        md = {"lord": lord, "start": cursor, "end": end, "years": years}
        md["antardashas"] = _subdivide(cursor, years, lord)
        mahadashas.append(md)
        cursor = end

    current = _resolve(mahadashas, now or datetime.now(birth_dt.tzinfo))

    # Pratyantardashas only for the running antardasha (keeps payload sane),
    # and Sookshma + Prana only for the running pratyantardasha / sookshma.
    if current:
        md = current["mahadasha"]
        ad = current["antardasha"]
        ad["pratyantardashas"] = _subdivide(ad["start"], ad["years"], ad["lord"])
        pd = next(
            (p for p in ad["pratyantardashas"] if p["start"] <= current["at"] < p["end"]),
            None,
        )
        current["pratyantardasha"] = pd
        if pd is not None:
            pd["sookshma_dashas"] = _subdivide(pd["start"], pd["years"], pd["lord"])
            sk = next(
                (p for p in pd["sookshma_dashas"] if p["start"] <= current["at"] < p["end"]),
                None,
            )
            current["sookshma"] = sk
            if sk is not None:
                sk["prana_dashas"] = _subdivide(sk["start"], sk["years"], sk["lord"])
                current["prana"] = next(
                    (p for p in sk["prana_dashas"] if p["start"] <= current["at"] < p["end"]),
                    None,
                )
            else:
                current["prana"] = None
        else:
            current["sookshma"] = None
            current["prana"] = None
    return {"mahadashas": mahadashas, "current": current, "balance_years": balance_years}


def _resolve(mahadashas: list[dict], at: datetime) -> dict | None:
    for md in mahadashas:
        if md["start"] <= at < md["end"]:
            for ad in md["antardashas"]:
                if ad["start"] <= at < ad["end"]:
                    return {"mahadasha": md, "antardasha": ad, "at": at}
            return {"mahadasha": md, "antardasha": None, "at": at}
    return None


# ---------------------------------------------------------------------------
# Yogini dasha — the 36-year, 8-yogini cycle offered by Nepali patros
# (Hamro Patro lists Vimshottari, Yogini and Trivagi side by side).
# Starting yogini: (nakshatra index + 3) mod 8 over the sequence below;
# the balance is the untraversed fraction of the starting yogini's years.
# ---------------------------------------------------------------------------
YOGINI_SEQUENCE = [
    ("Mangala", "Moon", 1), ("Pingala", "Sun", 2), ("Dhanya", "Jupiter", 3),
    ("Bhramari", "Mars", 4), ("Bhadrika", "Mercury", 5), ("Ulka", "Saturn", 6),
    ("Siddha", "Venus", 7), ("Sankata", "Rahu", 8),
]


def yogini_periods(birth_dt: datetime, moon_longitude: float,
                   now: datetime | None = None, cycles: int = 3) -> dict:
    nak_idx = int((moon_longitude % 360.0) // NAKSHATRA_SPAN)
    traversed = ((moon_longitude % 360.0) - nak_idx * NAKSHATRA_SPAN) / NAKSHATRA_SPAN
    start_idx = (nak_idx + 3) % 8
    name0, planet0, years0 = YOGINI_SEQUENCE[start_idx]
    balance_years = (1.0 - traversed) * years0

    periods = []
    cursor = birth_dt - _days(traversed * years0)
    total = cycles * len(YOGINI_SEQUENCE)
    for k in range(total):
        name, planet, years = YOGINI_SEQUENCE[(start_idx + k) % 8]
        end = cursor + _days(float(years))
        periods.append({"name": name, "planet": planet, "start": cursor, "end": end, "years": float(years)})
        cursor = end
    at = now or datetime.now(birth_dt.tzinfo)
    current = next((p for p in periods if p["start"] <= at < p["end"]), None)
    return {"periods": periods, "current": current, "balance_years": balance_years}


# ---------------------------------------------------------------------------
# Tribhagi (Trivagi) dasha — Vimshottari with every period divided by 3,
# the third Nepali-patro system. The 120-year cycle becomes three rounds
# of ~40 years; the starting balance is the Vimshottari balance / 3.
# ---------------------------------------------------------------------------
def tribhagi_periods(birth_dt: datetime, moon_longitude: float,
                     now: datetime | None = None) -> dict:
    nak_idx = int((moon_longitude % 360.0) // NAKSHATRA_SPAN)
    first_lord = NAKSHATRA_LORDS[nak_idx]
    traversed = ((moon_longitude % 360.0) - nak_idx * NAKSHATRA_SPAN) / NAKSHATRA_SPAN
    balance_years = (1.0 - traversed) * DASHA_YEARS[first_lord] / 3.0

    i0 = DASHA_SEQUENCE.index(first_lord)
    periods = []
    cursor = birth_dt - _days(traversed * DASHA_YEARS[first_lord] / 3.0)
    for k in range(27):  # three full rounds = 120 years
        lord = DASHA_SEQUENCE[(i0 + k) % 9]
        years = DASHA_YEARS[lord] / 3.0
        end = cursor + _days(years)
        periods.append({"lord": lord, "start": cursor, "end": end, "years": years})
        cursor = end
    at = now or datetime.now(birth_dt.tzinfo)
    current = next((p for p in periods if p["start"] <= at < p["end"]), None)
    return {"periods": periods, "current": current, "balance_years": balance_years}


# ---------------------------------------------------------------------------
# Ashtottari dasha — the 108-year, 8-lord conditional system (BPHS).
# Ketu is excluded; the lords' years are Sun 6, Moon 15, Mars 8,
# Mercury 17, Saturn 10, Jupiter 19, Rahu 12, Venus 21 (= 108).
#
# Nakshatra blocks are anchored at Ardra (the P.V.R. Narasimha Rao /
# Jagannatha Hora grouping): Sun takes Ardra, Punarvasu, Pushya,
# Ashlesha; Moon takes Magha, Purva Phalguni, Uttara Phalguni; Mars
# takes Hasta, Chitra, Swati, Vishakha; Mercury takes Anuradha,
# Jyeshtha, Mula; Saturn takes Purva Ashadha, Uttara Ashadha,
# Abhijit, Shravana; Jupiter takes Dhanishta, Shatabhisha, Purva
# Bhadrapada; Rahu takes Uttara Bhadrapada, Revati, Ashwini,
# Bharani (wrapping the zodiac's seam); Venus takes Krittika,
# Rohini, Mrigashira. The 28 divisions (27 + intercalary Abhijit,
# Capricorn 6 deg 40 min - 10 deg 53 min 20 sec) are what make the
# 4+3+4+3+4+3+4+3 block counts add up; Abhijit still belongs to
# Saturn's block, so it changes only the balance fraction, never
# the lord. A competing tradition anchors the count at Krittika
# for Shukla-paksha births instead of Ardra; the Ardra anchor is
# used here and the variant is noted.
#
# Applicability (Parasara, as published in modern conditional-dasha
# guides): (1) Rahu stands in a kendra (1/4/7/10) or trikona (1/5/9)
# from the Lagna lord, and not in the Lagna itself; (2) the birth
# is in daytime during Krishna paksha, or at night during Shukla
# paksha. Both conditions are reported separately; the system is
# computed regardless (advisory, as the major tools do), because
# traditions differ on whether the conditions are necessary or
# merely favouring. Vimshottari remains the primary dasha.
# ---------------------------------------------------------------------------
ASHTOTTARI_SEQUENCE = ["Sun", "Moon", "Mars", "Mercury", "Saturn", "Jupiter", "Rahu", "Venus"]
ASHTOTTARI_YEARS = {
    "Sun": 6, "Moon": 15, "Mars": 8, "Mercury": 17,
    "Saturn": 10, "Jupiter": 19, "Rahu": 12, "Venus": 21,
}
ASHTOTTARI_BLOCKS = [
    ("Sun", [5, 6, 7, 8]), ("Moon", [9, 10, 11]), ("Mars", [12, 13, 14, 15]),
    ("Mercury", [16, 17, 18]), ("Saturn", [19, 20, 21]), ("Jupiter", [22, 23, 24]),
    ("Rahu", [25, 26, 0, 1]), ("Venus", [2, 3, 4]),
]
_ABHIJIT_START = 270.0 + 6.0 + 40.0 / 60.0   # Capricorn 6 deg 40 min
_ABHIJIT_END = 270.0 + 10.0 + 53.0 / 60.0 + 20.0 / 3600.0  # 10 deg 53 min 20 sec


def ashtottari_division(moon_longitude: float) -> dict:
    """Birth division for Ashtottari: lord, span and traversed fraction."""
    lon = moon_longitude % 360.0
    if _ABHIJIT_START <= lon < _ABHIJIT_END:
        return {"division": "Abhijit", "lord": "Saturn",
                "span": _ABHIJIT_END - _ABHIJIT_START,
                "traversed": (lon - _ABHIJIT_START) / (_ABHIJIT_END - _ABHIJIT_START)}
    nak_idx = int(lon // NAKSHATRA_SPAN)
    lord = next(l for l, blocks in ASHTOTTARI_BLOCKS if nak_idx in blocks)
    return {"division": nak_idx, "lord": lord, "span": NAKSHATRA_SPAN,
            "traversed": (lon - nak_idx * NAKSHATRA_SPAN) / NAKSHATRA_SPAN}


def ashtottari_tree(birth_dt: datetime, moon_longitude: float,
                    now: datetime | None = None) -> dict:
    """Full Ashtottari mahadasha tree (8 lords, 108-year cycle) with
    antardashas for every mahadasha and the current MD/AD."""
    div = ashtottari_division(moon_longitude)
    first_lord = div["lord"]
    balance_years = (1.0 - div["traversed"]) * ASHTOTTARI_YEARS[first_lord]

    i0 = ASHTOTTARI_SEQUENCE.index(first_lord)
    mahadashas = []
    cursor = birth_dt - _days(div["traversed"] * ASHTOTTARI_YEARS[first_lord])
    for k in range(8):
        lord = ASHTOTTARI_SEQUENCE[(i0 + k) % 8]
        years = float(ASHTOTTARI_YEARS[lord])
        end = cursor + _days(years)
        md = {"lord": lord, "start": cursor, "end": end, "years": years}
        md["antardashas"] = _subdivide_years(
            cursor, years, lord, ASHTOTTARI_SEQUENCE, ASHTOTTARI_YEARS, 108.0)
        mahadashas.append(md)
        cursor = end

    at = now or datetime.now(birth_dt.tzinfo)
    current = None
    for md in mahadashas:
        if md["start"] <= at < md["end"]:
            ad = next((a for a in md["antardashas"] if a["start"] <= at < a["end"]), None)
            current = {"mahadasha": md, "antardasha": ad, "at": at}
            break
    return {"mahadashas": mahadashas, "current": current,
            "balance_years": balance_years, "birth_division": div["division"]}


def ashtottari_applicability(planets: dict, lagna_sign: int,
                             is_daytime: bool, paksha: str) -> dict:
    """The two classical Ashtottari conditions, reported separately."""
    from .charts import house_of
    from .names import SIGN_LORDS

    lagna_lord = SIGN_LORDS[lagna_sign]
    lagna_lord_sign = planets[lagna_lord]["sign"]
    rahu_from_lord = house_of(planets["Rahu"]["sign"], lagna_lord_sign)
    rahu_from_lagna = house_of(planets["Rahu"]["sign"], lagna_sign)
    rahu_ok = rahu_from_lord in (1, 4, 5, 7, 9, 10) and rahu_from_lagna != 1
    paksha_ok = (is_daytime and paksha == "Krishna") or (not is_daytime and paksha == "Shukla")
    return {
        "lagna_lord": lagna_lord,
        "rahu_house_from_lagna_lord": rahu_from_lord,
        "rahu_in_lagna": rahu_from_lagna == 1,
        "rahu_condition": rahu_ok,
        "day_night_paksha_condition": paksha_ok,
        "is_daytime": is_daytime, "paksha": paksha,
        "applies": bool(rahu_ok and paksha_ok),
        "note": ("Ashtottari is conditional: it is traditionally applied "
                 "when both conditions hold. The sequence is computed "
                 "regardless so it can be inspected on any chart."),
    }
