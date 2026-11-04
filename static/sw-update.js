"use strict";
/* Service-worker update prompt for the long-lived SPA tab.
 *
 * Problem it fixes: hash routing never performs a full navigation, so a
 * tab left open (or a profile whose old worker controls the page) never
 * triggers the browser's update check, and the old worker keeps serving
 * its cached app shell indefinitely. This module polls for updates while
 * the page is open and, when a new worker is ready, shows a small
 * bilingual banner. It NEVER reloads on its own: only the user's tap on
 * Refresh reloads, so work in progress (e.g. a computation) is never lost.
 *
 * How a new version is detected (either path shows the banner):
 *  - registration.waiting already set when we register, or an
 *    updatefound worker reaching "installed" while a controller exists;
 *  - controllerchange after a previous controller existed. This is the
 *    common path here because sw.js calls skipWaiting() on install, so
 *    the new worker usually activates (and claims) instead of waiting.
 * On a first install there is no previous controller, so no banner is
 * shown for the initial worker.
 */
(function () {
  if (!("serviceWorker" in navigator)) return;

  var UPDATE_MIN_INTERVAL_MS = 5 * 60 * 1000; // throttle: at most one check per 5 min
  var UPDATE_POLL_MS = 30 * 60 * 1000; // periodic check while the tab is open
  var TEXT = {
    en: { msg: "A new version of VedicAstro is available.", refresh: "Refresh", dismiss: "Dismiss" },
    ne: { msg: "VedicAstro को नयाँ संस्करण उपलब्ध छ।", refresh: "ताजा गर्नुहोस्", dismiss: "बन्द गर्नुहोस्" },
  };

  var registration = null;
  var banner = null;
  var dismissed = false; // dismissed for the currently-known update only
  var reloading = false; // Refresh tapped; reload once on controllerchange
  var lastCheck = 0;
  var hadController = !!navigator.serviceWorker.controller;

  function lang() {
    try {
      var stored = localStorage.getItem("vedic-astro-lang");
      if (stored === "ne" || stored === "en") return stored;
    } catch (e) { /* storage unavailable: fall through */ }
    return document.documentElement.lang === "ne" ? "ne" : "en";
  }

  function ensureBanner() {
    if (banner) return banner;
    banner = document.createElement("div");
    banner.id = "sw-update-banner";
    banner.className = "sw-update-banner";
    banner.setAttribute("role", "status");
    banner.hidden = true;
    var text = document.createElement("span");
    text.className = "sw-update-text";
    var refresh = document.createElement("button");
    refresh.type = "button";
    refresh.className = "sw-update-refresh";
    refresh.addEventListener("click", onRefresh);
    var dismiss = document.createElement("button");
    dismiss.type = "button";
    dismiss.className = "sw-update-dismiss";
    dismiss.textContent = "×";
    dismiss.addEventListener("click", function () {
      dismissed = true;
      banner.hidden = true;
    });
    banner.appendChild(text);
    banner.appendChild(refresh);
    banner.appendChild(dismiss);
    document.body.appendChild(banner);
    return banner;
  }

  function showBanner() {
    if (dismissed || reloading) return;
    ensureBanner();
    var t = TEXT[lang()] || TEXT.en;
    banner.querySelector(".sw-update-text").textContent = t.msg;
    banner.querySelector(".sw-update-refresh").textContent = t.refresh;
    banner.querySelector(".sw-update-dismiss").setAttribute("aria-label", t.dismiss);
    banner.hidden = false;
  }

  function hideBanner() {
    if (banner) banner.hidden = true;
  }

  function checkForUpdate() {
    if (!registration) return;
    var now = Date.now();
    if (now - lastCheck < UPDATE_MIN_INTERVAL_MS) return;
    lastCheck = now;
    registration.update().catch(function () { /* offline: try again later */ });
  }

  function trackWorker(worker) {
    if (!worker) return;
    worker.addEventListener("statechange", function () {
      if (worker.state === "installed" && navigator.serviceWorker.controller) showBanner();
    });
  }

  function onRefresh() {
    if (reloading) return;
    reloading = true;
    hideBanner();
    var waiting = registration && registration.waiting;
    if (waiting) {
      waiting.postMessage({ type: "SKIP_WAITING" });
      // Fallback: if controllerchange never fires, reload anyway shortly.
      setTimeout(function () {
        if (reloading) {
          reloading = false;
          window.location.reload();
        }
      }, 1500);
    } else {
      window.location.reload();
    }
  }

  navigator.serviceWorker.addEventListener("controllerchange", function () {
    if (!hadController) {
      // First install taking control: not an update, never show the banner.
      hadController = true;
      return;
    }
    hadController = true;
    if (reloading) {
      window.location.reload();
      return;
    }
    showBanner();
  });

  navigator.serviceWorker.register("/sw.js").then(function (reg) {
    registration = reg;
    if (reg.waiting && navigator.serviceWorker.controller) showBanner();
    if (reg.installing) trackWorker(reg.installing);
    reg.addEventListener("updatefound", function () {
      // A genuinely new worker arrived: a previous dismiss no longer applies.
      dismissed = false;
      trackWorker(reg.installing);
    });
    document.addEventListener("visibilitychange", function () {
      if (!document.hidden) checkForUpdate();
    });
    setInterval(checkForUpdate, UPDATE_POLL_MS);
    checkForUpdate();
  }).catch(function () { /* registration failed: app still works uncached */ });

  // Keep the banner's language in sync if the user toggles EN/NE while it shows.
  ["lang-en", "lang-ne"].forEach(function (id) {
    var btn = document.getElementById(id);
    if (btn) btn.addEventListener("click", function () {
      if (banner && !banner.hidden) showBanner();
    });
  });
})();
