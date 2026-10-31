"""Phase 3 dashas — the classical timing systems beyond Vimshottari.

Four systems, each implemented from the primary sources named below:

* **Narayana Dasha** (Jaimini Padha Krama): the sign dasha of the Jaimini
  Sutras. Starts from the stronger of Lagna and 7th, progresses by Padha
  Krama (movable: regular order; fixed: every 6th; dual: trine sets), with
  Chara-style year counts and a 12-minus second cycle.
  Sources: Jaimini Sutras via Sanjay Rath's "Upadesa Sutras" and
  P.V.R. Narasimha Rao's computation notes (indiadivine.org).
* **Shodshottari Dasha** (116 years): conditional nakshatra dasha, seed
  Pushya. Applies when Lagna is in Sun's hora in Shukla paksha or Moon's
  hora in Krishna paksha (BPHS; P.V.R. Narasimha Rao's "Unified Nakshatra
  Dasa Approach").
* **Mudda Dasha** (Vimshottari Mudda, Tajika): the 360-day annual dasha
  compressed from Vimshottari, anchored at Varshapravesh (solar return).
  Source: K.S. Charak's "A Textbook of Varshaphala" / Shanker Study
  encyclopedia of Tajika dashas.
* **Kalachakra Dasha**: the nakshatra-pada sign dasha in four
  savya/apasavya groups, Full-cycle-fraction balance, deha/jiva rasis.
  Source: Sanjay Rath's SJC Europe 2005 presentation "Kalacakra Dasa"
  (all 16 pada sequences verified: sign-year sums equal the paramayus).

Dates use the app-wide 365.25-day year. Every period is a [start, end)
interval of calendar dates.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from .chara import EVEN_FOOTED
from .charts import dignity
from .dasha import _days, _subdivide_years
from .ephemeris import nakshatra_of
from .jaimini import rasi_aspects, sign_lord_jaimini
from .names import (
    NAKSHATRA_SPAN,
    SIGN_LORDS,
    SIGNS_EN,
    SIGNS_NE,
)

YEAR_DAYS = 365.25


# ---------------------------------------------------------------------------
# Jaimini sign strength (for "stronger of ..." decisions)
# ---------------------------------------------------------------------------

def _modality(sign: int) -> int:
    """0 = movable, 1 = fixed, 2 = dual."""
    return (0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2)[sign]


def stronger_sign(planets: dict, sign_a: int, sign_b: int,
                  atmakaraka: str | None) -> int:
    """The stronger of two signs by the Jaimini hierarchy (Upadesa Sutras):

    1. the sign holding the Atmakaraka;
    2. the sign holding more planets (all 9 grahas counted);
    3. the sign whose strongest planet (highest degree in sign) is stronger;
    4. chara bala — dual > fixed > movable;
    5. drishti bala — Jaimini aspect by its own lord, Jupiter or Mercury.
    A full tie returns sign_a (documented; callers pass the preferred sign
    first where a classical default exists).
    """
    if sign_a == sign_b:
        return sign_a

    def occupants(sign: int) -> list[str]:
        return [p for p in planets if planets[p]["sign"] == sign]

    # (1) Atmakaraka's sign.
    if atmakaraka:
        ak_sign = planets[atmakaraka]["sign"]
        if (ak_sign == sign_a) != (ak_sign == sign_b):
            return sign_a if ak_sign == sign_a else sign_b

    # (2) More planets.
    occ_a, occ_b = occupants(sign_a), occupants(sign_b)
    if len(occ_a) != len(occ_b):
        return sign_a if len(occ_a) > len(occ_b) else sign_b

    # (3) Stronger "best" planet by degree in sign (chara-karaka principle).
    if occ_a:
        best_a = max(planets[p]["degree_in_sign"] for p in occ_a)
        best_b = max(planets[p]["degree_in_sign"] for p in occ_b)
        if best_a != best_b:
            return sign_a if best_a > best_b else sign_b

    # (4) Chara bala: dual (2) > fixed (1) > movable (0).
    mod_a, mod_b = _modality(sign_a), _modality(sign_b)
    if mod_a != mod_b:
        return sign_a if mod_a > mod_b else sign_b

    # (5) Drishti bala: Jaimini aspect by own lord, Jupiter or Mercury.
    def drishti(sign: int) -> int:
        lord = SIGN_LORDS[sign]
        score = 0
        for watcher in {lord, "Jupiter", "Mercury"}:
            w_sign = planets[watcher]["sign"]
            if w_sign == sign or sign in rasi_aspects(w_sign):
                score += 1
        return score

    dr_a, dr_b = drishti(sign_a), drishti(sign_b)
    if dr_a != dr_b:
        return sign_a if dr_a > dr_b else sign_b

    return sign_a


# ---------------------------------------------------------------------------
# Narayana Dasha (Jaimini Padha Krama)
# ---------------------------------------------------------------------------

def _count_rasis(a: int, b: int) -> int:
    return (b - a) % 12 + 1


def narayana_duration(planets: dict, sign: int) -> int:
    """Years of one sign's Narayana period.

    Count from the sign to its lord for odd-footed (vishamapada) signs and
    from the lord to the sign for even-footed signs, minus 1 (a count of 1
    gives 12). Scorpio/Aquarius use the stronger Jaimini co-lord. +1 when
    the lord is exalted, -1 when debilitated — except Mercury in Virgo,
    which counts as own sign (12 years, no bonus).
    """
    lord = sign_lord_jaimini(planets, sign)
    lord_sign = planets[lord]["sign"]
    if sign in EVEN_FOOTED:
        count = _count_rasis(lord_sign, sign)
    else:
        count = _count_rasis(sign, lord_sign)
    years = count - 1
    if years <= 0:
        years = 12
    # Mercury's exaltation (Virgo) is also its own sign: no bonus.
    if lord == "Mercury" and lord_sign == 5:
        return 12 if count == 1 else years
    d = dignity(lord, lord_sign)
    if d == "exalted":
        years += 1
    elif d == "debilitated":
        years -= 1
    return years


# Trikona sets in zodiacal order; the dual sign heading each set.
_TRIKONA_SETS = ((0, 4, 8), (1, 5, 9), (2, 6, 10), (3, 7, 11))
_SET_DUAL = (8, 5, 2, 11)  # Sg, Vi, Ge, Pi


def _padha_krama_sequence(start: int, forward: bool) -> list[int]:
    """The 12 signs in Narayana order from the initiating sign.

    Movable start: regular order. Fixed start: every 6th sign.
    Dual start: finish each trikona set, then move to the next set
    (sets run in zodiacal order; within a set start from its dual sign).
    """
    mod = _modality(start)
    if mod == 0:  # movable — regular order
        step = 1 if forward else -1
        return [(start + step * i) % 12 for i in range(12)]
    if mod == 1:  # fixed — every 6th sign inclusive = 5 exclusive steps
        step = 5 if forward else -5
        return [(start + step * i) % 12 for i in range(12)]
    # dual — trine sets
    set_idx = start % 4
    seq: list[int] = []
    for k in range(4):
        s = (set_idx + k) % 4 if forward else (set_idx - k) % 4
        d = _SET_DUAL[s]
        step = 4 if forward else -4
        seq.extend([(d + step * j) % 12 for j in range(3)])
    return seq


def _narayana_antars(birth_dt_unused, planets: dict, md_sign: int,
                     md_start: datetime, md_years: float,
                     atmakaraka: str | None) -> list[dict]:
    """Antardashas of one Narayana mahadasha.

    Stronger of the dasha sign and the 7th from it -> its lord -> the sign
    the lord occupies -> start there; odd sign goes forward, even sign goes
    backward, always in regular (consecutive) order. Twelve equal parts:
    an n-year dasha gives n-month antars.
    """
    seventh = (md_sign + 6) % 12
    strong = stronger_sign(planets, md_sign, seventh, atmakaraka)
    lord = sign_lord_jaimini(planets, strong)
    lord_sign = planets[lord]["sign"]
    # Odd signs (Ar, Ge, Le, ...) go forward; even signs go backward.
    forward = lord_sign % 2 == 0
    step = 1 if forward else -1
    order = [(lord_sign + step * i) % 12 for i in range(12)]
    antar_years = md_years / 12.0
    antars = []
    cursor = md_start
    for sign in order:
        end = cursor + _days(antar_years)
        antars.append({"sign": sign, "start": cursor, "end": end,
                       "years": antar_years})
        cursor = end
    return antars


def narayana_periods(birth_dt: datetime, planets: dict, lagna_sign: int,
                     atmakaraka: str | None,
                     now: datetime | None = None) -> dict:
    """Full Narayana mahadasha timeline with antardashas.

    Starts from the stronger of Lagna and the 7th. Direction: the 9th from
    the start is odd-footed -> zodiacal, even-footed -> anti-zodiacal
    (same foot rule as Chara). Two cycles are laid out; the second cycle's
    years are 12 minus the first cycle's.
    """
    seventh = (lagna_sign + 6) % 12
    start = stronger_sign(planets, lagna_sign, seventh, atmakaraka)
    ninth = (start + 8) % 12
    forward = ninth not in EVEN_FOOTED
    seq = _padha_krama_sequence(start, forward)
    first_years = [narayana_duration(planets, s) for s in seq]

    mahadashas = []
    cursor = birth_dt
    for cycle in (0, 1):
        for sign, y1 in zip(seq, first_years):
            years = float(y1 if cycle == 0 else 12 - y1)
            end = cursor + _days(years)
            md = {"sign": sign, "start": cursor, "end": end,
                  "years": years, "cycle": cycle + 1}
            md["antardashas"] = _narayana_antars(
                None, planets, sign, cursor, years, atmakaraka)
            mahadashas.append(md)
            cursor = end

    at = now or datetime.now(birth_dt.tzinfo)
    current = None
    for md in mahadashas:
        if md["start"] <= at < md["end"]:
            ad = next((a for a in md["antardashas"]
                       if a["start"] <= at < a["end"]), None)
            current = {"mahadasha": md, "antardasha": ad, "at": at}
            break
    return {
        "mahadashas": mahadashas,
        "current": current,
        "start_sign": start,
        "start_sign_en": SIGNS_EN[start],
        "start_sign_ne": SIGNS_NE[start],
        "forward": forward,
        "note": ("Narayana (Padha Krama): starts from the stronger of Lagna "
                 "and the 7th; the second 12-sign cycle runs 12-minus years."),
    }


# ---------------------------------------------------------------------------
# Shodshottari Dasha (116 years, conditional nakshatra dasha)
# ---------------------------------------------------------------------------

SHODSHOTTARI_SEQUENCE = [
    "Sun", "Mars", "Jupiter", "Saturn", "Ketu", "Moon", "Mercury", "Venus",
]
SHODSHOTTARI_YEARS = {
    "Sun": 11, "Mars": 12, "Jupiter": 13, "Saturn": 14,
    "Ketu": 15, "Moon": 16, "Mercury": 17, "Venus": 18,
}
SHODSHOTTARI_CYCLE = 116.0
_PUSHYA_IDX = 7  # seed nakshatra


def shodshottari_applicability(lagna_sign: int, lagna_degree_in_sign: float,
                               paksha: str) -> dict:
    """BPHS condition: Lagna in Sun's hora in Shukla paksha, or in Moon's
    hora in Krishna paksha. Hora: odd signs 0-15 deg = Sun, 15-30 = Moon;
    even signs 0-15 = Moon, 15-30 = Sun."""
    odd_sign = lagna_sign % 2 == 0  # Aries = 0 is the 1st (odd) sign
    if odd_sign:
        hora_lord = "Sun" if lagna_degree_in_sign < 15.0 else "Moon"
    else:
        hora_lord = "Moon" if lagna_degree_in_sign < 15.0 else "Sun"
    applies = ((hora_lord == "Sun" and paksha == "Shukla")
               or (hora_lord == "Moon" and paksha == "Krishna"))
    return {
        "hora_lord": hora_lord,
        "paksha": paksha,
        "applies": bool(applies),
        "note": ("Shodshottari applies when Lagna is in Sun's hora during "
                 "Shukla paksha or Moon's hora during Krishna paksha. The "
                 "sequence is computed regardless so it can be inspected on "
                 "any chart."),
    }


def shodshottari_tree(birth_dt: datetime, moon_longitude: float,
                      now: datetime | None = None) -> dict:
    """Full Shodshottari mahadasha tree (8 lords, 116-year cycle).

    Count nakshatras from Pushya (inclusive) to the Janma nakshatra
    (inclusive); divide by 8 — the remainder selects the starting lord
    (Sun 11, Mars 12, Jupiter 13, Saturn 14, Ketu 15, Moon 16,
    Mercury 17, Venus 18). Balance is proportional to the Moon's
    remaining traverse of its nakshatra.
    """
    lon = moon_longitude % 360.0
    nak_idx = int(lon // NAKSHATRA_SPAN)
    count = (nak_idx - _PUSHYA_IDX) % 27 + 1
    i0 = (count - 1) % 8
    first_lord = SHODSHOTTARI_SEQUENCE[i0]
    traversed = (lon - nak_idx * NAKSHATRA_SPAN) / NAKSHATRA_SPAN
    balance_years = (1.0 - traversed) * SHODSHOTTARI_YEARS[first_lord]

    mahadashas = []
    cursor = birth_dt - _days(traversed * SHODSHOTTARI_YEARS[first_lord])
    for k in range(8):
        lord = SHODSHOTTARI_SEQUENCE[(i0 + k) % 8]
        years = float(SHODSHOTTARI_YEARS[lord])
        end = cursor + _days(years)
        md = {"lord": lord, "start": cursor, "end": end, "years": years}
        md["antardashas"] = _subdivide_years(
            cursor, years, lord, SHODSHOTTARI_SEQUENCE,
            SHODSHOTTARI_YEARS, SHODSHOTTARI_CYCLE)
        mahadashas.append(md)
        cursor = end

    at = now or datetime.now(birth_dt.tzinfo)
    current = None
    for md in mahadashas:
        if md["start"] <= at < md["end"]:
            ad = next((a for a in md["antardashas"]
                       if a["start"] <= at < a["end"]), None)
            current = {"mahadasha": md, "antardasha": ad, "at": at}
            break
    return {
        "mahadashas": mahadashas,
        "current": current,
        "balance_years": balance_years,
        "seed": "Pushya",
        "janma_nakshatra_index": nak_idx,
    }


# ---------------------------------------------------------------------------
# Mudda Dasha (Vimshottari Mudda — Tajika annual dasha)
# ---------------------------------------------------------------------------

# Vimshottari order counted from the Sun.
MUDDA_SEQUENCE = ["Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn",
                  "Mercury", "Ketu", "Venus"]
# Annual days per planet: Vimshottari years x 3 (360-day year).
MUDDA_DAYS_360 = {
    "Sun": 18, "Moon": 30, "Mars": 21, "Rahu": 54, "Jupiter": 48,
    "Saturn": 57, "Mercury": 51, "Ketu": 21, "Venus": 60,
}
_MUDDA_SCALE = 365.0 / 360.0  # spread over the 365-day civil year


def _solar_return_jd(birth_sun_lon: float, year: int) -> float:
    """Julian day of the sidereal solar return nearest to `year`.

    Finds when the Sun's sidereal longitude next equals the birth
    longitude, searching from mid-year. Used to anchor the Varshaphala
    year for the Mudda dasha.
    """
    from .ephemeris import planet_longitude_at, to_julian_day

    target = birth_sun_lon % 360.0
    # Start the search a little before the expected return.
    jd_guess = to_julian_day(
        datetime(year, 1, 1).replace(tzinfo=None)) + 200.0

    def sun_lon(jd: float) -> float:
        return planet_longitude_at("Sun", jd) % 360.0

    # Coarse scan forward in 2-day steps to bracket the crossing.
    jd = jd_guess
    prev = sun_lon(jd)
    for _ in range(200):
        jd += 2.0
        cur = sun_lon(jd)
        # crossing when the longitude wraps past the target
        if (prev - target) % 360.0 > (cur - target) % 360.0 and \
                abs((cur - prev + 180.0) % 360.0 - 180.0) < 5.0:
            break
        prev = cur
    lo, hi = jd - 2.0, jd
    # Bisection on the circular distance.
    for _ in range(60):
        mid = (lo + hi) / 2.0
        # signed distance from target, in (-180, 180]
        def sdist(j: float) -> float:
            return (sun_lon(j) - target + 540.0) % 360.0 - 180.0
        # We approach from below (Sun moves forward); find first crossing.
        if sdist(lo) <= 0 <= sdist(mid) or sdist(mid) <= 0 <= sdist(lo):
            hi = mid
        else:
            lo = mid
        if hi - lo < 1e-7:
            break
    return (lo + hi) / 2.0


def mudda_dasha(birth_dt: datetime, moon_longitude: float,
                birth_sun_longitude: float,
                now: datetime | None = None) -> dict:
    """Vimshottari Mudda dasha for the current Varshaphala year.

    The year opens at the sidereal solar return (Varshapravesh). The
    opening planet: (completed years of life + birth nakshatra number - 2)
    / 9, remainder counted from the Sun (K.S. Charak). Each planet's days
    are its Vimshottari years x 3, scaled from the 360-day ritual year to
    365 days. The opening balance comes from the birth Moon's remaining
    traverse of its nakshatra. Antardashas: first AD is the MD lord, the
    rest follow Vimshottari order; AD = MD_days x AD_days / 360.
    """
    from .ephemeris import jd_to_utc_datetime, to_julian_day

    at = now or datetime.now(birth_dt.tzinfo)
    at_naive_utc = at.replace(tzinfo=None)

    # Anchor: the most recent solar return at or before `at`.
    sun_lon = birth_sun_longitude % 360.0
    jd_now = to_julian_day(at_naive_utc)
    jd_sr = _solar_return_jd(sun_lon, at_naive_utc.year)
    if jd_to_utc_datetime(jd_sr).replace(tzinfo=None) > at_naive_utc:
        jd_sr = _solar_return_jd(sun_lon, at_naive_utc.year - 1)
    varshapravesh = jd_to_utc_datetime(jd_sr)
    if birth_dt.tzinfo is not None:
        varshapravesh = varshapravesh.replace(tzinfo=birth_dt.tzinfo)

    # Completed years of life at Varshapravesh.
    vp_naive = varshapravesh.replace(tzinfo=None)
    birth_naive = birth_dt.replace(tzinfo=None)
    completed = vp_naive.year - birth_naive.year - (
        (vp_naive.month, vp_naive.day) < (birth_naive.month, birth_naive.day))

    nak_num = int((moon_longitude % 360.0) // NAKSHATRA_SPAN) + 1  # 1-27
    r = (completed + nak_num - 2) % 9
    if r == 0:
        r = 9
    first_planet = MUDDA_SEQUENCE[r - 1]

    # Opening balance from the birth Moon's nakshatra traverse.
    lon = moon_longitude % 360.0
    nak_idx = int(lon // NAKSHATRA_SPAN)
    traversed = (lon - nak_idx * NAKSHATRA_SPAN) / NAKSHATRA_SPAN
    balance_frac = 1.0 - traversed

    periods = []
    cursor = varshapravesh
    i0 = MUDDA_SEQUENCE.index(first_planet)
    for k in range(9):
        planet = MUDDA_SEQUENCE[(i0 + k) % 9]
        full_days = MUDDA_DAYS_360[planet] * _MUDDA_SCALE
        days = full_days * balance_frac if k == 0 else full_days
        end = cursor + timedelta(days=days)
        md = {"planet": planet, "start": cursor, "end": end, "days": days}
        # Antardashas: same planet first, then Vimshottari order.
        ad_cursor = cursor
        antars = []
        j0 = MUDDA_SEQUENCE.index(planet)
        for m in range(9):
            ad_planet = MUDDA_SEQUENCE[(j0 + m) % 9]
            ad_days = days * MUDDA_DAYS_360[ad_planet] / 360.0
            ad_end = ad_cursor + timedelta(days=ad_days)
            antars.append({"planet": ad_planet, "start": ad_cursor,
                           "end": ad_end, "days": ad_days})
            ad_cursor = ad_end
        md["antardashas"] = antars
        periods.append(md)
        cursor = end

    current = None
    for md in periods:
        if md["start"] <= at < md["end"]:
            ad = next((a for a in md["antardashas"]
                       if a["start"] <= at < a["end"]), None)
            current = {"mahadasha": md, "antardasha": ad, "at": at}
            break
    return {
        "periods": periods,
        "current": current,
        "varshapravesh": varshapravesh,
        "completed_years": completed,
        "birth_nakshatra_number": nak_num,
        "note": ("Vimshottari Mudda dasha for the Varshaphala year opening "
                 "at the sidereal solar return; 360 ritual days scaled to "
                 "365."),
    }


# ---------------------------------------------------------------------------
# Kalachakra Dasha
# ---------------------------------------------------------------------------

# Dasha years by sign (from the sign's lord).
_KALACHAKRA_SIGN_YEARS = {
    0: 7, 7: 7,      # Aries, Scorpio — Mars
    1: 16, 6: 16,    # Taurus, Libra — Venus
    2: 9, 5: 9,      # Gemini, Virgo — Mercury
    3: 21,           # Cancer — Moon
    4: 5,            # Leo — Sun
    8: 10, 11: 10,   # Sagittarius, Pisces — Jupiter
    9: 4, 10: 4,     # Capricorn, Aquarius — Saturn
}

# Nakshatra indices per Kalachakra group (Sanjay Rath, SJC 2005).
# 0=Ashwini ... 26=Revati.
_KC_SAVYA_RIGHT = (0, 2, 6, 8, 12, 14, 18, 20, 24, 26)   # Ashwini group
_KC_SAVYA_LEFT = (1, 7, 13, 19, 25)                      # Bharani group
_KC_APASAVYA_LEFT = (3, 9, 15, 21)                       # Rohini group
_KC_APASAVYA_RIGHT = (4, 5, 10, 11, 16, 17, 22, 23)      # Mrigashira group

# (sequence of 9 signs, paramayus) per group and pada (1-4).
# Sign indices: 0=Ar 1=Ta 2=Ge 3=Cn 4=Le 5=Vi 6=Li 7=Sc 8=Sg 9=Cp 10=Aq 11=Pi.
# Every sequence's sign-year sum equals its paramayus (verified).
_KC_TABLE = {
    "savya-right": {
        1: ([0, 1, 2, 3, 4, 5, 6, 7, 8], 100),
        2: ([9, 10, 11, 7, 6, 5, 3, 4, 2], 85),
        3: ([1, 0, 11, 10, 9, 8, 0, 1, 2], 83),
        4: ([3, 4, 5, 6, 7, 8, 9, 10, 11], 86),
    },
    "savya-left": {
        1: ([7, 6, 5, 3, 4, 2, 1, 0, 11], 100),
        2: ([10, 9, 8, 0, 1, 2, 3, 4, 5], 85),
        3: ([6, 7, 8, 9, 10, 11, 7, 6, 5], 83),
        4: ([3, 4, 2, 1, 0, 11, 10, 9, 8], 86),
    },
    "apasavya-left": {
        1: ([8, 9, 10, 11, 0, 1, 2, 4, 3], 86),
        2: ([5, 6, 7, 11, 10, 9, 8, 7, 6], 83),
        3: ([5, 4, 3, 2, 1, 0, 8, 9, 10], 85),
        4: ([11, 0, 1, 2, 4, 3, 5, 6, 7], 100),
    },
    "apasavya-right": {
        1: ([11, 10, 9, 8, 7, 6, 5, 4, 3], 86),
        2: ([2, 1, 0, 8, 9, 10, 11, 0, 1], 83),
        3: ([2, 4, 3, 5, 6, 7, 11, 10, 9], 85),
        4: ([8, 7, 6, 5, 4, 3, 2, 1, 0], 100),
    },
}

# Chakra-continuity: when a pada's nine dashas end, the wheel moves to the
# other foot within the same savya/apasavya, restarting at pada 1
# (Sanjay Rath's example: Shatabhisha pada-4 -> Rohini group pada-1).
_KC_NEXT_GROUP = {
    "savya-right": "savya-left",
    "savya-left": "savya-right",
    "apasavya-right": "apasavya-left",
    "apasavya-left": "apasavya-right",
}


def _kc_group(nak_idx: int) -> str:
    if nak_idx in _KC_SAVYA_RIGHT:
        return "savya-right"
    if nak_idx in _KC_SAVYA_LEFT:
        return "savya-left"
    if nak_idx in _KC_APASAVYA_LEFT:
        return "apasavya-left"
    return "apasavya-right"


def _kc_deha_jiva(group: str, sequence: list[int]) -> tuple[int, int]:
    """Deha (body) and Jiva (soul) rasis.

    Per the tabulated values in Sanjay Rath's SJC presentation (all 16
    padas): deha = first dasha sign, jiva = last dasha sign. (The
    presentation's explanatory text suggests apasavya reverses this, but
    the table itself — the primary data — is consistent: first/last for
    every pada, so the table is followed.)
    """
    return sequence[0], sequence[-1]


def _kc_antar_order(md_sign: int, apasavya: bool) -> list[int]:
    """Antardasha sign order within a Kalachakra mahadasha.

    Derived from Sanjay Rath's worked Rajiv Gandhi example (Apasavya-Right
    pada-2): antars run zodiacally from the MD sign, except Cancer and Leo
    are swapped — the same (Le, Cn) adjacency seen in every apasavya pada
    sequence. For savya padas the pure zodiacal order is used (theoretical;
    flagged for verification against a savya worked example).
    """
    order = [(md_sign + i) % 12 for i in range(12)]
    if apasavya:
        ci, li = order.index(3), order.index(4)
        order[ci], order[li] = order[li], order[ci]
    return order[:9]


def kalachakra_tree(birth_dt: datetime, moon_longitude: float,
                    now: datetime | None = None,
                    max_cycles: int = 3) -> dict:
    """Kalachakra mahadasha timeline (Full-cycle-fraction method).

    The Moon's nakshatra selects one of four savya/apasavya groups; the
    pada selects the nine-sign sequence and the paramayus. The pada is
    equated to the paramayus years; the Moon's elapsed fraction locates
    the opening dasha and its balance (the method "commonly accepted by
    the Pandits in India"). When the nine dashas end, the wheel continues
    by chakra continuity (other foot, same savya/apasavya, pada 1).
    Antardashas divide each mahadasha proportionally to the antar signs'
    years.
    """
    lon = moon_longitude % 360.0
    nak_idx = int(lon // NAKSHATRA_SPAN)
    pada = int((lon - nak_idx * NAKSHATRA_SPAN) // (NAKSHATRA_SPAN / 4.0)) + 1
    group = _kc_group(nak_idx)

    at = now or datetime.now(birth_dt.tzinfo)

    mahadashas = []
    cursor = birth_dt
    cur_group, cur_pada = group, pada
    first = True
    deha = jiva = None
    for _ in range(max_cycles):
        sequence, paramayus = _KC_TABLE[cur_group][cur_pada]
        apasavya = cur_group.startswith("apasavya")
        if first:
            deha, jiva = _kc_deha_jiva(cur_group, sequence)
            # Full-cycle fraction: locate the opening dasha.
            pada_start = nak_idx * NAKSHATRA_SPAN + (cur_pada - 1) * (NAKSHATRA_SPAN / 4.0)
            elapsed_frac = (lon - pada_start) / (NAKSHATRA_SPAN / 4.0)
            elapsed_years = elapsed_frac * paramayus
            acc = 0.0
            start_k = 0
            balance = 0.0
            for k, sign in enumerate(sequence):
                y = _KALACHAKRA_SIGN_YEARS[sign]
                if acc + y > elapsed_years:
                    start_k = k
                    balance = acc + y - elapsed_years
                    break
                acc += y
            else:  # Moon at the very end of the pada
                start_k, balance = 0, float(_KALACHAKRA_SIGN_YEARS[sequence[0]])
            # Rotate the first cycle to open at the running dasha.
            ordered = sequence[start_k:] + sequence[:start_k]
            first_years = ([balance] +
                           [_KALACHAKRA_SIGN_YEARS[s]
                            for s in ordered[1:]])
        else:
            ordered = list(sequence)
            first_years = [_KALACHAKRA_SIGN_YEARS[s] for s in ordered]

        for sign, years in zip(ordered, first_years):
            years_f = float(years)
            end = cursor + _days(years_f)
            # Antardashas: proportional to antar signs' years.
            antar_order = _kc_antar_order(sign, apasavya)
            total = sum(_KALACHAKRA_SIGN_YEARS[s] for s in antar_order)
            ad_cursor = cursor
            antars = []
            for a_sign in antar_order:
                a_years = years_f * _KALACHAKRA_SIGN_YEARS[a_sign] / total
                a_end = ad_cursor + _days(a_years)
                antars.append({"sign": a_sign, "start": ad_cursor,
                               "end": a_end, "years": a_years})
                ad_cursor = a_end
            mahadashas.append({"sign": sign, "start": cursor, "end": end,
                               "years": years_f, "antardashas": antars,
                               "group": cur_group, "pada": cur_pada})
            cursor = end
        first = False
        cur_group = _KC_NEXT_GROUP[cur_group]
        cur_pada = 1
        if cursor > at + _days(120):
            break

    current = None
    for md in mahadashas:
        if md["start"] <= at < md["end"]:
            ad = next((a for a in md["antardashas"]
                       if a["start"] <= at < a["end"]), None)
            current = {"mahadasha": md, "antardasha": ad, "at": at}
            break
    return {
        "mahadashas": mahadashas,
        "current": current,
        "birth_group": group,
        "birth_pada": pada,
        "birth_nakshatra_index": nak_idx,
        "deha": deha,
        "deha_en": SIGNS_EN[deha] if deha is not None else None,
        "deha_ne": SIGNS_NE[deha] if deha is not None else None,
        "jiva": jiva,
        "jiva_en": SIGNS_EN[jiva] if jiva is not None else None,
        "jiva_ne": SIGNS_NE[jiva] if jiva is not None else None,
        "note": ("Kalachakra (Full-cycle-fraction): the birth pada's nine "
                 "sign dashas open per the Moon's elapsed fraction; later "
                 "cycles continue by chakra continuity (other foot, pada 1)."),
    }
