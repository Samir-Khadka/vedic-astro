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

# Words that must never appear in the curated library (case-insensitive).
EXCLUDED = [
    "sex of", "abortion", "miscarriage", "call girl", "prostitution",
    "imprisonment", "rape",
]


def test_about_twenty_questions_unique_ids():
    assert 18 <= len(lq.QUESTIONS) <= 24, len(lq.QUESTIONS)
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


def test_no_excluded_topics_and_health_disclaimer():
    blob = " ".join(
        f"{q['question_en']} {q['what_to_check_en']} {q['timing_note_en']}".lower()
        for q in lq.QUESTIONS
    )
    for word in EXCLUDED:
        assert word not in blob, word
    health = lq.get_question("health_general")
    assert "not medical advice" in health["what_to_check_en"].lower()
    assert "not medical advice" in lq.DISCLAIMER_EN.lower()


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
