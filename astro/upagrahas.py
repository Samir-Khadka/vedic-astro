"""Upagrahas (shadow planets) — Dhuma, Vyatipata, Parivesha, Indrachapa,
Upaketu, Gulika/Mandi.

The solar family (BPHS) is derived from the Sun's sidereal longitude:
- Dhuma      = Sun + 133 deg 20'
- Vyatipata  = 360 - Dhuma
- Parivesha  = Vyatipata + 180 (mod 360)
- Indrachapa = 360 - Parivesha
- Upaketu    = Sun + 30

Gulika (day birth) / Mandi (night birth): the day (sunrise->sunset) or
night (sunset->sunrise) is divided into 8 equal segments; the segment
ruled by Saturn is the Gulika/Mandi segment, and the Upagraha's longitude
is the Ascendant at the START of that segment (BPHS).

Day segments (1-based from sunrise): Sun 7, Mon 6, Tue 5, Wed 4, Thu 3,
Fri 2, Sat 1. Night segments: the first segment is ruled by the weekday
lord 5th from the day's lord (Sun day -> Jupiter), then in weekday order;
the 8th segment is lordless in both cases.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from . import ephemeris

WEEKDAY_LORDS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

# Python weekday() Mon=0..Sun=6 -> segment index (1-based) of Saturn's part.
DAY_GULIKA_SEGMENT = {0: 6, 1: 5, 2: 4, 3: 3, 4: 2, 5: 1, 6: 7}


def solar_upagrahas(sun_longitude: float) -> dict[str, float]:
    """The five Sun-derived upagrahas (longitudes 0-360)."""
    dhuma = (sun_longitude + 133.0 + 20.0 / 60.0) % 360.0
    vyatipata = (360.0 - dhuma) % 360.0
    parivesha = (vyatipata + 180.0) % 360.0
    indrachapa = (360.0 - parivesha) % 360.0
    upaketu = (sun_longitude + 30.0) % 360.0
    return {
        "dhuma": dhuma,
        "vyatipata": vyatipata,
        "parivesha": parivesha,
        "indrachapa": indrachapa,
        "upaketu": upaketu,
    }


def _asc_at(dt: datetime, lat: float, lon: float) -> float:
    jd = ephemeris.to_julian_day(dt)
    return ephemeris.ascendant(jd, lat, lon)


def gulika_mandi(birth_dt: datetime, sunrise: datetime | None,
                 sunset: datetime | None, lat: float, lon: float) -> dict[str, dict | None]:
    """Gulika (day) and Mandi (night) longitudes + the segment used.

    Each entry is {longitude, sign, segment, segment_start} or None when
    sunrise/sunset is unavailable (polar day/night).
    """
    def entry(dt: datetime | None) -> dict | None:
        if dt is None:
            return None
        longitude = _asc_at(dt, lat, lon)
        return {"longitude": round(longitude, 4), "sign": int(longitude // 30) % 12,
                "at": dt.isoformat()}

    if sunrise is None or sunset is None:
        return {"gulika": None, "mandi": None}

    weekday = birth_dt.weekday()  # Mon=0..Sun=6
    day_len = (sunset - sunrise).total_seconds()
    seg = DAY_GULIKA_SEGMENT[weekday]
    gulika_start = sunrise + (seg - 1) * (day_len / 8) * timedelta(seconds=1)

    # Night: first segment ruled by the weekday lord 5th from the day lord.
    sun0 = (weekday + 1) % 7  # Sun=0..Sat=6
    first_lord = (sun0 + 4) % 7
    sat_segment = next(i for i in range(1, 8) if (first_lord + i - 1) % 7 == 6)
    night_len = (sunrise + timedelta(days=1) - sunset).total_seconds()
    mandi_start = sunset + (sat_segment - 1) * (night_len / 8) * timedelta(seconds=1)

    g = entry(gulika_start)
    if g:
        g["segment"] = seg
    m = entry(mandi_start)
    if m:
        m["segment"] = sat_segment
    return {"gulika": g, "mandi": m}


def compute_upagrahas(sun_longitude: float, birth_dt: datetime,
                      sunrise: datetime | None, sunset: datetime | None,
                      lat: float, lon: float) -> dict[str, dict | None]:
    """All six upagrahas as {key: {longitude, sign} | None}."""
    out: dict[str, dict | None] = {}
    for key, longitude in solar_upagrahas(sun_longitude).items():
        out[key] = {"longitude": round(longitude, 4), "sign": int(longitude // 30) % 12}
    gm = gulika_mandi(birth_dt, sunrise, sunset, lat, lon)
    out["gulika"] = gm["gulika"]
    out["mandi"] = gm["mandi"]
    return out
