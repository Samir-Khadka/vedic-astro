"""Ayanamsa selection — the sidereal zodiac offset, done the classical way.

Professional software (Parashara's Light, Jagannatha Hora, Kala) lets the
user choose the ayanamsa; every longitude in the chart then follows that
choice. This module owns the registry of supported modes and the
thread-safe "current mode" used by the ephemeris layer.

Threading: pyswisseph keeps the sidereal mode in thread-local state, and
FastAPI/uvicorn serve sync endpoints from a threadpool (the 2026-10-23
worker-thread ayanamsa bug was exactly this). The mode is therefore held
in a ContextVar — set once per computation in engine.compute_kundali —
and re-asserted via swe.set_sid_mode() in every public ephemeris entry
point, exactly like the old _ensure_lahiri() did.
"""
from __future__ import annotations

from contextvars import ContextVar

import swisseph as swe

# True Chitra is not available in Swiss Ephemeris 2.10 (this build); the
# four below cover the schools that matter: Lahiri (default, official
# Indian), Raman, Krishnamurti (KP), Yukteshwar.
AYANAMSA_MODES: dict[str, tuple[str, int]] = {
    "lahiri": ("Lahiri (Chitrapaksha)", swe.SIDM_LAHIRI),
    "raman": ("Raman", swe.SIDM_RAMAN),
    "krishnamurti": ("Krishnamurti (KP)", swe.SIDM_KRISHNAMURTI),
    "yukteshwar": ("Yukteshwar", swe.SIDM_YUKTESHWAR),
}
DEFAULT_AYANAMSA = "lahiri"

_current: ContextVar[str] = ContextVar("vedic_astro_ayanamsa", default=DEFAULT_AYANAMSA)


def validate_ayanamsa(name: str | None) -> str:
    """Normalise a user-supplied ayanamsa key; raises ValueError if unknown."""
    key = (name or DEFAULT_AYANAMSA).strip().lower()
    if key not in AYANAMSA_MODES:
        raise ValueError(
            f"Unknown ayanamsa '{name}'. Supported: {', '.join(sorted(AYANAMSA_MODES))}."
        )
    return key


def set_ayanamsa(name: str | None) -> str:
    """Set the ayanamsa for the current computation (thread). Returns the key."""
    key = validate_ayanamsa(name)
    _current.set(key)
    swe.set_sid_mode(AYANAMSA_MODES[key][1])
    return key


def current_ayanamsa() -> str:
    return _current.get()


def ensure_ayanamsa() -> str:
    """Re-assert the current thread's sidereal mode (call before swe use)."""
    key = _current.get()
    swe.set_sid_mode(AYANAMSA_MODES[key][1])
    return key


def mode_name(key: str) -> str:
    return AYANAMSA_MODES[validate_ayanamsa(key)][0]


def ayanamsa_value_ut(jd: float) -> float:
    """Ayanamsa in degrees at Julian day `jd` under the current mode."""
    ensure_ayanamsa()
    return swe.get_ayanamsa_ut(jd)
