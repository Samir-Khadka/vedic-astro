"""Phase 3 A3: the PDF fallback stays in the requested language.

WeasyPrint is the primary renderer; when it is unavailable the fallback
must still produce a Nepali PDF with correctly shaped Devanagari, not
silently switch to English. Text extraction needs `pdftotext`
(poppler-utils); the content tests skip without it, but the
bytes/structure tests always run.
"""
import shutil
import subprocess
import tempfile

import pytest

from astro import pdf as pdf_module

BUNDLE = {
    "name": "Test",
    "birth": {
        "date": "2000-01-01",
        "time": "06:30",
        "place": {"name": "Kathmandu"},
        "bs_date": "१७ पौष २०५६",
    },
    "deep_report": {
        "planet_chapters": {
            "Sun": [{"en": "Sun is strong.", "ne": "सूर्य बलियो छ।"}],
        },
    },
    "predictions": {
        "career": [{"en": "Good career.", "ne": "राम्रो पेशा।"}],
    },
    "report": {
        "chapters": {
            "personality": [{"en": "Kind.", "ne": "दयालु।"}],
        },
        "favourable_periods": [
            {
                "year": 2026,
                "mahadasha": "Jupiter",
                "antardasha": "Saturn",
                "summary": {"en": "Good year.", "ne": "राम्रो वर्ष।"},
            },
        ],
    },
}


def _extract(data: bytes) -> str:
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as fh:
        fh.write(data)
        path = fh.name
    out = subprocess.run(
        ["pdftotext", "-layout", path, "-"],
        capture_output=True, text=True, timeout=30,
    )
    assert out.returncode == 0, out.stderr
    return out.stdout


def test_fallback_fonts_exist():
    assert pdf_module._fallback_font_paths() is not None


def test_fallback_produces_valid_pdf_both_languages():
    for lang in ("en", "ne"):
        data = pdf_module._render_pdf_fallback(BUNDLE, lang)
        assert data[:5] == b"%PDF-"
        assert len(data) > 10_000, (lang, len(data))


def test_fallback_keeps_requested_language():
    if shutil.which("pdftotext") is None:
        pytest.skip("pdftotext not available")
    ne_text = _extract(pdf_module._render_pdf_fallback(BUNDLE, "ne"))
    assert "सूर्य बलियो छ" in ne_text
    assert "राम्रो पेशा" in ne_text
    assert "दयालु" in ne_text
    # Mixed-script content survives: Latin planet name and BS date.
    assert "Sun" in ne_text
    assert "१७ पौष २०५६" in ne_text
    assert "Jupiter/Saturn" in ne_text
    en_text = _extract(pdf_module._render_pdf_fallback(BUNDLE, "en"))
    assert "Sun is strong" in en_text
    assert "Good career" in en_text


def test_fallback_degrees_to_reportlab_without_fonts(monkeypatch):
    monkeypatch.setattr(pdf_module, "_fallback_font_paths", lambda: None)
    data = pdf_module._render_pdf_fallback(BUNDLE, "ne")
    assert data[:5] == b"%PDF-"
