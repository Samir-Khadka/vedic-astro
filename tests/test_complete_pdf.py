"""Tests for the downloadable Complete Report PDF (GET /api/complete-report.pdf)."""

from fastapi.testclient import TestClient

from astro import complete_pdf as cp
from astro import engine
from main import app

PARAMS = {"dob": "1990-05-15", "tob": "08:30", "place_id": "kathmandu"}

client = TestClient(app)


def test_detailed_pdf_is_real_attachment():
    r = client.get("/api/complete-report.pdf", params=PARAMS)
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert "attachment" in r.headers["content-disposition"]
    assert "vedic-complete-report.pdf" in r.headers["content-disposition"]
    assert r.content[:5] == b"%PDF-"
    assert len(r.content) > 50_000, "detailed PDF suspiciously small"


def test_nepali_and_basic_models():
    r = client.get("/api/complete-report.pdf", params={**PARAMS, "lang": "ne"})
    assert r.status_code == 200 and r.content[:5] == b"%PDF-"
    r = client.get("/api/complete-report.pdf", params={**PARAMS, "model": "basic"})
    assert r.status_code == 200 and r.content[:5] == b"%PDF-"
    r = client.get("/api/complete-report.pdf", params={**PARAMS, "model": "book"})
    assert r.status_code == 200 and r.content[:5] == b"%PDF-"
    assert client.get("/api/complete-report.pdf", params={**PARAMS, "model": "nope"}).status_code == 400


def test_html_covers_all_sections_in_order():
    bundle = engine.compute_kundali({"name": "Test", "dob": "1990-05-15", "tob": "08:30", "place_id": "kathmandu"})
    from astro import complete_report as cr

    report = cr.build_complete_report(bundle)
    html_text = cp.build_html(report, "en", "detailed")
    assert len(report["sections"]) == 31
    import html as html_mod

    positions = [html_text.index(html_mod.escape(s["title_en"])) for s in report["sections"]]
    assert positions == sorted(positions), "sections out of legacy order in PDF HTML"
    basic = cp.sections_for_model(report, "basic")
    assert [s["id"] for s in basic] == cp.BASIC_SECTIONS
