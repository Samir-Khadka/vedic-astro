"""Nepali festivals and public holidays (astro/festivals.py).

Sources named in each test:
- MOHA 2082: Government of Nepal, Ministry of Home Affairs, "List of
  Public Holidays, 2082 B.S. (2025/26 A.D.)", Nepal Gazette Part 5
  notice dated 2081/11/15 (BS dates below are the gazette's own).
- NPMC 2082/2083: Nepal Panchanga Nirnayak Bikas Samiti tika dates
  as reported in Nepali press (Dashain/Tihar sequences).
- Press/announced dates for Fagu Holi 2025 (hills 13 Mar, Terai
  14 Mar) and Chhath 2025 (main 27 Oct, Usha 28 Oct).

No date below comes from a calendar app; the engine computes each
one from its own sunrise/sunset/pradosh tithi plus the lunar-cycle
rule documented in astro/festivals.py.
"""

from datetime import date

from astro.festivals import festivals_for_day, festivals_for_days

LAT, LON, TZ = 27.7172, 85.3240, "Asia/Kathmandu"


def _keys(day):
    return sorted(e["key"] for e in festivals_for_day(day, LAT, LON, TZ))


def _holidays(day):
    return sorted(e["key"] for e in festivals_for_day(day, LAT, LON, TZ)
                  if e["holiday"])


def test_vijaya_dashami_two_years():
    # NPMC 2082: Vijaya Dashami 2 Oct 2025 (Ashwin 16, tika 11:53).
    # NPMC 2083: Vijaya Dashami 21 Oct 2026.
    assert _keys(date(2025, 10, 2)) == ["vijaya_dashami"]
    assert _keys(date(2026, 10, 21)) == ["vijaya_dashami"]


def test_ghatasthapana_two_years():
    # MOHA 2082: Ghatasthapana 22 Sep 2025 (Ashwin 6).
    # NPMC 2083: Ghatasthapana 11 Oct 2026 (Ashwin 25).
    assert _keys(date(2025, 9, 22)) == ["ghatasthapana"]
    assert _keys(date(2026, 10, 11)) == ["ghatasthapana"]


def test_laxmi_puja_two_years():
    # NPMC 2082: Laxmi Puja the evening of 20 Oct 2025 (Kartik 3,
    # same day as Kukur Tihar). NPMC 2083: Laxmi Puja 8 Nov 2026
    # (Kartik 22, same day as Kukur Tihar).
    assert _keys(date(2025, 10, 20)) == ["kukur_tihar", "laxmi_puja"]
    assert _keys(date(2026, 11, 8)) == ["kukur_tihar", "laxmi_puja"]


def test_tihar_sequence_2082():
    assert _keys(date(2025, 10, 19)) == ["kag_tihar"]
    assert _keys(date(2025, 10, 21)) == ["gai_tihar"]
    assert _keys(date(2025, 10, 22)) == ["govardhan_puja"]
    assert _keys(date(2025, 10, 23)) == ["bhai_tika"]
    # MOHA 2082 Tihar holiday runs Kartik 3-7; Kartik 7 (24 Oct)
    # is the extra day after Bhai Tika.
    assert _keys(date(2025, 10, 24)) == ["tihar_holiday"]


def test_tihar_sequence_2083():
    # MOHA 2083 Tihar holiday Kartik 22-26; Bhai Tika Kartik 25.
    assert _keys(date(2026, 11, 7)) == ["kag_tihar"]
    assert _keys(date(2026, 11, 9)) == ["gai_tihar"]
    assert _keys(date(2026, 11, 10)) == ["govardhan_puja"]
    assert _keys(date(2026, 11, 11)) == ["bhai_tika"]
    assert _keys(date(2026, 11, 12)) == ["tihar_holiday"]


def test_chhath_sequence():
    # Chhath 2025: Nahay 25 Oct, Kharna 26 Oct, Sandhya 27 Oct,
    # Usha 28 Oct. Chhath 2026: main 15 Nov (Kartik 29).
    assert _keys(date(2025, 10, 25)) == ["chhath_nahay"]
    assert _keys(date(2025, 10, 26)) == ["chhath_kharna"]
    assert _keys(date(2025, 10, 27)) == ["chhath_parwa"]
    assert _keys(date(2025, 10, 28)) == ["chhath_usha"]
    assert _keys(date(2026, 11, 15)) == ["chhath_parwa"]
    assert _keys(date(2026, 11, 16)) == ["chhath_usha"]


def test_purnima_prevailing_times():
    # Kojagrat: MOHA/NPMC 6 Oct 2025, 25 Oct 2026 (sunset Purnima).
    assert _keys(date(2025, 10, 6)) == ["kojagrat_purnima"]
    assert _keys(date(2026, 10, 25)) == ["kojagrat_purnima"]
    # Dhanya Purnima: MOHA 2082, 4 Dec 2025 (sunset Purnima).
    assert _keys(date(2025, 12, 4)) == ["dhanya_purnima", "udhauli",
                                       "yomari_punhi"]
    # Buddha Jayanti: MOHA 2082, 12 May 2025 (sunrise Purnima).
    assert _keys(date(2025, 5, 12)) == ["buddha_jayanti", "ubhauli"]
    # Janai Purnima: MOHA 2082, 9 Aug 2025 (sunrise Purnima).
    assert _keys(date(2025, 8, 9)) == ["janai_purnima"]


def test_holi_hills_and_terai():
    # MOHA 2082: Fagu Purnima 2 Mar 2026 (hills), Terai Holi 3 Mar.
    # Fagu 2025: hills 13 Mar, Terai 14 Mar (press/announced).
    assert _keys(date(2026, 3, 2)) == ["fagu_purnima"]
    assert _keys(date(2026, 3, 3)) == ["terai_holi"]
    assert _keys(date(2025, 3, 13)) == ["fagu_purnima"]
    assert _keys(date(2025, 3, 14)) == ["terai_holi"]


def test_shivaratri_two_years():
    # MOHA 2082: Maha Shivaratri 15 Feb 2026. Shivaratri 2025:
    # 26 Feb 2025 (sunset Chaturdashi in both years).
    assert _keys(date(2026, 2, 15)) == ["maha_shivaratri"]
    assert _keys(date(2025, 2, 26)) == ["maha_shivaratri"]


def test_other_tithi_festivals():
    # MOHA 2082 dates: Teej 26 Aug 2025, Gai Jatra 10 Aug 2025,
    # Janmashtami 16 Aug 2025, Indra Jatra 6 Sep 2025,
    # Jitiya 15 Sep 2025, Basanta Panchami 23 Jan 2026,
    # Ram Navami 27 Mar 2026, Gaura 31 Aug 2025,
    # Nag Panchami 29 Jul 2025.
    assert _keys(date(2025, 8, 26)) == ["teej"]
    assert _keys(date(2025, 8, 10)) == ["gai_jatra"]
    assert _keys(date(2025, 8, 16)) == ["krishna_janmashtami"]
    assert _keys(date(2025, 9, 6)) == ["indra_jatra"]
    assert _keys(date(2025, 9, 15)) == ["jitiya"]
    assert _keys(date(2026, 1, 23)) == ["basanta_panchami"]
    assert _keys(date(2026, 3, 27)) == ["ram_navami"]
    assert _keys(date(2025, 8, 31)) == ["gaura_parwa"]
    assert _keys(date(2025, 7, 29)) == ["nag_panchami"]


def test_fixed_public_holidays():
    # MOHA 2082 fixed BS dates, plus fixed AD dates in the gazette.
    assert "nepali_new_year" in _holidays(date(2025, 4, 14))
    assert "labour_day" in _holidays(date(2025, 5, 1))
    assert "republic_day" in _holidays(date(2025, 5, 29))
    assert "constitution_day" in _holidays(date(2025, 9, 19))
    assert "christmas" in _holidays(date(2025, 12, 25))
    assert "prithvi_jayanti" in _holidays(date(2026, 1, 11))
    assert "maghe_sankranti" in _holidays(date(2026, 1, 15))
    assert "martyrs_day" in _holidays(date(2026, 1, 30))
    assert "democracy_day" in _holidays(date(2026, 2, 19))
    assert "womens_day" in _holidays(date(2026, 3, 8))
    assert "tamu_lhosar" in _holidays(date(2025, 12, 30))


def test_scoped_holidays_carry_scope():
    entries = festivals_for_day(date(2025, 8, 10), LAT, LON, TZ)
    gai = [e for e in entries if e["key"] == "gai_jatra"][0]
    assert gai["holiday"] is True
    assert gai["scope_en"]  # Kathmandu Valley and Newar community
    assert gai["scope_ne"]
    entries = festivals_for_day(date(2026, 3, 2), LAT, LON, TZ)
    fagu = [e for e in entries if e["key"] == "fagu_purnima"][0]
    assert fagu["holiday"] is True
    assert fagu["scope_en"]


def test_day_with_no_festival_returns_empty():
    assert festivals_for_day(date(2026, 3, 21), LAT, LON, TZ) == []
    assert festivals_for_day(date(2026, 1, 19), LAT, LON, TZ) == []


def test_festivals_for_days_aligns_with_input():
    from astro.panchang import daily_panchang
    from astro.festivals import _noon_sun_sign

    days = [date(2025, 10, d) for d in range(19, 25)]
    infos = []
    for d in days:
        p = daily_panchang(d, LAT, LON, TZ)
        infos.append({"date": d, "tithi_index": p["tithi_index"],
                      "sun_sign": _noon_sun_sign(d, TZ)})
    results = festivals_for_days(infos, LAT, LON, TZ)
    assert len(results) == len(days)
    keys = [[e["key"] for e in r] for r in results]
    assert keys[0] == ["kag_tihar"]
    assert keys[1] == ["kukur_tihar", "laxmi_puja"]
    assert keys[2] == ["gai_tihar"]
    assert keys[3] == ["govardhan_puja"]
    assert keys[4] == ["bhai_tika"]
    assert keys[5] == ["tihar_holiday"]


# --- Endpoint wiring: both month responses carry festivals ---------

def _client():
    from fastapi.testclient import TestClient

    from main import app

    return TestClient(app)


def test_ad_month_response_carries_festivals():
    # AD October 2025 contains the whole Dashain/Tihar run.
    r = _client().get("/api/panchang-month",
                      params={"year": 2025, "month": 10,
                              "place_id": "kathmandu"})
    assert r.status_code == 200
    days = r.json()["days"]
    by_date = {d["date"]: [f["key"] for f in d["festivals"]]
               for d in days}
    assert by_date["2025-10-02"] == ["vijaya_dashami"]
    assert by_date["2025-10-20"] == ["kukur_tihar", "laxmi_puja"]
    assert by_date["2025-10-21"] == ["gai_tihar"]
    # Existing fields untouched.
    assert days[0]["tithi_index"] is not None
    assert days[0]["markers"] is not None


def test_bs_month_response_carries_festivals():
    # BS Ashwin 2082 (Sep/Oct 2025) contains Ghatasthapana and
    # Vijaya Dashami; BS Kartik 2082 contains Laxmi Puja.
    r = _client().get("/api/bs-month",
                      params={"bs_year": 2082, "bs_month": 6,
                              "place_id": "kathmandu"})
    assert r.status_code == 200
    days = r.json()["days"]
    by_bs = {d["bs"]: [f["key"] for f in d["festivals"]] for d in days}
    assert by_bs["2082-06-06"] == ["ghatasthapana"]
    assert by_bs["2082-06-16"] == ["vijaya_dashami"]
    r = _client().get("/api/bs-month",
                      params={"bs_year": 2082, "bs_month": 7,
                              "place_id": "kathmandu"})
    by_bs = {d["bs"]: [f["key"] for f in d["festivals"]]
             for d in r.json()["days"]}
    assert by_bs["2082-07-03"] == ["kukur_tihar", "laxmi_puja"]
    assert by_bs["2082-07-06"] == ["bhai_tika"]


def test_day_detail_response_carries_festivals():
    r = _client().get("/api/panchang-detail",
                      params={"date": "2025-10-20",
                              "place_id": "kathmandu"})
    assert r.status_code == 200
    festivals = r.json()["festivals"]
    assert sorted(f["key"] for f in festivals) == ["kukur_tihar",
                                                  "laxmi_puja"]
    laxmi = [f for f in festivals if f["key"] == "laxmi_puja"][0]
    assert laxmi["holiday"] is True
    assert laxmi["name_en"] == "Laxmi Puja"
    assert laxmi["name_ne"] == "लक्ष्मी पूजा"
