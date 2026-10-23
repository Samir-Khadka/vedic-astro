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


def _subdivide(start: datetime, total_years: float, first_lord: str) -> list[dict]:
    """Split a period of `total_years` into 9 sub-periods beginning with
    `first_lord`, each proportional to its lord's Vimshottari years."""
    seq = DASHA_SEQUENCE
    i0 = seq.index(first_lord)
    periods = []
    cursor = start
    for k in range(9):
        lord = seq[(i0 + k) % 9]
        years = total_years * DASHA_YEARS[lord] / 120.0
        end = cursor + _days(years)
        periods.append({"lord": lord, "start": cursor, "end": end, "years": years})
        cursor = end
    return periods


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

    # Pratyantardashas only for the running antardasha (keeps payload sane).
    if current:
        md = current["mahadasha"]
        ad = current["antardasha"]
        ad["pratyantardashas"] = _subdivide(ad["start"], ad["years"], ad["lord"])
        pd = next(
            (p for p in ad["pratyantardashas"] if p["start"] <= current["at"] < p["end"]),
            None,
        )
        current["pratyantardasha"] = pd
    return {"mahadashas": mahadashas, "current": current, "balance_years": balance_years}


def _resolve(mahadashas: list[dict], at: datetime) -> dict | None:
    for md in mahadashas:
        if md["start"] <= at < md["end"]:
            for ad in md["antardashas"]:
                if ad["start"] <= at < ad["end"]:
                    return {"mahadasha": md, "antardasha": ad, "at": at}
            return {"mahadasha": md, "antardasha": None, "at": at}
    return None
