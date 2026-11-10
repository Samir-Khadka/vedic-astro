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

from astro import bs_calendar as bs_calendar_module, engine, festivals as festivals_module, geocode, life_questions as life_questions_module, panchang as panchang_module, pdf as pdf_module, places as places_module, prashna as prashna_module

BASE = Path(__file__).resolve().parent
STATIC = BASE / "static"

app = FastAPI(title="Vedic Astro", version="1.0.0")


# --- Security: rate limiting + response headers --------------------------
# The heavy compute endpoints are unauthenticated and each costs real CPU
# (a full kundali bundle is ~0.6s warm; report.pdf renders a WeasyPrint
# PDF). A simple per-IP sliding-window limiter keeps one client from
# saturating the single free-tier worker. Limit via VEDIC_RL_LIMIT
# (requests per 60s per IP; default 60). /health and static are exempt.
# NOTE: keep this in sync with the endpoints that call
# engine.compute_kundali / compute_match / the WeasyPrint PDF renderers
# in main.py — every one of those is unauthenticated and heavy.
_RL_HEAVY_PATHS = {
    "/api/kundali", "/api/complete-report", "/api/match", "/api/prashna",
    "/api/life-areas", "/api/ask-astrologer",
    "/api/report.pdf", "/api/complete-report.pdf",
}
_RL_WINDOW_S = 60.0
_RL_BUCKETS: dict[str, deque] = {}


def _rl_is_heavy(method: str, path: str) -> bool:
    # HEAD is normalised to GET: a HEAD request to a GET endpoint must
    # never bypass the limiter for the heavier GET sibling.
    if method == "HEAD":
        method = "GET"
    if method not in ("GET", "POST"):
        return False
    if path in _RL_HEAVY_PATHS:
        return True
    # POST /api/life-questions/<id>/answer computes a full kundali, but
    # its path carries the question id, so no exact tuple can match it.
    return (method == "POST" and path.startswith("/api/life-questions/")
            and path.endswith("/answer"))


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
    if _rl_is_heavy(request.method, request.url.path) and not _rl_allowed(_rl_key(request)):
        return _security_headers(JSONResponse(
            {"detail": "rate limit exceeded; please slow down and retry"},
            status_code=429,
            headers={"Retry-After": "60"},
        ))
    return _security_headers(await call_next(request))


def _security_headers(response):
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
    """422 guard for the GET endpoints (query params skip pydantic models)
    and for raw place dicts (e.g. /api/ask-astrologer prashna mode), where
    the values arrive untyped JSON — a non-numeric lat/lon or a non-string
    tz must be a 422, not a TypeError 500 further down the call chain."""
    for v, lo, hi, name in ((lat, -90.0, 90.0, "lat"), (lon, -180.0, 180.0, "lon")):
        if v is not None:
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                raise HTTPException(status_code=422, detail=f"{name} must be a number")
            if not lo <= v <= hi:
                raise HTTPException(status_code=422, detail=f"{name} must be between {lo} and {hi}")
    if tz is not None:
        if not isinstance(tz, str):
            raise HTTPException(status_code=422, detail="tz must be a string")
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
    place_name: str | None = Field(default=None, max_length=200)
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


@app.post("/api/complete-report")
def complete_report(body: BirthInput):
    """Complete Kundali Report: the full legacy table-of-contents order
    (title, positions, panchang, charts, vargas, balas, dashas, Varshphal,
    predictions, doshas, Ratna-Mantra, Yantra) assembled from one kundali
    bundle. Accepts the same payload as /api/kundali."""
    from astro import complete_report as complete_report_module

    try:
        bundle = engine.compute_kundali(_payload(body))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return complete_report_module.build_complete_report(bundle)


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


@app.post("/api/life-questions/{question_id}/answer")
def life_question_answer(question_id: str, body: dict):
    """Answer a Life Question WITH a chart — the fix for the library's
    old dead-end buttons. Accepts either {"birth": <BirthInput>} or
    {"prashna": <PrashnaInput>}. 404 unknown id, 400 bad payload.
    Traditional probability guidance only; see astro/life_answers.py."""
    from astro import life_answers as life_answers_module
    from pydantic import ValidationError

    q = life_questions_module.get_question(question_id)
    if q is None:
        raise HTTPException(status_code=404, detail=f"unknown question: {question_id}")
    if not isinstance(body, dict):
        raise HTTPException(status_code=400, detail="body must be an object")
    try:
        if "birth" in body and body["birth"] is not None:
            birth = BirthInput.model_validate(body["birth"])
            bundle = engine.compute_kundali(_payload(birth))
            return life_answers_module.answer_from_birth(q, bundle)
        if "prashna" in body and body["prashna"] is not None:
            prashna_in = PrashnaInput.model_validate(body["prashna"])
            from datetime import datetime

            payload = prashna_in.model_dump()
            place = engine.resolve_place(payload)
            moment = datetime.now(ZoneInfo(place["tz"]))
            horary = prashna_module.horary(prashna_in.number, place, moment,
                                           prashna_in.question or "")
            return life_answers_module.answer_from_prashna(q, horary)
    except (ValidationError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    raise HTTPException(
        status_code=400,
        detail="provide either a 'birth' chart payload or a 'prashna' payload")


@app.post("/api/life-areas")
def life_areas(body: BirthInput):
    """Life Areas: the whole chart read area by area (8 areas, EN+NE).
    Accepts the same payload as /api/kundali. See astro/life_areas.py."""
    from astro import life_areas as life_areas_module

    try:
        bundle = engine.compute_kundali(_payload(body))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"areas": life_areas_module.analyse(bundle)}


@app.post("/api/ask-astrologer")
def ask_astrologer(body: dict):
    """AI Astrologer: answer a plain-language question from a real chart.

    Body: {"question": str (required, non-empty),
           "birth": <BirthInput dict> | None,
           "prashna_number": int (1-249) | None,
           "place": place dict (place_id or lat/lon/tz) | None,
           "lang": "en"|"ne" (default "en")}.
    Exactly one chart source is required: birth wins if present, else
    a prashna chart is cast for the current moment. No external service
    or LLM is ever called; see astro/ai_astrologer.py. 400 on any bad
    payload, missing source, or unresolvable place."""
    from datetime import datetime

    from pydantic import ValidationError

    from astro import ai_astrologer as ai_astrologer_module

    if not isinstance(body, dict):
        raise HTTPException(status_code=400, detail="body must be an object")
    question = body.get("question")
    if not isinstance(question, str) or not question.strip():
        raise HTTPException(status_code=400, detail="question must be a non-empty string")
    lang = body.get("lang", "en")
    if lang not in ("en", "ne"):
        raise HTTPException(status_code=400, detail="lang must be 'en' or 'ne'")
    try:
        if body.get("birth") is not None:
            birth = BirthInput.model_validate(body["birth"])
            bundle = engine.compute_kundali(_payload(birth))
            answer = ai_astrologer_module.build_answer(question, bundle, lang)
            answer["source"] = "birth"
        elif body.get("prashna_number") is not None:
            number = body["prashna_number"]
            if not isinstance(number, int) or isinstance(number, bool) or not 1 <= number <= 249:
                raise HTTPException(status_code=400, detail="prashna_number must be an integer between 1 and 249")
            place_dict = body.get("place")
            if not isinstance(place_dict, dict):
                raise HTTPException(status_code=400, detail="prashna mode requires a place (place_id or lat/lon/tz)")
            # The place dict is raw JSON, unlike BirthInput/PrashnaInput it
            # skips pydantic validation: an out-of-range lat/lon or an
            # unknown tz used to reach the ephemeris and surface as a 500.
            _validate_coords_tz(place_dict.get("lat"), place_dict.get("lon"),
                                place_dict.get("tz"))
            place = engine.resolve_place(place_dict)
            moment = datetime.now(ZoneInfo(place["tz"]))
            horary = prashna_module.horary(number, place, moment, question)
            answer = ai_astrologer_module.build_answer(question, horary, lang)
            answer["source"] = "prashna"
        else:
            raise HTTPException(
                status_code=400,
                detail="provide either a 'birth' chart payload or a 'prashna_number' with a place")
    except HTTPException:
        raise
    except (ValidationError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    answer["question"] = question
    return answer


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



@app.get("/api/bs")
def bs_convert(
    date_str: str | None = Query(default=None, alias="date", max_length=32),
    bs: str | None = Query(default=None, max_length=32),
):
    """BS <-> AD conversion. Give ?date=YYYY-MM-DD for AD->BS, or
    ?bs=YYYY-MM-DD (BS) for BS->AD. Out-of-range dates return 400."""
    try:
        if bs is not None:
            y, m, d = (int(x) for x in bs.split("-"))
            return bs_calendar_module.bs_date_dict(y, m, d)
        day = date.fromisoformat(date_str) if date_str else date.today()
        return bs_calendar_module.ad_to_bs(day)
    except (ValueError, TypeError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/panchang")
def panchang(
    date_str: str = Query(default=None, alias="date", max_length=32),
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


@app.get("/api/panchang-detail")
def panchang_detail(
    date_str: str = Query(default=None, alias="date", max_length=32),
    place_id: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    tz: str | None = None,
):
    """Full patro day detail for one date: rise/set times, tithi /
    nakshatra / yoga / karana with their transitions to the next one,
    moon sign, ritu, ayana and sidereal planet positions at sunrise.
    Additive only — month endpoints are untouched so month loads stay
    fast. 400 on a bad date."""
    _validate_coords_tz(lat, lon, tz)
    try:
        place = engine.resolve_place({"place_id": place_id, "lat": lat, "lon": lon, "tz": tz})
        day = date.fromisoformat(date_str) if date_str else date.today()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    result = panchang_module.day_detail(day, place["lat"], place["lon"], place["tz"])
    result["place"] = place
    # Additive: festivals/holidays for this day (computed from the
    # same sunrise tithi + lunar-cycle rule as the month grids).
    result["festivals"] = festivals_module.festivals_for_day(
        day, place["lat"], place["lon"], place["tz"],
        sunrise_tithi=result["tithi_index"], sun_sign=result["sun_sign"])
    return result


@app.get("/api/muhurta")
def muhurta(
    date_from: str = Query(default=None, max_length=16),
    date_to: str = Query(default=None, max_length=16),
    activity: str = "marriage",
    facing: str = "any",
    place_id: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    tz: str | None = None,
    birth_nakshatra: int | None = Query(default=None, ge=0, le=26),
    birth_moon_sign: int | None = Query(default=None, ge=0, le=11),
    birth_dob: str | None = Query(default=None, max_length=16),
    birth_tob: str | None = Query(default=None, max_length=16),
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
    if activity not in muhurta_module.ACTIVITIES:
        # The module silently falls back to "marriage" for unknown names
        # while echoing the caller's value — a typo'd activity would get
        # marriage scores labelled as the typo. Reject it instead.
        raise HTTPException(status_code=400, detail=f"unknown activity: {activity}")
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
    date_str: str = Query(default=None, alias="date", max_length=32),
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
    # Additive: a `festivals` list per day (month_panchang's own
    # shape is untouched); computed from the already-computed
    # per-day tithi/sun-sign, plus a short lookback for rules that
    # depend on neighbouring days.
    festivals_module.attach_festivals(result["days"], place["lat"], place["lon"], place["tz"])
    return result


@app.get("/api/bs-month")
def bs_month(
    bs_year: int, bs_month: int,
    place_id: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    tz: str | None = None,
):
    """Nepali-calendar month: every BS day with its AD date, weekday and
    tithi/nakshatra (computed exactly like /api/panchang-month, same place
    handling and defaults). Year/month are validated by hand so bad values
    return 400, not FastAPI's 422. Additive only — no existing shape changes."""
    _validate_coords_tz(lat, lon, tz)
    try:
        month_length = bs_calendar_module.days_in_bs_month(bs_year, bs_month)
        place = engine.resolve_place({"place_id": place_id, "lat": lat, "lon": lon, "tz": tz})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    from datetime import timedelta as _timedelta

    from astro.ephemeris import sun_moon_longitudes as _sun_moon, to_julian_day as _to_jd
    from datetime import datetime as _datetime, time as _time

    days = []
    prev_sun_sign = None
    # Sankranti for the first BS day compares against the previous AD day.
    first_ad = bs_calendar_module.bs_to_ad(bs_year, bs_month, 1)
    prev_ad = first_ad - _timedelta(days=1)
    _sun, _ = _sun_moon(_to_jd(_datetime.combine(prev_ad, _time(12, 0), tzinfo=ZoneInfo(place["tz"]))))
    prev_sun_sign = int(_sun // 30.0)
    for d in range(1, month_length + 1):
        ad = bs_calendar_module.bs_to_ad(bs_year, bs_month, d)
        p = panchang_module.daily_panchang(ad, place["lat"], place["lon"], place["tz"])
        sun, _moon = _sun_moon(_to_jd(_datetime.combine(ad, _time(12, 0), tzinfo=ZoneInfo(place["tz"]))))
        sun_sign = int(sun // 30.0)
        markers = []
        if p["tithi_index"] in (10, 25):
            markers.append("Ekadashi")
        if p["tithi_index"] == 14:
            markers.append("Purnima")
        if p["tithi_index"] == 29:
            markers.append("Amavasya")
        if sun_sign != prev_sun_sign:
            markers.append("Sankranti")
        prev_sun_sign = sun_sign
        days.append({
            "bs_year": bs_year, "bs_month": bs_month, "bs_day": d,
            "bs": f"{bs_year}-{bs_month:02d}-{d:02d}",
            "ad": ad.isoformat(), "date": ad.isoformat(),
            "weekday": ad.weekday(),
            "tithi_index": p["tithi_index"], "nakshatra_index": p["nakshatra_index"],
            "sun_sign": sun_sign, "markers": markers,
        })
    return {"bs_year": bs_year, "bs_month": bs_month, "month_length": month_length,
            "place": place, "days": festivals_module.attach_festivals(
                days, place["lat"], place["lon"], place["tz"])}


@app.get("/api/bs-month-length")
def bs_month_length(bs_year: int, bs_month: int):
    """Cheap month-length lookup for the BS date-entry widget (no ephemeris
    work, unlike /api/bs-month). 400 on out-of-range year/month."""
    try:
        length = bs_calendar_module.days_in_bs_month(bs_year, bs_month)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"bs_year": bs_year, "bs_month": bs_month, "month_length": length}


@app.get("/api/report.pdf")
def report_pdf(
    dob: str, tob: str,
    place_id: str | None = None,
    place_name: str | None = Query(default=None, max_length=200),
    lat: float | None = None, lon: float | None = None, tz: str | None = None,
    name: str | None = Query(default=None, max_length=200), lang: str = "en",
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


@app.get("/api/complete-report.pdf")
def complete_report_pdf(
    dob: str, tob: str,
    place_id: str | None = None,
    place_name: str | None = Query(default=None, max_length=200),
    lat: float | None = None, lon: float | None = None, tz: str | None = None,
    name: str | None = Query(default=None, max_length=200), lang: str = "en",
    ayanamsa: str | None = None, house_system: str | None = None,
    model: str = "detailed",
):
    """Downloadable PDF of the Complete Kundali Report (all 31 sections
    in legacy order for detailed/book, 9 sections for basic). Mirrors
    /api/report.pdf's parameter style; renders via astro/complete_pdf.py
    (WeasyPrint primary, fpdf2 + vendored Devanagari fallback)."""
    from astro import complete_pdf as complete_pdf_module
    from astro import complete_report as complete_report_module

    payload = {
        "name": name, "dob": dob, "tob": tob if len(tob) > 5 else tob + ":00",
        "place_id": place_id, "place_name": place_name, "lat": lat, "lon": lon, "tz": tz,
        "ayanamsa": ayanamsa, "house_system": house_system,
    }
    _validate_coords_tz(lat, lon, tz)
    if model not in ("detailed", "basic", "book"):
        raise HTTPException(status_code=400, detail=f"unknown model: {model}")
    try:
        bundle = engine.compute_kundali(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    report = complete_report_module.build_complete_report(bundle)
    try:
        pdf_bytes = complete_pdf_module.render_complete_pdf(
            report, lang="ne" if lang == "ne" else "en", model=model)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=vedic-complete-report.pdf"},
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
