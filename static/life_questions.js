/* Life Questions library (Phase 1 + answers) — small standalone script
   so the main app.js bundle is untouched. Fetches /api/life-questions
   and renders in the current language (localStorage vedic-astro-lang).

   Answers (new): each question can now actually be answered — from the
   most recently computed birth chart (exposed by app.js as
   window.vedicLastBirthPayload) or by Prashna (number 1-249 + place).
   POST /api/life-questions/{id}/answer returns an indication band plus
   an evidence table, so the user sees WHY. Traditional probability
   guidance only, never a certain verdict. */
(function () {
  var listEl = document.getElementById("lq-list");
  if (!listEl) return;
  var catEl = document.getElementById("lq-category");
  var detailEl = document.getElementById("lq-detail");
  var subEl = document.getElementById("lq-sub");
  var all = [];
  var cats = [];
  var currentId = null;
  var lastAnswer = null;

  function lang() {
    return (localStorage.getItem("vedic-astro-lang") || "en") === "ne" ? "ne" : "en";
  }
  function t(q, field) {
    return q[field + "_" + lang()] || q[field + "_en"] || "";
  }
  function houses(arr) {
    return arr.map(function (h) { return h + "H"; }).join(", ");
  }
  function esc(s) {
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
  function clsLabel(cls) {
    var L = lang();
    if (cls === "prime") return L === "ne" ? "प्रमुख" : "prime";
    if (cls === "supporting") return L === "ne" ? "समर्थन" : "supporting";
    if (cls === "negating") return L === "ne" ? "नकार्ने" : "negating";
    return L === "ne" ? "अन्य" : "other";
  }

  function renderCats() {
    if (!catEl) return;
    var L = lang();
    var allLabel = L === "ne" ? "सबै" : "All";
    catEl.innerHTML = '<option value="">' + allLabel + "</option>" + cats.map(function (c) {
      return '<option value="' + esc(c.slug) + '">' + esc(L === "ne" ? c.ne : c.en) + "</option>";
    }).join("");
  }

  function renderList() {
    var L = lang();
    var sel = catEl ? catEl.value : "";
    var items = sel ? all.filter(function (q) { return q.category === sel; }) : all;
    listEl.innerHTML = items.map(function (q) {
      return '<button type="button" class="lq-item" data-id="' + esc(q.id) + '">' +
        '<span class="lq-item-cat">' + esc(L === "ne" ? q.category_ne : q.category_en) + "</span>" +
        '<span class="lq-item-q">' + esc(t(q, "question")) + "</span></button>";
    }).join("") || '<p class="results-meta">' + (L === "ne" ? "कुनै प्रश्न भेटिएन।" : "No questions found.") + "</p>";
    listEl.querySelectorAll(".lq-item").forEach(function (btn) {
      btn.addEventListener("click", function () { renderDetail(btn.dataset.id); });
    });
  }

  function rulingHTML(q) {
    var r = q.ruling;
    if (!r) return "";
    var L = lang();
    var head = L === "ne" ? "परम्परागत निर्णय" : "Traditional ruling";
    if (r.source === "pending") {
      return "<h4>" + head + "</h4><p>" + esc(t(r, "note")) + "</p>";
    }
    var out = "<h4>" + head + "</h4>" +
      "<p><strong>" + (L === "ne" ? "पढ्ने विधि: " : "How to read: ") + "</strong>" + esc(t(r, "method")) + "</p>" +
      "<p><strong>" + (L === "ne" ? "अनुकूल सङ्केत: " : "Favourable: ") + "</strong>" + esc(t(r, "favourable")) + "</p>" +
      "<p><strong>" + (L === "ne" ? "प्रतिकूल सङ्केत: " : "Unfavourable: ") + "</strong>" + esc(t(r, "unfavourable")) + "</p>";
    if (r.timing_en || r.timing_ne) {
      out += "<p><strong>" + (L === "ne" ? "समय: " : "Timing: ") + "</strong>" + esc(t(r, "timing")) + "</p>";
    }
    out += '<p class="results-meta">' + (L === "ne" ? "स्रोत: " : "Source: ") + esc(t(r, "source_label")) + "</p>";
    return out;
  }

  function answerHTML(a) {
    var L = lang();
    var band = a.band_en && L === "ne" ? a.band_ne : (a.band_en || a.band);
    var out = '<div class="lq-answer lq-band-' + esc(a.band) + '">' +
      "<h4>" + (L === "ne" ? "उत्तर — " : "Answer — ") + esc(band) + "</h4>" +
      "<p>" + esc(t(a, "explanation")) + "</p>" +
      "<p><strong>" + (L === "ne" ? "अङ्क: " : "Score: ") + "</strong>" + esc(a.score) +
      " (" + (L === "ne" ? "प्रमुख" : "prime") + " " + esc(a.prime_hits) +
      ", " + (L === "ne" ? "समर्थन" : "supporting") + " " + esc(a.supporting_hits) +
      ", " + (L === "ne" ? "नकार्ने" : "negating") + " " + esc(a.negating_hits) + ")</p>";
    if (a.evidence && a.evidence.length) {
      out += '<div class="table-scroll"><table><thead><tr><th>' +
        (L === "ne" ? "जाँचिएको स्वामी" : "Checked lord") + "</th><th>" +
        (L === "ne" ? "ग्रह" : "Planet") + "</th><th>" +
        (L === "ne" ? "सङ्केत गरेका भाव" : "Houses signified") + "</th></tr></thead><tbody>" +
        a.evidence.map(function (e) {
          var hs = e.houses.map(function (h) {
            return h.house + "H (" + clsLabel(h.class) + ")";
          }).join(", ") || "—";
          return "<tr><td>" + esc(t(e, "role")) + "</td><td>" +
            esc(L === "ne" ? (e.planet_ne || e.planet) : e.planet) + "</td><td>" + esc(hs) + "</td></tr>";
        }).join("") + "</tbody></table></div>";
    } else {
      out += "<p>" + (L === "ne" ? "कुनै प्रमाण उपलब्ध छैन।" : "No evidence available.") + "</p>";
    }
    out += '<p class="results-meta">' + esc(t(a, "disclaimer")) + "</p></div>";
    return out;
  }

  function showAnswerStatus(msg) {
    var box = document.getElementById("lq-answer-box");
    if (box) box.innerHTML = '<p class="results-meta">' + esc(msg) + "</p>";
  }

  function requestAnswer(body) {
    var L = lang();
    var box = document.getElementById("lq-answer-box");
    if (!box || !currentId) return;
    box.innerHTML = '<p class="results-meta">' + (L === "ne" ? "उत्तर खोजिँदैछ…" : "Finding your answer…") + "</p>";
    fetch("/api/life-questions/" + encodeURIComponent(currentId) + "/answer", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }).then(function (r) {
      if (!r.ok) throw new Error("http" + r.status);
      return r.json();
    }).then(function (a) {
      lastAnswer = a;
      box.innerHTML = answerHTML(a);
    }).catch(function () {
      box.innerHTML = '<p class="results-meta">' +
        (L === "ne" ? "उत्तर प्राप्त हुन सकेन। कृपया फेरि प्रयास गर्नुहोस्।" : "Could not get an answer. Please try again.") + "</p>";
    });
  }

  function renderDetail(id, skipScroll) {
    var q = all.find(function (x) { return x.id === id; });
    if (!q || !detailEl) return;
    if (currentId !== id) lastAnswer = null;
    currentId = id;
    var L = lang();
    detailEl.hidden = false;
    detailEl.innerHTML =
      "<h3>" + esc(t(q, "question")) + "</h3>" +
      "<p><strong>" + (L === "ne" ? "प्रमुख भाव: " : "Prime houses: ") + esc(houses(q.prime_houses)) + "</strong><br>" +
      (L === "ne" ? "समर्थन गर्ने भाव: " : "Supporting houses: ") + esc(houses(q.supporting_houses)) + "<br>" +
      (L === "ne" ? "नकार्ने भाव: " : "Negating houses: ") + esc(houses(q.negating_houses)) + "<br>" +
      (L === "ne" ? "कारक: " : "Significator: ") + esc(t(q, "significator")) + "</p>" +
      "<p>" + esc(t(q, "what_to_check")) + "</p>" +
      "<p>" + esc(t(q, "timing_note")) + "</p>" +
      rulingHTML(q) +
      '<p class="results-meta">' + esc(t(q, "disclaimer")) + "</p>" +
      '<div class="field-row">' +
      '<button type="button" class="btn btn-gold" id="lq-answer-chart-btn">' + (L === "ne" ? "मेरो कुण्डलीबाट उत्तर" : "Answer from my chart") + "</button> " +
      '<button type="button" class="btn" id="lq-answer-prashna-btn">' + (L === "ne" ? "प्रश्नबाट उत्तर" : "Answer by Prashna") + "</button>" +
      "</div>" +
      '<div id="lq-prashna-inline" hidden><div class="field-row">' +
      '<label>' + (L === "ne" ? "प्रश्न अङ्क (१–२४९)" : "Prashna number (1–249)") +
      ' <input id="lq-p-number" type="number" min="1" max="249" style="width:6em"></label>' +
      '<label>' + (L === "ne" ? "स्थान" : "Place") +
      ' <input id="lq-p-place" type="text" placeholder="Kathmandu"></label>' +
      '<button type="button" class="btn btn-gold" id="lq-p-go">' + (L === "ne" ? "उत्तर पाउनुहोस्" : "Get answer") + "</button>" +
      "</div></div>" +
      '<div id="lq-answer-box">' + (lastAnswer ? answerHTML(lastAnswer) : "") + "</div>";
    document.getElementById("lq-answer-chart-btn").addEventListener("click", function () {
      var payload = window.vedicLastBirthPayload;
      if (!payload) {
        try { localStorage.setItem("vedic-pending-life-question", id); } catch (e) {}
        showAnswerStatus(L === "ne"
          ? "पहिले कुण्डली बनाउनुहोस् — त्यसपछि यो प्रश्नको उत्तर आफैँ आउँछ।"
          : "Compute a chart first — the answer for this question will then come up automatically.");
        if (window.vedicNavigate) window.vedicNavigate("kundali");
        else { var form = document.getElementById("kundali-form"); if (form) form.scrollIntoView({ behavior: "smooth" }); }
        return;
      }
      try { localStorage.removeItem("vedic-pending-life-question"); } catch (e) {}
      requestAnswer({ birth: payload });
    });
    document.getElementById("lq-answer-prashna-btn").addEventListener("click", function () {
      var box = document.getElementById("lq-prashna-inline");
      if (box) box.hidden = !box.hidden;
    });
    document.getElementById("lq-p-go").addEventListener("click", function () {
      var num = parseInt(document.getElementById("lq-p-number").value, 10);
      var place = document.getElementById("lq-p-place").value.trim();
      if (!num || num < 1 || num > 249) {
        showAnswerStatus(L === "ne" ? "कृपया १ देखि २४९ बीचको अङ्क भर्नुहोस्।" : "Please enter a number between 1 and 249.");
        return;
      }
      if (!place) {
        showAnswerStatus(L === "ne" ? "कृपया स्थान भर्नुहोस्।" : "Please enter a place.");
        return;
      }
      fetch("/api/places?q=" + encodeURIComponent(place)).then(function (r) { return r.json(); }).then(function (data) {
        var first = (data.places || [])[0];
        if (!first) throw new Error("noplace");
        requestAnswer({ prashna: { number: num, place_id: first.id } });
      }).catch(function () {
        showAnswerStatus(L === "ne" ? "स्थान भेटिएन — प्रश्न खण्डमा स्थान छान्नुहोस्।" : "Place not found — pick a place in the Prashna section.");
      });
    });
    if (!skipScroll) detailEl.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  /* When a chart is computed while a question waits for an answer,
     answer it automatically (app.js dispatches vedic-chart-computed). */
  window.addEventListener("vedic-chart-computed", function (ev) {
    var pending = null;
    try { pending = localStorage.getItem("vedic-pending-life-question"); } catch (e) {}
    if (pending && currentId === pending && ev.detail) {
      try { localStorage.removeItem("vedic-pending-life-question"); } catch (e) {}
      requestAnswer({ birth: ev.detail });
      if (window.vedicNavigate) window.vedicNavigate("life-questions", "lq-detail");
      else if (detailEl) detailEl.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  });

  function renderAll() {
    renderCats();
    var keep = catEl ? catEl.value : "";
    renderList();
    if (catEl) catEl.value = keep;
    if (subEl) {
      subEl.textContent = lang() === "ne"
        ? "प्रश्न छान्नुहोस्, त्यसपछि आफ्नो कुण्डली वा प्रश्नबाट उत्तर पाउनुहोस् — परम्परागत सम्भावना-आधारित मार्गदर्शन मात्र, निश्चित फैसला होइन।"
        : "Pick a question, then get an answer from your chart or by Prashna — traditional probability guidance, never a certain verdict.";
    }
    if (currentId) renderDetail(currentId, true);
  }

  if (catEl) catEl.addEventListener("change", renderList);
  ["lang-en", "lang-ne"].forEach(function (id) {
    var b = document.getElementById(id);
    if (b) b.addEventListener("click", function () { setTimeout(renderAll, 0); });
  });

  fetch("/api/life-questions").then(function (r) { return r.json(); }).then(function (data) {
    cats = data.categories || [];
    all = data.questions || [];
    renderAll();
  }).catch(function () {
    listEl.innerHTML = '<p class="results-meta">Life Questions could not be loaded.</p>';
  });
})();
