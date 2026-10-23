"""Engine facade — assembles the complete kundali bundle from birth data."""
from __future__ import annotations

from datetime import date, datetime, time, timezone
from zoneinfo import ZoneInfo

from . import (
    ashtakavarga as av_module,
    bala as bala_module,
    chara as chara_module,
    charts as charts_module,
    dasha as dasha_module,
    doshas as doshas_module,
    ephemeris,
    interpret as interpret_module,
    jaimini as jaimini_module,
    kp as kp_module,
    lalkitab as lk_module,
    naming as naming_module,
    numerology as numerology_module,
    panchang as panchang_module,
    places as places_module,
    predictions as predictions_module,
    transits as transits_module,
    yogas as yogas_module,
)
from .names import (
    NAKSHATRAS_EN, NAKSHATRAS_NE, PLANET_NE, SIGNS_EN, SIGNS_NE,
)


def resolve_place(payload: dict) -> dict:
    """A payload carries either place_id or explicit lat/lon/tz."""
    if payload.get("place_id"):
        place = places_module.get_place(payload["place_id"])
        if not place:
            raise ValueError(f"unknown place_id: {payload['place_id']}")
        return {
            "name": place["name"], "country": place["country"],
            "lat": place["lat"], "lon": place["lon"], "tz": place["tz"],
        }
    if payload.get("lat") is not None and payload.get("lon") is not None and payload.get("tz"):
        return {
            "name": payload.get("place_name") or "Custom location",
            "country": "", "lat": float(payload["lat"]),
            "lon": float(payload["lon"]), "tz": payload["tz"],
        }
    raise ValueError("provide place_id or lat/lon/tz")


def _serialize_period(p: dict | None) -> dict | None:
    if p is None:
        return None
    return {
        "lord": p["lord"],
        "start": p["start"].date().isoformat(),
        "end": p["end"].date().isoformat(),
        "years": round(p["years"], 3),
    }


def _serialize_dasha(tree: dict, birth_dt: datetime) -> dict:
    mds = []
    for md in tree["mahadashas"]:
        ads = []
        for ad in md["antardashas"]:
            entry = _serialize_period(ad)
            if "pratyantardashas" in ad:
                entry["pratyantardashas"] = [_serialize_period(x) for x in ad["pratyantardashas"]]
            ads.append(entry)
        m = _serialize_period(md)
        m["antardashas"] = ads
        # For display, the first mahadasha starts at birth (balance period).
        if md["start"] < birth_dt:
            m["display_start"] = birth_dt.date().isoformat()
        mds.append(m)
    cur = tree.get("current")
    current = None
    if cur:
        current = {
            "mahadasha": _serialize_period(cur["mahadasha"]),
            "antardasha": _serialize_period(cur.get("antardasha")),
            "pratyantardasha": _serialize_period(cur.get("pratyantardasha")),
        }
    return {"mahadashas": mds, "current": current, "balance_years": round(tree["balance_years"], 3)}


def compute_kundali(payload: dict, now: datetime | None = None) -> dict:
    place = resolve_place(payload)
    dob = date.fromisoformat(payload["dob"])
    tob = time.fromisoformat(payload["tob"])
    birth_dt = ephemeris.make_local_datetime(dob, tob, place["tz"])
    now = now or datetime.now(ZoneInfo(place["tz"]))

    jd = ephemeris.to_julian_day(birth_dt)
    planets = ephemeris.planet_longitudes(jd)
    lagna_lon = ephemeris.ascendant(jd, place["lat"], place["lon"], b"W")
    lagna_sign = int(lagna_lon // 30.0)
    cusps = ephemeris.placidus_cusps(jd, place["lat"], place["lon"])

    varga_charts = {v: charts_module.build_chart(planets, lagna_lon, v) for v in charts_module.VARGAS}
    combust = charts_module.combustions(planets)
    karakas = charts_module.jaimini_karakas(planets)

    dasha_tree = dasha_module.vimshottari_tree(birth_dt, planets["Moon"]["longitude"], now)
    kp = kp_module.kp_tables(planets, cusps)

    # Transits right now (signs of the slow movers) for gochar / Sade Sati.
    jd_now = ephemeris.to_julian_day(now)
    now_planets = ephemeris.planet_longitudes(jd_now)
    transit_signs = {p: now_planets[p]["sign"] for p in ("Saturn", "Jupiter", "Rahu", "Ketu", "Moon", "Sun", "Mars")}
    sade_sati = doshas_module.sade_sati(planets["Moon"]["sign"], transit_signs["Saturn"])

    dosha_results = {
        "manglik": doshas_module.manglik(planets, lagna_sign),
        "kaal_sarp": doshas_module.kaal_sarp(planets, lagna_sign),
        "sade_sati": sade_sati,
        "pitra": doshas_module.pitra(planets, lagna_sign),
    }
    av = av_module.compute_ashtakavarga(planets, lagna_sign)
    yoga_list = yogas_module.detect_yogas(planets, lagna_sign)
    birth_panchang = panchang_module.panchang_at(birth_dt, place["lat"], place["lon"], place["tz"])
    rise, set_ = ephemeris.sunrise_sunset(dob, place["lat"], place["lon"], place["tz"])

    ctx = {
        "planets": planets, "lagna_sign": lagna_sign,
        "charts": varga_charts, "combust": combust,
        "dasha": dasha_tree, "transit_signs": transit_signs, "sade_sati": sade_sati,
    }
    preds = predictions_module.generate_predictions(ctx)

    # Premium-strength layer: Shadbala / Bhava Bala / Vimshopaka,
    # transit ingress table, Lal Kitab, Yogini + Tribhagi dashas.
    sb = bala_module.shadbala(planets, lagna_sign, cusps, varga_charts,
                              birth_dt, place["lat"], place["lon"], place["tz"], jd)
    bb = bala_module.bhava_bala(planets, lagna_sign, cusps, sb)
    vs = bala_module.vimshopaka(planets, varga_charts)
    transit_tbl = transits_module.transit_table(jd_now, planets["Moon"]["sign"])
    lk = lk_module.lal_kitab(planets)
    yogini = dasha_module.yogini_periods(birth_dt, planets["Moon"]["longitude"], now)
    tribhagi = dasha_module.tribhagi_periods(birth_dt, planets["Moon"]["longitude"], now)

    # Deep layer (interpretation engine v2): Jaimini special lagnas,
    # Chara dasha, Sade Sati span dates, double transit, 10-year
    # ingress chains for the forecast.
    special = jaimini_module.special_lagnas(planets, lagna_sign)
    chara = chara_module.chara_periods(birth_dt, planets, lagna_sign, now)
    saturn_span = transits_module.saturn_moon_span(planets["Moon"]["sign"], jd_now)
    double_tr = transits_module.double_transit(jd_now)
    jd_10y = jd_now + 10.2 * 365.25
    ingress_chains = {
        p: transits_module.ingress_chain(p, jd_now, jd_10y)
        for p in ("Saturn", "Jupiter", "Rahu")
    }

    from . import report as report_module
    report_ctx = dict(ctx)
    report_ctx.update({
        "predictions": preds, "yogas": yoga_list, "doshas": dosha_results,
        "karakas": karakas, "dasha_tree": dasha_tree, "now": now,
        "birth_dt": birth_dt, "place": place,
        "transit_ingress": transit_tbl["ingress"],
        "shadbala": sb, "chara": chara, "ingress_chains": ingress_chains,
    })
    premium = report_module.generate_premium_report(report_ctx)

    deep_ctx = dict(report_ctx)
    deep_ctx.update({
        "ashtakavarga": av, "bhava_bala": bb, "special": special,
        "saturn_span": saturn_span, "double_transit": double_tr,
        "jd_now": jd_now,
    })
    deep_report = interpret_module.build_deep_report(deep_ctx)
    dasha_phala = deep_report["dasha_deep_dive"]

    planet_rows = []
    for name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        p = planets[name]
        kpc = kp["planets"][name]
        planet_rows.append({
            "planet": name,
            "name_ne": PLANET_NE[name],
            "longitude": round(p["longitude"], 4),
            "sign": p["sign"],
            "sign_en": SIGNS_EN[p["sign"]],
            "sign_ne": SIGNS_NE[p["sign"]],
            "degree_in_sign": round(p["degree_in_sign"], 3),
            "nakshatra": p["nakshatra"],
            "nakshatra_en": NAKSHATRAS_EN[p["nakshatra"]],
            "nakshatra_ne": NAKSHATRAS_NE[p["nakshatra"]],
            "pada": p["pada"],
            "retrograde": p["retrograde"],
            "house": charts_module.house_of(p["sign"], lagna_sign),
            "dignity": charts_module.dignity(name, p["sign"]) if name not in ("Rahu", "Ketu") else "neutral",
            "combust": bool(combust.get(name, False)),
            "kp": kpc,
        })

    bundle = {
        "name": payload.get("name") or "",
        "birth": {
            "date": dob.isoformat(), "time": tob.isoformat(),
            "place": place,
            "sunrise": rise.isoformat() if rise else None,
            "sunset": set_.isoformat() if set_ else None,
        },
        "lagna": {
            "longitude": round(lagna_lon, 4),
            "sign": lagna_sign,
            "sign_en": SIGNS_EN[lagna_sign],
            "sign_ne": SIGNS_NE[lagna_sign],
            "degree_in_sign": round(lagna_lon % 30.0, 3),
            "nakshatra": ephemeris.nakshatra_of(lagna_lon)[0],
            "nakshatra_en": NAKSHATRAS_EN[ephemeris.nakshatra_of(lagna_lon)[0]],
            "nakshatra_ne": NAKSHATRAS_NE[ephemeris.nakshatra_of(lagna_lon)[0]],
            "pada": ephemeris.nakshatra_of(lagna_lon)[1],
        },
        "planets": planet_rows,
        "charts": varga_charts,
        "karakas": karakas,
        "dasha": _serialize_dasha(dasha_tree, birth_dt),
        "kp": {
            "planets": kp["planets"],
            "cusps": [
                {**c, "longitude": round(c["longitude"], 4),
                 "sign_en": SIGNS_EN[c["sign"]], "sign_ne": SIGNS_NE[c["sign"]]}
                for c in kp["cusps"]
            ],
            "house_significators": kp["house_significators"],
            "planet_signified_houses": kp["planet_signified_houses"],
        },
        "doshas": dosha_results,
        "ashtakavarga": av,
        "yogas": yoga_list,
        "panchang_at_birth": birth_panchang,
        "transits_now": {p: {"sign": s, "sign_en": SIGNS_EN[s], "sign_ne": SIGNS_NE[s]} for p, s in transit_signs.items()},
        "predictions": preds,
        "report": premium,
        "strength": {
            "shadbala": sb,
            "bhava_bala": bb,
            "vimshopaka": vs,
            "bhava_bala_note": {
                "en": "Bhava Bala = house lord's Shadbala + Drik Bala on the house (Dig Bala of houses omitted — see the method note in the analysis).",
                "ne": "भाव बल = भाव स्वामीको षड्बल + भावमाथिको दृष्टि बल (भावहरूको दिग्बल छाडिएको छ — विश्लेषणको विधि-टिप्पणी हेर्नुहोस्)।",
            },
        },
        "transits_detail": transit_tbl,
        "lal_kitab": lk,
        "numerology": numerology_module.numerology(dob),
        "name_letters": naming_module.name_letters(planets["Moon"]["nakshatra"], planets["Moon"]["pada"]),
        "dasha_phala": dasha_phala,
        "special_lagnas": {
            "arudha_lagna": {
                "sign": special["arudha_lagna"]["sign"],
                "sign_en": SIGNS_EN[special["arudha_lagna"]["sign"]],
                "sign_ne": SIGNS_NE[special["arudha_lagna"]["sign"]],
                "house_from_lagna": charts_module.house_of(special["arudha_lagna"]["sign"], lagna_sign),
                "lord": special["arudha_lagna"]["lord"],
            },
            "upapada": {
                "sign": special["upapada"]["sign"],
                "sign_en": SIGNS_EN[special["upapada"]["sign"]],
                "sign_ne": SIGNS_NE[special["upapada"]["sign"]],
                "house_from_lagna": charts_module.house_of(special["upapada"]["sign"], lagna_sign),
                "lord": special["upapada"]["lord"],
            },
            "chandra_lagna": {
                "sign": special["chandra_lagna_sign"],
                "sign_en": SIGNS_EN[special["chandra_lagna_sign"]],
                "sign_ne": SIGNS_NE[special["chandra_lagna_sign"]],
            },
        },
        "chara_dasha": {
            "direction": chara["direction"],
            "periods": [
                {"sign": p["sign"], "sign_en": p["sign_en"], "sign_ne": p["sign_ne"],
                 "lord": p["lord"], "start": p["start"].date().isoformat(),
                 "end": p["end"].date().isoformat(), "years": p["years"]}
                for p in chara["periods"][:24]
            ],
            "current": (
                {"sign": chara["current"]["sign"], "sign_en": chara["current"]["sign_en"],
                 "sign_ne": chara["current"]["sign_ne"], "lord": chara["current"]["lord"],
                 "start": chara["current"]["start"].date().isoformat(),
                 "end": chara["current"]["end"].date().isoformat(),
                 "years": chara["current"]["years"]}
                if chara["current"] else None
            ),
            "current_antardashas": [
                {"sign": a["sign"], "sign_en": a["sign_en"], "sign_ne": a["sign_ne"],
                 "start": a["start"].date().isoformat(), "end": a["end"].date().isoformat()}
                for a in chara["current_antardashas"]
            ],
        },
        "deep_report": deep_report,
        "yogini": {
            "periods": [
                {"name": p["name"], "planet": p["planet"],
                 "start": p["start"].date().isoformat(), "end": p["end"].date().isoformat(),
                 "years": p["years"]}
                for p in yogini["periods"][:16]
            ],
            "current": (
                {"name": yogini["current"]["name"], "planet": yogini["current"]["planet"],
                 "start": yogini["current"]["start"].date().isoformat(),
                 "end": yogini["current"]["end"].date().isoformat()}
                if yogini["current"] else None
            ),
            "balance_years": round(yogini["balance_years"], 3),
        },
        "tribhagi": {
            "periods": [
                {"lord": p["lord"], "start": p["start"].date().isoformat(),
                 "end": p["end"].date().isoformat(), "years": round(p["years"], 3)}
                for p in tribhagi["periods"][:12]
            ],
            "current": (
                {"lord": tribhagi["current"]["lord"],
                 "start": tribhagi["current"]["start"].date().isoformat(),
                 "end": tribhagi["current"]["end"].date().isoformat()}
                if tribhagi["current"] else None
            ),
            "balance_years": round(tribhagi["balance_years"], 3),
        },
    }
    return bundle


def compute_match(payload_a: dict, payload_b: dict) -> dict:
    from . import matching as matching_module

    def moon_of(payload: dict) -> dict:
        place = resolve_place(payload)
        dob = date.fromisoformat(payload["dob"])
        tob = time.fromisoformat(payload["tob"])
        dt = ephemeris.make_local_datetime(dob, tob, place["tz"])
        jd = ephemeris.to_julian_day(dt)
        planets = ephemeris.planet_longitudes(jd)
        moon = planets["Moon"]
        lagna_sign = int(ephemeris.ascendant(jd, place["lat"], place["lon"], b"W") // 30.0)
        return {
            "moon_sign": moon["sign"], "moon_nakshatra": moon["nakshatra"],
            "lagna_sign": lagna_sign,
            "manglik": doshas_module.manglik(planets, lagna_sign),
        }

    groom = moon_of(payload_a)
    bride = moon_of(payload_b)
    result = matching_module.guna_milan(groom, bride)
    result["groom"] = {
        "moon_sign_en": SIGNS_EN[groom["moon_sign"]], "moon_sign_ne": SIGNS_NE[groom["moon_sign"]],
        "nakshatra_en": NAKSHATRAS_EN[groom["moon_nakshatra"]], "nakshatra_ne": NAKSHATRAS_NE[groom["moon_nakshatra"]],
        "manglik": groom["manglik"],
    }
    result["bride"] = {
        "moon_sign_en": SIGNS_EN[bride["moon_sign"]], "moon_sign_ne": SIGNS_NE[bride["moon_sign"]],
        "nakshatra_en": NAKSHATRAS_EN[bride["moon_nakshatra"]], "nakshatra_ne": NAKSHATRAS_NE[bride["moon_nakshatra"]],
        "manglik": bride["manglik"],
    }
    gm, bm = groom["manglik"], bride["manglik"]
    if gm["present"] and bm["present"]:
        note_en, note_ne = "Both partners are Manglik — the dosha is traditionally considered mutually cancelled.", "दुवै जना माङ्गलिक छन् — यो दोष परम्परागत रूपमा आपसमा निरस्त भएको मानिन्छ।"
    elif gm["present"] or bm["present"]:
        note_en, note_ne = "Only one partner is Manglik — traditionally this asks for remedies or a balancing match.", "एक जना मात्र माङ्गलिक छन् — परम्परागत रूपमा यसका लागि उपाय वा सन्तुलित मेल सुझाव दिइन्छ।"
    else:
        note_en, note_ne = "Neither partner is Manglik.", "दुवै जना माङ्गलिक छैनन्।"
    result["manglik_note"] = {"en": note_en, "ne": note_ne}
    return result
