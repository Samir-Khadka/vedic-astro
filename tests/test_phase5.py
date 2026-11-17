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


def test_score_planet_shadbala_branches():
    # Mercury in the 2nd, neutral dignity: base 0.5 + 0.25 = 0.75.
    planets = {"Mercury": {"house": 2, "dignity": "neutral"}}
    assert p5._score_planet("Mercury", planets, {}) == 0.75
    # Strong shadbala (>= 6.5 rupas) adds 0.5; weak (<= 5.0) subtracts 0.5.
    assert p5._score_planet("Mercury", planets, {"Mercury": {"total": 7.0}}) == 1.25
    assert p5._score_planet("Mercury", planets, {"Mercury": {"total": 6.5}}) == 1.25
    assert p5._score_planet("Mercury", planets, {"Mercury": {"total": 4.0}}) == 0.25
    assert p5._score_planet("Mercury", planets, {"Mercury": {"total": 5.0}}) == 0.25
    # A non-dict shadbala entry defaults to 6.0 (no adjustment).
    assert p5._score_planet("Mercury", planets, {"Mercury": "strong"}) == 0.75


def test_period_at_unparseable_dates_fall_back_to_current():
    now = datetime.now(timezone.utc)
    # Dates that do not parse are skipped; the 'current' block is the fallback.
    tree = {"mahadashas": [{"lord": "Sun", "start": "not-a-date",
                            "end": "also-not-a-date"}],
            "current": {"mahadasha": {"lord": "Sun"}}}
    assert p5._period_at(tree, now) == {"lord": "Sun"}
    # No covering period and no usable 'current' block: None.
    assert p5._period_at({"mahadashas": [{"lord": "Sun", "start": "not-a-date",
                                          "end": "also-not-a-date"}]}, now) is None
    assert p5._period_at({"current": {"mahadasha": {"start": "2020-01-01"}}},
                         now) is None


def test_dasha_consensus_skips_uncovered_and_valueless_systems():
    # No system covers "now" and there is no 'current' fallback: the month
    # is skipped entirely, so the timeline is empty.
    bundle = {"planets": [], "dasha": {
        "mahadashas": [{"lord": "Sun", "start": "2010-01-01",
                        "end": "2016-01-01", "antardashas": []}]},
        "chara_dasha": {"periods": [{"sign_en": "Aries",
                                     "start": "2010-01-01",
                                     "end": "2016-01-01"}]}}
    c = p5.dasha_consensus(bundle, months=3)
    assert c["timeline"] == [] and c["highlights"] == []
    # A period covering now but carrying no lord/sign value is skipped too.
    bundle["dasha"] = {"mahadashas": [{"start": "2000-01-01",
                                       "end": "2100-01-01"}]}
    bundle["chara_dasha"] = {"periods": [{"start": "2000-01-01",
                                          "end": "2100-01-01"}]}
    assert p5.dasha_consensus(bundle, months=1)["timeline"] == []


def test_yoga_fructification_skips_yogas_without_planets():
    bundle = {"yogas": [{"name": "Nameless Yoga",
                         "basis": "A yoga whose basis names no planet."}],
              "dasha": {"mahadashas": []}}
    assert p5.yoga_fructification(bundle)["yogas"] == []


def test_yoga_fructification_skips_unparseable_dates():
    # MD dates that do not parse, and AD dates that do not parse, are
    # skipped — the yoga gets no activation windows and drops out.
    bundle = {
        "yogas": [{"name": "Gajakesari Yoga",
                   "basis": "Jupiter in kendra from Moon."}],
        "dasha": {"mahadashas": [
            {"lord": "Jupiter", "start": "garbage", "end": "garbage",
             "antardashas": []},
            {"lord": "Jupiter", "start": "2000-01-01", "end": "2100-01-01",
             "antardashas": [{"lord": "Moon", "start": "garbage",
                              "end": "garbage"}]},
        ]},
    }
    assert p5.yoga_fructification(bundle, years=5)["yogas"] == []


def test_ashtakavarga_gochar_without_sav():
    assert p5.ashtakavarga_gochar({}) == {"days": [], "note": "SAV unavailable."}
    # A short SAV list is just as unavailable as a missing one.
    assert p5.ashtakavarga_gochar(
        {"ashtakavarga": {"Sarvashtakavarga": [28] * 5}})["days"] == []
