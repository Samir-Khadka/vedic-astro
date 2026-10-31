"""Phase 1 tests — classical calculation core.

Ayanamsa selection, house systems, the six BPHS special lagnas and the
six upagrahas. Reference values are derived from the classical formulas
(BPHS Ch. 5; JHora/P.V.R. Narasimha Rao for Shri Lagna; the weekday
Gulika segment tables), cross-checked against published worked examples.
"""
import threading

import pytest

from astro import ayanamsa, ephemeris, special_lagnas, upagrahas


# ---------- ayanamsa ----------

def test_default_ayanamsa_is_lahiri():
    assert ayanamsa.current_ayanamsa() == "lahiri"
    assert ayanamsa.validate_ayanamsa(None) == "lahiri"


def test_invalid_ayanamsa_rejected():
    with pytest.raises(ValueError):
        ayanamsa.validate_ayanamsa("fagan")


def test_ayanamsa_changes_longitudes():
    jd = ephemeris.to_julian_day(
        ephemeris.make_local_datetime(
            __import__("datetime").date(1998, 5, 14),
            __import__("datetime").time(6, 30),
            "Asia/Kathmandu"))
    ayanamsa.set_ayanamsa("lahiri")
    sun_lahiri = ephemeris.planet_longitudes(jd)["Sun"]["longitude"]
    ayanamsa.set_ayanamsa("raman")
    sun_raman = ephemeris.planet_longitudes(jd)["Sun"]["longitude"]
    # Raman ayanamsa is ~1.4 deg smaller than Lahiri in this era, so its
    # sidereal longitudes are larger (Swiss Ephemeris values).
    assert 1.0 < sun_raman - sun_lahiri < 2.0
    ayanamsa.set_ayanamsa("lahiri")
    assert abs(ephemeris.planet_longitudes(jd)["Sun"]["longitude"] - sun_lahiri) < 1e-9


def test_ayanamsa_is_thread_local():
    # A mode set in one thread must not leak into another (the 2026-10-23
    # worker-thread bug class).
    ayanamsa.set_ayanamsa("lahiri")
    seen = {}

    def worker():
        ayanamsa.set_ayanamsa("raman")
        seen["worker"] = ayanamsa.current_ayanamsa()

    t = threading.Thread(target=worker)
    t.start(); t.join()
    assert seen["worker"] == "raman"
    assert ayanamsa.current_ayanamsa() == "lahiri"


# ---------- house systems ----------

def test_house_system_validation():
    assert ephemeris.validate_house_system(None) == "placidus"
    with pytest.raises(ValueError):
        ephemeris.validate_house_system("koch")


def test_placidus_default_unchanged():
    jd = ephemeris.to_julian_day(
        ephemeris.make_local_datetime(
            __import__("datetime").date(1998, 5, 14),
            __import__("datetime").time(6, 30),
            "Asia/Kathmandu"))
    assert ephemeris.house_cusps(jd, 27.7, 85.3, "placidus") == \
        ephemeris.placidus_cusps(jd, 27.7, 85.3)


def test_equal_house_cusps():
    jd = ephemeris.to_julian_day(
        ephemeris.make_local_datetime(
            __import__("datetime").date(1998, 5, 14),
            __import__("datetime").time(6, 30),
            "Asia/Kathmandu"))
    cusps = ephemeris.house_cusps(jd, 27.7, 85.3, "equal")
    lagna = ephemeris.ascendant(jd, 27.7, 85.3)
    assert len(cusps) == 12
    assert abs(cusps[0] - lagna) < 1e-6
    for i in range(12):
        assert abs(((cusps[i] - cusps[0]) % 360) - i * 30) < 1e-6


def test_whole_sign_cusps():
    jd = ephemeris.to_julian_day(
        ephemeris.make_local_datetime(
            __import__("datetime").date(1998, 5, 14),
            __import__("datetime").time(6, 30),
            "Asia/Kathmandu"))
    cusps = ephemeris.house_cusps(jd, 27.7, 85.3, "whole")
    lagna = ephemeris.ascendant(jd, 27.7, 85.3)
    lagna_sign = int(lagna // 30)
    assert len(cusps) == 12
    for i in range(12):
        assert abs(cusps[i] - ((lagna_sign + i) * 30 % 360)) < 1e-6


def test_sripati_cusps_sane():
    jd = ephemeris.to_julian_day(
        ephemeris.make_local_datetime(
            __import__("datetime").date(1998, 5, 14),
            __import__("datetime").time(6, 30),
            "Asia/Kathmandu"))
    cusps = ephemeris.house_cusps(jd, 27.7, 85.3, "sripati")
    assert len(cusps) == 12
    assert all(0.0 <= c < 360.0 for c in cusps)


# ---------- special lagnas ----------

def test_varnada_nehru_example():
    # Published example: Lagna Cancer (even), Hora Lagna Pisces (even)
    # -> A=9, B=1, C=10 -> count 10 back from Pisces = Gemini (index 2).
    assert special_lagnas.varnada_sign(3, 11) == 2


def test_varnada_odd_lagna():
    # Lagna Aries (odd, A=1), Hora Lagna Leo (odd, B=5): same parity -> 6,
    # count 6 forward from Aries = Virgo (index 5).
    assert special_lagnas.varnada_sign(0, 4) == 5


def test_shri_lagna_worked_example():
    # Published example: Moon 13 Li 06 (193.1 deg, Swati), Lagna 25 Vi 05
    # (175.083 deg) -> Shri Lagna 18 Pi 47 (348.78 deg).
    sl = special_lagnas.shri_lagna_longitude(175.083, 193.1)
    assert abs(sl - 348.78) < 0.05


def test_indu_lagna():
    # Lagna Aries: 9th lord Jupiter (10 kalas). Moon Taurus: 9th lord
    # Saturn (1 kala). Total 11 -> count 11 from Taurus = Pisces (11),
    # keeping the Moon's degree in sign.
    sign, lon = special_lagnas.indu_lagna(0, 1, 15.5)
    assert sign == 11
    assert abs(lon - (11 * 30 + 15.5)) < 1e-9


def test_sunrise_trio_rates():
    # The trio advances at 6 / 12 / 30 deg per ghati from the sunrise Sun.
    from datetime import date, time
    birth = ephemeris.make_local_datetime(date(1998, 5, 14), time(12, 0), "Asia/Kathmandu")
    udaya, ghatis = special_lagnas._udaya_and_ghatis(birth, 27.7172, 85.3240, "Asia/Kathmandu")
    trio = special_lagnas.hora_bhava_ghati(birth, 27.7172, 85.3240, "Asia/Kathmandu")
    assert abs(trio["bhava_lagna"] - (udaya + ghatis * 6) % 360) < 1e-6
    assert abs(trio["hora_lagna"] - (udaya + ghatis * 12) % 360) < 1e-6
    assert abs(trio["ghati_lagna"] - (udaya + ghatis * 30) % 360) < 1e-6
    # Midday birth in May: several ghatis after sunrise.
    assert ghatis > 5


# ---------- upagrahas ----------

def test_solar_upagraha_formulas():
    u = upagrahas.solar_upagrahas(100.0)
    assert abs(u["dhuma"] - 233.3333) < 1e-3
    assert abs(u["vyatipata"] - (360 - 233.3333)) < 1e-3
    assert abs(u["parivesha"] - ((360 - 233.3333 + 180) % 360)) < 1e-3
    assert abs(u["indrachapa"] - (360 - u["parivesha"]) % 360) < 1e-3
    assert abs(u["upaketu"] - 130.0) < 1e-9


def test_gulika_day_segments():
    # Sunday -> 7th segment, Saturday -> 1st, Monday -> 6th.
    assert upagrahas.DAY_GULIKA_SEGMENT[6] == 7  # Sunday
    assert upagrahas.DAY_GULIKA_SEGMENT[5] == 1  # Saturday
    assert upagrahas.DAY_GULIKA_SEGMENT[0] == 6  # Monday


def test_gulika_mandi_longitudes():
    from datetime import date, time
    birth = ephemeris.make_local_datetime(date(1998, 5, 14), time(6, 30), "Asia/Kathmandu")
    rise, set_ = ephemeris.sunrise_sunset(date(1998, 5, 14), 27.7172, 85.3240, "Asia/Kathmandu")
    gm = upagrahas.gulika_mandi(birth, rise, set_, 27.7172, 85.3240)
    assert gm["gulika"] is not None and gm["mandi"] is not None
    assert 0.0 <= gm["gulika"]["longitude"] < 360.0
    assert 0.0 <= gm["mandi"]["longitude"] < 360.0


# ---------- engine integration ----------

def _payload(**kw):
    p = {"name": "T", "dob": "1998-05-14", "tob": "06:30:00",
         "lat": 27.7172, "lon": 85.3240, "tz": "Asia/Kathmandu"}
    p.update(kw)
    return p


def test_engine_phase1_bundle():
    from astro import engine
    b = engine.compute_kundali(_payload())
    assert b["ayanamsa"] == {"key": "lahiri", "name": "Lahiri (Chitrapaksha)"}
    assert b["house_system"]["key"] == "placidus"
    assert len(b["house_cusps"]) == 12
    assert set(b["classical_lagnas"]) == {"hora_lagna", "bhava_lagna", "ghati_lagna",
                                          "varnada_lagna", "shri_lagna", "indu_lagna"}
    assert set(b["upagrahas"]) == {"dhuma", "vyatipata", "parivesha", "indrachapa",
                                   "upaketu", "gulika", "mandi"}
    assert b["upagrahas"]["gulika"] is not None


def test_engine_ayanamsa_flows_through():
    from astro import engine
    b = engine.compute_kundali(_payload(ayanamsa="krishnamurti"))
    assert b["ayanamsa"]["key"] == "krishnamurti"
    b2 = engine.compute_kundali(_payload())
    sun_kp = next(p for p in b["planets"] if p["planet"] == "Sun")["longitude"]
    sun_def = next(p for p in b2["planets"] if p["planet"] == "Sun")["longitude"]
    assert abs(sun_kp - sun_def) > 0.01


def test_engine_bad_params_rejected():
    from astro import engine
    with pytest.raises(ValueError):
        engine.compute_kundali(_payload(ayanamsa="bogus"))
    with pytest.raises(ValueError):
        engine.compute_kundali(_payload(house_system="bogus"))


def test_kp_always_placidus():
    from astro import engine
    b_plac = engine.compute_kundali(_payload(house_system="placidus"))
    b_eq = engine.compute_kundali(_payload(house_system="equal"))
    cusps_plac = [c["longitude"] for c in b_plac["kp"]["cusps"]]
    cusps_eq = [c["longitude"] for c in b_eq["kp"]["cusps"]]
    assert cusps_plac == cusps_eq
    # ...while the bhava cusps do change with the selection.
    assert [c["longitude"] for c in b_plac["house_cusps"]] != \
        [c["longitude"] for c in b_eq["house_cusps"]]
