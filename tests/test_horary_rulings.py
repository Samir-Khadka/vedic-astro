"""Step 3 (horary deepening): every Life Question carries a full
traditional ruling, or an honest pending marker — never an invented
one. Checks the API payload shape (additive: all Phase 1 fields still
present), ruling completeness in both languages, documented sources,
and that sensitive questions keep their probability framing."""

from fastapi.testclient import TestClient

from astro import horary_rulings as hr
from astro import life_questions as lq
from main import app

client = TestClient(app)

SENSITIVE_IDS = [
    "children_sex_indication", "children_pregnancy_difficulty",
    "marriage_relationship_strain", "litigation_legal_trouble",
    "litigation_court_outcome", "health_serious_periods",
]

# Questions whose ruling is anchored in a legacy Subjects template
# actually read from Drive for this step (id after "template:").
TEMPLATE_ANCHORED = {
    "marriage_timing": "1BA-FSO_O264rPw90nNVckSkEqtGRqv6i",
    "education_exams": "1KSwPLdi3KL9hyea2FVEtRJpvWfkV_SBw",
    "education_field": "1KSwPLdi3KL9hyea2FVEtRJpvWfkV_SBw",
    "career_business_vs_service": "1c2YlB2zZF_x3pCUhspvtVnYlIvinyeLu",
    "property_buying": "1BkKEQ7Dhd9EEnA4XLHaxrZRYABACtVBE",
    "vehicle_buying": "1r2j4q95exlfFLHYhLulaiYqLGYbpiNG_",
    "vehicle_sale_loan": "1r2j4q95exlfFLHYhLulaiYqLGYbpiNG_",
    "health_general": "1F4-A-aowvw9ixguaqjtsvNvV1HTytjtj",
    "litigation_court_outcome": "1Tr76-M1aCBaExg7AJDjppirinfMBBCS_",
    "children_sex_indication": "1pY7NW7i2_hNdNgcogHQJIs3yMNWJBkIL",
}


def _is_devanagari(s):
    return any("\u0900" <= ch <= "\u097f" for ch in s)


def test_every_question_has_a_ruling_in_payload():
    for q in lq.QUESTIONS:
        pub = lq.to_public(q)
        assert "ruling" in pub, q["id"]
        ruling = pub["ruling"]
        assert ruling["source"] in ("pending", "classical") or ruling["source"].startswith("template:"), q["id"]
        if ruling["source"] != "pending":
            for key in ("method_en", "method_ne", "favourable_en",
                        "favourable_ne", "unfavourable_en",
                        "unfavourable_ne", "source_label_en",
                        "source_label_ne"):
                assert ruling.get(key), (q["id"], key)
            assert _is_devanagari(ruling["method_ne"]), q["id"]
            assert _is_devanagari(ruling["favourable_ne"]), q["id"]
            assert ruling["method_ne"] != ruling["method_en"], q["id"]
        else:
            # Pending rulings must not smuggle in favourable claims.
            assert "favourable_en" not in ruling, q["id"]
            assert ruling.get("note_en") and ruling.get("note_ne"), q["id"]


def test_no_question_left_pending():
    pending = [q["id"] for q in lq.QUESTIONS
               if lq.to_public(q)["ruling"]["source"] == "pending"]
    assert pending == [], pending


def test_template_anchored_sources_match():
    for qid, template_id in TEMPLATE_ANCHORED.items():
        ruling = hr.get_ruling(qid)
        assert template_id in ruling["source"], (qid, ruling["source"])
    # Every other question is honestly labelled classical, not template.
    for q in lq.QUESTIONS:
        if q["id"] not in TEMPLATE_ANCHORED:
            assert hr.get_ruling(q["id"])["source"] == "classical", q["id"]


def test_ruling_sources_cover_all_questions():
    assert set(hr.RULINGS) == {q["id"] for q in lq.QUESTIONS}
    assert len(hr.RULINGS) == 26


def test_children_sex_ruling_leads_with_template_warning():
    ruling = hr.get_ruling("children_sex_indication")
    method = ruling["method_en"].lower()
    assert "no confirmed sutra" in method
    assert "should not predict" in method
    assert "unsatisfactory" in method
    assert "unsatisfactory" in ruling["favourable_en"].lower()


def test_sensitive_rulings_keep_probability_framing():
    for qid in SENSITIVE_IDS:
        ruling = hr.get_ruling(qid)
        text = " ".join(
            ruling[k] for k in ("method_en", "favourable_en",
                                "unfavourable_en") if ruling.get(k)
        ).lower()
        assert "probability" in text, qid


def test_api_returns_ruling_and_keeps_old_shape():
    resp = client.get("/api/life-questions/marriage_timing")
    assert resp.status_code == 200
    body = resp.json()
    assert body["prime_houses"] == [7, 2, 11]
    assert body["significator_en"] == "Venus"
    assert body["ruling"]["source"].startswith("template:")
    assert "Venus" in body["ruling"]["favourable_en"]
    resp = client.get("/api/life-questions?category=litigation")
    assert resp.status_code == 200
    for item in resp.json()["questions"]:
        assert item["ruling"]["source"] != "pending"
