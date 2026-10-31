"""Engine facade — assembles the complete kundali bundle from birth data."""
from __future__ import annotations

from datetime import date, datetime, time, timezone
from zoneinfo import ZoneInfo

from . import (
    argala as argala_module,
    ashtakavarga as av_module,
    ayanamsa as ayanamsa_module,
    bala as bala_module,
    chalit as chalit_module,
    chara as chara_module,
    charts as charts_module,
    dasha as dasha_module,
    dasha_phase3 as dasha_p3_module,
    doshas as doshas_module,
    ephemeris,
    phase4 as phase4_module,
    interpret as interpret_module,
    jaimini as jaimini_module,
    kp as kp_module,
    kp_events as kp_events_module,
    lalkitab as lk_module,
    nakshatra as nakshatra_module,
    naming as naming_module,
    numerology as numerology_module,
    panchang as panchang_module,
    places as places_module,
    prastara as prastara_module,
    predictions as predictions_module,
    special_lagnas as special_lagnas_module,
    sudarshana as sudarshana_module,
    transits as transits_module,
    upagrahas as upagrahas_module,
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
                pd_entries = []
                for pd in ad["pratyantardashas"]:
                    pd_entry = _serialize_period(pd)
                    if "sookshma_dashas" in pd:
                        sk_entries = []
                        for sk in pd["sookshma_dashas"]:
                            sk_entry = _serialize_period(sk)
                            if "prana_dashas" in sk:
                                sk_entry["prana_dashas"] = [_serialize_period(x) for x in sk["prana_dashas"]]
                            sk_entries.append(sk_entry)
                        pd_entry["sookshma_dashas"] = sk_entries
                    pd_entries.append(pd_entry)
                entry["pratyantardashas"] = pd_entries
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
            "sookshma": _serialize_period(cur.get("sookshma")),
            "prana": _serialize_period(cur.get("prana")),
        }
    return {"mahadashas": mds, "current": current, "balance_years": round(tree["balance_years"], 3)}


def _serialize_ashtottari(tree: dict, birth_dt: datetime,
                        cycle_years: int = 108) -> dict:
    mds = []
    for md in tree["mahadashas"]:
        m = _serialize_period(md)
        m["antardashas"] = [_serialize_period(a) for a in md["antardashas"]]
        if md["start"] < birth_dt:
            m["display_start"] = birth_dt.date().isoformat()
        mds.append(m)
    cur = tree.get("current")
    current = None
    if cur:
        current = {
            "mahadasha": _serialize_period(cur["mahadasha"]),
            "antardasha": _serialize_period(cur.get("antardasha")),
        }
    return {"mahadashas": mds, "current": current,
            "balance_years": round(tree["balance_years"], 3),
            "birth_division": tree.get("birth_division"),
            "cycle_years": cycle_years}


def _serialize_sign_dasha(tree: dict, birth_dt: datetime) -> dict:
    """Serialize a sign-based dasha tree (Narayana / Kalachakra)."""
    from .names import SIGNS_EN, SIGNS_NE

    def ser_sign(p: dict | None) -> dict | None:
        if p is None:
            return None
        return {
            "sign": p["sign"],
            "sign_en": SIGNS_EN[p["sign"]],
            "sign_ne": SIGNS_NE[p["sign"]],
            "start": p["start"].date().isoformat(),
            "end": p["end"].date().isoformat(),
            "years": round(p["years"], 3),
        }

    mds = []
    for md in tree["mahadashas"]:
        m = ser_sign(md)
        m["antardashas"] = [ser_sign(a) for a in md["antardashas"]]
        if md["start"] < birth_dt:
            m["display_start"] = birth_dt.date().isoformat()
        mds.append(m)
    cur = tree.get("current")
    current = None
    if cur:
        current = {
            "mahadasha": ser_sign(cur["mahadasha"]),
            "antardasha": ser_sign(cur.get("antardasha")),
        }
    out = {"mahadashas": mds, "current": current}
    for key in ("start_sign_en", "start_sign_ne", "forward", "deha_en",
                "deha_ne", "jiva_en", "jiva_ne", "birth_group",
                "birth_pada", "note"):
        if key in tree:
            out[key] = tree[key]
    return out


def _serialize_mudda(tree: dict, birth_dt: datetime) -> dict:
    """Serialize the Mudda annual dasha."""
    periods = []
    for md in tree["periods"]:
        m = {
            "planet": md["planet"],
            "start": md["start"].date().isoformat(),
            "end": md["end"].date().isoformat(),
            "days": round(md["days"], 1),
            "antardashas": [
                {"planet": a["planet"],
                 "start": a["start"].date().isoformat(),
                 "end": a["end"].date().isoformat(),
                 "days": round(a["days"], 2)}
                for a in md["antardashas"]
            ],
        }
        periods.append(m)
    cur = tree.get("current")
    current = None
    if cur:
        current = {
            "mahadasha": cur["mahadasha"]["planet"],
            "antardasha": cur["antardasha"]["planet"] if cur.get("antardasha") else None,
        }
    return {
        "periods": periods,
        "current": current,
        "varshapravesh": tree["varshapravesh"].date().isoformat(),
        "completed_years": tree["completed_years"],
        "note": tree.get("note"),
    }


def compute_kundali(payload: dict, now: datetime | None = None) -> dict:
    # Phase 1: the computation honours the requested ayanamsa and house
    # system. The ayanamsa is set thread-locally so every downstream
    # ephemeris call (planets, dashas, transits, KP, panchang) follows it.
    ayanamsa_key = ayanamsa_module.set_ayanamsa(payload.get("ayanamsa"))
    house_system = ephemeris.validate_house_system(payload.get("house_system"))

    place = resolve_place(payload)
    dob = date.fromisoformat(payload["dob"])
    tob = time.fromisoformat(payload["tob"])
    birth_dt = ephemeris.make_local_datetime(dob, tob, place["tz"])
    now = now or datetime.now(ZoneInfo(place["tz"]))

    jd = ephemeris.to_julian_day(birth_dt)
    planets = ephemeris.planet_longitudes(jd)
    lagna_lon = ephemeris.ascendant(jd, place["lat"], place["lon"], b"W")
    lagna_sign = int(lagna_lon // 30.0)
    # Bhava cusps follow the selected house system (drives Bhava Chalit,
    # Shadbala Dig Bala, Bhava Bala). KP doctrinally requires Placidus,
    # so it always gets Placidus cusps regardless of the selection.
    cusps = ephemeris.house_cusps(jd, place["lat"], place["lon"], house_system)
    placidus = ephemeris.placidus_cusps(jd, place["lat"], place["lon"])

    varga_charts = {v: charts_module.build_chart(planets, lagna_lon, v) for v in charts_module.VARGAS}
    combust = charts_module.combustions(planets)
    karakas = charts_module.jaimini_karakas(planets)

    dasha_tree = dasha_module.vimshottari_tree(birth_dt, planets["Moon"]["longitude"], now)
    kp = kp_module.kp_tables(planets, placidus)

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
    shodhya = av_module.compute_shodhya_pindas(av, planets)
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
    # Phase 1: classical special lagnas (BPHS Ch.5) and the six upagrahas.
    # Sunrise-dependent points are skipped gracefully at polar latitudes.
    try:
        classical_lagnas = special_lagnas_module.compute_special_lagnas(
            birth_dt, place["lat"], place["lon"], place["tz"],
            lagna_lon, lagna_sign,
            planets["Moon"]["longitude"], planets["Moon"]["sign"],
            planets["Moon"]["degree_in_sign"])
    except ValueError:
        classical_lagnas = None
    upagrahas = upagrahas_module.compute_upagrahas(
        planets["Sun"]["longitude"], birth_dt, rise, set_,
        place["lat"], place["lon"])
    chara = chara_module.chara_periods(birth_dt, planets, lagna_sign, now)
    # Phase 3 dashas: Narayana (Jaimini), Shodshottari (116-yr),
    # Mudda (Tajika annual), Kalachakra.
    atmakaraka = karakas.get("Atmakaraka")
    narayana = dasha_p3_module.narayana_periods(
        birth_dt, planets, lagna_sign, atmakaraka, now)
    shodsho_tree = dasha_p3_module.shodshottari_tree(
        birth_dt, planets["Moon"]["longitude"], now)
    shodsho_applies = dasha_p3_module.shodshottari_applicability(
        lagna_sign, lagna_lon % 30.0, birth_panchang["paksha"])
    mudda = dasha_p3_module.mudda_dasha(
        birth_dt, planets["Moon"]["longitude"],
        planets["Sun"]["longitude"], now)
    kalachakra = dasha_p3_module.kalachakra_tree(
        birth_dt, planets["Moon"]["longitude"], now)
    # Phase 4: Sarvatobhadra, dasha pravesh, transit calendar,
    # favourable periods.
    from .names import NAKSHATRAS_EN, WEEKDAYS_EN, SIGNS_EN as _SE
    sbc_natal = {
        "moon_nakshatra_27": NAKSHATRAS_EN[birth_panchang["nakshatra_index"]],
        "moon_longitude": planets["Moon"]["longitude"],
        "lagna_rasi_en": _SE[lagna_sign],
        "tithi": birth_panchang["tithi_index"] + 1,
        "weekday_en": WEEKDAYS_EN[birth_panchang["weekday"]],
    }
    # Reuse now_planets (computed above) — avoids a duplicate ephemeris call.
    sbc_transits = {
        p: {"nakshatra_27": NAKSHATRAS_EN[now_planets[p]["nakshatra"]],
            "longitude": now_planets[p]["longitude"]}
        for p in ("Sun", "Moon", "Mars", "Mercury", "Jupiter",
                  "Venus", "Saturn", "Rahu", "Ketu")
    }
    sbc = phase4_module.sarvatobhadra(sbc_natal, sbc_transits)
    # Dasha pravesh for the current Vimshottari MD.
    _md_now = dasha_tree["current"]["mahadasha"]
    pravesh = phase4_module.dasha_pravesh(
        birth_dt, _md_now["start"], place["lat"], place["lon"])
    p4_calendar = phase4_module.transit_calendar(now)
    p4_favourable = phase4_module.favourable_periods(
        birth_dt, birth_panchang["nakshatra_index"], dasha_tree, now)
    # Ishta Devta + baby-name syllable.
    _navamsa = varga_charts["D9"]
    ishta = phase4_module.ishta_devta(atmakaraka, _navamsa)
    _moon_nak = NAKSHATRAS_EN[birth_panchang["nakshatra_index"]]
    _moon_pada = birth_panchang["nakshatra_pada"]
    baby_name = phase4_module.baby_name_syllables(_moon_nak, _moon_pada)
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
        "narayana": narayana, "shodshottari": shodsho_tree,
        "shodshottari_applicability": shodsho_applies,
        "mudda": mudda, "kalachakra": kalachakra,
        "sarvatobhadra": sbc, "dasha_pravesh": pravesh,
        "transit_calendar": p4_calendar,
        "favourable_periods": p4_favourable,
        "ishta_devta": ishta, "baby_name": baby_name,
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

    # World-class layer: Bhava Chalit, Prastara, KP event verdicts,
    # Sudarshana Chakra — all computed from this chart's facts.
    chalit = chalit_module.bhava_chalit(planets, cusps, lagna_sign)
    prastara = prastara_module.prastara(planets, lagna_sign)
    kp_events = kp_events_module.kp_event_analysis(kp, dasha_tree, transit_signs, lagna_sign)
    sudar = sudarshana_module.sudarshana(planets, lagna_sign)

    # Gap-closure layer: Argala, Nakshatra deep-dive, Ashtottari,
    # lifetime Sade Sati, Lal Kitab dasha.
    argala = argala_module.argala_full(planets, lagna_sign)
    natal_moon_nak = planets["Moon"]["nakshatra"]
    natal_moon_sign = planets["Moon"]["sign"]
    nakshatra_deep = {
        "nava_tara": nakshatra_module.nava_tara(natal_moon_nak),
        "tarabala_today": nakshatra_module.tara_of(natal_moon_nak, now_planets["Moon"]["nakshatra"]),
        "chandrabala_today": nakshatra_module.chandrabala(natal_moon_sign, transit_signs["Moon"]),
        "avasthas": nakshatra_module.avasthas_for_chart(planets),
    }
    ashto_tree = dasha_module.ashtottari_tree(birth_dt, planets["Moon"]["longitude"], now)
    is_day_birth = bool(rise and set_ and rise <= birth_dt <= set_)
    ashto_applies = dasha_module.ashtottari_applicability(
        planets, lagna_sign, is_day_birth, birth_panchang["paksha"])
    sade_lifetime = transits_module.sade_sati_lifetime(natal_moon_sign, jd, jd_now)
    lk_dasha = lk_module.lal_kitab_dasha(birth_dt, now)

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
        "shodhya_pindas": shodhya,
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
                "en": "Bhava Bala = house lord's Shadbala + Bhava Dig Bala (directional strength from the sign's nature: Nara east, Chatushpada south, Jalachara north, Keeta west) + Drik Bala on the house.",
                "ne": "भाव बल = भाव स्वामीको षड्बल + भाव दिग्बल (राशिको स्वभावअनुसार दिशागत बल: नर पूर्व, चतुष्पद दक्षिण, जलचर उत्तर, कीट पश्चिम) + भावमाथिको दृष्टि बल।",
            },
        },
        "transits_detail": transit_tbl,
        "lal_kitab": lk,
        "numerology": numerology_module.numerology(dob),
        "name_letters": naming_module.name_letters(planets["Moon"]["nakshatra"], planets["Moon"]["pada"]),
        "dasha_phala": dasha_phala,
        "ayanamsa": {
            "key": ayanamsa_key,
            "name": ayanamsa_module.mode_name(ayanamsa_key),
        },
        "house_system": {
            "key": house_system,
            "name": ephemeris.HOUSE_SYSTEMS[house_system][0],
        },
        "house_cusps": [
            {"cusp": i + 1, "longitude": round(c, 4),
             "sign": int(c // 30) % 12,
             "sign_en": SIGNS_EN[int(c // 30) % 12],
             "sign_ne": SIGNS_NE[int(c // 30) % 12],
             "degree_in_sign": round(c % 30.0, 3)}
            for i, c in enumerate(cusps)
        ],
        "classical_lagnas": (
            {key: {"longitude": v["longitude"], "sign": v["sign"],
                   "sign_en": SIGNS_EN[v["sign"]], "sign_ne": SIGNS_NE[v["sign"]],
                   "degree_in_sign": round(v["longitude"] % 30.0, 3)}
             for key, v in classical_lagnas.items()}
            if classical_lagnas else None
        ),
        "upagrahas": {
            key: ({"longitude": v["longitude"], "sign": v["sign"],
                   "sign_en": SIGNS_EN[v["sign"]], "sign_ne": SIGNS_NE[v["sign"]],
                   "degree_in_sign": round(v["longitude"] % 30.0, 3),
                   **({"segment": v["segment"]} if "segment" in v else {})}
                  if v else None)
            for key, v in upagrahas.items()
        },
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
        "bhava_chalit": chalit,
        "prastara": prastara,
        "kp_events": kp_events,
        "sudarshana": sudar,
        "argala": argala,
        "nakshatra_deep": nakshatra_deep,
        "ashtottari": _serialize_ashtottari(ashto_tree, birth_dt),
        "ashtottari_applicability": ashto_applies,
        "narayana": _serialize_sign_dasha(narayana, birth_dt),
        "shodshottari": _serialize_ashtottari(shodsho_tree, birth_dt, 116),
        "shodshottari_applicability": shodsho_applies,
        "mudda": _serialize_mudda(mudda, birth_dt),
        "kalachakra": _serialize_sign_dasha(kalachakra, birth_dt),
        "sarvatobhadra": sbc,
        "dasha_pravesh": pravesh,
        "transit_calendar": p4_calendar,
        "favourable_periods": p4_favourable,
        "ishta_devta": ishta,
        "baby_name": baby_name,
        "sade_sati_lifetime": sade_lifetime,
        "lal_kitab_dasha": lk_dasha,
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


_MALEFICS = ("Sun", "Mars", "Saturn", "Rahu", "Ketu")
_PAPASAMYA_HOUSES = {1, 2, 4, 7, 8, 12}


def _papasamya(planets: dict, lagna_sign: int) -> dict:
    """Simplified Papasamya dosha count (documented simplification).

    Malefics in houses 1/2/4/7/8/12 counted from three references —
    Lagna, Moon and Venus — summed. Classical Papasamya also weighs
    the specific malefic and house; this count is the widely used
    first-pass balance check: partners with similar totals are
    considered balanced.
    """
    from .charts import house_of

    refs = {"lagna": lagna_sign, "moon": planets["Moon"]["sign"], "venus": planets["Venus"]["sign"]}
    per_ref = {}
    for ref_name, ref_sign in refs.items():
        per_ref[ref_name] = sum(
            1 for m in _MALEFICS if house_of(planets[m]["sign"], ref_sign) in _PAPASAMYA_HOUSES
        )
    return {"per_reference": per_ref, "total": sum(per_ref.values())}


def _bhava_milan(groom: dict, bride: dict) -> dict:
    """Simplified Lagna–Moon harmony (documented simplification).

    Each partner's Moon sign measured from the other's Lagna: distances
    1/5/7/9 are harmonious, 6/8/12 challenging, the rest neutral.
    """
    from .charts import house_of

    def harmony(moon_sign: int, other_lagna: int) -> str:
        d = house_of(moon_sign, other_lagna)
        if d in (1, 5, 7, 9):
            return "harmonious"
        if d in (6, 8, 12):
            return "challenging"
        return "neutral"

    g_to_b = harmony(groom["moon_sign"], bride["lagna_sign"])
    b_to_g = harmony(bride["moon_sign"], groom["lagna_sign"])
    score = {"harmonious": 2, "neutral": 1, "challenging": 0}
    total = score[g_to_b] + score[b_to_g]
    verdict = "Harmonious" if total >= 3 else "Mixed" if total >= 2 else "Challenging"
    return {"groom_moon_vs_bride_lagna": g_to_b, "bride_moon_vs_groom_lagna": b_to_g,
            "verdict": verdict}


def _dasha_sandhi(person: dict, marriage_day: date) -> dict:
    """Dasha-change proximity to a planned marriage date.

    Classical Dasha Sandhi: a Mahadasha or Antardasha change within
    about 6 months of the wedding is considered inauspicious and
    traditionally asks for remedies or a shifted date. Returns the
    nearest boundary in the window, if any.
    """
    from datetime import datetime, timedelta
    from zoneinfo import ZoneInfo

    from . import dasha as dasha_module

    moment = datetime.combine(marriage_day, time(12, 0), tzinfo=ZoneInfo(person["tz"]))
    tree = dasha_module.vimshottari_tree(person["birth_dt"], person["moon_lon"], moment)
    window = timedelta(days=180)
    hits = []
    for md in tree["mahadashas"]:
        for label, start, end, lord in (
            ("Mahadasha", md["start"], md["end"], md["lord"]),
        ):
            for boundary, kind in ((start, "starts"), (end, "ends")):
                if abs((boundary - moment).days) <= 180 and boundary.date() != marriage_day:
                    hits.append({"level": label, "lord": lord, "kind": kind,
                                 "date": boundary.date().isoformat(),
                                 "days_away": (boundary.date() - marriage_day).days})
        for ad in md["antardashas"]:
            for boundary, kind in ((ad["start"], "starts"), (ad["end"], "ends")):
                if abs((boundary - moment).days) <= 180 and boundary.date() != marriage_day:
                    hits.append({"level": "Antardasha", "lord": ad["lord"], "kind": kind,
                                 "date": boundary.date().isoformat(),
                                 "days_away": (boundary.date() - marriage_day).days})
    hits.sort(key=lambda h: abs(h["days_away"]))
    return {"in_window": bool(hits), "nearest": hits[0] if hits else None,
            "all_in_window": hits[:4]}


def compute_match(payload_a: dict, payload_b: dict, marriage_date: str | None = None) -> dict:
    from . import matching as matching_module
    from . import porutham as porutham_module

    def person_of(payload: dict) -> dict:
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
            "lagna_sign": lagna_sign, "planets": planets,
            "birth_dt": dt, "moon_lon": moon["longitude"], "tz": place["tz"],
            "manglik": doshas_module.manglik(planets, lagna_sign),
        }

    groom = person_of(payload_a)
    bride = person_of(payload_b)
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

    # Beyond Guna: Papasamya balance, Lagna–Moon harmony, Dasha Sandhi.
    pap_g = _papasamya(groom["planets"], groom["lagna_sign"])
    pap_b = _papasamya(bride["planets"], bride["lagna_sign"])
    pap_diff = abs(pap_g["total"] - pap_b["total"])
    pap_verdict = "Balanced" if pap_diff <= 3 else "Uneven"
    result["papasamya"] = {
        "groom": pap_g, "bride": pap_b, "difference": pap_diff, "verdict": pap_verdict,
    }
    result["bhava_milan"] = _bhava_milan(groom, bride)
    # Second system: South Indian Dashakoota / Porutham (10 factors).
    result["porutham"] = porutham_module.porutham(groom, bride)
    sandhi = None
    if marriage_date:
        mday = date.fromisoformat(marriage_date)
        sandhi = {"groom": _dasha_sandhi(groom, mday),
                  "bride": _dasha_sandhi(bride, mday)}
    result["dasha_sandhi"] = sandhi
    guna = result.get("total", 0)
    flags = []
    if pap_verdict != "Balanced":
        flags.append("Papasamya is uneven — the dosha load differs between partners.")
    if result["bhava_milan"]["verdict"] == "Challenging":
        flags.append("Lagna–Moon harmony is challenging — understanding needs conscious effort.")
    if sandhi and (sandhi["groom"]["in_window"] or sandhi["bride"]["in_window"]):
        flags.append("A dasha change falls near the planned date (Dasha Sandhi) — traditionally remedies or a shifted date are advised.")
    if guna >= 18 and not flags:
        combined_en = "Strong overall match: Guna Milan is above 18 and the extended checks raise no flag."
        combined_ne = "समग्रमा बलियो मेल: गुण मिलन १८ भन्दा माथि छ र विस्तारित जाँचमा कुनै चेतावनी छैन।"
    elif flags:
        combined_en = "Workable match with notes: " + " ".join(flags)
        combined_ne = "टिप्पणीसहितको सम्भव मेल: " + " ".join(
            {"Papasamya is uneven — the dosha load differs between partners.": "पापसाम्य असन्तुलित छ — दुवैको दोष भार फरक छ।",
             "Lagna–Moon harmony is challenging — understanding needs conscious effort.": "लग्न–चन्द्र सामञ्जस्य चुनौतीपूर्ण छ — बुझाइका लागि सचेत प्रयास चाहिन्छ।",
             "A dasha change falls near the planned date (Dasha Sandhi) — traditionally remedies or a shifted date are advised.": "योजनाबद्ध मितिनजिकै दशा परिवर्तन पर्छ (दशा सन्धि) — परम्परागत रूपमा उपाय वा मिति सार्न सुझाव दिइन्छ।"}.get(f, f)
            for f in flags)
    else:
        combined_en = "Modest match: Guna Milan is below 18 — weigh the extended checks and family counsel."
        combined_ne = "सामान्य मेल: गुण मिलन १८ भन्दा कम छ — विस्तारित जाँच र पारिवारिक सल्लाहलाई तौलिनुहोस्।"
    result["combined_verdict"] = {"en": combined_en, "ne": combined_ne}
    return result
