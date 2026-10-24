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
    chart_caption_d1:"Rashi chart (D1) — Nepali janma-patri style", chart_caption_d9:"Navamsa chart (D9)", chart_caption_d10:"Dashamsa chart (D10)",
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
    chart_caption_d1:"राशि कुण्डली (D1) — नेपाली जन्मपत्री शैली", chart_caption_d9:"नवांश कुण्डली (D9)", chart_caption_d10:"दशमांश कुण्डली (D10)",
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
  let stars = [], w = 0, h = 0, raf = null;
  function resize() {
    w = canvas.width = window.innerWidth;
    h = canvas.height = window.innerHeight;
    stars = Array.from({ length: Math.min(170, w / 8) }, () => ({
      x: Math.random() * w, y: Math.random() * h,
      r: Math.random() * 1.3 + 0.3, p: Math.random() * Math.PI * 2,
      s: 0.4 + Math.random() * 0.8,
    }));
    draw(0);
  }
  function draw(time) {
    ctx.clearRect(0, 0, w, h);
    for (const st of stars) {
      const a = 0.35 + 0.55 * Math.abs(Math.sin(st.p + time * 0.0004 * st.s));
      ctx.globalAlpha = a;
      ctx.fillStyle = "#e9e2ff";
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
      fetch(`/api/tz?lat=${encodeURIComponent(p.lat)}&lon=${encodeURIComponent(p.lon)}`)
        .then((r) => (r.ok ? r.json() : null))
        .then((d) => { if (d && d.tz) frag.tz = d.tz; })
        .catch(() => {});
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

["f-place", "m1-place", "m2-place", "p-place"].forEach((id) => {
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
  ["f-place", "m1-place", "m2-place", "p-place"].forEach((id) => {
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
function scheduleTzLookup() {
  clearTimeout(tzTimer);
  tzTimer = setTimeout(async () => {
    const latR = readCoord("lat"), lonR = readCoord("lon");
    if (!latR.ok || !lonR.ok) return;
    clearCoordError();
    try {
      const res = await fetch(`/api/tz?lat=${latR.value}&lon=${lonR.value}`);
      if (res.ok) document.getElementById("f-tz").value = (await res.json()).tz;
    } catch (e) { /* leave the field for manual entry */ }
  }, 400);
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
document.getElementById("birth-form").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const errEl = document.getElementById("form-error");
  errEl.hidden = true;
  const name = document.getElementById("f-name").value.trim();
  const dob = document.getElementById("f-dob").value;
  const tob = document.getElementById("f-tob").value;
  if (!dob || !tob) { errEl.textContent = t("err_fields"); errEl.hidden = false; return; }
  let payload = { name, dob, tob };
  const place = resolvePlace("f-place");
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
    const res = await fetch("/api/kundali", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error("bad");
    STATE.bundle = await res.json();
    STATE.birthPayload = payload;
    STATE.varga = "D1";
    document.querySelectorAll(".mini-btn[data-varga]").forEach((b) =>
      b.classList.toggle("is-active", b.dataset.varga === "D1"));
    renderBundle();
    document.getElementById("results").hidden = false;
    document.getElementById("premium").hidden = false;
    revealSection(document.getElementById("results"));
    revealSection(document.getElementById("premium"));
    document.getElementById("results").scrollIntoView({ behavior: "smooth" });
  } catch (e) {
    errEl.textContent = t("err_server"); errEl.hidden = false;
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

function bundleChartOpts() {
  const b = STATE.bundle;
  const retro = new Set((b?.planets || []).filter((p) => p.retrograde).map((p) => p.planet));
  if (STATE.varga !== "D1") return { style: STATE.chartStyle, retro, captionShort: STATE.varga };
  const degrees = {};
  (b?.planets || []).forEach((p) => { degrees[p.planet] = p.degree_in_sign; });
  return {
    style: STATE.chartStyle, retro, degrees,
    lagnaDegree: b ? b.lagna.degree_in_sign : null, captionShort: STATE.varga,
  };
}

function drawChart(chartMap) {
  const wrap = document.getElementById("chart-svg-wrap");
  const opts = bundleChartOpts();
  wrap.innerHTML = STATE.chartStyle === "south" ? southSVG(chartMap, opts) : diamondSVG(chartMap, opts);
  const cap = document.getElementById("chart-caption");
  if (STATE.chartStyle === "south") cap.textContent = t("chart_caption_south");
  else cap.textContent = STATE.varga === "D1" ? t("chart_caption_d1") : STATE.varga === "D9" ? t("chart_caption_d9") : t("chart_caption_d10");
}
document.querySelectorAll(".mini-btn[data-varga]").forEach((btn) => {
  btn.addEventListener("click", () => {
    STATE.varga = btn.dataset.varga;
    document.querySelectorAll(".mini-btn[data-varga]").forEach((b) => b.classList.toggle("is-active", b === btn));
    if (STATE.bundle) drawChart(STATE.bundle.charts[STATE.varga]);
  });
});
document.querySelectorAll(".mini-btn[data-style]").forEach((btn) => {
  btn.addEventListener("click", () => {
    STATE.chartStyle = btn.dataset.style;
    localStorage.setItem("vedic-astro-style", STATE.chartStyle);
    document.querySelectorAll(".mini-btn[data-style]").forEach((b) => b.classList.toggle("is-active", b === btn));
    if (STATE.bundle) drawChart(STATE.bundle.charts[STATE.varga]);
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

function renderBundle() {
  const b = STATE.bundle;
  if (!b) return;
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

  drawChart(b.charts[STATE.varga]);

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

  const karakas = Object.entries(b.karakas)
    .map(([k, v]) => `<b>${k}</b>: ${planetName(v)}`).join(" · ");
  document.getElementById("karaka-box").innerHTML =
    `<span>${t("karakas_title")}</span><br>${karakas}`;

  renderDasha(b);
  renderKP(b);
  renderDoshasYogas(b);
  renderAV(b);
  renderPredictions(b);
  renderStrength(b);
  renderTransits(b);
  renderNumerology(b);
  renderLalKitab(b);
  renderPremium(b);
  renderDeep(b);
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
  head.innerHTML = `<th>${t("th_planet")}</th>` + SIGNS_EN.map((_, i) => `<th>${signName(i).slice(0, 4)}</th>`).join("");
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
    <p>${bi(v.reading)}</p></div>`).join("");

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
  if (p.place_id) q.set("place_id", p.place_id);
  else {
    q.set("lat", p.lat); q.set("lon", p.lon); q.set("tz", p.tz);
    if (p.place_name) q.set("place_name", p.place_name);
  }
  window.open("/api/report.pdf?" + q.toString(), "_blank");
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
    const place = resolvePlace(prefix + "-place");
    if (!dob || !tob || !place) return null;
    return { dob, tob, ...place };
  }
  const groom = person("m1"), bride = person("m2");
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
}

/* ---------------- KP Prashna (Horary) ---------------- */
document.getElementById("prashna-form").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const errEl = document.getElementById("prashna-error");
  errEl.hidden = true;
  const number = parseInt(document.getElementById("p-number").value, 10);
  const question = document.getElementById("p-question").value.trim();
  const place = resolvePlace("p-place");
  if (!number || number < 1 || number > 249) {
    errEl.textContent = LANG === "ne" ? "कृपया १ देखि २४९ बीचको अङ्क भर्नुहोस्।" : "Please enter a number between 1 and 249.";
    errEl.hidden = false; return;
  }
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
