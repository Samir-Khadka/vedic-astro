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

from datetime import date
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, field_validator

from astro import engine, geocode, panchang as panchang_module, pdf as pdf_module, places as places_module, prashna as prashna_module

BASE = Path(__file__).resolve().parent
STATIC = BASE / "static"

app = FastAPI(title="Vedic Astro", version="1.0.0")


class BirthInput(BaseModel):
    name: str | None = None
    dob: str  # YYYY-MM-DD
    tob: str  # HH:MM or HH:MM:SS
    place_id: str | None = None
    place_name: str | None = None
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
    question: str | None = None
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


@app.get("/api/places")
def places(q: str = Query(default="")):
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
            d_from, d_to, place["lat"], place["lon"], place["tz"], activity,
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
        bundle = engine.compute_kundali(payload)
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


app.mount("/static", StaticFiles(directory=STATIC), name="static")
