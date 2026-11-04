"""Bikram Sambat (BS) <-> Gregorian (AD) conversion.

BS has no generating formula: month lengths (29-32 days) are set by
Nepal's Panchanga authority and published year by year. This module
therefore uses a lookup table, not arithmetic.

Table provenance (recorded here so a later reader can re-check it):
`data/bs_calendar.json` is the month-length table for BS 2000-2090
from nepkit 0.4.1 (MIT), whose own provenance records two independent
sources agreeing row-for-row over BS 2000-2090 — medic/bikram-sambat
(Apache-2.0) and sbmdkl/nepali-date-converter — plus the anchor
BS 2000-01-01 = AD 1943-04-14. Only the table (factual day counts)
is vendored here; no nepkit code is used, and the app gains no new
runtime dependency. Dates outside BS 2000-2090 (AD 1943-04-14 to
2034-04-13) raise ValueError instead of extrapolating, because later
years are not yet settled by the Panchanga authority.
"""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

_PATH = Path(__file__).resolve().parent.parent / "data" / "bs_calendar.json"
_TABLE = {entry["year"]: entry["months"] for entry in json.loads(_PATH.read_text(encoding="utf-8"))}
_MIN_YEAR, _MAX_YEAR = min(_TABLE), max(_TABLE)
_ANCHOR_BS = (2000, 1, 1)
_ANCHOR_AD = date(1943, 4, 14)

BS_MONTHS_EN = ["Baisakh", "Jestha", "Ashadh", "Shrawan", "Bhadra", "Ashwin",
                "Kartik", "Mangsir", "Poush", "Magh", "Falgun", "Chaitra"]
BS_MONTHS_NE = ["बैशाख", "जेठ", "असार", "श्रावण", "भदौ", "आश्विन",
                "कार्तिक", "मंसिर", "पौष", "माघ", "फाल्गुन", "चैत्र"]
_NEPALI_DIGITS = "०१२३४५६७८९"


def to_nepali_digits(text: str) -> str:
    return "".join(_NEPALI_DIGITS[int(c)] if c.isdigit() else c for c in text)


def days_in_bs_month(year: int, month: int) -> int:
    if year not in _TABLE or not 1 <= month <= 12:
        raise ValueError(f"BS date out of supported range: {year}-{month}")
    return _TABLE[year][month - 1]


def _bs_to_offset(year: int, month: int, day: int) -> int:
    if year not in _TABLE or not 1 <= month <= 12:
        raise ValueError(f"BS date out of supported range: {year}-{month:02d}-{day:02d}")
    if not 1 <= day <= _TABLE[year][month - 1]:
        raise ValueError(f"invalid BS day: {year}-{month:02d}-{day:02d}")
    offset = 0
    for y in range(_MIN_YEAR, year):
        offset += sum(_TABLE[y])
    for m in range(1, month):
        offset += _TABLE[year][m - 1]
    return offset + (day - 1)


def bs_to_ad(year: int, month: int, day: int) -> date:
    return _ANCHOR_AD + timedelta(days=_bs_to_offset(year, month, day))


def ad_to_bs(day: date) -> dict:
    offset = (day - _ANCHOR_AD).days
    if offset < 0:
        raise ValueError(f"AD date before supported range: {day}")
    remaining = offset
    year = _MIN_YEAR
    while True:
        year_days = sum(_TABLE[year]) if year in _TABLE else None
        if year_days is None or remaining < year_days:
            break
        remaining -= year_days
        year += 1
    if year not in _TABLE:
        raise ValueError(f"AD date beyond supported range: {day}")
    month = 1
    while remaining >= _TABLE[year][month - 1]:
        remaining -= _TABLE[year][month - 1]
        month += 1
    return {
        "year": year, "month": month, "day": remaining + 1,
        "month_en": BS_MONTHS_EN[month - 1], "month_ne": BS_MONTHS_NE[month - 1],
        "iso": f"{year}-{month:02d}-{remaining + 1:02d}",
        "formatted_en": f"{remaining + 1} {BS_MONTHS_EN[month - 1]} {year}",
        "formatted_ne": f"{to_nepali_digits(str(remaining + 1))} {BS_MONTHS_NE[month - 1]} {to_nepali_digits(str(year))}",
    }


def bs_date_dict(year: int, month: int, day: int) -> dict:
    ad = bs_to_ad(year, month, day)
    return {**ad_to_bs(ad), "ad": ad.isoformat()}
