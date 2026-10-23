# Vedic Astro — ज्योतिष

A precision Vedic astrology web application: real astronomy (Swiss Ephemeris,
Lahiri / Chitrapaksha ayanamsa, sidereal zodiac) with the three classical
method layers the premium tools use — **Parashari**, **KP (Krishnamurti
Paddhati)** and **Jaimini** — plus a premium multi-chapter life report,
Kundali matching, daily panchang and PDF export. Fully bilingual:
**English + नेपाली (Nepali)** throughout the UI, names and predictions.

## Features

- **Kundali engine** — 9 grahas + Lagna from `pyswisseph`; D1 Rashi and
  divisional charts D2, D3, D4, D7, D9 (Navamsa), D10 (Dashamsa), D12, D16,
  D20, D24, D27, D30, D60; whole-sign houses (Parashari) and Placidus cusps
  (KP); retrograde, combustion and dignity (exalted / own / debilitated).
- **Vimshottari dasha** — full Mahadasha → Antardasha tree with exact dates
  and Pratyantardasha for the running period.
- **KP layer** — sign / star / sub / sub-sub lord for every planet and cusp,
  cuspal sub-lord table, house significators.
- **Jaimini** — chara karakas (Atmakaraka … Darakaraka).
- **Doshas** — Manglik (with cancellations), Kaal Sarp (all 12 types),
  Sade Sati phase, Pitra dosha patterns.
- **Ashtakavarga** — Bhinnashtakavarga + Sarvashtakavarga (337 bindus).
- **Yogas** — Pancha Mahapurusha, Gajakesari, Budha-Aditya, Chandra-Mangala,
  Kemadruma, Dhana and Raj yoga combinations, each with its factual basis.
- **Rule-based predictions** — generated only from computed facts (dasha-lord
  lordship/placement/dignity, strengths, gochar transits, house-lord themes),
  in English and Nepali.
- **Premium life report** — 8 chapters (Personality, Career, Finance,
  Marriage, Health, Education, Family & Home, Foreign Settlement), a 10-year
  favourable-period forecast, Varshphal annual charts (solar-return Lagna,
  Muntha, year lord) for 3 years, remedies (life/lucky/fortune gemstones,
  Rudraksha, beej mantra, dosha remedies) and lucky attributes.
- **PDF export** — the full premium report as a downloadable PDF
  (WeasyPrint; reportlab fallback).
- **Kundali matching** — Ashtakoota Guna Milan (36 points) with full
  koota-by-koota breakdown, Manglik comparison and bilingual verdict.
- **Panchang** — tithi, nakshatra, yoga, karana, vaara at sunrise, with
  sunrise/sunset, for any date and place.
- **Places** — built-in gazetteer of 51 cities (Nepal, India and world
  majors) or raw latitude/longitude/timezone input.

## Run it

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install pytest httpx   # only for tests
.venv/bin/uvicorn main:app --port 8077
# open http://localhost:8077
```

WeasyPrint needs the usual system libraries (Pango etc.) for the best PDF
output incl. Devanagari; without them the app automatically falls back to a
reportlab-generated English PDF.

## API

| Endpoint | Description |
|---|---|
| `POST /api/kundali` | `{name, dob, tob, place_id}` or `{..., lat, lon, tz}` → full bundle |
| `POST /api/match` | `{groom: {...}, bride: {...}}` → Guna Milan |
| `GET /api/panchang?date=&place_id=` | daily panchang |
| `GET /api/places?q=` | gazetteer search |
| `GET /api/report.pdf?dob=&tob=&place_id=&lang=` | premium report PDF |
| `GET /health` | service status |

## Tests

```bash
.venv/bin/python -m pytest -q
```

Golden-value and invariant tests cover the KP sub-lord math, dasha tiling
(9 mahadashas = 120 years), Ashtakavarga totals (337), a hand-computed
Guna Milan case (28/36), and cross-checks of the sample chart against raw
Swiss Ephemeris calls.

## Notes & limitations

- Mean node is used for Rahu/Ketu; whole-sign houses for Parashari and
  Placidus cusps for KP, per mainstream practice.
- Varshphal is a documented simplification of the Tajika annual system
  (solar-return Lagna + Muntha + Lagna-lord as year lord).
- Matching koota `detail` strings are English; all verdicts, names and UI
  text are fully bilingual.
- Astrology is offered for guidance and reflection; predictions are
  rule-based readings of a traditional system, not scientific claims.
