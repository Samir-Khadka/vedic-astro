# Vedic Astro — REA-style competitor audit

**Date:** 2026-10-25 · **Scope:** research only, no code changed
**Our product:** Vedic Astro, live at https://vedic-astro-ggel.onrender.com, repo `~/workspace/vedic-astro/`
**Method (morluto/REA discipline):** public surfaces only — official feature lists, pricing/feature pages, free tiers, documentation and open-source READMEs. No logins, no paywall bypass, no paid-report content, no decompilation, no copied text. Every feature below is described in my own words; every competitor claim carries the public URL it was verified on. Store listings and marketing pages are claims by their vendors, not hands-on tests — treat prices and "free" labels as point-in-time (2026-10-25) and re-check before acting on them.

## 0. Baseline — what we already have (not re-audited as gaps)

16 vargas; Vimshottari + Yogini + Tribhagi + Chara dashas; KP sub-lords + Prashna horary (249-sub table); Shadbala + Bhava Bala + Vimshopaka; Lal Kitab (partial: 3 of 9 Rin detected); transit tables with ingress dates + double-transit; Ashtakavarga (Sarva 337); yogas; Ashtakoota Guna Milan; panchang (single-day); doshas (Manglik / Kaal Sarp / Sade Sati / Pitra); numerology; nakshatra name letters; combinatorial premium report + PDF; Nepali chart style (diamond + in-cell degrees); worldwide place search (Open-Meteo → Photon → Nominatim).

Two baseline corrections found while checking the code (not from competitors):

- **Varshphal already contains Muntha.** `astro/report.py` computes a solar-return chart, Muntha as natal Lagna advanced one sign per completed year, and year lord as lord of the annual (Varshphal) Lagna. The gap in §3.6 is therefore only the *full* Tajika layer (five-officer election, Tajika yogas, Sahams, Mudda dasha), not Muntha itself.
- **Gemstone/Rudraksha already exist in the report.** `astro/report.py` maps life/lucky/fortune stones and a Rudraksha mukhi per planet, with a safety rule that refuses the gemstone of a planet ruling the 6th/8th/12th houses. The gap in §3.12 is only a *standalone deep-dive* (finger/metal/weight/day, conflict rules, yantra), not the existence of gemstone guidance.
- **Sade Sati phase dates already exist for the current cycle.** `astro/interpret.py` reports the full span plus peak-phase start and setting-phase start from real sidereal Saturn ingresses. The only extension is a lifetime list of past/future cycles (§3.13, P2).
- **localStorage today holds only preferences.** `static/app.js` stores language (`vedic-astro-lang`) and chart style (`vedic-astro-style`) only — no saved charts and no shareable link (§3.10 confirmed).

## 1. Competitor profiles (what it is, free vs paid, source)

### 1.1 AstroSage — website + app (free core, paid human-prepared premium)

Free tier: birth chart with life predictions, Varshphal, dasha predictions, Sade Sati predictions, Mangal Dosha predictions, transit predictions, a comprehensive PDF, Lal Kitab life predictions and remedies, and a baby-name suggestion; classical calculations including Shadbala & Bhavbala, Ashtakavarga, all 16 divisional charts, Yogini & Chara dasha and Mangal Dosha; a KP section with cuspal charts, house and planet significators, ruling planets and 1–249 horary; a Lal Kitab section including its 36-year dasha; a Tajik Varshaphal section with Varsha chart, Muntha, Saham, Mudda Vimshottari dasha, Yogini dasha and Panchadhikari; horary; Ashtakoot + Mangal Dosha matching; and chart sharing as an image. Source: http://www.astrosage.com/freekundli/

Its app listing adds, in one place, the features that matter for this audit: Shadbala, Ashtakvarga *and Prastarashtakvarga*, Bhava Chalit chart, Vimshottari up to five levels plus Yogini, daily Panchang & Muhurat, Hora, Rahu Kaal, Choghadiya, Abhijit/Vijay Muhurta, and Moon-sign daily/weekly/monthly horoscopes. Source: https://www.appbrain.com/app/astrosage-kundli-ai-astrology/com.ojassoft.astrosage

Paid flagship — **Brihat Kundli** (listed at ₹996 against ₹3,999, 250+ pages, delivered by email within 24 hours and explicitly prepared by expert astrologers, i.e. partly a human service, not instant software): all systems in one (Vedic, Lal Kitab, Tajik, KP, KCIL, 4-Step, numerology), Shodashvarga, Ashtakvarga table, Chalit chart, 5-year Varshphal, Lal Kitab Teva type and debts, favourable periods, gemstone + yantra + Rudraksha suggestions, Ishta Devta, Vimshottari/Pratyantar/Jaimini/Yogini dashas, Raj Yogas and a "golden period", doshas with remedies, and Shubh Din & Muhurat. Sources: https://www.astrosage.com/pgads/brihat-horoscope.asp?prtnr_id=BRVFB&utm_id=6717258727041 · https://buy.astrosage.com/service/astrosage-brihat-horoscope?language=en&prtnr_id=BAFBH · https://www.astrosage.com/pdf/brihat-horoscope.pdf

**Where it beats us:** the deepest free KP + Tajika + Lal Kitab stack of any website checked, and Bhava Chalit + Prastara free. **Where we beat it:** bilingual EN/नेपाली parity, the Nepali diamond-with-degrees style, and a combinatorial report engine rather than a fixed template.

### 1.2 Clickastro — website + app (free core, paid in-depth reports)

Free report contents: Panchanga predictions (tithi, nakshatra, yoga, karana, weekday), dasha predictions, Bhava (house) predictions, yoga analysis, favourable periods, Graha Dosha with remedies, Ashtakavarga predictions and transit forecast. Source: https://www.clickastro.com/horoscope-by-date-of-birth-time

Paid flagship — **In-Depth Horoscope** (100+ pages, 40+ years, plus a Q&A section answering 15 personalised life questions): career/marriage/health/wealth guidance, dasha–bhukti timelines, remedies, divisional-chart insights (D9, D10 and more) and life-event timing. Source: https://www.clickastro.com/campaign/2025/in-depth/multi-micro-video-v2.php

App (free tier): free Janam Kundli, Kundli matching on Guna Milan plus dosha, Papasamya and Dasha Sandhi covering both north- and south-Indian methods, daily horoscope and Rashi predictions, daily Panchang & Muhurat (nakshatra, Rahu Kaal, Gulika Kaal, Abhijit Muhurat), daily numerology (lucky number/colour), Sookshma and Prana dasha levels, multiple saved profiles for family members, and premium reports including marriage, career, wealth, education, gem recommendation, numerology, yearly horoscope and separate Saturn/Jupiter transit reports; consultation by chat/call is paid. Source: https://play.google.com/store/apps/details?id=com.clickastro.freehoroscope.astrology&hl=en_SG

**Where it beats us:** matching depth (Papasamya, Dasha Sandhi, south-Indian methods), dasha depth to Prana level, and saved family profiles. **Where we beat it:** KP Prashna, Jaimini Chara dasha, Shadbala depth and Nepali presentation.

### 1.3 AstroTalk — app-first marketplace (free tools, paid human consultation)

Free: Kundli and Kundli Milan, daily/weekly/monthly/yearly horoscopes, and a daily Panchang with Muhurat suggestions; calculators for love, numerology, Sun/Rising, dasha, nakshatra and Mangal Dosha. Paid core: chat/call with astrologers (first session free), live sessions, an AstroMall remedy shop and pooja booking. Systems listed: Vedic, Tarot, Nadi, numerology, Lal Kitab, Western, KP, Prashna, psychic, face reading, palmistry, Vastu. Source: https://play.google.com/store/apps/details?id=com.astrotalk&hl=en_IE

**Where it beats us:** only in the marketplace/human layer (see §5) and in Rashi Phal cadence. As a calculation engine it is thinner than AstroSage/Clickastro; there is no reason to chase its Tarot/palmistry/face-reading surface.

### 1.4 Cosmic Insights — app (free, most complete free calculation list found)

Free feature list, verbatim in scope: all 16 divisional charts "and more"; Shadbala, Ashtakvarga **and Prastarashtakvarga**, Avasthas, **Argala**, Bhava Bala, **Bhava Chalit chart**; yogas, Arudha Padas, Jaimini Karakas, Badhaka planets; Panchang (daily Panchang & Muhurat, Hora, Rahu Kaal, Hindu calendar with festivals, Abhijit Muhurat, Panchak, Tarabala, Chandrabala); detailed Nakshatra analysis including divisional-chart nakshatras, Nadi nakshatras, Nava Tara and Tarabala table; Kalachakra, Narachakra, Drekkanas, divisional deities, Somnath/Jagannath Drekkana, Yogataras; Rahu–Ketu analysis; Panchapakshi; Tithi Pravesha (true Vedic birthday); matching on Ashtakoota, Dashakoota and modern methods; planet dignities across all vargas; **15+ dasha systems**; remedies; PDF download; Jyotish reference tables and Karakas learning module; GPS Prashna/time charts; **store thousands of horoscopes**; offline access; North/South chart styles. Sources: https://apps.apple.com/us/app/cosmic-insights-astrology/id1184918628 · https://play.google.com/store/apps/details?id=gman.vedicastro&hl=en_US&gl=US

**Where it beats us:** this is the single strongest free reference implementation — Argala, Prastara, Bhava Chalit, Avasthas, Tarabala/Chandrabala, 15+ dashas and saved-chart storage, all free. It is the benchmark for §3. **Where we beat it:** KP Prashna horary, Lal Kitab, bilingual Nepali output and the combinatorial PDF report (Cosmic Insights' strength is tables; ours is narrative synthesis).

### 1.5 Drik Panchang — website + app (free; calendar authority)

The website is treated by third-party comparison as the definitive online Panchang reference: daily Panchang page with all five limbs plus exact start/end times for the user's location, Rahu Kalam, Yamagandam, Gulika Kalam, Abhijit Muhurat, Amrit Kalam, Brahma Muhurat and the full Hora sequence, a Muhurat section for specific activities (travel, business, property, wedding), and a festival calendar with regional variations and exact timings. Source: https://asksoma.ai/compare/vs/drikpanchang.html

App: grid calendar customisable for lunar and solar calendars (Bengali, Malayalam, Odia, Tamil variants; Purnimanta/Amanta; Vikrama/Shaka/Gujarati Samvat); the most comprehensive festival list (Ekadashi, Sankashti, Pradosham, Purnima, Sankranti, eclipses, government holidays, Jayanti, fasting days, with reminders); Kundali support with Lagna/Surya/Chandra/etc. Kundalis, **Bhav Chalit chart including D1–D60**, North/South/East chart formats, and **Kundali save/edit/delete/open** with each Kundali tagged with its running dasha/antardasha; detailed daily Panchang (Panchaka, Ganda Moola, Bhadra, Vinchudo, Ravi/Amrita/Sarvartha Siddhi/Tripushkara/Dwipushkara/Ravi Pushya/Guru Pushya yogas); Muhurta table with day/night Choghadiya, Shubh Horai, Udaya Lagna and Pancha Pakshi Muhurta with a countdown; cloud sync; Prashnavali (Rama/Ganesha/Durga/Hanuman); Ashta Kuta matching with Bhakoot/Nadi consideration and saved matches; user-defined Tithi reminders. Source: https://play.google.com/store/apps/details?id=com.drikp.core

**Where it beats us:** month-grid calendar, festival calendar, activity Muhurat search, saved charts. **Where we beat it:** everything interpretive — Drik's Kundli interpretation is, by that same comparison, limited to generic planetary descriptions without aspects, lordships, dasha context or yogas.

### 1.6 AstroYogi — app/website (free tools, paid consultation from ~$0.65/min)

Free: 2026 annual horoscope, daily horoscope, Janam Kundli, Kundli matching (compatibility, Shani Dosha, Manglik Dosha, lucky gemstone), Tarot (1- and 3-card), Panchang calendar (Tithi, Muhurat, Chaughadia every day), numerology report (Life Path, Destiny, Name, Lucky Number), first chat free. Paid: chat/call with 5,000+ verified astrologers across Vedic, Tarot, numerology, Vastu, KP, palmistry, Reiki, Feng Shui, face reading, Prashna. Source: https://apps.apple.com/us/app/astroyogi-astrology-kundli/id1475620580

**Where it beats us:** Rashi Phal cadence + annual horoscope as a free front door, and the consultation marketplace. Calculation depth is not its pitch.

### 1.7 Cafe Astrology — website (free; Western, not Vedic)

Free: interactive birth-chart wheel with hover interpretations, planet signs/houses/aspects, asteroid lists, multiple house systems (default Placidus; also Alcabitius, Porphyry, Equal, Koch, Whole Sign, plus a sidereal/Lahiri whole-sign variant), compatibility reports (including a no-birth-time variant), daily horoscope by birth date/time from current transits to the natal chart, and **saved charts in the browser (cookie) with a Profile number + PIN to restore them on another device, up to 10 charts**. Sources: https://cafeastrology.com/reports/ · https://astro.cafeastrology.com/

**Relevance is partial:** it is a Western-tropical system, so its house systems and aspect doctrine do not transfer to a Vedic product. What transfers is the *pattern*: free + deep + saved charts as the retention loop, and a daily transit-to-natal horoscope as the return-visit hook. Do not chase its Western content.

### 1.8 astro.com (Astrodienst) — website (free charts, paid authored reports)

Free: chart drawings with a wide choice of chart types, drawing styles, house systems and asteroids; ephemeris for any time range; personal daily horoscope (Robert Hand) with love horoscope and celestial events; transits-of-the-year and yearly analysis as free try-out editions; weekly Sun-sign horoscope; an electional ("Best Time") horoscope for choosing a moment for a project; personality, career/vocation, money/success and relationship reports as free try-out editions; Astro-Databank and an Astro-Wiki. Paid: full authored reports (order ~$65 for a personal e-horoscope in third-party summaries) and a PDF-chart subscription whose **Extended Data Storage holds up to 2,000 chart data sets** in one profile. Sources: https://www.astro.com/horoscopes?ract=xx68747470733a2f2f7777772e617374726f2e636f6d2f6367692f61747867656e2e6367693f6369643d71713866696c65326b443359652d75313235333932303437333b6e686f723d343b627479703d636626c616e673d65&nhor=19 · https://www.astro.com/horoscope?nhor=512

**What transfers:** saved-chart storage at scale, a daily transit horoscope, and electional timing as a named feature ("Best Time") — the Western cousin of our Muhurta finder. Its authored-report model is the paid/human pattern in §5.

### 1.9 Prokerala — API (paid, credit-weighted; the feature list is the audit)

Its published credit catalogue is itself a competitor feature list, and it names modules we lack as first-class products: **Sudharshanachakra** (500 credits), **Bhava Chart** (200), **Papa Dosha**, **Papa Samaya** and **Dasha Sandi** in the compatibility report, **Kerala Porutham** and **Tamil Porutham** (south-Indian matching), Nabhasa/Chandra/Surya yogas, planet transit Kakshya/Nakshatra/prediction modules, favourable periods, and daily horoscopes (general/health/career/love, 250 credits each in English). Pricing model (third-party summaries of the same catalogue): free tier 5,000 credits/month, then Ruby $19/month for 100,000 credits, Emerald $49/350,000, Sapphire $99/1,000,000 — each endpoint consuming a different credit weight (e.g. birth chart 50, advanced Kundli 300, basic Panchang 10, matching 50 in one summary). Source: https://api.prokerala.com/api-credits/

**Relevance:** Prokerala is not a consumer rival; it is proof that Sudarshana, Bhava Chart, Papasamya and Dasha Sandhi are sellable as *separate* modules. If we ever expose an API, these are the module boundaries to copy.

### 1.10 Jagannatha Hora — desktop freeware (free; the scholars' benchmark)

Free, offline, Windows (via Wine/Parallels on Mac): 23 divisional charts (D1–D144 including D60/D81/D108/D144) plus variant Hora/Drekkana/D9/D30 calculations, a generic D-m×n mixed chart and custom D-N for any N 1–300; Bhava/Chalit chakra under many house schemes (Rasi, equal 30°, Sripathi/Porphyry, KP/Placidus, Koch, Regiomontanus, Campanus, axial rotation, Polich/Page, Alcabitus) from Lagna, Moon or Sun; 9 planets + outer planets + Gulika/Mandi and 9 other Upagrahas; special Lagnas (Bhava, Hora, Ghati, Sree, Indu, Vighati, Pranapada, Varnada and 11 more Varnadas); Vimshottari, Chara, Ashtottari and Yogini dashas; transits; yogas; Ashtakavarga; **Muhurta module**; Panchanga; KP; Prashna; matching; North/South print formats and PDF export. Sources: https://www.scribd.com/document/420783239/Jagannatha-Hora-features-doc · https://www.techjockey.com/detail/jagannathahora/ · https://www.softwaredekho.in/software/jagannatha-hora

**Where it beats us:** chart-count ceiling (D60+ variants, custom vargas), Upagrahas/special Lagnas, Muhurta, and research depth. **Where we beat it:** it is a desktop install with no web sharing, no Nepali bilingual output and no narrative report — our distribution advantage.

### 1.11 Parashara's Light — desktop/mobile paid software (paid)

Paid (listings from ₹5,900 personal to ₹25,960 professional edition): marketed as 5,000 calculations; birth/divisional charts in North/South/circular/Bengali/Oriya styles; ayanamsa options; Panchanga; dashas; Ashtakavarga; Gochar; **Varshphala, Muhurta (commercial edition), Panch Pakshi (commercial edition), Prashna, compatibility, Jaimini, KP Prashna**; classical interpretation, yogas, health, dasha-phala, Gochara-phala and remedies; inbuilt atlas of 5 million locations with timezone/DST lookup; unlimited chart file manager (commercial/professional); birth-time rectification from events/vargas/dashas (professional); Vedic tutorials and Jyotish classic texts. Sources: https://www.parasharagroup.com/parasharas-light-7-0-software.html · https://www.indiamart.com/proddetail/parashara-s-light-astrology-software-commercial-edition-14053388191.html

**Where it beats us:** Muhurta + Varshphal + rectification as professional tools, and the location atlas (our geocoding chain is the web equivalent and already covers this). Price puts it out of reach of our casual web audience — a reason to ship its *features* free on the web rather than to mimic its business model.

### 1.12 Maitreya — open-source desktop (free, GPL)

Free, GPL, Windows/macOS/Linux/UNIX: classical Vedic + KP + parts of Jaimini + Western in one configurable environment; dashas (text/tree/graphical timeline), Ashtakavarga, Shadbala, yogas, **Arudha Padas, higher Vargas, partner analysis**, Upagrahas, Kala Velas, Arabic points, Uranian planets/planetoids, ephemerides, eclipse data, planetary Hora, a **Sarvatobhadra Chakra** diagram, custom-yoga definitions and an astrological scripting language; large geographical database. Sources: https://www.linuxlinks.com/Maitreya/ · https://launchpad.net/maitreya

**Where it beats us:** scriptability/research tooling and Sarvatobhadra — both niche. Its UI polish is, by its own reviewers' admission, community-grade; not a consumer benchmark.

### 1.13 Open engines — PyJHora and similar pyswisseph projects (free, study material)

**PyJHora** (Python, Swiss Ephemeris, after P. V. R. Narasimha Rao's Jagannatha Hora): modules for Arudhas; Ashtakavarga (**Binna, Prastara and Samudhaya**, Sodhana Pinda); rasi + divisional charts (D1–D300 incl. mixed charts); **Bhava chart under 17 house schemes** (equal, KP, Sripathi, Placidus, Koch, Porphyry, Regiomontanus, Campanus, Vehlow, axial rotation, azimuthal, Polich/Page, Alcabitus, Morinus); retrogression/combustion; Vaiseshikamsa and Vimsopaka (Dasa/Shad/Sapta/Shodasa varga); Varnada Lagna under several authorities; Pushkara Navamsa/Bhaga; Mrityu Bhaga; Marana Karaka Sthana; Lattha stars; next/previous planetary entries into divisional charts; **47 dasha systems** (Graha, Rasi and annual); 100+ yogas; 8 doshas (Kala Sarpa, Manglik, Pitru, Guru Chandala, Ganda Moola, Kalathra, Ghata, Shrapit); a **monthly Vedic calendar widget**; 6 languages; ~6,300 unit tests. Sources: https://pypi.org/project/PyJHora/4.3.5/ · https://deepwiki.com/naturalstupid/PyJHora

**VedicAstro** (Python, flatlib/sidereal branch, FastAPI companion): chart generation, planet/house tables, **ABCD significators per planet and per house**, Vimshottari dasha, Western-style aspects, and a FastAPI deployment pattern — i.e. the closest open analogue to our own stack. Source: https://pypi.org/project/vedicastro/0.1.5/

**jyotishganit** (Python, Skyfield/JPL DE421 rather than Swiss Ephemeris): whole-sign houses, drishti, Panchanga, D2–D60 vargas, Binnashtakavarga + Sarvashtakavarga, Shadbala, Vimshottari. Source: https://deepwiki.com/northtara/jyotishganit/1.2-system-architecture

**Rule for reuse:** method lists, house-scheme names, dasha counts and table structures are legitimate study material. Do not copy code, text or test data from these projects into our repo without checking their licences (PyJHora is AGPL-family; Maitreya is GPL) — rebuild the *method* from BPHS/Jaimini/KP rules, as §4 does.

## 2. Comparison matrix

Priority rule (per brief): **P0** = flagship, seen on 3+ competitors or a headline premium feature. **P1** = valuable. **P2** = nice-to-have. "Ours" uses: ✅ covered · ◐ partial · ❌ gap. Competitor abbreviations: AS=A AstroSage, CL=Clickastro, AT=AstroTalk, CI=Cosmic Insights, DR=Drik Panchang, AY=AstroYogi, CA=Cafe Astrology, AC=astro.com, PK=Prokerala, JH=Jagannatha Hora, PL=Parashara's Light, MA=Maitreya, PJ=PyJHora/open engines.

| # | Feature | Competitors with it | Ours | Verdict | Priority |
|---|---|---|---|---|---|
| 1 | Muhurta finder (activity + date-range search: Choghadiya, Hora, Rahu/Yamaganda/Gulika, Abhijit, activity rules) | AS, CL, CI, DR, AY, JH, PL | ❌ (single-day Panchang only; no /api/muhurta, no Choghadiya/Hora/Rahu Kaal output) | CONFIRMED GAP | **P0** |
| 2 | Bhava Chalit chart (Sripathi and/or equal/Placidus cusps, planet house-shift table) | AS, CI, DR, JH, PK, PJ | ❌ | CONFIRMED GAP | **P0** |
| 3 | Prastara Ashtakavarga (per-planet × per-sign bindu/rekha grid, with Trikona/Ekadhipatya reduction) | AS, CI, PJ | ❌ (Sarva 337 only) | CONFIRMED GAP | **P0** |
| 4 | Sudarshana Chakra (Lagna + Moon + Sun concentric rings) | PK (named module); classical method widely described | ❌ | CONFIRMED GAP | P1 |
| 5 | KP cusp-promise / event analysis (Placidus cusps, significator tables, promise + dasha + transit triple filter) | AS, PL, MA, PJ-adjacent (VedicAstro ABCD significators) | ◐ (sub-lords + Prashna exist; no cusp chart, no significator table, no event verdict) | CONFIRMED GAP (partial coverage) | **P0** |
| 6 | Full Varshphal (Panchadhikari 5-officer election, Tajika yogas, Sahams, Mudda dasha) | AS, CL (yearly), PL, JH-adjacent | ◐ (solar return + Muntha + annual-Lagna lord exist; 5-officer election, Tajika yogas, Sahams, Mudda dasha missing) | CONFIRMED GAP (partial coverage) | **P0** |
| 7 | Jaimini Argala (+ Virodhargala, incl. Ketu reversal) | CI (named); JH/MA/PL Jaimini modules (Argala not separately named in their public lists) | ❌ | CONFIRMED GAP | P1 |
| 8 | Daily/weekly/monthly Rashi Phal (Moon-sign horoscope, incl. personalised transit-to-natal version) | AS, CL, AT, AY, CA (daily), AC (weekly) | ❌ | CONFIRMED GAP | **P0** |
| 9 | Panchang month calendar view (grid month, festivals, per-day limbs) | DR, CI, AS (Hindu calendar), PJ (calendar widget) | ❌ (single-day /api/panchang only) | CONFIRMED GAP | **P0** |
| 10 | Saved charts (localStorage) + shareable link | CI (thousands), DR (save/edit/delete + cloud sync), CA (10, Profile+PIN), AC (2,000 on subscription), PL (file manager) | ❌ (localStorage holds language + style only) | CONFIRMED GAP | **P0** |
| 11 | Matchmaking beyond Guna (Papasamya, Dasha Sandhi, Bhava Milan, Dashakoota/Porutham, 7th-house + D9 read) | CL, CI (Dashakoota), PK (Papa Samaya, Dasha Sandi, Kerala/Tamil Porutham), AY (Shani/Manglik in match) | ◐ (Guna + separate dosha flags exist; no combined verdict, no Papasamya/Dasha Sandhi/Bhava Milan) | CONFIRMED GAP (partial coverage) | **P0** |
| 12 | Gemstone/Rudraksha deep-dive (standalone: stone, finger, metal, weight, day, mantra, conflicts, yantra) | AS (Brihat headline), CL (premium gem report), AY (lucky gemstone) | ◐ (life/lucky/fortune stones + mukhi + 6/8/12 safety rule already in the PDF report; no standalone page, no finger/metal/weight/conflicts/yantra) | PARTIAL — extension only | P2 |
| 13 | Sade Sati phase calendar (detailed phase dates) | AS, CL, PK (Sade Sati report modules) | ✅ for the current cycle (span + peak start + setting start from real Saturn ingresses) | ALREADY COVERED (core); lifetime past/future cycle list is the only extension | P2 (extension) |
| 14a | More dasha systems (Ashtottari, plus Vimshottari to Sookshma/Prana levels) | CI (15+), JH, PJ (47), CL (Sookshma/Prana) | ◐ (4 systems; Vimshottari depth to check against Sookshma/Prana) | CONFIRMED GAP (depth) | P1 |
| 14b | Nakshatra deep-dive (Avasthas, Tarabala, Chandrabala, Nava Tara, divisional nakshatras) | CI (named set) | ◐ (nakshatra + pada + name letters exist; no Avastha/Tarabala/Chandrabala/Nava Tara) | CONFIRMED GAP | P1 |
| 14c | Upagrahas + special Lagnas (Gulika, Mandi, Hora/Ghati/Sree/Indu/Varnada Lagnas) | JH, MA | ❌ | CONFIRMED GAP | P2 |
| 14d | Ishta Devta (Atmakaraka in D9 → deity) | AS (Brihat headline) | ❌ | CONFIRMED GAP | P2 |
| 14e | Sarvatobhadra Chakra / Kalachakra / Panchapakshi / Tithi Pravesha | MA (Sarvatobhadra), CI (Kalachakra, Panchapakshi, Tithi Pravesha) | ❌ | CONFIRMED GAP (niche) | P2 |
| 14f | Favourable periods / golden period as a standalone view | AS (Brihat), CL, PK (Favourable Periods module) | ◐ (favourable-period logic exists inside forecast/transit text; no standalone ranked list) | PARTIAL | P2 |
| 14g | Baby-name list generator (names per nakshatra pada) | AS (free baby-name suggestion) | ◐ (nakshatra name letters exist; no name list) | PARTIAL | P2 |
| — | Lal Kitab full depth (Teva types, all 9 Rin, 36-year dasha) | AS (fullest free Lal Kitab) | ◐ (khana chart, pakka ghar, 3 of 9 Rin) | KNOWN PARTIAL (pre-existing, not new) | P1 (finish Rin set before adding new systems) |
| — | Western tropical charts / Tarot / palmistry / face reading | CA, AC (Western); AT, AY (Tarot/palmistry) | ❌ (by design — Vedic product) | NOT A GAP — do not chase | — |

**Count check:** P0 = 9 items (§3.1, 3.2, 3.3, 3.5, 3.6, 3.8, 3.9, 3.10, 3.11). The single biggest pattern: **every P0 except KP/Varshphal is a return-visit or sharing feature** (Muhurta, Rashi Phal, month calendar, saved charts) or a **chart-view competitors sell as a module** (Chalit, Prastara, matching depth). Our engine is ahead on depth; our product is behind on daily utility and persistence.

## 3. Gap verdicts in detail (the 14 checks)

### 3.1 Muhurta finder — CONFIRMED GAP, P0

Present on AstroSage (daily Panchang & Muhurat, Hora, Rahu Kaal, Choghadiya, Abhijit/Vijay), Clickastro (daily Panchang & Muhurat), Cosmic Insights (daily Panchang & Muhurat, Hora, Rahu Kaal, Abhijit), Drik Panchang (Muhurta table + activity Muhurat section), AstroYogi (Panchang calendar with Muhurat/Chaughadia), Jagannatha Hora (Muhurta module) and Parashara's Light commercial edition. Our `/api/panchang` returns one day's five limbs plus sunrise/sunset only. A finder is the highest-frequency use case in this whole audit: it is what brings a user back on a day they are *not* reading their birth chart.

### 3.2 Bhava Chalit chart — CONFIRMED GAP, P0

Named on AstroSage (Chalit chart/table), Cosmic Insights (Bhava Chalit chart), Drik Panchang (Bhav Chalit incl. D1–D60), Jagannatha Hora (Bhava/Chalit under 11+ house schemes), Prokerala (Bhava Chart module) and PyJHora (Bhava chart under 17 schemes). We show only whole-sign houses, so any planet near a sign boundary is shown in exactly one house where competitors show the house-shift explicitly. This is the most-cited "why does my chart differ between sites" feature — shipping it also answers support questions.

### 3.3 Prastara Ashtakavarga — CONFIRMED GAP, P0

Named on AstroSage's app list (Prastarashtakvarga), Cosmic Insights (Prastarashtakvarga) and PyJHora (Prastara module). We publish only the Sarva (summed) 337 total with per-house interpretation. The Prastara grid is the underlying evidence for that total; without it, a serious user cannot audit or use our Ashtakavarga for transit timing.

### 3.4 Sudarshana Chakra — CONFIRMED GAP, P1

**Correction to the brief:** the classical Sudarshana Chakra is *not* D1/D9/Moon. It is three concentric rings counted from three origins in the *same* D1 chart: Lagna (body/self), Moon (mind) and Sun (soul/atman) — see §4.4. Prokerala sells it as a named module (Sudharshanachakra); a D1+D9 combined view is a different, modern composite and should not be labelled Sudarshana. Priority P1, not P0: only one competitor names it as a module, but it is cheap once D1 exists (it is a re-projection, not new astronomy) and it is visually distinctive — three rings render well in our chart style.

### 3.5 KP cusp-promise / event analysis — CONFIRMED GAP (partial), P0

We have the hard half (249-sub table, sub-lords, Prashna) and lack the usable half: no Placidus cusp chart, no significator table (which planets signify which houses, by occupation/ownership/star/sub), and no event verdict (promise → dasha activation → transit confirmation). AstroSage's free KP section (cuspal charts, house/planet significators, ruling planets, 1–249 horary) is the closest free parallel, and Parashara's Light and Maitreya both list KP/KP-Prashna as headline modules. KP users do not come for sub-lord tables; they come for "will this event happen, and when" — that question is currently unanswerable in our product.

### 3.6 Full Varshphal — CONFIRMED GAP (partial), P0

Muntha and the annual-Lagna lord are already ours (§0). Missing, and present on AstroSage's Tajik Varshaphal (Varsha chart, Muntha, Saham, Mudda Vimshottari, Yogini, Panchadhikari) and Parashara's Light (Varshphala): the five-officer (Panchadhikari) election of the true year lord, Tajika yogas (the annual-chart aspect yogas, distinct from natal yogas), Sahams (sensitive points such as fortune, marriage, children — the Tajika Arabic-parts analogue), and Mudda dasha (the year-internal dasha that times months). Clickastro's yearly horoscope and Drik's annual framing show the same demand from the casual side: a year-ahead page is a natural annual return-visit hook.

### 3.7 Jaimini Argala — CONFIRMED GAP, P1

Named explicitly only by Cosmic Insights among the consumer apps; Jagannatha Hora, Maitreya and Parashara's Light list Jaimini modules without naming Argala separately in their public lists. That is why P1, not P0. It is nevertheless the cheapest Jaimini extension available to us (we already compute Jaimini karakas and Chara dasha; Argala needs only sign placements, no new ephemeris work) and it completes the Jaimini story we already tell.

### 3.8 Daily/weekly/monthly Rashi Phal — CONFIRMED GAP, P0

Free on AstroSage (Moon-sign daily/weekly/monthly/yearly), Clickastro (daily + Rashi predictions), AstroTalk (daily/weekly/monthly/yearly), AstroYogi (daily/weekly/monthly/yearly + 2026 annual), Cafe Astrology (daily from transits to natal) and astro.com (weekly Sun-sign + personal daily). We have no horoscope feed at all — no generic Moon-sign text and no personalised transit-to-natal daily. This is, with Muhurta, the other half of the daily-utility gap: without it there is no reason to return tomorrow.

### 3.9 Panchang month calendar view — CONFIRMED GAP, P0

Drik Panchang's grid calendar (with festival list and reminders) and Cosmic Insights' Hindu calendar are the benchmarks; AstroSage's Hindu calendar and PyJHora's monthly Vedic calendar widget show the same pattern. Our Panchang is a single-day API response with no month view, no festival dates and no per-day navigation. Note this is largely *presentation* of data we can already compute day-by-day, plus a festival table (which needs a sourced festival rule set — do not invent festival dates; Drik's list is the reference to study, not copy).

### 3.10 Saved charts + shareable link — CONFIRMED GAP, P0

Cosmic Insights stores thousands of horoscopes; Drik Panchang saves/edits/deletes Kundalis with cloud sync; Cafe Astrology saves up to 10 charts in the browser restorable by Profile + PIN; astro.com's subscription stores up to 2,000; Parashara's Light has an unlimited chart file manager. We store only language and chart style. A localStorage chart library (birth data + a shareable URL encoding the same data, no server account needed) is the smallest change with the largest retention effect in this audit, and it matches our no-login web architecture. Privacy note: birth data in a shareable URL is visible to anyone with the link — say so in the UI.

### 3.11 Matchmaking beyond Guna — CONFIRMED GAP (partial), P0

Guna Milan alone is, in every serious source checked, explicitly *not* a full match: Clickastro's matching adds dosha, Papasamya and Dasha Sandhi in both north- and south-Indian methods; Cosmic Insights adds Dashakoota and modern methods; Prokerala sells Papa Samaya, Dasha Sandi, Kerala Porutham and Tamil Porutham as separate compatibility modules; AstroYogi's matching surfaces Shani and Manglik dosha. We have Guna plus standalone dosha flags, but no combined verdict, no Papasamya (malefic-point balance between charts), no Dasha Sandhi (whether a dasha change falls too close to the wedding for either partner), no Bhava Milan (element/temperament and 7th-house comparison) and no D9 cross-read. This is P0 because matching is the second-most-visited astrology surface after the birth chart itself, and a bare Guna score is the feature most likely to be judged "incomplete" by a knowledgeable user.

### 3.12 Gemstone/Rudraksha deep-dive — PARTIAL, P2 (extension only)

AstroSage's Brihat headline (gemstone + yantra + Rudraksha), Clickastro's premium gem-recommendation report and AstroYogi's lucky-gemstone-in-matching establish the demand. But our PDF already gives life/lucky/fortune stones, a Rudraksha mukhi and a 6/8/12 safety rule (§0). What is missing is a standalone calculator page with finger, metal, weight guidance, day/mantra, stone-conflict rules (which stones must not be worn together) and yantra suggestions. P2 because the entry-level need is already met, and because gemstone advice is the feature most exposed to commercial pressure (shops selling stones) — keep it guidance-only, never a shop link, and keep the existing safety rule (never recommend strengthening a 6/8/12 lord by gemstone).

### 3.13 Sade Sati phase calendar — ALREADY COVERED (core), P2 extension

Our current-cycle span, peak start and setting start from real Saturn ingresses already answer the question competitors' Sade Sati reports answer (AstroSage Sade Sati predictions, Clickastro's Saturn transit report, Prokerala's Sade Sati report module). The only genuine extension is a lifetime view: all past and future Sade Sati cycles for the Moon sign with retrograde wobble dates (Saturn re-entering a sign during retrogression, which splits a phase boundary into two crossings). Do not build a second Sade Sati page; add the lifetime list to the existing transit section if anything.

### 3.14 Other flagship features found on 2+ competitors

- **More dasha systems (P1).** Cosmic Insights 15+ systems, Jagannatha Hora (Vimshottari/Chara/Ashtottari/Yogini), PyJHora 47 systems, Clickastro Sookshma/Prana levels. The cheapest credible additions are Ashtottari (108-year cycle, used when Ardra-to-Revati conditions apply) and Vimshottari depth to Sookshma/Prana — both pure arithmetic on data we already hold.
- **Nakshatra deep-dive (P1).** Cosmic Insights' Avasthas, Tarabala, Chandrabala, Nava Tara and divisional-chart nakshatras. We have nakshatra + pada + name letters; Tarabala (counting from Janma nakshatra in 9-fold Tara cycle) and Chandrabala (Moon-sign strength by Tara) are small tables that make the existing nakshatra section feel complete.
- **Upagrahas + special Lagnas (P2).** Jagannatha Hora and Maitreya both list Gulika/Mandi and special Lagnas; our engine has no Upagraha layer. Niche, scholar-facing, cheap only after the P0s.
- **Ishta Devta (P2).** AstroSage Brihat headline only. Method: Atmakaraka's sign in D9 maps to a deity (with the 12th-from-Karaka nuance in Jaimini practice) — small, but single-source, so verify against a second Jaimini reference before shipping.
- **Sarvatobhadra / Kalachakra / Panchapakshi / Tithi Pravesha (P2).** Maitreya (Sarvatobhadra) and Cosmic Insights (Kalachakra, Panchapakshi, Tithi Pravesha) — all niche, all single-vendor-named in this audit.
- **Favourable periods / golden period (P2, partial).** AstroSage Brihat, Clickastro and Prokerala (Favourable Periods module) all surface a ranked "best periods" list; ours buries the logic in forecast text. A standalone ranked list is presentation work.
- **Baby-name list (P2, partial).** AstroSage free baby-name suggestion; we have the letters, not the names. A name list per pada needs a sourced, culturally checked name set — do not generate names by invention.
- **Lal Kitab completion (P1, pre-existing).** AstroSage has the fullest free Lal Kitab (Teva types, debts, 36-year dasha); we detect 3 of 9 Rin. Finishing the Rin set is higher value than any new P2, because it completes a system we already advertise.

## 4. How each P0/P1 gap is computed (classical method, for an implementer)

One paragraph each — enough to build from BPHS/Jaimini/KP rules, no competitor text copied. All longitudes below are sidereal (Lahiri, as our engine already uses); all house counts are whole-sign unless a cusp system is named.

### 4.1 P0 — Muhurta finder

For a chosen place and date range, first compute local sunrise/sunset astronomically (we already have `sunrise_sunset`), then derive the day's fixed windows: Rahu Kaal, Yamaganda and Gulika as the weekday-ordered 1.5-hour (one-eighth of day/night length) segment for that weekday (Sun→Mon→Tue→Wed→Thu→Fri→Sat sequences differ per segment, so encode the three classical weekday tables, not a single offset); Abhijit as the 48-minute window centred on local solar noon (midpoint of sunrise–sunset), disallowed on Wednesdays in the classical rule; Brahma Muhurta as the 48 minutes ending 96 minutes before sunrise; Choghadiya by splitting sunrise–sunset and sunset–next-sunrise each into 8 equal parts and assigning the weekday's day/night Choghadiya sequence (Amrit/Shubh/Labh good, Char neutral, Rog/Kaal/Udveg avoid, with the night sequence starting from the day's continuation); Hora by taking the weekday lord as the first Hora at sunrise and cycling the Chaldean order (Sun, Venus, Mercury, Moon, Saturn, Jupiter, Mars) through 24 hours. On top of those generic windows, layer the activity filter the finder exists for: for each candidate day compute tithi, nakshatra, yoga, karana and weekday at the window, score the day against the activity's classical allowed/forbidden sets (e.g. marriage bars Rikta tithis and certain nakshatras; travel bars directional weekday rules), exclude any window overlapping Rahu Kaal/Yamaganda/Gulika, and return ranked windows with the reason each window passed or failed — the ranking and the reasons, not just a green slot, are the feature. Sources for the window definitions: https://www.gochar.in/features/muhurta-finder · https://dekhopanchang.com/en/learn/muhurtas

### 4.2 P0 — Bhava Chalit chart

Ship two cusp systems and label them, because competitors disagree and users compare: (a) equal-house Chalit — house *i* cusp = Lagna longitude + (i−1)×30°, a planet belongs to the house whose 30° span (cusp ±15° in the "cusp as middle" reading, or cusp-to-next-cusp in the "cusp as start" reading — pick one, document it, and keep it consistent) contains its longitude; (b) Sripathi/Porphyry — Lagna longitude is the 1st cusp (middle), the MC is the 10th cusp, +180° gives the 7th and 4th cusps, and each quadrant arc is trisected to give the remaining cusps, with house boundaries at the midpoints between adjacent cusps. Output must be a *shift table* (planet, Rasi house → Chalit house, and whether it changed) plus a redrawn chart, because the shift table is what users actually argue about; lordships, dignities and dashas do not change — only occupied-house readings change — and the UI must say so. Sources: https://modernastro.com/astrology/vedic/bhav-chalit · https://deepwiki.com/jatingodnani/vedic-calc/6.5-utility-functions

### 4.3 P0 — Prastara Ashtakavarga

Start from the Bhinnashtakavarga (BAV) already implicit in our Sarva total: for each of the 7 planets plus Lagna as reference points, apply that planet's classical 8×12 contribution table (reference body × house counted from it) to mark a bindu (favourable) or rekha in each of the 12 signs, giving 8 BAV grids whose row totals are fixed (Sun 48, Moon 49, Mars 39, Mercury 54, Jupiter 56, Venus 52, Saturn 39, total 337 — a checksum to test against). The Prastara is then the *unreduced* presentation of those 8 grids stacked sign-by-sign (for each sign, which reference bodies contributed a bindu), followed by the two classical reductions the user needs to read it: Trikona Sodhana (in each triplicity of signs 1-5-9, 2-6-10, 3-7-11, 4-8-12, remove the bindus common to all three signs of the triplicity from each) and Ekadhipatya Sodhana (when two signs share one lord and one of them is unoccupied, remove its bindus; rules differ for occupied/empty pairs and must be implemented per the BPHS chapter, not approximated), with the reduced totals (Samudhaya) reconciling to the Sarva we already publish — if they do not reconcile, the Prastara is wrong. Sources: https://paramarsh.app/patrika/dashas-transits/ashtakavarga-system-complete · https://pypi.org/project/PyJHora/4.3.5/

### 4.4 P1 — Sudarshana Chakra

Take the D1 longitudes once and render three concentric rings from three origins: inner ring houses counted from the Lagna sign, middle ring from the Moon sign, outer ring from the Sun sign, with the same planets placed in each ring according to which house their sign falls in counted from that ring's origin. The reading rule to implement (not just the picture) is the cross-ring agreement test: a house number that holds a planet in two or three rings is a reinforced life theme, a house whose rings disagree (e.g. a benefic in the Lagna ring but a malefic in the Moon ring for the same house number) is an internal-conflict theme, and the annual use is to step the rings year by year (each year of life = one house progressing through the rings). Do not add D9 to this view; if a D1+D9 composite is wanted later, name it separately. Source: https://modernastro.com/astrology/vedic/sudarshan-chakra

### 4.5 P0 — KP cusp-promise / event analysis

Compute Placidus cusps for the birth time/place (KP's house system — this is the one place Placidus is mandatory, and it is why birth-time accuracy matters more here than anywhere else in our product; show a birth-time sensitivity warning), then for each planet and each cusp determine its sub-lord from the 249-sub table we already own, and build the significator table by the four KP links: a planet signifies a house if it occupies it, owns it, occupies the star (nakshatra) of its occupant/owner, or is the sub-lord chain behind those — collapsed in practice to the standard A/B/C significator grading (strongest = planet in the star of, or sub of, a house occupant with no planets in its own star, and so on). For an event, fix its house set from the classical KP sets (marriage 2-7-11, career 2-6-10-11, education 4-5-9, property 4-11-12, childbirth 2-5-11, foreign travel 3-9-12, litigation 6-7-11, health 1-6-8-12), then apply the triple filter and report each filter separately so a "no" is auditable: (1) promise — the relevant cusp's sub-lord must signify the event's favourable houses and not predominantly its 12th-from houses (for marriage, 1-6-10 negate 2-7-11); (2) dasha activation — the running Mahadasha/Antardasha/Pratyantardasha lords must jointly signify the same houses; (3) transit confirmation — Jupiter/Saturn transiting the natal significators or relevant cusps. A verdict that fails filter 1 must never be rescued by filters 2–3. Sources: https://kpastroapp.com/learn/introduction-to-kp-astrology · https://astroavastha.com/blog/kp-house-cusps-cosmic/

### 4.6 P0 — Full Varshphal (Tajika layer on top of our solar return)

Keep our existing solar-return chart (exact return of the Sun to natal sidereal longitude, cast for the birth place) and add four layers: (a) Panchadhikari election — score the five candidates (lord of the Muntha sign, lord of the annual Lagna, triplicity lord of the annual Lagna, day/night lord i.e. lord of the Sun's sign by day or the Moon's sign by night, and lord of the natal Lagna) by Tajika strength (Panchavargaja Bala and placement dignity in the annual chart) and crown the strongest as Varshesha, reporting all five scores so the election is auditable — this replaces our current single-candidate year lord; (b) Muntha reading, which we already place, extended with its lord's placement and aspects in the annual chart and the classical good/bad house sets (9/10/11 best, 1/2/3/5 good, 6/8/12 difficult); (c) Tajika yogas — the annual-chart-only aspect yogas formed by the five Tajika aspects (Ittasala/conjunction-application, Isharpha/separation, Nakta, Yamaya, etc.) between annual planets, each computed from applying/separating orbs and planetary speeds rather than natal yoga geometry; (d) Sahams — sensitive points computed as Lagna + (significator planet − Sun) style arcs per the Tajika Saham list (fortune, marriage, children, etc.) placed in the annual chart; and (e) Mudda dasha — the year-internal dasha that divides the solar year by the annual chart's planetary order for month-level timing. Ship (a) and (b) first; (c)–(e) are the professional tier. Sources: https://panchangbodh.com/varshaphal · https://www.wisdomlib.org/hinduism/book/hayanaratna-the-jewel-of-annual-astrology/d/doc1500936.html

### 4.7 P1 — Jaimini Argala

For a chosen sign or planet as the reference point, scan the signs counted from it: planets in the 2nd, 4th and 11th signs (and, in the extended reading, the 5th) exert Argala — intervention that supports or modifies the reference's results, benefic if the intervening planets are benefics, obstructive in character if malefics; planets in the 12th, 10th and 3rd signs (and 9th against the 5th) exert Virodhargala — obstruction of the corresponding Argala (12th blocks 2nd, 10th blocks 4th, 3rd blocks 11th, 9th blocks 5th); a special case with no obstruction is three or more malefics in the 3rd, which form a malefic Argala of their own; strength comparison decides the outcome — an obstructing planet weaker (fewer planets, or lesser longitude weight) than the Argala-causing planets does not cancel the Argala; and every count reverses for Ketu (Argala from Ketu, and Argala on Ketu, are counted backwards round the zodiac). Render it as a table per planet/house (Argala planets, Virodhargala planets, net verdict: unobstructed / obstructed / malefic-Argala) rather than prose, because the table is the whole value. Sources: https://vedicsiddhanta.in/2016/01/an-introduction-to-jaimini-astrology.html · https://www.slideshare.net/slideshow/jaimini-astrology-argala-in-predictive-astrology/39282404

### 4.8 P0 — Daily/weekly/monthly Rashi Phal

Two products, not one, and the second is the one that differentiates us: (a) generic Moon-sign text — for each of the 12 Moon signs, a short daily/weekly/monthly reading generated from the day's Moon sign, its nakshatra, the Moon's aspects/transits and the day's Panchang quality, with a fixed template (mood, work, money, relationships, caution) so all 12 signs are comparable and none is systematically "luckier"; (b) personalised daily — the user's own chart with today's transits read from Lagna and Moon (we already compute transit-phala from both), the running dasha/antardasha, and any Sade Sati/Dhaiya or double-transit state, composed into the same template so the personal version is recognisably *theirs*, not the generic text with their sign swapped in. Both must carry the date they were computed for and must never present a generic reading as personalised. Cadence to ship: daily first (the return hook), weekly/monthly as aggregations of the same engine, yearly as the Varshphal page (§4.6) — not a fourth text generator.

### 4.9 P0 — Panchang month calendar view

Reuse `daily_panchang` in a loop over the month for the user's place (one sunrise computation per day is cheap; cache by month+place), and render a grid where each cell shows tithi (with Paksha), nakshatra (+pada), and a marker for the day's quality flags (Rahu Kaal window, Abhijit window, festival/fast day, eclipse, Sankranti, Ekadashi/Purnima/Amavasya) with a tap to expand that day's full five limbs plus sunrise/sunset and the Muhurta windows from §4.1 — the month view and the Muhurta finder are one feature with two doors, and should share the day-computation code. The festival layer is the only new data: build it from a sourced rule set (tithi-based festivals computed from the Panchang itself — e.g. Ekadashi = 11th tithi — plus a small curated table for solar events like Sankranti and Mesha Sankranti), and mark any festival whose regional date varies (Purnimanta vs Amanta month reckoning, which Drik Panchang exposes as a setting) with its reckoning, rather than silently picking one. Sources: https://play.google.com/store/apps/details?id=com.drikp.core · https://asksoma.ai/compare/vs/drikpanchang.html

### 4.10 P0 — Saved charts + shareable link

No account, no server storage — the architecture that fits our product: store an array of saved charts in localStorage (name, birth date/time, place name + coordinates + timezone, chart style, created date), render a library list with one-tap reload and delete, and generate a shareable link by encoding the same birth payload (plus language/style) in the URL query or hash (compressed, not a database ID, so the link works without any backend lookup and survives our free Render tier sleeping). Cap the library visibly (Cafe Astrology's 10 and Cosmic Insights' thousands bracket the choice; 20–50 local charts is honest for localStorage), warn that clearing browser data deletes the library and that anyone with a share link can see the birth data in it, and offer export/import as a JSON file so a user can move libraries between devices without an account — that file export is what makes "no account" a feature instead of a limitation.

### 4.11 P0 — Matchmaking beyond Guna

Keep Ashtakoota as the first screen and add four checks that together form the verdict, each reported pass/fail/neutral with its cancellation rules, never collapsed into a single number: (a) Papasamya — count malefic points (Mars, Saturn, Sun, Rahu, Ketu in the classical Papasamya houses 1/2/4/7/8/12, with the south-Indian weighting variants) for each partner from Lagna, Moon and Venus, and compare the two totals — a match needs *balanced* Papa, not zero Papa, and a large imbalance is the flag; (b) Dasha Sandhi — for each partner, check whether a Mahadasha change (or, stricter, an Antardasha change of the Mahadasha lord) falls within a window around the proposed wedding date (commonly ±6–12 months; state the window used) and flag it, since a dasha junction near marriage is classically treated as instability at the foundation; (c) Bhava Milan — compare the two charts' 7th houses and 7th lords (sign, dignity, affliction, placement in each other's charts), Venus/Jupiter condition, and Lagna/Moon-sign elemental compatibility (fire–fire/air, earth–earth/water pairings), plus the D9 (Navamsa) 7th-house cross-read; (d) Dashakoota/Porutham as an optional south-Indian second score (10 Poruthams: Nakshatra, Gana, Yoni, Mahendra, Stree Dirgha, Rashi, Rasyadhipati, Vashya, Rajju, Vedha) shown alongside, not merged into, the Ashtakoota score, with a note when the two systems disagree. The final verdict must be a paragraph naming which checks passed and which did not — a couple with 28/36 Guna but failing Papasamya and Dasha Sandhi must not receive a green "excellent match" badge. Sources: https://paramarsh.app/patrika/compatibility/kundli-matching-guide · https://vedicpredict.com/what-needs-to-be-checked-while-match-making-for-marriage-kundali-milan/ · https://api.prokerala.com/api-credits/

### 4.12 P1 — More dasha systems

Ashtottari: a 108-year cycle whose order and year-lengths differ from Vimshottari (Sun 6, Moon 15, Mars 8, Mercury 17, Saturn 10, Jupiter 19, Rahu 12, Venus 21 — summing to 108, with Ketu excluded in the classical scheme), applied only when its classical condition holds (birth in Ardra through Revati nakshatras under the commonly cited rule, or the alternative Lagna-based conditions — pick one authority, document it, and show the condition check in the UI so a user whose chart does not qualify is not silently given Ashtottari dates); Vimshottari depth: extend the existing tree one level past Antardasha to Pratyantar (sub-sub, ~1/9 of the Antardasha by the same proportional split) and one further to Sookshma, reusing the existing proportional engine rather than a new one. Both are arithmetic, both are testable against Jagannatha Hora/PyJHora published examples — pin at least one published example per system in a regression test before shipping, as we did for Chara dasha.

### 4.13 P1 — Nakshatra deep-dive (Tarabala / Chandrabala / Avasthas)

Tarabala: count from the Janma (birth Moon) nakshatra to the day's/transit's Moon nakshatra, reduce modulo 9, and map to the Tara cycle (Janma, Sampat, Vipat, Kshema, Pratyak, Sadhana, Naidhana, Mitra, Parama Mitra) — Vipat (3rd), Pratyak (5th) and Naidhana (7th) are the caution Taras and must be labelled as caution, not doom; Nava Tara extends the same count to planets (each planet's nakshatra counted from Janma). Chandrabala: the Moon's strength by its sign counted from the natal Moon sign in the 1-4-7-10 style groupings used for Muhurta suitability (strong in 1st/4th/7th/10th from itself in the classical Muhurta table, with the day's Moon sign checked against the user's Janma Rashi). Avasthas: each planet's state by its degree within its sign (Bala/Kumara/Yuva/Vriddha/Mrita by the 6°-division scheme, plus Jagrat/Svapna/Sushupti by sign type) — a dignity modifier table, not a verdict. Ship Tarabala/Chandrabala first (they feed the Muhurta finder in §4.1); Avasthas second.

### 4.14 P1 — Lal Kitab completion (finish before new systems)

Complete the Rin set from 3 to 9 using the same detection pattern already in the code (khana chart + pakka ghar + planet-in-house conditions per Rin, each with its classical remedy and its cancellation/confirmation condition), add the Teva type classification (Dharmi / Nabalik / Andha / Rataundhi — the Brihat headline feature) derived from the Lal Kitab chart's planet placements, and the 36-year Lal Kitab dasha cycle (each planet's period in the fixed Lal Kitab sequence applied from the chart). This is P1 rather than P0 only because Lal Kitab is already partially shipped; it outranks every P2 because it completes an advertised system.

## 5. Where paid/human services still win (honesty section)

- **Personal judgement on ambiguous charts.** AstroSage's Brihat Kundli is explicitly prepared by expert astrologers within 24 hours; Clickastro's in-depth report is reviewed by experienced astrologers; AstroTalk/AstroYogi sell chat/call with a human. A birth-time-uncertain chart, a borderline Guna score, or a dasha junction near a wedding are judgement calls — our engine can show all three filters (§4.5, §4.11) and still should not pretend the filters decide. The honest UI line is: "the calculations are exact; the interpretation is a reading, not a verdict."
- **Consultation, counselling and life decisions.** Career crossroads, marriage obstacles, health anxiety and grief are the top topics on AstroTalk/AstroYogi for a reason: people want a conversation, not a table. We should never position a PDF as a substitute for professional, medical, financial or legal advice, and remedies must never be sold as cures.
- **Palmistry, face reading, Tarot, psychic reading, Vastu visits, pooja booking and remedy shops.** These are human/physical services (AstroTalk, AstroYogi) that software cannot replicate and should not imitate with a randomiser — a Tarot spread generated by code is a different product from a Tarot reading, and labelling it as one would be dishonest. Out of scope by design.
- **Birth-time rectification.** Parashara's Light professional edition rectifies birth time from life events, Vargas and dashas — a skilled, iterative, human-in-the-loop process. Our product should flag birth-time sensitivity (especially for KP cusps, §4.5, and fine Vargas) rather than silently computing on a guessed time.
- **Authored long-form reports.** astro.com's Liz Greene/Robert Hand reports and AstroSage's 250-page Brihat show what a named author with a distinctive interpretive voice adds: coherence across a whole life story, not just correct sections. Our combinatorial engine is the scalable approximation of that; it is not the same thing, and the PDF should not claim a human author.
- **What software wins on, and should keep winning on:** instant, exact, re-runnable calculation; bilingual access; no appointment, no per-minute meter, no account; a chart you can re-open, share and audit against the tables (Prastara, significators, Panchadhikari scores) instead of taking on trust.

## 6. Recommended build order

1. **Saved charts + shareable link (§4.10)** — smallest change, largest retention effect, unblocks every other feature's testing (users can return to a chart).
2. **Bhava Chalit (§4.2) + Prastara (§4.3)** — pure calculation on data we hold; both make our existing Ashtakavarga and house readings auditable.
3. **Muhurta finder (§4.1) + Panchang month view (§4.9)** — one shared day-computation engine, two daily-utility doors; the highest-frequency return reason in the audit.
4. **Rashi Phal (§4.8)** — the second daily-utility door; ship generic first, personalised second.
5. **KP event analysis (§4.5) + matching depth (§4.11)** — the two "is this complete?" credibility features; both reuse significator/house machinery.
6. **Full Varshphal (§4.6) + Argala (§4.7) + dasha depth (§4.12) + Tarabala/Chandrabala (§4.13)** — depth for serious users, in that order.
7. **Lal Kitab completion (§4.14)** — can move earlier if Lal Kitab traffic justifies it; do not start a new system while an advertised one is 3/9 complete.
8. **P2s only after 1–7:** gemstone deep-dive page, Sade Sati lifetime list, Ishta Devta, Upagrahas, Sarvatobhadra/Kalachakra, favourable-periods page, baby-name list.

## 7. Limitations of this audit

- Public pages and store listings only; no account was created, no report was bought, no app was installed, so "free" means "listed as free on the public page" and some features may sit behind in-app steps not visible publicly.
- Competitor marketing routinely overstates ("world's most comprehensive", "100% accurate", "5,000 calculations") — those claims are reported as claims, not verified.
- Prices (Brihat ₹996/₹3,999; Prokerala tiers; Parashara's Light ₹5,900–₹25,960; AstroYogi ~$0.65/min) are point-in-time snapshots from public pages on 2026-10-25 and will drift.
- The Sudarshana correction (§3.4) and the Varshphal/gemstone/Sade Sati corrections (§0) were verified against our own code, not against competitors.
- Nothing in this file is copied from a competitor: feature descriptions are paraphrases, method paragraphs (§4) are reconstructions from classical rules as described in the cited public method pages, and code must be written fresh — in particular, do not lift PyJHora (AGPL-family) or Maitreya (GPL) code into this repo without a licence review.

## 8. Gap-closure addendum (2026-10-25) — all remaining gaps built

Samir's instruction for this round: build every remaining gap **except live
pandit consultation** ("will add pandit later on", 2026-10-25 14:28 NPT).
Every item below is computed from the real chart, bilingual EN/नेपाली,
on-page + premium PDF where it belongs, with goldens/invariants in
`tests/test_worldclass2.py` (27 tests). Baseline at closure: 102 pytest +
17 node before this round; see §8.10 for the final totals.

### 8.1 Varshphal Tajika layer — CLOSED (§3.6, §4.6 a/c/d)

`astro/tajika.py`: Tajika yogas from the annual (solar-return) chart —
Ithasala vs Isharpha by 1-day linear extrapolation of signed speeds
(applying vs separating, retrograde-safe), Nakta (translation of light:
no mutual aspect, a faster planet aspects both), Yamaya (collection of
light: both apply to one common slower planet), Manau (Ithasala spoiled by
Mars/Saturn within orb of the faster planet), Kambula/Gairi-Kambula as a
flagged simplified Moon reading, Ikbala/Induvara chart patterns. Tajika
aspects are the five classical angles (0/60/90/120/180) within a documented
8° orb simplification (classical Deeptamsa varies by planet). Sahams by the
direct formula (no +30° variant): Punya day Moon−Sun+Lagna / night
Sun−Moon+Lagna, Vivaha Venus−Saturn+Lagna, Yasas Jupiter−Punya+Lagna,
Mahatmya Punya−Mars+Lagna, each with lord, house, dignity and strength.
Panchadhikari election (§4.6a): the five officers (natal-Lagna lord,
Muntha lord, Varsha-Lagna lord, Dina-Ratri lord = lord of the Sun's sign by
day / Moon's sign by night, Dorothean triplicity lord), qualifying only by
a Tajika aspect to the Varsha Lagna degree, scored by a simplified Pancha
Vargeeya Bala (dignity + house points, documented approximation — the full
five-fold strength needs divisional charts), classical fallback to the
Muntha lord when no officer aspects. All three layers render per year in
the premium Varshphal block and the PDF forecast section. **Remainder
inside §4.6: Mudda dasha (§4.6e), the year-internal month-timing dasha —
not built in this round** (the task item named Tajika yogas + Sahams +
year-lord integration only). Recorded here, not dropped, not silently
added.

### 8.2 Jaimini Argala — CLOSED (§3.7, §4.7)

`astro/argala.py`: per-house Argala (2nd/4th/11th, extended 5th) and
Virodhargala (12th/10th/3rd, extended 9th against 5th), Ketu reversal
(Ketu in 12th/10th/3rd supports, in 2nd/4th/11th obstructs, 9th extends),
3+ malefics in the 3rd as a malefic Argala of its own, verdict "argala
prevails" iff supporters outnumber obstructers. Per-house and per-planet
tables on-page and in the PDF. Goldens hand-checked incl. the Ketu
reversal cases.

### 8.3 More dasha systems — CLOSED (§3.14, §4.12)

`astro/dasha.py`: **Ashtottari** — 108-year cycle, Ketu excluded
(Mercury included; an early research table claiming the reverse was
checked against two further sources and rejected), Ardra-anchored blocks
(Sun 4 / Moon 3 / Mars 4 / Mercury 3 / Saturn 4 / Jupiter 3 / Rahu 4 /
Venus 3 nakshatras, Abhijit-aware: the intercalary division belongs to
Saturn's block and changes only the balance fraction), 8 MDs + 8 ADs
each, both classical applicability conditions reported separately
(Rahu in kendra/trikona from the Lagna lord and not in the Lagna; day
birth in Krishna paksha OR night birth in Shukla paksha) — computed
regardless, as advisory, since traditions differ on necessity.
**Vimshottari depth**: the current period now resolves to Sookshma
(9 sub-periods of the running Pratyantardasha) and Prana (9 of the
running Sookshma) via a generalised subdivider (Vimshottari behaviour
unchanged). Sample chart: Ashtottari current Jupiter MD, Vimshottari
current Venus MD / Mercury AD / Moon PD / Mercury Sookshma / Saturn Prana.

### 8.4 Nakshatra deep-dive — CLOSED (§3.14, §4.13)

`astro/nakshatra.py`: **Nava Tara** — all 27 nakshatras counted from the
natal Moon nakshatra with Tara names and the 9 caution stars (Vipat,
Pratyak, Naidhana across 3 cycles). **Tarabala** with cycle and strength
note (2nd-cycle evil halved, 3rd negligible, but Vipat/Naidhana still
flagged). **Chandrabala** — transit Moon sign counted from Janma Rashi:
favourable {1,3,6,7,10,11}, neutral {2,5,9} (the 9th-position split is
documented: one tradition mildly unfavourable, the classical Muhurta
text favourable; neutral used), avoid {4,8,12}, 8th = Ashtama Chandra.
**Avasthas** per BPHS ch. 45: Balaadi by 6° parts per sign (odd signs
Bala→Mrita outward, even signs reversed; strengths Bala 1/4, Kumara 1/2,
Yuva full, Vriddha minimal, Mrita none) + Jagratadi (own/exalted =
Jagrat, friendly/neutral = Swapna, enemy/debilitated = Sushupti);
Rahu/Ketu Jagratadi shown as Swapna and flagged indeterminate (no
classical dignity table). Scheme documented in the module, not a verdict.

### 8.5 Lal Kitab completion — CLOSED (§3.14, §4.14, with one correction)

`astro/lalkitab.py`: all 8 detectable Rin now detected (Pitri, Swa,
Matri pre-existing + **Stree** Sun/Moon/Rahu in 2/7, **Bhratri**
Mercury/Venus in 1/8, **Kanya** Mercury in 3/6, **Zulm** Sun/Moon/Mars in
10/12, **Ajanma** Sun/Venus/Mars in 12), each with a `confidence` field;
**Kudrati Rin stays reference-only** — no formation rule for it was
verified in the sources found, so it is listed with its remedy but never
presented as detected (honesty rule from the task brief). Two
pre-existing associated labels were corrected while adding detection
(Bhratri: Mercury/Venus, not Mars; Zulm: Sun/Moon/Mars, not Saturn).
**Teva types**: Andha (mutual enemy planets together in the 10th khana,
or the 10th khana entirely vacant), Adha Andha (Sun in 4th + Saturn in
7th), Dharmi (OR-reading: Jupiter+Saturn together, or Saturn in 11th,
or Rahu/Ketu in 4th / with the Moon — the stricter AND-variant from a
second source is documented in the `variance_note`, not silently
picked), Nabaligh (kendra khanas vacant or holding only Mercury, Saturn,
Rahu or Ketu). **CORRECTION to §3.14/§4.14: the Lal Kitab dasha cycle is
35 years, not 36** — the published source found (IndiaDivine "LK Grammar:
35 year Dasha Chakra", citing Arun Sanhita 1952 ed. p.10) gives Jupiter 6,
Sun 2, Moon 1, Venus 3, Mars 6, Mercury 2, Saturn 6, Rahu 6, Ketu 3 = 35,
with three equal antardashas per Mahadasha (generalised from the single
published Jupiter example: prev/self/next order, flagged low-confidence).
The same source stresses the book gives NO start-point rule and scholars
propose conflicting alternatives — **no start point was invented**: the
first cycle is anchored at birth with Jupiter (first planet of the
published sequence) and every LK-dasha date is marked indicative.
Sample chart: current Rahu MD 2024-05-13→2030-05-14.

### 8.6 Dashakoota / Porutham full tables — CLOSED (§3.11, §4.11d)

`astro/porutham.py`: the South Indian 10-Porutham system as a second
matchmaking system alongside Ashtakoota, with its own verdict — Dina 3,
Gana 4, Mahendra 2, Sthree Deergha 2, Yoni 4, Rasi 7, Rasyadhipati 5,
Vasya 2, Rajju 5, Vedha 2 (36 points; ≥28 Excellent, ≥18 Acceptable).
Tables as verified from multiple agreeing sources: Gana triads, Yoni
animals + 5-tier scoring (same 4, friend 3, neutral 2, mild enemy 1,
bitter enemy 0; serpent–rat counted mild, with the bitter-variant
documented), Mahendra counts {4,7,10,13,16,19,22,25}, Sthree Deergha
>13 (variants >15 / >9 documented, not adopted), Rasi 6/8/12 fail,
Rasyadhipati mirroring Graha Maitri scoring, Vasya control table,
Rajju five groups (consensus groups; the getzodian Ardra/Punarvasu
variant noted, not used), 13 Vedha pairs (Chitra neither gives nor
receives). Direction conventions documented: Dina counts the groom's
star from the bride's; Mahendra/Sthree Deergha count the bride's star
from the groom's; Gana scored without direction. Rajju Dosha is a
deal-breaker flag even when the total passes; Vedha flagged. Two pairs
hand-recomputed in tests (14/36 with Rajju Dosha + Vedha; 23/36 clean).
A drive-by fix landed with this item: `renderMatch`'s extended block
referenced stale engine fields and rendered "undefined" — fixed to the
actual engine fields.

### 8.7 Lifetime Sade Sati list — CLOSED (§3.13)

`astro/transits.py: sade_sati_lifetime`: every Sade Sati period across
100 years from birth, reusing the existing bisected-ingress machinery —
maximal runs inside {Moon−1, Moon, Moon+1}, retrograde dips under 400 days
merged, first entries into Moon−1 (rising) / Moon (peak) / Moon+1
(setting) + final exit, past/current/future marked,
`already_running_at_birth` flagged. Sample chart (Moon Scorpio):
3 periods, first 2011-11-15 → 2020-01-24 (matches the known sidereal
Saturn ingresses Libra Nov 2011 / Scorpio Nov 2014 / Sagittarius Jan 2017
/ Capricorn Jan 2020). Rendered in the existing transit section, not a
second Sade Sati page (per §3.13).

### 8.8 Standalone gemstone/Rudraksha section — CLOSED (§3.12)

`astro/report.py: gemstone_guide`: all 9 planets with stone, weight in
ratti + ≈carat (1 ratti ≈ 0.91 carat jeweller's conversion), finger,
metal, day, beej mantra, deity, colour, number, Rudraksha mukhi, wearing
guidance, chart roles (life/lucky/fortune), weak-by-Shadbala flags, the
dusthana-lord caution reused from the remedies logic, and a trial-period
note. Guidance-only, no shop link, and the existing safety rule is kept:
never recommend strengthening a 6/8/12 lord by gemstone. On-page premium
card + PDF remedies section, EN + NE.

### 8.9 Full personalised election (Muhurta v2) — CLOSED (§3.1, §4.1 extension)

`astro/muhurta.py`: the finder now layers, on top of the existing
Choghadiya/Rahu Kaal/Abhijit/Hora/activity scoring, four personalising
checks combined into one **election score with the reasoning shown**:
Chandra Bala (+2/0/−2 from the user's Janma Rashi), Panchaka check
(active set + classical remainder-rule type, used to *type* the day's
Panchaka — traditionally a death/funeral-timing rule, labelled as such;
−2, or −3 for a house activity), Lagna strength at the elected moment
(Lagna lord dignity, benefics/malefics in Lagna, Moon's house from
Lagna; +2/0/−2), and dasha-period suitability (running Vimshottari MD:
benefic or Lagna lord +1, debilitated or dusthana −1, else 0). The
elected moment is the first good Choghadiya window start, else the
Abhijit midpoint. `GET /api/muhurta` accepts `birth_moon_sign` and/or
full birth data (dob+tob+place resolve the natal chart in-session);
`best_election` ranks days by election score while `best` keeps the
original day-score ranking (an existing test pins that ordering).
This is computation, not the deferred pandit consultation: the UI still
says the election is classical guidance, not a pandit's judgement.

### 8.10 Honestly deferred — NOT built, NOT dropped

- **Live pandit consultation** (human judgement: conflicting-rule
  judgement, remedial prescription for a specific life situation,
  conversation). Deferred by Samir to a later phase ("will add pandit
  later on", 2026-10-25 14:28 NPT). Recorded here as **planned later**,
  not dropped. §5's first two bullets still stand.
- **Palmistry / photo-based inputs** (face reading, Tarot-as-a-service,
  Vastu visits, pooja booking, remedy shops). Assessed honestly: a
  photo-based palm reading cannot be done reliably without a human —
  palm-line detection from a phone photo is error-prone, and any
  code-generated "reading" from it would be fabrication, not astrology.
  This is the one remaining human-judgement item alongside pandit
  consultation, for the reason in §5's third bullet. Out of scope by
  design, not a technical gap to close with a randomiser.
- **Mudda dasha** (§4.6e) — see §8.1. A real classical sub-system,
  deferred because the task item named only Tajika yogas + Sahams +
  year-lord integration; it is the only computation item left open.
- P2s still open from §6 step 8 (not in this round's scope): Upagrahas +
  special Lagnas, Ishta Devta, Sarvatobhadra/Kalachakra/Panchapakshi/
  Tithi Pravesha, favourable-periods page, baby-name list.

### 8.11 Build notes (honest)

- A real bug was found and fixed during this round: two PDF lines used
  `\"...\"` inside a double-quoted f-string expression, which this
  Python 3.12.3 build rejects at import ("unexpected character after
  line continuation character"). Fixed to single-quoted strings; the
  new PDF tests cover both languages' new sections.
- Method decisions that must not be silently changed: Tajika 8° orb;
  Saham direct formula; Panchadhikari simplified Bala + Muntha
  fallback; LK dasha 35 years, birth-anchored, indicative dates;
  Ashtottari Ardra anchor, Ketu excluded, Abhijit-aware; Porutham
  36-point weighting + stated direction conventions; Chandra Bala
  neutral set {2,5,9} with the 9th-split note; Panchaka remainder rule
  used for typing only; Avastha schemes per BPHS ch. 45 as documented
  in `astro/nakshatra.py`.
- Final totals for this round (full-suite run after the PDF fix):
  **130 pytest passed** (103 pre-existing + 27 new
  `tests/test_worldclass2.py`) **+ 17 node passed**; `node --check`
  clean on app.js. Full run: 188.79s, zero failures.
