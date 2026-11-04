"""Downloadable PDF of the Complete Kundali Report.

Renders the same 31 sections, in legacy order, that POST
/api/complete-report returns — as a real attachment download, not just
a browser print. Primary renderer: WeasyPrint (HTML/CSS, handles
Devanagari when a suitable font is present). Fallback: fpdf2 with the
vendored Noto Sans Devanagari fonts (data/fonts/) and uharfbuzz shaping
— the same pattern astro/pdf.py uses for the premium report — so Nepali
text stays Nepali instead of degrading to English.

Print models: ?model=detailed (default, all 31 sections), basic (the
same 9-section quick reading as the in-app model selector, with
Vimshottari condensed to the current Mahadasha/Antardasha), or book
(all 31 sections, larger type). The in-app Download button passes the
currently selected model.
"""

from __future__ import annotations

import html

BASIC_SECTIONS = [
    "title", "planet_position", "birth_details", "moon_navamsa",
    "vimshottari", "sade_sati", "manglik", "kaalsarp",
    "general_predictions",
]


def sections_for_model(report: dict, model: str) -> list:
    sections = (report or {}).get("sections") or []
    if model == "basic":
        # Same 9 sections, in the same order, as the in-app Basic model.
        order = {sid: i for i, sid in enumerate(BASIC_SECTIONS)}
        chosen = [s for s in sections if s.get("id") in order]
        return sorted(chosen, key=lambda s: order[s["id"]])
    return list(sections)


def _esc(s) -> str:
    return html.escape(str(s))


def _short(s: str, limit: int = 400) -> str:
    s = str(s)
    return s if len(s) <= limit else s[:limit] + "…"


def _html_value(v, depth: int = 0) -> str:
    """Generic data -> HTML. Dicts become key/value tables, lists of
    dicts become tables, other lists become bullet lists, scalars
    become text. Depth-capped so deeply nested engine data cannot
    blow up the document."""
    if isinstance(v, dict):
        if not v:
            return "<p>—</p>"
        if depth >= 3:
            return "<p>" + _esc(_short(v)) + "</p>"
        rows = "".join(
            f"<tr><th>{_esc(k)}</th><td>{_html_value(val, depth + 1)}</td></tr>"
            for k, val in v.items()
        )
        return f"<table>{rows}</table>"
    if isinstance(v, list):
        if not v:
            return "<p>—</p>"
        if all(isinstance(x, dict) for x in v) and depth < 3:
            keys = []
            for x in v:
                for k in x:
                    if k not in keys:
                        keys.append(k)
            head = "".join(f"<th>{_esc(k)}</th>" for k in keys)
            rows = "".join(
                "<tr>" + "".join(
                    f"<td>{_html_value(x.get(k, ''), depth + 1)}</td>" for k in keys
                ) + "</tr>" for x in v
            )
            return f"<table><tr>{head}</tr>{rows}</table>"
        return "<ul>" + "".join(
            f"<li>{_html_value(x, depth + 1)}</li>" for x in v[:200]
        ) + "</ul>"
    if isinstance(v, bool):
        return "Yes" if v else "No"
    if v is None:
        return "—"
    if isinstance(v, float):
        return f"{v:.3f}"
    return _esc(_short(v))


def _section_data_for_model(section: dict, model: str):
    data = section.get("data") or {}
    if model == "basic" and section.get("id") == "vimshottari" and isinstance(data, dict):
        current = data.get("current") or {}
        return {"current_mahadasha": (current.get("mahadasha") or {}).get("lord"),
                "current_antardasha": (current.get("antardasha") or {}).get("lord")}
    return data


_CSS = """
@page { size: A4; margin: 18mm 15mm 16mm 15mm;
  @bottom-center { content: "Vedic Astro — Complete Kundali Report · " counter(page) " / " counter(pages);
                   font-size: 8pt; color: #8a6a4a; } }
body { font-family: 'Noto Sans Devanagari','DejaVu Sans',sans-serif; color:#3a1e0c; font-size:10.5pt; line-height:1.5; }
body.book { font-size:12pt; line-height:1.75; }
h1 { color:#5c2f08; font-size:26pt; text-align:center; }
h2 { color:#7a3c06; border-bottom:1.5px solid #e07b0a; padding-bottom:1mm; margin-top:7mm; font-size:14.5pt; page-break-before: always; }
h2.first { page-break-before: auto; }
h3 { color:#5c2f08; margin-top:4mm; font-size:11.5pt; }
table { border-collapse:collapse; width:100%; margin:2.5mm 0; }
th,td { border:0.5pt solid #d9b98a; padding:1.4mm 1.8mm; text-align:left; font-size:9pt; vertical-align:top; }
th { background:#fbeed7; color:#7a3c06; }
p { margin: 1.6mm 0; text-align: justify; }
.meta { color:#555; font-size:9.5pt; text-align:center; }
.toc { font-size:11pt; line-height:2; }
.note { border:1pt solid #d9b98a; background:#fffdf7; padding:3mm 4mm; }
"""


def build_html(report: dict, lang: str = "en", model: str = "detailed") -> str:
    ne = lang == "ne"
    sections = sections_for_model(report, model)
    title = report.get("title") or {}
    if isinstance(title, dict):
        title_txt = title.get("ne" if ne else "en") or title.get("en") or ""
    else:
        title_txt = str(title)
    book_cls = ' class="book"' if model == "book" else ""
    parts = [f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{_CSS}</style></head>"
             f"<body{book_cls}>"]
    parts.append(f"<h1>{_esc(title_txt) if title_txt else ('पूर्ण कुण्डली प्रतिवेदन' if ne else 'Complete Kundali Report')}</h1>")
    title_sec = next((s for s in sections if s.get("id") == "title"), None)
    if title_sec and isinstance(title_sec.get("data"), dict):
        disc = (title_sec["data"].get("disclaimer") or {})
        disc_txt = disc.get("ne" if ne else "en") or disc.get("en") or ""
        if disc_txt:
            parts.append(f'<p class="meta">{_esc(disc_txt)}</p>')
    parts.append(f"<h2 class='first'>{'सूची' if ne else 'Contents'}</h2><ol class='toc'>")
    for i, s in enumerate(sections, 1):
        parts.append(f"<li>{_esc(s.get('title_ne' if ne else 'title_en') or s.get('title_en') or s['id'])}</li>")
    parts.append("</ol>")
    for i, s in enumerate(sections):
        t = s.get("title_ne" if ne else "title_en") or s.get("title_en") or s["id"]
        parts.append(f"<h2{' class=\"first\"' if i == 0 else ''}>{i}. {_esc(t)}</h2>")
        if not s.get("available", True):
            note = s.get("note") or {}
            note_txt = note.get("ne" if ne else "en") or note.get("en") or ""
            parts.append(f'<p class="note">{_esc(note_txt) if note_txt else ("Not yet computed." if not ne else "अहिलेसम्म गणना गरिएको छैन।")}</p>')
            continue
        parts.append(_html_value(_section_data_for_model(s, model)))
    parts.append("</body></html>")
    return "".join(parts)


def _text_lines(report: dict, lang: str = "en", model: str = "detailed") -> list:
    """Plain-text mirror of build_html for the fpdf2 fallback:
    (level, text) lines — level 0 = document title, 1 = section, 2 = body."""
    ne = lang == "ne"
    lines = []
    title = report.get("title") or {}
    if isinstance(title, dict):
        title_txt = title.get("ne" if ne else "en") or title.get("en") or ""
    else:
        title_txt = str(title)
    lines.append((0, title_txt or ("पूर्ण कुण्डली प्रतिवेदन" if ne else "Complete Kundali Report")))

    def walk(v, prefix=""):
        if isinstance(v, dict):
            for k, val in v.items():
                if isinstance(val, (dict, list)):
                    lines.append((2, f"{prefix}{k}:"))
                    walk(val, prefix + "  ")
                else:
                    lines.append((2, f"{prefix}{k}: {val}"))
        elif isinstance(v, list):
            for x in v[:200]:
                if isinstance(x, (dict, list)):
                    walk(x, prefix + "- ")
                else:
                    lines.append((2, f"{prefix}- {x}"))
        elif v is not None:
            lines.append((2, f"{prefix}{v}"))

    for i, s in enumerate(sections_for_model(report, model), 1):
        t = s.get("title_ne" if ne else "title_en") or s.get("title_en") or s["id"]
        lines.append((1, f"{i}. {t}"))
        if not s.get("available", True):
            note = s.get("note") or {}
            note_txt = note.get("ne" if ne else "en") or note.get("en") or ""
            lines.append((2, note_txt or ("Not yet computed." if not ne else "अहिलेसम्म गणना गरिएको छैन।")))
            continue
        walk(_section_data_for_model(s, model))
    return lines


def render_complete_pdf(report: dict, lang: str = "en", model: str = "detailed") -> bytes:
    html_text = build_html(report, lang, model)
    try:
        from weasyprint import HTML

        return HTML(string=html_text).write_pdf()
    except Exception:
        pass
    return _render_fpdf_fallback(report, lang, model)


def _render_fpdf_fallback(report: dict, lang: str, model: str) -> bytes:
    """fpdf2 + vendored Devanagari fonts, same pattern as astro/pdf.py.
    Falls back to plain Latin text if fonts/fpdf2 are unavailable."""
    from .pdf import _fallback_font_paths, _is_devanagari_word

    paths = _fallback_font_paths()
    if paths is None:
        raise RuntimeError("no PDF renderer available (WeasyPrint, fpdf2 fonts missing)")
    try:
        from fpdf import FPDF
    except Exception as e:
        raise RuntimeError(f"fpdf2 unavailable: {e}")
    dev_regular, dev_bold, lat_regular, lat_bold = paths
    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(15, 15, 15)
    pdf.add_page()
    pdf.add_font("NotoDev", "", dev_regular)
    pdf.add_font("NotoDev", "B", dev_bold)
    pdf.add_font("DejaVu", "", lat_regular)
    pdf.add_font("DejaVu", "B", lat_bold)

    def clean(text: str) -> str:
        return (str(text).replace("—", "-").replace("–", "-")
                .replace("·", "-").replace("“", '"').replace("”", '"')
                .replace("‘", "'").replace("’", "'"))

    def paragraph(text: str, size: int, bold: bool):
        style = "B" if bold else ""
        pdf.set_x(pdf.l_margin)
        for word in clean(text).split(" "):
            if not word:
                continue
            family = "NotoDev" if _is_devanagari_word(word) else "DejaVu"
            pdf.set_font(family, style, size)
            width = pdf.get_string_width(word + " ")
            if pdf.get_x() + width > pdf.w - pdf.r_margin:
                pdf.ln(size * 0.45)
                pdf.set_x(pdf.l_margin)
            pdf.cell(width, size * 0.45, word + " ")
        pdf.ln(size * 0.45)

    for level, text in _text_lines(report, lang, model):
        if level == 0:
            paragraph(text, 20, True)
        elif level == 1:
            paragraph(text, 14, True)
        else:
            paragraph(text, 11, False)
    return bytes(pdf.output())
