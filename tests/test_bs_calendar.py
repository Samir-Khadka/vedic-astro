"""Phase 3 A2: Bikram Sambat conversion, anchored on independent sources."""
from datetime import date

from astro.bs_calendar import ad_to_bs, bs_to_ad, days_in_bs_month


def test_independent_anchors():
    # BS 2000-01-01 = AD 1943-04-14 (nepkit anchor, two sources).
    assert bs_to_ad(2000, 1, 1) == date(1943, 4, 14)
    # BS 2083 New Year, and Kartik 17 2083 = Nov 3 2026 (ICE converter,
    # nepal-date-kit example, both independent of nepkit).
    assert ad_to_bs(date(2026, 4, 14))["iso"] == "2083-01-01"
    assert ad_to_bs(date(2026, 4, 13))["iso"] == "2082-12-30"
    assert ad_to_bs(date(2026, 11, 3))["iso"] == "2083-07-17"
    assert ad_to_bs(date(2026, 11, 4))["iso"] == "2083-07-18"
    assert bs_to_ad(2081, 4, 15) == date(2024, 7, 30)
    # 2083 month lengths from nepal-date-kit: 31 31 32 31 31 31 30 29 30 29 30 30.
    assert [days_in_bs_month(2083, m) for m in range(1, 13)] == [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30]


def test_round_trip_and_range():
    for d in [date(1943, 4, 14), date(2000, 1, 1), date(2026, 11, 4), date(2034, 4, 13)]:
        bs = ad_to_bs(d)
        assert bs_to_ad(bs["year"], bs["month"], bs["day"]) == d
    for bad in [lambda: ad_to_bs(date(1943, 4, 13)),
                lambda: ad_to_bs(date(2034, 4, 14)),
                lambda: bs_to_ad(1999, 1, 1),
                lambda: bs_to_ad(2091, 1, 1),
                lambda: bs_to_ad(2083, 7, 31)]:
        try:
            bad()
        except ValueError:
            pass
        else:
            raise AssertionError("expected ValueError")


def test_nepali_formatting():
    bs = ad_to_bs(date(2026, 11, 4))
    assert bs["formatted_en"] == "18 Kartik 2083"
    assert bs["formatted_ne"] == "१८ कार्तिक २०८३"
