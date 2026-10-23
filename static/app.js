"use strict";
/* Vedic Astro frontend — vanilla JS SPA. All rendering from /api JSON. */

/* ---------------- i18n ---------------- */
const SIGNS_EN = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"];
const SIGNS_NE = ["मेष","वृष","मिथुन","कर्कट","सिंह","कन्या","तुला","वृश्चिक","धनु","मकर","कुम्भ","मीन"];
const SIGN_GLYPHS = ["♈","♉","♊","♋","♌","♍","♎","♏","♐","♑","♒","♓"];
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
    hero_sub:"Swiss Ephemeris astronomy with Lahiri ayanamsa — Parashari depth, KP timing, Jaimini insight. In English and Nepali.",
    hero_cta:"Create my Kundali",
    panchang_title:"Today's Panchang", loading:"Loading…",
    form_title:"Birth Details", f_name:"Name", f_dob:"Date of birth", f_tob:"Time of birth",
    f_place:"Birth place", f_place_hint:"Search any place in the world, or enter coordinates below.",
    place_global_unavailable:"Worldwide search is unavailable right now — try entering coordinates manually.",
    manual_coords:"Enter coordinates manually", f_lat:"Latitude", f_lon:"Longitude", f_tz:"Timezone (IANA)",
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
    chart_caption_d1:"Rashi chart (D1) — North Indian style", chart_caption_d9:"Navamsa chart (D9)", chart_caption_d10:"Dashamsa chart (D10)",
    sarva:"Sarvashtakavarga",
  },
  ne: {
    nav_kundali:"कुण्डली", nav_premium:"प्रिमियम रिपोर्ट", nav_matching:"मेल मिलान", nav_panchang:"पञ्चाङ्ग",
    hero_title:"तपाईंका तारा, यथार्थ रूपमा गणना गरिएको।",
    hero_sub:"लाहिरी अयनांशसहित स्विस एफेमेरिस खगोल विज्ञान — पराशरी गहिराइ, KP समय-शुद्धता, जैमिनी अन्तर्दृष्टि। अङ्ग्रेजी र नेपालीमा।",
    hero_cta:"मेरो कुण्डली बनाउनुहोस्",
    panchang_title:"आजको पञ्चाङ्ग", loading:"लोड हुँदैछ…",
    form_title:"जन्म विवरण", f_name:"नाम", f_dob:"जन्म मिति", f_tob:"जन्म समय",
    f_place:"जन्म स्थान", f_place_hint:"विश्वको कुनै पनि ठाउँ खोज्नुहोस्, वा तल निर्देशाङ्क भर्नुहोस्।",
    place_global_unavailable:"विश्वव्यापी खोज अहिले उपलब्ध छैन — निर्देशाङ्क आफैँ भरेर प्रयास गर्नुहोस्।",
    manual_coords:"निर्देशाङ्क आफैँ भर्नुहोस्", f_lat:"अक्षांश", f_lon:"देशान्तर", f_tz:"समय क्षेत्र (IANA)",
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
    chart_caption_d1:"राशि कुण्डली (D1) — उत्तर भारतीय शैली", chart_caption_d9:"नवांश कुण्डली (D9)", chart_caption_d10:"दशमांश कुण्डली (D10)",
    sarva:"सर्वाष्टकवर्ग",
  }
};

let LANG = localStorage.getItem("vedic-astro-lang") || "en";
const t = (key) => (I18N[LANG] && I18N[LANG][key]) || I18N.en[key] || key;
const planetName = (p) => (LANG === "ne" ? (PLANET_NE[p] || p) : p);
const signName = (s) => (LANG === "ne" ? SIGNS_NE[s] : SIGNS_EN[s]);
const bi = (obj) => (obj ? (obj[LANG] || obj.en || "") : "");

const STATE = { bundle: null, birthPayload: null, match: null, varga: "D1" };

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

["f-place", "m1-place", "m2-place"].forEach((id) => {
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
  ["f-place", "m1-place", "m2-place"].forEach((id) => {
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

/* Manual coordinates: auto-fill the IANA timezone from the backend. */
let tzTimer = null;
["f-lat", "f-lon"].forEach((id) => {
  document.getElementById(id).addEventListener("input", () => {
    clearTimeout(tzTimer);
    tzTimer = setTimeout(async () => {
      const lat = parseFloat(document.getElementById("f-lat").value);
      const lon = parseFloat(document.getElementById("f-lon").value);
      if (!Number.isFinite(lat) || !Number.isFinite(lon)) return;
      try {
        const res = await fetch(`/api/tz?lat=${lat}&lon=${lon}`);
        if (res.ok) document.getElementById("f-tz").value = (await res.json()).tz;
      } catch (e) { /* leave the field for manual entry */ }
    }, 400);
  });
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
    const lat = document.getElementById("f-lat").value;
    const lon = document.getElementById("f-lon").value;
    const tz = document.getElementById("f-tz").value.trim();
    if (lat && lon && tz) payload = { ...payload, lat: parseFloat(lat), lon: parseFloat(lon), tz };
    else { errEl.textContent = t("err_place"); errEl.hidden = false; return; }
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
    document.querySelectorAll(".mini-btn").forEach((b) =>
      b.classList.toggle("is-active", b.dataset.varga === "D1"));
    renderBundle();
    document.getElementById("results").hidden = false;
    document.getElementById("premium").hidden = false;
    document.getElementById("results").scrollIntoView({ behavior: "smooth" });
  } catch (e) {
    errEl.textContent = t("err_server"); errEl.hidden = false;
  } finally {
    btn.disabled = false; btn.textContent = t("submit");
  }
});

/* ---------------- North Indian chart (SVG) ---------------- */
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
const ABBR_NE = { Sun: "सू", Moon: "च", Mars: "मं", Mercury: "बु", Jupiter: "बृ", Venus: "शु", Saturn: "श", Rahu: "रा", Ketu: "के" };

function drawChart(chartMap) {
  const lagnaSign = chartMap["Lagna"];
  const wrap = document.getElementById("chart-svg-wrap");
  let svg = `<svg class="kundali-svg" viewBox="0 0 400 400" role="img" aria-label="Kundali chart">`;
  HOUSE_REGIONS.forEach((region, idx) => {
    const house = idx + 1;
    const sign = (lagnaSign + house - 1) % 12;
    const bodies = Object.keys(chartMap).filter((k) => k !== "Lagna" && chartMap[k] === sign);
    const isLagna = house === 1;
    svg += `<polygon class="house-poly${isLagna ? " lagna-house" : ""}" points="${region.poly}"/>`;
    svg += `<text class="sign-num" x="${region.sign[0]}" y="${region.sign[1]}">${sign + 1}</text>`;
    const abbrs = bodies.map((b) => (LANG === "ne" ? ABBR_NE[b] : ABBR[b]) + (isRetro(b) ? "ᴿ" : ""));
    if (isLagna) abbrs.unshift(LANG === "ne" ? "ल" : "Asc");
    const lines = [];
    for (let i = 0; i < abbrs.length; i += 3) lines.push(abbrs.slice(i, i + 3).join(" "));
    lines.forEach((line, li) => {
      svg += `<text class="planet-txt" x="${region.label[0]}" y="${region.label[1] + li * 15}">${line}</text>`;
    });
  });
  svg += "</svg>";
  wrap.innerHTML = svg;
  document.getElementById("chart-caption").textContent =
    STATE.varga === "D1" ? t("chart_caption_d1") : STATE.varga === "D9" ? t("chart_caption_d9") : t("chart_caption_d10");
}
function isRetro(planet) {
  const row = (STATE.bundle?.planets || []).find((p) => p.planet === planet);
  return !!(row && row.retrograde);
}
document.querySelectorAll(".mini-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    STATE.varga = btn.dataset.varga;
    document.querySelectorAll(".mini-btn").forEach((b) => b.classList.toggle("is-active", b === btn));
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
  renderPremium(b);
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

/* ---------------- Premium ---------------- */
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

  document.getElementById("forecast-list").innerHTML = rep.favourable_periods.map((f) => `
    <div class="fc-row"><span class="yr">${f.year}</span> — ${planetName(f.mahadasha)}${f.antardasha ? " / " + planetName(f.antardasha) : ""}
    <p>${bi(f.summary)}</p></div>`).join("");

  document.getElementById("varshphal-list").innerHTML = rep.varshphal.map((v) => `
    <div class="fc-row"><span class="yr">${v.year}</span> — ${LANG === "ne" ? v.varsha_lagna.sign_ne : v.varsha_lagna.sign_en}
    · ${t("year_lord")}: ${planetName(v.year_lord)} · ${t("muntha")}: ${v.muntha.house}${LANG === "ne" ? "" : " " + t("house_word")}
    <p>${bi(v.reading)}</p></div>`).join("");

  const r = rep.remedies;
  let html = `<h4>${t("gemstones")}</h4><div class="gem-grid">` + r.gemstones.map((g) => `
    <div class="gem-item"><b>${bi(g.role)}</b>
    ${bi(g.stone)} · ${bi(g.metal)} · ${bi(g.finger)} · ${bi(g.day)} · ${g.weight}</div>`).join("") + "</div>";
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
    document.getElementById("match-result").scrollIntoView({ behavior: "smooth" });
  } catch (e) {
    errEl.textContent = t("err_server"); errEl.hidden = false;
  }
});

function renderMatch() {
  const m = STATE.match;
  if (!m) return;
  document.getElementById("score-value").textContent = m.total;
  document.getElementById("score-verdict").textContent = LANG === "ne" ? m.verdict_ne : m.verdict_en;
  document.getElementById("match-meta").textContent =
    `${t("groom_moon")}: ${LANG === "ne" ? m.groom.moon_sign_ne : m.groom.moon_sign_en} / ${LANG === "ne" ? m.groom.nakshatra_ne : m.groom.nakshatra_en} · ` +
    `${t("bride_moon")}: ${LANG === "ne" ? m.bride.moon_sign_ne : m.bride.moon_sign_en} / ${LANG === "ne" ? m.bride.nakshatra_ne : m.bride.nakshatra_en}`;
  document.querySelector("#match-table tbody").innerHTML = m.breakdown.map((row) => `
    <tr><td><b>${t("kootas")[row.koota] || row.koota}</b></td>
    <td>${row.score} / ${row.max}</td><td>${row.detail}</td></tr>`).join("");
  document.getElementById("manglik-note").textContent = bi(m.manglik_note);
}

/* Init */
applyLang();
