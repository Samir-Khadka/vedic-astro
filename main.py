"""Vedic Astro API — FastAPI surface over the astro engine.

Endpoints:
  POST /api/kundali    full chart bundle incl. premium report (en+ne)
  POST /api/match      Ashtakoota Guna Milan for two births
  GET  /api/panchang   daily panchang (?date=YYYY-MM-DD&place_id=..|lat&lon&tz)
  GET  /api/places     place search (?q=) — built-in gazetteer first, then
                       global OpenStreetMap results with IANA timezones;
                       body: {places: [...], global_available: bool}
  GET  /api/tz         offline timezone lookup (?lat=&lon=) -> {tz}
  GET  /api/report.pdf downloadable premium report PDF
  GET  /health
The static single-page frontend is served from /static and /.
"""
from __future__ import annotations

import os
import time
from collections import deque
from datetime import date
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

from astro import engine, geocode, life_questions as life_questions_module, panchang as panchang_module, pdf as pdf_module, places as places_module, prashna as prashna_module

BASE = Path(__file__).resolve().parent
STATIC = BASE / "static"

app = FastAPI(title="Vedic Astro", version="1.0.0")


# --- Security: rate limiting + response headers --------------------------
# The heavy compute endpoints are unauthenticated and each costs real CPU
# (a full kundali bundle is ~0.6s warm; report.pdf renders a WeasyPrint
# PDF). A simple per-IP sliding-window limiter keeps one client from
# saturating the single free-tier worker. Limit via VEDIC_RL_LIMIT
# (requests per 60s per IP; default 60). /health and static are exempt.
_RL_HEAVY = {("POST", "/api/kundali"), ("POST", "/api/match"),
             ("POST", "/api/prashna"), ("GET", "/api/report.pdf")}
_RL_WINDOW_S = 60.0
_RL_BUCKETS: dict[str, deque] = {}


def _rl_limit() -> int:
    try:
        return max(1, int(os.environ.get("VEDIC_RL_LIMIT", "60")))
    except ValueError:
        return 60


def _rl_key(request) -> str:
    # Behind Render, the real client IP is the first X-Forwarded-For entry.
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()[:64] or "unknown"
    client = request.client
    return client.host if client else "unknown"


def _rl_allowed(key: str) -> bool:
    now = time.monotonic()
    dq = _RL_BUCKETS.get(key)
    if dq is None:
        dq = _RL_BUCKETS[key] = deque()
    while dq and now - dq[0] > _RL_WINDOW_S:
        dq.popleft()
    if len(dq) >= _rl_limit():
        return False
    dq.append(now)
    if len(_RL_BUCKETS) > 8192:
        # Shed the stalest buckets so the map cannot grow unboundedly.
        stale = sorted(_RL_BUCKETS,
                       key=lambda k: _RL_BUCKETS[k][-1] if _RL_BUCKETS[k] else 0)
        for k in stale[:4096]:
            del _RL_BUCKETS[k]
    return True


@app.middleware("http")
async def security_middleware(request, call_next):
    if (request.method, request.url.path) in _RL_HEAVY and not _rl_allowed(_rl_key(request)):
        return JSONResponse(
            {"detail": "rate limit exceeded; please slow down and retry"},
            status_code=429,
            headers={"Retry-After": "60"},
        )
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


class BirthInput(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    dob: str  # YYYY-MM-DD
    tob: str  # HH:MM or HH:MM:SS
    place_id: str | None = None
    place_name: str | None = Field(default=None, max_length=200)
    lat: float | None = None
    lon: float | None = None
    tz: str | None = None
    ayanamsa: str | None = None  # lahiri (default), raman, krishnamurti, yukteshwar
    house_system: str | None = None  # placidus (default), equal, whole, sripati

    @field_validator("lat")
    @classmethod
    def _lat_in_range(cls, v: float | None) -> float | None:
        if v is not None and not -90.0 <= v <= 90.0:
            raise ValueError("lat must be between -90 and 90")
        return v

    @field_validator("lon")
    @classmethod
    def _lon_in_range(cls, v: float | None) -> float | None:
        if v is not None and not -180.0 <= v <= 180.0:
            raise ValueError("lon must be between -180 and 180")
        return v

    @field_validator("tz")
    @classmethod
    def _tz_is_real(cls, v: str | None) -> str | None:
        if v is not None:
            try:
                ZoneInfo(v)
            except Exception:
                raise ValueError(f"unknown IANA timezone: {v}")
        return v


def _validate_coords_tz(lat: float | None, lon: float | None, tz: str | None) -> None:
    """422 guard for the GET endpoints (query params skip pydantic models)."""
    if lat is not None and not -90.0 <= lat <= 90.0:
        raise HTTPException(status_code=422, detail="lat must be between -90 and 90")
    if lon is not None and not -180.0 <= lon <= 180.0:
        raise HTTPException(status_code=422, detail="lon must be between -180 and 180")
    if tz is not None:
        try:
            ZoneInfo(tz)
        except Exception:
            raise HTTPException(status_code=422, detail=f"unknown IANA timezone: {tz}")


class MatchInput(BaseModel):
    groom: BirthInput
    bride: BirthInput
    marriage_date: str | None = None  # YYYY-MM-DD, optional: enables Dasha Sandhi check


class PrashnaInput(BaseModel):
    number: int
    question: str | None = Field(default=None, max_length=500)
    place_id: str | None = None
    place_name: str | None = None
    lat: float | None = None
    lon: float | None = None
    tz: str | None = None

    @field_validator("number")
    @classmethod
    def _number_in_range(cls, v: int) -> int:
        if not 1 <= v <= 249:
            raise ValueError("horary number must be between 1 and 249")
        return v

    @field_validator("lat")
    @classmethod
    def _lat_in_range(cls, v: float | None) -> float | None:
        if v is not None and not -90.0 <= v <= 90.0:
            raise ValueError("lat must be between -90 and 90")
        return v

    @field_validator("lon")
    @classmethod
    def _lon_in_range(cls, v: float | None) -> float | None:
        if v is not None and not -180.0 <= v <= 180.0:
            raise ValueError("lon must be between -180 and 180")
        return v

    @field_validator("tz")
    @classmethod
    def _tz_is_real(cls, v: str | None) -> str | None:
        if v is not None:
            try:
                ZoneInfo(v)
            except Exception:
                raise ValueError(f"unknown IANA timezone: {v}")
        return v


def _payload(b: BirthInput) -> dict:
    d = b.model_dump()
    if d.get("tob") and len(d["tob"]) == 5:
        d["tob"] = d["tob"] + ":00"
    return d


@app.get("/health")
@app.head("/health")
def health():
    # HEAD is explicit: UptimeRobot's free checks use HEAD, and Starlette
    # does not answer HEAD for a GET-only route (it returned 405, which
    # showed two live monitors as falsely Down).
    return {"status": "ok", "service": "vedic-astro"}


@app.post("/api/kundali")
def kundali(body: BirthInput):
    try:
        return engine.compute_kundali(_payload(body))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/match")
def match(body: MatchInput):
    try:
        return engine.compute_match(_payload(body.groom), _payload(body.bride),
                                   marriage_date=body.marriage_date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/prashna")
def prashna(body: PrashnaInput):
    """KP Horary (Prashna): the 1-249 number chart at the querent's place,
    cast for the current moment."""
    from datetime import datetime

    payload = body.model_dump()
    try:
        place = engine.resolve_place(payload)
        moment = datetime.now(ZoneInfo(place["tz"]))
        return prashna_module.horary(body.number, place, moment, body.question or "")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/life-questions")
def life_questions(category: str | None = Query(default=None, max_length=50)):
    """Curated Life Questions library (EN+NE guide, no verdict without a
    chart). Filter by category slug, e.g. ?category=marriage."""
    if category is not None and category not in {c["slug"] for c in life_questions_module.categories()}:
        raise HTTPException(status_code=400, detail=f"unknown category: {category}")
    return {
        "categories": life_questions_module.categories(),
        "questions": [life_questions_module.to_public(q)
                      for q in life_questions_module.list_questions(category)],
    }


@app.get("/api/life-questions/{question_id}")
def life_question(question_id: str):
    q = life_questions_module.get_question(question_id)
    if q is None:
        raise HTTPException(status_code=404, detail=f"unknown question: {question_id}")
    return life_questions_module.to_public(q)


@app.get("/api/places")
def places(q: str = Query(default="", max_length=200)):
    local = places_module.search_places(q)
    global_hits, global_available = geocode.search_global(q)
    local_names = {p["name"].lower() for p in local}
    merged = list(local)
    for g in global_hits:
        if g["name"].lower() in local_names:
            continue  # gazetteer entry already covers this place
        if any(abs(g["lat"] - p["lat"]) < 0.05 and abs(g["lon"] - p["lon"]) < 0.05 for p in local):
            continue
        merged.append(g)
    return {"places": merged, "global_available": global_available}


@app.get("/api/tz")
def tz_lookup(lat: float, lon: float):
    _validate_coords_tz(lat, lon, None)
    tz = geocode.timezone_at(lat, lon)
    if tz is None:
        raise HTTPException(status_code=422, detail="no timezone found for these coordinates")
    return {"tz": tz}


@app.get("/api/panchang")
def panchang(
    date_str: str = Query(default=None, alias="date"),
    place_id: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    tz: str | None = None,
):
    payload = {"place_id": place_id, "lat": lat, "lon": lon, "tz": tz}
    _validate_coords_tz(lat, lon, tz)
    try:
        place = engine.resolve_place(payload)
        day = date.fromisoformat(date_str) if date_str else date.today()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    result = panchang_module.daily_panchang(day, place["lat"], place["lon"], place["tz"])
    result["place"] = place
    return result


@app.get("/api/muhurta")
def muhurta(
    date_from: str = Query(default=None),
    date_to: str = Query(default=None),
    activity: str = "marriage",
    facing: str = "any",
    place_id: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    tz: str | None = None,
    birth_nakshatra: int | None = None,
    birth_moon_sign: int | None = None,
    birth_dob: str | None = None,
    birth_tob: str | None = None,
    birth_place_id: str | None = None,
    birth_lat: float | None = None,
    birth_lon: float | None = None,
    birth_tz: str | None = None,
):
    """Muhurta finder; optional birth_* params enable the personalised
    election (Chandra Bala needs birth_moon_sign; dasha suitability
    needs the full birth chart)."""
    from datetime import datetime as _dt
    from datetime import time as _time

    from astro import ephemeris as _eph
    from astro import dasha as _dasha
    from astro import muhurta as muhurta_module

    _validate_coords_tz(lat, lon, tz)
    _validate_coords_tz(birth_lat, birth_lon, birth_tz)
    if facing not in ("any", "east", "west", "north", "south"):
        raise HTTPException(status_code=400, detail=f"unknown facing: {facing}")
    try:
        place = engine.resolve_place({"place_id": place_id, "lat": lat, "lon": lon, "tz": tz})
        d_from = date.fromisoformat(date_from) if date_from else date.today()
        d_to = date.fromisoformat(date_to) if date_to else d_from
        dasha_tree = natal_planets = natal_lagna = None
        if birth_dob and birth_tob:
            bplace = engine.resolve_place({"place_id": birth_place_id, "lat": birth_lat,
                                           "lon": birth_lon, "tz": birth_tz})
            bdt = _eph.make_local_datetime(date.fromisoformat(birth_dob),
                                           _time.fromisoformat(birth_tob), bplace["tz"])
            bjd = _eph.to_julian_day(bdt)
            natal_planets = _eph.planet_longitudes(bjd)
            natal_lagna = int(_eph.ascendant(bjd, bplace["lat"], bplace["lon"], b"W") // 30.0)
            dasha_tree = _dasha.vimshottari_tree(bdt, natal_planets["Moon"]["longitude"])
            if birth_moon_sign is None:
                birth_moon_sign = natal_planets["Moon"]["sign"]
        result = muhurta_module.muhurta_range(
            d_from, d_to, place["lat"], place["lon"], place["tz"], activity, facing,
            birth_nakshatra, birth_moon_sign, dasha_tree, natal_planets, natal_lagna)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    result["place"] = place
    return result


@app.get("/api/horoscope")
def horoscope(
    sign: int = Query(ge=0, le=11),
    span: str = "daily",
    date_str: str = Query(default=None, alias="date"),
    tz: str = "Asia/Kathmandu",
):
    from astro import horoscope as horoscope_module

    try:
        day = date.fromisoformat(date_str) if date_str else date.today()
        ZoneInfo(tz)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ZoneInfoNotFoundError as e:
        # Unknown IANA names raise ZoneInfoNotFoundError (a KeyError, not a
        # ValueError) — without this it surfaced as a 500.
        raise HTTPException(status_code=400, detail=f"unknown IANA timezone: {tz}") from e
    try:
        return horoscope_module.horoscope(sign, span, day, tz)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/panchang-month")
def panchang_month(
    year: int, month: int = Query(ge=1, le=12),
    place_id: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    tz: str | None = None,
):
    _validate_coords_tz(lat, lon, tz)
    try:
        place = engine.resolve_place({"place_id": place_id, "lat": lat, "lon": lon, "tz": tz})
        result = panchang_module.month_panchang(year, month, place["lat"], place["lon"], place["tz"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    result["place"] = place
    return result


@app.get("/api/report.pdf")
def report_pdf(
    dob: str, tob: str,
    place_id: str | None = None,
    place_name: str | None = None,
    lat: float | None = None, lon: float | None = None, tz: str | None = None,
    name: str | None = None, lang: str = "en",
    ayanamsa: str | None = None, house_system: str | None = None,
):
    payload = {
        "name": name, "dob": dob, "tob": tob if len(tob) > 5 else tob + ":00",
        "place_id": place_id, "place_name": place_name, "lat": lat, "lon": lon, "tz": tz,
        "ayanamsa": ayanamsa, "house_system": house_system,
    }
    _validate_coords_tz(lat, lon, tz)
    try:
        # light=True: skip heavy Phase 5 consensus for faster PDF on free tier.
        bundle = engine.compute_kundali(payload, light=True)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    pdf_bytes = pdf_module.render_pdf(bundle, lang="ne" if lang == "ne" else "en")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=vedic-report.pdf"},
    )


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/sw.js")
def service_worker():
    # Served from the root so the worker's scope covers the whole app
    # (a worker under /static/ could only control /static/*).
    return FileResponse(STATIC / "sw.js", media_type="application/javascript")


app.mount("/static", StaticFiles(directory=STATIC), name="static")
