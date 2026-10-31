"""Classical special lagnas — Hora, Bhava, Ghati, Varnada, Shri, Indu.

BPHS Chapter 5 (verified against the Sanskrit text and standard software):
- Bhava Lagna: Sun's longitude at sunrise + ishta-ghatis x 6 deg
  (one sign per 5 ghatis / 120 min).
- Hora Lagna: Sun's longitude at sunrise + ishta-ghatis x 12 deg
  (one sign per 2.5 ghatis / 60 min).
- Ghati Lagna: Sun's longitude at sunrise + ishta-ghatis x 30 deg
  (one sign per ghati / 24 min; vighatis/2 give the degrees).
  For night births the *previous* sunrise is the reference.
- Varnada Lagna: from Janma Lagna + Hora Lagna signs — count A from
  Aries (odd Lagna) or Pisces-reversed (even Lagna) to the Lagna sign,
  B likewise to the Hora Lagna sign; add when the parities match,
  subtract (larger minus smaller) when they differ; expunge multiples
  of 12; count the result from Aries/Pisces per the Lagna's parity.
- Shri Lagna: Lagna longitude + (Moon's fraction through its nakshatra
  x 360 deg) — the JHora/P.V.R. Narasimha Rao method.
- Indu Lagna: 9th lords from Lagna and from Moon -> kalas
  (Sun 30, Moon 16, Mars 6, Mercury 8, Jupiter 10, Venus 12, Saturn 1);
  sum, divide by 12, count the remainder from the Moon's sign
  (remainder 0 -> 12); Indu takes the Moon's degree in its sign.

All longitudes here are sidereal under the computation's ayanamsa.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from . import ephemeris

GHATI_MINUTES = 24.0

# Kalamsha (rays) for Indu Lagna.
KALAS = {"Sun": 30, "Moon": 16, "Mars": 6, "Mercury": 8,
         "Jupiter": 10, "Venus": 12, "Saturn": 1}

SIGN_LORDS = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
              "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]


def _udaya_and_ghatis(birth_dt: datetime, lat: float, lon: float,
                      tz_name: str) -> tuple[float, float]:
    """Return (Sun's sidereal longitude at the reference sunrise, ishta ghatis).

    Reference sunrise is the sunrise of the birth civil day; for a birth
    before that sunrise (night birth) the previous day's sunrise is used,
    per BPHS.
    """
    from datetime import date as date_cls

    rise, _set = ephemeris.sunrise_sunset(birth_dt.date(), lat, lon, tz_name)
    if rise is None or birth_dt < rise:
        prev = birth_dt.date() - timedelta(days=1)
        rise, _set = ephemeris.sunrise_sunset(prev, lat, lon, tz_name)
    if rise is None:
        raise ValueError("Cannot determine sunrise for special lagnas.")
    ghatis = (birth_dt - rise).total_seconds() / 60.0 / GHATI_MINUTES
    sun_lon = ephemeris.planet_longitude_at("Sun", ephemeris.to_julian_day(rise))
    return sun_lon, ghatis


def hora_bhava_ghati(birth_dt: datetime, lat: float, lon: float,
                     tz_name: str) -> dict[str, float]:
    """Longitudes of the sunrise-anchored trio (degrees, 0-360)."""
    udaya, ghatis = _udaya_and_ghatis(birth_dt, lat, lon, tz_name)
    return {
        "bhava_lagna": (udaya + ghatis * 6.0) % 360.0,
        "hora_lagna": (udaya + ghatis * 12.0) % 360.0,
        "ghati_lagna": (udaya + ghatis * 30.0) % 360.0,
    }


def _count_to(sign: int, odd_lagna: bool) -> int:
    """1-based count to `sign` (0-11) from Aries (odd) or Pisces reversed (even)."""
    if odd_lagna:
        return sign + 1
    return (11 - sign) + 1


def varnada_sign(lagna_sign: int, hora_sign: int) -> int:
    """Varnada Lagna sign (0-11) from Janma Lagna and Hora Lagna signs."""
    lagna_odd = lagna_sign % 2 == 0  # Aries=0 is "odd" in the classical sense
    hora_odd = hora_sign % 2 == 0
    a = _count_to(lagna_sign, lagna_odd)
    b = _count_to(hora_sign, hora_odd)
    if lagna_odd == hora_odd:
        c = a + b
    else:
        c = abs(a - b)
    c = c % 12
    if c == 0:
        c = 12
    # Count the result from Aries / Pisces per the *Lagna's* parity.
    if lagna_odd:
        return (c - 1) % 12
    return (12 - c) % 12


def shri_lagna_longitude(lagna_lon: float, moon_lon: float) -> float:
    """Shri Lagna longitude: lagna + Moon's nakshatra-fraction x 360."""
    nak_span = 360.0 / 27.0
    frac = ((moon_lon % 360.0) % nak_span) / nak_span
    return (lagna_lon + frac * 360.0) % 360.0


def indu_lagna(lagna_sign: int, moon_sign: int, moon_degree_in_sign: float) -> tuple[int, float]:
    """Return (Indu Lagna sign, longitude)."""
    lord_lagna_9 = SIGN_LORDS[(lagna_sign + 8) % 12]
    lord_moon_9 = SIGN_LORDS[(moon_sign + 8) % 12]
    total = KALAS[lord_lagna_9] + KALAS[lord_moon_9]
    rem = total % 12
    steps = rem if rem != 0 else 12
    indu_sign = (moon_sign + steps - 1) % 12
    return indu_sign, (indu_sign * 30.0 + moon_degree_in_sign) % 360.0


def compute_special_lagnas(birth_dt: datetime, lat: float, lon: float, tz_name: str,
                           lagna_lon: float, lagna_sign: int,
                           moon_lon: float, moon_sign: int,
                           moon_degree_in_sign: float) -> dict[str, dict]:
    """All six classical lagnas as {key: {longitude, sign}}.

    Raises ValueError when sunrise cannot be determined (polar day/night).
    """
    trio = hora_bhava_ghati(birth_dt, lat, lon, tz_name)
    hora_sign = int(trio["hora_lagna"] // 30)
    varnada = varnada_sign(lagna_sign, hora_sign)
    shri = shri_lagna_longitude(lagna_lon, moon_lon)
    indu_sign, indu_lon = indu_lagna(lagna_sign, moon_sign, moon_degree_in_sign)

    def entry(longitude: float) -> dict:
        return {"longitude": round(longitude, 4), "sign": int(longitude // 30) % 12}

    return {
        "hora_lagna": entry(trio["hora_lagna"]),
        "bhava_lagna": entry(trio["bhava_lagna"]),
        "ghati_lagna": entry(trio["ghati_lagna"]),
        "varnada_lagna": {"longitude": round(varnada * 30.0, 4), "sign": varnada},
        "shri_lagna": entry(shri),
        "indu_lagna": {"longitude": round(indu_lon, 4), "sign": indu_sign},
    }
