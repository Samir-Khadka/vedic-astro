"""Ayanamsa regression tests — Lahiri must hold in EVERY thread.

Background (bug found live 2026-10-23): pyswisseph stores the sidereal
mode in thread-local state. astro/ephemeris set SIDM_LAHIRI once at
import (main thread), but FastAPI/uvicorn serve sync endpoints from a
threadpool whose threads defaulted to Fagan-Bradley, shifting every
production longitude by -0.8832 deg (live Sun 28.3266 vs Lahiri
29.2098 for the sample chart). These tests pin the published Lahiri
values and reproduce the production threading context so the bug
cannot return silently.
"""
import json
import socket
import subprocess
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import swisseph as swe

from astro import engine, ephemeris

SAMPLE = {"name": "Sample", "dob": "1998-05-14", "tob": "06:30:00", "place_id": "kathmandu"}
# Golden Lahiri longitudes for the sample chart (Swiss Ephemeris,
# SIDM_LAHIRI, cross-checked against raw swe calls in test_engine.py).
GOLDEN = {"Sun": 29.2098, "Moon": 236.7822}
GOLDEN_LAGNA = 48.2062


def test_ayanamsa_matches_published_lahiri_values():
    # 1998-05-14 00:45 UT — published Lahiri ayanamsa 23.8342 deg.
    jd = swe.julday(1998, 5, 14, 0.75)
    assert abs(ephemeris.ayanamsa_ut(jd) - 23.8342) < 0.002
    # 2000-01-01 00:00 UT — published Lahiri ayanamsa 23.8571 deg.
    jd2 = swe.julday(2000, 1, 1, 0.0)
    assert abs(ephemeris.ayanamsa_ut(jd2) - 23.8571) < 0.002


def test_worker_thread_computes_lahiri_not_fagan_bradley():
    """Reproduces FastAPI's threadpool execution: the whole kundali is
    computed in a worker thread, where the import-time set_sid_mode
    never ran. Before the fix this returned Fagan-Bradley longitudes."""
    jd = swe.julday(1998, 5, 14, 0.75)

    def work():
        ay = ephemeris.ayanamsa_ut(jd)
        bundle = engine.compute_kundali(SAMPLE)
        return ay, bundle

    with ThreadPoolExecutor(max_workers=1) as ex:
        ay, bundle = ex.submit(work).result(timeout=60)

    assert abs(ay - 23.8342) < 0.002
    by_name = {p["planet"]: p for p in bundle["planets"]}
    for planet, golden in GOLDEN.items():
        assert abs(by_name[planet]["longitude"] - golden) < 0.01, planet
    assert abs(bundle["lagna"]["longitude"] - GOLDEN_LAGNA) < 0.01


def _free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def test_uvicorn_server_end_to_end_lahiri():
    """The exact production shape: a real uvicorn process serving a
    real HTTP request from its threadpool. Guards the original bug
    end-to-end rather than by analogy."""
    root = Path(__file__).resolve().parent.parent
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app",
         "--host", "127.0.0.1", "--port", str(port)],
        cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        base = f"http://127.0.0.1:{port}"
        deadline = time.time() + 30
        while True:
            try:
                with urllib.request.urlopen(base + "/health", timeout=2) as r:
                    if r.status == 200:
                        break
            except Exception:
                if time.time() > deadline:
                    raise RuntimeError("uvicorn did not come up in 30s")
                time.sleep(0.3)
        payload = json.dumps(SAMPLE).encode()
        req = urllib.request.Request(
            base + "/api/kundali", data=payload,
            headers={"Content-Type": "application/json"}, method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            bundle = json.loads(r.read().decode())
        by_name = {p["planet"]: p for p in bundle["planets"]}
        assert abs(by_name["Sun"]["longitude"] - GOLDEN["Sun"]) < 0.01
        assert abs(by_name["Moon"]["longitude"] - GOLDEN["Moon"]) < 0.01
        assert abs(bundle["lagna"]["longitude"] - GOLDEN_LAGNA) < 0.01
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
