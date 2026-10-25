"""KP event analysis — does the chart promise an event, and is it
supported right now?

Classical KP judgement in three layers (the same promise → dasha →
transit filter the KP schools teach):
  1. PROMISE: the cuspal sub lord of the event house. If the sub lord
     signifies the event's favourable houses, the event is promised;
     if it signifies their negating houses, it is denied or delayed.
     Negating houses are derived by the 12th-from rule: the 12th
     house from any favourable house negates it (so marriage
     {2,7,11} is negated by {1,6,10} — the textbook table).
  2. DASHA: the running Mahadasha and Antardasha lords must signify
     the event houses for the promise to ripen in this period.
  3. TRANSIT: Jupiter and Saturn currently transiting (whole-sign,
     from Lagna) the event houses support timing.
Significations come from the engine's KP tables (occupied + ruled +
via star lord). Verdicts are guidance, not guarantees — KP itself
treats a weak promise as "effort and remedy first".
"""
from __future__ import annotations

from .charts import house_of
from .names import PLANET_NE, SIGNS_EN, SIGNS_NE

EVENTS = {
    "marriage": {"en": "Marriage", "ne": "विवाह", "houses": [2, 7, 11]},
    "career": {"en": "Career", "ne": "पेशा", "houses": [2, 6, 10, 11]},
    "wealth": {"en": "Wealth", "ne": "धन", "houses": [2, 5, 11]},
    "children": {"en": "Children", "ne": "सन्तान", "houses": [2, 5, 11]},
    "education": {"en": "Education", "ne": "शिक्षा", "houses": [4, 9, 11]},
    "foreign": {"en": "Foreign travel / settlement", "ne": "विदेश यात्रा / बसोबास", "houses": [3, 9, 12]},
    "property": {"en": "Property", "ne": "सम्पत्ति", "houses": [4, 11, 12]},
}


def _negating(fav: list[int]) -> list[int]:
    neg = sorted({((h - 2) % 12) + 1 for h in fav} - set(fav))
    return neg


def kp_event_analysis(kp: dict, dasha_tree: dict, transit_signs: dict,
                      lagna_sign: int) -> dict:
    """Per-event promise/dasha/transit verdicts."""
    sig = kp["planet_signified_houses"]
    cusps = {c["house"]: c for c in kp["cusps"]}
    cur = dasha_tree.get("current") or {}
    md_lord = (cur.get("mahadasha") or {}).get("lord")
    ad_lord = (cur.get("antardasha") or {}).get("lord")
    dasha_lords = [l for l in (md_lord, ad_lord) if l]

    out: dict[str, dict] = {}
    for key, ev in EVENTS.items():
        fav = set(ev["houses"])
        neg = set(_negating(ev["houses"]))
        house = ev["houses"][1] if len(ev["houses"]) > 1 else ev["houses"][0]
        # Primary house: marriage 7, career 10, wealth 2, children 5,
        # education 4, foreign 12, property 4 — the first listed house
        # is the significator anchor except career (10) and wealth (2).
        primary = {"marriage": 7, "career": 10, "wealth": 2, "children": 5,
                   "education": 4, "foreign": 12, "property": 4}[key]
        sub_lord = cusps[primary]["sub_lord"]
        sub_sig = set(sig.get(sub_lord, []))
        fav_hits = sorted(sub_sig & fav)
        neg_hits = sorted(sub_sig & neg)
        if fav_hits and not neg_hits:
            verdict, verdict_ne = "Promised", "प्रतिज्ञात"
        elif fav_hits and neg_hits:
            verdict, verdict_ne = "Mixed", "मिश्रित"
        elif neg_hits and not fav_hits:
            verdict, verdict_ne = "Not indicated", "सङ्केत छैन"
        else:
            verdict, verdict_ne = "Weak", "कमजोर"

        dasha_hits = []
        for lord in dasha_lords:
            hits = sorted(set(sig.get(lord, [])) & fav)
            if hits:
                dasha_hits.append({"lord": lord, "houses": hits})
        dasha_support = bool(dasha_hits)

        transit_hits = {}
        for planet in ("Jupiter", "Saturn"):
            h = house_of(transit_signs[planet], lagna_sign)
            if h in fav:
                transit_hits[planet] = h

        summary_en = (
            f"Cuspal sub lord {sub_lord} of the {primary}th house signifies "
            f"{', '.join(map(str, fav_hits)) or 'none of the event houses'}"
            + (f" (negating: {', '.join(map(str, neg_hits))})" if neg_hits else "")
            + f". Verdict: {verdict}."
            + (f" Current dasha lords support it ({', '.join(d['lord'] for d in dasha_hits)})."
               if dasha_support else " Current dasha lords do not signify the event houses.")
            + (f" Transit support: {', '.join(f'{p} in house {h}' for p, h in transit_hits.items())}."
               if transit_hits else " No Jupiter/Saturn transit support right now.")
        )
        summary_ne = (
            f"{primary}औं भावका कस्पल सब लर्ड {PLANET_NE.get(sub_lord, sub_lord)} ले "
            f"{', '.join(map(str, fav_hits)) or 'घटना भावहरूमध्ये कुनै'} लाई सङ्केत गर्छन्"
            + (f" (निषेधक: {', '.join(map(str, neg_hits))})" if neg_hits else "")
            + f"। निष्कर्ष: {verdict_ne}।"
            + (f" हालको दशा स्वामीहरूले साथ दिन्छन् ({', '.join(PLANET_NE.get(d['lord'], d['lord']) for d in dasha_hits)})।"
               if dasha_support else " हालको दशा स्वामीहरूले घटना भावहरूलाई सङ्केत गर्दैनन्।")
        )
        out[key] = {
            "event_en": ev["en"], "event_ne": ev["ne"],
            "houses": ev["houses"], "negating": sorted(neg),
            "primary_house": primary, "cuspal_sub_lord": sub_lord,
            "sub_signified": sorted(sub_sig),
            "fav_hits": fav_hits, "neg_hits": neg_hits,
            "verdict": verdict, "verdict_ne": verdict_ne,
            "dasha_lords": dasha_lords, "dasha_hits": dasha_hits,
            "dasha_support": dasha_support,
            "transit_hits": transit_hits,
            "summary": {"en": summary_en, "ne": summary_ne},
        }
    return out
