"""Premium-report v2 tests (interpretation engine, Jaimini layer).

Goldens are hand-computed from the published rules — the working is
shown in comments — plus one genuinely published worked example:
P. V. R. Narasimha Rao's Chara dasha test chart (Chennai,
1996-12-07 10:34), whose KN Rao durations ship in PyJHora's own
test suite (jhora.tests.pvr_tests.chara_dhasa_test).
"""
from datetime import datetime
from zoneinfo import ZoneInfo

from astro import engine, jaimini, pdf, transits
from astro.charts import house_lords
from astro.names import HOUSE_NAMES_EN

SAMPLE = {"name": "Sample", "dob": "1998-05-14", "tob": "06:30:00", "place_id": "kathmandu"}
NOW = datetime(2026, 10, 23, 12, 0, tzinfo=ZoneInfo("Asia/Kathmandu"))


def _planets(signs: dict[str, int], degrees: dict[str, float] | None = None) -> dict:
    degrees = degrees or {}
    return {p: {"sign": s, "degree_in_sign": degrees.get(p, 10.0)}
            for p, s in signs.items()}


_ALL = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]


def _full(partial: dict[str, int]) -> dict:
    signs = {p: 0 for p in _ALL}
    signs.update(partial)
    return _planets(signs)


# ---------------------------------------------------------------------------
# Arudha / Upapada goldens (hand-computed)
# ---------------------------------------------------------------------------
def test_arudha_hand_computed_plain():
    # Lagna Aries (0); Lagna lord Mars in Taurus (1).
    # Count Aries->Taurus inclusive = 2; AL = 2 signs from Taurus = Gemini (2).
    # Offset of AL from Lagna = 3rd sign -> no exception.
    planets = _full({"Mars": 1})
    al, work = jaimini.bhava_arudha(planets, 0)
    assert work["count"] == 2 and al == 2


def test_arudha_exception_on_lagna():
    # Lagna Aries; Mars in Aries: count 1 -> AL candidate = Aries itself.
    # The sutra exception fires: take the 10th from the candidate = Capricorn (9).
    planets = _full({"Mars": 0})
    al, work = jaimini.bhava_arudha(planets, 0)
    assert work["exception"] is True and al == 9


def test_arudha_exception_on_seventh():
    # Lagna Aries; Mars in Cancer (3): count = 4 -> AL = Cancer + 4 - 1 = Libra (6),
    # which is the 7th sign from Aries -> exception: 10th from Libra = Cancer (3).
    planets = _full({"Mars": 3})
    al, work = jaimini.bhava_arudha(planets, 0)
    assert work["exception"] is True and al == 3


def test_upapada_hand_computed():
    # Lagna Gemini (2) -> 12th sign Taurus (1), lord Venus in Virgo (5).
    # Count Taurus->Virgo inclusive = 5; UL = 5 from Virgo = Capricorn (9).
    # Offset from the 12th sign = 9th -> no exception.
    planets = _full({"Venus": 5})
    ul, work = jaimini.bhava_arudha(planets, 1)
    assert work["count"] == 5 and work["exception"] is False and ul == 9


def test_sample_special_lagnas():
    # Sample chart (Taurus Lagna, verified positions):
    #  AL: Lagna lord Venus in Pisces (11). Count Taurus->Pisces = 11;
    #      AL = Pisces + 11 - 1 = Capricorn (9). Offset from Lagna = 9th
    #      sign -> no exception.
    #  UL: 12th sign Aries (0), lord Mars in Aries (0). Count = 1 ->
    #      candidate Aries = the 12th sign itself -> exception ->
    #      10th from Aries = Capricorn (9).
    b = engine.compute_kundali(SAMPLE, now=NOW)
    assert b["special_lagnas"]["arudha_lagna"]["sign"] == 9
    assert b["special_lagnas"]["upapada"]["sign"] == 9
    assert b["special_lagnas"]["chandra_lagna"]["sign"] == 7  # Moon in Scorpio


# ---------------------------------------------------------------------------
# Chara dasha goldens
# ---------------------------------------------------------------------------
def test_chara_pvr_published_example():
    """PVR's published KN Rao example (PyJHora pvr_tests): Chennai,
    1996-12-07 10:34. Lagna Capricorn; 9th sign Virgo is even-footed,
    so the sequence runs in reverse. Expected durations (years):
    Capricorn 10, Sagittarius 12, Scorpio 4, Libra 12, Virgo 9, Leo 9,
    Cancer 9, Gemini 6, Taurus 5, Aries 4, Pisces 3, Aquarius 11.
    (Scorpio's 4 comes from the stronger co-lord rule: Ketu in Pisces
    is joined by Saturn, Mars in Leo is alone, so Ketu lords Scorpio;
    count Scorpio->Pisces = 5, minus 1 = 4.)"""
    payload = {"dob": "1996-12-07", "tob": "10:34:00", "lat": 13.0878,
               "lon": 80.2785, "tz": "Asia/Kolkata", "place_name": "Chennai"}
    b = engine.compute_kundali(payload, now=NOW)
    assert b["lagna"]["sign"] == 9  # Capricorn
    cd = b["chara_dasha"]
    assert cd["direction"] == "reverse"
    assert [p["sign"] for p in cd["periods"][:12]] == [9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 11, 10]
    assert [p["years"] for p in cd["periods"][:12]] == [10, 12, 4, 12, 9, 9, 9, 6, 5, 4, 3, 11]
    assert cd["periods"][0]["start"] == "1996-12-07"
    # First period 10 years -> next starts within days of 2006-12-07
    # (365.25-day years vs PyJHora's sidereal year: tolerance 5 days).
    from datetime import date
    second = date.fromisoformat(cd["periods"][1]["start"])
    assert abs((second - date(2006, 12, 8)).days) <= 5


def test_chara_sample_hand_computed():
    """Sample chart by hand (Taurus Lagna -> reverse sequence).
    Taurus: Venus Pisces, ojapada count 11 -> 10, Venus exalted +1 = 11.
    Aries: Mars Aries, count 1 -> 12. Pisces: Jupiter Aquarius,
    samapada count 2 -> 1. Aquarius: Saturn (stronger co-lord) Aries,
    count 11 -> 10, debilitated -1 = 9. Capricorn: Saturn Aries,
    count 10 -> 9, debilitated -1 = 8. Sagittarius: Jupiter Aquarius,
    count 3 -> 2. Scorpio: Mars (stronger, joined by 3 planets) Aries,
    count 6 -> 5. Libra: Venus Pisces, count 6 -> 5, exalted +1 = 6.
    Virgo: Mercury Aries, samapada count 6 -> 5. Leo: Sun Aries,
    count 5 -> 4, exalted +1 = 5. Cancer: Moon Scorpio, count 9 -> 8,
    debilitated -1 = 7. Gemini: Mercury Aries, count 11 -> 10."""
    b = engine.compute_kundali(SAMPLE, now=NOW)
    cd = b["chara_dasha"]
    assert cd["direction"] == "reverse"
    assert [p["sign"] for p in cd["periods"][:12]] == [1, 0, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2]
    assert [p["years"] for p in cd["periods"][:12]] == [11, 12, 1, 9, 8, 2, 5, 6, 5, 5, 7, 10]
    # 1998 + 11 + 12 + 1 = Aquarius runs 2022-05-14 -> 2031-05-14.
    assert cd["current"]["sign"] == 10
    assert cd["current"]["start"] == "2022-05-14"
    assert cd["current"]["end"] == "2031-05-14"
    assert len(cd["current_antardashas"]) == 12


# ---------------------------------------------------------------------------
# Combinatorial integrity of the interpretation engine
# ---------------------------------------------------------------------------
def test_planet_chapters_name_true_lordships():
    b = engine.compute_kundali(SAMPLE, now=NOW)
    chapters = b["deep_report"]["planet_chapters"]
    lords = house_lords(b["lagna"]["sign"])
    for planet in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
        text = " ".join(f["en"] for f in chapters[planet])
        ruled = [h for h, lp in lords.items() if lp == planet]
        for h in ruled:
            assert f"{HOUSE_NAMES_EN[h-1]} house" in text, (planet, h)
        # The planet's own placement sign is named in its chapter.
        row = next(p for p in b["planets"] if p["planet"] == planet)
        assert row["sign_en"] in text, planet
        # Graha chapters carry at least four fact paragraphs.
        assert len(chapters[planet]) >= 4, planet
    # The brief's named check: Mercury for Taurus Lagna = 2nd & 5th lord.
    mercury = " ".join(f["en"] for f in chapters["Mercury"])
    assert "2nd house" in mercury and "5th house" in mercury
    # Saturn is the Yogakaraka for Taurus (rules trine 9 + kendra 10).
    saturn = " ".join(f["en"] for f in chapters["Saturn"])
    assert "Yogakaraka" in saturn


def test_house_chapter_ten_names_true_lord():
    b = engine.compute_kundali(SAMPLE, now=NOW)
    h10 = b["deep_report"]["house_chapters"][9]
    assert h10["house"] == 10 and h10["lord"] == "Saturn" and h10["sign"] == 10
    assert "Saturn" in h10["facts"][0]["en"] and "Aquarius" in h10["facts"][0]["en"]
    # House 12 occupants are Sun, Mars, Mercury, Saturn — all named.
    h12_text = " ".join(f["en"] for f in b["deep_report"]["house_chapters"][11]["facts"])
    for name in ("Sun", "Mars", "Mercury", "Saturn"):
        assert name in h12_text, name


def test_deep_report_language_parity():
    b = engine.compute_kundali(SAMPLE, now=NOW)
    bad = []

    def walk(node, path=""):
        if isinstance(node, dict):
            if "en" in node or "ne" in node:
                if not (isinstance(node.get("en"), str) and node["en"].strip()):
                    bad.append(path + ".en")
                if not (isinstance(node.get("ne"), str) and node["ne"].strip()):
                    bad.append(path + ".ne")
                return
            for k, v in node.items():
                walk(v, f"{path}.{k}")
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{path}[{i}]")

    walk(b["deep_report"])
    assert bad == []


# ---------------------------------------------------------------------------
# Transits: Sade Sati span dates + double transit
# ---------------------------------------------------------------------------
def test_sade_sati_span_dates_golden():
    # Sample Moon is Scorpio (7). At 2013-01-15 Saturn is in Libra:
    # documented sidereal ingresses — into Libra 2012-08-04, into
    # Scorpio 2014-11-02, into Sagittarius 2017-01-26, into Capricorn
    # 2020-01-24 (the end of the span).
    from astro import ephemeris
    jd = ephemeris.to_julian_day(datetime(2013, 1, 15, 12, 0, tzinfo=ZoneInfo("Asia/Kathmandu")))
    span = transits.saturn_moon_span(7, jd)
    assert span == {"start": "2012-08-04", "peak_start": "2014-11-02",
                    "setting_start": "2017-01-26", "end": "2020-01-24"}
    b = engine.compute_kundali(SAMPLE, now=datetime(2013, 1, 15, 12, 0,
                                                    tzinfo=ZoneInfo("Asia/Kathmandu")))
    detail = b["deep_report"]["transit_phala"]["sade_sati_detail"]
    assert detail is not None
    assert "2012-08-04" in detail["en"] and "2020-01-24" in detail["en"]


def test_double_transit_activation():
    b = engine.compute_kundali(SAMPLE, now=NOW)
    dt = b["deep_report"]["transit_phala"]["double_transit"]
    # Oct 2026: Saturn in Pisces aspects Pisces/Aries/Cancer/Scorpio;
    # Jupiter in Cancer aspects Cancer/Scorpio/Pisces/Aquarius.
    # Joint activation = Pisces alone = 11th house from Taurus Lagna.
    assert dt["joint_signs"] == [11]
    assert dt["joint_houses_from_lagna"] == [11]
    assert dt["note"] is not None and "Pisces" in dt["note"]["en"]


# ---------------------------------------------------------------------------
# Forecast v2 + remedies keyed to Shadbala
# ---------------------------------------------------------------------------
def test_forecast_v2_has_chara_and_transit_events():
    b = engine.compute_kundali(SAMPLE, now=NOW)
    rows = b["report"]["favourable_periods"]
    assert len(rows) == 10
    assert all(r["chara_sign"] for r in rows)
    assert "Chara" in rows[0]["summary"]["en"]
    all_events = [e for r in rows for e in r["transit_events"]]
    assert len(all_events) >= 8  # ~10 Jupiter + ~4 Saturn + ~6 Rahu ingresses
    assert all(e["en"] and e["ne"] for e in all_events)


def test_remedies_weak_planet_support_matches_shadbala():
    b = engine.compute_kundali(SAMPLE, now=NOW)
    sb = b["strength"]["shadbala"]["planets"]
    two_weakest = [p for p, _ in sorted(sb.items(), key=lambda kv: kv[1]["rank"], reverse=True)][:2]
    support = b["report"]["remedies"]["weak_planet_support"]
    assert [w["planet"] for w in support] == two_weakest == ["Saturn", "Mercury"]
    for w in support:
        assert w["note"]["en"] and w["note"]["ne"]
        assert w["mantra_ne"] and w["rudraksha"]["en"]


# ---------------------------------------------------------------------------
# PDF: structure + size growth
# ---------------------------------------------------------------------------
def test_pdf_premium_structure_and_size():
    b = engine.compute_kundali(SAMPLE, now=NOW)
    html_en = pdf.build_html(b, "en")
    assert "Contents" in html_en
    for pname in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"):
        assert f"<h3>{pname}</h3>" in html_en, pname
    assert "House 10" in html_en          # house chapters present
    assert "Arudha" in html_en and "Chara" in html_en
    en_bytes = pdf.render_pdf(b, "en")
    ne_bytes = pdf.render_pdf(b, "ne")
    # Previous premium PDF was 38,930 B (EN) / 39,738 B (NE).
    assert len(en_bytes) > 100_000, len(en_bytes)
    assert len(ne_bytes) > 100_000, len(ne_bytes)
