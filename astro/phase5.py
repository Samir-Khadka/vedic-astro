"""Phase 5: Predictive Intelligence.

1. Dasha Consensus Engine — all dasha systems on one timeline, scored and
   weighted by lord strength. When independent systems agree, confidence is
   high. This is what experienced astrologers do mentally; the engine does
   it explicitly.
2. Yoga Fructification Timing — WHEN detected yogas deliver results.
3. Ashtakavarga Gochar Scores — daily SAV transit scores.
4. Tajika Varshphal Yogas — Ithasala etc. for the annual chart.
5. All 12 Arudha Padas.
"""
from __future__ import annotations

from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# Dasha Consensus Engine
# ---------------------------------------------------------------------------
# Planet nature scores.
_PLANET_NATURE = {
    "Jupiter": 1.0, "Venus": 1.0,
    "Mercury": 0.5, "Moon": 0.5,
    "Sun": 0.0,
    "Rahu": -0.5, "Ketu": -0.5,
    "Mars": -1.0, "Saturn": -1.0,
}
# House scores (whole-sign from Lagna).
_HOUSE_SCORE = {
    1: 1.0, 5: 1.0, 9: 1.0,      # kendra/trikona
    4: 0.5, 7: 0.5, 10: 0.5,     # kendra
    2: 0.25, 11: 0.25,           # wealth/gains
    3: -0.5, 6: -1.0, 8: -1.0, 12: -1.0,  # dusthana
}
# Dignity scores.
_DIGNITY_SCORE = {
    "exalted": 1.0, "own": 0.75, "friendly": 0.25,
    "neutral": 0.0, "enemy": -0.5, "debilitated": -1.0,
}
# System weights (Vimshottari is the primary timing system).
_SYSTEM_WEIGHTS = {
    "vimshottari": 3.0,
    "chara": 2.0,
    "narayana": 2.0,
    "yogini": 1.0,
    "shodshottari": 1.0,
    "kalachakra": 1.0,
}
# Sign lords.
_SIGN_LORDS = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
               "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]


def _score_planet(planet: str, planets_by_name: dict,
                  shadbala: dict) -> float:
    """Score a dasha lord: nature + house + dignity + strength."""
    p = planets_by_name.get(planet, {})
    score = _PLANET_NATURE.get(planet, 0.0)
    score += _HOUSE_SCORE.get(p.get("house", 0), 0.0)
    score += _DIGNITY_SCORE.get(p.get("dignity", "neutral"), 0.0)
    sb = shadbala.get(planet, {})
    # Shadbala total in rupas; >6 is strong, <5 is weak (classical).
    total = sb.get("total", 6.0) if isinstance(sb, dict) else 6.0
    if total >= 6.5:
        score += 0.5
    elif total <= 5.0:
        score -= 0.5
    return max(-2.0, min(2.0, score))


def _score_sign(sign_en: str, planets_by_name: dict, shadbala: dict,
                signs_en: list[str]) -> float:
    """Score a sign dasha: lord's score + occupant modifiers."""
    idx = signs_en.index(sign_en)
    lord = _SIGN_LORDS[idx]
    score = _score_planet(lord, planets_by_name, shadbala)
    # Occupants: benefics help, malefics hurt.
    for pname, p in planets_by_name.items():
        if p.get("sign_en") == sign_en:
            nature = _PLANET_NATURE.get(pname, 0.0)
            score += 0.25 if nature > 0 else (-0.25 if nature < 0 else 0)
    return max(-2.0, min(2.0, score))


def _period_at(tree: dict, at: datetime):
    """Find the running period in a serialized dasha tree.

    Handles 'mahadashas' (Vimshottari-style) and 'periods' (Chara/Yogini).
    """
    for key in ("mahadashas", "periods"):
        for per in tree.get(key, []):
            start = per.get("start") or per.get("display_start")
            end = per.get("end")
            try:
                s = (datetime.fromisoformat(start)
                     if isinstance(start, str) else start)
                e = (datetime.fromisoformat(end)
                     if isinstance(end, str) else end)
            except (TypeError, ValueError):
                continue
            if s and e and s <= at < e:
                return per
    # Fallback: use the 'current' block if dates don't parse.
    cur = tree.get("current")
    if isinstance(cur, dict):
        md = cur.get("mahadasha") or cur
        if isinstance(md, dict) and ("sign_en" in md or "lord" in md
                                     or "planet" in md):
            return md
    return None


def dasha_consensus(bundle: dict, months: int = 60) -> dict:
    """Monthly consensus across all dasha systems for `months` ahead.

    Returns a timeline with per-system scores and a weighted consensus.
    """
    from .names import SIGNS_EN

    planets = {p["planet"]: p for p in bundle.get("planets", [])}
    shadbala = bundle.get("strength", {}).get("shadbala", {})
    now = datetime.now()

    # Collect the dasha trees.
    systems = {}
    if bundle.get("dasha"):
        systems["vimshottari"] = (bundle["dasha"], "lord")
    if bundle.get("chara_dasha"):
        systems["chara"] = (bundle["chara_dasha"], "sign_en")
    if bundle.get("narayana"):
        systems["narayana"] = (bundle["narayana"], "sign_en")
    if bundle.get("yogini"):
        systems["yogini"] = (bundle["yogini"], "planet")
    if bundle.get("shodshottari"):
        systems["shodshottari"] = (bundle["shodshottari"], "lord")
    if bundle.get("kalachakra"):
        systems["kalachakra"] = (bundle["kalachakra"], "sign_en")

    timeline = []
    for m in range(months):
        at = now + timedelta(days=m * 30.44)
        scores = {}
        for sys_name, (tree, field) in systems.items():
            per = _period_at(tree, at)
            if not per:
                continue
            val = per.get(field) or (per.get("mahadasha", {}).get(field)
                                     if isinstance(per.get("mahadasha"), dict)
                                     else None)
            if not val:
                continue
            if field in ("lord", "planet"):
                score = _score_planet(val, planets, shadbala)
            else:  # sign-based
                score = _score_sign(val, planets, shadbala, SIGNS_EN)
            scores[sys_name] = {"value": val, "score": round(score, 2)}

        if not scores:
            continue
        # Weighted consensus.
        total_w = sum(_SYSTEM_WEIGHTS.get(s, 1.0) for s in scores)
        consensus = sum(scores[s]["score"] * _SYSTEM_WEIGHTS.get(s, 1.0)
                          for s in scores) / total_w
        # Agreement: fraction of systems on the same side as consensus.
        side = 1 if consensus > 0.25 else (-1 if consensus < -0.25 else 0)
        agree = sum(1 for s in scores
                    if (scores[s]["score"] > 0.25 and side == 1) or
                       (scores[s]["score"] < -0.25 and side == -1) or
                       (abs(scores[s]["score"]) <= 0.25 and side == 0))
        agreement = agree / len(scores) if scores else 0

        timeline.append({
            "month": at.strftime("%Y-%m"),
            "consensus": round(consensus, 2),
            "agreement": round(agreement, 2),
            "systems": scores,
            "verdict": ("favourable" if consensus > 0.5 else
                        "challenging" if consensus < -0.5 else "mixed"),
        })

    # Highlight high-confidence periods (agreement >= 0.75).
    highlights = [t for t in timeline
                  if t["agreement"] >= 0.75 and abs(t["consensus"]) > 0.5]

    return {
        "timeline": timeline,
        "highlights": highlights,
        "note": ("Consensus across independent dasha systems. High agreement "
                 "(≥75%) with a strong consensus score is the closest software "
                 "gets to a confident prediction. Always confirm with transits."),
    }


# ---------------------------------------------------------------------------
# Yoga Fructification Timing
# ---------------------------------------------------------------------------
import re as _re

_PLANET_RE = _re.compile(
    r"\b(Sun|Moon|Mars|Mercury|Jupiter|Venus|Saturn|Rahu|Ketu)\b")


def _yoga_planets(basis: str) -> list[str]:
    """Extract planet names mentioned in a yoga's basis text."""
    return sorted(set(_PLANET_RE.findall(basis)))


def yoga_fructification(bundle: dict, years: int = 10) -> dict:
    """WHEN each detected yoga is likely to deliver results.

    A yoga fructifies in the Vimshottari MD/AD of its causing planets.
    Returns the next activation window for each yoga.
    """
    yogas = bundle.get("yogas", [])
    dasha = bundle.get("dasha", {})
    now = datetime.now()
    horizon = now + timedelta(days=years * 365.25)

    results = []
    for yoga in yogas:
        name = yoga.get("name", "Yoga")
        basis = yoga.get("basis", "")
        planets = _yoga_planets(basis)
        if not planets:
            continue
        windows = []
        for md in dasha.get("mahadashas", []):
            try:
                s = (datetime.fromisoformat(md["start"])
                     if isinstance(md["start"], str) else md["start"])
                e = (datetime.fromisoformat(md["end"])
                     if isinstance(md["end"], str) else md["end"])
            except (TypeError, ValueError, KeyError):
                continue
            if e < now or s > horizon:
                continue
            md_lord = md.get("lord", "")
            # Check MD and ADs.
            for ad in md.get("antardashas", []):
                try:
                    as_ = (datetime.fromisoformat(ad["start"])
                           if isinstance(ad["start"], str) else ad["start"])
                    ae = (datetime.fromisoformat(ad["end"])
                          if isinstance(ad["end"], str) else ad["end"])
                except (TypeError, ValueError, KeyError):
                    continue
                if ae < now or as_ > horizon:
                    continue
                ad_lord = ad.get("lord", "")
                if md_lord in planets or ad_lord in planets:
                    windows.append({
                        "md": md_lord, "ad": ad_lord,
                        "start": as_.date().isoformat(),
                        "end": ae.date().isoformat(),
                        "trigger": ("MD lord" if md_lord in planets
                                    else "AD lord"),
                    })
                    if len(windows) >= 3:
                        break
            if len(windows) >= 3:
                break
        if windows:
            results.append({
                "yoga": name,
                "planets": planets,
                "basis": basis,
                "activations": windows,
            })

    return {
        "yogas": results,
        "note": ("A yoga delivers in the dasha of its causing planets. "
                 "The strongest activations are when BOTH MD and AD lords "
                 "are yoga planets."),
    }


# ---------------------------------------------------------------------------
# Ashtakavarga Gochar — transit scores
# ---------------------------------------------------------------------------

def ashtakavarga_gochar(bundle: dict, days: int = 30) -> dict:
    """Daily Sarvashtakavarga scores for the transit Moon.

    SAV > 28 in the Moon's sign: favourable day. SAV < 25: challenging.
    Also reports Saturn and Jupiter's current SAV.
    """
    from .names import SIGNS_EN
    from .ephemeris import planet_longitude_at, sign_of, to_julian_day

    sav = bundle.get("ashtakavarga", {}).get("Sarvashtakavarga", [])
    if len(sav) != 12:
        return {"days": [], "note": "SAV unavailable."}
    now = datetime.now()
    days_out = []
    for d in range(days):
        day = now + timedelta(days=d)
        jd = to_julian_day(day.replace(tzinfo=None))
        moon_sign = sign_of(planet_longitude_at("Moon", jd) % 360.0)
        score = sav[moon_sign]
        days_out.append({
            "date": day.date().isoformat(),
            "moon_sign_en": SIGNS_EN[moon_sign],
            "sav": score,
            "verdict": ("favourable" if score > 28 else
                        "challenging" if score < 25 else "neutral"),
        })
    # Current Saturn/Jupiter SAV.
    jd_now = to_julian_day(now.replace(tzinfo=None))
    sat_sign = sign_of(planet_longitude_at("Saturn", jd_now) % 360.0)
    jup_sign = sign_of(planet_longitude_at("Jupiter", jd_now) % 360.0)
    return {
        "days": days_out,
        "saturn": {"sign_en": SIGNS_EN[sat_sign], "sav": sav[sat_sign]},
        "jupiter": {"sign_en": SIGNS_EN[jup_sign], "sav": sav[jup_sign]},
        "note": ("SAV > 28: transits through the sign give good results. "
                 "SAV < 25: difficult. The Moon's daily SAV is the classic "
                 "day-to-day timing tool."),
    }


# ---------------------------------------------------------------------------
# All 12 Arudha Padas
# ---------------------------------------------------------------------------

def arudha_padas(planets_by_name: dict, lagna_sign: int) -> dict:
    """Arudha Pada for all 12 houses.

    Arudha of a house = sign at (2 * lord_sign - house_sign), with the
    exceptions: not the same as the house, not the 7th from it.
    """
    from .names import SIGNS_EN, SIGNS_NE

    padas = []
    for house in range(1, 13):
        house_sign = (lagna_sign + house - 1) % 12
        lord = _SIGN_LORDS[house_sign]
        lord_sign = planets_by_name.get(lord, {}).get("sign", house_sign)
        # Arudha = count from house to lord, then same distance further.
        arudha = (2 * lord_sign - house_sign) % 12
        # Exceptions: not the house itself, not the 7th from it.
        if arudha == house_sign:
            arudha = (arudha + 10) % 12  # 10th from it
        elif arudha == (house_sign + 6) % 12:
            arudha = (arudha + 10) % 12
        padas.append({
            "house": house,
            "arudha_sign": arudha,
            "arudha_en": SIGNS_EN[arudha],
            "arudha_ne": SIGNS_NE[arudha],
            "label": f"A{house}",
        })
    return {
        "padas": padas,
        "note": ("Arudha Padas show the 'image' of each house — how the world "
                 "perceives that area of life. A1 (Arudha Lagna) is the most "
                 "important."),
    }
