"""Vedic Astro API — FastAPI surface over the astro engine.

Endpoints:
  POST /api/kundali    full chart bundle incl. premium report (en+ne)
  POST /api/match      Ashtakoota Guna Milan for two births
  GET  /api/panchang   daily panchang (?date=YYYY-MM-DD&place_id=..|lat&lon&tz)
  GET  /api/places     gazetteer search (?q=)
  GET  /api/report.pdf downloadable premium report PDF
  GET  /health
The static single-page frontend is served from /static and /.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from astro import engine, panchang as panchang_module, pdf as pdf_module, places as places_module

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


class MatchInput(BaseModel):
    groom: BirthInput
    bride: BirthInput


def _payload(b: BirthInput) -> dict:
    d = b.model_dump()
    if d.get("tob") and len(d["tob"]) == 5:
        d["tob"] = d["tob"] + ":00"
    return d


@app.get("/health")
def health():
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
        return engine.compute_match(_payload(body.groom), _payload(body.bride))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/places")
def places(q: str = Query(default="")):
    return {"places": places_module.search_places(q)}


@app.get("/api/panchang")
def panchang(
    date_str: str = Query(default=None, alias="date"),
    place_id: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    tz: str | None = None,
):
    payload = {"place_id": place_id, "lat": lat, "lon": lon, "tz": tz}
    try:
        place = engine.resolve_place(payload)
        day = date.fromisoformat(date_str) if date_str else date.today()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    result = panchang_module.daily_panchang(day, place["lat"], place["lon"], place["tz"])
    result["place"] = place
    return result


@app.get("/api/report.pdf")
def report_pdf(
    dob: str, tob: str,
    place_id: str | None = None,
    lat: float | None = None, lon: float | None = None, tz: str | None = None,
    name: str | None = None, lang: str = "en",
):
    payload = {
        "name": name, "dob": dob, "tob": tob if len(tob) > 5 else tob + ":00",
        "place_id": place_id, "lat": lat, "lon": lon, "tz": tz,
    }
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
