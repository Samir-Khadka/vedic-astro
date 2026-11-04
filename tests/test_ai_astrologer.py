"""Tests for the AI Astrologer + Life Areas backend.

Covers: EN/NE classification (2+ questions per area per language),
analyse() on a sample Kathmandu chart, build_answer() structure for
career and health, the graceful fallback, out-of-scope refusals,
strengthened disclaimers, and the two new HTTP endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from astro import ai_astrologer as aa
from astro import engine, life_areas as la
from main import app

SAMPLE = {"name": "Test", "dob": "1990-05-15", "tob": "08:30", "place_id": "kathmandu"}

EN_CASES = [
    ("What is my personality like?", "personality"),
    ("Tell me about my nature and character.", "personality"),
    ("Will I get a promotion in my job?", "career"),
    ("Should I start a business?", "career"),
    ("Will my income increase this year?", "finance"),
    ("How can I grow my wealth and savings?", "finance"),
    ("When will I get married?", "marriage"),
    ("Will my relationship with my partner improve?", "marriage"),
    ("Will my health improve?", "health"),
    ("What does my chart say about chronic disease?", "health"),
    ("Will I pass my exam?", "education"),
    ("Should I pursue higher study at university?", "education"),
    ("Will I buy a house for my family?", "family_home"),
    ("How are my family and home life?", "family_home"),
    ("Will I get a visa to go abroad?", "foreign"),
    ("Should I settle abroad?", "foreign"),
]

NE_CASES = [
    ("मेरो स्वभाव कस्तो छ?", "personality"),
    ("मेरो व्यक्तित्व बारे बताउनुहोस्।", "personality"),
    ("म जागिरमा पदोन्नति पाउँछु?", "career"),
    ("व्यवसाय सुरु गर्नु राम्रो हो?", "career"),
    ("मेरो आम्दानी बढ्छ?", "finance"),
    ("पैसा बचत कसरी गर्ने?", "finance"),
    ("मेरो विवाह कहिले हुन्छ?", "marriage"),
    ("मेरो जीवनसाथीसँगको सम्बन्ध कस्तो?", "marriage"),
    ("मेरो स्वास्थ्य कस्तो रहन्छ?", "health"),
    ("रोग निको हुन्छ?", "health"),
    ("परीक्षा पास हुन्छु?", "education"),
    ("म पढाइमा सफल हुन्छु?", "education"),
    ("परिवारका लागि घर किन्दा राम्रो?", "family_home"),
    ("मेरो घर र परिवार कस्तो रहन्छ?", "family_home"),
    ("विदेश जाने भिसा पाउँछु?", "foreign"),
    ("विदेशमा बसोबास गर्नु राम्रो?", "foreign"),
]


@pytest.mark.parametrize("question,expected", EN_CASES)
def test_classification_english(question, expected):
    area, _second, conf = aa.classify(question)
    assert area == expected, f"{question!r} -> {area}"
    assert conf > 0


@pytest.mark.parametrize("question,expected", NE_CASES)
def test_classification_nepali(question, expected):
    area, _second, conf = aa.classify(question)
    assert area == expected, f"{question!r} -> {area}"
    assert conf > 0


def test_classification_second_area():
    area, second, conf = aa.classify("Will my job promotion increase my income?")
    assert area == "career"
    assert second == "finance"
    assert 0 < conf < 1


def _bundle():
    return engine.compute_kundali(SAMPLE)


def test_analyse_returns_eight_areas_with_real_content():
    areas = la.analyse(_bundle())
    assert [a["id"] for a in areas] == la.AREA_ORDER
    expected_houses = {
        "personality": [1], "career": [10, 6, 7], "finance": [2, 11, 5],
        "marriage": [7, 2, 11, 5], "health": [1, 6, 8, 12],
        "education": [4, 5, 9], "family_home": [2, 4], "foreign": [9, 12, 3],
    }
    for area in areas:
        assert area["houses"] == expected_houses[area["id"]]
        assert area["title_en"] and area["title_ne"]
        assert set(area["house_lords"]) == set(area["houses"])
        assert isinstance(area["planets_in"], dict)
        assert isinstance(area["planets_aspecting"], dict)
        assert 1 <= len(area["strongest"]) <= 3
        dasha = area["dasha_influence"]
        assert dasha["mahadasha_lord"] and dasha["antardasha_lord"]
        assert area["reading_en"] and area["reading_ne"]
        # Reading mentions at least one real placement, not filler.
        assert any(p in area["reading_en"] for p in la.PLANETS)


def test_analyse_aspects_follow_classical_drishti():
    # Jupiter aspects 5th/7th/9th from itself; sample Jupiter is in house 1.
    assert la.aspected_houses("Jupiter", 1) == [5, 7, 9]
    assert la.aspected_houses("Mars", 1) == [4, 7, 8]
    assert la.aspected_houses("Saturn", 1) == [3, 7, 10]
    assert la.aspected_houses("Venus", 1) == [7]


def test_build_answer_career_full_structure():
    ans = aa.build_answer("Will I get a promotion in my job?", _bundle(), "en")
    assert ans["area_id"] == "career"
    assert ans["area_title_en"] == "Career" and ans["area_title_ne"] == "करियर"
    assert ans["direct_answer_en"] and ans["direct_answer_ne"]
    assert "probability" in ans["direct_answer_en"].lower()
    assert ans["planet_table"], "career planet table must not be empty"
    row = ans["planet_table"][0]
    assert {"planet", "sign_en", "sign_ne", "house", "rules", "aspects",
            "effect_en", "effect_ne"} <= set(row)
    assert ans["timing_en"] and ans["timing_ne"]
    assert "exact date" not in ans["timing_en"].lower() or "never as exact dates" in ans["timing_en"]
    assert ans["disclaimer_en"] and ans["disclaimer_ne"]
    assert ans["band"] in ("favourable", "mixed", "unfavourable", "unclear")
    assert ans["life_area"]["id"] == "career"


def test_build_answer_health_strengthened_disclaimer():
    ans = aa.build_answer("Will my health improve?", _bundle(), "en")
    assert ans["area_id"] == "health"
    assert ans["planet_table"]
    assert ans["timing_en"]
    assert "clinician" in ans["disclaimer_en"]
    assert "चिकित्सक" in ans["disclaimer_ne"]


def test_build_answer_finance_strengthened_disclaimer():
    ans = aa.build_answer("Will my income increase?", _bundle(), "en")
    assert ans["area_id"] == "finance"
    assert "financial adviser" in ans["disclaimer_en"]


def test_build_answer_unmappable_returns_fallback():
    ans = aa.build_answer("Tell me about zebras and quantum entanglement.", _bundle(), "en")
    assert ans.get("fallback") is True
    assert ans["area_id"] is None
    assert len(ans["suggestions"]) == 8
    assert ans["planet_table"] == []


def test_build_answer_out_of_scope_death():
    ans = aa.build_answer("When will I die?", _bundle(), "en")
    assert ans.get("refusal") is True
    assert ans["kind"] == "death"
    assert "does not predict death" in ans["explanation_en"]


def test_build_answer_out_of_scope_death_nepali():
    ans = aa.build_answer("म कहिले मर्छु?", _bundle(), "ne")
    assert ans.get("refusal") is True
    assert ans["kind"] == "death"


def test_build_answer_out_of_scope_lottery():
    ans = aa.build_answer("Will I win the lottery this week?", _bundle(), "en")
    assert ans.get("refusal") is True
    assert ans["kind"] == "lottery"


def test_build_answer_out_of_scope_exact_date_keeps_area():
    ans = aa.build_answer("What is the exact date of my marriage?", _bundle(), "en")
    assert ans.get("refusal") is True
    assert ans["kind"] == "exact_date"
    assert ans["area_id"] == "marriage"


def test_build_answer_timing_question_is_not_refused():
    # A legitimate timing question gets a dasha period, not a refusal.
    ans = aa.build_answer("When will I get married?", _bundle(), "en")
    assert not ans.get("refusal")
    assert ans["area_id"] == "marriage"
    assert "Mahadasha" in ans["timing_en"]


def test_build_answer_prashna_mode():
    from astro import prashna as prashna_module

    place = engine.resolve_place({"place_id": "kathmandu"})
    from datetime import datetime
    from zoneinfo import ZoneInfo

    horary = prashna_module.horary(42, place, datetime.now(ZoneInfo(place["tz"])),
                                   "Will I get a promotion in my job?")
    ans = aa.build_answer("Will I get a promotion in my job?", horary, "en")
    assert ans["area_id"] == "career"
    assert ans["source_note"] == "prashna"
    assert ans["planet_table"]
    assert ans["timing_en"]


def test_life_areas_endpoint():
    client = TestClient(app)
    resp = client.post("/api/life-areas", json=SAMPLE)
    assert resp.status_code == 200
    areas = resp.json()["areas"]
    assert len(areas) == 8
    assert areas[0]["id"] == "personality"
    assert areas[0]["reading_en"]


def test_life_areas_endpoint_bad_payload():
    client = TestClient(app)
    resp = client.post("/api/life-areas", json={"dob": "not-a-date", "tob": "08:30"})
    assert resp.status_code == 400


def test_ask_endpoint_birth_and_prashna():
    client = TestClient(app)
    resp = client.post("/api/ask-astrologer", json={
        "question": "Will I get a promotion in my job?",
        "birth": SAMPLE, "lang": "en"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["source"] == "birth"
    assert data["question"] == "Will I get a promotion in my job?"
    assert data["area_id"] == "career"
    assert data["planet_table"]

    resp = client.post("/api/ask-astrologer", json={
        "question": "Will my health improve?",
        "prashna_number": 42, "place": {"place_id": "kathmandu"}})
    assert resp.status_code == 200
    assert resp.json()["source"] == "prashna"


def test_ask_endpoint_validation_errors():
    client = TestClient(app)
    assert client.post("/api/ask-astrologer", json={"question": "  "}).status_code == 400
    assert client.post("/api/ask-astrologer", json={
        "question": "Will I get a job?"}).status_code == 400
    assert client.post("/api/ask-astrologer", json={
        "question": "Will I get a job?", "prashna_number": 300,
        "place": {"place_id": "kathmandu"}}).status_code == 400
    assert client.post("/api/ask-astrologer", json={
        "question": "Will I get a job?", "prashna_number": 42}).status_code == 400
    assert client.post("/api/ask-astrologer", json={
        "question": "Will I get a job?", "birth": SAMPLE, "lang": "hi"}).status_code == 400
