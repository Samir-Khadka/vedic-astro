"""Tests for Life Question answers (POST /api/life-questions/{id}/answer)."""

from fastapi.testclient import TestClient

from astro import life_answers as la
from astro import life_questions as lq
from main import app

SAMPLE_BIRTH = {"name": "Test", "dob": "1990-05-15", "tob": "08:30", "place_id": "kathmandu"}

client = TestClient(app)


def test_birth_answer_returns_band_and_evidence():
    r = client.post("/api/life-questions/marriage_timing/answer", json={"birth": SAMPLE_BIRTH})
    assert r.status_code == 200
    a = r.json()
    assert a["band"] in ("favourable", "mixed", "unfavourable", "unclear")
    assert a["source"] == "birth"
    assert a["evidence"], "evidence table must not be empty"
    roles = [e["role_en"] for e in a["evidence"]]
    assert "Current Mahadasha lord" in roles
    assert "Current Antardasha lord" in roles
    # Every evidence row classifies its houses for this question.
    for e in a["evidence"]:
        for h in e["houses"]:
            assert h["class"] in ("prime", "supporting", "negating", "other")
    assert a["disclaimer_en"] and a["disclaimer_ne"]


def test_prashna_answer_returns_band_and_evidence():
    r = client.post("/api/life-questions/marriage_timing/answer",
                    json={"prashna": {"number": 42, "place_id": "kathmandu"}})
    assert r.status_code == 200
    a = r.json()
    assert a["band"] in ("favourable", "mixed", "unfavourable", "unclear")
    assert a["source"] == "prashna"
    assert a["evidence"]


def test_unknown_question_404():
    r = client.post("/api/life-questions/nope/answer", json={"birth": SAMPLE_BIRTH})
    assert r.status_code == 404


def test_bad_payloads_400():
    assert client.post("/api/life-questions/marriage_timing/answer", json={}).status_code == 400
    assert client.post("/api/life-questions/marriage_timing/answer",
                       json={"prashna": {"number": 300, "place_id": "kathmandu"}}).status_code == 400
    assert client.post("/api/life-questions/marriage_timing/answer",
                       json={"birth": {"tob": "08:30", "place_id": "kathmandu"}}).status_code == 400


def test_unclear_when_no_significators():
    q = lq.get_question("marriage_timing")
    a = la.answer_from_birth(q, {})
    assert a["band"] == "unclear"
    assert a["reason"] == "no_checked_lords"
    assert a["evidence"] == []


def test_sensitive_answers_carry_stronger_disclaimers():
    r = client.post("/api/life-questions/health_serious_periods/answer", json={"birth": SAMPLE_BIRTH})
    assert r.status_code == 200
    assert "clinician" in r.json()["disclaimer_en"]
    r = client.post("/api/life-questions/litigation_court_outcome/answer", json={"birth": SAMPLE_BIRTH})
    assert r.status_code == 200
    assert "lawyer" in r.json()["disclaimer_en"]


def test_all_questions_answer_without_crash():
    for q in lq.QUESTIONS:
        r = client.post(f"/api/life-questions/{q['id']}/answer", json={"birth": SAMPLE_BIRTH})
        assert r.status_code == 200, q["id"]
        assert r.json()["band"] in ("favourable", "mixed", "unfavourable", "unclear")
