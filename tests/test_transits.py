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
    scanning forever — forced here by a stubbed longitude that never
    moves (the scan reads the longitude directly for its step size)."""
    monkeypatch.setattr(ephemeris, "planet_longitude_at",
                        lambda name, jd: 15.0)
    with pytest.raises(ValueError, match="no ingress found"):
        transits.ingress_jd("Saturn", JD_2026)


# --- Longitude-aware scan steps (2026-11-24) ---------------------------
#
# The ingress scan used to walk _STEP_DAYS at a time (Saturn: 10 days,
# ~91 steps per sign); it now takes longitude-aware steps that can
# never cross a sign boundary (see _scan_step / _VMAX_DEG_PER_DAY),
# falling back to exactly _STEP_DAYS near a boundary. These tests pin
# the step sizes, the no-crossing invariant, the equivalence with the
# old fixed-step walk, and the cost.


def test_scan_step_sizes():
    """Far from a boundary the scan takes wide steps; near one it
    falls back to exactly _STEP_DAYS (the old scan's resolution)."""
    assert transits._scan_step("Saturn", 15.0) == pytest.approx(15.0 / 0.20)
    assert transits._scan_step("Saturn", 29.9) == transits._STEP_DAYS["Saturn"]
    assert transits._scan_step("Saturn", 0.1) == transits._STEP_DAYS["Saturn"]
    assert transits._scan_step("Moon", 15.0) == pytest.approx(15.0 / 23.0)
    assert transits._scan_step("Sun", 15.0) == pytest.approx(15.0 / 1.50)


def test_scan_step_never_crosses_a_boundary():
    """The safety invariant itself, pinned: a step wider than the
    fixed step must never carry the planet into another sign — in
    either direction, for every planet. Seeded sweep over real
    longitudes (a step that could cross would break the equivalence
    test below by skipping an ingress)."""
    import random

    rng = random.Random(20261124)
    jd0 = ephemeris.to_julian_day(datetime(2020, 1, 1, 0, 0))
    jd1 = ephemeris.to_julian_day(datetime(2032, 1, 1, 0, 0))
    for planet in ("Saturn", "Jupiter", "Rahu", "Ketu", "Mars", "Sun",
                   "Venus", "Mercury", "Moon"):
        for _ in range(100):
            jd = rng.uniform(jd0, jd1)
            lon = ephemeris.planet_longitude_at(planet, jd)
            step = transits._scan_step(planet, lon)
            if step <= transits._STEP_DAYS[planet]:
                continue  # fixed steps may cross; only wide steps are pinned
            sign = transits._sign_at(planet, jd)
            assert transits._sign_at(planet, jd + step) == sign, (planet, jd, lon, step)
            assert transits._sign_at(planet, jd - step) == sign, (planet, jd, lon, step)


def _old_ingress_jd(planet, jd_from):
    """The pre-2026-11-24 implementation, kept as the reference:
    fixed _STEP_DAYS steps, same bisection."""
    start_sign = transits._sign_at(planet, jd_from)
    step = transits._STEP_DAYS[planet]
    lo = jd_from
    hi = jd_from + step
    while transits._sign_at(planet, hi) == start_sign:
        lo = hi
        hi += step
        if hi - jd_from > 4000:
            raise ValueError("no ingress found")
    return transits._bisect_ingress(planet, lo, hi, start_sign, forward=True)


@pytest.mark.parametrize("planet", ["Saturn", "Jupiter", "Rahu", "Ketu",
                                    "Mars", "Sun", "Venus", "Mercury", "Moon"])
def test_scan_matches_fixed_step_walk(planet):
    """Every ingress in 2024-2027 must match the old fixed-step walk:
    same count, same signs, same UTC dates, JDs within ~90 s (the
    true node wobbles across the boundary, so two methods can land on
    adjacent genuine crossings seconds apart)."""
    jd0 = ephemeris.to_julian_day(datetime(2024, 1, 1, 0, 0))
    jd1 = ephemeris.to_julian_day(datetime(2027, 1, 1, 0, 0))
    transits._INGRESS_MEMO.clear()
    new_events = transits._ingress_events(planet, jd0, jd1)
    old_events = []
    cursor = jd0
    while cursor < jd1:
        njd = _old_ingress_jd(planet, cursor)
        if njd > jd1:
            break
        old_events.append((njd, transits._sign_at(planet, njd + 0.01)))
        cursor = njd + 1.0
    assert new_events, f"fixture must hold an ingress for {planet}"
    assert len(new_events) == len(old_events), planet
    for (nj, ns), (oj, os_) in zip(new_events, old_events):
        assert ns == os_, (planet, nj, oj)
        _assert_same_crossing(nj, oj)


def test_saturn_walk_scan_cost(monkeypatch):
    """The speedup itself, pinned: the 100-year Saturn walk must cost
    far fewer ephemeris evaluations than the ~8k the fixed 10-day
    steps needed (86 ingresses, measured 2,279 calls). Counts
    planet_longitude_at, which every single-planet lookup routes
    through."""
    calls = {"n": 0}
    orig = ephemeris.planet_longitude_at

    def counting(name, jd):
        calls["n"] += 1
        return orig(name, jd)

    monkeypatch.setattr(ephemeris, "planet_longitude_at", counting)
    transits._INGRESS_MEMO.clear()
    jd_birth = ephemeris.to_julian_day(datetime(1998, 5, 14, 6, 30))
    events = transits._ingress_events("Saturn", jd_birth, jd_birth + 100 * 365.25)
    assert len(events) > 40, len(events)  # a century of Saturn holds 40+ ingresses
    assert calls["n"] < 3000, calls["n"]


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


# --- Illinois false-position bisection (2026-11-18) -------------------------
#
# _bisect_ingress used to halve the bracket on the sign (~24 calc_ut for
# Saturn's 10-day step); it now interpolates on the sidereal longitude's
# distance to the sign boundary (Illinois false position, ~9 evals).
# These tests pin the equivalence: same crossing, same UTC date.


def _plain_bisect(planet, lo, hi, start_sign, forward):
    """The pre-2026-11-18 implementation, kept as the reference: pure
    midpoint bisection on the sign."""
    for _ in range(64):
        mid = (lo + hi) / 2.0
        past = transits._sign_at(planet, mid) != start_sign
        if past:
            if forward:
                hi = mid
            else:
                lo = mid
        elif forward:
            lo = mid
        else:
            hi = mid
        if hi - lo < transits._BISECT_TOL:
            break
    return (lo + hi) / 2.0


def _forward_brackets(planet, jd0, jd1):
    """(lo, hi, start_sign) triples holding a sign change, forward scan."""
    step = transits._STEP_DAYS[planet]
    out = []
    lo, s0 = jd0, transits._sign_at(planet, jd0)
    while lo < jd1:
        hi = lo + step
        s1 = transits._sign_at(planet, hi)
        if s1 != s0:
            out.append((lo, hi, s0))
            s0 = s1
        lo = hi
    return out


def _backward_brackets(planet, jd0, jd1):
    """(lo, hi, start_sign) triples holding a sign change, backward scan:
    sign(lo) != start_sign, sign(hi) == start_sign."""
    step = transits._STEP_DAYS[planet]
    out = []
    hi, s1 = jd1, transits._sign_at(planet, jd1)
    while hi > jd0:
        lo = hi - step
        s0 = transits._sign_at(planet, lo)
        if s0 != s1:
            out.append((lo, hi, s1))
            s1 = s0
        hi = lo
    return out


def _assert_same_crossing(a, b):
    # Same UTC date (what the API reports) and within ~90 seconds — the
    # true node wobbles across the boundary, so two methods can land on
    # adjacent genuine crossings up to ~20 s apart (measured over a
    # 12-year sweep); a wrong crossing would be days off.
    assert ephemeris.jd_to_date_str(a) == ephemeris.jd_to_date_str(b)
    assert abs(a - b) < 1e-3


@pytest.mark.parametrize("planet", ["Saturn", "Jupiter", "Rahu", "Ketu",
                                    "Mars", "Sun", "Venus", "Mercury", "Moon"])
def test_bisect_forward_matches_plain_bisection(planet):
    """Every ingress bracket in 2024-2027 must bisect to the same
    crossing as plain bisection — including retrograde dips (Mars,
    Mercury, Venus) and the backwards-moving nodes (Rahu/Ketu)."""
    jd0 = ephemeris.to_julian_day(datetime(2024, 1, 1, 0, 0))
    jd1 = ephemeris.to_julian_day(datetime(2027, 1, 1, 0, 0))
    brackets = _forward_brackets(planet, jd0, jd1)
    assert brackets, f"fixture must hold an ingress for {planet}"
    for lo, hi, start_sign in brackets:
        new = transits._bisect_ingress(planet, lo, hi, start_sign, True)
        old = _plain_bisect(planet, lo, hi, start_sign, True)
        _assert_same_crossing(new, old)


@pytest.mark.parametrize("planet", ["Saturn", "Mars", "Ketu", "Moon"])
def test_bisect_backward_matches_plain_bisection(planet):
    """The prev_ingress direction (forward=False) must agree too."""
    jd0 = ephemeris.to_julian_day(datetime(2024, 1, 1, 0, 0))
    jd1 = ephemeris.to_julian_day(datetime(2027, 1, 1, 0, 0))
    brackets = _backward_brackets(planet, jd0, jd1)
    assert brackets, f"fixture must hold an ingress for {planet}"
    for lo, hi, start_sign in brackets:
        new = transits._bisect_ingress(planet, lo, hi, start_sign, False)
        old = _plain_bisect(planet, lo, hi, start_sign, False)
        _assert_same_crossing(new, old)


def test_bisect_iteration_budget(monkeypatch):
    """The speedup itself, pinned: one bisection must cost far fewer
    ephemeris evaluations than the ~24 that halving Saturn's 10-day
    bracket needed. Counts every planet_longitude_at call (the sign
    checks route through it too), so a revert to plain bisection
    fails this test."""
    calls = {"n": 0}
    orig = ephemeris.planet_longitude_at

    def counting(name, jd):
        calls["n"] += 1
        return orig(name, jd)

    monkeypatch.setattr(ephemeris, "planet_longitude_at", counting)
    jd0 = ephemeris.to_julian_day(datetime(2026, 1, 1, 0, 0))
    jd1 = ephemeris.to_julian_day(datetime(2027, 1, 1, 0, 0))
    evals = []
    for planet in ("Saturn", "Jupiter", "Sun", "Mercury", "Ketu"):
        for lo, hi, start_sign in _forward_brackets(planet, jd0, jd1):
            before = calls["n"]
            transits._bisect_ingress(planet, lo, hi, start_sign, True)
            evals.append(calls["n"] - before)
    assert evals, "fixture must hold ingress brackets"
    assert max(evals) <= 20, f"slowest bisection took {max(evals)} evals"
    assert sum(evals) / len(evals) <= 12, f"mean {sum(evals)/len(evals):.1f} evals"
