"use strict";
/* Vedic Astro frontend — vanilla JS SPA. All rendering from /api JSON. */

/* ---------------- i18n ---------------- */
const SIGNS_EN = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"];
const SIGNS_NE = ["मेष","वृष","मिथुन","कर्कट","सिंह","कन्या","तुला","वृश्चिक","धनु","मकर","कुम्भ","मीन"];
const SIGN_GLYPHS = ["♈","♉","♊","♋","♌","♍","♎","♏","♐","♑","♒","♓"];
const SIGN_LORDS = ["Mars","Venus","Mercury","Moon","Sun","Mercury","Venus","Mars","Jupiter","Saturn","Saturn","Jupiter"];
const NE_DIGITS = "०१२३४५६७८९";
const nepNum = (n) => String(n).replace(/\d/g, (d) => NE_DIGITS[+d]);
const locNum = (n) => (LANG === "ne" ? nepNum(n) : String(n));
const PLANET_NE = {Sun:"सूर्य",Moon:"चन्द्र",Mars:"मङ्गल",Mercury:"बुध",Jupiter:"बृहस्पति",Venus:"शुक्र",Saturn:"शनि",Rahu:"राहु",Ketu:"केतु",Lagna:"लग्न"};
const NAK_EN = ["Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra","Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni","Hasta","Chitra","Swati","Vishakha","Anuradha","Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha","Shravana","Dhanishta","Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati"];
const NAK_NE = ["अश्विनी","भरणी","कृत्तिका","रोहिणी","मृगशिरा","आर्द्रा","पुनर्वसु","पुष्य","अश्लेषा","मघा","पूर्व फाल्गुनी","उत्तर फाल्गुनी","हस्त","चित्रा","स्वाती","विशाखा","अनुराधा","ज्येष्ठा","मूल","पूर्वाषाढा","उत्तराषाढा","श्रवण","धनिष्ठा","शतभिषा","पूर्व भाद्रपदा","उत्तर भाद्रपदा","रेवती"];
const TITHI_EN = ["Pratipada","Dwitiya","Tritiya","Chaturthi","Panchami","Shashthi","Saptami","Ashtami","Navami","Dashami","Ekadashi","Dwadashi","Trayodashi","Chaturdashi","Purnima","Pratipada","Dwitiya","Tritiya","Chaturthi","Panchami","Shashthi","Saptami","Ashtami","Navami","Dashami","Ekadashi","Dwadashi","Trayodashi","Chaturdashi","Amavasya"];
const TITHI_NE = ["प्रतिपदा","द्वितीया","तृतीया","चतुर्थी","पञ्चमी","षष्ठी","सप्तमी","अष्टमी","नवमी","दशमी","एकादशी","द्वादशी","त्रयोदशी","चतुर्दशी","पूर्णिमा","प्रतिपदा","द्वितीया","तृतीया","चतुर्थी","पञ्चमी","षष्ठी","सप्तमी","अष्टमी","नवमी","दशमी","एकादशी","द्वादशी","त्रयोदशी","चतुर्दशी","औंसी"];
const YOGA_EN = ["Vishkambha","Priti","Ayushman","Saubhagya","Shobhana","Atiganda","Sukarma","Dhriti","Shoola","Ganda","Vriddhi","Dhruva","Vyaghata","Harshana","Vajra","Siddhi","Vyatipata","Variyan","Parigha","Shiva","Siddha","Sadhya","Shubha","Shukla","Brahma","Indra","Vaidhriti"];
const YOGA_NE = ["विष्कम्भ","प्रीति","आयुष्मान्","सौभाग्य","शोभन","अतिगण्ड","सुकर्मा","धृति","शूल","गण्ड","वृद्धि","ध्रुव","व्याघात","हर्षण","वज्र","सिद्धि","व्यतीपात","वरीयान्","परिघ","शिव","सिद्ध","साध्य","शुभ","शुक्ल","ब्रह्मा","इन्द्र","वैधृति"];
const KARANA_NE = {Bava:"बव",Balava:"बालव",Kaulava:"कौलव",Taitila:"तैतिल",Garaja:"गरज",Vanija:"वणिज",Vishti:"विष्टि",Kimstughna:"किंस्तुघ्न",Shakuni:"शकुनि",Chatushpada:"चतुष्पाद",Naga:"नाग"};
const WEEKDAY_EN = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"];
const WEEKDAY_NE = ["सोमबार","मङ्गलबार","बुधबार","बिहीबार","शुक्रबार","शनिबार","आइतबार"];

const I18N = {
  en: {
    nav_kundali:"Kundali", nav_premium:"Premium Report", nav_matching:"Matching", nav_panchang:"Panchang",
    hero_title:"Your stars, computed precisely.",
    hero_eyebrow:"Parashari · KP · Jaimini",
    eb_kundali:"Chapter I — The Birth Chart", eb_results:"The Reading",
    eb_premium:"Chapter II — The Deep Reading", eb_prashna:"Chapter III — Horary",
    eb_matching:"Chapter IV — Compatibility",
    hero_sub:"Swiss Ephemeris astronomy with Lahiri ayanamsa — Parashari depth, KP timing, Jaimini insight. In English and Nepali.",
    hero_cta:"Create my Kundali",
    panchang_title:"Today's Panchang", loading:"Loading…",
    form_title:"Birth Details", f_name:"Name", f_dob:"Date of birth", f_tob:"Time of birth",
    f_place:"Birth place", f_place_hint:"Search any place in the world, or enter coordinates below.",
    place_global_unavailable:"Worldwide search is unavailable right now — try entering coordinates manually.",
    manual_coords:"Enter coordinates manually", f_lat:"Latitude", f_lon:"Longitude", f_tz:"Timezone (IANA)",
    dir_n:"N · North", dir_s:"S · South", dir_e:"E · East", dir_w:"W · West",
    err_coord_invalid:"That coordinate doesn't look right — try 27.7172 N or 27°43′2″ N.",
    err_coord_lat_range:"Latitude must be between 0° and 90°.",
    err_coord_lon_range:"Longitude must be between 0° and 180°.",
    submit:"Generate Kundali", generating:"Computing…",
    chart_title:"Birth Chart", planets_title:"Planetary Positions",
    th_planet:"Planet", th_sign:"Sign", th_degree:"Degree", th_nakshatra:"Nakshatra", th_house:"House", th_state:"State",
    dasha_title:"Vimshottari Dasha", kp_title:"KP — Cuspal Sub Lords",
    th_signlord:"Sign Lord", th_starlord:"Star Lord", th_sublord:"Sub Lord",
    dosha_title:"Doshas", yoga_title:"Yogas", av_title:"Ashtakavarga (Bindus)",
    av_hint:"Higher bindus (28+) in a house strengthen its results. Sarvashtakavarga total: 337.",
    pred_title:"Predictions — from your chart facts",
    premium_title:"Premium Life Report",
    premium_sub:"The full multi-chapter reading — the depth the premium sites sell, generated from your computed chart.",
    forecast_title:"Favourable Periods — 10 Years", varshphal_title:"Varshphal — Annual Charts",
    remedies_title:"Remedies", pdf_btn:"Download Premium Report (PDF)",
    read_book:"Read Your Book", book_hint:"Your full kundali as a beautiful flipbook — chapters, charts, dashas and remedies.",
    book_cover_sub:"Janma Kundali", book_tap:"Tap to open", book_open_aria:"Open your Janma Kundali book",
    birth_details:"Birth Details", ayanamsa:"Ayanamsa",
    charts_title:"Charts", rashi_word:"Rashi", navamsa_word:"Navamsa", th_planet:"Planet",
    yogas_title:"Yogas", no_yogas:"No major named yogas in this chart.",
    doshas_title:"Doshas", pitra_dosha:"Pitra Dosha",
    remedies_hint:"See the full premium report below for remedies.",
    mahadasha_word:"Mahadasha", antardasha_word:"Antardasha", th_from:"From", th_to:"To",
    dob:"Date of birth", tob:"Time of birth", place:"Place of birth",
    manglik:"Manglik", kaal_sarp:"Kaal Sarp", sade_sati:"Sade Sati",
    match_title:"Kundali Matching — Guna Milan", groom:"Groom / Partner 1", bride:"Bride / Partner 2",
    match_submit:"Match Kundalis", th_koota:"Koota", th_score:"Score", th_detail:"Detail",
    footer_text:"Vedic Astro — Swiss Ephemeris · Lahiri Ayanamsa · Parashari, KP & Jaimini methods. For guidance and reflection.",
    results_for:"Kundali of", born_at:"born", in_word:"in",
    lagna_word:"Lagna", moon_word:"Moon", current_period:"Current period",
    mahadasha:"Mahadasha", antardasha:"Antardasha", pratyantardasha:"Pratyantardasha", until:"until",
    present:"Present", absent:"Absent", yes:"Yes", no:"No",
    exalted:"Exalted", debilitated:"Debilitated", own:"Own sign", neutral:"—", combust:"Combust", retrograde:"Retrograde",
    karakas_title:"Jaimini Karakas",
    tithi:"Tithi", nakshatra:"Nakshatra", yoga:"Yoga", karana:"Karana", sunrise:"Sunrise", sunset:"Sunset",
    shukla:"Shukla", krishna:"Krishna",
    pred_sections:{current_period:"Current Dasha Period",strengths:"Planetary Strengths",transits:"Transits (Gochar)",career:"Career",wealth:"Wealth",relationships:"Relationships",health:"Health"},
    chapters:{personality:"Personality",career:"Career",finance:"Finance & Wealth",marriage:"Marriage & Relationships",health:"Health",education:"Education",family:"Family & Home",foreign:"Foreign Travel & Settlement"},
    doshas:{manglik:"Manglik",kaal_sarp:"Kaal Sarp",sade_sati:"Sade Sati",pitra:"Pitra"},
    lucky:{number:"Lucky Number",colour:"Lucky Colour",day:"Lucky Day",deity:"Deity"},
    gemstones:"Gemstones", rudraksha:"Rudraksha", mantra:"Mantra", dosha_remedies:"Dosha Remedies",
    year_lord:"Year lord", muntha:"Muntha", house_word:"house",
    kootas:{Varna:"Varna",Vashya:"Vashya",Tara:"Tara",Yoni:"Yoni","Graha Maitri":"Graha Maitri",Gana:"Gana",Bhakoot:"Bhakoot",Nadi:"Nadi"},
    groom_moon:"Groom", bride_moon:"Bride",
    err_place:"Please pick a birth place from the list, or enter latitude, longitude and timezone.",
    err_fields:"Please fill in date and time of birth.",
    err_server:"Something went wrong while computing. Please check the details and try again.",
    err_input:"The server could not use these details — please check the date, time and place, then try again.",
    err_timeout:"The server is taking too long to answer (it may be waking up after idling). Please try again in a moment.",
    err_waking:"The server is waking up — retrying…",
    waking:"Waking up the server…",
    section_failed:"This section could not be shown",
    err_incomplete:"The chart data came back incomplete, so the chart itself could not be drawn. Please try again.",
    chart_caption_d1:"Rashi chart (D1) — Nepali janma-patri style", chart_caption_d9:"Navamsa chart (D9)", chart_caption_d10:"Dashamsa chart (D10)",
    chart_caption_pair:"Lagna (D1) + Navamsa (D9) — the traditional kundali pair; D10 below for career",
    chart_lagna:"Lagna", chart_navamsa:"Navamsa", chart_d1_sub:"Rashi · D1", chart_d9_sub:"D9 · strength of planets",
    varga_more:"More vargas — Dashamsa (D10), career chart", birth_panchang_title:"Panchang at birth", vara:"Weekday",
    glance_lagna:"Lagna (Ascendant)", glance_moon:"Moon sign", glance_sun:"Sun sign", glance_lagna_lord:"Lagna lord", pada_word:"Pada",
    sarva:"Sarvashtakavarga",
    nav_prashna:"KP Prashna",
    style_nepali:"Nepali", style_north:"North Indian", style_south:"South Indian",
    chart_caption_south:"South Indian style — signs are fixed; houses count from the marked Lagna sign",
    dasha_phala_title:"Dasha Phala — what each period brings",
    strength_title:"Planetary Strength — Shadbala", bhava_bala_title:"Bhava Bala — house strength (Rupas)",
    vimshopaka_title:"Vimshopaka Bala (of 20)",
    th_sthana:"Sthana", th_dig:"Dig", th_kala:"Kala", th_cheshta:"Cheshta", th_naisargika:"Naisargika",
    th_drik:"Drik", th_total:"Total", th_rupas:"Rupas", th_min:"Min", th_ratio:"Ratio", th_rank:"Rank",
    th_ishta:"Ishta", th_kashta:"Kashta", th_lord:"Lord", th_lord_bala:"Lord's Shadbala",
    transit_title:"Transits (Gochar) & Ingress Dates", th_now:"Now", th_from_moon:"From Moon", th_ingress:"Next ingress",
    numerology_title:"Numerology & Name Letter",
    moolank:"Moolank (root number)", bhagyank:"Bhagyank (destiny number)", name_letter:"Name letter (Moon nakshatra)",
    ruler_word:"Ruler",
    lalkitab_title:"Lal Kitab — the chart in fixed khanas",
    lalkitab_hint:"In Lal Kitab, khana 1 is Aries for everyone; a planet's house is its sign. A planet in its pakka ghar (permanent house) is always awake (jagta).",
    pakka_word:"Pakka ghar", jagta:"Awake (jagta)", soya:"Sleeping (soya)", sleeping_houses:"Sleeping houses",
    rin_title:"Rin — karmic debts & remedies", remedy_word:"Remedy", detected:"Indicated in this chart", reference_only:"Reference (formation rules vary by source)",
    year_ahead_title:"Year Ahead — by your Moon sign",
    prashna_title:"KP Prashna — Horary (1–249)", prashna_sub:"Hold your question in mind, pick a number between 1 and 249, and cast the chart of this moment.",
    p_number:"Your number (1–249)", p_question:"Question (optional)", prashna_submit:"Cast Prashna Chart",
    prashna_chart:"Prashna Chart", ruling_title:"Ruling Planets",
    yogini_word:"Yogini Dasha", tribhagi_word:"Tribhagi Dasha",
    strongest_word:"Strongest planet", weakest_word:"Weakest planet",
    casting:"Casting…",
    deep_special_title:"Special Lagnas — Arudha & Upapada",
    deep_planets_title:"The Planets — Chapter by Chapter",
    deep_houses_title:"The Twelve Houses",
    deep_div_title:"Divisional Charts — the Vargas Speak",
    chara_title:"Jaimini Chara Dasha (K. N. Rao)",
    timing_title:"Timing Synthesis — Two Clocks, One Chart",
    transit_phala_title:"Transit Phala — Gochar from Lagna & Moon",
    av_reading_title:"Ashtakavarga — What the Bindus Say",
    arudha_word:"Arudha Lagna", upapada_word:"Upapada Lagna", chandra_lagna_word:"Chandra Lagna",
    chara_current:"Current Chara period", direction_word:"Direction",
    weak_support_title:"Weak-Planet Support (by Shadbala)",
    house_word_cap:"House",
    nav_horoscope:"Horoscope", nav_muhurta:"Muhurta",
    eb_horoscope:"Chapter V — Rashi Phal", eb_muhurta:"Chapter VI — Auspicious Timing",
    horoscope_title:"Moon-Sign Horoscope",
    horoscope_hint:"Computed from today's real transits counted from your Moon sign — never a generic column.",
    h_sign:"Moon sign", h_span:"Span", h_daily:"Daily", h_weekly:"Weekly", h_monthly:"Monthly",
    horoscope_submit:"Show horoscope",
    muhurta_title:"Muhurta Finder",
    muhurta_hint:"Classical guidance: tithi class, Moon-nakshatra suitability, Rahu Kaal, Choghadiya and Hora. A full election also weighs Chandra Bala, Panchaka and the Lagna.",
    u_from:"From", u_to:"To (max 31 days)", u_activity:"Activity",
    u_nakshatra:"Birth nakshatra (optional, for Tara Bala)",
    muhurta_submit:"Find best days", muhurta_best:"Best days", muhurta_detail:"Day detail",
    act_marriage:"Marriage", act_travel:"Travel", act_business:"Business / trade", act_house:"House construction",
    act_education:"Education", act_job:"Starting a job", act_vehicle:"Buying a vehicle", act_naming:"Naming ceremony",
    month_cal_title:"Month Calendar", cal_load:"Show month",
    cal_hint:"Markers are astronomical only (Ekadashi, Purnima, Amavasya, Sankranti) — regional festival dates are not guessed.",
    saved_title:"Saved Charts",
    saved_hint:"Stored only in this browser — no account needed. A share link opens the same chart on any device.",
    share_btn:"Copy share link", share_copied:"Link copied!", saved_empty:"No saved charts yet.",
    saved_load:"Open", saved_delete:"Remove",
    chalit_title:"Bhava Chalit — houses by actual cusps",
    chalit_hint:"Sripathi method: each house is centred on its cusp. Planets marked shifted sit in a different Chalit house than their Rashi house.",
    th_rashi_house:"Rashi house", th_chalit_house:"Chalit house", th_shifted:"Shifted?",
    f_ayanamsa:"Ayanamsa", f_house:"House system",
    aya_lahiri:"Lahiri (Chitrapaksha) — default", aya_raman:"Raman",
    aya_kp:"Krishnamurti (KP)", aya_yuk:"Yukteshwar",
    hs_placidus:"Placidus — default", hs_equal:"Equal house",
    hs_whole:"Whole sign", hs_sripati:"Sripati",
    f_calc_hint:"Ayanamsa shifts every longitude in the chart. KP always uses Placidus cusps, per KP doctrine.",
    phase1_title:"Classical Core — special lagnas, upagrahas, house cusps",
    cl_title:"Special Lagnas (BPHS Ch. 5)", up_title:"Upagrahas — the shadow points",
    hc_title:"House Cusps",
    th_lagna:"Lagna", th_degree:"Degree", th_use:"Classical use", th_point:"Point", th_note:"Note", th_house:"House",
    calc_settings:"Computed with {aya} ayanamsa and {hs} cusps.",
    use_hora:"Wealth, sustenance, flow of resources", use_bhava:"General circumstances of birth",
    use_ghati:"Power, authority, sudden rise", use_varnada:"Profession, livelihood, social standing",
    use_shri:"Prosperity, Lakshmi's grace", use_indu:"Wealth potential",
    lagna_hora:"Hora Lagna", lagna_bhava:"Bhava Lagna", lagna_ghati:"Ghati Lagna",
    lagna_varnada:"Varnada Lagna", lagna_shri:"Shri Lagna", lagna_indu:"Indu Lagna",
    up_dhuma:"Grief, loss — where sorrow can strike", up_vyatipata:"Calamity, downfall",
    up_parivesha:"Enclosure, restriction", up_indrachapa:"Deception, false appearance",
    up_upaketu:"Comet-like disturbance", up_gulika:"Saturn's son — slow poison (day birth)",
    up_mandi:"Saturn's son — slow poison (night birth)",
    note_gulika:"Rises at the start of Saturn's day-segment", note_mandi:"Rises at the start of Saturn's night-segment",
    kp_placidus_note:"KP cusps are always Placidus, per KP doctrine.",
    prastara_title:"Prastara Ashtakavarga — the bindu grids",
    prastara_hint:"Each grid shows which contributor donates a bindu in each sign. Reduced totals apply Trikona then Ekadhipatya Shodhana (BPHS).",
    prastara_pick:"Planet grid",
    kp_events_title:"KP Event Analysis — promise, dasha, transit",
    kp_events_hint:"Cuspal sub lord promise, checked against the running dasha and current Jupiter/Saturn transits. Guidance, not a guarantee.",
    sudarshana_title:"Sudarshana Chakra — three rings, one chart",
    sudarshana_hint:"The same chart read from Lagna, Moon and Sun. A planet in the same relative house in two or three rings has its results confirmed.",
    th_agreement:"Agreement",
    m_date:"Planned wedding date (optional — enables Dasha Sandhi check)",
    argala_title:"Jaimini Argala — planetary intervention",
    argala_hint:"Planets in the 2nd, 4th and 11th from a house support it; planets in the 12th, 10th and 3rd obstruct it. Ketu's intervention counts backwards.",
    th_house:"House", th_argala:"Argala (support)", th_virodh:"Virodhargala (obstruction)", th_verdict:"Verdict",
    th_balaadi:"Balaadi", th_jagratadi:"Jagratadi", th_status:"Status",
    th_rising:"Rising (enters Moon−1)", th_peak:"Peak (enters Moon sign)", th_setting:"Setting (enters Moon+1)", th_end:"Ends",
    nakshatra_deep_title:"Nakshatra Deep-Dive — Tara, Chandra Bala, Avasthas",
    nakshatra_deep_hint:"Your Moon nakshatra's nine Taras, today's Tara Bala and Chandra Bala, and every planet's Avastha (maturity + wakefulness).",
    ashto_title:"Ashtottari Dasha — the 108-year conditional system",
    ashto_hint:"Eight lords, Ketu excluded. Traditionally applied when Rahu stands in a kendra/trikona from the Lagna lord and the day-night/paksha rule holds — both conditions are shown, and the sequence is computed regardless.",
    sade_lifetime_title:"Lifetime Sade Sati — every period, exact dates",
    sade_lifetime_hint:"Saturn's passage over the three signs around your Moon sign, across a full lifetime. Past, current and future periods are marked.",
    gem_guide_title:"Gemstones & Rudraksha — the complete guide",
    gem_guide_hint:"Every planet's stone, weight, finger, metal, weekday, mantra and Rudraksha — with this chart's cautions (a dusthana lord's stone is never advised).",
    teva_title:"Teva — chart types", lk_dasha_title:"Lal Kitab Dasha — 35-year cycle",
    porutham_title:"Dashakoota / Porutham — the South Indian 10-factor match",
    u_moonsign:"Birth Moon sign (optional, for Chandra Bala)",
    muhurta_personal_hint:"If you already generated a kundali above, its birth details are used automatically for the dasha-suitability check.",
    election_score_word:"Election score",
  },
  ne: {
    nav_kundali:"कुण्डली", nav_premium:"प्रिमियम रिपोर्ट", nav_matching:"मेल मिलान", nav_panchang:"पञ्चाङ्ग",
    hero_title:"तपाईंका तारा, यथार्थ रूपमा गणना गरिएको।",
    hero_eyebrow:"पराशरी · केपी · जैमिनी",
    eb_kundali:"अध्याय १ — जन्म कुण्डली", eb_results:"अध्ययन",
    eb_premium:"अध्याय २ — गहन अध्ययन", eb_prashna:"अध्याय ३ — प्रश्न ज्योतिष",
    eb_matching:"अध्याय ४ — मेल मिलान",
    hero_sub:"लाहिरी अयनांशसहित स्विस एफेमेरिस खगोल विज्ञान — पराशरी गहिराइ, KP समय-शुद्धता, जैमिनी अन्तर्दृष्टि। अङ्ग्रेजी र नेपालीमा।",
    hero_cta:"मेरो कुण्डली बनाउनुहोस्",
    panchang_title:"आजको पञ्चाङ्ग", loading:"लोड हुँदैछ…",
    form_title:"जन्म विवरण", f_name:"नाम", f_dob:"जन्म मिति", f_tob:"जन्म समय",
    f_place:"जन्म स्थान", f_place_hint:"विश्वको कुनै पनि ठाउँ खोज्नुहोस्, वा तल निर्देशाङ्क भर्नुहोस्।",
    place_global_unavailable:"विश्वव्यापी खोज अहिले उपलब्ध छैन — निर्देशाङ्क आफैँ भरेर प्रयास गर्नुहोस्।",
    manual_coords:"निर्देशाङ्क आफैँ भर्नुहोस्", f_lat:"अक्षांश", f_lon:"देशान्तर", f_tz:"समय क्षेत्र (IANA)",
    dir_n:"N · उत्तर", dir_s:"S · दक्षिण", dir_e:"E · पूर्व", dir_w:"W · पश्चिम",
    err_coord_invalid:"यो निर्देशाङ्क मिलेन — जस्तै 27.7172 N वा 27°43′2″ N प्रयास गर्नुहोस्।",
    err_coord_lat_range:"अक्षांश ०° देखि ९०° भित्र हुनुपर्छ।",
    err_coord_lon_range:"देशान्तर ०° देखि १८०° भित्र हुनुपर्छ।",
    submit:"कुण्डली बनाउनुहोस्", generating:"गणना हुँदैछ…",
    chart_title:"जन्म कुण्डली", planets_title:"ग्रहहरूको स्थिति",
    th_planet:"ग्रह", th_sign:"राशि", th_degree:"अंश", th_nakshatra:"नक्षत्र", th_house:"भाव", th_state:"अवस्था",
    dasha_title:"विंशोत्तरी दशा", kp_title:"KP — भाव उपस्वामीहरू",
    th_signlord:"राशि स्वामी", th_starlord:"नक्षत्र स्वामी", th_sublord:"उपस्वामी",
    dosha_title:"दोषहरू", yoga_title:"योगहरू", av_title:"अष्टकवर्ग (बिन्दु)",
    av_hint:"भावमा बढी बिन्दु (२८+) ले त्यसको फल बलियो बनाउँछ। सर्वाष्टकवर्ग जम्मा: ३३७।",
    pred_title:"भविष्यवाणी — तपाईंको कुण्डलीका तथ्यबाट",
    premium_title:"प्रिमियम जीवन रिपोर्ट",
    premium_sub:"पूर्ण बहु-अध्याय विश्लेषण — प्रिमियम साइटहरूले बेच्ने गहिराइ, तपाईंको गणना गरिएको कुण्डलीबाटै तयार।",
    forecast_title:"अनुकूल अवधिहरू — १० वर्ष", varshphal_title:"वर्षफल — वार्षिक कुण्डली",
    remedies_title:"उपायहरू", pdf_btn:"प्रिमियम रिपोर्ट डाउनलोड गर्नुहोस् (PDF)",
    read_book:"आफ्नो किताब पढ्नुहोस्", book_hint:"तपाईंको पूर्ण कुण्डली सुन्दर फ्लिपबुकको रूपमा — अध्याय, कुण्डली, दशा र उपायहरू।",
    book_cover_sub:"जन्म कुण्डली", book_tap:"खोल्न ट्याप गर्नुहोस्", book_open_aria:"आफ्नो जन्म कुण्डली किताब खोल्नुहोस्",
    birth_details:"जन्म विवरण", ayanamsa:"अयनांश",
    charts_title:"कुण्डलीहरू", rashi_word:"राशि", navamsa_word:"नवांश", th_planet:"ग्रह",
    yogas_title:"योगहरू", no_yogas:"यस कुण्डलीमा प्रमुख नामित योगहरू छैनन्।",
    doshas_title:"दोषहरू", pitra_dosha:"पितृ दोष",
    remedies_hint:"उपायहरूका लागि तलको प्रिमियम रिपोर्ट हेर्नुहोस्।",
    mahadasha_word:"महादशा", antardasha_word:"अन्तर्दशा", th_from:"देखि", th_to:"सम्म",
    dob:"जन्म मिति", tob:"जन्म समय", place:"जन्म स्थान",
    manglik:"माङ्गलिक", kaal_sarp:"काल सर्प", sade_sati:"साढेसाती",
    match_title:"कुण्डली मेल — गुण मिलान", groom:"दुलहा / साथी १", bride:"दुलही / साथी २",
    match_submit:"कुण्डली मिलाउनुहोस्", th_koota:"कूट", th_score:"अङ्क", th_detail:"विवरण",
    footer_text:"Vedic Astro — स्विस एफेमेरिस · लाहिरी अयनांश · पराशरी, KP र जैमिनी विधि। मार्गदर्शन र मननका लागि।",
    results_for:"कुण्डली —", born_at:"जन्म", in_word:"मा",
    lagna_word:"लग्न", moon_word:"चन्द्र", current_period:"हालको अवधि",
    mahadasha:"महादशा", antardasha:"अन्तर्दशा", pratyantardasha:"प्रत्यन्तर्दशा", until:"सम्म",
    present:"छ", absent:"छैन", yes:"हो", no:"होइन",
    exalted:"उच्च", debilitated:"नीच", own:"स्वराशि", neutral:"—", combust:"अस्त", retrograde:"वक्री",
    karakas_title:"जैमिनी कारकहरू",
    tithi:"तिथि", nakshatra:"नक्षत्र", yoga:"योग", karana:"करण", sunrise:"सूर्योदय", sunset:"सूर्यास्त",
    shukla:"शुक्ल", krishna:"कृष्ण",
    pred_sections:{current_period:"हालको दशा अवधि",strengths:"ग्रहहरूको बल",transits:"गोचर",career:"पेशा",wealth:"धन",relationships:"सम्बन्ध",health:"स्वास्थ्य"},
    chapters:{personality:"व्यक्तित्व",career:"पेशा",finance:"धन र सम्पत्ति",marriage:"विवाह र सम्बन्ध",health:"स्वास्थ्य",education:"शिक्षा",family:"परिवार र घर",foreign:"विदेश यात्रा र बसोबास"},
    doshas:{manglik:"माङ्गलिक",kaal_sarp:"काल सर्प",sade_sati:"साढेसाती",pitra:"पितृ"},
    lucky:{number:"भाग्य अङ्क",colour:"भाग्य रङ",day:"भाग्य बार",deity:"इष्ट देवता"},
    gemstones:"रत्नहरू", rudraksha:"रुद्राक्ष", mantra:"मन्त्र", dosha_remedies:"दोषका उपायहरू",
    year_lord:"वर्ष स्वामी", muntha:"मुन्था", house_word:"भाव",
    kootas:{Varna:"वर्ण",Vashya:"वश्य",Tara:"तारा",Yoni:"योनि","Graha Maitri":"ग्रह मैत्री",Gana:"गण",Bhakoot:"भकूट",Nadi:"नाडी"},
    groom_moon:"दुलहा", bride_moon:"दुलही",
    err_place:"कृपया सूचीबाट जन्म स्थान छान्नुहोस्, वा अक्षांश, देशान्तर र समय क्षेत्र भर्नुहोस्।",
    err_fields:"कृपया जन्म मिति र समय भर्नुहोस्।",
    err_server:"गणना गर्दा समस्या भयो। विवरण जाँचेर फेरि प्रयास गर्नुहोस्।",
    err_input:"सर्भरले यी विवरण प्रयोग गर्न सकेन — मिति, समय र स्थान जाँचेर फेरि प्रयास गर्नुहोस्।",
    err_timeout:"सर्भरबाट जवाफ आउन धेरै समय लाग्यो (सर्भर अलि बेर निष्क्रिय बसेर उठ्दै हुन सक्छ)। केही क्षणमा फेरि प्रयास गर्नुहोस्।",
    err_waking:"सर्भर उठ्दैछ — फेरि प्रयास गर्दैछ…",
    waking:"सर्भर जगाउँदै…",
    section_failed:"यो खण्ड देखाउन सकिएन",
    err_incomplete:"कुण्डली डाटा अपूर्ण आयो, त्यसैले चार्ट कोर्न सकिएन। फेरि प्रयास गर्नुहोस्।",
    chart_caption_d1:"राशि कुण्डली (D1) — नेपाली जन्मपत्री शैली", chart_caption_d9:"नवांश कुण्डली (D9)", chart_caption_d10:"दशमांश कुण्डली (D10)",
    chart_caption_pair:"लग्न (D1) + नवांश (D9) — परम्परागत कुण्डली जोडी; करियरका लागि D10 तल",
    chart_lagna:"लग्न", chart_navamsa:"नवांश", chart_d1_sub:"राशि · D1", chart_d9_sub:"D9 · ग्रह बल",
    varga_more:"थप वर्गहरू — दशमांश (D10), करियर कुण्डली", birth_panchang_title:"जन्म पञ्चाङ्ग", vara:"वार",
    glance_lagna:"लग्न", glance_moon:"चन्द्र राशि", glance_sun:"सूर्य राशि", glance_lagna_lord:"लग्न स्वामी", pada_word:"पद",
    sarva:"सर्वाष्टकवर्ग",
    nav_prashna:"KP प्रश्न",
    style_nepali:"नेपाली", style_north:"उत्तर भारतीय", style_south:"दक्षिण भारतीय",
    chart_caption_south:"दक्षिण भारतीय शैली — राशिहरू स्थिर छन्; भावहरू चिन्ह लगाइएको लग्न राशिबाट गनिन्छन्",
    dasha_phala_title:"दशाफल — प्रत्येक अवधिले के ल्याउँछ",
    strength_title:"ग्रह बल — षड्बल", bhava_bala_title:"भाव बल — भावहरूको शक्ति (रूपामा)",
    vimshopaka_title:"विंशोपक बल (२० मा)",
    th_sthana:"स्थान", th_dig:"दिग्", th_kala:"काल", th_cheshta:"चेष्टा", th_naisargika:"नैसर्गिक",
    th_drik:"दृष्टि", th_total:"जम्मा", th_rupas:"रूपा", th_min:"न्यूनतम", th_ratio:"अनुपात", th_rank:"क्रम",
    th_ishta:"इष्ट", th_kashta:"कष्ट", th_lord:"स्वामी", th_lord_bala:"स्वामीको षड्बल",
    transit_title:"गोचर र प्रवेश मितिहरू", th_now:"हाल", th_from_moon:"चन्द्रमाबाट", th_ingress:"अर्को प्रवेश",
    numerology_title:"अङ्कशास्त्र र नामको अक्षर",
    moolank:"मूलाङ्क", bhagyank:"भाग्याङ्क", name_letter:"नामको अक्षर (चन्द्र नक्षत्र)",
    ruler_word:"स्वामी ग्रह",
    lalkitab_title:"लाल किताब — स्थिर खानामा कुण्डली",
    lalkitab_hint:"लाल किताबमा खाना १ सबैका लागि मेष हो; ग्रहको घर उसको राशि नै हो। आफ्नो पक्का घरमा बसेको ग्रह सधैँ जागेको (जागता) हुन्छ।",
    pakka_word:"पक्का घर", jagta:"जागेको (जागता)", soya:"सुतेको (सोया)", sleeping_houses:"सुतेका घरहरू",
    rin_title:"ऋण — कर्मिक ऋण र उपाय", remedy_word:"उपाय", detected:"यस कुण्डलीमा देखिएको", reference_only:"सन्दर्भ (बन्ने नियम स्रोतअनुसार फरक छन्)",
    year_ahead_title:"वर्ष अगाडि — तपाईंको चन्द्र राशिअनुसार",
    prashna_title:"KP प्रश्न — होरारी (१–२४९)", prashna_sub:"प्रश्न मनमा राख्नुहोस्, १ देखि २४९ बीचको एउटा अङ्क रोज्नुहोस्, र यस क्षणको कुण्डली बनाउनुहोस्।",
    p_number:"तपाईंको अङ्क (१–२४९)", p_question:"प्रश्न (ऐच्छिक)", prashna_submit:"प्रश्न कुण्डली बनाउनुहोस्",
    prashna_chart:"प्रश्न कुण्डली", ruling_title:"शासक ग्रहहरू (Ruling Planets)",
    yogini_word:"योगिनी दशा", tribhagi_word:"त्रिभागी दशा",
    strongest_word:"सबैभन्दा बलियो ग्रह", weakest_word:"सबैभन्दा कमजोर ग्रह",
    casting:"बनाउँदै…",
    deep_special_title:"विशेष लग्नहरू — आरूढ र उपपद",
    deep_planets_title:"ग्रहहरू — अध्यायगत विश्लेषण",
    deep_houses_title:"बाह्र भावहरू",
    deep_div_title:"वर्ग कुण्डलीहरू — वर्गहरूको विश्लेषण",
    chara_title:"जैमिनी चर दशा (के. एन. राव)",
    timing_title:"समय संश्लेषण — दुई घडी, एउटै कुण्डली",
    transit_phala_title:"गोचर फल — लग्न र चन्द्रमाबाट",
    av_reading_title:"अष्टकवर्ग — बिन्दुहरूले के भन्छन्",
    arudha_word:"आरूढ लग्न", upapada_word:"उपपद लग्न", chandra_lagna_word:"चन्द्र लग्न",
    chara_current:"हालको चर अवधि", direction_word:"दिशा",
    weak_support_title:"कमजोर ग्रहको साथ (षड्बलअनुसार)",
    house_word_cap:"भाव",
    nav_horoscope:"राशिफल", nav_muhurta:"मुहूर्त",
    eb_horoscope:"अध्याय ५ — राशिफल", eb_muhurta:"अध्याय ६ — शुभ मुहूर्त",
    horoscope_title:"चन्द्र राशिफल",
    horoscope_hint:"आजको वास्तविक गोचरलाई तपाईंको चन्द्र राशिबाट गनेर तयार — कहिल्यै सामान्य स्तम्भ होइन।",
    h_sign:"चन्द्र राशि", h_span:"अवधि", h_daily:"दैनिक", h_weekly:"साप्ताहिक", h_monthly:"मासिक",
    horoscope_submit:"राशिफल देखाउनुहोस्",
    muhurta_title:"मुहूर्त खोजकर्ता",
    muhurta_hint:"शास्त्रीय मार्गदर्शन: तिथि वर्ग, चन्द्र नक्षत्र उपयुक्तता, राहुकाल, चौघडिया र होरा। पूर्ण मुहूर्तमा चन्द्रबल, पञ्चक र लग्न पनि हेरिन्छ।",
    u_from:"देखि", u_to:"सम्म (अधिकतम ३१ दिन)", u_activity:"काम",
    u_nakshatra:"जन्म नक्षत्र (ऐच्छिक, ताराबलका लागि)",
    muhurta_submit:"उत्तम दिन खोज्नुहोस्", muhurta_best:"उत्तम दिनहरू", muhurta_detail:"दिनको विवरण",
    act_marriage:"विवाह", act_travel:"यात्रा", act_business:"व्यापार", act_house:"गृह निर्माण",
    act_education:"शिक्षा", act_job:"नोकरी सुरु", act_vehicle:"वाहन खरिद", act_naming:"नामकरण",
    month_cal_title:"महिनाको पात्रो", cal_load:"महिना देखाउनुहोस्",
    cal_hint:"चिन्हहरू खगोलीय मात्र हुन् (एकादशी, पूर्णिमा, औंसी, सङ्क्रान्ति) — क्षेत्रीय पर्व मितिहरू अनुमान गरिँदैनन्।",
    saved_title:"सुरक्षित कुण्डलीहरू",
    saved_hint:"यही ब्राउजरमा मात्र राखिन्छ — कुनै खाता चाहिँदैन। साझा लिङ्कले कुनै पनि यन्त्रमा उही कुण्डली खोल्छ।",
    share_btn:"साझा लिङ्क कपी गर्नुहोस्", share_copied:"लिङ्क कपी भयो!", saved_empty:"अहिलेसम्म कुनै सुरक्षित कुण्डली छैन।",
    saved_load:"खोल्नुहोस्", saved_delete:"हटाउनुहोस्",
    chalit_title:"भाव चलित — वास्तविक भावसीमाबाट घरहरू",
    chalit_hint:"श्रीपति विधि: प्रत्येक भाव आफ्नो कस्पमा केन्द्रित हुन्छ। 'सरेको' चिन्ह लागेका ग्रह राशि घरभन्दा फरक चलित घरमा छन्।",
    th_rashi_house:"राशि भाव", th_chalit_house:"चलित भाव", th_shifted:"सरेको?",
    f_ayanamsa:"अयनांश", f_house:"भाव प्रणाली",
    aya_lahiri:"लाहिरी (चित्रपक्ष) — पूर्वनिर्धारित", aya_raman:"रमन",
    aya_kp:"कृष्णमूर्ति (KP)", aya_yuk:"युक्टेश्वर",
    hs_placidus:"प्लेसिडस — पूर्वनिर्धारित", hs_equal:"समान भाव",
    hs_whole:"पूर्ण राशि", hs_sripati:"श्रीपति",
    f_calc_hint:"अयनांशले कुण्डलीका सबै देशान्तर सार्छ। KP मा सधैं प्लेसिडस कस्प प्रयोग हुन्छ।",
    phase1_title:"शास्त्रीय आधार — विशेष लग्न, उपग्रह, भाव कस्प",
    cl_title:"विशेष लग्नहरू (BPHS अध्याय ५)", up_title:"उपग्रहहरू — छाया बिन्दुहरू",
    hc_title:"भाव कस्पहरू",
    th_lagna:"लग्न", th_degree:"डिग्री", th_use:"शास्त्रीय प्रयोग", th_point:"बिन्दु", th_note:"टिप्पणी", th_house:"भाव",
    calc_settings:"{aya} अयनांश र {hs} कस्प प्रयोग गरी गणना गरिएको।",
    use_hora:"धन, जीविका, स्रोतको प्रवाह", use_bhava:"जन्मका सामान्य परिस्थिति",
    use_ghati:"शक्ति, अधिकार, आकस्मिक उत्थान", use_varnada:"पेशा, जीविका, सामाजिक स्थान",
    use_shri:"समृद्धि, लक्ष्मीको कृपा", use_indu:"धन सम्भावना",
    lagna_hora:"होरा लग्न", lagna_bhava:"भाव लग्न", lagna_ghati:"घटी लग्न",
    lagna_varnada:"वर्णद लग्न", lagna_shri:"श्री लग्न", lagna_indu:"इन्दु लग्न",
    up_dhuma:"शोक, हानि — दुःख पर्न सक्ने ठाउँ", up_vyatipata:"विपत्ति, पतन",
    up_parivesha:"घेराबन्दी, बन्धन", up_indrachapa:"छल, मिथ्या रूप",
    up_upaketu:"धूमकेतुजस्तो विघ्न", up_gulika:"शनिपुत्र — मन्द विष (दिनको जन्म)",
    up_mandi:"शनिपुत्र — मन्द विष (रातको जन्म)",
    note_gulika:"शनिको दिन-खण्डको सुरुमा उदय", note_mandi:"शनिको रात-खण्डको सुरुमा उदय",
    kp_placidus_note:"KP कस्प सधैं प्लेसिडस हुन्छन्।",
    prastara_title:"प्रस्तार अष्टकवर्ग — बिन्दु तालिकाहरू",
    prastara_hint:"प्रत्येक तालिकाले कुन योगदानकर्ताले कुन राशिमा बिन्दु दिन्छ भन्ने देखाउँछ। घटाइएको जम्मामा त्रिकोण अनि एकाधिपत्य शोधन (BPHS) लागू हुन्छ।",
    prastara_pick:"ग्रहको तालिका",
    kp_events_title:"KP घटना विश्लेषण — प्रतिज्ञा, दशा, गोचर",
    kp_events_hint:"कस्पल उपस्वामीको प्रतिज्ञा, चालु दशा र वर्तमान बृहस्पति/शनि गोचरसँग जाँचिएको। मार्गदर्शन हो, ग्यारेन्टी होइन।",
    sudarshana_title:"सुदर्शन चक्र — तीन घेरा, एउटै कुण्डली",
    sudarshana_hint:"उही कुण्डली लग्न, चन्द्र र सूर्यबाट पढिन्छ। दुई वा तीन घेरामा एउटै सापेक्ष भावमा रहेको ग्रहको फल पुष्टि हुन्छ।",
    th_agreement:"सहमति",
    m_date:"योजनाबद्ध विवाह मिति (ऐच्छिक — दशा सन्धि जाँच सक्षम गर्छ)",
    argala_title:"जैमिनी अर्गला — ग्रह हस्तक्षेप",
    argala_hint:"कुनै भावबाट दोस्रो, चौथो र एघारौँमा रहेका ग्रहले साथ दिन्छन्; बाह्रौँ, दशौँ र तेस्रोमा रहेकाले अवरोध गर्छन्। केतुको हस्तक्षेप उल्टो गनिन्छ।",
    th_house:"भाव", th_argala:"अर्गला (साथ)", th_virodh:"विरोधर्गला (अवरोध)", th_verdict:"निष्कर्ष",
    th_balaadi:"बालादि", th_jagratadi:"जाग्रतादि", th_status:"स्थिति",
    th_rising:"उदय (चन्द्र−१ मा प्रवेश)", th_peak:"चरम (चन्द्र राशिमा प्रवेश)", th_setting:"अस्त (चन्द्र+१ मा प्रवेश)", th_end:"समाप्ति",
    nakshatra_deep_title:"नक्षत्र गहन अध्ययन — तारा, चन्द्रबल, अवस्था",
    nakshatra_deep_hint:"तपाईंको चन्द्र नक्षत्रका नौ तारा, आजको ताराबल र चन्द्रबल, र प्रत्येक ग्रहको अवस्था (परिपक्वता + जागरण)।",
    ashto_title:"अष्टोत्तरी दशा — १०८-वर्षीय सशर्त प्रणाली",
    ashto_hint:"आठ स्वामी, केतु बाहेक। परम्परागत रूपमा राहु लग्न स्वामीबाट केन्द्र/त्रिकोणमा हुँदा र दिन-रात/पक्ष नियम मिल्दा लागू हुन्छ — दुवै शर्त देखाइन्छ, र क्रम जेसुकै भए पनि गणना गरिन्छ।",
    sade_lifetime_title:"आजीवन साढेसाती — हरेक अवधि, ठ्याक्कै मितिसहित",
    sade_lifetime_hint:"तपाईंको चन्द्र राशिवरिपरि तीन राशिमा शनिको यात्रा, पूरै जीवनभर। विगत, चालु र भावी अवधि चिन्ह लगाइएका छन्।",
    gem_guide_title:"रत्न र रुद्राक्ष — पूर्ण मार्गदर्शन",
    gem_guide_hint:"प्रत्येक ग्रहको रत्न, तौल, औंला, धातु, बार, मन्त्र र रुद्राक्ष — यस कुण्डलीका सावधानीसहित (दुष्टस्थान स्वामीको रत्न कहिल्यै सल्लाह दिइँदैन)।",
    teva_title:"टेवा — कुण्डलीका प्रकारहरू", lk_dasha_title:"लाल किताब दशा — ३५-वर्षीय चक्र",
    porutham_title:"दशकूट / पोरुथम — दक्षिण भारतीय १०-तत्व मेल",
    u_moonsign:"जन्म चन्द्र राशि (ऐच्छिक, चन्द्रबलका लागि)",
    muhurta_personal_hint:"यदि तपाईंले माथि कुण्डली बनाइसक्नुभएको छ भने, दशा-उपयुक्तता जाँचका लागि त्यसकै जन्म विवरण स्वतः प्रयोग हुन्छ।",
    election_score_word:"निर्वाचन अङ्क",
  }
};

let LANG = localStorage.getItem("vedic-astro-lang") || "en";
const t = (key) => (I18N[LANG] && I18N[LANG][key]) || I18N.en[key] || key;
const planetName = (p) => (LANG === "ne" ? (PLANET_NE[p] || p) : p);
const signName = (s) => (LANG === "ne" ? SIGNS_NE[s] : SIGNS_EN[s]);
const bi = (obj) => (obj ? (obj[LANG] || obj.en || "") : "");

const STATE = { bundle: null, birthPayload: null, match: null, varga: "D1",
                chartStyle: localStorage.getItem("vedic-astro-style") || "nepali",
                prashna: null };

/* ---------------- Starfield ---------------- */
(function starfield() {
  const canvas = document.getElementById("starfield");
  const ctx = canvas.getContext("2d");
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  /* Phase 5: on the light ivory stage the "stars" are fine gold/violet
     dust motes — pale starlight would vanish against the cream page. */
  const DUST = ["#C9A227", "#7C3AED", "#B8860B"];
  let stars = [], w = 0, h = 0, raf = null;
  function resize() {
    w = canvas.width = window.innerWidth;
    h = canvas.height = window.innerHeight;
    stars = Array.from({ length: Math.min(170, w / 8) }, () => ({
      x: Math.random() * w, y: Math.random() * h,
      r: Math.random() * 1.0 + 0.3, p: Math.random() * Math.PI * 2,
      s: 0.4 + Math.random() * 0.8,
      c: DUST[(Math.random() * DUST.length) | 0],
    }));
    draw(0);
  }
  function draw(time) {
    ctx.clearRect(0, 0, w, h);
    for (const st of stars) {
      const a = 0.16 + 0.34 * Math.abs(Math.sin(st.p + time * 0.0004 * st.s));
      ctx.globalAlpha = a;
      ctx.fillStyle = st.c;
      ctx.beginPath();
      ctx.arc(st.x, st.y, st.r, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.globalAlpha = 1;
    if (!reduced) raf = requestAnimationFrame(draw);
  }
  window.addEventListener("resize", resize);
  resize();
  if (!reduced) raf = requestAnimationFrame(draw);
})();

/* Hero ring signs */
(function heroRing() {
  const g = document.querySelector(".ring-signs");
  if (!g) return;
  const cx = 100, cy = 100, r = 84;
  SIGN_GLYPHS.forEach((glyph, i) => {
    const a = ((i * 30 - 90) * Math.PI) / 180;
    const txt = document.createElementNS("http://www.w3.org/2000/svg", "text");
    txt.setAttribute("x", cx + r * Math.cos(a));
    txt.setAttribute("y", cy + r * Math.sin(a));
    txt.textContent = glyph;
    g.appendChild(txt);
  });
})();

/* ---------------- Language ---------------- */
function applyLang() {
  document.documentElement.lang = LANG === "ne" ? "ne" : "en";
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (I18N[LANG][key]) el.textContent = I18N[LANG][key];
  });
  document.getElementById("lang-en").classList.toggle("is-active", LANG === "en");
  document.getElementById("lang-ne").classList.toggle("is-active", LANG === "ne");
  loadPanchang();
  if (STATE.bundle) renderBundle();
  if (STATE.match) renderMatch();
  if (STATE.prashna) renderPrashna();
}
document.getElementById("lang-en").addEventListener("click", () => { LANG = "en"; localStorage.setItem("vedic-astro-lang", LANG); applyLang(); });
document.getElementById("lang-ne").addEventListener("click", () => { LANG = "ne"; localStorage.setItem("vedic-astro-lang", LANG); applyLang(); });

/* ---------------- Panchang strip ---------------- */
function fmtTime(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  return d.toLocaleTimeString(LANG === "ne" ? "ne-NP" : "en-GB", { hour: "2-digit", minute: "2-digit" });
}
async function loadPanchang() {
  const grid = document.getElementById("panchang-grid");
  try {
    const res = await fetch("/api/panchang?place_id=kathmandu");
    const p = await res.json();
    const items = [
      [t("tithi"), (LANG === "ne" ? (p.paksha === "Shukla" ? "शुक्ल" : "कृष्ण") : p.paksha) + " " + (LANG === "ne" ? TITHI_NE[p.tithi_index] : TITHI_EN[p.tithi_index])],
      [t("nakshatra"), LANG === "ne" ? NAK_NE[p.nakshatra_index] : NAK_EN[p.nakshatra_index]],
      [t("yoga"), LANG === "ne" ? YOGA_NE[p.yoga_index] : YOGA_EN[p.yoga_index]],
      [t("karana"), LANG === "ne" ? (KARANA_NE[p.karana] || p.karana) : p.karana],
      [t("sunrise"), fmtTime(p.sunrise)],
      [t("sunset"), fmtTime(p.sunset)],
    ];
    const wd = LANG === "ne" ? WEEKDAY_NE[p.weekday] : WEEKDAY_EN[p.weekday];
    document.querySelector(".strip-title").textContent = t("panchang_title") + " — " + wd;
    grid.innerHTML = items.map(([k, v]) =>
      `<div class="strip-item"><span class="k">${k}</span><span class="v">${v}</span></div>`).join("");
  } catch (e) {
    grid.innerHTML = `<p class="muted">${t("err_server")}</p>`;
  }
}

/* ---------------- Places: search-as-you-type, anywhere on Earth --------
   The backend merges the built-in gazetteer (entries with an `id`) with
   worldwide OpenStreetMap results (entries with `source: "global"`, each
   carrying lat/lon + its IANA timezone). The selected place is stored as
   a ready-to-submit payload fragment per input:
     {place_id}  or  {place_name, lat, lon, tz}
   Suggestions are real DOM elements (a rendered dropdown), not the
   browser's native datalist popup. */
const PLACE_SELECTED = {};
const placeTimers = {};
/* Async /api/tz lookups still in flight, keyed by place-input id. A submit
   that lands before the lookup resolves would see a tz-less selection and
   wrongly fail; awaiting the pending promise (bounded) makes a selected
   place resolve deterministically. */
const PLACE_TZ_PENDING = {};
function settlePlaceTz(inputId, timeoutMs = 8000) {
  const pending = PLACE_TZ_PENDING[inputId];
  if (!pending) return Promise.resolve();
  delete PLACE_TZ_PENDING[inputId];
  return Promise.race([
    pending,
    new Promise((_, reject) => setTimeout(() => reject(new Error("tz-timeout")), timeoutMs)),
  ]).catch(() => {});
}

const suggestBox = (inputEl) => document.getElementById(inputEl.id + "-suggest");

function closeSuggest(inputEl) {
  const box = suggestBox(inputEl);
  if (box) { box.hidden = true; box.innerHTML = ""; }
}

function selectPlace(inputEl, p) {
  if (p.id) {
    PLACE_SELECTED[inputEl.id] = { place_id: p.id };
    inputEl.value = `${p.name}, ${p.country}`;
  } else {
    const frag = { place_name: p.label || p.name, lat: p.lat, lon: p.lon, tz: p.tz || null };
    PLACE_SELECTED[inputEl.id] = frag;
    inputEl.value = p.label || p.name;
    if (!p.tz) {
      // Land places virtually always resolve; for the rare miss, try the
      // offline resolver, then hand the coordinates to the manual fields.
      // The lookup is registered so a submit that lands before it resolves
      // can wait for it instead of failing on a place that was selected.
      PLACE_TZ_PENDING[inputEl.id] = fetch(`/api/tz?lat=${encodeURIComponent(p.lat)}&lon=${encodeURIComponent(p.lon)}`)
        .then((r) => (r.ok ? r.json() : null))
        .then((d) => {
          const tz = d && d.tz;
          if (tz) {
            frag.tz = tz;
            if (inputEl.id === "f-place") {
              const tzField = document.getElementById("f-tz");
              if (!tzField.value.trim()) tzField.value = tz; // hand-entered wins
            }
          }
          return tz || null;
        })
        .catch(() => null);
      if (inputEl.id === "f-place") {
        document.getElementById("f-lat").value = p.lat;
        document.getElementById("f-lon").value = p.lon;
        document.getElementById("f-lat-dir").value = p.lat < 0 ? "S" : "N";
        document.getElementById("f-lon-dir").value = p.lon < 0 ? "W" : "E";
        document.getElementById("manual-coords").open = true;
      }
    }
  }
  closeSuggest(inputEl);
}

async function searchPlaces(inputEl) {
  const q = inputEl.value.trim();
  const box = suggestBox(inputEl);
  if (!box || q.length < 2) { closeSuggest(inputEl); return; }
  let data;
  try {
    const res = await fetch("/api/places?q=" + encodeURIComponent(q));
    if (!res.ok) { closeSuggest(inputEl); return; }
    data = await res.json();
  } catch (e) { closeSuggest(inputEl); return; }
  if (inputEl.value.trim() !== q) return;  // user typed on meanwhile
  box.innerHTML = "";
  for (const p of data.places || []) {
    const item = document.createElement("button");
    item.type = "button";
    item.className = "place-item";
    item.setAttribute("role", "option");
    const nameEl = document.createElement("span");
    nameEl.className = "place-item-name";
    nameEl.textContent = p.id ? `${p.name}, ${p.country}` : (p.label || p.name);
    const metaEl = document.createElement("span");
    metaEl.className = "place-item-meta";
    metaEl.textContent = p.tz || "";
    item.append(nameEl, metaEl);
    item.addEventListener("mousedown", (ev) => { ev.preventDefault(); selectPlace(inputEl, p); });
    box.appendChild(item);
  }
  if (data.global_available === false) {
    const hint = document.createElement("div");
    hint.className = "place-item-hint";
    hint.textContent = t("place_global_unavailable");
    box.appendChild(hint);
  }
  box.hidden = box.childElementCount === 0;
}

["f-place", "m1-place", "m2-place", "p-place", "u-place", "c-place"].forEach((id) => {
  const el = document.getElementById(id);
  if (!el) return;
  el.addEventListener("input", () => {
    delete PLACE_SELECTED[id];
    clearTimeout(placeTimers[id]);
    placeTimers[id] = setTimeout(() => searchPlaces(el), 350);
  });
  el.addEventListener("focus", () => {
    if (el.value.trim().length >= 2 && !PLACE_SELECTED[id]) searchPlaces(el);
  });
  el.addEventListener("blur", () => setTimeout(() => closeSuggest(el), 150));
});
document.addEventListener("click", (ev) => {
  ["f-place", "m1-place", "m2-place", "p-place", "u-place", "c-place"].forEach((id) => {
    const el = document.getElementById(id);
    if (el && !el.closest(".place-wrap").contains(ev.target)) closeSuggest(el);
  });
});

function resolvePlace(placeInputId) {
  const sel = PLACE_SELECTED[placeInputId];
  if (!sel) return null;
  if (sel.place_id) return { place_id: sel.place_id };
  if (sel.lat !== undefined && sel.lon !== undefined && sel.tz) {
    return { place_name: sel.place_name, lat: sel.lat, lon: sel.lon, tz: sel.tz };
  }
  return null;
}

/* Manual coordinates: free-form text + N/S/E/W selects, resolved by the
   pure parser in coords.js. The parser always yields ONE signed value
   and the hemisphere it implies; we mirror that hemisphere back into the
   select, so the field and the select can never contradict each other. */
const coordEls = {
  lat: { input: document.getElementById("f-lat"), dir: document.getElementById("f-lat-dir"), kind: "lat" },
  lon: { input: document.getElementById("f-lon"), dir: document.getElementById("f-lon-dir"), kind: "lon" },
};
const coordErrEl = document.getElementById("coord-error");

function readCoord(which) {
  const c = coordEls[which];
  const r = parseCoordinate(c.input.value, c.kind, c.dir.value);
  if (r.ok) c.dir.value = r.direction; // keep the select in sync with the text
  return r;
}

function coordErrorText(r, which) {
  if (r.error === "range") {
    return t(which === "lat" ? "err_coord_lat_range" : "err_coord_lon_range");
  }
  return t("err_coord_invalid");
}

function showCoordError(r, which) {
  coordErrEl.textContent = coordErrorText(r, which);
  coordErrEl.hidden = false;
}
function clearCoordError() { coordErrEl.hidden = true; coordErrEl.textContent = ""; }

/* Auto-fill the IANA timezone from the backend once both fields parse. */
let tzTimer = null;
async function lookupManualTz() {
  const latR = readCoord("lat"), lonR = readCoord("lon");
  if (!latR.ok || !lonR.ok) return;
  clearCoordError();
  try {
    const res = await fetch(`/api/tz?lat=${latR.value}&lon=${lonR.value}`);
    if (res.ok) document.getElementById("f-tz").value = (await res.json()).tz;
  } catch (e) { /* leave the field for manual entry */ }
}
function scheduleTzLookup() {
  clearTimeout(tzTimer);
  tzTimer = setTimeout(lookupManualTz, 400);
}
/* A submit can also land inside the 400ms debounce — run the lookup now
   instead of failing on an empty timezone the user never had a chance to
   fill. A hand-entered timezone always wins over the lookup. */
async function ensureManualTz() {
  try {
    if (document.getElementById("f-tz").value.trim()) return;
    clearTimeout(tzTimer);
    await lookupManualTz();
  } catch (e) { /* a timezone hint must never break submission */ }
}
["lat", "lon"].forEach((which) => {
  const c = coordEls[which];
  c.input.addEventListener("input", () => { clearCoordError(); scheduleTzLookup(); });
  c.input.addEventListener("change", () => {
    const r = readCoord(which);
    if (!r.ok && r.error !== "empty") showCoordError(r, which);
    else if (r.ok) clearCoordError();
  });
  c.dir.addEventListener("change", () => { clearCoordError(); scheduleTzLookup(); });
});

/* ---------------- Birth form ---------------- */
/* Typed fetch for /api/kundali. Render's free tier sleeps when idle and
   can take ~90s to wake, so the budget is 120s and a wake-up failure
   (timeout, network drop, 5xx, or a non-JSON error page from a deploy)
   is retried once automatically instead of failing the user. A 4xx is
   the user's input and is never retried. */
async function fetchKundaliOnce(payload, timeoutMs) {
  const ctl = new AbortController();
  const timer = setTimeout(() => ctl.abort(), timeoutMs);
  try {
    const res = await fetch("/api/kundali", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload), signal: ctl.signal,
    });
    if (!res.ok) {
      const e = new Error("http"); e.status = res.status; throw e;
    }
    try { return await res.json(); }
    catch (e) { throw new Error("badjson"); }
  } finally { clearTimeout(timer); }
}
function isRetryableKundaliError(e) {
  // Name-based (not just instanceof) so the check also holds across realms;
  // fetch network failures reject with a TypeError in browsers.
  return !!e && (e.name === "AbortError" || e.name === "TypeError" || e instanceof TypeError ||
    e.message === "badjson" || (e.status && e.status >= 500));
}
async function fetchKundaliWithRetry(payload, onRetry) {
  try {
    return await fetchKundaliOnce(payload, 120000);
  } catch (e) {
    if (!isRetryableKundaliError(e)) throw e;
    if (onRetry) onRetry();
    return fetchKundaliOnce(payload, 120000);
  }
}

document.getElementById("birth-form").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const errEl = document.getElementById("form-error");
  errEl.hidden = true;
  const name = document.getElementById("f-name").value.trim();
  const dob = document.getElementById("f-dob").value;
  const tob = document.getElementById("f-tob").value;
  if (!dob || !tob) { errEl.textContent = t("err_fields"); errEl.hidden = false; return; }
  let payload = { name, dob, tob };
  payload.ayanamsa = document.getElementById("f-ayanamsa").value;
  payload.house_system = document.getElementById("f-house").value;
  await settlePlaceTz("f-place");
  let place = resolvePlace("f-place");
  if (!place) {
    // The place may be selected but its async timezone lookup hadn't landed
    // yet (or the manual-coords debounce hadn't fired): resolve it now.
    await ensureManualTz();
    place = resolvePlace("f-place");
  }
  if (place) {
    payload = { ...payload, ...place };
  } else {
    const tz = document.getElementById("f-tz").value.trim();
    const latR = readCoord("lat"), lonR = readCoord("lon");
    if (latR.ok && lonR.ok && tz) {
      payload = { ...payload, lat: latR.value, lon: lonR.value, tz };
    } else if (!latR.ok && latR.error !== "empty") {
      showCoordError(latR, "lat"); return;
    } else if (!lonR.ok && lonR.error !== "empty") {
      showCoordError(lonR, "lon"); return;
    } else { errEl.textContent = t("err_place"); errEl.hidden = false; return; }
  }
  const btn = document.getElementById("submit-btn");
  btn.disabled = true; btn.textContent = t("generating");
  try {
    const bundle = await fetchKundaliWithRetry(payload, () => {
      btn.textContent = t("waking");
      errEl.textContent = t("err_waking"); errEl.hidden = false;
    });
    errEl.hidden = true;
    STATE.bundle = bundle;
    STATE.birthPayload = payload;
    saveCurrentChart();
    /* Unhide BEFORE rendering: a partial render (with per-section notes)
       is still a chart, and must not be hidden behind a generic error. */
    document.getElementById("results").hidden = false;
    document.getElementById("premium").hidden = false;
    const coreOk = renderBundle();
    if (!coreOk) { errEl.textContent = t("err_incomplete"); errEl.hidden = false; }
    revealSection(document.getElementById("results"));
    revealSection(document.getElementById("premium"));
    document.getElementById("results").scrollIntoView({ behavior: "smooth" });
  } catch (e) {
    if (e.status === 400 || e.status === 422) errEl.textContent = t("err_input");
    else if (e.name === "AbortError" || e instanceof TypeError) errEl.textContent = t("err_timeout");
    else errEl.textContent = t("err_server");
    errEl.hidden = false;
  } finally {
    btn.disabled = false; btn.textContent = t("submit");
  }
});

/* ---------------- Kundali charts (SVG) -------------------------------
   Three styles, one geometry family tree:
   * "nepali" (default) — the authentic Nepali janma-patri presentation:
     North-Indian fixed-house diamond, Lagna top-centre, houses counted
     counterclockwise, sign name + number in every cell, and each planet
     written WITH its degree-in-sign, the way Nepali apps (Mero Jyotish)
     and printed patris show it.
   * "north" — the same diamond, compact software style (abbreviations
     only, no degrees).
   * "south" — South-Indian fixed-sign square grid: signs never move,
     the Lagna sign is marked and houses count clockwise from it.     */
const HOUSE_REGIONS = [
  { poly: "200,0 300,100 100,100", label: [200, 62], sign: [200, 24] },
  { poly: "0,0 200,0 100,100", label: [100, 46], sign: [28, 24] },
  { poly: "0,0 100,100 0,200", label: [42, 104], sign: [16, 60] },
  { poly: "0,200 100,100 100,300", label: [58, 204], sign: [18, 168] },
  { poly: "0,200 100,300 0,400", label: [42, 296], sign: [16, 340] },
  { poly: "0,400 100,300 200,400", label: [100, 352], sign: [30, 382] },
  { poly: "200,400 100,300 300,300", label: [200, 336], sign: [200, 380] },
  { poly: "200,400 300,300 400,400", label: [300, 352], sign: [368, 382] },
  { poly: "400,200 300,300 400,400", label: [358, 296], sign: [382, 340] },
  { poly: "400,200 300,100 300,300", label: [342, 204], sign: [380, 168] },
  { poly: "400,0 400,200 300,100", label: [358, 104], sign: [382, 60] },
  { poly: "200,0 400,0 300,100", label: [300, 46], sign: [370, 24] },
];
const ABBR = { Sun: "Su", Moon: "Mo", Mars: "Ma", Mercury: "Me", Jupiter: "Ju", Venus: "Ve", Saturn: "Sa", Rahu: "Ra", Ketu: "Ke" };
const ABBR_NE = { Sun: "सू", Moon: "चं", Mars: "मं", Mercury: "बु", Jupiter: "बृ", Venus: "शु", Saturn: "श", Rahu: "रा", Ketu: "के" };

/* Text anchoring for each house's sign label, so written-out sign names
   stay inside the diamond: left-side houses grow rightwards, right-side
   houses grow leftwards, top/bottom centre houses are centred. */
const SIGN_ANCHORS = ["middle", "start", "start", "start", "start", "start",
                      "middle", "end", "end", "end", "end", "end"];

/* opts: {degrees: {body: degreeInSign}, lagnaDegree, retro: Set, style} */
function diamondSVG(chartMap, opts) {
  const lagnaSign = chartMap["Lagna"];
  const withDeg = opts.style === "nepali";
  let svg = `<svg class="kundali-svg${withDeg ? " nepali" : ""}" viewBox="0 0 400 400" role="img" aria-label="Kundali chart">`;
  HOUSE_REGIONS.forEach((region, idx) => {
    const house = idx + 1;
    const sign = (lagnaSign + house - 1) % 12;
    const bodies = Object.keys(chartMap).filter((k) => k !== "Lagna" && chartMap[k] === sign);
    const isLagna = house === 1;
    svg += `<polygon class="house-poly${isLagna ? " lagna-house" : ""}" points="${region.poly}"/>`;
    const anchor = SIGN_ANCHORS[idx];
    svg += `<text class="sign-name" style="text-anchor:${anchor}" x="${region.sign[0]}" y="${region.sign[1]}">${signName(sign)}</text>`;
    svg += `<text class="sign-num" style="text-anchor:${anchor}" x="${region.sign[0]}" y="${region.sign[1] + 12}">${locNum(sign + 1)}</text>`;
    if (isLagna) {
      const degTxt = withDeg && opts.lagnaDegree != null ? " " + locNum(Math.floor(opts.lagnaDegree)) + "°" : "";
      svg += `<text class="lagna-txt" x="${region.label[0]}" y="${region.label[1] - 16}">${LANG === "ne" ? "लग्न" : "Lagna"}${degTxt}</text>`;
    }
    const labelOf = (b) => {
      let s = (LANG === "ne" ? ABBR_NE[b] : ABBR[b]);
      if (opts.retro && opts.retro.has(b)) s += "ᴿ";
      if (withDeg && opts.degrees && opts.degrees[b] != null) s += " " + locNum(Math.floor(opts.degrees[b])) + "°";
      return s;
    };
    const labels = bodies.map(labelOf);
    const perLine = withDeg ? 2 : 3;
    const lines = [];
    for (let i = 0; i < labels.length; i += perLine) lines.push(labels.slice(i, i + perLine).join(" "));
    lines.forEach((line, li) => {
      svg += `<text class="planet-txt" x="${region.label[0]}" y="${region.label[1] + li * 15}">${line}</text>`;
    });
  });
  svg += "</svg>";
  return svg;
}

/* Bindu-table sign column headers: English names truncate to four letters
   for column width; Nepali names are shown whole — a UTF-16 slice would cut
   Devanagari combining marks (halant, matras) and print broken words like
   "वृश्", "कन्य" or "कुम्" instead of "वृश्चिक", "कन्या", "कुम्भ". */
function signColHeader(i) {
  const name = signName(i);
  return LANG === "ne" ? name : name.slice(0, 4);
}

/* South-Indian fixed-sign grid: sign -> [row, col]; signs never move. */
const SOUTH_POS = { 11: [0, 0], 0: [0, 1], 1: [0, 2], 2: [0, 3], 10: [1, 0],
                    3: [1, 3], 9: [2, 0], 4: [2, 3], 8: [3, 0], 7: [3, 1],
                    6: [3, 2], 5: [3, 3] };

function southSVG(chartMap, opts) {
  const lagnaSign = chartMap["Lagna"];
  let svg = `<svg class="kundali-svg south" viewBox="0 0 400 400" role="img" aria-label="Kundali chart, South Indian style">`;
  svg += `<rect class="house-poly" x="0" y="0" width="400" height="400"/>`;
  for (let i = 1; i < 4; i++) {
    svg += `<line class="grid-line" x1="${i * 100}" y1="0" x2="${i * 100}" y2="400"/>`;
    svg += `<line class="grid-line" x1="0" y1="${i * 100}" x2="400" y2="${i * 100}"/>`;
  }
  svg += `<rect class="centre-cell" x="100" y="100" width="200" height="200"/>`;
  svg += `<text class="centre-txt" x="200" y="192">${LANG === "ne" ? "जन्म कुण्डली" : "Janma Kundali"}</text>`;
  svg += `<text class="centre-sub" x="200" y="216">${opts.captionShort || ""}</text>`;
  Object.entries(SOUTH_POS).forEach(([signStr, [row, col]]) => {
    const sign = +signStr;
    const x = col * 100, y = row * 100;
    const isLagna = sign === lagnaSign;
    if (isLagna) {
      svg += `<rect class="lagna-cell" x="${x}" y="${y}" width="100" height="100"/>`;
      svg += `<line class="lagna-stroke" x1="${x}" y1="${y}" x2="${x + 26}" y2="${y + 26}"/>`;
      svg += `<text class="lagna-txt small" x="${x + 97}" y="${y + 14}" style="text-anchor:end">${LANG === "ne" ? "लग्न" : "Asc"}</text>`;
    }
    svg += `<text class="sign-name" x="${x + 6}" y="${y + 15}">${signName(sign)}</text>`;
    svg += `<text class="sign-num" x="${x + 6}" y="${y + 27}" style="text-anchor:start">${locNum(sign + 1)}</text>`;
    const bodies = Object.keys(chartMap).filter((k) => k !== "Lagna" && chartMap[k] === sign);
    const labels = bodies.map((b) => (LANG === "ne" ? ABBR_NE[b] : ABBR[b]) + (opts.retro && opts.retro.has(b) ? "ᴿ" : ""));
    const lines = [];
    for (let i = 0; i < labels.length; i += 3) lines.push(labels.slice(i, i + 3).join(" "));
    lines.forEach((line, li) => {
      svg += `<text class="planet-txt" x="${x + 50}" y="${y + 48 + li * 15}">${line}</text>`;
    });
  });
  svg += "</svg>";
  return svg;
}

function bundleChartOpts(varga) {
  const b = STATE.bundle;
  const retro = new Set((b?.planets || []).filter((p) => p.retrograde).map((p) => p.planet));
  // Degrees + lagna degree print only on the Rashi (D1) chart — the Nepali
  // janma-patri style; divisional charts stay clean like the reference sites.
  if (varga !== "D1") return { style: STATE.chartStyle, retro, captionShort: varga };
  const degrees = {};
  (b?.planets || []).forEach((p) => { degrees[p.planet] = p.degree_in_sign; });
  return {
    style: STATE.chartStyle, retro, degrees,
    lagnaDegree: b ? b.lagna.degree_in_sign : null, captionShort: varga,
  };
}

function drawChartInto(el, chartMap, varga) {
  if (!el || !chartMap) return; // missing varga data: the section note covers it
  const opts = bundleChartOpts(varga);
  el.innerHTML = STATE.chartStyle === "south" ? southSVG(chartMap, opts) : diamondSVG(chartMap, opts);
}

/* Traditional kundali view: Lagna (D1) + Navamsa (D9) side by side,
   Dashamsa (D10) one tap below — the layout the popular kundali sites use. */
function renderChartPair() {
  const b = STATE.bundle;
  if (!b) return;
  drawChartInto(document.getElementById("chart-d1"), b.charts["D1"], "D1");
  drawChartInto(document.getElementById("chart-d9"), b.charts["D9"], "D9");
  drawChartInto(document.getElementById("chart-d10"), b.charts["D10"], "D10");
  const cap = document.getElementById("chart-caption");
  cap.textContent = STATE.chartStyle === "south" ? t("chart_caption_south") : t("chart_caption_pair");
}
document.querySelectorAll(".mini-btn[data-style]").forEach((btn) => {
  btn.addEventListener("click", () => {
    STATE.chartStyle = btn.dataset.style;
    localStorage.setItem("vedic-astro-style", STATE.chartStyle);
    document.querySelectorAll(".mini-btn[data-style]").forEach((b) => b.classList.toggle("is-active", b === btn));
    if (STATE.bundle) renderChartPair();
  });
});

/* ---------------- Render bundle ---------------- */
function stateText(row) {
  const bits = [];
  if (row.dignity === "exalted") bits.push(t("exalted"));
  else if (row.dignity === "debilitated") bits.push(t("debilitated"));
  else if (row.dignity === "own") bits.push(t("own"));
  if (row.combust) bits.push(t("combust"));
  if (row.retrograde) bits.push(t("retrograde"));
  return bits.length ? bits.join(", ") : t("neutral");
}

/* One failing section must never kill the whole chart (previously a single
   throwing renderer surfaced as the generic "something went wrong" error and
   hid even the sections that had rendered). Each section runs isolated; a
   failure leaves a small named note instead of the chart. */
const SECTION_TITLES = {
  chart: "chart_title", karakas: "karakas_title", dasha: "dasha_title", kp: "kp_title", doshas: "dosha_title",
  av: "av_title", predictions: "pred_title", strength: "strength_title",
  transits: "transit_title", numerology: "numerology_title", lalkitab: "lalkitab_title",
  premium: "premium_title", deep: "deep_planets_title",
  worldclass: "Worldclass · Chalit · Prastara · KP events · Sudarshana",
  gap: "Gap · Argala · Nakshatra · Ashtottari · Sade Sati",
};
function noteSection(name) {
  try {
    const notes = document.getElementById("section-notes");
    if (!notes) return;
    notes.hidden = false;
    const div = document.createElement("div");
    div.className = "section-note";
    const title = SECTION_TITLES[name];
    const label = title && I18N.en[title] ? t(title) : (title || name);
    div.textContent = `${t("section_failed")} — ${label}`;
    notes.appendChild(div);
  } catch (e) { /* notes are best-effort */ }
}
function renderSection(name, fn, b) {
  try { fn(b); return true; }
  catch (e) { noteSection(name); return false; }
}

function renderCore(b) {
  const moon = b.planets.find((p) => p.planet === "Moon");
  document.getElementById("results-title").textContent =
    (b.name ? `${t("results_for")} ${b.name}` : t("results_for")) ;
  document.getElementById("results-meta").textContent =
    `${t("born_at")} ${b.birth.date} · ${b.birth.time} · ${b.birth.place.name} — ` +
    `${t("lagna_word")}: ${signName(b.lagna.sign)} · ${t("moon_word")}: ${signName(moon.sign)} / ${LANG === "ne" ? moon.nakshatra_ne : moon.nakshatra_en}`;

  /* Chart at a glance — the four facts a layperson checks first, in plain
     language, so the chart can be verified without reading the diamond. */
  const sun = b.planets.find((p) => p.planet === "Sun");
  const lordPlanet = SIGN_LORDS[b.lagna.sign];
  const lordRow = b.planets.find((p) => p.planet === lordPlanet);
  const glanceItems = [
    [t("glance_lagna"), signName(b.lagna.sign)],
    [t("glance_moon"), `${signName(moon.sign)} · ${LANG === "ne" ? moon.nakshatra_ne : moon.nakshatra_en} · ${t("pada_word")} ${locNum(moon.pada)}`],
    [t("glance_sun"), signName(sun.sign)],
    [t("glance_lagna_lord"), lordRow ? `${planetName(lordPlanet)} · ${t("house_word")} ${locNum(lordRow.house)}` : "—"],
  ];
  document.getElementById("glance-strip").innerHTML = glanceItems.map(([k, v]) =>
    `<div class="strip-item"><span class="k">${k}</span><span class="v">${v}</span></div>`).join("");

  /* Panchang at birth — tithi, vara, nakshatra, yoga, karana: the five
     limbs every traditional janma-patri prints under the charts. */
  const bp = b.panchang_at_birth;
  if (bp) {
    const tithiName = (LANG === "ne" ? (bp.paksha === "Shukla" ? "शुक्ल " : "कृष्ण ") : bp.paksha + " ") +
      (LANG === "ne" ? TITHI_NE[bp.tithi_index] : TITHI_EN[bp.tithi_index]);
    const bpItems = [
      [t("tithi"), tithiName],
      [t("vara"), LANG === "ne" ? WEEKDAY_NE[bp.weekday] : WEEKDAY_EN[bp.weekday]],
      [t("nakshatra"), `${LANG === "ne" ? NAK_NE[bp.nakshatra_index] : NAK_EN[bp.nakshatra_index]} · ${t("pada_word")} ${locNum(bp.nakshatra_pada)}`],
      [t("yoga"), LANG === "ne" ? YOGA_NE[bp.yoga_index] : YOGA_EN[bp.yoga_index]],
      [t("karana"), LANG === "ne" ? (KARANA_NE[bp.karana] || bp.karana) : bp.karana],
    ];
    document.getElementById("birth-panchang-strip").innerHTML =
      `<div class="strip-title-sm">${t("birth_panchang_title")}</div>` +
      bpItems.map(([k, v]) => `<div class="strip-item"><span class="k">${k}</span><span class="v">${v}</span></div>`).join("");
  }

  renderChartPair();

  const tbody = document.querySelector("#planet-table tbody");
  tbody.innerHTML = b.planets.map((p) => `
    <tr>
      <td><b>${LANG === "ne" ? p.name_ne : p.planet}</b></td>
      <td>${signName(p.sign)}</td>
      <td>${p.degree_in_sign.toFixed(2)}°</td>
      <td>${LANG === "ne" ? p.nakshatra_ne : p.nakshatra_en} · ${p.pada}</td>
      <td>${p.house}</td>
      <td>${stateText(p)}</td>
    </tr>`).join("");

}

function renderKarakas(b) {
  const karakas = Object.entries(b.karakas)
    .map(([k, v]) => `<b>${k}</b>: ${planetName(v)}`).join(" · ");
  document.getElementById("karaka-box").innerHTML =
    `<span>${t("karakas_title")}</span><br>${karakas}`;
}

/* Returns true when the core chart itself rendered. Section failures are
   isolated and noted; only a core failure means "no chart at all". */
function renderBundle() {
  const b = STATE.bundle;
  if (!b) return false;
  const bookName = document.getElementById("book-3d-name");
  if (bookName) bookName.textContent = b.name || t("book_cover_sub");
  const notes = document.getElementById("section-notes");
  if (notes) { notes.hidden = true; notes.innerHTML = ""; }
  let coreOk = false;
  const sections = [
    ["chart", renderCore], ["karakas", renderKarakas], ["dasha", renderDasha], ["kp", renderKP],
    ["doshas", renderDoshasYogas], ["av", renderAV], ["predictions", renderPredictions],
    ["strength", renderStrength], ["transits", renderTransits],
    ["numerology", renderNumerology], ["lalkitab", renderLalKitab],
    ["premium", renderPremium], ["deep", renderDeep],
    ["worldclass", renderWorldclass], ["gap", renderGapLayer],
    ["phase1", renderPhase1],
  ];
  for (const [name, fn] of sections) {
    if (renderSection(name, fn, b) && name === "chart") coreOk = true;
  }
  return coreOk;
}

function renderDasha(b) {
  const cur = b.dasha.current;
  const el = document.getElementById("current-dasha");
  if (cur && cur.mahadasha) {
    let txt = `${t("current_period")}: ${planetName(cur.mahadasha.lord)} ${t("mahadasha")}`;
    if (cur.antardasha) txt += ` · ${planetName(cur.antardasha.lord)} ${t("antardasha")} (${t("until")} ${cur.antardasha.end})`;
    if (cur.pratyantardasha) txt += ` · ${planetName(cur.pratyantardasha.lord)} ${t("pratyantardasha")}`;
    el.textContent = txt;
  }
  const tl = document.getElementById("dasha-timeline");
  tl.innerHTML = b.dasha.mahadashas.map((md) => {
    const isCur = cur && cur.mahadasha && cur.mahadasha.lord === md.lord && cur.mahadasha.start === md.start;
    const width = Math.min(100, (md.years / 20) * 100);
    let ads = "";
    if (isCur) {
      ads = `<div class="tl-dates">${md.antardashas.map((ad) =>
        `${planetName(ad.lord)} ${ad.start} → ${ad.end}`).join("<br>")}</div>`;
    }
    return `<div class="tl-row${isCur ? " is-current" : ""}">
      <div class="tl-head"><span class="lord">${planetName(md.lord)}</span>
      <span class="tl-dates">${md.display_start || md.start} → ${md.end}</span></div>
      <div class="tl-bar"><i style="width:${width}%"></i></div>${ads}</div>`;
  }).join("");

  const yg = b.yogini && b.yogini.current;
  document.getElementById("yogini-line").textContent = yg
    ? `${t("yogini_word")}: ${yg.name} (${planetName(yg.planet)}) · ${yg.start} → ${yg.end}` : "";
  const tb = b.tribhagi && b.tribhagi.current;
  document.getElementById("tribhagi-line").textContent = tb
    ? `${t("tribhagi_word")}: ${planetName(tb.lord)} · ${tb.start} → ${tb.end}` : "";

  document.getElementById("dasha-phala").innerHTML = (b.dasha_phala || []).map((e) => {
    let html = `<div class="pred-block"><h4>${planetName(e.lord)} · ${e.start} → ${e.end}</h4>` +
      e.summary.map((f) => `<p>${bi(f)}</p>`).join("");
    if (e.antardashas) {
      html += e.antardashas.map((ad) =>
        `<p class="ad-line"><b>${planetName(ad.lord)}</b> ${ad.start} → ${ad.end}</p>` +
        ad.summary.map((f) => `<p>${bi(f)}</p>`).join("")).join("");
    }
    return html + "</div>";
  }).join("");
}

function renderKP(b) {
  const tbody = document.querySelector("#kp-table tbody");
  tbody.innerHTML = b.kp.cusps.map((c) => `
    <tr><td>${c.house}</td><td>${LANG === "ne" ? c.sign_ne : c.sign_en}</td>
    <td>${planetName(c.sign_lord)}</td><td>${planetName(c.star_lord)}</td>
    <td><b>${planetName(c.sub_lord)}</b></td></tr>`).join("");
  const kpCard = document.querySelector("#kp-table").closest(".card");
  if (kpCard && !kpCard.querySelector(".kp-placidus-note")) {
    const p = document.createElement("p");
    p.className = "hint kp-placidus-note";
    p.textContent = t("kp_placidus_note");
    kpCard.appendChild(p);
  }
}

/* Phase 1 — classical calculation core: special lagnas, upagrahas,
   house cusps, all computed under the selected ayanamsa. */
function renderPhase1(b) {
  const note = document.getElementById("calc-settings-note");
  if (note && b.ayanamsa && b.house_system) {
    note.textContent = t("calc_settings")
      .replace("{aya}", b.ayanamsa.name).replace("{hs}", b.house_system.name);
  }
  const LAGNA_KEYS = [
    ["hora_lagna", "lagna_hora", "use_hora"],
    ["bhava_lagna", "lagna_bhava", "use_bhava"],
    ["ghati_lagna", "lagna_ghati", "use_ghati"],
    ["varnada_lagna", "lagna_varnada", "use_varnada"],
    ["shri_lagna", "lagna_shri", "use_shri"],
    ["indu_lagna", "lagna_indu", "use_indu"],
  ];
  const cl = b.classical_lagnas;
  document.querySelector("#classical-lagnas-table tbody").innerHTML = cl
    ? LAGNA_KEYS.map(([k, nk, uk]) => {
        const v = cl[k];
        return `<tr><td><b>${t(nk)}</b></td><td>${signName(v.sign)}</td>` +
          `<td>${v.degree_in_sign.toFixed(2)}°</td><td>${t(uk)}</td></tr>`;
      }).join("")
    : "";
  const UP_KEYS = [
    ["dhuma", "up_dhuma", null], ["vyatipata", "up_vyatipata", null],
    ["parivesha", "up_parivesha", null], ["indrachapa", "up_indrachapa", null],
    ["upaketu", "up_upaketu", null],
    ["gulika", "up_gulika", "note_gulika"], ["mandi", "up_mandi", "note_mandi"],
  ];
  document.querySelector("#upagrahas-table tbody").innerHTML = UP_KEYS.map(([k, nk, nnk]) => {
    const v = b.upagrahas[k];
    if (!v) return `<tr><td><b>${t(nk)}</b></td><td colspan="3">—</td></tr>`;
    return `<tr><td><b>${t(nk)}</b></td><td>${signName(v.sign)}</td>` +
      `<td>${v.degree_in_sign.toFixed(2)}°</td><td>${nnk ? t(nnk) : "—"}</td></tr>`;
  }).join("");
  document.querySelector("#house-cusps-table tbody").innerHTML = b.house_cusps.map((c) =>
    `<tr><td><b>${c.cusp}</b></td><td>${signName(c.sign)}</td>` +
    `<td>${c.degree_in_sign.toFixed(2)}°</td></tr>`).join("");
}

function renderDoshasYogas(b) {
  const d = b.doshas;
  const rows = [
    ["manglik", d.manglik.present, d.manglik.strength + (d.manglik.cancellations.length ? " · " + d.manglik.cancellations.join("; ") : "")],
    ["kaal_sarp", d.kaal_sarp.present, d.kaal_sarp.present ? (d.kaal_sarp.type + " · Rahu house " + d.kaal_sarp.rahu_house) : ""],
    ["sade_sati", d.sade_sati.active, d.sade_sati.active ? (d.sade_sati.phase || "") : (d.sade_sati.dhaiya ? "Dhaiya (4th/8th Saturn)" : "")],
    ["pitra", d.pitra.present, d.pitra.patterns.join("; ")],
  ];
  document.getElementById("dosha-cards").innerHTML = rows.map(([key, present, detail]) => `
    <div class="dosha-badge ${present ? "present" : "absent"}">
      <span class="st">${t("doshas")[key]} — ${present ? t("present") : t("absent")}</span>
      ${detail ? `<small>${detail}</small>` : ""}
    </div>`).join("");
  document.getElementById("yoga-list").innerHTML = b.yogas.length
    ? b.yogas.map((y) => `<div class="yoga-item"><b>${y.name}</b><span>${y.basis}</span></div>`).join("")
    : `<p class="muted">—</p>`;
}

function renderAV(b) {
  const av = b.ashtakavarga;
  const head = document.getElementById("av-head");
  head.innerHTML = `<th>${t("th_planet")}</th>` + SIGNS_EN.map((_, i) => `<th>${signColHeader(i)}</th>`).join("");
  const rows = Object.keys(av);
  document.querySelector("#av-table tbody").innerHTML = rows.map((name) => {
    const label = name === "Sarvashtakavarga" ? t("sarva") : planetName(name);
    return `<tr><td><b>${label}</b></td>${av[name].map((v) => `<td class="${v >= 5 ? "hot" : ""}">${v}</td>`).join("")}</tr>`;
  }).join("");
}

function renderPredictions(b) {
  const wrap = document.getElementById("prediction-sections");
  const titles = t("pred_sections");
  wrap.innerHTML = Object.entries(b.predictions)
    .filter(([, facts]) => facts && facts.length)
    .map(([key, facts]) => `
      <div class="pred-block"><h4>${titles[key] || key}</h4>
      ${facts.map((f) => `<p>${bi(f)}</p>`).join("")}</div>`).join("");
}

/* ---------------- Premium strengths, transits, Lal Kitab, numerology --- */
const PLANET_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"];

function renderStrength(b) {
  const sb = b.strength.shadbala;
  const rows = PLANET_ORDER.map((p) => sb.planets[p]);
  document.getElementById("strength-summary").textContent =
    `${t("strongest_word")}: ${planetName(sb.strongest)} (${sb.planets[sb.strongest].rupas}) · ` +
    `${t("weakest_word")}: ${planetName(sb.weakest)} (${sb.planets[sb.weakest].rupas})`;
  document.querySelector("#shadbala-table tbody").innerHTML = PLANET_ORDER.map((p) => {
    const r = sb.planets[p];
    return `<tr><td><b>${planetName(p)}</b></td><td>${r.sthana.total.toFixed(1)}</td><td>${r.dig.toFixed(1)}</td>` +
      `<td>${r.kala.total.toFixed(1)}</td><td>${r.cheshta.toFixed(1)}</td><td>${r.naisargika.toFixed(1)}</td>` +
      `<td>${r.drik.toFixed(1)}</td><td>${r.total_virupas.toFixed(1)}</td><td><b>${r.rupas.toFixed(2)}</b></td>` +
      `<td>${r.min_rupas.toFixed(1)}</td><td>${r.ratio.toFixed(2)}</td><td>${locNum(r.rank)}</td>` +
      `<td>${r.ishta.toFixed(1)}</td><td>${r.kashta.toFixed(1)}</td></tr>`;
  }).join("");
  document.querySelector("#bhava-bala-table tbody").innerHTML = b.strength.bhava_bala.map((h) =>
    `<tr><td>${locNum(h.house)}</td><td>${planetName(h.lord)}</td><td>${h.lord_bala_rupas.toFixed(2)}</td>` +
    `<td>${h.drik_bala_rupas.toFixed(2)}</td><td><b>${h.total_rupas.toFixed(2)}</b></td></tr>`).join("");
  document.getElementById("bhava-bala-note").textContent = bi(b.strength.bhava_bala_note);
  document.querySelector("#vimshopaka-table tbody").innerHTML = PLANET_ORDER.map((p) => {
    const v = b.strength.vimshopaka[p];
    return `<tr><td><b>${planetName(p)}</b></td><td>${v.shadvarga.toFixed(2)}</td><td>${v.saptavarga.toFixed(2)}</td><td>${v.shodashavarga.toFixed(2)}</td></tr>`;
  }).join("");
}

function renderTransits(b) {
  document.querySelector("#transit-table tbody").innerHTML = b.transits_detail.ingress.map((r) =>
    `<tr><td><b>${planetName(r.planet)}</b></td><td>${LANG === "ne" ? r.current_sign_ne : r.current_sign_en}</td>` +
    `<td>${locNum(r.house_from_moon)}</td><td>${r.next_ingress_date} → ${LANG === "ne" ? r.next_sign_ne : r.next_sign_en}</td></tr>`).join("");
  const ss = b.doshas.sade_sati;
  const note = document.getElementById("dhaiya-note");
  if (ss.dhaiya) {
    note.textContent = LANG === "ne"
      ? "ढैया (कण्टक शनि) सक्रिय छ — गोचरको शनि चन्द्र राशिबाट चौथो/आठौँ स्थानमा छ।"
      : "Dhaiya (Kantaka Shani) is active — transiting Saturn is in the 4th/8th sign from your Moon sign.";
  } else if (ss.active) {
    note.textContent = LANG === "ne" ? `साढेसाती सक्रिय छ (${ss.phase})।` : `Sade Sati is active (${ss.phase} phase).`;
  } else {
    note.textContent = "";
  }
}

function renderNumerology(b) {
  const n = b.numerology, nl = b.name_letters;
  const moon = b.planets.find((p) => p.planet === "Moon");
  const entry = (label, e) =>
    `<p><b>${label}: ${locNum(e.value)}</b> — ${t("ruler_word")}: ${planetName(e.ruler)}<br>${bi(e.trait)}</p>`;
  document.getElementById("numerology-body").innerHTML =
    entry(t("moolank"), n.moolank) + entry(t("bhagyank"), n.bhagyank) +
    `<p><b>${t("name_letter")}: ${LANG === "ne" ? nl.syllable_ne : nl.syllable_en}</b> ` +
    `(${(LANG === "ne" ? moon.nakshatra_ne : moon.nakshatra_en)} · ${t("pada_word")} ${locNum(nl.pada)})<br>` +
    nl.options.map((o) => `${LANG === "ne" ? o.ne : o.en}`).join(" · ") + `</p>`;
}

function renderLalKitab(b) {
  const lk = b.lal_kitab;
  const grid = document.getElementById("lalkitab-chart");
  grid.innerHTML = Array.from({ length: 12 }, (_, i) => {
    const k = i + 1;
    const planets = (lk.chart[String(k)] || []).map((p) => planetName(p)).join(", ");
    return `<div class="lk-cell"><span class="k">${locNum(k)} · ${signName(k - 1)}</span><span class="v">${planets || "—"}</span></div>`;
  }).join("");
  const rows = lk.planets.map((r) =>
    `<div class="yoga-item"><b>${planetName(r.planet)}</b> — ${LANG === "ne" ? "खाना" : "khana"} ${locNum(r.khana)} · ` +
    `${r.state === "jagta" ? t("jagta") : t("soya")}${r.in_pakka_ghar ? " · " + t("pakka_word") + " ✓" : ""}` +
    `<span>${bi(r.reading)}</span></div>`).join("");
  let html = rows;
  if (lk.sleeping_houses.length) {
    html += `<p class="hint">${t("sleeping_houses")}: ${lk.sleeping_houses.map((k) => locNum(k)).join(", ")}</p>`;
  }
  html += `<h4 class="sub-title">${t("rin_title")}</h4>` + lk.rin.map((r) =>
    `<div class="yoga-item"><b>${bi(r.name)}</b> — ${r.detected === true ? t("detected") : (r.detected === null ? t("reference_only") : "—")}` +
    `<span>${t("remedy_word")}: ${bi(r.remedy)}</span></div>`).join("");
  document.getElementById("lalkitab-body").innerHTML = html;
  const tevaEl = document.getElementById("lalkitab-teva");
  if (tevaEl && lk.teva) {
    tevaEl.innerHTML = `<h4 class="sub-title">${t("teva_title")}</h4>` +
      (lk.teva.matched.length ? lk.teva.matched.map((m) =>
        `<div class="yoga-item"><b>${LANG === "ne" ? m.type_ne : m.type}</b> — ${m.formation}<br><span>${bi(m.reading)} ${t("remedy_word")}: ${bi(m.remedy)}</span></div>`).join("")
        : `<p class="hint">—</p>`) +
      `<p class="hint">${bi(lk.teva.variance_note)}</p>`;
  }
  const lkDashaEl = document.getElementById("lalkitab-dasha");
  if (lkDashaEl && b.lal_kitab_dasha) {
    const ld = b.lal_kitab_dasha;
    lkDashaEl.innerHTML = `<h4 class="sub-title">${t("lk_dasha_title")}</h4>` +
      `<p>${ld.current ? `${planetName(ld.current.planet)} ${ld.current.start} – ${ld.current.end}` +
        (ld.current.antardasha ? ` · ${planetName(ld.current.antardasha.planet)} ${t("antardasha_word") || "Antardasha"}` : "") : "—"}</p>` +
      `<p class="hint">${bi(ld.method_note)}</p>`;
  }
}

/* ---------------- Gap-closure layer: Argala, Nakshatra deep-dive, Ashtottari, lifetime Sade Sati --- */
function renderGapLayer(b) {
  if (b.argala) {
    const rows = b.argala.by_house.map((h) =>
      `<tr><td>${locNum(h.house)} — ${bi(h.theme)}</td>` +
      `<td>${h.argala.map((a) => planetName(a.planet) + (a.ketu_reversed ? " (Ketu ↓)" : "") + (a.extended ? " *" : "")).join(", ") || "—"}</td>` +
      `<td>${h.virodhargala.map((v) => planetName(v.planet) + (v.ketu_reversed ? " (Ketu ↓)" : "")).join(", ") || "—"}</td>` +
      `<td>${h.verdict}</td></tr>`).join("");
    document.querySelector("#argala-table tbody").innerHTML = rows;
    document.getElementById("argala-summary").textContent =
      `${b.argala.prevailing_count} / 12 ${LANG === "ne" ? "भावमा अर्गला प्रबल" : "houses with prevailing Argala"} · ` +
      `${b.argala.obstructed_count} ${LANG === "ne" ? "अवरुद्ध" : "obstructed"}`;
  }
  const nd = b.nakshatra_deep;
  if (nd) {
    const nt = nd.nava_tara, tb = nd.tarabala_today, cb = nd.chandrabala_today;
    document.getElementById("nakshatra-deep-body").innerHTML =
      `<p><b>${LANG === "ne" ? "जन्म नक्षत्र" : "Birth nakshatra"}:</b> ${LANG === "ne" ? nt.natal_nakshatra_ne : nt.natal_nakshatra_en} · ` +
      `<b>${LANG === "ne" ? "आजको ताराबल" : "Today's Tarabala"}:</b> ${tb.tara} ${LANG === "ne" ? tb.tara_ne : tb.tara_en} (${tb.verdict}) · ` +
      `<b>${LANG === "ne" ? "आजको चन्द्रबल" : "Today's Chandra Bala"}:</b> ${cb.position} (${cb.verdict})</p>` +
      `<p class="hint">${LANG === "ne" ? "सावधानीका तारा" : "Caution stars"}: ${nt.caution_stars.join(", ")}</p>`;
    document.querySelector("#avastha-table tbody").innerHTML = nd.avasthas.planets.map((r) =>
      `<tr><td><b>${planetName(r.planet)}</b></td><td>${signName(r.sign)}</td>` +
      `<td>${r.balaadi} (${Math.round(r.balaadi_strength * 100)}%)</td><td>${r.jagratadi}</td></tr>`).join("");
  }
  if (b.ashtottari) {
    const a = b.ashtottari, cur = a.current;
    document.getElementById("ashto-current").textContent = cur
      ? `${planetName(cur.mahadasha.lord)} ${cur.mahadasha.start} – ${cur.mahadasha.end}` +
        (cur.antardasha ? ` / ${planetName(cur.antardasha.lord)}` : "")
      : "—";
    const ap = b.ashtottari_applicability;
    document.getElementById("ashto-applicability").textContent = ap
      ? `${LANG === "ne" ? "लागू हुन्छ" : "Applies"}: ${ap.applies ? "✓" : "✗"} · ` +
        `${LANG === "ne" ? "राहु शर्त" : "Rahu condition"}: ${ap.rahu_condition ? "✓" : "✗"} · ` +
        `${LANG === "ne" ? "दिन-रात/पक्ष शर्त" : "Day-night/paksha condition"}: ${ap.day_night_paksha_condition ? "✓" : "✗"}`
      : "";
    document.getElementById("ashto-timeline").innerHTML = a.mahadashas.map((m) =>
      `<div class="tl-row"><span class="tl-lord">${planetName(m.lord)}</span> ${m.display_start || m.start} – ${m.end}</div>`).join("");
  }
  if (b.sade_sati_lifetime) {
    document.querySelector("#sade-lifetime-table tbody").innerHTML = b.sade_sati_lifetime.periods.map((p) =>
      `<tr><td><b>${p.status}</b></td><td>${p.start || "—"}</td><td>${p.peak_start || "—"}</td><td>${p.setting_start || "—"}</td><td>${p.end}</td></tr>`).join("");
  }
}
/* ---------------- World-class layer: Chalit, Prastara, KP events, Sudarshana --- */
function renderWorldclass(b) {
  /* Bhava Chalit */
  const ch = b.bhava_chalit;
  if (ch) {
    document.querySelector("#chalit-table tbody").innerHTML = b.planets.map((p) => {
      const row = ch.houses[p.planet];
      return `<tr><td><b>${LANG === "ne" ? p.name_ne : p.planet}</b></td><td>${signName(p.sign)}</td>` +
        `<td>${locNum(row.rashi_house)}</td><td>${locNum(row.chalit_house)}</td>` +
        `<td>${row.shifted ? t("yes") : t("no")}</td></tr>`;
    }).join("");
  }
  /* Prastara */
  const pr = b.prastara;
  if (pr) {
    const sel = document.getElementById("prastara-planet");
    if (!sel.options.length) {
      PLANET_ORDER.forEach((p) => {
        const o = document.createElement("option");
        o.value = p; o.textContent = planetName(p); sel.appendChild(o);
      });
      sel.addEventListener("change", () => renderPrastaraGrid(b));
    }
    renderPrastaraGrid(b);
  }
  /* KP events */
  const ev = b.kp_events;
  if (ev) {
    document.getElementById("kp-events-body").innerHTML = Object.values(ev).map((e) => `
      <div class="pred-block"><h4>${LANG === "ne" ? e.event_ne : e.event_en} — ${LANG === "ne" ? e.verdict_ne : e.verdict}</h4>
      <p>${bi(e.summary)}</p></div>`).join("");
  }
  /* Sudarshana */
  const sd = b.sudarshana;
  if (sd) {
    document.querySelector("#sudarshana-table tbody").innerHTML = Object.entries(sd.planets).map(([p, r]) => `
      <tr><td><b>${planetName(p)}</b></td><td>${signName(r.sign)}</td>` +
      `<td>${locNum(r.lagna_house)}</td><td>${locNum(r.moon_house)}</td><td>${locNum(r.sun_house)}</td>` +
      `<td>${r.agreement}</td></tr>`).join("");
    document.getElementById("sudarshana-confirmed").textContent = sd.confirmed.length
      ? sd.confirmed.map((c) => `${planetName(c.planet)}: ${t("house_word")} ${locNum(c.house)} (${c.level})`).join(" · ")
      : "—";
    document.getElementById("sudarshana-svg").innerHTML = sudarshanaSvg(sd);
  }
}

function renderPrastaraGrid(b) {
  const planet = document.getElementById("prastara-planet").value || "Sun";
  const entry = b.prastara[planet];
  if (!entry) return;
  const head = document.getElementById("prastara-head");
  head.innerHTML = `<th>${t("th_planet")}</th>` + SIGNS_EN.map((_, i) => `<th>${signColHeader(i)}</th>`).join("");
  let rows = Object.entries(entry.grid).map(([c, row]) => {
    const label = c === "Lagna" ? t("lagna_word") : planetName(c);
    return `<tr><td><b>${label}</b></td>${row.map((v) => `<td class="${v ? "hot" : ""}">${v}</td>`).join("")}</tr>`;
  }).join("");
  rows += `<tr><td><b>BAV</b></td>${entry.bav.map((v) => `<td><b>${v}</b></td>`).join("")}</tr>`;
  rows += `<tr><td><b>${LANG === "ne" ? "घटाइएको" : "Reduced"}</b></td>${entry.reduced.map((v) => `<td><b>${v}</b></td>`).join("")}</tr>`;
  document.querySelector("#prastara-table tbody").innerHTML = rows;
  document.getElementById("prastara-totals").textContent =
    `${planetName(planet)}: BAV ${entry.bav.reduce((a, x) => a + x, 0)} → ${LANG === "ne" ? "घटाइएको" : "reduced"} ${entry.reduced_total}`;
}

const PLANET_GLYPHS = { Sun: "☉", Moon: "☽", Mars: "♂", Mercury: "☿", Jupiter: "♃", Venus: "♀", Saturn: "♄", Rahu: "Rā", Ketu: "Ke" };
function sudarshanaSvg(sd) {
  const C = 150, rings = [
    { r0: 138, r1: 104, key: "lagna_house", label: "Lagna" },
    { r0: 102, r1: 68, key: "moon_house", label: "Moon" },
    { r0: 66, r1: 32, key: "sun_house", label: "Sun" },
  ];
  let s = `<svg viewBox="0 0 300 300" class="sud-svg" role="img" aria-label="Sudarshana Chakra">`;
  for (const ring of rings) {
    s += `<circle cx="${C}" cy="${C}" r="${ring.r0}" fill="none" stroke="var(--gold)" stroke-opacity="0.55"/>` +
      `<circle cx="${C}" cy="${C}" r="${ring.r1}" fill="none" stroke="var(--gold)" stroke-opacity="0.35"/>`;
    for (let h = 1; h <= 12; h++) {
      const a = ((h - 1) * 30 - 90) * Math.PI / 180;
      const x1 = C + ring.r1 * Math.cos(a), y1 = C + ring.r1 * Math.sin(a);
      const x2 = C + ring.r0 * Math.cos(a), y2 = C + ring.r0 * Math.sin(a);
      s += `<line x1="${x1.toFixed(1)}" y1="${y1.toFixed(1)}" x2="${x2.toFixed(1)}" y2="${y2.toFixed(1)}" stroke="var(--gold)" stroke-opacity="0.3"/>`;
    }
    const la = (-90 + 15) * Math.PI / 180;
    s += `<text x="${(C + (ring.r0 + 2) * Math.cos(la)).toFixed(1)}" y="${(C + (ring.r0 + 2) * Math.sin(la)).toFixed(1)}" class="sud-label" text-anchor="middle">${ring.label} 1</text>`;
  }
  for (const [p, r] of Object.entries(sd.planets)) {
    for (const ring of rings) {
      const h = r[ring.key];
      const a = ((h - 1) * 30 - 75) * Math.PI / 180;
      const rm = (ring.r0 + ring.r1) / 2;
      s += `<text x="${(C + rm * Math.cos(a)).toFixed(1)}" y="${(C + rm * Math.sin(a)).toFixed(1)}" class="sud-glyph" text-anchor="middle" dominant-baseline="middle">${PLANET_GLYPHS[p] || p}</text>`;
    }
  }
  return s + "</svg>";
}

function renderPremium(b) {
  const rep = b.report;
  const lucky = rep.lucky;
  document.getElementById("lucky-strip").innerHTML = [
    [t("lucky").number, bi(lucky.number)], [t("lucky").colour, bi(lucky.colour)],
    [t("lucky").day, bi(lucky.day)], [t("lucky").deity, bi(lucky.deity)],
  ].map(([k, v]) => `<div class="lucky-item"><span class="k">${k}</span><span class="v">${v}</span></div>`).join("");

  const ct = t("chapters");
  document.getElementById("premium-chapters").innerHTML = Object.entries(rep.chapters)
    .filter(([, facts]) => facts && facts.length)
    .map(([key, facts]) => `
      <div class="chapter-block"><h4>${ct[key] || key}</h4>
      ${facts.map((f) => `<p>${bi(f)}</p>`).join("")}</div>`).join("");

  document.getElementById("year-ahead").innerHTML = (rep.year_ahead || []).length
    ? `<div class="pred-block">${rep.year_ahead.map((f) => `<p>${bi(f)}</p>`).join("")}</div>`
    : `<p class="muted">—</p>`;

  document.getElementById("forecast-list").innerHTML = rep.favourable_periods.map((f) => `    <div class="fc-row"><span class="yr">${f.year}</span> — ${planetName(f.mahadasha)}${f.antardasha ? " / " + planetName(f.antardasha) : ""}
    <p>${bi(f.summary)}</p></div>`).join("");

  document.getElementById("varshphal-list").innerHTML = rep.varshphal.map((v) => `
    <div class="fc-row"><span class="yr">${v.year}</span> — ${LANG === "ne" ? v.varsha_lagna.sign_ne : v.varsha_lagna.sign_en}
    · ${t("year_lord")}: ${planetName(v.year_lord)} · ${t("muntha")}: ${v.muntha.house}${LANG === "ne" ? "" : " " + t("house_word")}
    <p>${bi(v.reading)}</p>` +
    (v.panchadhikari ? `<p><b>${LANG === "ne" ? "पञ्चाधिकारी वर्ष स्वामी" : "Panchadhikari Year Lord"}:</b> ${planetName(v.panchadhikari.year_lord)}` +
      (v.panchadhikari.fallback_to_muntha ? ` (${LANG === "ne" ? "मुन्था पूर्वनिर्धारित" : "Muntha default"})` : "") +
      ` · <b>Tajika:</b> ${v.tajika.favourable_count} ${LANG === "ne" ? "शुभ" : "favourable"} / ${v.tajika.unfavourable_count} ${LANG === "ne" ? "अशुभ" : "unfavourable"}` +
      (v.tajika.patterns.length ? ` · ${v.tajika.patterns.map((pt) => LANG === "ne" ? pt.pattern_ne : pt.pattern).join(", ")}` : "") + `</p>` +
      `<p>${Object.entries(v.sahams).map(([k, s]) => `${k}: ${signName(s.sign)} (${s.strength})`).join(" · ")}</p>` : "") +
    `</div>`).join("");
  const gemEl = document.getElementById("gem-guide-body");
  if (gemEl && rep.gemstones) {
    gemEl.innerHTML = rep.gemstones.planets.map((g) =>
      `<div class="gem-item"><b>${planetName(g.planet)}</b> — ${bi(g.stone)} · ${g.weight_ratti} (${g.weight_carat_approx}) · ` +
      `${bi(g.metal)} · ${bi(g.finger)} · ${bi(g.day)} · ${bi(g.rudraksha.name)} (${g.rudraksha.mukhi})<br>` +
      `<span>${g.mantra_ne} · <i>${g.mantra_transliteration}</i></span>` +
      (g.caution ? `<br><span class="warn">${bi(g.caution)}</span>` : "") +
      (g.chart_role ? `<br><span>${g.chart_role}</span>` : "") + `</div>`).join("") +
      `<p class="hint">${bi(rep.gemstones.conversion_note)}</p>`;
  }

  const r = rep.remedies;
  let html = `<h4>${t("gemstones")}</h4><div class="gem-grid">` + r.gemstones.map((g) => `
    <div class="gem-item"><b>${bi(g.role)}</b>
    ${bi(g.stone)} · ${bi(g.metal)} · ${bi(g.finger)} · ${bi(g.day)} · ${g.weight}</div>`).join("") + "</div>";
  if (r.weak_planet_support && r.weak_planet_support.length) {
    html += `<h4>${t("weak_support_title")}</h4>` + r.weak_planet_support.map((w) => `
      <p><b>${planetName(w.planet)}</b> — ${bi(w.rudraksha)} · ${w.mantra_ne}<br>${bi(w.note)}</p>`).join("");
  }
  html += `<h4>${t("rudraksha")}</h4><p><b>${bi(r.rudraksha.recommendation)}</b> (${planetName(r.rudraksha.for_planet)}) — ${bi(r.rudraksha.reason)}</p>`;
  html += `<h4>${t("mantra")} — ${planetName(r.mantra.for_planet)}</h4><p>${r.mantra.beej_ne}<br><i>${r.mantra.transliteration}</i><br>${bi(r.mantra.instruction)}</p>`;
  if (r.dosha_remedies.length) {
    html += `<h4>${t("dosha_remedies")}</h4>` + r.dosha_remedies.map((dr) => `
      <p><b>${bi(dr.dosha)}</b></p><ul>${dr.items.map((it) => `<li>${bi(it)}</li>`).join("")}</ul>`).join("");
  }
  document.getElementById("remedies-body").innerHTML = html;
}

document.getElementById("pdf-btn").addEventListener("click", () => {
  const p = STATE.birthPayload;
  if (!p) return;
  const q = new URLSearchParams();
  q.set("dob", p.dob); q.set("tob", p.tob); q.set("lang", LANG);
  if (p.name) q.set("name", p.name);
  if (p.ayanamsa) q.set("ayanamsa", p.ayanamsa);
  if (p.house_system) q.set("house_system", p.house_system);
  if (p.place_id) q.set("place_id", p.place_id);
  else {
    q.set("lat", p.lat); q.set("lon", p.lon); q.set("tz", p.tz);
    if (p.place_name) q.set("place_name", p.place_name);
  }
  window.open("/api/report.pdf?" + q.toString(), "_blank");
});

/* ============ Floating book reader (flipbook) ============ */
const bkesc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const BK = { pages: [], spread: 0, busy: false, single: false };

function buildBookPages(b) {
  const ne = LANG === "ne";
  const name = bkesc(b.name || t("book_cover_sub"));
  const birth = b.birth || {}, place = birth.place || {};
  const lagna = b.lagna || {}, moon = (b.planets || [])[1] || {};
  const bp = b.panchang_at_birth || {};
  const tithiName = bp.tithi_index != null
    ? ((ne ? (bp.paksha === "Shukla" ? "शुक्ल " : "कृष्ण ") : (bp.paksha || "") + " ") +
       (ne ? TITHI_NE[bp.tithi_index] : TITHI_EN[bp.tithi_index])) : "—";
  const P = [];
  /* p0 — ornamental left of cover */
  P.push(`<div class="bk-mangala">॥ शुभम् ॥</div><div class="bk-om">ॐ</div>
    <p class="bk-center" style="color:#b85f06">${bkesc(ne ? "श्री गणेशाय नमः" : "Salutations to Lord Ganesha")}</p>`);
  /* p1 — cover */
  P.push(`<div class="bk-mangala">॥ अथ श्री गणेशाय नमः ॥</div><div class="bk-om">ॐ</div>
    <div class="bk-name">${name}</div><div class="bk-sub">${bkesc(t("book_cover_sub"))}</div>
    <div class="bk-meta">${bkesc(birth.date || "")} · ${bkesc(birth.time || "")}<br>${bkesc(place.name || "")}<br><br>
    ${bkesc(t("glance_lagna"))}: <b>${bkesc(signName(lagna.sign))}</b><br>
    ${bkesc(t("glance_moon"))}: <b>${bkesc(signName(moon.sign))}</b></div>`);
  /* p2 — birth details */
  const det = [
    [t("dob"), `${bkesc(birth.date || "—")}`],
    [t("tob"), `${bkesc(birth.time || "—")}`],
    [t("place"), `${bkesc(place.name || "—")}`],
    [t("vara"), bp.weekday != null ? bkesc(ne ? WEEKDAY_NE[bp.weekday] : WEEKDAY_EN[bp.weekday]) : "—"],
    [t("ayanamsa"), "Lahiri"],
  ];
  P.push(`<div class="bk-h">${bkesc(t("birth_details"))}</div><table class="bk-table">` +
    det.map(([k, v]) => `<tr><th>${bkesc(k)}</th><td>${v}</td></tr>`).join("") + `</table>`);
  /* p3 — panchang */
  const pan = [
    [t("tithi"), tithiName],
    [t("nakshatra"), bp.nakshatra_index != null
      ? `${bkesc(ne ? NAK_NE[bp.nakshatra_index] : NAK_EN[bp.nakshatra_index])} · ${bkesc(t("pada_word"))} ${locNum(bp.nakshatra_pada)}` : "—"],
    [t("yoga"), bp.yoga_index != null ? bkesc(ne ? YOGA_NE[bp.yoga_index] : YOGA_EN[bp.yoga_index]) : "—"],
    [t("karana"), bkesc(ne ? (KARANA_NE[bp.karana] || bp.karana || "—") : (bp.karana || "—"))],
  ];
  P.push(`<div class="bk-h">${bkesc(t("birth_panchang_title"))}</div><table class="bk-table">` +
    pan.map(([k, v]) => `<tr><th>${bkesc(k)}</th><td>${v}</td></tr>`).join("") + `</table>`);
  /* p4 — charts */
  const d1 = document.getElementById("chart-d1"), d9 = document.getElementById("chart-d9");
  P.push(`<div class="bk-h">${bkesc(t("charts_title"))}</div>
    <div class="bk-chart">${d1 ? d1.innerHTML : ""}<div class="bk-chart-cap">D1 · ${bkesc(t("rashi_word"))}</div></div>
    <div class="bk-chart">${d9 ? d9.innerHTML : ""}<div class="bk-chart-cap">D9 · ${bkesc(t("navamsa_word"))}</div></div>`);
  /* p5 — planets */
  P.push(`<div class="bk-h">${bkesc(t("planets_title"))}</div><table class="bk-table">
    <tr><th>${bkesc(t("th_planet"))}</th><th>${bkesc(t("th_sign"))}</th><th>°</th><th>${bkesc(t("th_house"))}</th></tr>` +
    (b.planets || []).map((p) => `<tr><td><b>${bkesc(ne ? p.name_ne : p.planet)}</b>${p.retrograde && !["Rahu","Ketu"].includes(p.planet) ? " (R)" : ""}</td>
      <td>${bkesc(signName(p.sign))}</td><td>${Number(p.degree_in_sign).toFixed(1)}°</td><td>${p.house}</td></tr>`).join("") +
    `</table>`);
  /* p6 — yogas */
  const yogas = b.yogas || [];
  P.push(`<div class="bk-h">${bkesc(t("yogas_title"))} (${yogas.length})</div>` +
    (yogas.length ? yogas.slice(0, 8).map((y) =>
      `<p class="bk-yoga"><b>${bkesc(y.name)}</b><br><span style="font-size:11px;color:#6b4a26">${bkesc(y.basis || "").slice(0, 140)}</span></p>`).join("")
      : `<p>${bkesc(t("no_yogas"))}</p>`));
  /* p7 — doshas */
  const dz = b.doshas || {}, dl = [];
  if (dz.manglik) dl.push([t("manglik"), dz.manglik.present ? bkesc(dz.manglik.strength || t("yes")) : t("no")]);
  if (dz.kaal_sarp) dl.push([t("kaal_sarp"), dz.kaal_sarp.present ? bkesc(dz.kaal_sarp.type || t("yes")) : t("no")]);
  if (dz.sade_sati) dl.push([t("sade_sati"), dz.sade_sati.active ? bkesc(dz.sade_sati.phase || t("yes")) : t("no")]);
  if (dz.pitra) dl.push([t("pitra_dosha"), dz.pitra.present ? t("yes") : t("no")]);
  P.push(`<div class="bk-h">${bkesc(t("doshas_title"))}</div><table class="bk-table">` +
    dl.map(([k, v]) => `<tr><th>${bkesc(k)}</th><td>${v}</td></tr>`).join("") + `</table>
    <p style="font-size:11px;color:#6b4a26">${bkesc(t("remedies_hint"))}</p>`);
  /* p8 — dashas */
  const dasha = b.dasha || {}, mds = dasha.mahadashas || [], cur = dasha.current || {};
  const curLine = cur.mahadasha
    ? `<p><b>${bkesc(cur.mahadasha.lord)}</b> ${bkesc(t("mahadasha_word"))}` +
      (cur.antardasha ? ` · <b>${bkesc(cur.antardasha.lord)}</b> ${bkesc(t("antardasha_word"))}` : "") + `</p>` : "";
  P.push(`<div class="bk-h">${bkesc(t("dasha_title"))}</div>${curLine}<table class="bk-table">
    <tr><th>${bkesc(t("mahadasha_word"))}</th><th>${bkesc(t("th_from"))}</th><th>${bkesc(t("th_to"))}</th></tr>` +
    mds.map((m) => `<tr${cur.mahadasha && m.lord === cur.mahadasha.lord ? ` style="background:#fbeed7"` : ""}>
      <td><b>${bkesc(m.lord)}</b></td><td>${bkesc(m.start)}</td><td>${bkesc(m.end)}</td></tr>`).join("") + `</table>`);
  /* p9 — back cover */
  P.push(`<div class="bk-om" style="margin-top:34px">ॐ</div>
    <p class="bk-center" style="color:#7a3c06"><b>॥ ${bkesc(ne ? "समाप्तम्" : "Samaptam") } ॥</b></p>
    <p class="bk-center" style="font-size:11px;color:#6b4a26">${bkesc(t("footer_text")).slice(0, 160)}</p>
    <p class="bk-center" style="margin-top:14px"><button type="button" class="btn btn-saffron" id="bk-pdf-btn" style="font-size:12px;padding:9px 20px">${bkesc(t("pdf_btn"))}</button></p>`);
  return P;
}

function bkSpreadCount() { return BK.single ? BK.pages.length : Math.ceil(BK.pages.length / 2); }

function bkRender(instant) {
  const s = BK.spread, left = document.getElementById("bk-left"), right = document.getElementById("bk-right");
  const book = document.getElementById("bk-book");
  if (BK.single) {
    book.classList.add("single");
    left.hidden = true;
    right.innerHTML = BK.pages[s] || "";
  } else {
    book.classList.remove("single");
    left.hidden = false;
    left.innerHTML = BK.pages[2 * s] || "";
    right.innerHTML = BK.pages[2 * s + 1] || "";
  }
  const n = bkSpreadCount();
  document.getElementById("bk-counter").textContent = `${s + 1} / ${n}`;
  document.getElementById("bk-prev").disabled = s <= 0;
  document.getElementById("bk-next").disabled = s >= n - 1;
}

function bkFlipDone(leaf) {
  leaf.hidden = true;
  leaf.style.transition = "none";
  leaf.style.transform = "";
  leaf.classList.remove("fwd", "bwd");
  BK.busy = false;
}

function bkNext() {
  if (BK.busy || BK.spread >= bkSpreadCount() - 1) return;
  if (BK.single) return bkTurnSingle(1);
  BK.busy = true;
  const s = BK.spread;
  const leaf = document.getElementById("bk-leaf");
  document.getElementById("bk-leaf-front").innerHTML = BK.pages[2 * s + 1] || "";
  document.getElementById("bk-leaf-back").innerHTML = BK.pages[2 * s + 2] || "";
  leaf.hidden = false;
  leaf.classList.add("fwd");
  leaf.style.transition = "none";
  leaf.style.transform = "rotateY(0deg)";
  void leaf.offsetWidth;
  leaf.style.transition = "transform .8s cubic-bezier(.4,.1,.3,1)";
  leaf.style.transform = "rotateY(-180deg)";
  leaf.addEventListener("transitionend", function h(ev) {
    if (ev.propertyName !== "transform") return;
    leaf.removeEventListener("transitionend", h);
    BK.spread = s + 1;
    bkRender();
    bkFlipDone(leaf);
  });
}

function bkPrev() {
  if (BK.busy || BK.spread <= 0) return;
  if (BK.single) return bkTurnSingle(-1);
  BK.busy = true;
  const s = BK.spread;
  const leaf = document.getElementById("bk-leaf");
  document.getElementById("bk-leaf-front").innerHTML = BK.pages[2 * s] || "";
  document.getElementById("bk-leaf-back").innerHTML = BK.pages[2 * s - 1] || "";
  leaf.hidden = false;
  leaf.classList.add("bwd");
  leaf.style.transition = "none";
  leaf.style.transform = "rotateY(0deg)";
  void leaf.offsetWidth;
  leaf.style.transition = "transform .8s cubic-bezier(.4,.1,.3,1)";
  leaf.style.transform = "rotateY(180deg)";
  leaf.addEventListener("transitionend", function h(ev) {
    if (ev.propertyName !== "transform") return;
    leaf.removeEventListener("transitionend", h);
    BK.spread = s - 1;
    bkRender();
    bkFlipDone(leaf);
  });
}

function bkTurnSingle(dir) {
  if (BK.busy) return;
  BK.busy = true;
  const page = document.getElementById("bk-right");
  page.classList.add("bk-turning");
  page.style.transform = `rotateY(${dir > 0 ? "-" : ""}28deg)`;
  page.style.opacity = ".25";
  setTimeout(() => {
    BK.spread += dir;
    bkRender();
    page.style.transform = "rotateY(0deg)";
    page.style.opacity = "1";
    setTimeout(() => { page.classList.remove("bk-turning"); page.style.transform = ""; page.style.opacity = ""; BK.busy = false; }, 200);
  }, 190);
}

function openBook() {
  const b = STATE.bundle;
  if (!b) return;
  BK.pages = buildBookPages(b);
  BK.spread = 0;
  BK.busy = false;
  BK.single = window.innerWidth < 680;
  bkRender();
  document.getElementById("book-modal").hidden = false;
  document.body.style.overflow = "hidden";
}

function closeBook() {
  document.getElementById("book-modal").hidden = true;
  document.body.style.overflow = "";
}

document.getElementById("read-book-btn").addEventListener("click", openBook);
document.getElementById("book-3d").addEventListener("click", openBook);
document.getElementById("book-3d").addEventListener("keydown", (e) => {
  if (e.key === "Enter" || e.key === " ") { e.preventDefault(); openBook(); }
});
document.getElementById("bk-close").addEventListener("click", closeBook);
document.getElementById("bk-backdrop").addEventListener("click", closeBook);
document.getElementById("bk-next").addEventListener("click", bkNext);
document.getElementById("bk-prev").addEventListener("click", bkPrev);
document.getElementById("bk-book").addEventListener("click", (e) => {
  if (e.target.closest("button, a")) return;
  const r = document.getElementById("bk-book").getBoundingClientRect();
  const x = (e.clientX - r.left) / r.width;
  if (BK.single) { (x > 0.5 ? bkNext : bkPrev)(); }
  else {
    const leftHidden = document.getElementById("bk-left").hidden;
    if (!leftHidden && x < 0.5) bkPrev(); else bkNext();
  }
});
document.addEventListener("keydown", (e) => {
  if (document.getElementById("book-modal").hidden) return;
  if (e.key === "Escape") closeBook();
  else if (e.key === "ArrowRight") bkNext();
  else if (e.key === "ArrowLeft") bkPrev();
});
document.getElementById("book-modal").addEventListener("click", (e) => {
  if (e.target && e.target.id === "bk-pdf-btn") document.getElementById("pdf-btn").click();
});
window.addEventListener("resize", () => {
  if (document.getElementById("book-modal").hidden) return;
  const single = window.innerWidth < 680;
  if (single !== BK.single) {
    BK.single = single;
    BK.spread = 0;
    bkRender();
  }
});

/* ---------------- Deep report (interpretation engine v2) ---------------- */
function renderDeep(b) {
  const deep = b.deep_report || {};
  const sl = b.special_lagnas || {};
  const signOf = (s) => signName(s);

  if (sl.arudha_lagna) {
    document.getElementById("special-lagna-line").textContent =
      `${t("arudha_word")}: ${signOf(sl.arudha_lagna.sign)} (${t("house_word_cap")} ${locNum(sl.arudha_lagna.house_from_lagna)}) · ` +
      `${t("upapada_word")}: ${signOf(sl.upapada.sign)} (${t("house_word_cap")} ${locNum(sl.upapada.house_from_lagna)}) · ` +
      `${t("chandra_lagna_word")}: ${signOf(sl.chandra_lagna.sign)}`;
  }
  const sr = deep.special_readings || {};
  document.getElementById("deep-special").innerHTML = ["arudha", "upapada"]
    .filter((k) => sr[k] && sr[k].length)
    .map((k) => `<div class="pred-block"><h4>${k === "arudha" ? t("arudha_word") : t("upapada_word")}</h4>` +
      sr[k].map((f) => `<p>${bi(f)}</p>`).join("") + "</div>").join("");

  const pc = deep.planet_chapters || {};
  document.getElementById("deep-planets").innerHTML =
    ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"]
      .filter((p) => pc[p] && pc[p].length)
      .map((p) => `<div class="chapter-block"><h4>${planetName(p)}</h4>` +
        pc[p].map((f) => `<p>${bi(f)}</p>`).join("") + "</div>").join("");

  document.getElementById("deep-houses").innerHTML = (deep.house_chapters || [])
    .map((row) => `<div class="chapter-block"><h4>${t("house_word_cap")} ${locNum(row.house)} · ${signOf(row.sign)} · ${planetName(row.lord)}</h4>` +
      row.facts.map((f) => `<p>${bi(f)}</p>`).join("") + "</div>").join("");

  const dv = deep.divisional_chapters || {};
  document.getElementById("deep-divisional").innerHTML = Object.values(dv)
    .map((ch) => `<div class="chapter-block"><h4>${bi(ch.title)}</h4>` +
      ch.facts.map((f) => `<p>${bi(f)}</p>`).join("") + "</div>").join("");

  const cd = b.chara_dasha || {};
  const curEl = document.getElementById("chara-current");
  if (cd.current) {
    curEl.textContent = `${t("chara_current")}: ${signOf(cd.current.sign)} (${planetName(cd.current.lord)}) · ` +
      `${cd.current.start} → ${cd.current.end} · ${t("direction_word")}: ${cd.direction}`;
  } else {
    curEl.textContent = "";
  }
  document.getElementById("chara-timeline").innerHTML = (cd.periods || []).slice(0, 12).map((p) => {
    const isCur = cd.current && p.start === cd.current.start;
    return `<div class="tl-row${isCur ? " is-current" : ""}">
      <div class="tl-head"><span class="lord">${signOf(p.sign)}</span>
      <span class="tl-dates">${p.start} → ${p.end} · ${locNum(p.years)}y · ${planetName(p.lord)}</span></div>
      <div class="tl-bar"><i style="width:${Math.min(100, (p.years / 12) * 100)}%"></i></div></div>`;
  }).join("");

  document.getElementById("deep-timing").innerHTML = (deep.timing_synthesis || []).length
    ? `<div class="pred-block">${deep.timing_synthesis.map((f) => `<p>${bi(f)}</p>`).join("")}</div>`
    : `<p class="muted">—</p>`;

  const tp = deep.transit_phala || {};
  document.getElementById("deep-transits").innerHTML =
    ["Saturn","Jupiter","Rahu","Ketu","Mars","Sun"]
      .filter((p) => tp.planets && tp.planets[p])
      .map((p) => `<div class="pred-block"><h4>${planetName(p)}</h4>` +
        tp.planets[p].map((f) => `<p>${bi(f)}</p>`).join("") + "</div>").join("");
  document.getElementById("sade-sati-detail").textContent =
    tp.sade_sati_detail ? bi(tp.sade_sati_detail) : "";
  document.getElementById("double-transit-note").textContent =
    tp.double_transit && tp.double_transit.note ? bi(tp.double_transit.note) : "";

  document.getElementById("deep-av").innerHTML = (deep.ashtakavarga_reading || []).length
    ? `<div class="pred-block">${deep.ashtakavarga_reading.map((f) => `<p>${bi(f)}</p>`).join("")}</div>`
    : `<p class="muted">—</p>`;
}

/* ---------------- Matching ---------------- */
document.getElementById("match-form").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const errEl = document.getElementById("match-error");
  errEl.hidden = true;
  function person(prefix) {
    const dob = document.getElementById(prefix + "-dob").value;
    const tob = document.getElementById(prefix + "-tob").value;
    return settlePlaceTz(prefix + "-place").then(() => {
      const place = resolvePlace(prefix + "-place");
      if (!dob || !tob || !place) return null;
      return { dob, tob, ...place };
    });
  }
  const groom = await person("m1"), bride = await person("m2");
  if (!groom || !bride) { errEl.textContent = t("err_place") + " / " + t("err_fields"); errEl.hidden = false; return; }
  try {
    const res = await fetch("/api/match", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ groom, bride }),
    });
    if (!res.ok) throw new Error("bad");
    STATE.match = await res.json();
    renderMatch();
    document.getElementById("match-result").hidden = false;
    revealSection(document.getElementById("match-result"));
    document.getElementById("match-result").scrollIntoView({ behavior: "smooth" });
  } catch (e) {
    errEl.textContent = t("err_server"); errEl.hidden = false;
  }
});

function renderMatch() {
  const m = STATE.match;
  if (!m) return;
  animateScore(document.getElementById("score-value"), m.total);
  document.getElementById("score-verdict").textContent = LANG === "ne" ? m.verdict_ne : m.verdict_en;
  document.getElementById("match-meta").textContent =
    `${t("groom_moon")}: ${LANG === "ne" ? m.groom.moon_sign_ne : m.groom.moon_sign_en} / ${LANG === "ne" ? m.groom.nakshatra_ne : m.groom.nakshatra_en} · ` +
    `${t("bride_moon")}: ${LANG === "ne" ? m.bride.moon_sign_ne : m.bride.moon_sign_en} / ${LANG === "ne" ? m.bride.nakshatra_ne : m.bride.nakshatra_en}`;
  document.querySelector("#match-table tbody").innerHTML = m.breakdown.map((row) => `
    <tr><td><b>${t("kootas")[row.koota] || row.koota}</b></td>
    <td>${row.score} / ${row.max}</td><td>${bi(row.detail)}</td></tr>`).join("");
  document.getElementById("manglik-note").textContent = bi(m.manglik_note);
  const ext = document.getElementById("match-extended");
  if (ext) {
    const ps = m.papasamya, bm = m.bhava_milan;
    let html = `<div class="pred-block"><h4>Papasamya</h4><p>${t("groom_moon")}: ${ps.groom.total} · ${t("bride_moon")}: ${ps.bride.total} · ${ps.verdict}</p></div>`;
    html += `<div class="pred-block"><h4>Bhava Milan</h4><p>${t("groom_moon")} vs ${t("bride_moon")}: ${bm.groom_moon_vs_bride_lagna} · ${bm.bride_moon_vs_groom_lagna}<br><b>${bm.verdict}</b></p></div>`;
    if (m.dasha_sandhi) {
      const dsLine = (d) => d.in_window && d.nearest
        ? `${d.nearest.level} ${planetName(d.nearest.lord)} ${d.nearest.kind} ${d.nearest.date} (${d.nearest.days_away} ${LANG === "ne" ? "दिन टाढा" : "days away"})`
        : (LANG === "ne" ? "सन्धि छैन" : "no Sandhi in window");
      html += `<div class="pred-block"><h4>Dasha Sandhi</h4><p>${t("groom_moon")}: ${dsLine(m.dasha_sandhi.groom)}<br>${t("bride_moon")}: ${dsLine(m.dasha_sandhi.bride)}</p></div>`;
    }
    html += `<div class="pred-block"><h4>${LANG === "ne" ? "संयुक्त निष्कर्ष" : "Combined verdict"}</h4><p>${bi(m.combined_verdict)}</p></div>`;
    ext.innerHTML = html;
  }
  const porEl = document.getElementById("match-porutham");
  if (porEl && m.porutham) {
    const po = m.porutham;
    porEl.innerHTML = `<h3>${t("porutham_title")}</h3>` +
      `<div class="score-hero"><div class="score-number"><span>${po.total}</span><span class="score-max">/36</span></div>` +
      `<p class="score-verdict">${LANG === "ne" ? po.verdict_ne : po.verdict_en}</p></div>` +
      `<div class="table-scroll"><table class="data-table"><thead><tr><th>${LANG === "ne" ? "पोरुथम" : "Porutham"}</th><th>${t("th_score")}</th><th>${t("th_detail")}</th></tr></thead>` +
      `<tbody>${po.breakdown.map((row) => `<tr><td><b>${LANG === "ne" ? row.porutham_ne : row.porutham}</b></td><td>${row.score} / ${row.max}</td><td>${bi(row.detail)}</td></tr>`).join("")}</tbody></table></div>` +
      (po.rajju_dosha ? `<p class="hint">⚠ Rajju Dosha</p>` : "") +
      (po.vedha_present ? `<p class="hint">⚠ Vedha present</p>` : "");
  }
}

/* ---------------- World-class tools: saved charts, share, horoscope, muhurta, month calendar --- */
const SAVED_KEY = "vedic-astro-charts";
function loadSavedCharts() {
  try { return JSON.parse(localStorage.getItem(SAVED_KEY) || "[]"); } catch { return []; }
}
function renderSavedList() {
  const list = document.getElementById("saved-list");
  if (!list) return;
  const charts = loadSavedCharts();
  list.innerHTML = charts.length ? charts.map((c, i) => `
    <div class="saved-row"><span>${c.name ? `${c.name} — ` : ""}${c.dob} ${c.tob} · ${c.place_name || ""}</span>
    <button type="button" class="mini-btn" data-load="${i}">${t("saved_load")}</button>
    <button type="button" class="mini-btn" data-del="${i}">${t("saved_delete")}</button></div>`).join("")
    : `<p class="hint">${t("saved_empty")}</p>`;
  list.querySelectorAll("[data-load]").forEach((b) => b.addEventListener("click", () => loadSavedChart(charts[+b.dataset.load])));
  list.querySelectorAll("[data-del]").forEach((b) => b.addEventListener("click", () => {
    const next = loadSavedCharts().filter((_, j) => j !== +b.dataset.del);
    localStorage.setItem(SAVED_KEY, JSON.stringify(next)); renderSavedList();
  }));
}
/* Saving must never kill a generation: storage can fail (private mode,
   quota) and a bug here once hid every chart behind the generic error. */
function saveCurrentChart() {
  try {
    const p = STATE.birthPayload;
    if (!p || typeof dedupeCharts !== "function") return;
    const entry = { name: p.name || "", dob: p.dob, tob: p.tob,
      place_name: STATE.bundle && STATE.bundle.birth ? STATE.bundle.birth.place.name : (p.place_name || ""),
      payload: p };
    localStorage.setItem(SAVED_KEY, JSON.stringify(dedupeCharts(loadSavedCharts(), entry)));
    renderSavedList();
  } catch (e) { /* saved charts are a convenience, not the chart itself */ }
}
function loadSavedChart(entry) {
  const p = entry.payload;
  document.getElementById("f-name").value = p.name || "";
  document.getElementById("f-dob").value = p.dob || "";
  document.getElementById("f-tob").value = p.tob || "";
  if (p.place_id) {
    PLACE_SELECTED["f-place"] = { place_id: p.place_id };
    document.getElementById("f-place").value = entry.place_name || "";
  } else {
    document.getElementById("f-place").value = "";
    document.getElementById("f-lat").value = p.lat != null ? String(p.lat) : "";
    document.getElementById("f-lon").value = p.lon != null ? String(p.lon) : "";
    document.getElementById("f-tz").value = p.tz || "";
  }
  document.getElementById("birth-form").requestSubmit();
}
const shareBtn = document.getElementById("share-btn");
if (shareBtn) shareBtn.addEventListener("click", async () => {
  const p = STATE.birthPayload;
  if (!p || typeof buildShareUrl !== "function") return;
  try {
    await navigator.clipboard.writeText(buildShareUrl(window.location.origin, p));
    shareBtn.textContent = t("share_copied");
    setTimeout(() => { shareBtn.textContent = t("share_btn"); }, 2500);
  } catch { /* clipboard unavailable — user can copy from the address bar */ }
});

/* Horoscope */
(function initHoroscope() {
  const signSel = document.getElementById("h-sign");
  const nakSel = document.getElementById("u-nakshatra");
  if (signSel) SIGNS_EN.forEach((_, i) => {
    const o = document.createElement("option"); o.value = i; o.textContent = signName(i); signSel.appendChild(o);
  });
  if (nakSel) {
    const none = document.createElement("option"); none.value = ""; none.textContent = "—"; nakSel.appendChild(none);
    NAK_EN.forEach((n, i) => {
      const o = document.createElement("option"); o.value = i; o.textContent = LANG === "ne" ? NAK_NE[i] : n; nakSel.appendChild(o);
    });
  }
  const moonSel = document.getElementById("u-moonsign");
  if (moonSel) {
    const none = document.createElement("option"); none.value = ""; none.textContent = "—"; moonSel.appendChild(none);
    SIGNS_EN.forEach((_, i) => {
      const o = document.createElement("option"); o.value = i; o.textContent = signName(i); moonSel.appendChild(o);
    });
  }
})();
const horoscopeForm = document.getElementById("horoscope-form");
if (horoscopeForm) horoscopeForm.addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const sign = +document.getElementById("h-sign").value;
  const span = document.getElementById("h-span").value;
  try {
    const res = await fetch(`/api/horoscope?sign=${sign}&span=${span}&tz=${encodeURIComponent(Intl.DateTimeFormat().resolvedOptions().timeZone || "Asia/Kathmandu")}`);
    if (!res.ok) throw new Error("bad");
    const h = await res.json();
    document.getElementById("horoscope-head").textContent = `${signName(h.moon_sign)} — ${h.span} · ${h.start}${h.end !== h.start ? " → " + h.end : ""}`;
    document.getElementById("horoscope-summary").textContent = bi(h.summary);
    document.getElementById("horoscope-areas").innerHTML = Object.entries(h.areas).map(([area, a]) => `
      <div class="pred-block"><h4>${area} — ${LANG === "ne" ? a.rating_ne : a.rating}</h4><p>${bi(a.text)}</p></div>`).join("");
    let extra = "";
    if (h.moon_journey && h.moon_journey.length) extra += `<p class="hint">${LANG === "ne" ? "चन्द्रमाको यात्रा" : "Moon's journey"}: ${h.moon_journey.map((j) => `${j.date}: ${LANG === "ne" ? j.sign_ne : j.sign_en}`).join(" · ")}</p>`;
    if (h.ingresses && h.ingresses.length) extra += `<p class="hint">${h.ingresses.map((g) => `${planetName(g.planet)} → ${LANG === "ne" ? g.to_sign_ne : g.to_sign_en} (${g.date})`).join(" · ")}</p>`;
    document.getElementById("horoscope-extra").innerHTML = extra;
    document.getElementById("horoscope-result").hidden = false;
    revealSection(document.getElementById("horoscope-result"));
  } catch { /* leave the form; the API error surface is the section itself */ }
});

/* Muhurta */
let MUHURTA_DATA = null;
const muhurtaForm = document.getElementById("muhurta-form");
if (muhurtaForm) {
  const today = new Date();
  const iso = (d) => d.toISOString().slice(0, 10);
  document.getElementById("u-from").value = iso(today);
  const plus7 = new Date(today); plus7.setDate(plus7.getDate() + 7);
  document.getElementById("u-to").value = iso(plus7);
  muhurtaForm.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const errEl = document.getElementById("muhurta-error"); errEl.hidden = true;
    const place = resolvePlace("u-place");
    const params = new URLSearchParams({
      date_from: document.getElementById("u-from").value,
      date_to: document.getElementById("u-to").value,
      activity: document.getElementById("u-activity").value,
    });
    if (place && place.place_id) params.set("place_id", place.place_id);
    else if (place && place.lat != null) { params.set("lat", place.lat); params.set("lon", place.lon); if (place.tz) params.set("tz", place.tz); }
    else params.set("tz", Intl.DateTimeFormat().resolvedOptions().timeZone || "Asia/Kathmandu");
    const nak = document.getElementById("u-nakshatra").value;
    if (nak) params.set("birth_nakshatra", nak);
    const ms = document.getElementById("u-moonsign").value;
    if (ms) params.set("birth_moon_sign", ms);
    // Personalised election: reuse the kundali birth details from this session.
    const bp = STATE.birthPayload;
    if (bp && bp.dob && bp.tob) {
      params.set("birth_dob", bp.dob); params.set("birth_tob", bp.tob);
      if (bp.place_id) params.set("birth_place_id", bp.place_id);
      else { if (bp.lat != null) params.set("birth_lat", bp.lat); if (bp.lon != null) params.set("birth_lon", bp.lon); if (bp.tz) params.set("birth_tz", bp.tz); }
    }
    try {
      const res = await fetch(`/api/muhurta?${params}`);
      if (!res.ok) throw new Error("bad");
      MUHURTA_DATA = await res.json();
      const bestList = MUHURTA_DATA.best_election || MUHURTA_DATA.best;
      document.getElementById("muhurta-best").innerHTML = bestList.map((d) => `
        <div class="pred-block"><h4>${d.date} — ${LANG === "ne" ? d.election_grade_ne : d.election_grade} (${t("election_score_word")} ${d.election_score})</h4><p>${d.election_factors.map((f) => bi(f)).join(" · ")}</p></div>`).join("");
      const daySel = document.getElementById("muhurta-day");
      daySel.innerHTML = MUHURTA_DATA.days.map((d) => `<option value="${d.date}">${d.date} (${LANG === "ne" ? d.grade_ne : d.grade})</option>`).join("");
      daySel.onchange = () => renderMuhurtaDay(daySel.value);
      renderMuhurtaDay(daySel.value);
      document.getElementById("muhurta-result").hidden = false;
      revealSection(document.getElementById("muhurta-result"));
    } catch { errEl.textContent = t("err_server"); errEl.hidden = false; }
  });
}
const hhmm = (s) => (s ? String(s).slice(11, 16) : "");
function renderMuhurtaDay(dateStr) {
  const d = MUHURTA_DATA && MUHURTA_DATA.days.find((x) => x.date === dateStr);
  const el = document.getElementById("muhurta-day-detail");
  if (!d || !el) return;
  const segs = (list) => list.map((c) => `${c.lord} ${hhmm(c.start)}–${hhmm(c.end)}`).join(" · ") || "—";
  const wedNote = d.abhijit.wednesday_note
    ? (LANG === "ne" ? " — बुधबार अभिजित् मुहूर्त परम्परागत रूपमा बेवास्ता गरिन्छ" : " — Abhijit is traditionally avoided on Wednesdays") : "";
  el.innerHTML = `<p><b>${LANG === "ne" ? "चन्द्र नक्षत्र" : "Moon nakshatra"}:</b> ${LANG === "ne" ? d.nakshatra_ne : d.nakshatra_en} · <b>${LANG === "ne" ? "तिथि वर्ग" : "Tithi class"}:</b> ${d.tithi_class} · <b>${LANG === "ne" ? "अङ्क" : "Score"}:</b> ${d.score}</p>` +
    `<p><b>${LANG === "ne" ? "राहुकाल" : "Rahu Kaal"}:</b> ${hhmm(d.rahu_kaal.start)}–${hhmm(d.rahu_kaal.end)}</p>` +
    `<p><b>${LANG === "ne" ? "अभिजित" : "Abhijit"}:</b> ${hhmm(d.abhijit.start)}–${hhmm(d.abhijit.end)}${wedNote}</p>` +
    `<p><b>Choghadiya (day):</b> ${segs(d.choghadiya_day)}<br><b>Choghadiya (night):</b> ${segs(d.choghadiya_night)}</p>` +
    `<p><b>Hora:</b> ${d.hora.map((h) => `${planetName(h.lord)} ${hhmm(h.start)}`).join(" · ")}</p>` +
    `<p class="hint">${d.factors.map((f) => `${bi(f)} (${f.points > 0 ? "+" : ""}${f.points})`).join(" · ")}</p>` +
    `<p><b>${t("election_score_word")}:</b> ${d.election_score} (${LANG === "ne" ? d.election_grade_ne : d.election_grade})</p>` +
    `<p class="hint">${(d.election_factors || []).map((f) => `${bi(f)} (${f.points > 0 ? "+" : ""}${f.points})`).join(" · ")}</p>` +
    (d.panchaka ? `<p><b>Panchaka:</b> ${d.panchaka.active ? (LANG === "ne" ? "सक्रिय" : "active") + (d.panchaka.type ? ` (${d.panchaka.type})` : "") : (LANG === "ne" ? "छैन" : "none")}</p>` : "") +
    (d.lagna_strength ? `<p><b>${LANG === "ne" ? "निर्वाचित लग्न" : "Elected Lagna"}:</b> ${signName(d.lagna_strength.lagna_sign)} (${d.lagna_strength.verdict})</p>` : "") +
    (d.dasha_suitability ? `<p><b>Dasha:</b> ${planetName(d.dasha_suitability.mahadasha_lord)} (${d.dasha_suitability.verdict})</p>` : "");
}

/* Month calendar */
(function initCalendar() {
  const ySel = document.getElementById("cal-year"), mSel = document.getElementById("cal-month");
  if (!ySel || !mSel) return;
  const now = new Date();
  for (let y = now.getFullYear() - 1; y <= now.getFullYear() + 1; y++) {
    const o = document.createElement("option"); o.value = y; o.textContent = y; ySel.appendChild(o);
  }
  ySel.value = now.getFullYear();
  SIGNS_EN.forEach((_, i) => {}); // months are not signs; names below
  const MONTH_EN = ["January","February","March","April","May","June","July","August","September","October","November","December"];
  const MONTH_NE = ["जनवरी","फेब्रुअरी","मार्च","अप्रिल","मे","जुन","जुलाई","अगस्ट","सेप्टेम्बर","अक्टोबर","नोभेम्बर","डिसेम्बर"];
  MONTH_EN.forEach((m, i) => {
    const o = document.createElement("option"); o.value = i + 1; o.textContent = LANG === "ne" ? MONTH_NE[i] : m; mSel.appendChild(o);
  });
  mSel.value = now.getMonth() + 1;
})();
const calBtn = document.getElementById("cal-load");
if (calBtn) calBtn.addEventListener("click", async () => {
  const place = resolvePlace("c-place");
  const params = new URLSearchParams({
    year: document.getElementById("cal-year").value,
    month: document.getElementById("cal-month").value,
  });
  if (place && place.place_id) params.set("place_id", place.place_id);
  else if (place && place.lat != null) { params.set("lat", place.lat); params.set("lon", place.lon); if (place.tz) params.set("tz", place.tz); }
  else params.set("tz", Intl.DateTimeFormat().resolvedOptions().timeZone || "Asia/Kathmandu");
  try {
    const res = await fetch(`/api/panchang-month?${params}`);
    if (!res.ok) throw new Error("bad");
    const cal = await res.json();
    document.getElementById("cal-grid").innerHTML = cal.days.map((d) => `
      <div class="cal-cell"><b>${d.date.slice(-2)}</b> ${(LANG === "ne" ? TITHI_NE[d.tithi_index] : TITHI_EN[d.tithi_index])} · ${(LANG === "ne" ? NAK_NE[d.nakshatra_index] : NAK_EN[d.nakshatra_index])}
      ${d.markers.map((m) => `<span class="cal-marker">${m}</span>`).join(" ")}</div>`).join("");
  } catch { /* keep previous grid */ }
});

/* Share-link autoload + saved list on start */
(function initShare() {
  renderSavedList();
  if (typeof parseShareParams !== "function") return;
  const params = parseShareParams(window.location.search);
  if (!params) return;
  document.getElementById("f-name").value = params.name || "";
  document.getElementById("f-dob").value = params.dob || "";
  document.getElementById("f-tob").value = params.tob || "";
  if (params.ayanamsa) document.getElementById("f-ayanamsa").value = params.ayanamsa;
  if (params.house_system) document.getElementById("f-house").value = params.house_system;
  if (params.place_id) {
    PLACE_SELECTED["f-place"] = { place_id: params.place_id };
    document.getElementById("f-place").value = params.place_name || "";
  } else if (params.lat != null) {
    document.getElementById("f-lat").value = String(params.lat);
    document.getElementById("f-lon").value = String(params.lon);
    document.getElementById("f-tz").value = params.tz || "";
  }
  document.getElementById("birth-form").requestSubmit();
})();

/* ---------------- KP Prashna (Horary) ---------------- */
document.getElementById("prashna-form").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const errEl = document.getElementById("prashna-error");
  errEl.hidden = true;
  const number = parseInt(document.getElementById("p-number").value, 10);
  const question = document.getElementById("p-question").value.trim();
  if (!number || number < 1 || number > 249) {
    errEl.textContent = LANG === "ne" ? "कृपया १ देखि २४९ बीचको अङ्क भर्नुहोस्।" : "Please enter a number between 1 and 249.";
    errEl.hidden = false; return;
  }
  const place = await settlePlaceTz("p-place").then(() => resolvePlace("p-place"));
  if (!place) { errEl.textContent = t("err_place"); errEl.hidden = false; return; }
  const btn = document.getElementById("prashna-btn");
  btn.disabled = true; btn.textContent = t("casting");
  try {
    const res = await fetch("/api/prashna", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ number, question, ...place }),
    });
    if (!res.ok) throw new Error("bad");
    STATE.prashna = await res.json();
    renderPrashna();
    document.getElementById("prashna-result").hidden = false;
    revealSection(document.getElementById("prashna-result"));
    document.getElementById("prashna-result").scrollIntoView({ behavior: "smooth" });
  } catch (e) {
    errEl.textContent = t("err_server"); errEl.hidden = false;
  } finally {
    btn.disabled = false; btn.textContent = t("prashna_submit");
  }
});

function renderPrashna() {
  const p = STATE.prashna;
  if (!p) return;
  const degrees = {}, retro = new Set();
  p.planets.forEach((r) => { degrees[r.planet] = r.degree_in_sign; if (r.retrograde) retro.add(r.planet); });
  document.getElementById("prashna-chart-wrap").innerHTML = diamondSVG(p.chart, {
    style: "nepali", degrees, lagnaDegree: p.lagna.degree_in_sign, retro,
  });
  document.getElementById("prashna-meta").textContent =
    `#${locNum(p.number)} · ${t("lagna_word")}: ${LANG === "ne" ? p.lagna.sign_ne : p.lagna.sign_en} ${p.lagna.degree_in_sign.toFixed(2)}° · ` +
    `${p.chart_moment_local.replace("T", " ").slice(0, 16)} · ${p.place.name}` +
    (p.question ? ` · “${p.question}”` : "");
  document.getElementById("ruling-list").innerHTML = p.ruling_planets.map((r) =>
    `<div class="yoga-item"><b>${planetName(r.planet)}</b><span>${LANG === "ne" ? r.role_ne : r.role}</span></div>`).join("");
  document.querySelector("#prashna-kp-table tbody").innerHTML = p.cusps.map((c) => `
    <tr><td>${locNum(c.house)}</td><td>${LANG === "ne" ? c.sign_ne : c.sign_en}</td>
    <td>${planetName(c.sign_lord)}</td><td>${planetName(c.star_lord)}</td>
    <td><b>${planetName(c.sub_lord)}</b></td></tr>`).join("");
}

/* Init */
document.querySelectorAll(".mini-btn[data-style]").forEach((b) =>
  b.classList.toggle("is-active", b.dataset.style === STATE.chartStyle));
applyLang();

/* ================================================================
   Phase 4 — cinematic presentation layer (design only).
   Scroll reveal, dynamic-section reveals, score count-up, sticky
   header shrink, pointer-tracked card tilt, intro dismissal.
   Every feature is independently guarded: a failure here can
   never break rendering, and content is only ever hidden by JS
   that is running and able to reveal it again.
   ================================================================ */
const REDUCED_MOTION = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

/* Staggered rise for dynamically revealed sections (results, premium,
   prashna, matching). Called right after the section is unhidden. */
function revealSection(sec) {
  if (!sec || REDUCED_MOTION || sec.dataset.revealed) return;
  sec.dataset.revealed = "1";
  try {
    const items = sec.querySelectorAll(
      ".card, .glance-strip, .lucky-strip, .pdf-row, .chapter-grid, .score-hero");
    items.forEach((el, i) => {
      el.classList.add("rv-pending");
      el.style.transitionDelay = `${Math.min(i * 70, 560)}ms`;
      requestAnimationFrame(() => requestAnimationFrame(() => el.classList.add("rv-go")));
      setTimeout(() => { el.style.transitionDelay = ""; }, 1600);
    });
  } catch (e) { /* presentation only */ }
}

/* Animated count-up for the Guna Milan score (x or x.5 of 36). */
function animateScore(el, total) {
  if (!el) return;
  const target = Number(total);
  if (REDUCED_MOTION || !Number.isFinite(target)) { el.textContent = total; return; }
  const decimals = Number.isInteger(target) ? 0 : 1;
  const dur = 900, t0 = performance.now();
  (function tick(now) {
    const p = Math.min((now - t0) / dur, 1);
    const eased = 1 - Math.pow(1 - p, 3);
    el.textContent = (target * eased).toFixed(decimals);
    if (p < 1) requestAnimationFrame(tick);
    else el.textContent = total;
  })(t0);
}

/* Scroll reveal for static blocks (.rv) */
try {
  const rvEls = document.querySelectorAll(".rv");
  if (rvEls.length && !REDUCED_MOTION && "IntersectionObserver" in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (en.isIntersecting) { en.target.classList.add("in-view"); io.unobserve(en.target); }
      });
    }, { threshold: 0.1, rootMargin: "0px 0px -36px 0px" });
    rvEls.forEach((el, i) => {
      el.classList.add("rv-armed");
      el.style.transitionDelay = `${Math.min((i % 3) * 80, 160)}ms`;
      io.observe(el);
    });
  }
} catch (e) { /* content simply stays visible */ }

/* Sticky header shrink */
try {
  const header = document.querySelector(".site-header");
  if (header) {
    const onScroll = () => header.classList.toggle("scrolled", window.scrollY > 12);
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }
} catch (e) { /* presentation only */ }

/* Pointer-tracked 3D tilt on small cards (desktop, fine pointer only) */
try {
  const FINE = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  if (FINE && !REDUCED_MOTION) {
    const SEL = ".chapter-block, .pred-block, .lucky-item, .strip-item, .gem-item, .dosha-badge";
    let current = null;
    document.addEventListener("pointermove", (ev) => {
      const el = ev.target && ev.target.closest ? ev.target.closest(SEL) : null;
      if (current && current !== el) {
        current.style.setProperty("--rx", "0deg");
        current.style.setProperty("--ry", "0deg");
        current = null;
      }
      if (!el) return;
      current = el;
      el.classList.add("tilt-on");
      const r = el.getBoundingClientRect();
      if (!r.width || !r.height) return;
      const px = (ev.clientX - r.left) / r.width - 0.5;
      const py = (ev.clientY - r.top) / r.height - 0.5;
      el.style.setProperty("--ry", `${(px * 7).toFixed(2)}deg`);
      el.style.setProperty("--rx", `${(-py * 7).toFixed(2)}deg`);
    }, { passive: true });
    document.addEventListener("pointerleave", () => {
      if (current) {
        current.style.setProperty("--rx", "0deg");
        current.style.setProperty("--ry", "0deg");
        current = null;
      }
    });
  }
} catch (e) { /* presentation only */ }

/* Intro overlay — dismiss on first interaction, sweep up regardless */
try {
  const intro = document.getElementById("intro");
  if (intro) {
    const dismiss = () => intro.classList.add("done");
    window.addEventListener("pointerdown", dismiss, { once: true, passive: true });
    window.addEventListener("keydown", dismiss, { once: true });
    setTimeout(() => intro.remove(), 2400);
  }
} catch (e) { /* CSS animation hides it anyway */ }
