"""Phase 1 Life Questions library: bilingual completeness, shape,
categories, and the excluded-topics guard."""
from fastapi.testclient import TestClient

from astro import life_questions as lq
from main import app

client = TestClient(app)

REQUIRED = [
    "id", "category", "category_en", "category_ne",
    "question_en", "question_ne",
    "prime_houses", "supporting_houses", "negating_houses",
    "significator_en", "significator_ne",
    "what_to_check_en", "what_to_check_ne",
    "timing_note_en", "timing_note_ne",
    "disclaimer_en", "disclaimer_ne",
]

# Sensitive topics are included only in probability framing (per Samir,
# 2026-11-04): each such entry must say so explicitly, never as a
# guaranteed outcome, and must point to a clinician/lawyer where relevant.
SENSITIVE_IDS = [
    "children_sex_indication", "children_pregnancy_difficulty",
    "marriage_relationship_strain", "litigation_legal_trouble",
    "litigation_court_outcome", "health_serious_periods",
]


def test_about_twenty_questions_unique_ids():
    assert 18 <= len(lq.QUESTIONS) <= 30, len(lq.QUESTIONS)
    ids = [q["id"] for q in lq.QUESTIONS]
    assert len(ids) == len(set(ids))


def test_every_question_bilingual_and_valid_houses():
    for q in lq.QUESTIONS:
        pub = lq.to_public(q)
        for key in REQUIRED:
            assert pub[key], (q["id"], key)
        assert pub["question_ne"] != pub["question_en"], q["id"]
        for houses in (pub["prime_houses"], pub["supporting_houses"], pub["negating_houses"]):
            assert houses and all(1 <= h <= 12 for h in houses), (q["id"], houses)
        # Nepali text should contain Devanagari.
        assert any("\u0900" <= ch <= "\u097f" for ch in pub["question_ne"]), q["id"]


def test_sensitive_topics_probability_framed_and_health_disclaimer():
    for qid in SENSITIVE_IDS:
        q = lq.get_question(qid)
        assert q is not None, qid
        text = f"{q['what_to_check_en']} {q['timing_note_en']}".lower()
        assert "probability" in text, qid
        assert "not" in text, qid
    health = lq.get_question("health_general")
    assert "not medical advice" in health["what_to_check_en"].lower()
    assert "not medical advice" in lq.DISCLAIMER_EN.lower()
    # No sensitive entry may claim a guaranteed outcome.
    for qid in SENSITIVE_IDS:
        q = lq.get_question(qid)
        assert "will happen" not in q["what_to_check_en"].lower(), qid


def test_api_list_filter_and_single():
    r = client.get("/api/life-questions")
    assert r.status_code == 200
    data = r.json()
    assert len(data["questions"]) == len(lq.QUESTIONS)
    assert {c["slug"] for c in data["categories"]} >= {"marriage", "education", "career", "health"}
    r = client.get("/api/life-questions", params={"category": "marriage"})
    assert r.status_code == 200
    assert r.json()["questions"] and all(
        q["category"] == "marriage" for q in r.json()["questions"])
    assert client.get("/api/life-questions", params={"category": "nope"}).status_code == 400
    r = client.get("/api/life-questions/marriage_timing")
    assert r.status_code == 200 and r.json()["prime_houses"] == [7, 2, 11]
    assert client.get("/api/life-questions/nope").status_code == 404
