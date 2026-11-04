"use strict";
/* Page router — one page visible at a time, chosen by URL hash.
 *
 * Pages (hash -> page id):
 *   #home, #kundali, #complete-report, #premium, #prashna, #matching,
 *   #panchang, #horoscope, #muhurta, #life-questions, #ai-astrologer
 * Unknown hashes fall back to Home, EXCEPT hashes that name an element
 * on the current page (e.g. Complete Report contents links like
 * #cr-section-...) — those are in-page anchors and are left alone so
 * the browser's native anchor scroll keeps working.
 *
 * Other scripts navigate with window.vedicNavigate(page, targetId):
 * it sets the hash (so Back/Forward keep working) and scrolls to the
 * target element on that page when given, instead of the page top.
 * If the page is already current, it shows it directly, since setting
 * an unchanged hash fires no hashchange event.
 */
var ROUTER_PAGES = [
  { id: "home", hash: "home" },
  { id: "kundali", hash: "kundali" },
  { id: "complete-report", hash: "complete-report" },
  { id: "premium", hash: "premium" },
  { id: "prashna", hash: "prashna" },
  { id: "matching", hash: "matching" },
  { id: "panchang", hash: "panchang" },
  { id: "horoscope", hash: "horoscope" },
  { id: "muhurta", hash: "muhurta" },
  { id: "life-questions", hash: "life-questions" },
  { id: "ai-astrologer", hash: "ai-astrologer" },
];

/* Pure: hash (with or without leading '#') -> page id, or null when
 * the hash names no page. Empty hash means Home. */
function pageFromHash(hash) {
  if (!hash) return "home";
  var h = String(hash).replace(/^#/, "");
  if (!h) return "home";
  for (var i = 0; i < ROUTER_PAGES.length; i++) {
    if (ROUTER_PAGES[i].hash === h) return ROUTER_PAGES[i].id;
  }
  return null;
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { ROUTER_PAGES: ROUTER_PAGES, pageFromHash: pageFromHash };
}

if (typeof document !== "undefined") {
  (function () {
    var currentPage = null;
    var pendingTarget = null;

    function showPage(id, targetId) {
      /* Page containers only (.page) — nav links also carry data-page
         attributes and must never be hidden by page switching. */
      var pages = document.querySelectorAll(".page[data-page]");
      pages.forEach(function (p) {
        p.hidden = p.getAttribute("data-page") !== id;
      });
      document.querySelectorAll(".main-nav a[data-page]").forEach(function (a) {
        a.classList.toggle("is-active", a.getAttribute("data-page") === id);
      });
      currentPage = id;
      if (targetId) {
        var el = document.getElementById(targetId);
        if (el) el.scrollIntoView({ behavior: "smooth" });
      } else {
        window.scrollTo(0, 0);
      }
      /* The hero 3D canvas sizes itself on window resize; a page that
         was hidden at load may have measured zero width, so re-measure
         when Home becomes visible. */
      if (id === "home") window.dispatchEvent(new Event("resize"));
    }

    function handleHash() {
      var raw = window.location.hash.replace(/^#/, "");
      var page = pageFromHash(raw);
      if (page) {
        showPage(page, pendingTarget);
        pendingTarget = null;
        return;
      }
      if (raw && document.getElementById(raw)) return; /* in-page anchor */
      showPage("home");
    }

    window.addEventListener("hashchange", handleHash);

    window.vedicNavigate = function (page, targetId) {
      if (window.location.hash === "#" + page) {
        showPage(page, targetId || null);
        return;
      }
      pendingTarget = targetId || null;
      window.location.hash = page;
    };

    window.vedicCurrentPage = function () { return currentPage; };

    /* Nav clicks on the already-current page fire no hashchange, so
       still scroll that page to the top. */
    document.querySelectorAll(".main-nav a[data-page]").forEach(function (a) {
      a.addEventListener("click", function () {
        var page = a.getAttribute("data-page");
        if (window.location.hash === "#" + page) showPage(page);
      });
    });

    /* Initial page. */
    (function init() {
      var raw = window.location.hash.replace(/^#/, "");
      var page = pageFromHash(raw);
      if (page) { showPage(page); return; }
      if (raw) {
        var el = document.getElementById(raw);
        var container = el && el.closest ? el.closest("[data-page]") : null;
        if (container) { showPage(container.getAttribute("data-page"), raw); return; }
      }
      /* A share link carrying a chart opens on the Kundali page, where
         the form and results live. */
      try {
        if (typeof parseShareParams === "function" && parseShareParams(window.location.search)) {
          showPage("kundali");
          return;
        }
      } catch (e) { /* fall through to Home */ }
      showPage("home");
    })();
  })();
}
