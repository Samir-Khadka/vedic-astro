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
  (WeasyPrint; fpdf2 + vendored Noto Sans Devanagari fallback, so the
  PDF stays in Nepali or English even without Pango).
- **Kundali matching** — Ashtakoota Guna Milan (36 points) with full
  koota-by-koota breakdown, Manglik comparison and bilingual verdict.
- **Panchang** — tithi, nakshatra, yoga, karana, vaara at sunrise, with
  sunrise/sunset, for any date and place.
- **Places** — built-in gazetteer of 51 cities (Nepal, India and world
  majors) or raw latitude/longitude/timezone input.
- **Muhurta Finder** — auspicious timing for 15 activities in English
  and Nepali: marriage, travel, business/trade, house construction,
  education, starting a job, buying a vehicle, naming, house entry
  (Grahapravesh, with east/west/north/south facing), shop inauguration,
  bride's entry, bride/groom selection, vehicle ceremony, planting and
  first ploughing. Each day shows Choghadiya, Hora, Rahu Kaal, Abhijit
  and a per-factor score with reasons (see "How Muhurta scoring works"
  below), plus personalised Chandra Bala, Panchaka, elected-Lagna and
  dasha-suitability checks when birth details are given.
- **KP Prashna (horary)** — pick a number 1–249 and cast the chart of
  the moment, with ruling planets and cuspal sub-lords.
- **Life Questions library** — 26 curated chart-reading guides in
  English and Nepali (marriage, education, career, travel, children,
  property, vehicle, health, general caution and litigation), each with
  prime/supporting/negating houses, significator, what to check and a
  timing note. Sensitive topics are included only as traditional
  probability indications, not guaranteed outcomes, with medical/legal
  disclaimers (see the library's disclaimer).
- **Lal Kitab & Numerology** — Lal Kitab remedies/planetary notes and
  a numerology profile, alongside the main chart.

## Run it

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install pytest httpx   # only for tests
.venv/bin/uvicorn main:app --port 8077
# open http://localhost:8077
```

WeasyPrint needs the usual system libraries (Pango etc.) for the best PDF
output incl. Devanagari; without them the app automatically falls back to
an fpdf2 PDF using the vendored Noto Sans Devanagari fonts in
`data/fonts/` (with uharfbuzz shaping), so the PDF stays in the requested
language. Only if those fonts are unavailable does it degrade to the
English-only reportlab path.

## Deployment

The live site runs on Render. `render.yaml` is the Blueprint for it
(Python web service, `uvicorn main:app --host 0.0.0.0 --port $PORT`,
health check at `/health`): connect it in the Render dashboard
("New + > Blueprint") to make the deployment reproducible instead of
dashboard-only. The health endpoint answers both GET and HEAD — the
free UptimeRobot checks use HEAD, and a GET-only route used to return
405 and show the service as falsely Down. GitHub Actions (`.github/workflows/ci.yml`)
runs the Python and JavaScript test suites on every push to main and
every pull request.

## API

| Endpoint | Description |
|---|---|
| `POST /api/kundali` | `{name, dob, tob, place_id}` or `{..., lat, lon, tz}` → full bundle |
| `POST /api/match` | `{groom: {...}, bride: {...}}` → Guna Milan |
| `GET /api/panchang?date=&place_id=` | daily panchang |
| `GET /api/places?q=` | gazetteer search |
| `GET /api/report.pdf?dob=&tob=&place_id=&lang=` | premium report PDF |
| `GET /api/muhurta?activity=&facing=&date_from=&date_to=&place_id=` | Muhurta Finder day scores and best days (facing: any/east/west/north/south, for Grahapravesh) |
| `POST /api/prashna` | `{number (1–249), question?, place_id}` → KP horary chart |
| `GET /api/life-questions?category=` | Life Questions library (EN+NE); `GET /api/life-questions/{id}` for one question |
| `GET /api/horoscope?sign=&span=&date=` | Moon-sign horoscope |
| `GET /api/panchang-month?year=&month=&place_id=` | month panchang |
| `GET /api/tz?lat=&lon=` | offline timezone lookup |
| `GET /api/bs?date=` or `?bs=` | Bikram Sambat ↔ AD conversion (BS 2000–2090 table, out-of-range → 400) |
| `GET /health` | service status |

## How Muhurta scoring works

Each civil day gets a **day score** for the chosen activity, built only
from factors shown to the user, with points:

- Weekday not allowed for the activity: **−2**
- Tithi on the activity's preferred list: **+1**; not on it: **−2**
  (activities without an explicit tithi list use the generic class
  instead: Rikta tithis 4/9/14/19/24/29: **−2**;
  Nanda/Jaya/Purna tithis: **+1**)
- Moon in a preferred nakshatra for the activity: **+2**; otherwise **0**
  (Grahapravesh uses the facing-specific list when a facing is chosen)
- Tara Bala, when a birth nakshatra is given: favourable taras
  2/4/6/8/9: **+2**; unfavourable: **−2**
- Grahapravesh lunar month (Amanta convention, named from the sidereal
  Sun sign at Purnima): Vaishakh, Jyeshtha, Magh or Phalguna: **+2**;
  any other lunar month: **−2**. The panchang response reports the
  month and its convention, so a Krishna-paksha date's one-month
  difference under Purnimanta is visible, not hidden.
- Abhijit on Wednesday is **flagged at 0 points**, not scored.

Day grades: **Excellent ≥ 4, Good ≥ 2, Average ≥ 0, otherwise Avoid.**
The personalised **election score** adds Chandra Bala, Panchaka, elected
Lagna strength and dasha suitability on top of the day score, with its
own grades (Excellent ≥ 6, Good ≥ 3, Average ≥ 0, otherwise Avoid).
`best` ranks by day score; `best_election` ranks by election score.
This is classical guidance with transparent reasons, not a pandit's
full election — lists vary slightly between traditions.

## Tests

```bash
.venv/bin/python -m pytest -q
```

Golden-value and invariant tests cover the KP sub-lord math, dasha tiling
(9 mahadashas = 120 years), Ashtakavarga totals (337), a hand-computed
Guna Milan case (28/36), and cross-checks of the sample chart against raw
Swiss Ephemeris calls.

## Notes & limitations

- True node is used for Rahu/Ketu (the convention Hamro Patro and
  Jagannatha Hora print in Nepali janma-patris); whole-sign houses for
  Parashari and Placidus cusps for KP, per mainstream practice.
- Varshphal is a documented simplification of the Tajika annual system
  (solar-return Lagna + Muntha + Lagna-lord as year lord).
- Matching koota `detail` strings are English; all verdicts, names and UI
  text are fully bilingual.
- Astrology is offered for guidance and reflection; predictions are
  rule-based readings of a traditional system, not scientific claims.
