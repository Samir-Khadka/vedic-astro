"""Transits: the paths the coverage report showed as untested —

- ``prev_ingress`` (whole function: no caller in production or tests,
  so its direct-scan and memo branches were never exercised);
- the ``ValueError`` guards in ``next_ingress`` / ``prev_ingress`` /
  ``ingress_jd``;
- the direct-scan fallback inside ``saturn_moon_span`` (added with the
  shared ingress walk) and its defensive ``None`` return.
"""
from datetime import datetime

import pytest

from astro import ephemeris, transits

JD_2026 = ephemeris.to_julian_day(datetime(2026, 11, 2, 0, 0))
JD_SPAN = ephemeris.to_julian_day(datetime(2024, 1, 1, 0, 0))


@pytest.fixture(autouse=True)
def _clear_memo():
    transits._INGRESS_MEMO.clear()
    yield
    transits._INGRESS_MEMO.clear()


def test_prev_ingress_pinned_dates():
    """prev_ingress returns the ingress into the sign occupied at jd,
    with from/to signs — pinned against the live ephemeris."""
    expected = {
        # (planet, date, from_sign, to_sign)
        "Saturn": ("2025-03-29", 10, 11),
        "Jupiter": ("2026-10-31", 3, 4),
        "Rahu": ("2025-05-29", 11, 10),
        "Sun": ("2026-10-17", 5, 6),
        "Mars": ("2026-09-18", 2, 3),
    }
    for planet, (date, from_sign, to_sign) in expected.items():
        prev = transits.prev_ingress(planet, JD_2026)
        assert prev["planet"] == planet
        assert prev["date"] == date, planet
        assert prev["from_sign"] == from_sign, planet
        assert prev["to_sign"] == to_sign, planet
        assert prev["to_sign"] == transits._sign_at(planet, JD_2026)
        assert "jd" in prev


def test_prev_ingress_round_trips_next_ingress():
    """prev_ingress just after an ingress must return that same ingress
    (same date and to_sign) — the two scanners agree on the moment."""
    for planet in ("Saturn", "Jupiter", "Rahu", "Sun", "Mars"):
        nxt = transits.next_ingress(planet, JD_2026)
        y, m, d = map(int, nxt["date"].split("-"))
        jd_after = ephemeris.to_julian_day(datetime(y, m, d, 12, 0)) + 1.0
        back = transits.prev_ingress(planet, jd_after)
        assert back["date"] == nxt["date"], planet
        assert back["to_sign"] == nxt["to_sign"], planet
        assert back["from_sign"] == nxt["from_sign"], planet


def test_prev_ingress_memo_matches_direct_scan():
    """The memo path must agree with the direct backward scan on date
    and signs, and on the JD to within the bisection tolerance. The
    memo must cover [jd - max_days, jd], so the chain is built back
    1500 days, past the default 1200-day window. (The two paths bisect
    different brackets, so their JDs differ by a few milliseconds —
    both are within _BISECT_TOL of the true ingress and land on the
    same UTC date.)"""
    transits.ingress_chain("Saturn", JD_2026 - 1500.0, JD_2026 + 100.0)
    via_memo = transits.prev_ingress("Saturn", JD_2026)
    transits._INGRESS_MEMO.clear()
    direct = transits.prev_ingress("Saturn", JD_2026)
    for key in ("planet", "from_sign", "to_sign", "date"):
        assert via_memo[key] == direct[key], key
    assert abs(via_memo["jd"] - direct["jd"]) < transits._BISECT_TOL


def test_prev_ingress_memo_without_events_raises():
    """A covering walk with no ingress inside the window must raise,
    the same as the direct scan would — not return a stale ingress."""
    # Seed a 20-day walk around jd: it covers [jd-10, jd] but holds no
    # ingress (Saturn's last one was ~583 days earlier).
    transits._ingress_events("Saturn", JD_2026 - 10.0, JD_2026 + 10.0)
    with pytest.raises(ValueError, match="no previous ingress"):
        transits.prev_ingress("Saturn", JD_2026, max_days=10.0)


def test_prev_ingress_no_ingress_in_window_raises():
    """A window shorter than the planet's stay in a sign has no previous
    ingress — ValueError, not a silently wrong date."""
    with pytest.raises(ValueError, match="no previous ingress"):
        transits.prev_ingress("Saturn", JD_2026, max_days=1.0)


def test_next_ingress_direct_scan_no_ingress_raises():
    """Same guard on the direct-scan path (no covering walk): a window
    shorter than the planet's stay raises instead of returning a
    wrong date."""
    with pytest.raises(ValueError, match="no ingress found"):
        transits.next_ingress("Saturn", JD_2026, max_days=1.0)


def test_next_ingress_memo_without_events_raises():
    """A covering walk that contains no ingress inside the window must
    raise, the same as the direct scan would — not return a stale one."""
    # Seed a 1-day walk for Saturn: it covers [jd, jd+1] but holds no
    # ingress (Saturn stays ~2.5 years per sign).
    transits._ingress_events("Saturn", JD_2026, JD_2026 + 1.0)
    with pytest.raises(ValueError, match="no ingress found"):
        transits.next_ingress("Saturn", JD_2026, max_days=1.0)


def test_ingress_jd_no_ingress_raises(monkeypatch):
    """ingress_jd gives up after 4000 days of no sign change instead of
    scanning forever — forced here by a stubbed sign that never moves."""
    monkeypatch.setattr(transits, "_sign_at", lambda planet, jd: 0)
    with pytest.raises(ValueError, match="no ingress found"):
        transits.ingress_jd("Saturn", JD_2026)


def test_saturn_moon_span_direct_scan_fallback(monkeypatch):
    """When the shared walk runs out of future events, the span must
    fall back to direct ingress_jd scans and still land on the same
    patro dates (the retrograde-dip case from test_engine)."""
    events = transits._ingress_events("Saturn", JD_SPAN - 3650.0, JD_SPAN + 20 * 365.25)
    past_only = [e for e in events if e[0] <= JD_SPAN]
    assert past_only, "fixture must hold past events"

    def _truncated(planet, lo, hi):
        assert planet == "Saturn"
        return list(past_only)

    monkeypatch.setattr(transits, "_ingress_events", _truncated)
    span = transits.saturn_moon_span(11, JD_SPAN)  # Moon Pisces
    assert span is not None
    assert span["start"] == "2022-04-29"       # first entry, not the 2023 re-entry
    assert span["peak_start"] == "2025-03-29"
    assert span["setting_start"] == "2027-06-02"
    assert span["end"] == "2030-04-17"         # final exit, not the 2029 first entry


def test_saturn_moon_span_returns_none_when_targets_unfindable(monkeypatch):
    """The defensive None — Saturn is in the span but the boundaries
    cannot be resolved — must be reachable, not a crash. Forced by
    stubbing the walk empty and every direct scan to one fixed JD, so
    at most one target sign is ever recorded in 16 iterations."""
    monkeypatch.setattr(transits, "_ingress_events", lambda planet, lo, hi: [])
    monkeypatch.setattr(transits, "ingress_jd", lambda planet, jd: JD_SPAN + 100000.0)
    assert transits.saturn_moon_span(11, JD_SPAN) is None
