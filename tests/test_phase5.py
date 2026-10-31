"""Phase 5: Predictive Intelligence — consensus, yoga timing, AV gochar,
Arudha padas."""
from datetime import datetime, timezone

from astro import phase5 as p5


def _bundle():
    from astro.engine import compute_kundali
    return compute_kundali({
        'name': 'Test', 'dob': '1998-05-14', 'tob': '06:30',
        'lat': 27.7, 'lon': 85.3, 'tz': 'Asia/Kathmandu',
        'place_name': 'Kathmandu',
    })


def test_dasha_consensus_structure():
    b = _bundle()
    c = p5.dasha_consensus(b, months=6)
    assert len(c["timeline"]) == 6
    t = c["timeline"][0]
    assert "consensus" in t and "agreement" in t
    assert t["verdict"] in ("favourable", "challenging", "mixed")
    assert 0 <= t["agreement"] <= 1
    # At least Vimshottari should be present.
    assert "vimshottari" in t["systems"]


def test_dasha_consensus_scoring():
    # Benefic in kendra should score positive.
    planets = {"Jupiter": {"house": 1, "dignity": "own", "sign_en": "Sagittarius"}}
    score = p5._score_planet("Jupiter", planets, {})
    assert score > 1.0
    # Malefic in dusthana should score negative.
    planets = {"Saturn": {"house": 8, "dignity": "debilitated", "sign_en": "Aries"}}
    score = p5._score_planet("Saturn", planets, {})
    assert score < -1.0


def test_yoga_fructification():
    b = _bundle()
    yf = p5.yoga_fructification(b, years=5)
    assert len(yf["yogas"]) > 0
    y = yf["yogas"][0]
    assert "yoga" in y and "activations" in y
    assert len(y["activations"]) > 0
    assert "md" in y["activations"][0]


def test_ashtakavarga_gochar():
    b = _bundle()
    ag = p5.ashtakavarga_gochar(b, days=7)
    assert len(ag["days"]) == 7
    assert ag["days"][0]["verdict"] in ("favourable", "challenging", "neutral")
    assert "saturn" in ag and "jupiter" in ag


def test_arudha_padas():
    planets = {"Mars": {"sign": 0}, "Venus": {"sign": 1}, "Mercury": {"sign": 2},
               "Moon": {"sign": 3}, "Sun": {"sign": 4}, "Jupiter": {"sign": 8},
               "Saturn": {"sign": 9}}
    ap = p5.arudha_padas(planets, 0)  # Aries lagna
    assert len(ap["padas"]) == 12
    # A1 should not be the lagna itself (exception rule).
    a1 = ap["padas"][0]
    assert a1["label"] == "A1"
    assert a1["arudha_sign"] != 0  # not Aries
