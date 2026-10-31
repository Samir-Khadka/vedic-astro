"""PDF export of the premium report — premium structure:

cover + birth details & panchang → table of contents → chart set
(Nepali-style D1 + D9) → planetary positions → Shadbala / Bhava Bala /
Vimshopaka → Ashtakavarga tables + interpretation → planet chapters →
house chapters → special lagnas → dasha chapters (Vimshottari
deep-dive, Chara, Yogini, Tribhagi) → divisional chapters → yogas →
doshas & remedies → Lal Kitab → transits & timing synthesis → year
forecast → gemstones & lucky attributes → disclaimer.

Primary renderer: WeasyPrint (HTML/CSS — handles Devanagari when a
suitable font is present). Fallback: reportlab, English-only.
"""
from __future__ import annotations

import html

from .chart_svg import diamond_svg
from .names import (
    HOUSE_NAMES_EN, NAKSHATRAS_EN, NAKSHATRAS_NE, SIGNS_EN, SIGNS_NE,
    TITHIS_EN, TITHIS_NE, WEEKDAYS_EN, WEEKDAYS_NE, YOGAS_EN, YOGAS_NE,
)

CHAPTER_TITLES = {
    "personality": ("Personality", "व्यक्तित्व"),
    "career": ("Career", "पेशा"),
    "finance": ("Finance & Wealth", "धन र सम्पत्ति"),
    "marriage": ("Marriage & Relationships", "विवाह र सम्बन्ध"),
    "health": ("Health", "स्वास्थ्य"),
    "education": ("Education", "शिक्षा"),
    "family": ("Family & Home", "परिवार र घर"),
    "foreign": ("Foreign Travel & Settlement", "विदेश यात्रा र बसोबास"),
}
PREDICTION_TITLES = {
    "current_period": ("Current Dasha Period", "हालको दशा अवधि"),
    "strengths": ("Planetary Strengths", "ग्रहहरूको बल"),
    "transits": ("Transits (Gochar)", "गोचर"),
    "career": ("Career", "पेशा"),
    "wealth": ("Wealth", "धन"),
    "relationships": ("Relationships", "सम्बन्ध"),
    "health": ("Health", "स्वास्थ्य"),
}
PLANET_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]


def _esc(s) -> str:
    return html.escape(str(s))


_CSS = """
@page { size: A4; margin: 18mm 15mm 16mm 15mm;
  @bottom-center { content: "Vedic Astro — Janma Kundali · " counter(page) " / " counter(pages);
                   font-size: 8pt; color: #8a6a4a; } }
@page cover { margin: 0; @bottom-center { content: none; } }
body { font-family: 'Noto Sans Devanagari','DejaVu Sans',sans-serif; color:#3a1e0c; font-size:10.5pt; line-height:1.5;
       background: #fdf9f0; }
/* Cover — light devotional: cream page, double gold-saffron frame */
.cover { page: cover; height: 297mm; box-sizing: border-box; text-align: center;
         background: #fdf9f0; padding: 12mm; }
.cover-frame { border: 3pt double #b8860b; height: 269mm; box-sizing: border-box; padding: 10mm 8mm; }
.cover-frame-inner { border: 1pt solid #e07b0a; height: 100%; box-sizing: border-box;
                     padding-top: 38mm; }
.cover .mangala { font-size: 16pt; color: #7a3c06; margin-bottom: 10mm; }
.cover .om { font-size: 64pt; color: #e07b0a; margin: 0 0 8mm; line-height: 1; }
.cover h1 { font-size: 30pt; color: #5c2f08; margin: 0 6mm 4mm; }
.cover .sub { font-size: 14pt; color: #b85f06; margin: 0 10mm 3mm; }
.cover .meta { margin-top: 12mm; font-size: 11pt; color: #6b4a26; }
.cover .foot { margin-top: 18mm; font-size: 9pt; color: #8a6a4a; }
/* Chapter heads */
h2 { color:#7a3c06; border-bottom:1.5px solid #e07b0a; padding-bottom:1mm; margin-top:7mm;
     font-size:14.5pt; page-break-before: always; }
h2.no-break { page-break-before: auto; }
h2 .ch-num { display:block; font-size:10pt; color:#b85f06; letter-spacing:2pt; margin-bottom:1mm; }
h3 { color:#5c2f08; margin-top:4.5mm; font-size:11.5pt; }
table { border-collapse:collapse; width:100%; margin:2.5mm 0; }
th,td { border:0.5pt solid #d9b98a; padding:1.4mm 1.8mm; text-align:left; font-size:9pt; }
th { background:#fbeed7; color:#7a3c06; }
.meta { color:#555; font-size:9.5pt; }
/* TOC */
.toc { font-size:11pt; line-height:2; }
.toc a { color:#3a1e0c; text-decoration:none; }
.toc a::after { content: leader('.') target-counter(attr(href), page); }
/* Summary cards */
.sum-grid { display: block; }
.sum-card { border: 1pt solid #d9b98a; border-radius: 3mm; background: #fffdf7;
            padding: 4mm 5mm; margin: 0 0 4mm 0; }
.sum-card h3 { margin: 0 0 2mm; color:#b85f06; font-size:12pt; }
.sum-card .count { float: right; font-size: 11pt; color:#e07b0a; font-weight:700; }
.sum-card p { margin: 1mm 0; font-size: 9.5pt; color:#5c3a20; }
/* Birth detail two-column */
.detail-table td { border: none; padding: 2mm 3mm; font-size: 10.5pt; }
.detail-table td.k { color:#b85f06; font-size:9pt; text-transform:uppercase; letter-spacing:0.06em; width:32%; }
.detail-table td.v { font-weight:700; color:#3a1e0c; }
.chart-row { text-align:center; }
.chart-box { display:inline-block; margin:2mm 3mm; vertical-align:top; }
.chart-title { font-weight:700; color:#7a3c06; margin-bottom:1mm; }
p { margin: 1.6mm 0; text-align: justify; }
.small { font-size: 9pt; color:#6b5a44; }
"""


def build_html(bundle: dict, lang: str = "en") -> str:
    name = bundle.get("name") or ("Vedic Astrology Report" if lang == "en" else "वैदिक ज्योतिष रिपोर्ट")
    birth = bundle["birth"]
    place = birth["place"]
    lagna = bundle["lagna"]
    deep = bundle.get("deep_report") or {}
    report = bundle.get("report", {})
    ne = lang == "ne"

    def T(en: str, nep: str) -> str:
        return nep if ne else en

    def pick(bi: dict) -> str:
        if not isinstance(bi, dict):
            return _esc(bi)
        return _esc(bi.get(lang) or bi.get("en", ""))

    def paras(facts) -> str:
        return "".join(f"<p>{pick(f)}</p>" for f in facts or [])

    moon = bundle["planets"][1]
    sections: list[tuple[str, str]] = []  # (anchor, title) for the TOC
    body: list[str] = []

    ch_num = [0]

    def h2(anchor: str, en: str, nep: str, no_break: bool = False) -> None:
        title = nep if ne else en
        ch_num[0] += 1
        label = T(f"Chapter {ch_num[0]}", f"अध्याय {ch_num[0]}")
        sections.append((anchor, f"{label} — {title}"))
        body.append(f"<h2 id='{anchor}'{' class=\"no-break\"' if no_break else ''}>"
                    f"<span class='ch-num'>{_esc(label)}</span>{_esc(title)}</h2>")

    # ---------------------------------------------------------------- cover
    parts = [
        "<!DOCTYPE html><html><head><meta charset='utf-8'><style>",
        _CSS,
        "</style></head><body>",
        "<div class='cover'><div class='cover-frame'><div class='cover-frame-inner'>",
        f"<div class='mangala'>॥ अथ श्री गणेशाय नमः ॥</div>",
        "<div class='om'>ॐ</div>",
        f"<h1>{_esc(name)}</h1>",
        f"<div class='sub'>{T('Janma Kundali', 'जन्म कुण्डली')}</div>",
        f"<div class='meta'>{_esc(birth['date'])} · {_esc(birth['time'])} · {_esc(place['name'])}<br>"
        f"{T('Lagna', 'लग्न')}: {_esc(lagna['sign_ne'] if ne else lagna['sign_en'])} · "
        f"{T('Moon', 'चन्द्र')}: {_esc(moon['sign_ne'] if ne else moon['sign_en'])} / "
        f"{_esc(moon['nakshatra_ne'] if ne else moon['nakshatra_en'])}</div>",
        f"<div class='foot'>{T('Computed with Swiss Ephemeris · Lahiri ayanamsa · Parashari, KP & Jaimini methods',
                                'स्विस एफेमेरिस · लाहिरी अयनांश · पराशरी, KP र जैमिनी विधिबाट गणना')}</div>",
        "</div></div></div>",
    ]

    # ------------------------------------------------- birth details & panchang
    h2("birth", "Birth Details & Panchang", "जन्म विवरण र पञ्चाङ्ग", no_break=True)
    panch = bundle.get("panchang_at_birth") or {}
    tithi = TITHIS_NE[panch["tithi_index"]] if ne else TITHIS_EN[panch["tithi_index"]] \
        if "tithi_index" in panch else ""
    yoga_n = YOGAS_NE[panch["yoga_index"]] if ne else YOGAS_EN[panch["yoga_index"]] \
        if "yoga_index" in panch else ""
    nak_n = NAKSHATRAS_NE[panch["nakshatra_index"]] if ne else NAKSHATRAS_EN[panch["nakshatra_index"]] \
        if "nakshatra_index" in panch else ""
    weekday = ""
    if "weekday" in panch:
        weekday = WEEKDAYS_NE[panch["weekday"]] if ne else WEEKDAYS_EN[panch["weekday"]]
    body.append(
        "<table>"
        f"<tr><th>{T('Date of birth', 'जन्म मिति')}</th><td>{_esc(birth['date'])} ({_esc(weekday)})</td>"
        f"<th>{T('Time of birth', 'जन्म समय')}</th><td>{_esc(birth['time'])}</td></tr>"
        f"<tr><th>{T('Place', 'स्थान')}</th><td>{_esc(place['name'])}</td>"
        f"<th>{T('Coordinates', 'निर्देशाङ्क')}</th><td>{place['lat']}, {place['lon']} · {_esc(place['tz'])}</td></tr>"
        f"<tr><th>{T('Sunrise / Sunset', 'सूर्योदय / सूर्यास्त')}</th><td>{_esc(birth.get('sunrise') or '—')} / {_esc(birth.get('sunset') or '—')}</td>"
        f"<th>{T('Ayanamsa', 'अयनांश')}</th><td>Lahiri</td></tr>"
        f"<tr><th>{T('Tithi', 'तिथि')}</th><td>{_esc(panch.get('paksha', ''))} {_esc(tithi)}</td>"
        f"<th>{T('Nakshatra', 'नक्षत्र')}</th><td>{_esc(nak_n)} · {T('pada', 'पद')} {panch.get('nakshatra_pada', '')}</td></tr>"
        f"<tr><th>{T('Yoga', 'योग')}</th><td>{_esc(yoga_n)}</td>"
        f"<th>{T('Karana', 'करण')}</th><td>{_esc(panch.get('karana', ''))}</td></tr>"
        "</table>"
    )

    # ---------------------------------------------------------------- charts
    h2("charts", "Charts — Rashi (D1) & Navamsa (D9)", "कुण्डलीहरू — राशि (D1) र नवांश (D9)")
    degrees = {p["planet"]: p["degree_in_sign"] for p in bundle["planets"]}
    charts = bundle["charts"]
    body.append("<div class='chart-row'>")
    body.append(diamond_svg(charts["D1"], lagna["sign"], degrees,
                            T("Rashi Chart (D1)", "राशि कुण्डली (D1)")))
    body.append(diamond_svg(charts["D9"], charts["D9"]["Lagna"], None,
                            T("Navamsa Chart (D9)", "नवांश कुण्डली (D9)")))
    body.append("</div>")
    # Key varga signs table
    vargas = ["D1", "D4", "D7", "D9", "D10", "D12", "D20", "D24"]
    body.append(f"<h3>{T('Divisional Chart Signs', 'वर्ग कुण्डलीका राशिहरू')}</h3><table><tr><th>{T('Planet', 'ग्रह')}</th>"
                + "".join(f"<th>{v}</th>" for v in vargas) + "</tr>")
    for pname in PLANET_ORDER:
        row = "".join(f"<td>{_esc((SIGNS_NE if ne else SIGNS_EN)[charts[v][pname]])}</td>" for v in vargas)
        body.append(f"<tr><td>{_esc(pname)}</td>{row}</tr>")
    body.append("</table>")

    # ------------------------------------------------------- planetary positions
    h2("positions", "Planetary Positions", "ग्रहहरूको स्थिति")
    body.append(f"<table><tr><th>{T('Planet', 'ग्रह')}</th><th>{T('Sign', 'राशि')}</th><th>{T('Degree', 'अंश')}</th>"
                f"<th>{T('Nakshatra', 'नक्षत्र')}</th><th>{T('Pada', 'पद')}</th><th>{T('House', 'भाव')}</th>"
                f"<th>{T('Dignity', 'गरिमा')}</th><th>{T('State', 'अवस्था')}</th></tr>")
    for p in bundle["planets"]:
        state = []
        if p["retrograde"] and p["planet"] not in ("Rahu", "Ketu"):
            state.append("R")
        if p["combust"]:
            state.append(T("Combust", "अस्त"))
        body.append(
            f"<tr><td>{_esc(p['planet'])}</td><td>{_esc(p['sign_ne'] if ne else p['sign_en'])}</td>"
            f"<td>{p['degree_in_sign']:.2f}°</td><td>{_esc(p['nakshatra_ne'] if ne else p['nakshatra_en'])}</td>"
            f"<td>{p['pada']}</td><td>{p['house']}</td><td>{_esc(p['dignity'])}</td>"
            f"<td>{_esc(', '.join(state))}</td></tr>"
        )
    body.append("</table>")
    karakas = bundle.get("karakas") or {}
    if karakas:
        body.append("<p class='small'>" + T("Jaimini Chara Karakas: ", "जैमिनी चर कारकहरू: ")
                    + _esc(", ".join(f"{k} — {v}" for k, v in karakas.items())) + "</p>")

    # ---------------------------------------------------------------- strength
    h2("strength", "Planetary Strength — Shadbala, Bhava Bala, Vimshopaka",
       "ग्रह बल — षड्बल, भाव बल, विंशोपक")
    strength = bundle.get("strength", {})
    sb = strength.get("shadbala", {})
    if sb:
        body.append("<table><tr><th>Planet</th><th>Sthana</th><th>Dig</th><th>Kala</th><th>Cheshta</th>"
                    "<th>Naisargika</th><th>Drik</th><th>Total</th><th>Rupas</th><th>Min</th><th>Ratio</th>"
                    "<th>Rank</th><th>Ishta</th><th>Kashta</th></tr>")
        for pname in PLANET_ORDER[:7]:
            r = sb["planets"][pname]
            body.append(
                f"<tr><td>{pname}</td><td>{r['sthana']['total']:.1f}</td><td>{r['dig']:.1f}</td>"
                f"<td>{r['kala']['total']:.1f}</td><td>{r['cheshta']:.1f}</td><td>{r['naisargika']:.1f}</td>"
                f"<td>{r['drik']:.1f}</td><td>{r['total_virupas']:.1f}</td><td><b>{r['rupas']:.2f}</b></td>"
                f"<td>{r['min_rupas']:.1f}</td><td>{r['ratio']:.2f}</td><td>{r['rank']}</td>"
                f"<td>{r['ishta']:.1f}</td><td>{r['kashta']:.1f}</td></tr>"
            )
        body.append("</table>")
        bb = strength.get("bhava_bala", [])
        if bb:
            body.append(f"<h3>{T('Bhava Bala (rupas)', 'भाव बल (रूपा)')}</h3><table><tr>"
                        + "".join(f"<th>{h}</th>" for h in range(1, 13)) + "</tr><tr>"
                        + "".join(f"<td>{row['total_rupas']:.2f}</td>" for row in bb) + "</tr></table>")
        vs = strength.get("vimshopaka", {})
        if vs:
            body.append(f"<h3>{T('Vimshopaka Bala (of 20, Shodashavarga)', 'विंशोपक बल (२० मा, षोडशवर्ग)')}</h3><p>"
                        + _esc("; ".join(f"{p}: {vs[p]['shodashavarga']:.1f}" for p in PLANET_ORDER[:7])) + "</p>")

    # ------------------------------------------------------------ ashtakavarga
    h2("av", "Ashtakavarga — Bindu Strength", "अष्टकवर्ग — बिन्दु बल")
    av = bundle.get("ashtakavarga") or {}
    if av:
        body.append("<table><tr><th></th>" + "".join(
            f"<th>{_esc((SIGNS_NE if ne else SIGNS_EN)[s][:4])}</th>" for s in range(12)) + "<th>Total</th></tr>")
        for pname in PLANET_ORDER[:7] + ["Sarvashtakavarga"]:
            row = av[pname]
            body.append(f"<tr><td>{_esc(pname)}</td>" + "".join(f"<td>{v}</td>" for v in row)
                        + f"<td>{sum(row)}</td></tr>")
        body.append("</table>")
        body.append(paras(deep.get("ashtakavarga_reading")))

    # ------------------------------------------------------------ world-class layer
    chalit = bundle.get("bhava_chalit") or {}
    if chalit.get("houses"):
        h2("chalit", "Bhava Chalit — Houses by Actual Cusps", "भाव चलित — वास्तविक भावसीमाबाट घरहरू")
        body.append(f"<p>{T('Sripathi method: each house is centred on its Placidus cusp. Planets marked shifted sit in a different Chalit house than their Rashi house.', 'श्रीपति विधि: प्रत्येक भाव आफ्नो प्लेसिडस कस्पमा केन्द्रित हुन्छ। सरेको चिन्ह लागेका ग्रह राशि घरभन्दा फरक चलित घरमा छन्।')}</p>")
        body.append("<table><tr><th>" + T("Planet", "ग्रह") + "</th><th>" + T("Sign", "राशि") + "</th><th>" + T("Rashi house", "राशि भाव") + "</th><th>" + T("Chalit house", "चलित भाव") + "</th><th>" + T("Shifted?", "सरेको?") + "</th></tr>")
        for p in bundle["planets"]:
            row = chalit["houses"].get(p["planet"]) or {}
            body.append(f"<tr><td>{_esc(p['planet'])}</td><td>{_esc(p['sign_ne'] if ne else p['sign_en'])}</td>"
                        f"<td>{row.get('rashi_house', '')}</td><td>{row.get('chalit_house', '')}</td>"
                        f"<td>{T('Yes', 'हो') if row.get('shifted') else T('No', 'होइन')}</td></tr>")
        body.append("</table>")
    prastara = bundle.get("prastara") or {}
    if prastara:
        h2("prastara", "Prastara Ashtakavarga — Reduced Totals", "प्रस्तार अष्टकवर्ग — घटाइएको जम्मा")
        body.append(f"<p>{T('Reduced totals after Trikona then Ekadhipatya Shodhana (BPHS). The full 8×12 grids are on the website.', 'त्रिकोण अनि एकाधिपत्य शोधन (BPHS) पछिको घटाइएको जम्मा। पूरा ८×१२ तालिकाहरू वेबसाइटमा छन्।')}</p>")
        body.append("<table><tr><th>" + T("Planet", "ग्रह") + "</th><th>" + T("Reduced total", "घटाइएको जम्मा") + "</th></tr>")
        for pname in PLANET_ORDER[:7]:
            entry = prastara.get(pname) or {}
            body.append(f"<tr><td>{_esc(pname)}</td><td>{entry.get('reduced_total', '')}</td></tr>")
        body.append("</table>")
    kp_events = bundle.get("kp_events") or {}
    if kp_events:
        h2("kp-events", "KP Event Analysis — Promise, Dasha, Transit", "KP घटना विश्लेषण — प्रतिज्ञा, दशा, गोचर")
        body.append(f"<p>{T('Cuspal sub lord promise, checked against the running dasha and current Jupiter/Saturn transits. Guidance, not a guarantee.', 'कस्पल उपस्वामीको प्रतिज्ञा, चालु दशा र वर्तमान बृहस्पति/शनि गोचरसँग जाँचिएको। मार्गदर्शन हो, ग्यारेन्टी होइन।')}</p>")
        body.append("<table><tr><th>" + T("Event", "घटना") + "</th><th>" + T("Verdict", "निष्कर्ष") + "</th><th>" + T("Basis", "आधार") + "</th></tr>")
        for ev in kp_events.values():
            body.append(f"<tr><td>{_esc(ev['event_ne'] if ne else ev['event_en'])}</td>"
                        f"<td>{_esc(ev['verdict_ne'] if ne else ev['verdict'])}</td>"
                        f"<td>{pick(ev['summary'])}</td></tr>")
        body.append("</table>")
    sudar = bundle.get("sudarshana") or {}
    if sudar.get("confirmed") is not None:
        h2("sudarshana", "Sudarshana Chakra — Confirmed Results", "सुदर्शन चक्र — पुष्टि भएका फलहरू")
        body.append(f"<p>{T('The same chart read from Lagna, Moon and Sun. A planet in the same relative house in two or three rings has its results confirmed.', 'उही कुण्डली लग्न, चन्द्र र सूर्यबाट पढिन्छ। दुई वा तीन घेरामा एउटै सापेक्ष भावमा रहेको ग्रहको फल पुष्टि हुन्छ।')}</p>")
        if sudar["confirmed"]:
            body.append("<ul>" + "".join(
                f"<li>{_esc(c['planet'])}: {T('house', 'भाव')} {c['house']} ({_esc(c['level'])})</li>"
                for c in sudar["confirmed"]) + "</ul>")
        else:
            body.append(f"<p>{T('No planet repeats a relative house across rings in this chart.', 'यस कुण्डलीमा कुनै ग्रहले घेराहरूमा सापेक्ष भाव दोहोर्याएको छैन।')}</p>")

    # ------------------------------------------------------------ planet chapters
    h2("planets", "The Planets — Chapter by Chapter", "ग्रहहरू — अध्यायगत विश्लेषण")
    for pname in PLANET_ORDER:
        body.append(f"<h3>{_esc(pname)}</h3>")
        body.append(paras((deep.get("planet_chapters") or {}).get(pname)))

    # ------------------------------------------------------------- house chapters
    h2("houses", "The Twelve Houses", "बाह्र भावहरू")
    for row in deep.get("house_chapters") or []:
        title = T(f"House {row['house']} — {(SIGNS_NE if ne else SIGNS_EN)[row['sign']]}",
                  f"भाव {row['house']} — {SIGNS_NE[row['sign']]}")
        body.append(f"<h3>{_esc(title)}</h3>")
        body.append(paras(row["facts"]))

    # ------------------------------------------------------------- special lagnas
    h2("special", "Special Lagnas — Arudha & Upapada", "विशेष लग्नहरू — आरूढ र उपपद")
    sl = bundle.get("special_lagnas") or {}
    if sl:
        al, ul = sl["arudha_lagna"], sl["upapada"]
        body.append(
            f"<p>{T('Arudha Lagna', 'आरूढ लग्न')}: <b>{_esc(al['sign_ne'] if ne else al['sign_en'])}</b> "
            f"({T('house', 'भाव')} {al['house_from_lagna']}) · "
            f"{T('Upapada Lagna', 'उपपद लग्न')}: <b>{_esc(ul['sign_ne'] if ne else ul['sign_en'])}</b> "
            f"({T('house', 'भाव')} {ul['house_from_lagna']}) · "
            f"{T('Chandra Lagna', 'चन्द्र लग्न')}: <b>{_esc(sl['chandra_lagna']['sign_ne'] if ne else sl['chandra_lagna']['sign_en'])}</b></p>"
        )
    sr = deep.get("special_readings") or {}
    body.append(f"<h3>{T('Arudha Lagna — the public image', 'आरूढ लग्न — सार्वजनिक छवि')}</h3>")
    body.append(paras(sr.get("arudha")))
    body.append(f"<h3>{T('Upapada Lagna — marriage', 'उपपद लग्न — विवाह')}</h3>")
    body.append(paras(sr.get("upapada")))

    # ------------------------------------------------------------------- dashas
    h2("dashas", "Dasha Chapters — Vimshottari Deep-Dive", "दशा अध्यायहरू — विंशोत्तरी गहन विश्लेषण")
    mds = (bundle.get("dasha") or {}).get("mahadashas") or []
    if mds:
        body.append(f"<h3 class='no-break'>{T('Vimshottari Mahadashas', 'विंशोत्तरी महादशाहरू')}</h3>")
        body.append("<table><tr><th>" + T("Mahadasha", "महादशा") + "</th><th>" + T("Start date", "सुरु मिति")
                    + "</th><th>" + T("End date", "अन्त्य मिति") + "</th></tr>")
        for md in mds:
            body.append(f"<tr><td>{_esc(md['lord'])}</td><td>{_esc(md['start'])}</td><td>{_esc(md['end'])}</td></tr>")
        body.append("</table>")
    cur = bundle["dasha"].get("current") or {}
    md0, ad0 = cur.get("mahadasha") or {}, cur.get("antardasha") or {}
    if md0:
        body.append(f"<p><b>{T('Current period', 'हालको अवधि')}:</b> {_esc(md0.get('lord', ''))} "
                    f"{T('Mahadasha', 'महादशा')} ({_esc(md0.get('start', ''))} → {_esc(md0.get('end', ''))}) · "
                    f"{_esc(ad0.get('lord', ''))} {T('Antardasha', 'अन्तर्दशा')} ({T('until', 'सम्म')} {_esc(ad0.get('end', ''))})</p>")
    for e in deep.get("dasha_deep_dive") or []:
        body.append(f"<h3>{_esc(e['lord'])} {T('Mahadasha', 'महादशा')} ({_esc(e['start'])} → {_esc(e['end'])})</h3>")
        body.append(paras(e["summary"]))
        for ad in e.get("antardashas", []):
            body.append(f"<p><b>{_esc(ad['lord'])} {T('Antardasha', 'अन्तर्दशा')} "
                        f"({_esc(ad['start'])} → {_esc(ad['end'])})</b></p>")
            body.append(paras(ad["summary"]))
    # Chara dasha
    cd = bundle.get("chara_dasha") or {}
    if cd.get("periods"):
        body.append(f"<h3>{T('Jaimini Chara Dasha (K. N. Rao)', 'जैमिनी चर दशा (के. एन. राव)')}</h3>")
        body.append("<table><tr><th>" + T("Sign", "राशि") + "</th><th>" + T("Lord", "स्वामी") + "</th><th>"
                    + T("From", "देखि") + "</th><th>" + T("To", "सम्म") + "</th><th>" + T("Years", "वर्ष") + "</th></tr>")
        for p in cd["periods"][:12]:
            body.append(f"<tr><td>{_esc(p['sign_ne'] if ne else p['sign_en'])}</td><td>{_esc(p['lord'])}</td>"
                        f"<td>{_esc(p['start'])}</td><td>{_esc(p['end'])}</td><td>{p['years']}</td></tr>")
        body.append("</table>")
        if cd.get("current"):
            c = cd["current"]
            body.append(f"<p>{T('Current Chara period', 'हालको चर अवधि')}: <b>{_esc(c['sign_ne'] if ne else c['sign_en'])}</b> "
                        f"({_esc(c['start'])} → {_esc(c['end'])})</p>")
    yg, tb = bundle.get("yogini") or {}, bundle.get("tribhagi") or {}
    if yg.get("current"):
        body.append(f"<p>{T('Yogini Dasha now', 'हालको योगिनी दशा')}: {_esc(yg['current']['name'])} "
                    f"({_esc(yg['current']['planet'])}) · {_esc(yg['current']['start'])} → {_esc(yg['current']['end'])}</p>")
    if tb.get("current"):
        body.append(f"<p>{T('Tribhagi Dasha now', 'हालको त्रिभागी दशा')}: {_esc(tb['current']['lord'])} · "
                    f"{_esc(tb['current']['start'])} → {_esc(tb['current']['end'])}</p>")
    # Ashtottari dasha (108-year conditional system, Ketu excluded).
    ash = bundle.get("ashtottari") or {}
    if ash.get("current"):
        body.append(f"<h3>{T('Ashtottari Dasha — 108-year cycle', 'अष्टोत्तरी दशा — १०८-वर्षीय चक्र')}</h3>")
        ac = ash["current"]
        body.append(f"<p>{T('Current', 'हाल')}: {_esc(ac['mahadasha']['lord'])} {T('Mahadasha', 'महादशा')} "
                    f"({_esc(ac['mahadasha']['start'])} → {_esc(ac['mahadasha']['end'])})"
                    f"{(' · ' + _esc(ac['antardasha']['lord']) + ' ' + T('Antardasha', 'अन्तर्दशा')) if ac.get('antardasha') else ''}</p>")
        ap = bundle.get("ashtottari_applicability") or {}
        if ap:
            body.append(f"<p>{T('Applies traditionally', 'परम्परागत रूपमा लागू हुन्छ')}: "
                        f"{T('yes', 'हो') if ap.get('applies') else T('no', 'होइन')} · "
                        f"{T('Rahu condition', 'राहु शर्त')}: {T('met', 'पूरा') if ap.get('rahu_condition') else T('not met', 'पूरा छैन')} · "
                        f"{T('Day-night/paksha condition', 'दिन-रात/पक्ष शर्त')}: "
                        f"{T('met', 'पूरा') if ap.get('day_night_paksha_condition') else T('not met', 'पूरा छैन')}</p>")
        body.append("<table><tr><th>" + T("Lord", "स्वामी") + "</th><th>" + T("From", "देखि") + "</th><th>"
                    + T("To", "सम्म") + "</th><th>" + T("Years", "वर्ष") + "</th></tr>")
        for m in ash["mahadashas"]:
            body.append(f"<tr><td>{_esc(m['lord'])}</td><td>{_esc(m.get('display_start') or m['start'])}</td>"
                        f"<td>{_esc(m['end'])}</td><td>{m['years']}</td></tr>")
        body.append("</table>")
    # Vimshottari depth: Sookshma + Prana of the running period.
    cur_full = bundle["dasha"].get("current") or {}
    if cur_full.get("sookshma"):
        sk, pr = cur_full["sookshma"], cur_full.get("prana")
        body.append(f"<p>{T('Sookshma', 'सूक्ष्म')}: {_esc(sk['lord'])} ({_esc(sk['start'])} → {_esc(sk['end'])})"
                    f"{(' · ' + T('Prana', 'प्राण') + ': ' + _esc(pr['lord']) + ' (' + _esc(pr['start']) + ' → ' + _esc(pr['end']) + ')') if pr else ''}</p>")

    # --------------------------------------------------------------- divisional
    h2("vargas", "Divisional Charts — the Vargas Speak", "वर्ग कुण्डलीहरू — वर्गहरूको विश्लेषण")
    for varga in ("D9", "D10", "D7", "D4", "D12", "D24", "D20"):
        ch = (deep.get("divisional_chapters") or {}).get(varga)
        if not ch:
            continue
        body.append(f"<h3>{pick(ch['title'])}</h3>")
        body.append(paras(ch["facts"]))

    # ------------------------------------------------------------- yogas + doshas
    h2("yogas", "Yogas in this Chart", "यस कुण्डलीका योगहरू")
    yogas = bundle.get("yogas") or []
    if yogas:
        for y in yogas:
            body.append(f"<p><b>{_esc(y['name'])}</b> — {_esc(y['basis'])}</p>")
    else:
        body.append(f"<p>{T('No major named yogas fire in this chart.', 'यस कुण्डलीमा प्रमुख नामित योगहरू छैनन्।')}</p>")
    body.append(f"<h3>{T('Predictions Digest', 'भविष्यवाणी सारांश')}</h3>")
    for key, facts in bundle.get("predictions", {}).items():
        if not facts or key == "current_period":
            continue
        title = PREDICTION_TITLES.get(key, (key.title(), key))[1 if ne else 0]
        body.append(f"<h3>{_esc(title)}</h3>")
        body.append(paras(facts))
    for key, facts in report.get("chapters", {}).items():
        title_pair = CHAPTER_TITLES.get(key, (key.title(), key))
        body.append(f"<h3>{_esc(title_pair[1] if ne else title_pair[0])}</h3>")
        body.append(paras(facts))

    # ------------------------------------------------- argala + nakshatra deep-dive
    arg = bundle.get("argala") or {}
    if arg.get("by_house"):
        h2("argala", "Jaimini Argala — Planetary Intervention", "जैमिनी अर्गला — ग्रह हस्तक्षेप")
        body.append("<table><tr><th>" + T("House", "भाव") + "</th><th>" + T("Argala", "अर्गला") + "</th><th>"
                    + T("Virodhargala", "विरोधर्गला") + "</th><th>" + T("Verdict", "निष्कर्ष") + "</th></tr>")
        for row in arg["by_house"]:
            body.append(f"<tr><td>{row['house']}</td>"
                        f"<td>{_esc(', '.join(a['planet'] for a in row['argala']) or '—')}</td>"
                        f"<td>{_esc(', '.join(v['planet'] for v in row['virodhargala']) or '—')}</td>"
                        f"<td>{_esc(row['verdict'])}</td></tr>")
        body.append("</table>")
        body.append(f"<p>{pick(arg['method_note'])}</p>")
    nd = bundle.get("nakshatra_deep") or {}
    if nd:
        h2("nakshatra", "Nakshatra Deep-Dive — Tara, Chandra Bala, Avasthas",
           "नक्षत्र गहन अध्ययन — तारा, चन्द्रबल, अवस्था")
        nt = nd.get("nava_tara") or {}
        if nt:
            body.append(f"<p>{T('Birth nakshatra', 'जन्म नक्षत्र')}: "
                        f"{_esc(nt.get('natal_nakshatra_ne') if ne else nt.get('natal_nakshatra_en', ''))} · "
                        f"{T('Caution stars', 'सावधानीका तारा')}: {_esc(', '.join(nt.get('caution_stars', [])))}</p>")
        tb = nd.get("tarabala_today") or {}
        cb = nd.get("chandrabala_today") or {}
        if tb:
            body.append(f"<p>{T('Today\'s Tarabala', 'आजको ताराबल')}: {tb['tara']} "
                        f"{_esc(tb['tara_ne'] if ne else tb['tara_en'])} ({_esc(tb['verdict'])})</p>")
        if cb:
            body.append(f"<p>{T('Today\'s Chandra Bala', 'आजको चन्द्रबल')}: {cb['position']} ({_esc(cb['verdict'])})</p>")
        avs = (nd.get("avasthas") or {}).get("planets", [])
        if avs:
            body.append("<table><tr><th>" + T("Planet", "ग्रह") + "</th><th>" + T("Sign", "राशि") + "</th><th>"
                        + T("Balaadi", "बालादि") + "</th><th>" + T("Jagratadi", "जाग्रतादि") + "</th></tr>")
            for r in avs:
                body.append(f"<tr><td>{_esc(r['planet'])}</td><td>{_esc(r['sign_ne'] if ne else r['sign_en'])}</td>"
                            f"<td>{_esc(r['balaadi'])} ({int(r['balaadi_strength'] * 100)}%)</td>"
                            f"<td>{_esc(r['jagratadi'])}</td></tr>")
            body.append("</table>")

    h2("remedies", "Doshas & Remedies", "दोष र उपायहरू")
    doshas = bundle.get("doshas") or {}
    dosha_lines = []
    if doshas:
        m = doshas["manglik"]
        dosha_lines.append(f"Manglik: {T('present', 'छ') if m['present'] else T('absent', 'छैन')} ({_esc(m['strength'])})")
        ks = doshas["kaal_sarp"]
        dosha_lines.append(f"Kaal Sarp: {(_esc(ks['type']) + ' ' + T('type', 'प्रकार')) if ks['present'] else T('absent', 'छैन')}")
        ssx = doshas["sade_sati"]
        dosha_lines.append(f"Sade Sati: {T('active', 'सक्रिय') + ' — ' + _esc(ssx['phase']) if ssx['active'] else T('not active', 'सक्रिय छैन')}")
        pt = doshas["pitra"]
        dosha_lines.append(f"Pitra Dosha: {T('indicated', 'देखिएको') if pt['present'] else T('absent', 'छैन')}")
    body.append("<p>" + _esc(" · ".join(dosha_lines)) + "</p>")
    rems = report.get("remedies", {})
    for g in rems.get("gemstones", []):
        body.append(
            f"<p><strong>{pick(g['role'])}:</strong> {pick(g['stone'])} in {pick(g['metal'])}, "
            f"{pick(g['finger'])}, worn on {pick(g['day'])}, weight {_esc(g['weight'])}.</p>"
        )
    for w in rems.get("weak_planet_support", []):
        body.append(f"<h3>{T('Weak-planet support', 'कमजोर ग्रहको साथ')} — {_esc(w['planet'])}</h3>")
        body.append(f"<p>{pick(w['note'])}</p>")
        body.append(f"<p>{T('Rudraksha', 'रुद्राक्ष')}: {pick(w['rudraksha'])} · "
                    f"{T('Mantra', 'मन्त्र')}: {_esc(w['mantra_ne'])} ({_esc(w['mantra_transliteration'])})</p>")
    rud = rems.get("rudraksha", {})
    if rud:
        body.append(f"<p><strong>Rudraksha:</strong> {pick(rud['recommendation'])} — {pick(rud['reason'])}</p>")
    man = rems.get("mantra", {})
    if man:
        body.append(f"<p><strong>Mantra ({_esc(man['for_planet'])}):</strong> {_esc(man['beej_ne'])} "
                    f"({_esc(man['transliteration'])}). {pick(man['instruction'])}</p>")
    for dr in rems.get("dosha_remedies", []):
        body.append(f"<h3>{pick(dr['dosha'])}</h3>")
        for item in dr["items"]:
            body.append(f"<p>• {pick(item)}</p>")
    # Full gemstone + Rudraksha guide (all nine planets).
    gem = report.get("gemstones", {})
    if gem.get("planets"):
        body.append(f"<h3>{T('Gemstone & Rudraksha Guide', 'रत्न र रुद्राक्ष मार्गदर्शन')}</h3>")
        body.append("<table><tr><th>" + T("Planet", "ग्रह") + "</th><th>" + T("Stone", "रत्न") + "</th><th>"
                    + T("Weight", "तौल") + "</th><th>" + T("Metal / Finger / Day", "धातु / औंला / बार")
                    + "</th><th>" + T("Rudraksha", "रुद्राक्ष") + "</th></tr>")
        for g in gem["planets"]:
            body.append(f"<tr><td>{_esc(g['planet'])}</td><td>{pick(g['stone'])}</td>"
                        f"<td>{_esc(g['weight_ratti'])} ({_esc(g['weight_carat_approx'])})</td>"
                        f"<td>{pick(g['metal'])} / {pick(g['finger'])} / {pick(g['day'])}</td>"
                        f"<td>{pick(g['rudraksha']['name'])}</td></tr>")
        body.append("</table>")
        for g in gem["planets"]:
            if g.get("caution"):
                body.append(f"<p><strong>{_esc(g['planet'])}:</strong> {pick(g['caution'])}</p>")

    # ---------------------------------------------------------------- lal kitab
    lk = bundle.get("lal_kitab", {})
    if lk:
        h2("lalkitab", "Lal Kitab", "लाल किताब")
        khana_bits = []
        for k in range(1, 13):
            occ = ", ".join(lk["chart"].get(str(k), []))
            if occ:
                khana_bits.append(f"Khana {k}: {occ}")
        body.append(f"<p>{_esc('; '.join(khana_bits))}</p>")
        for r in lk.get("rin", []):
            if r["detected"] is True:
                body.append(f"<p><strong>{pick(r['name'])}:</strong> {pick(r['remedy'])}</p>")
        teva = lk.get("teva") or {}
        for m in teva.get("matched", []):
            body.append(f"<p><strong>{_esc(m['type_ne'] if ne else m['type'])}:</strong> "
                        f"{_esc(m['formation'])} — {pick(m['reading'])} {pick(m['remedy'])}</p>")
        if teva.get("variance_note"):
            body.append(f"<p class='small'>{pick(teva['variance_note'])}</p>")
        lkd = bundle.get("lal_kitab_dasha") or {}
        if lkd.get("current"):
            c = lkd["current"]
            body.append(f"<h3>{T('Lal Kitab Dasha — 35-year cycle', 'लाल किताब दशा — ३५-वर्षीय चक्र')}</h3>")
            body.append(f"<p>{T('Current', 'हाल')}: {_esc(c['planet'])} ({_esc(c['start'])} → {_esc(c['end'])})"
                        f"{(' · ' + _esc(c['antardasha']['planet']) + ' ' + T('Antardasha', 'अन्तर्दशा')) if c.get('antardasha') else ''}</p>")
            body.append(f"<p class='small'>{pick(lkd['method_note'])}</p>")

    # ------------------------------------------------- transits & timing synthesis
    h2("transits", "Transits, Sade Sati & Timing Synthesis", "गोचर, साढेसाती र समय संश्लेषण")
    tp = deep.get("transit_phala") or {}
    for pname in ("Saturn", "Jupiter", "Rahu", "Ketu", "Mars", "Sun"):
        facts = (tp.get("planets") or {}).get(pname)
        if facts:
            body.append(f"<h3>{_esc(pname)}</h3>")
            body.append(paras(facts))
    if tp.get("sade_sati_detail"):
        body.append(f"<h3>{T('Sade Sati — exact span', 'साढेसाती — यथार्थ अवधि')}</h3>")
        body.append(f"<p>{pick(tp['sade_sati_detail'])}</p>")
    sade_lt = bundle.get("sade_sati_lifetime") or {}
    if sade_lt.get("periods"):
        body.append(f"<h3>{T('Lifetime Sade Sati', 'आजीवन साढेसाती')}</h3>")
        body.append("<table><tr><th>" + T("Status", "स्थिति") + "</th><th>" + T("Rising", "उदय")
                    + "</th><th>" + T("Peak", "चरम") + "</th><th>" + T("Setting", "अस्त")
                    + "</th><th>" + T("Ends", "समाप्ति") + "</th></tr>")
        for p in sade_lt["periods"]:
            body.append(f"<tr><td>{_esc(p['status'])}</td><td>{_esc(p['start'] or '—')}</td>"
                        f"<td>{_esc(p['peak_start'] or '—')}</td><td>{_esc(p['setting_start'] or '—')}</td>"
                        f"<td>{_esc(p['end'])}</td></tr>")
        body.append("</table>")
    ingress = (bundle.get("transits_detail") or {}).get("ingress", [])
    if ingress:
        body.append(f"<h3>{T('Next Ingresses', 'आगामी प्रवेशहरू')}</h3><table><tr><th>{T('Planet', 'ग्रह')}</th>"
                    f"<th>{T('Now', 'हाल')}</th><th>{T('Next ingress', 'अर्को प्रवेश')}</th></tr>")
        for r in ingress:
            body.append(f"<tr><td>{_esc(r['planet'])}</td><td>{_esc(r['current_sign_ne'] if ne else r['current_sign_en'])}</td>"
                        f"<td>{_esc(r['next_ingress_date'])} → {_esc(r['next_sign_ne'] if ne else r['next_sign_en'])}</td></tr>")
        body.append("</table>")
    body.append(f"<h3>{T('Timing Synthesis — two clocks, one chart', 'समय संश्लेषण — दुई घडी, एउटै कुण्डली')}</h3>")
    body.append(paras(deep.get("timing_synthesis")))

    # ------------------------------------------------------------------ forecast
    h2("forecast", "Year-by-Year Forecast", "वर्षगत भविष्यफल")
    for row in report.get("favourable_periods", []):
        body.append(f"<p><strong>{row['year']} — {_esc(row['mahadasha'])} / {_esc(row.get('antardasha') or '')}"
                    f"{(' · ' + T('Chara', 'चर') + ': ' + _esc(row['chara_sign'])) if row.get('chara_sign') else ''}:</strong> "
                    f"{pick(row['summary'])}</p>")
    body.append(f"<h3>{T('Varshphal (Annual Charts)', 'वर्षफल (वार्षिक कुण्डली)')}</h3>")
    for v in report.get("varshphal", []):
        body.append(
            f"<p><strong>{v['year']}:</strong> {T('Annual Lagna', 'वार्षिक लग्न')} "
            f"{_esc(v['varsha_lagna']['sign_ne'] if ne else v['varsha_lagna']['sign_en'])}, "
            f"Muntha {v['muntha']['house']}, {T('year lord', 'वर्ष स्वामी')} {_esc(v['year_lord'])}. {pick(v['reading'])}</p>"
        )
        if v.get("panchadhikari"):
            pc = v["panchadhikari"]
            tj = v.get("tajika") or {}
            body.append(
                f"<p>{T('Panchadhikari Year Lord', 'पञ्चाधिकारी वर्ष स्वामी')}: {_esc(pc['year_lord'])} · "
                f"{T('Tajika yogas', 'ताजिक योगहरू')}: {tj.get('favourable_count', 0)} "
                f"{T('favourable', 'शुभ')} / {tj.get('unfavourable_count', 0)} {T('unfavourable', 'अशुभ')} · "
                + "; ".join(f"{k}: {_esc(s['sign_ne'] if ne else s['sign_en'])} ({_esc(s['strength'])})"
                            for k, s in (v.get("sahams") or {}).items())
                + "</p>"
            )
            for pr in tj.get("pairs", []):
                body.append(f"<p>• {_esc(pr['yoga'])}: {', '.join(pr['planets'])} — {pick(pr['reading'])}</p>")
    ya = report.get("year_ahead", [])
    if ya:
        body.append(f"<h3>{T('Year Ahead — by Moon Sign', 'वर्ष अगाडि — चन्द्र राशिअनुसार')}</h3>")
        body.append(paras(ya))

    # ------------------------------------------------------------- lucky & numbers
    h2("lucky", "Lucky Attributes, Numerology & Name Letter", "भाग्य तत्त्व, अङ्कशास्त्र र नामको अक्षर")
    lucky = report.get("lucky", {})
    if lucky:
        body.append(
            f"<p>{T('Number', 'अङ्क')}: {pick(lucky['number'])} · {T('Colour', 'रङ')}: {pick(lucky['colour'])} · "
            f"{T('Day', 'बार')}: {pick(lucky['day'])} · {T('Deity', 'इष्ट देवता')}: {pick(lucky['deity'])}</p>"
        )
    num = bundle.get("numerology", {})
    nl = bundle.get("name_letters", {})
    if num:
        body.append(
            f"<p>Moolank {num['moolank']['value']} ({num['moolank']['ruler']}): {pick(num['moolank']['trait'])}<br>"
            f"Bhagyank {num['bhagyank']['value']} ({num['bhagyank']['ruler']}): {pick(num['bhagyank']['trait'])}<br>"
            f"{T('Name letter', 'नामको अक्षर')}: {_esc(nl.get('syllable_en', ''))} / {_esc(nl.get('syllable_ne', ''))}</p>"
        )

    # --------------------------------- Phase 3: Classical Dashas
    h2("classical-dashas", "Classical Dashas — Narayana, Shodshottari, Mudda, Kalachakra",
       "शास्त्रीय दशाहरू — नारायण, षोडशोत्तरी, मुद्दा, कालचक्र")
    nar = bundle.get("narayana")
    if nar and nar.get("current"):
        cur = nar["current"]["mahadasha"]
        body.append(f"<p><b>Narayana (Jaimini):</b> {T('Now', 'अहिले')}: "
                    f"{_esc(cur.get('sign_en', ''))} ({cur.get('start', '')} – {cur.get('end', '')})</p>")
    sho = bundle.get("shodshottari")
    if sho and sho.get("current"):
        cur = sho["current"]["mahadasha"]
        body.append(f"<p><b>Shodshottari (116-yr):</b> {T('Now', 'अहिले')}: "
                    f"{_esc(cur.get('lord', ''))} ({cur.get('start', '')} – {cur.get('end', '')})</p>")
    mud = bundle.get("mudda")
    if mud and mud.get("current"):
        cur = mud["current"]
        body.append(f"<p><b>Mudda (Tajika annual):</b> {T('Now', 'अहिले')}: "
                    f"{_esc(cur.get('mahadasha', ''))} / {_esc(cur.get('antardasha', ''))}</p>")
    kc = bundle.get("kalachakra")
    if kc and kc.get("current"):
        cur = kc["current"]["mahadasha"]
        body.append(f"<p><b>Kalachakra:</b> {T('Now', 'अहिले')}: "
                    f"{_esc(cur.get('sign_en', ''))} ({cur.get('start', '')} – {cur.get('end', '')}) · "
                    f"{T('Deha', 'देह')}: {_esc(kc.get('deha_en', ''))} · "
                    f"{T('Jiva', 'जीव')}: {_esc(kc.get('jiva_en', ''))}</p>")

    # --------------------------------- Phase 4: Classical Utilities
    h2("classical-utils", "Classical Utilities — Sarvatobhadra, Pravesh, Ishta Devta",
       "शास्त्रीय उपकरणहरू — सर्वतोभद्र, प्रवेश, इष्ट देवता")
    sbc = bundle.get("sarvatobhadra")
    if sbc:
        body.append(f"<p><b>Sarvatobhadra:</b> {T('Janma nakshatra', 'जन्म नक्षत्र')}: "
                    f"{_esc(sbc['natal_points']['janma_nakshatra_28'])} · "
                    f"{T('Tithi group', 'तिथि समूह')}: {_esc(sbc['natal_points']['tithi_group'])}</p>")
        for key, vals in sbc.get("summary", {}).items():
            ben = ", ".join(vals.get("benefic", [])) or "—"
            mal = ", ".join(vals.get("malefic", [])) or "—"
            body.append(f"<p>{_esc(key)}: ✓ {ben} · ✗ {mal}</p>")
    ishta = bundle.get("ishta_devta")
    if ishta:
        body.append(f"<p><b>{T('Ishta Devta', 'इष्ट देवता')}:</b> "
                    f"{_esc(ishta['deity_en'] if not ne else ishta['deity_ne'])} "
                    f"({T('via', 'मार्फत')} {_esc(ishta['indicator_planet'])})</p>")
    bn = bundle.get("baby_name")
    if bn:
        body.append(f"<p><b>{T('Namakaran syllable', 'नामकरण अक्षर')}:</b> "
                    f"{_esc(bn['syllable'])} ({_esc(bn['nakshatra'])} {_esc(str(bn['pada']))})</p>")

    # --------------------------------- Phase 5: Predictive Intelligence
    h2("predictive", "Predictive Intelligence — Consensus & Timing",
       "भविष्यवाणी बुद्धिमत्ता — सहमति र समय")
    dc = bundle.get("dasha_consensus")
    if dc and dc.get("highlights"):
        body.append(f"<p><b>{T('High-confidence periods', 'उच्च-विश्वास अवधिहरू')}:</b></p>")
        for hl in dc["highlights"][:6]:
            body.append(f"<p>{_esc(hl['month'])}: {_esc(hl['verdict'])} "
                        f"({hl['consensus']}, {round(hl['agreement']*100)}% {T('agree', 'सहमत')})</p>")
    elif dc is None:
        # Light mode (PDF): consensus skipped for speed; point to the site.
        body.append(f"<p class='small'>{T('Full 60-month dasha consensus timeline is available in the interactive report on the site.', 'पूर्ण ६०-महिने दशा सहमति समयरेखा साइटको इन्टरएक्टिभ रिपोर्टमा उपलब्ध छ।')}</p>")
    yf = bundle.get("yoga_fructification")
    if yf and yf.get("yogas"):
        body.append(f"<p><b>{T('Yoga activations', 'योग सक्रियता')}:</b></p>")
        for y in yf["yogas"][:5]:
            acts = "; ".join(f"{a['start']}–{a['end']}: {a['md']}/{a['ad']}"
                             for a in y["activations"][:2])
            body.append(f"<p>{_esc(y['yoga'])}: {acts}</p>")

    body.append(f"<p class='small'>{T('Generated by Vedic Astro — Swiss Ephemeris (Lahiri ayanamsa), Parashari + KP + Jaimini methods (special lagnas, Chara dasha, Shadbala). Every reading in this report is computed from this chart alone. For guidance and reflection; not a substitute for professional advice.',
                                      'Vedic Astro द्वारा तयार — स्विस एफेमेरिस (लाहिरी अयनांश), पराशरी + KP + जैमिनी विधि (विशेष लग्न, चर दशा, षड्बल)। यस रिपोर्टका हरेक विश्लेषण यही कुण्डलीबाट मात्र गणना गरिएका हुन्। मार्गदर्शन र मननका लागि; व्यावसायिक सल्लाहको विकल्प होइन।')}</p>")

    # ------------------------------------------------------- summary page
    # "Your Janma Kundali — Summary": count cards + one-line excerpts, all
    # computed from this chart (mirrors the traditional report summary page).
    def first_fact(facts, n=2):
        out = []
        for f in facts or []:
            out.append(pick(f))
            if len(out) >= n:
                break
        return out

    sum_cards = []
    yogas_all = bundle.get("yogas") or []
    if yogas_all:
        sum_cards.append((T("Yogas", "योगहरू"), str(len(yogas_all)),
                          [_esc(y["name"]) for y in yogas_all[:3]]))
    doshas_all = bundle.get("doshas") or {}
    dosha_present = []
    if doshas_all:
        if doshas_all.get("manglik", {}).get("present"):
            dosha_present.append(T("Manglik", "मांगलिक"))
        if doshas_all.get("kaal_sarp", {}).get("present"):
            dosha_present.append(T("Kaal Sarp", "कालसर्प"))
        if doshas_all.get("pitra", {}).get("present"):
            dosha_present.append(T("Pitra Dosha", "पितृ दोष"))
        if doshas_all.get("sade_sati", {}).get("active"):
            dosha_present.append(T("Sade Sati (active)", "साढेसाती (सक्रिय)"))
    sum_cards.append((T("Doshas", "दोषहरू"),
                      str(len(dosha_present)) if dosha_present else T("none", "छैन"),
                      dosha_present or [T("No major dosha afflictions detected.", "प्रमुख दोष देखिएन।")]))
    rep_ch = report.get("chapters", {})
    pred = bundle.get("predictions", {})
    for key, title_en, title_ne in (("career", "Career", "पेशा"),
                                    ("marriage", "Marriage", "विवाह"),
                                    ("finance", "Wealth", "धन"),
                                    ("health", "Health", "स्वास्थ्य")):
        facts = rep_ch.get(key) or pred.get(key) or pred.get(
            {"marriage": "relationships", "finance": "wealth"}.get(key, key))
        lines = first_fact(facts, 2)
        if lines:
            sum_cards.append((T(title_en, title_ne), "", lines))
    summary = ["<h2 class='no-break' style='page-break-before:always'>"
               + T("Your Janma Kundali — Summary", "तपाईंको जन्म कुण्डली — सारांश") + "</h2>"
               + "<div class='sum-grid'>"]
    for title, count, lines in sum_cards:
        summary.append(
            f"<div class='sum-card'><h3>{_esc(title)}"
            + (f"<span class='count'>{_esc(count)}</span>" if count else "")
            + "</h3>" + "".join(f"<p>{_esc(l)[:220]}</p>" for l in lines) + "</div>")
    summary.append("</div>")

    # ------------------------------------------------------------- assemble + TOC
    toc = ["<h2 class='no-break' style='page-break-before:always'>"
           + T("Contents", "विषयसूची") + "</h2><div class='toc'>"]
    for anchor, title in sections:
        toc.append(f"<div><a href='#{anchor}'>{_esc(title)}</a></div>")
    toc.append("</div>")
    # Insert TOC + summary right after the cover.
    parts.append("<!--TOC-->")
    parts.append("<!--SUMMARY-->")
    parts.extend(body)
    parts.append("</body></html>")
    html_text = "".join(parts)
    html_text = html_text.replace("<!--TOC-->", "".join(toc), 1)
    return html_text.replace("<!--SUMMARY-->", "".join(summary), 1)


def render_pdf(bundle: dict, lang: str = "en") -> bytes:
    html_text = build_html(bundle, lang)
    try:
        from weasyprint import HTML

        return HTML(string=html_text).write_pdf()
    except Exception:
        return _render_pdf_reportlab(bundle)


def _render_pdf_reportlab(bundle: dict) -> bytes:
    """English-only fallback when WeasyPrint's system libraries are absent."""
    import io

    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, title="Vedic Astrology Report")
    styles = getSampleStyleSheet()
    story = [Paragraph("Vedic Astro — Premium Report", styles["Title"])]
    birth = bundle["birth"]
    story.append(Paragraph(
        f"Born {birth['date']} at {birth['time']} — {birth['place']['name']}", styles["Normal"]))
    story.append(Spacer(1, 10))

    def add_section(title: str, facts):
        if not facts:
            return
        story.append(Paragraph(title, styles["Heading2"]))
        for f in facts:
            text = f.get("en", "") if isinstance(f, dict) else str(f)
            story.append(Paragraph(html.escape(text), styles["BodyText"]))
        story.append(Spacer(1, 6))

    deep = bundle.get("deep_report") or {}
    for pname in PLANET_ORDER:
        add_section(f"Planet — {pname}", (deep.get("planet_chapters") or {}).get(pname))
    for key, facts in bundle.get("predictions", {}).items():
        add_section(PREDICTION_TITLES.get(key, (key.title(),))[0], facts)
    report = bundle.get("report", {})
    for key, facts in report.get("chapters", {}).items():
        add_section(CHAPTER_TITLES.get(key, (key.title(),))[0], facts)
    story.append(Paragraph("Favourable Periods", styles["Heading2"]))
    for row in report.get("favourable_periods", []):
        story.append(Paragraph(
            html.escape(f"{row['year']} — {row['mahadasha']}/{row.get('antardasha') or ''}: {row['summary']['en']}"),
            styles["BodyText"]))
    doc.build(story)
    return buf.getvalue()
