"""Transits (Gochar) — current signs of the grahas plus the next sign
ingress (pravesh) dates for the slow movers, computed by bracketing the
sign change in Julian days and bisecting on the sidereal longitude.

Dates are the UTC calendar dates on which the ingress occurs (transits
are global events; the exact local time varies by longitude, so the
table reports dates, matching how patros print them).
"""
from __future__ import annotations

from datetime import datetime, timezone

from . import ephemeris
from .names import SIGNS_EN, SIGNS_NE

_STEP_DAYS = {
    "Saturn": 10.0, "Jupiter": 5.0, "Rahu": 5.0, "Ketu": 5.0,
    "Mars": 2.0, "Sun": 1.0, "Venus": 1.0, "Mercury": 1.0, "Moon": 0.25,
}
INGRESS_PLANETS = ["Saturn", "Jupiter", "Rahu", "Ketu", "Mars", "Sun"]


# Max |sidereal speed| (deg/day) per planet — measured 2026-11-24 over
# 100 years of daily samples (Saturn 0.13, Jupiter 0.24, Mars 0.79, Sun
# 1.02, Venus 1.26, Mercury 2.20, Moon 15.38, true node 0.25; the node
# was also sampled hourly over 2 years: 0.23). Each bound carries
# ~1.5-2.4x headroom over the measured maximum, and the scan step below
# only ever advances the distance to the nearest sign boundary at that
# speed — so a step can never carry the planet across a boundary, and
# a retrograde dip (cross and come back: over twice that distance)
# would need a true speed above 2x the bound. A sign change is
# therefore only ever detected in a step of exactly _STEP_DAYS,
# exactly as the old fixed-step scan detected it.
_VMAX_DEG_PER_DAY = {
    "Saturn": 0.20, "Jupiter": 0.35, "Rahu": 0.60, "Ketu": 0.60,
    "Mars": 1.20, "Sun": 1.50, "Venus": 1.90, "Mercury": 3.30, "Moon": 23.0,
}


def _scan_step(planet: str, lon: float) -> float:
    """Days to advance the ingress scan from sidereal longitude `lon`.

    Far from a sign boundary the planet cannot reach one within the
    step, so those steps skip dead walking (Saturn mid-sign: 37.5 days
    instead of 10); near a boundary the step is exactly
    _STEP_DAYS[planet], preserving the old scan's resolution where a
    sign change can actually happen. Pure arithmetic — no ephemeris
    call — so the scan loop can carry the longitude forward instead of
    re-reading it at every cursor.
    """
    pos = lon % 30.0
    d_near = min(pos, 30.0 - pos)
    # The full distance, not half: the planet's speed is bounded by
    # _VMAX_DEG_PER_DAY, so in one step it travels at most d_near
    # degrees and cannot reach either boundary — a step wider than
    # _STEP_DAYS therefore cannot contain a sign change. Missing a
    # retrograde dip would need it to cross a boundary AND come back
    # inside one step (over 2 * d_near of travel), i.e. a true speed
    # above 2x the bound — physically impossible for every graha at
    # these margins (worst case the Moon: 2x23 = 46 deg/day against a
    # ~15.5 deg/day physical maximum). Landing exactly on a boundary
    # is still a valid bracket: the sign at hi differs and the
    # bisection finds the crossing inside [lo, hi].
    return max(_STEP_DAYS[planet], d_near / _VMAX_DEG_PER_DAY[planet])


def _sign_lon_at(planet: str, jd: float) -> tuple[int, float]:
    """(sign, sidereal longitude) of one graha at `jd` — a single
    swe.calc_ut, shared by the sign check and the step computation."""
    lon = ephemeris.planet_longitude_at(planet, jd)
    return ephemeris.sign_of(lon), lon


def _scan_bracket_forward(planet: str, jd_from: float,
                          max_days: float) -> tuple[float, float, int] | None:
    """First [lo, hi] bracket after `jd_from` whose endpoints straddle a
    sign change (sign(lo) == start_sign, sign(hi) != start_sign), or
    None if none is found within `max_days` — the crossing is still
    returned when it lands just past `max_days`, matching the old
    fixed-step scan. A step wider than _STEP_DAYS can never contain a
    sign change (see _scan_step), so the detecting step is always
    exactly _STEP_DAYS wide, exactly as before."""
    start_sign, lon_lo = _sign_lon_at(planet, jd_from)
    lo = jd_from
    while True:
        hi = lo + _scan_step(planet, lon_lo)
        hi_sign, lon_hi = _sign_lon_at(planet, hi)
        if hi_sign != start_sign:
            return lo, hi, start_sign
        if hi - jd_from > max_days:
            return None
        lo, lon_lo = hi, lon_hi


def _scan_bracket_backward(planet: str, jd_from: float,
                           max_days: float) -> tuple[float, float, int] | None:
    """Mirror image for the backward scan: [lo, hi] with sign(lo) !=
    start_sign and sign(hi) == start_sign, or None within `max_days`."""
    start_sign, lon_hi = _sign_lon_at(planet, jd_from)
    hi = jd_from
    while True:
        lo = hi - _scan_step(planet, lon_hi)
        lo_sign, lon_lo = _sign_lon_at(planet, lo)
        if lo_sign != start_sign:
            return lo, hi, start_sign
        if jd_from - lo > max_days:
            return None
        hi, lon_hi = lo, lon_lo


def _sign_at(planet: str, jd: float) -> int:
    # Single-planet fast path: the scanners below call this ~8k times per
    # chart, and the old planet_longitudes() route spent nine swe.calc_ut
    # per call (~90% of /api/kundali wall time).
    return ephemeris.planet_sign_at(planet, jd)


def _jd_to_date(jd: float) -> str:
    return ephemeris.jd_to_date_str(jd)


# Bisection tolerance for ingress moments. The old 0.002-day window let
# the reported JD sit up to ~3 minutes past the true ingress, so two
# scanners walking different cursor paths could date the same ingress
# on different UTC days when it fell near midnight (e.g. Saturn's
# 2027-06-02 Aries ingress at 23:58 UTC). At 1e-6 days every path
# converges to the same moment and the dates agree.
_BISECT_TOL = 1e-6


# One cached ingress walk per planet: ingresses are global astronomical
# events, so a walk built for one chart serves every later caller whose
# range it covers. The lifetime walk (birth -> birth+100y) covers the
# Sade Sati span, the 10-year chains, the transit calendar and the next
# ingress lookups, so those stop re-scanning the same ingresses. A
# range outside the cached walk is rebuilt for exactly that range —
# never worse than the old per-call scans. One entry per planet, so
# the cache is bounded; entries are (jd, to_sign) pairs, computed by
# the same ingress_jd / bisection code as before.
_INGRESS_MEMO: dict[str, dict] = {}


def _ingress_events(planet: str, lo: float, hi: float) -> list[tuple[float, int]]:
    """Consecutive ingresses of `planet` in [lo, hi] as (jd, to_sign)."""
    memo = _INGRESS_MEMO.get(planet)
    if memo is not None and memo["lo"] <= lo and memo["hi"] >= hi:
        return [(jd, s) for jd, s in memo["events"] if lo <= jd <= hi]
    events: list[tuple[float, int]] = []
    cursor = lo
    while cursor < hi:
        njd = ingress_jd(planet, cursor)
        if njd > hi:
            break
        events.append((njd, _sign_at(planet, njd + 0.01)))
        cursor = njd + 1.0
    _INGRESS_MEMO[planet] = {"lo": lo, "hi": hi, "events": events}
    return events


def _wrap180(deg: float) -> float:
    """Signed angular distance to a longitude, wrapped to (-180, 180]."""
    return (deg + 180.0) % 360.0 - 180.0


def _bisect_ingress(planet: str, lo: float, hi: float, start_sign: int,
                    forward: bool) -> float:
    """Canonical ingress moment inside the bracket [lo, hi].

    The bracket holds exactly one sign change: sign(lo) == start_sign
    and sign(hi) != start_sign when scanning forward (reversed when
    scanning back). Returns the bracket midpoint; callers bisecting the
    same bracket get the identical JD, and callers from different
    brackets agree to within _BISECT_TOL (and on the UTC date).

    The root is found by Illinois false position on the sidereal
    longitude's distance to the sign boundary, not by plain bisection
    on the sign: the longitude is nearly linear over a bracket (a few
    degrees), so the secant step lands within ~1e-6 days in ~5
    evaluations instead of the ~24 that halving the bracket needs
    (Saturn's 10-day step: log2(10/1e-6)). Each evaluation is still a
    single swe.calc_ut — the same call planet_sign_at() makes — so a
    bisection costs ~7 calc_ut instead of ~24. The bracket update
    itself stays sign-based, exactly as before, so a retrograde dip
    inside the bracket converges to the same crossing pure bisection
    would find; if the longitude interpolation is ever unusable
    (multi-sign jump, same-signed endpoints), it falls back to plain
    midpoint bisection.
    """
    far_sign = _sign_at(planet, hi) if forward else _sign_at(planet, lo)
    if (far_sign - start_sign) % 12 == 1:
        boundary = ((start_sign + 1) * 30.0) % 360.0
    elif (start_sign - far_sign) % 12 == 1:
        boundary = (start_sign * 30.0) % 360.0
    else:
        boundary = None
    flo = fhi = None
    if boundary is not None:
        flo = _wrap180(ephemeris.planet_longitude_at(planet, lo) - boundary)
        fhi = _wrap180(ephemeris.planet_longitude_at(planet, hi) - boundary)
        if flo * fhi >= 0.0 or abs(flo) > 90.0 or abs(fhi) > 90.0:
            flo = fhi = None  # unusable bracket: plain bisection
    side = 0  # endpoint updated last: -1 lo, +1 hi
    # Last evaluated point, for the local slope: the secant step can land
    # on the root to machine precision (fm ~ 1e-12 deg) while the bracket
    # is still wide — without a function-value stop the loop then stalls,
    # re-evaluating the same mid while Illinois halving drags the next
    # step to the midpoint (~20 wasted evals). So stop as soon as the
    # evaluated point is within _BISECT_TOL of the root in *time*,
    # estimated from the local slope between the last two evaluations.
    prev_jd, prev_f = hi, fhi
    for _ in range(64):
        if flo is not None:
            mid = lo - flo * (hi - lo) / (fhi - flo) if fhi != flo else (lo + hi) / 2.0
            if not (lo < mid < hi):
                mid = (lo + hi) / 2.0
            lon = ephemeris.planet_longitude_at(planet, mid)
            fm = _wrap180(lon - boundary)
            if fm == 0.0:
                return mid
            if prev_jd is not None and mid != prev_jd:
                slope = (fm - prev_f) / (mid - prev_jd)
                if slope != 0.0 and abs(fm / slope) < _BISECT_TOL:
                    return mid
            prev_jd, prev_f = mid, fm
            past = ephemeris.sign_of(lon) != start_sign
        else:
            mid = (lo + hi) / 2.0
            past = _sign_at(planet, mid) != start_sign
            fm = None
        if past:
            if forward:
                hi = mid
                if fm is not None:
                    fhi = fm
                new_side = 1
            else:
                lo = mid
                if fm is not None:
                    flo = fm
                new_side = -1
        elif forward:
            lo = mid
            if fm is not None:
                flo = fm
            new_side = -1
        else:
            hi = mid
            if fm is not None:
                fhi = fm
            new_side = 1
        if flo is not None and new_side == side:
            # Illinois: the same endpoint was updated twice running, so
            # the retained endpoint's value is halved to keep the
            # secant step from stagnating on one side.
            if new_side == -1:
                fhi /= 2.0
            else:
                flo /= 2.0
        side = new_side
        if hi - lo < _BISECT_TOL:
            break
    return (lo + hi) / 2.0


def next_ingress(planet: str, jd_from: float, max_days: float = 900.0) -> dict:
    """Next moment after `jd_from` at which `planet` changes sign."""
    memo = _INGRESS_MEMO.get(planet)
    if memo is not None and memo["lo"] <= jd_from and memo["hi"] >= jd_from + max_days:
        events = [(jd, s) for jd, s in memo["events"]
                  if jd_from < jd <= jd_from + max_days]
        if events:
            jd_ing, to_sign = events[0]
            return {
                "planet": planet,
                "from_sign": _sign_at(planet, jd_from),
                "to_sign": to_sign,
                "date": _jd_to_date(jd_ing),
            }
        raise ValueError(f"no ingress found for {planet}")
    # No covering walk: scan directly for the one ingress (the shared
    # walk builds a whole window, which for fast planets like the Sun
    # would be dozens of ingresses just to answer "the next one").
    bracket = _scan_bracket_forward(planet, jd_from, max_days)
    if bracket is None:
        raise ValueError(f"no ingress found for {planet}")
    lo, hi, start_sign = bracket
    # Bisect: sign at lo == start_sign, sign at hi != start_sign.
    jd_ing = _bisect_ingress(planet, lo, hi, start_sign, forward=True)
    return {
        "planet": planet,
        "from_sign": start_sign,
        "to_sign": _sign_at(planet, jd_ing + 0.01),
        "date": _jd_to_date(jd_ing),
    }


def prev_ingress(planet: str, jd_from: float, max_days: float = 1200.0) -> dict:
    """The most recent sign ingress of `planet` at or before `jd_from` —
    i.e. when it entered the sign it occupies at `jd_from`."""
    memo = _INGRESS_MEMO.get(planet)
    if memo is not None and memo["lo"] <= jd_from - max_days and memo["hi"] >= jd_from:
        events = [(jd, s) for jd, s in memo["events"]
                  if jd_from - max_days <= jd <= jd_from]
        if events:
            jd_ing, _to_sign = events[-1]
            return {
                "planet": planet,
                "from_sign": _sign_at(planet, jd_ing - 0.01),
                "to_sign": _sign_at(planet, jd_from),
                "date": _jd_to_date(jd_ing),
                "jd": jd_ing,
            }
        raise ValueError(f"no previous ingress found for {planet}")
    # No covering walk: scan directly for the one ingress.
    bracket = _scan_bracket_backward(planet, jd_from, max_days)
    if bracket is None:
        raise ValueError(f"no previous ingress found for {planet}")
    lo, hi, start_sign = bracket
    # Bisect: sign at lo != start_sign, sign at hi == start_sign.
    jd_ing = _bisect_ingress(planet, lo, hi, start_sign, forward=False)
    return {
        "planet": planet,
        "from_sign": _sign_at(planet, jd_ing - 0.01),
        "to_sign": start_sign,
        "date": _jd_to_date(jd_ing),
        "jd": jd_ing,
    }


def ingress_jd(planet: str, jd_from: float) -> float:
    """JD of the next ingress of `planet` after `jd_from` (bisected)."""
    bracket = _scan_bracket_forward(planet, jd_from, 4000.0)
    if bracket is None:
        raise ValueError(f"no ingress found for {planet}")
    lo, hi, start_sign = bracket
    return _bisect_ingress(planet, lo, hi, start_sign, forward=True)


def ingress_chain(planet: str, jd_from: float, jd_to: float) -> list[dict]:
    """Every ingress of `planet` in (jd_from, jd_to], chronological:
    [{planet, from_sign, to_sign, date}]."""
    events = _ingress_events(planet, jd_from, jd_to)
    out = []
    # No sign change happens between jd_from and the first event, or
    # between consecutive events, so the running sign is exact — the
    # same from_sign the old per-row _sign_at(njd - 0.01) returned.
    cur_sign = _sign_at(planet, jd_from)
    for njd, to_sign in events:
        out.append({
            "planet": planet,
            "from_sign": cur_sign,
            "to_sign": to_sign,
            "date": _jd_to_date(njd),
        })
        cur_sign = to_sign
    return out


def saturn_moon_span(moon_sign: int, jd_now: float) -> dict | None:
    """Boundary ingress dates of Saturn's passage over the three signs
    around the Moon sign (the Sade Sati span): when Saturn entered /
    will enter moon-1, moon, moon+1 and moon+2.

    Computed only when Saturn is in the span or one sign before it;
    otherwise None. Retrograde dips are resolved the way patros print
    the span: past boundaries are the FIRST entries (the backward walk
    keeps overwriting, so an entry left and re-entered during a dip
    resolves to its earliest date), and the span END is the FINAL entry
    into moon+2 (the forward walk continues until Saturn has moved on
    to moon+3, updating on every re-entry).
    """
    cur = _sign_at("Saturn", jd_now)
    rel = (cur - moon_sign) % 12
    if rel not in (10, 11, 0, 1):
        return None
    rising = (moon_sign - 1) % 12
    peak = moon_sign
    setting = (moon_sign + 1) % 12
    end_target = (moon_sign + 2) % 12
    beyond = (moon_sign + 3) % 12
    targets = (rising, peak, setting, end_target)
    found: dict[int, float] = {}
    # One shared walk covers both directions (the lifetime walk already
    # built it in the usual compute_kundali order, so this is a slice).
    # Backwards: entry dates for targets at or before now. Overwriting
    # as we walk back resolves retrograde re-entries to the FIRST entry.
    # Same window as before: at most 12 ingresses, at most 3650 days back.
    events = _ingress_events("Saturn", jd_now - 3650.0, jd_now + 20 * 365.25)
    past = [e for e in events if e[0] <= jd_now]
    for jd, to_sign in reversed(past[-12:]):
        if to_sign in targets:
            found[to_sign] = jd
    # Forwards: first future entries into the rising/peak/setting signs;
    # the END keeps updating until Saturn has moved past the span.
    # Same cap as before: at most 16 ingresses forward; if the shared
    # walk runs out first, fall back to direct scans for the remainder.
    fwd_iter = iter(e for e in events if e[0] > jd_now)
    fwd_jd = jd_now
    past_end = False
    for _ in range(16):
        if all(t in found for t in targets) and past_end:
            break
        try:
            njd, nsign = next(fwd_iter)
        except StopIteration:
            njd = ingress_jd("Saturn", fwd_jd)
            nsign = _sign_at("Saturn", njd + 0.01)
        if nsign == end_target or (nsign in targets and nsign not in found):
            found[nsign] = njd
        if nsign == beyond and end_target in found:
            past_end = True
        fwd_jd = njd + 1.0
    if not all(t in found for t in targets):
        return None
    return {
        "start": _jd_to_date(found[rising]),         # Saturn enters moon-1
        "peak_start": _jd_to_date(found[peak]),      # enters the Moon sign
        "setting_start": _jd_to_date(found[setting]),  # enters moon+1
        "end": _jd_to_date(found[end_target]),       # enters moon+2: over
    }


def transit_table(now_jd: float, moon_sign: int) -> dict:
    """Current transit signs + next ingresses, with each slow planet's
    house counted from the natal Moon sign."""
    planets_now = ephemeris.planet_longitudes(now_jd)
    rows = []
    for p in INGRESS_PLANETS:
        ing = next_ingress(p, now_jd)
        cur_sign = planets_now[p]["sign"]
        rows.append({
            "planet": p,
            "current_sign": cur_sign,
            "current_sign_en": SIGNS_EN[cur_sign],
            "current_sign_ne": SIGNS_NE[cur_sign],
            "house_from_moon": (cur_sign - moon_sign) % 12 + 1,
            "next_ingress_date": ing["date"],
            "next_sign": ing["to_sign"],
            "next_sign_en": SIGNS_EN[ing["to_sign"]],
            "next_sign_ne": SIGNS_NE[ing["to_sign"]],
        })
    return {"ingress": rows}


# Graha-drishti offsets used for double-transit activation: a transiting
# planet activates its own sign plus the signs it aspects.
_DT_OFFSETS = {"Saturn": (0, 2, 6, 9), "Jupiter": (0, 4, 6, 8)}


def double_transit(jd_now: float) -> dict:
    """Signs jointly activated by transiting Saturn and Jupiter (the
    classical double transit used for event timing)."""
    signs_now = ephemeris.planet_longitudes(jd_now)
    activated: dict[str, set[int]] = {}
    for planet, offsets in _DT_OFFSETS.items():
        base = signs_now[planet]["sign"]
        activated[planet] = {(base + o) % 12 for o in offsets}
    joint = sorted(activated["Saturn"] & activated["Jupiter"])
    return {
        "saturn_sign": signs_now["Saturn"]["sign"],
        "jupiter_sign": signs_now["Jupiter"]["sign"],
        "joint_signs": joint,
    }


def sade_sati_lifetime(moon_sign: int, jd_birth: float, jd_now: float,
                        years: int = 100) -> dict:
    """Every Sade Sati period across the native's life, with exact
    ingress dates. Saturn's sign is walked from birth over `years`
    years; maximal runs inside {moon-1, moon, moon+1} are periods,
    with short retrograde dips out of the set (< 400 days) merged
    into the surrounding period — patros print the span from first
    entry to final exit. Boundaries inside a period are the FIRST
    entries into moon-1 (rising), the Moon sign (peak) and moon+1
    (setting); the period end is the final exit from the set.
    """
    in_set = {(moon_sign - 1) % 12, moon_sign, (moon_sign + 1) % 12}
    jd_end = jd_birth + years * 365.25
    # Walk ingresses with their JDs — the shared walk, so the span,
    # chains and next-ingress lookups later reuse these same events.
    events = _ingress_events("Saturn", jd_birth, jd_end)
    # Raw in-set intervals between consecutive events.
    intervals: list[tuple[float, float]] = []
    cur_sign = _sign_at("Saturn", jd_birth)
    cur_start = jd_birth
    for jd, to_sign in events:
        if cur_sign in in_set and to_sign not in in_set:
            intervals.append((cur_start, jd))
        elif cur_sign not in in_set and to_sign in in_set:
            cur_start = jd
        cur_sign = to_sign
    if cur_sign in in_set:
        intervals.append((cur_start, jd_end))
    # Merge intervals separated by < 400 days (retrograde dips).
    merged: list[list[float]] = []
    for s, e in intervals:
        if merged and s - merged[-1][1] < 400.0:
            merged[-1][1] = e
        else:
            merged.append([s, e])
    periods = []
    for s, e in merged:
        # First entries into moon-1 / moon / moon+1 within [s, e].
        bounds = {}
        for target, key in (((moon_sign - 1) % 12, "start"),
                            (moon_sign, "peak_start"),
                            ((moon_sign + 1) % 12, "setting_start")):
            if s == jd_birth and _sign_at("Saturn", jd_birth) == target:
                bounds[key] = _jd_to_date(jd_birth)
                continue
            hit = next((jd for jd, ts in events if s <= jd <= e and ts == target), None)
            bounds[key] = _jd_to_date(hit) if hit is not None else None
        if e >= jd_now >= s:
            status = "current"
        elif e < jd_now:
            status = "past"
        else:
            status = "future"
        periods.append({
            **bounds,
            "end": _jd_to_date(e),
            "status": status,
            "already_running_at_birth": s == jd_birth,
        })
    return {"moon_sign": moon_sign, "periods": periods, "count": len(periods)}
