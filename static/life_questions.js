/* Life Questions library (Phase 1) — small standalone script so the
   main app.js bundle is untouched. Fetches /api/life-questions and
   renders in the current language (localStorage vedic-astro-lang). */
(function () {
  var listEl = document.getElementById("lq-list");
  if (!listEl) return;
  var catEl = document.getElementById("lq-category");
  var detailEl = document.getElementById("lq-detail");
  var all = [];
  var cats = [];

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

  function renderDetail(id) {
    var q = all.find(function (x) { return x.id === id; });
    if (!q || !detailEl) return;
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
      '<p class="results-meta">' + esc(t(q, "disclaimer")) + "</p>" +
      '<div class="field-row">' +
      '<button type="button" class="btn btn-gold" id="lq-kundali-btn">' + (L === "ne" ? "मेरो कुण्डली जाँच्नुहोस्" : "Check my chart") + "</button> " +
      '<button type="button" class="btn" id="lq-prashna-btn">' + (L === "ne" ? "प्रश्न सोध्नुहोस्" : "Ask Prashna") + "</button>" +
      "</div>";
    document.getElementById("lq-kundali-btn").addEventListener("click", function () {
      document.getElementById("kundali-form").scrollIntoView({ behavior: "smooth" });
    });
    document.getElementById("lq-prashna-btn").addEventListener("click", function () {
      var pq = document.getElementById("p-question");
      if (pq) pq.value = t(q, "question");
      document.getElementById("prashna").scrollIntoView({ behavior: "smooth" });
    });
    detailEl.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  function renderAll() {
    renderCats();
    var keep = catEl ? catEl.value : "";
    renderList();
    if (catEl) catEl.value = keep;
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
