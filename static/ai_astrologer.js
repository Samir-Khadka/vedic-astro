/* AI Astrologer chat + Life Areas view (rule-based, chart-grounded).
 *
 * No external LLM is involved: every answer comes from the user's own
 * computed chart via POST /api/ask-astrologer, and every Life Area from
 * POST /api/life-areas. Language follows localStorage vedic-astro-lang.
 * If no chart is computed yet, the question is remembered and answered
 * automatically once a chart is computed (vedic-chart-computed event,
 * same pattern as the Life Questions answers).
 */
(function () {
  "use strict";

  function lang() {
    try {
      return (localStorage.getItem("vedic-astro-lang") || "en") === "ne" ? "ne" : "en";
    } catch (e) { return "en"; }
  }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  /* Bilingual field: tries base_en/base_ne, then base.title_en style, then plain base. */
  function t(obj, base) {
    if (!obj) return "";
    var L = lang();
    if (obj[base + "_" + L] != null) return obj[base + "_" + L];
    if (obj[base + "_en"] != null) return obj[base + "_en"];
    if (obj[base] != null) return obj[base];
    if (obj.title_en != null && base === "title") return L === "ne" ? (obj.title_ne || obj.title_en) : obj.title_en;
    return "";
  }
  function houses(list) {
    if (!list || !list.length) return "—";
    return list.map(function (h) { return h + (lang() === "ne" ? "औँ" : ""); }).join(", ");
  }

  var chatEl = document.getElementById("ai-chat");
  var areasEl = document.getElementById("ai-areas");
  var inputEl = document.getElementById("ai-input");
  var sendEl = document.getElementById("ai-send");
  var suggEl = document.getElementById("ai-suggestions");
  var prashnaBox = document.getElementById("ai-prashna-inline");
  var lastAnswer = null;
  var lastAreas = null;
  var lastQuestion = "";

  var SUGGESTIONS = [
    { area: "personality", en: "What is my nature and personality like?", ne: "मेरो स्वभाव र व्यक्तित्व कस्तो छ?" },
    { area: "career", en: "Will my career grow? What work suits me?", ne: "मेरो करियर बढ्छ? कुन काम उपयुक्त छ?" },
    { area: "finance", en: "How will my money and wealth be?", ne: "मेरो धन र सम्पत्ति कस्तो हुन्छ?" },
    { area: "marriage", en: "When and how will my marriage be?", ne: "मेरो विवाह कहिले र कस्तो हुन्छ?" },
    { area: "health", en: "What should I watch for my health?", ne: "मेरो स्वास्थ्यमा के ध्यान दिने?" },
    { area: "education", en: "What field of study suits me?", ne: "मलाई कुन विषय पढाइ उपयुक्त छ?" },
    { area: "family_home", en: "How will my family and home life be?", ne: "मेरो परिवार र घर जीवन कस्तो हुन्छ?" },
    { area: "foreign", en: "Will I go abroad or settle in a foreign country?", ne: "के म विदेश जान्छु वा विदेशमै बसोबास गर्छु?" }
  ];

  function renderSuggestions() {
    if (!suggEl) return;
    var L = lang();
    suggEl.innerHTML = SUGGESTIONS.map(function (s) {
      return '<button type="button" class="mini-btn ai-sugg" data-q="' + esc(L === "ne" ? s.ne : s.en) + '">' + esc(L === "ne" ? s.ne : s.en) + "</button>";
    }).join(" ");
    suggEl.querySelectorAll(".ai-sugg").forEach(function (b) {
      b.addEventListener("click", function () {
        if (inputEl) inputEl.value = b.dataset.q;
        ask();
      });
    });
  }

  function planetTableHTML(rows) {
    if (!rows || !rows.length) return "";
    var L = lang();
    var head = "<tr><th>" + (L === "ne" ? "ग्रह" : "Planet") + "</th><th>" + (L === "ne" ? "राशि / भाव" : "Sign / House") + "</th><th>" + (L === "ne" ? "यस क्षेत्रमा प्रभाव" : "Effect on this area") + "</th></tr>";
    var body = rows.map(function (r) {
      var sign = r.sign_en != null ? (L === "ne" ? (r.sign_ne || r.sign_en) : r.sign_en) : (r.sign || "");
      var house = r.house != null ? (r.house + (L === "ne" ? "औँ भाव" : "th house")) : "";
      var effect = t(r, "effect");
      return "<tr><td><strong>" + esc(r.planet || r.name || "") + "</strong></td><td>" + esc(sign) + (house ? " · " + esc(house) : "") + "</td><td>" + esc(effect) + "</td></tr>";
    }).join("");
    return '<div class="table-scroll"><table class="ai-table">' + head + body + "</table></div>";
  }

  function listHTML(items) {
    if (!items || !items.length) return "";
    return "<ul>" + items.map(function (x) { return "<li>" + esc(typeof x === "string" ? x : (t(x, "text") || x.en || "")) + "</li>"; }).join("") + "</ul>";
  }

  function answerHTML(a) {
    var L = lang();
    if (!a) return "";
    /* Refusal / fallback shape (backend: reason_en/ne + suggestions list
       of {id, title_en, title_ne}; fallback also carries direct_answer). */
    if (a.refusal || a.fallback) {
      var msg = t(a, "direct_answer") || t(a, "reason") || t(a, "explanation") || "";
      var sugg = "";
      if (a.suggestions && a.suggestions.length) {
        var names = a.suggestions.map(function (s) {
          return typeof s === "string" ? s : (L === "ne" ? (s.title_ne || s.title_en || s.id) : (s.title_en || s.id));
        }).join(", ");
        sugg = "<p>" + (L === "ne" ? "यी क्षेत्रहरूमा सोध्न सक्नुहुन्छ: " : "You can ask about these areas: ") + esc(names) + "</p>";
      }
      var disc = t(a, "disclaimer");
      return '<div class="ai-answer"><p>' + esc(msg || (L === "ne" ? "यो प्रश्नको उत्तर यसरी दिन सकिँदैन।" : "This question cannot be answered this way.")) + "</p>" + sugg + (disc ? '<p class="results-meta">' + esc(disc) + "</p>" : "") + "</div>";
    }
    var title = a.area_title_en != null ? (L === "ne" ? (a.area_title_ne || a.area_title_en) : a.area_title_en) : (t(a, "area_title") || a.area_id || "");
    var direct = t(a, "direct_answer") || a.direct_answer_en || "";
    var timing = t(a, "timing") || "";
    var disc = t(a, "disclaimer") || "";
    var band = a.band || a.indication || "";
    var out = '<div class="ai-answer">';
    if (title) out += "<h4>" + esc(title) + "</h4>";
    if (band) out += '<p><strong>' + esc(L === "ne" ? "सङ्केत: " : "Indication: ") + esc(band) + "</strong></p>";
    if (direct) out += "<p>" + esc(direct) + "</p>";
    var rows = a.planet_table || a.planets || [];
    if (rows.length) {
      out += "<h5>" + (L === "ne" ? "कुन ग्रहले के प्रभाव पार्दैछ" : "Which planets are influencing this") + "</h5>" + planetTableHTML(rows);
    }
    if (a.supporting && a.supporting.length) out += "<h5>" + (L === "ne" ? "सहयोगी प्रभाव" : "Supporting influences") + "</h5>" + listHTML(a.supporting);
    if (a.challenging && a.challenging.length) out += "<h5>" + (L === "ne" ? "चुनौतीपूर्ण प्रभाव" : "Challenging influences") + "</h5>" + listHTML(a.challenging);
    if (timing) out += "<h5>" + (L === "ne" ? "समय" : "Timing") + "</h5><p>" + esc(timing) + "</p>";
    if (disc) out += '<p class="results-meta">' + esc(disc) + "</p>";
    out += "</div>";
    return out;
  }

  function appendMessage(html, cls) {
    if (!chatEl) return;
    var div = document.createElement("div");
    div.className = "ai-msg " + (cls || "");
    div.innerHTML = html;
    chatEl.appendChild(div);
    chatEl.scrollTop = chatEl.scrollHeight;
  }

  function showStatus(msg) {
    appendMessage('<p class="results-meta">' + esc(msg) + "</p>", "ai-status");
  }

  function ask() {
    var q = (inputEl ? inputEl.value : "").trim();
    if (!q) return;
    lastQuestion = q;
    var L = lang();
    appendMessage("<p><strong>" + (L === "ne" ? "तपाईं: " : "You: ") + "</strong>" + esc(q) + "</p>", "ai-user");
    var payload = window.vedicLastBirthPayload;
    if (!payload) {
      /* No chart yet: remember the question, ask for a chart first. */
      try { localStorage.setItem("vedic-pending-ai-question", q); } catch (e) {}
      showStatus(L === "ne"
        ? "पहिले कुण्डली बनाउनुहोस् — त्यसपछि यो प्रश्नको उत्तर आफैँ आउँछ।"
        : "Compute a chart first — the answer to this question will then come up automatically.");
      var form = document.getElementById("kundali-form");
      if (form) form.scrollIntoView({ behavior: "smooth" });
      return;
    }
    try { localStorage.removeItem("vedic-pending-ai-question"); } catch (e) {}
    requestAsk({ question: q, lang: L, birth: payload });
  }

  function askByPrashna() {
    var numEl = document.getElementById("ai-p-number");
    var placeEl = document.getElementById("ai-p-place");
    var q = (inputEl ? inputEl.value : "").trim();
    var L = lang();
    if (!q) { showStatus(L === "ne" ? "पहिले प्रश्न लेख्नुहोस्।" : "Please type a question first."); return; }
    var num = numEl ? parseInt(numEl.value, 10) : NaN;
    var place = placeEl ? placeEl.value.trim() : "";
    if (!num || num < 1 || num > 249) { showStatus(L === "ne" ? "कृपया १ देखि २४९ बीचको अङ्क भर्नुहोस्।" : "Please enter a number between 1 and 249."); return; }
    if (!place) { showStatus(L === "ne" ? "कृपया स्थान भर्नुहोस्।" : "Please enter a place."); return; }
    lastQuestion = q;
    appendMessage("<p><strong>" + (L === "ne" ? "तपाईं: " : "You: ") + "</strong>" + esc(q) + "</p>", "ai-user");
    fetch("/api/places?q=" + encodeURIComponent(place)).then(function (r) { return r.json(); }).then(function (data) {
      var first = (data.places || [])[0];
      if (!first) throw new Error("noplace");
      requestAsk({ question: q, lang: L, prashna_number: num, place: first });
    }).catch(function () {
      showStatus(L === "ne" ? "स्थान भेटिएन — प्रश्न खण्डमा स्थान छान्नुहोस्।" : "Place not found — pick a place in the Prashna section.");
    });
  }

  function requestAsk(body) {
    var L = lang();
    appendMessage('<p class="results-meta">' + (L === "ne" ? "उत्तर खोजिँदैछ…" : "Finding your answer…") + "</p>", "ai-wait");
    fetch("/api/ask-astrologer", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    }).then(function (r) {
      if (!r.ok) throw new Error("http" + r.status);
      return r.json();
    }).then(function (a) {
      var waits = chatEl ? chatEl.querySelectorAll(".ai-wait") : [];
      waits.forEach(function (w) { w.remove(); });
      lastAnswer = a;
      appendMessage(answerHTML(a), "ai-bot");
    }).catch(function () {
      var waits = chatEl ? chatEl.querySelectorAll(".ai-wait") : [];
      waits.forEach(function (w) { w.remove(); });
      showStatus(L === "ne" ? "उत्तर प्राप्त हुन सकेन। कृपया फेरि प्रयास गर्नुहोस्।" : "Could not get an answer. Please try again.");
    });
  }

  function renderAreas() {
    if (!areasEl || !lastAreas) return;
    var L = lang();
    var list = lastAreas.areas || lastAreas;
    areasEl.innerHTML = (Array.isArray(list) ? list : []).map(function (area, i) {
      var title = area.title_en != null ? (L === "ne" ? (area.title_ne || area.title_en) : area.title_en) : (t(area, "title") || area.id || "");
      var reading = t(area, "reading") || "";
      var lords = area.house_lords || {};
      var lordsText = Object.keys(lords).map(function (h) { return h + ": " + lords[h]; }).join(" · ");
      /* planets_in: backend map planet -> {sign_en, sign_ne, house, ...} */
      var rows = area.planets_in || area.planets || {};
      var planetRows = [];
      if (Array.isArray(rows)) {
        planetRows = rows.map(function (r) {
          if (typeof r === "string") return r;
          return (r.planet || r.name || "") + " — " + (r.sign_en || r.sign || "") + " (" + (r.house != null ? r.house : "") + ")";
        });
      } else if (rows && typeof rows === "object") {
        planetRows = Object.keys(rows).map(function (p) {
          var v = rows[p] || {};
          var sign = lang() === "ne" ? (v.sign_ne || v.sign_en || "") : (v.sign_en || "");
          return p + " — " + sign + (v.house != null ? " (" + v.house + ")" : "");
        });
      }
      /* planets_aspecting: backend map planet -> [houses it aspects]. */
      var asp = area.planets_aspecting || {};
      var aspText = "";
      if (Array.isArray(asp)) aspText = asp.join(", ");
      else if (asp && typeof asp === "object") aspText = Object.keys(asp).map(function (p) { return p + " → " + houses(asp[p]); }).join(" · ");
      /* dasha_influence: {mahadasha_lord, antardasha_lord, periods, ..._signifies_area_houses}. */
      var dasha = area.dasha_influence || {};
      var dashaText = "";
      if (typeof dasha === "string") dashaText = dasha;
      else if (dasha && typeof dasha === "object") {
        var parts = [];
        if (dasha.mahadasha_lord) parts.push((lang() === "ne" ? "महादशा: " : "Mahadasha: ") + dasha.mahadasha_lord);
        if (dasha.antardasha_lord) parts.push((lang() === "ne" ? "अन्तर्दशा: " : "Antardasha: ") + dasha.antardasha_lord);
        var hits = (dasha.mahadasha_signifies_area_houses || []).concat(dasha.antardasha_signifies_area_houses || []);
        if (hits.length) parts.push((lang() === "ne" ? "यस क्षेत्रका भाव: " : "Area houses signified: ") + houses(hits));
        dashaText = parts.join(" · ");
      }
      return '<div class="glass card ai-area-card">' +
        '<button type="button" class="ai-area-head" data-i="' + i + '"><strong>' + esc(title) + "</strong> <span>" + esc(houses(area.houses)) + "</span></button>" +
        '<div class="ai-area-body" data-body="' + i + '" hidden>' +
        (lordsText ? "<p><strong>" + (L === "ne" ? "भाव स्वामी: " : "House lords: ") + "</strong>" + esc(lordsText) + "</p>" : "") +
        (planetRows.length ? "<p><strong>" + (L === "ne" ? "भावमा ग्रह: " : "Planets in these houses: ") + "</strong>" + esc(planetRows.join(" · ")) + "</p>" : "") +
        (aspText ? "<p><strong>" + (L === "ne" ? "दृष्टि दिने ग्रह: " : "Planets aspecting: ") + "</strong>" + esc(aspText) + "</p>" : "") +
        ((area.strongest && area.strongest.length) ? "<p><strong>" + (L === "ne" ? "सबैभन्दा बलियो प्रभाव: " : "Strongest influences: ") + "</strong>" + esc(area.strongest.map(function (s) { return typeof s === "string" ? s : (((s.planet_ne && lang() === "ne" ? s.planet_ne : s.planet) || "") + (t(s, "effect") ? ": " + t(s, "effect") : "")); }).join(" · ")) + "</p>" : "") +
        (dashaText ? "<p><strong>" + (L === "ne" ? "दशा प्रभाव: " : "Dasha influence: ") + "</strong>" + esc(dashaText) + "</p>" : "") +
        (reading ? "<p>" + esc(reading) + "</p>" : "") +
        "</div></div>";
    }).join("");
    areasEl.querySelectorAll(".ai-area-head").forEach(function (b) {
      b.addEventListener("click", function () {
        var body = areasEl.querySelector('[data-body="' + b.dataset.i + '"]');
        if (body) body.hidden = !body.hidden;
      });
    });
  }

  function loadAreas() {
    var L = lang();
    var payload = window.vedicLastBirthPayload;
    if (!payload) {
      showStatus(L === "ne"
        ? "पहिले कुण्डली बनाउनुहोस् — त्यसपछि ८ जीवन क्षेत्र देखिन्छन्।"
        : "Compute a chart first — the 8 life areas will then appear.");
      var form = document.getElementById("kundali-form");
      if (form) form.scrollIntoView({ behavior: "smooth" });
      return;
    }
    if (areasEl) areasEl.innerHTML = '<p class="results-meta">' + (L === "ne" ? "क्षेत्रहरू निकालिँदैछन्…" : "Loading your life areas…") + "</p>";
    fetch("/api/life-areas", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    }).then(function (r) {
      if (!r.ok) throw new Error("http" + r.status);
      return r.json();
    }).then(function (data) {
      lastAreas = data;
      renderAreas();
      if (areasEl) areasEl.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }).catch(function () {
      if (areasEl) areasEl.innerHTML = '<p class="results-meta">' + (L === "ne" ? "क्षेत्रहरू प्राप्त हुन सकेनन्। कृपया फेरि प्रयास गर्नुहोस्।" : "Could not load the life areas. Please try again.") + "</p>";
    });
  }

  /* Wiring. */
  if (sendEl) sendEl.addEventListener("click", ask);
  if (inputEl) inputEl.addEventListener("keydown", function (ev) {
    if (ev.key === "Enter") { ev.preventDefault(); ask(); }
  });
  var prashnaBtn = document.getElementById("ai-prashna-btn");
  if (prashnaBtn) prashnaBtn.addEventListener("click", function () {
    if (prashnaBox) prashnaBox.hidden = !prashnaBox.hidden;
  });
  var prashnaGo = document.getElementById("ai-p-go");
  if (prashnaGo) prashnaGo.addEventListener("click", askByPrashna);
  var areasBtn = document.getElementById("ai-areas-btn");
  if (areasBtn) areasBtn.addEventListener("click", loadAreas);
  var resultsBtn = document.getElementById("ai-astrologer-btn");
  if (resultsBtn) resultsBtn.addEventListener("click", function () {
    var sec = document.getElementById("ai-astrologer");
    if (sec) sec.scrollIntoView({ behavior: "smooth" });
  });

  /* Pending question: answered automatically once a chart is computed. */
  window.addEventListener("vedic-chart-computed", function (ev) {
    var pending = null;
    try { pending = localStorage.getItem("vedic-pending-ai-question"); } catch (e) {}
    if (pending && ev.detail) {
      try { localStorage.removeItem("vedic-pending-ai-question"); } catch (e) {}
      if (inputEl) inputEl.value = pending;
      lastQuestion = pending;
      var L = lang();
      appendMessage("<p><strong>" + (L === "ne" ? "तपाईं: " : "You: ") + "</strong>" + esc(pending) + "</p>", "ai-user");
      requestAsk({ question: pending, lang: L, birth: ev.detail });
      var sec = document.getElementById("ai-astrologer");
      if (sec) sec.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  });

  /* Language toggle re-renders suggestions, last answer and areas. */
  ["lang-en", "lang-ne"].forEach(function (id) {
    var b = document.getElementById(id);
    if (b) b.addEventListener("click", function () {
      setTimeout(function () {
        renderSuggestions();
        if (lastAnswer && chatEl) {
          var bots = chatEl.querySelectorAll(".ai-bot");
          if (bots.length) bots[bots.length - 1].innerHTML = answerHTML(lastAnswer);
        }
        renderAreas();
      }, 0);
    });
  });

  renderSuggestions();
})();
