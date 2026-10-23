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
  @bottom-center { content: "Vedic Astro — Premium Kundali Report · " counter(page) " / " counter(pages);
                   font-size: 8pt; color: #8a8578; } }
@page cover { margin: 0; @bottom-center { content: none; } }
body { font-family: 'Noto Sans Devanagari','DejaVu Sans',sans-serif; color:#1c1a2e; font-size:10.5pt; line-height:1.5; }
.cover { page: cover; height: 297mm; background: #141126; color: #f3ead2; text-align: center;
         padding-top: 92mm; box-sizing: border-box; }
.cover h1 { font-size: 30pt; color: #e9c767; margin: 0 6mm 4mm; }
.cover .sub { font-size: 13pt; color: #cfc4a5; margin: 0 10mm; }
.cover .meta { margin-top: 14mm; font-size: 11pt; color: #a99e7f; }
h2 { color:#6b4f12; border-bottom:1.5px solid #c9a227; padding-bottom:1mm; margin-top:7mm;
     font-size:14.5pt; page-break-before: always; }
h2.no-break { page-break-before: auto; }
h3 { color:#3a2f5e; margin-top:4.5mm; font-size:11.5pt; }
table { border-collapse:collapse; width:100%; margin:2.5mm 0; }
th,td { border:0.5pt solid #b9b3d6; padding:1.4mm 1.8mm; text-align:left; font-size:9pt; }
th { background:#efe9fb; }
.meta { color:#555; font-size:9.5pt; }
.toc { font-size:11pt; line-height:1.9; }
.toc a { color:#1c1a2e; text-decoration:none; }
.toc a::after { content: leader('.') target-counter(attr(href), page); }
.chart-row { text-align:center; }
.chart-box { display:inline-block; margin:2mm 3mm; vertical-align:top; }
.chart-title { font-weight:700; color:#6b4f12; margin-bottom:1mm; }
p { margin: 1.6mm 0; text-align: justify; }
.small { font-size: 9pt; color:#555; }
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

    def h2(anchor: str, en: str, nep: str, no_break: bool = False) -> None:
        title = nep if ne else en
        sections.append((anchor, title))
        body.append(f"<h2 id='{anchor}'{' class=\"no-break\"' if no_break else ''}>{_esc(title)}</h2>")

    # ---------------------------------------------------------------- cover
    parts = [
        "<!DOCTYPE html><html><head><meta charset='utf-8'><style>",
        _CSS,
        "</style></head><body>",
        "<div class='cover'>",
        f"<h1>{_esc(name)}</h1>",
        f"<div class='sub'>{T('Premium Kundali Report', 'प्रिमियम कुण्डली रिपोर्ट')}</div>",
        f"<div class='sub'>{T('Parashari · KP · Jaimini — computed with Swiss Ephemeris, Lahiri ayanamsa',
                              'पराशरी · KP · जैमिनी — स्विस एफेमेरिस, लाहिरी अयनांशले गणना गरिएको')}</div>",
        f"<div class='meta'>{_esc(birth['date'])} · {_esc(birth['time'])} · {_esc(place['name'])}<br>"
        f"{T('Lagna', 'लग्न')}: {_esc(lagna['sign_ne'] if ne else lagna['sign_en'])} · "
        f"{T('Moon', 'चन्द्र')}: {_esc(moon['sign_ne'] if ne else moon['sign_en'])} / "
        f"{_esc(moon['nakshatra_ne'] if ne else moon['nakshatra_en'])}</div>",
        "</div>",
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
    body.append(f"<p class='small'>{T('Generated by Vedic Astro — Swiss Ephemeris (Lahiri ayanamsa), Parashari + KP + Jaimini methods (special lagnas, Chara dasha, Shadbala). Every reading in this report is computed from this chart alone. For guidance and reflection; not a substitute for professional advice.',
                                      'Vedic Astro द्वारा तयार — स्विस एफेमेरिस (लाहिरी अयनांश), पराशरी + KP + जैमिनी विधि (विशेष लग्न, चर दशा, षड्बल)। यस रिपोर्टका हरेक विश्लेषण यही कुण्डलीबाट मात्र गणना गरिएका हुन्। मार्गदर्शन र मननका लागि; व्यावसायिक सल्लाहको विकल्प होइन।')}</p>")

    # ------------------------------------------------------------- assemble + TOC
    toc = ["<h2 class='no-break' style='page-break-before:always'>"
           + T("Contents", "विषयसूची") + "</h2><div class='toc'>"]
    for anchor, title in sections:
        toc.append(f"<div><a href='#{anchor}'>{_esc(title)}</a></div>")
    toc.append("</div>")
    # Insert TOC right after the cover.
    parts.append("<!--TOC-->")
    parts.extend(body)
    parts.append("</body></html>")
    html_text = "".join(parts)
    return html_text.replace("<!--TOC-->", "".join(toc), 1)


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
