"""Phase 4: classical utilities — Sarvatobhadra Chakra, dasha pravesh,
transit calendar, ephemeris tables, favourable periods.

Sarvatobhadra Chakra (SBC): the 9x9 "auspicious from all directions" grid
for reading transit vedha (obstruction). Layout follows the grid published
on Wikipedia (citing Gopesh Kumar Ojha's Phaladeepika commentary and
M.K. Aggarwal), cross-checked with P.V.R. Narasimha Rao's "Vedic
Astrology: An Integrated Approach" (Sagar Publications, 2000) for the
vedha rules and worked examples.

Grid coordinates: (row, col), row 0 = north/top, col 0 = west/left.
The 28 nakshatras run clockwise from Krittika at the north-east.
"""
from __future__ import annotations

from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# The 9x9 grid
# ---------------------------------------------------------------------------
# 28 nakshatras in SBC order (Krittika-start), 1-indexed.
# Spellings match astro.names.NAKSHATRAS_EN (plus Abhijit).
_SBC_NAKSHATRAS = [
    "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya",
    "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta",
    "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula",
    "Purva Ashadha", "Uttara Ashadha", "Abhijit", "Shravana", "Dhanishta",
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
    "Ashwini", "Bharani",
]

# (row, col) for each of the 28 nakshatras (1-indexed).
# East side (col 8, rows 1-7): Krittika..Ashlesha.
# South side (row 8, cols 7-1): Magha..Vishakha.
# West side (col 0, rows 7-1): Anuradha..Shravana.
# North side (row 0, cols 1-7): Dhanishtha..Bharani.
_SBC_NAK_POS = {}
for i, name in enumerate(_SBC_NAKSHATRAS):
    n = i + 1  # 1-indexed
    if 1 <= n <= 7:      # east side, top to bottom
        _SBC_NAK_POS[name] = (n, 8)
    elif 8 <= n <= 14:   # south side, right to left
        _SBC_NAK_POS[name] = (8, 15 - n)
    elif 15 <= n <= 21:  # west side, bottom to top
        _SBC_NAK_POS[name] = (22 - n, 0)
    else:                # north side, left to right (22-28)
        _SBC_NAK_POS[name] = (0, n - 21)

# Rasi positions (from the Wikipedia grid).
_SBC_RASI_POS = {
    "Aquarius": (2, 3), "Pisces": (2, 4), "Aries": (2, 5),
    "Capricorn": (3, 2), "Taurus": (3, 6),
    "Sagittarius": (4, 2), "Gemini": (4, 6),
    "Scorpio": (5, 2), "Cancer": (5, 6),
    "Libra": (6, 3), "Virgo": (6, 4), "Leo": (6, 5),
}

# Tithi groups and weekday positions (the 5 central squares).
# Nanda: 1,6,11,16,21,26; Bhadra: 2,7,12,17,22,27; Jaya: 3,8,13,18,23,28;
# Rikta: 4,9,14,19,24,29; Purna: 5,10,15,20,30.
_SBC_TITHI_POS = {
    "Nanda": (4, 5), "Bhadra": (5, 4), "Jaya": (4, 3),
    "Rikta": (3, 4), "Purna": (4, 4),
}
_SBC_WEEKDAY_POS = {
    "Sunday": (4, 5), "Tuesday": (4, 5),
    "Monday": (5, 4), "Wednesday": (5, 4),
    "Thursday": (4, 3), "Friday": (3, 4), "Saturday": (4, 4),
}

# 27-nakshatra name -> 28-system index (Abhijit handled separately).
# Spellings match astro.names.NAKSHATRAS_EN.
_27_TO_28 = {
    "Krittika": 1, "Rohini": 2, "Mrigashira": 3, "Ardra": 4,
    "Punarvasu": 5, "Pushya": 6, "Ashlesha": 7, "Magha": 8,
    "Purva Phalguni": 9, "Uttara Phalguni": 10, "Hasta": 11,
    "Chitra": 12, "Swati": 13, "Vishakha": 14, "Anuradha": 15,
    "Jyeshtha": 16, "Mula": 17, "Purva Ashadha": 18, "Uttara Ashadha": 19,
    "Shravana": 21, "Dhanishta": 22, "Shatabhisha": 23,
    "Purva Bhadrapada": 24, "Uttara Bhadrapada": 25, "Revati": 26,
    "Ashwini": 27, "Bharani": 28,
}

# Abhijit: Capricorn 6°40' to 10°53'20".
_ABHIJIT_START = 270.0 + 6.0 + 40.0 / 60.0
_ABHIJIT_END = 270.0 + 10.0 + 53.0 / 60.0 + 20.0 / 3600.0

# Benefics and malefics for vedha.
_BENEFICS = {"Moon", "Mercury", "Jupiter", "Venus"}
_MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}


def nakshatra_28(longitude: float, nakshatra_27_name: str) -> str:
    """The 28-system nakshatra for a longitude (Abhijit aware)."""
    lon = longitude % 360.0
    if _ABHIJIT_START <= lon < _ABHIJIT_END:
        return "Abhijit"
    return _SBC_NAKSHATRAS[_27_TO_28[nakshatra_27_name] - 1]


def _trace_line(r: int, c: int, dr: int, dc: int) -> list[tuple[int, int]]:
    """All cells from (r,c) along (dr,dc), inclusive, within the 9x9."""
    cells = []
    while 0 <= r < 9 and 0 <= c < 9:
        cells.append((r, c))
        r += dr
        c += dc
    return cells


def vedha_lines(nakshatra: str) -> list[list[tuple[int, int]]]:
    """The 3 vedha lines from a nakshatra: 1 straight + 2 diagonals.

    From the nakshatra's border position: straight across the grid, plus
    the two inward diagonals. (P.V.R. Narasimha Rao's method; cf. the
    Saturn-in-Punarvasu worked example.)
    """
    r, c = _SBC_NAK_POS[nakshatra]
    lines = []
    if c == 8:      # east border -> west, NW, SW
        lines = [_trace_line(r, c, 0, -1),
                 _trace_line(r, c, -1, -1),
                 _trace_line(r, c, 1, -1)]
    elif c == 0:    # west border -> east, NE, SE
        lines = [_trace_line(r, c, 0, 1),
                 _trace_line(r, c, -1, 1),
                 _trace_line(r, c, 1, 1)]
    elif r == 0:    # north border -> south, SW, SE
        lines = [_trace_line(r, c, 1, 0),
                 _trace_line(r, c, 1, -1),
                 _trace_line(r, c, 1, 1)]
    else:           # south border -> north, NW, NE
        lines = [_trace_line(r, c, -1, 0),
                 _trace_line(r, c, -1, -1),
                 _trace_line(r, c, -1, 1)]
    return lines


def vedha_cells(nakshatra: str) -> set[tuple[int, int]]:
    """All grid cells under vedha from a planet in `nakshatra`."""
    cells: set[tuple[int, int]] = set()
    for line in vedha_lines(nakshatra):
        cells.update(line)
    return cells


def tithi_group(tithi: int) -> str:
    """Nanda/Bhadra/Jaya/Rikta/Purna for tithi 1-30."""
    return ["Nanda", "Bhadra", "Jaya", "Rikta", "Purna"][(tithi - 1) % 5]


def sarvatobhadra(natal: dict, transits: dict) -> dict:
    """Vedha of transiting planets on the natal reference points.

    natal: {moon_nakshatra_27, moon_longitude, lagna_rasi_en, tithi,
            weekday_en}
    transits: {planet: {nakshatra_27, longitude}}
    Returns per-planet vedha hits and a summary of benefic/malefic
    vedha on each natal point.
    """
    from .names import SIGNS_EN

    # Natal reference cells.
    janma_nak = nakshatra_28(natal["moon_longitude"],
                             natal["moon_nakshatra_27"])
    natal_cells = {
        "janma_nakshatra": _SBC_NAK_POS[janma_nak],
        "lagna_rasi": _SBC_RASI_POS[natal["lagna_rasi_en"]],
        "tithi": _SBC_TITHI_POS[tithi_group(natal["tithi"])],
        "weekday": _SBC_WEEKDAY_POS[natal["weekday_en"]],
    }

    planets = []
    summary: dict[str, dict[str, list[str]]] = {
        key: {"benefic": [], "malefic": []} for key in natal_cells
    }
    for planet, t in transits.items():
        t_nak = nakshatra_28(t["longitude"], t["nakshatra_27"])
        cells = vedha_cells(t_nak)
        hits = [key for key, cell in natal_cells.items() if cell in cells]
        nature = ("benefic" if planet in _BENEFICS else
                  "malefic" if planet in _MALEFICS else "neutral")
        planets.append({
            "planet": planet,
            "nakshatra_28": t_nak,
            "vedha_hits": hits,
            "nature": nature,
        })
        for key in hits:
            if nature in ("benefic", "malefic"):
                summary[key][nature].append(planet)

    return {
        "natal_points": {
            "janma_nakshatra_28": janma_nak,
            "tithi_group": tithi_group(natal["tithi"]),
        },
        "planets": planets,
        "summary": summary,
        "note": ("Vedha by benefics (Moon, Mercury, Jupiter, Venus) is "
                 "favourable; by malefics (Sun, Mars, Saturn, Rahu, Ketu) "
                 "unfavourable. A prediction needs 2-3 natal points under "
                 "vedha from a couple of planets, confirmed by dashas."),
    }


# ---------------------------------------------------------------------------
# Ishta Devta — the personal deity (Jaimini)
# ---------------------------------------------------------------------------
# Planet -> Ishta Devta (Jaimini Upadesha Sutras 1.2.72-79; BPHS).
_ISHTA_DEVATA = {
    "Sun": ("Shiva", "शिव"),
    "Moon": ("Gauri (Parvati)", "गौरी (पार्वती)"),
    "Mars": ("Skanda (Subrahmanya)", "स्कन्द (सुब्रह्मण्य)"),
    "Mercury": ("Vishnu", "विष्णु"),
    "Jupiter": ("Samba Shiva", "साम्ब शिव"),
    "Venus": ("Lakshmi", "लक्ष्मी"),
    "Saturn": ("Vishnu (Kurma)", "विष्णु (कूर्म)"),
    "Rahu": ("Durga", "दुर्गा"),
    "Ketu": ("Ganesha", "गणेश"),
}


def ishta_devta(atmakaraka: str, navamsa: dict) -> dict:
    """The Ishta Devta from the Karakamsa (Atmakaraka's Navamsa sign).

    The 12th from Karakamsa is Jivanmuktamsa: a planet there (strongest
    if several) indicates the deity; if empty, the lord of that sign.
    navamsa: {body: sign 0-11} from build_chart(..., "D9").
    """
    from .names import SIGNS_EN, SIGNS_NE
    # Sign lords (whole-sign).
    _LORDS = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
              "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]

    karakamsa = navamsa[atmakaraka]
    jivan = (karakamsa + 11) % 12  # 12th from Karakamsa
    occupants = [p for p in ("Sun", "Moon", "Mars", "Mercury", "Jupiter",
                             "Venus", "Saturn", "Rahu", "Ketu")
                 if navamsa.get(p) == jivan]
    if occupants:
        # Strongest = highest degree in sign; we don't have degrees here,
        # so list all and take the first as primary.
        indicator = occupants[0]
        method = "planet in Jivanmuktamsa"
    else:
        indicator = _LORDS[jivan]
        method = "lord of Jivanmuktamsa (house empty)"
    deity_en, deity_ne = _ISHTA_DEVATA[indicator]
    return {
        "atmakaraka": atmakaraka,
        "karakamsa_en": SIGNS_EN[karakamsa],
        "karakamsa_ne": SIGNS_NE[karakamsa],
        "jivanmuktamsa_en": SIGNS_EN[jivan],
        "jivanmuktamsa_ne": SIGNS_NE[jivan],
        "indicator_planet": indicator,
        "method": method,
        "deity_en": deity_en,
        "deity_ne": deity_ne,
        "note": ("Ishta Devta guides the soul toward moksha. Worship of "
                 "this form is classically recommended."),
    }


# ---------------------------------------------------------------------------
# Baby-name syllables — the 108 nakshatra-pada aksharas
# ---------------------------------------------------------------------------
# North-Indian list (astrosimply, cross-checked vs Dekho Panchang/Daanyam/
# VedicFeed). Spellings match astro.names.NAKSHATRAS_EN.
_PADA_SYLLABLES = {
    "Ashwini": ["Chu", "Che", "Cho", "La"],
    "Bharani": ["Li", "Lu", "Le", "Lo"],
    "Krittika": ["A", "I", "U", "E"],
    "Rohini": ["O", "Va", "Vi", "Vu"],
    "Mrigashira": ["Ve", "Vo", "Ka", "Ki"],
    "Ardra": ["Ku", "Gha", "Ng", "Chha"],
    "Punarvasu": ["Ke", "Ko", "Ha", "Hi"],
    "Pushya": ["Hu", "He", "Ho", "Da"],
    "Ashlesha": ["Di", "Du", "De", "Do"],
    "Magha": ["Ma", "Mi", "Mu", "Me"],
    "Purva Phalguni": ["Mo", "Ta", "Ti", "Tu"],
    "Uttara Phalguni": ["Te", "To", "Pa", "Pi"],
    "Hasta": ["Pu", "Sha", "Na", "Tha"],
    "Chitra": ["Pe", "Po", "Ra", "Ri"],
    "Swati": ["Ru", "Re", "Ro", "Ta"],
    "Vishakha": ["Ti", "Tu", "Te", "To"],
    "Anuradha": ["Na", "Ni", "Nu", "Ne"],
    "Jyeshtha": ["No", "Ya", "Yi", "Yu"],
    "Mula": ["Ye", "Yo", "Bha", "Bhi"],
    "Purva Ashadha": ["Bhu", "Dha", "Pha", "Dha"],
    "Uttara Ashadha": ["Bhe", "Bho", "Ja", "Ji"],
    "Shravana": ["Khi", "Khu", "Khe", "Kho"],
    "Dhanishta": ["Ga", "Gi", "Gu", "Ge"],
    "Shatabhisha": ["Go", "Sa", "Si", "Su"],
    "Purva Bhadrapada": ["Se", "So", "Da", "Di"],
    "Uttara Bhadrapada": ["Du", "Tha", "Jha", "Jna"],
    "Revati": ["De", "Do", "Cha", "Chi"],
}


def baby_name_syllables(nakshatra_27: str, pada: int) -> dict:
    """The Namakaran syllable for a Moon nakshatra + pada (1-4).

    Returns the pada's syllable plus the other three of the nakshatra
    (all four are considered auspicious).
    """
    syllables = _PADA_SYLLABLES[nakshatra_27]
    return {
        "nakshatra": nakshatra_27,
        "pada": pada,
        "syllable": syllables[pada - 1],
        "all_padas": syllables,
        "note": ("The name traditionally begins with this sound. All four "
                 "padas of the janma nakshatra are auspicious; regional "
                 "panchangs differ on a few cells — the family pandit's "
                 "panchang is authoritative."),
    }

def dasha_pravesh(birth_dt: datetime, dasha_start: datetime,
                  lat: float, lon: float) -> dict:
    """Planetary longitudes and Lagna at the moment a dasha begins.

    The dasha pravesh chakra is cast for the dasha-start instant at the
    birth location; it is read alongside the natal chart to judge the
    dasha's character.
    """
    from .ephemeris import (ascendant, planet_longitudes, sign_of,
                            to_julian_day)
    from .names import SIGNS_EN, SIGNS_NE

    jd = to_julian_day(dasha_start.replace(tzinfo=None))
    longs = planet_longitudes(jd)
    lagna_lon = ascendant(jd, lat, lon) % 360.0
    planets = []
    for name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus",
                 "Saturn", "Rahu", "Ketu"]:
        plon = longs[name]["longitude"] % 360.0
        s = sign_of(plon)
        planets.append({
            "planet": name,
            "longitude": round(plon, 3),
            "sign": s,
            "sign_en": SIGNS_EN[s],
            "sign_ne": SIGNS_NE[s],
        })
    ls = sign_of(lagna_lon)
    return {
        "dasha_start": dasha_start.date().isoformat(),
        "lagna": {"longitude": round(lagna_lon, 3), "sign": ls,
                  "sign_en": SIGNS_EN[ls], "sign_ne": SIGNS_NE[ls]},
        "planets": planets,
        "note": ("Dasha pravesh chakra: transits at the dasha-entry moment, "
                 "read with the natal chart."),
    }


# ---------------------------------------------------------------------------
# Transit calendar — ingresses for the coming 12 months
# ---------------------------------------------------------------------------

def transit_calendar(now: datetime, months: int = 12) -> dict:
    """Saturn/Jupiter/Rahu ingresses (sign changes) over `months`.

    Uses the existing ingress chains, clipped to the window.
    """
    from . import transits as transits_module
    from .ephemeris import to_julian_day
    from .names import SIGNS_EN, SIGNS_NE

    jd_now = to_julian_day(now.replace(tzinfo=None))
    jd_end = jd_now + months * 30.44
    events = []
    for planet in ("Saturn", "Jupiter", "Rahu", "Ketu"):
        chain = transits_module.ingress_chain(planet, jd_now, jd_end)
        for ing in chain:
            events.append({
                "planet": planet,
                "date": ing["date"],
                "from_sign_en": SIGNS_EN[ing["from_sign"]],
                "to_sign_en": SIGNS_EN[ing["to_sign"]],
                "to_sign_ne": SIGNS_NE[ing["to_sign"]],
            })
    events.sort(key=lambda e: e["date"])
    return {"events": events, "months": months}


# ---------------------------------------------------------------------------
# Ephemeris table — daily longitudes for a month
# ---------------------------------------------------------------------------

def ephemeris_table(year: int, month: int) -> dict:
    """Daily sidereal longitudes (sign + degree) for the 7 classical
    planets + nodes, for each day of `month`. A mini ephemeris."""
    from .ephemeris import planet_longitudes, sign_of, to_julian_day
    from .names import SIGNS_EN, SIGNS_NE
    import calendar

    ndays = calendar.monthrange(year, month)[1]
    rows = []
    for day in range(1, ndays + 1):
        jd = to_julian_day(datetime(year, month, day))
        longs = planet_longitudes(jd)
        entry: dict = {"date": f"{year:04d}-{month:02d}-{day:02d}"}
        for name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter",
                     "Venus", "Saturn", "Rahu", "Ketu"]:
            plon = longs[name]["longitude"] % 360.0
            s = sign_of(plon)
            entry[name] = {
                "sign_en": SIGNS_EN[s], "sign_ne": SIGNS_NE[s],
                "degree": round(plon % 30.0, 1),
            }
        rows.append(entry)
    return {"year": year, "month": month, "rows": rows}


# ---------------------------------------------------------------------------
# Favourable periods — 30-day outlook from tara bala + dasha
# ---------------------------------------------------------------------------

def favourable_periods(birth_dt: datetime, janma_nak_idx: int,
                       dasha_tree: dict,
                       now: datetime | None = None,
                       days: int = 30) -> dict:
    """Day-by-day outlook: Tara Bala from the transit Moon against the
    janma nakshatra, plus the running Vimshottari MD/AD.

    Tara: (transit_nak - janma_nak) % 9 -> Janma(1)/Sampat(2)/Vipat(3)/
    Kshema(4)/Pratyak(5)/Sadhana(6)/Naidhana(7)/Mitra(8)/ParamaMitra(0).
    Good: 2,4,6,8,0. Bad: 1,3,5,7.
    """
    from . import nakshatra as nakshatra_module
    from .dasha import period_at
    from .ephemeris import planet_longitude_at, to_julian_day

    at = now or datetime.now(birth_dt.tzinfo)
    out = []
    for d in range(days):
        day = at + timedelta(days=d)
        jd = to_julian_day(day.replace(tzinfo=None))
        moon_lon = planet_longitude_at("Moon", jd) % 360.0
        t_nak = int(moon_lon // (360.0 / 27.0))
        tara_num = (t_nak - janma_nak_idx) % 9
        # 0-indexed: 0=Janma,1=Sampat,2=Vipat,3=Kshema,4=Pratyak,
        # 5=Sadhana,6=Naidhana,7=Mitra,8=ParamaMitra
        good = tara_num in (1, 3, 5, 7, 8)
        md, ad = period_at(dasha_tree, day)
        out.append({
            "date": day.date().isoformat(),
            "tara": tara_num + 1,  # 1-9
            "tara_good": good,
            "md": md["lord"] if md else None,
            "ad": ad["lord"] if ad else None,
        })
    good_days = sum(1 for r in out if r["tara_good"])
    return {
        "days": out,
        "good_days": good_days,
        "note": ("Tara Bala from the daily Moon; Sampat/Kshema/Sadhana/"
                 "Mitra/ParamaMitra taras favour new undertakings."),
    }
