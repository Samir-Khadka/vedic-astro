"""Tests for Life Question answers (POST /api/life-questions/{id}/answer)."""

import pytest
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


def test_prashna_answer_with_global_place_coordinates():
    # Pins the backend half of the 2026-11-22 frontend fix, at engine
    # level — kept off HTTP because the suite sits at the rate-limit
    # edge and extra heavy endpoint calls 429 downstream tests (see
    # 2026-11-21). The Life Questions Prashna flow sends the first
    # /api/places hit, and a worldwide hit carries lat/lon/tz with id
    # null — that shape must resolve and answer.
    from datetime import datetime
    from zoneinfo import ZoneInfo

    from astro import engine, prashna as prashna_module

    place = engine.resolve_place({"place_name": "Lukla", "lat": 27.6875,
                                  "lon": 86.7314, "tz": "Asia/Kathmandu"})
    horary = prashna_module.horary(42, place, datetime.now(ZoneInfo(place["tz"])), "")
    a = la.answer_from_prashna(lq.get_question("marriage_timing"), horary)
    assert a["source"] == "prashna"
    assert a["band"] in ("favourable", "mixed", "unfavourable", "unclear")


def test_prashna_answer_with_null_place_id_400():
    # place_id null carries no place at all — resolve_place must raise
    # (the endpoint converts that ValueError to 400), so the frontend
    # can never silently send it.
    from astro import engine

    with pytest.raises(ValueError):
        engine.resolve_place({"place_id": None})


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
