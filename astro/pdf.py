"""PDF export of the premium report.

Primary renderer: WeasyPrint (HTML/CSS template — handles Devanagari when
a suitable font is present on the system). Fallback: reportlab with an
English-only rendering (its built-in fonts have no Devanagari glyphs).
"""
from __future__ import annotations

import html

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


def _esc(s) -> str:
    return html.escape(str(s))


def build_html(bundle: dict, lang: str = "en") -> str:
    name = bundle.get("name") or "Vedic Astrology Report"
    birth = bundle["birth"]
    place = birth["place"]
    lagna = bundle["lagna"]

    def pick(bi: dict) -> str:
        return _esc(bi.get(lang) or bi.get("en", ""))

    parts = [
        "<!DOCTYPE html><html><head><meta charset='utf-8'>",
        "<style>",
        "@page { size: A4; margin: 20mm 16mm; }",
        "body { font-family: 'Noto Sans Devanagari','DejaVu Sans',sans-serif; color:#1c1a2e; font-size:11pt; line-height:1.55; }",
        "h1 { color:#6b4f12; font-size:22pt; margin-bottom:2mm; }",
        "h2 { color:#6b4f12; border-bottom:1.5px solid #c9a227; padding-bottom:1mm; margin-top:8mm; font-size:14pt; }",
        "h3 { color:#3a2f5e; margin-top:5mm; font-size:12pt; }",
        "table { border-collapse:collapse; width:100%; margin:3mm 0; }",
        "th,td { border:0.5pt solid #b9b3d6; padding:1.6mm 2mm; text-align:left; font-size:9.5pt; }",
        "th { background:#efe9fb; }",
        ".meta { color:#555; }",
        "</style></head><body>",
        f"<h1>{_esc(name)}</h1>",
        f"<p class='meta'>Born {_esc(birth['date'])} at {_esc(birth['time'])} — {_esc(place['name'])}"
        f" ({place['lat']}, {place['lon']}, {_esc(place['tz'])})</p>",
        f"<p class='meta'>Lagna: {_esc(lagna['sign_en'])} · Moon: "
        f"{_esc(bundle['planets'][1]['sign_en'])} / {_esc(bundle['planets'][1]['nakshatra_en'])}</p>",
    ]

    # Planet table
    parts.append("<h2>Planetary Positions</h2><table><tr><th>Planet</th><th>Sign</th><th>Degree</th><th>Nakshatra</th><th>Pada</th><th>House</th><th>Retro</th></tr>")
    for p in bundle["planets"]:
        parts.append(
            f"<tr><td>{_esc(p['planet'])}</td><td>{_esc(p['sign_en'])}</td><td>{p['degree_in_sign']:.2f}</td>"
            f"<td>{_esc(p['nakshatra_en'])}</td><td>{p['pada']}</td><td>{p['house']}</td>"
            f"<td>{'R' if p['retrograde'] else ''}</td></tr>"
        )
    parts.append("</table>")

    # Current dasha
    cur = bundle["dasha"].get("current") or {}
    md = cur.get("mahadasha") or {}
    ad = cur.get("antardasha") or {}
    if md:
        parts.append(
            f"<h2>Current Period</h2><p>{_esc(md.get('lord',''))} Mahadasha ({_esc(md.get('start',''))} → {_esc(md.get('end',''))})"
            f" · {_esc(ad.get('lord',''))} Antardasha (until {_esc(ad.get('end',''))})</p>"
        )

    # Predictions
    parts.append("<h2>Predictions</h2>")
    for key, facts in bundle.get("predictions", {}).items():
        if not facts:
            continue
        title = PREDICTION_TITLES.get(key, (key.title(), key))[0 if lang == "en" else 1]
        parts.append(f"<h3>{_esc(title)}</h3>")
        for f in facts:
            parts.append(f"<p>{pick(f)}</p>")

    # Premium chapters
    report = bundle.get("report", {})
    parts.append("<h2>Premium Life Report</h2>")
    for key, facts in report.get("chapters", {}).items():
        title_pair = CHAPTER_TITLES.get(key, (key.title(), key))
        title = title_pair[0] if lang == "en" else title_pair[1]
        parts.append(f"<h3>{_esc(title)}</h3>")
        for f in facts:
            parts.append(f"<p>{pick(f)}</p>")

    # Favourable periods
    parts.append("<h2>Favourable Periods — 10 Year Outlook</h2>")
    for row in report.get("favourable_periods", []):
        parts.append(f"<p><strong>{row['year']} — {_esc(row['mahadasha'])} / {_esc(row.get('antardasha') or '')}:</strong> {pick(row['summary'])}</p>")

    # Varshphal
    parts.append("<h2>Varshphal (Annual Charts)</h2>")
    for v in report.get("varshphal", []):
        parts.append(
            f"<p><strong>{v['year']}:</strong> Annual Lagna {_esc(v['varsha_lagna']['sign_en'])}, "
            f"Muntha in house {v['muntha']['house']}, year lord {_esc(v['year_lord'])}. {pick(v['reading'])}</p>"
        )

    # Remedies
    rems = report.get("remedies", {})
    parts.append("<h2>Remedies</h2>")
    for g in rems.get("gemstones", []):
        parts.append(
            f"<p><strong>{pick(g['role'])}:</strong> {pick(g['stone'])} in {pick(g['metal'])}, "
            f"{pick(g['finger'])}, worn on {pick(g['day'])}, weight { _esc(g['weight']) }.</p>"
        )
    rud = rems.get("rudraksha", {})
    if rud:
        parts.append(f"<p><strong>Rudraksha:</strong> {pick(rud['recommendation'])} — {pick(rud['reason'])}</p>")
    man = rems.get("mantra", {})
    if man:
        parts.append(f"<p><strong>Mantra ({_esc(man['for_planet'])}):</strong> {_esc(man['beej_ne'])} "
                     f"({ _esc(man['transliteration']) }). {pick(man['instruction'])}</p>")
    for dr in rems.get("dosha_remedies", []):
        parts.append(f"<h3>{pick(dr['dosha'])}</h3>")
        for item in dr["items"]:
            parts.append(f"<p>• {pick(item)}</p>")

    lucky = report.get("lucky", {})
    if lucky:
        parts.append(
            f"<h2>Lucky Attributes</h2><p>Number: {pick(lucky['number'])} · Colour: {pick(lucky['colour'])} · "
            f"Day: {pick(lucky['day'])} · Deity: {pick(lucky['deity'])}</p>"
        )

    parts.append("<p class='meta'>Generated by Vedic Astro — Swiss Ephemeris (Lahiri ayanamsa), "
                 "Parashari + KP + Jaimini methods. For guidance and reflection.</p>")
    parts.append("</body></html>")
    return "".join(parts)


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
    story = [Paragraph("Vedic Astrology — Premium Report", styles["Title"])]
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
