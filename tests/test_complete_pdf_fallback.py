"""Complete-report PDF: the fpdf2 fallback path.

The existing tests only exercise the WeasyPrint primary renderer, so
``_text_lines`` and ``_render_fpdf_fallback`` were entirely uncovered
(complete_pdf.py was at 53%). The fallback is the production safety
net — if WeasyPrint fails on Render, the download must still work and
stay in the requested language instead of 500ing.
"""
import shutil

import pytest
from fastapi.testclient import TestClient

from astro import complete_pdf as cp
from main import app

REPORT = {
    "title": {"en": "Complete Kundali Report", "ne": "पूर्ण कुण्डली प्रतिवेदन"},
    "sections": [
        {"id": "title", "title_en": "Title", "title_ne": "शीर्षक",
         "data": {"disclaimer": {"en": "Traditional guidance only.",
                                  "ne": "परम्परागत मार्गदर्शन मात्र।"}}},
        {"id": "planets", "title_en": "Planets", "title_ne": "ग्रहहरू",
         "data": {"Sun": {"sign": "Aries", "house": 1},
                  "notes": ["strong", "benefic"],
                  "score": 8.5, "verified": True, "missing": None}},
        {"id": "missing", "title_en": "Missing", "title_ne": "हराएको",
         "available": False,
         "note": {"en": "Not computed yet.", "ne": "अहिलेसम्म गणना गरिएको छैन।"}},
        {"id": "gone", "title_en": "Gone", "title_ne": "गएको",
         "available": False},
        {"id": "empty", "title_en": "Empty", "title_ne": "खाली", "data": {}},
    ],
}

client = TestClient(app)


def test_text_lines_title_forms():
    en = cp._text_lines(REPORT, "en", "detailed")
    assert en[0] == (0, "Complete Kundali Report")
    ne = cp._text_lines(REPORT, "ne", "detailed")
    assert ne[0] == (0, "पूर्ण कुण्डली प्रतिवेदन")
    assert cp._text_lines({"title": "Plain Title", "sections": []}, "en", "detailed") == [
        (0, "Plain Title")]
    assert cp._text_lines({"sections": []}, "en", "detailed") == [
        (0, "Complete Kundali Report")]
    assert cp._text_lines({"sections": []}, "ne", "detailed") == [
        (0, "पूर्ण कुण्डली प्रतिवेदन")]


def test_text_lines_section_bodies():
    lines = cp._text_lines(REPORT, "en", "detailed")
    texts = [t for _, t in lines]
    assert texts[1] == "1. Title"
    assert "disclaimer:" in texts
    assert "  en: Traditional guidance only." in texts
    assert "  ne: परम्परागत मार्गदर्शन मात्र।" in texts
    assert "2. Planets" in texts
    assert "Sun:" in texts and "  sign: Aries" in texts and "  house: 1" in texts
    assert "notes:" in texts and "  - strong" in texts
    assert "score: 8.5" in texts and "verified: True" in texts
    assert "missing: None" in texts
    # Unavailable sections print their note, or the default when absent.
    assert "3. Missing" in texts and "Not computed yet." in texts
    assert "4. Gone" in texts and "Not yet computed." in texts
    ne_texts = [t for _, t in cp._text_lines(REPORT, "ne", "detailed")]
    assert "अहिलेसम्म गणना गरिएको छैन।" in ne_texts
    assert "3. हराएको" in ne_texts


def test_text_lines_truncates_long_lists():
    report = {"sections": [{"id": "big", "title_en": "Big", "data": list(range(250))}]}
    lines = cp._text_lines(report, "en", "detailed")
    items = [t for _, t in lines if t.startswith("- ")]
    assert len(items) == 200
    assert items[0] == "- 0" and items[-1] == "- 199"


def test_fpdf_fallback_renders_real_pdf():
    for lang in ("en", "ne"):
        data = cp._render_fpdf_fallback(REPORT, lang, "detailed")
        assert data[:5] == b"%PDF-"
        assert len(data) > 10_000, lang


@pytest.mark.skipif(shutil.which("pdftotext") is None, reason="pdftotext not installed")
def test_fpdf_fallback_keeps_language():
    import subprocess
    import tempfile

    for lang, needle in (("en", "Complete Kundali Report"), ("ne", "पूर्ण कुण्डली प्रतिवेदन")):
        data = cp._render_fpdf_fallback(REPORT, lang, "detailed")
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as fh:
            fh.write(data)
            path = fh.name
        out = subprocess.run(["pdftotext", "-layout", path, "-"],
                             capture_output=True, text=True, timeout=30)
        assert out.returncode == 0, out.stderr
        assert needle in out.stdout, lang
        assert "Traditional guidance only." in out.stdout or "परम्परागत" in out.stdout


def test_render_complete_pdf_falls_back_when_weasyprint_fails(monkeypatch):
    """render_complete_pdf must degrade to the fpdf fallback — a real
    PDF with the report content — when WeasyPrint raises. (No byte
    equality with a second render: fpdf embeds a CreationDate, so two
    renders a second apart differ.)"""
    import subprocess
    import tempfile

    import weasyprint

    def _boom(*args, **kwargs):
        raise RuntimeError("weasyprint down")

    monkeypatch.setattr(weasyprint, "HTML", _boom)
    out = cp.render_complete_pdf(REPORT, "en", "detailed")
    assert out[:5] == b"%PDF-"
    assert len(out) > 10_000
    if shutil.which("pdftotext") is None:
        pytest.skip("pdftotext not installed")
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as fh:
        fh.write(out)
        path = fh.name
    text = subprocess.run(["pdftotext", "-layout", path, "-"],
                          capture_output=True, text=True, timeout=30).stdout
    assert "Complete Kundali Report" in text
    assert "Traditional guidance only." in text


def test_fpdf_fallback_without_fonts_raises(monkeypatch):
    """No vendored fonts and no WeasyPrint means no renderer at all —
    a clear RuntimeError, not a half-built PDF."""
    import astro.pdf as pdf_module

    monkeypatch.setattr(pdf_module, "_fallback_font_paths", lambda: None)
    with pytest.raises(RuntimeError, match="no PDF renderer available"):
        cp._render_fpdf_fallback(REPORT, "en", "detailed")


def test_endpoint_still_downloads_when_weasyprint_fails(monkeypatch):
    """The HTTP download degrades gracefully too: 200 + a real PDF
    attachment when the primary renderer is down."""
    import weasyprint

    monkeypatch.setattr(weasyprint, "HTML",
                        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("down")))
    r = client.get("/api/complete-report.pdf",
                   params={"dob": "1990-05-15", "tob": "08:30", "place_id": "kathmandu"})
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert r.content[:5] == b"%PDF-"
    assert len(r.content) > 10_000
