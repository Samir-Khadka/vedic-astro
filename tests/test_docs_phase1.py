"""Phase 1 docs: README lists the new APIs, and the Muhurta scoring
note exists in both languages in the UI strings."""
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
README = (BASE / "README.md").read_text()
APP_JS = (BASE / "static" / "app.js").read_text()
INDEX = (BASE / "static" / "index.html").read_text()


def test_readme_lists_new_apis_and_features():
    for needle in (
        "/api/muhurta", "/api/prashna", "/api/life-questions",
        "Muhurta Finder", "Life Questions library", "KP Prashna",
        "How Muhurta scoring works", "Excellent",
    ):
        assert needle in README, needle


def test_muhurta_scoring_note_bilingual_in_ui():
    assert 'data-i18n="muhurta_scoring"' in INDEX
    assert "muhurta_scoring:" in APP_JS
    # Both language blocks carry the key: English text and a Devanagari one.
    assert "How scoring works" in APP_JS
    assert "अङ्कन कसरी हुन्छ" in APP_JS
