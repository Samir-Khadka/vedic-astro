"use strict";
/* Service-worker update prompt: static checks over the wiring.
 *
 * The live banner/refresh behavior is covered by the Playwright audit
 * (stuck-tab simulation); these tests pin the wiring so a later edit
 * cannot silently drop a piece of it. No Western astrological symbols
 * appear in any of the asserted strings.
 */
const assert = require("node:assert");
const fs = require("node:fs");
const path = require("node:path");
const { test } = require("node:test");

const read = (p) => fs.readFileSync(path.join(__dirname, "..", p), "utf8");

test("update module polls for updates while the tab is open", () => {
  const src = read("static/sw-update.js");
  assert.ok(src.includes("registration.update()"), "must call registration.update()");
  assert.ok(src.includes("visibilitychange"), "must check again when the tab becomes visible");
  assert.ok(src.includes("setInterval"), "must poll on a timer while the page is open");
  assert.ok(src.includes("30 * 60 * 1000"), "poll interval must be 30 minutes");
  assert.ok(src.includes("UPDATE_MIN_INTERVAL_MS"), "update checks must be throttled");
});

test("update module shows a banner only for a real update, never auto-reloads", () => {
  const src = read("static/sw-update.js");
  assert.ok(src.includes("sw-update-banner"), "must render a banner element");
  assert.ok(src.includes("registration.waiting"), "must handle an already-waiting worker");
  assert.ok(src.includes("updatefound"), "must watch for newly found workers");
  assert.ok(src.includes("controllerchange"), "must react when a new worker takes control");
  assert.ok(src.includes("hadController"), "must not show the banner for the first install");
  assert.ok(src.includes("dismissed"), "banner must be dismissible");
  // Reloads happen only after the user taps Refresh: every location.reload
  // call site is guarded by the reloading flag (set only in onRefresh), and
  // no reload call appears before onRefresh is defined.
  assert.ok(src.includes("reloading = true"), "reload must be gated on the Refresh tap");
  assert.ok(src.indexOf("location.reload") > src.indexOf("function onRefresh"),
    "no reload may be wired before the Refresh handler");
});

test("refresh path hands control to the waiting worker", () => {
  const src = read("static/sw-update.js");
  assert.ok(src.includes('postMessage({ type: "SKIP_WAITING" })'),
    "Refresh must ask the waiting worker to skip waiting");
  const sw = read("static/sw.js");
  assert.ok(sw.includes('event.data.type === "SKIP_WAITING"'),
    "sw.js must listen for the SKIP_WAITING message");
  assert.ok(sw.includes("self.skipWaiting()"), "sw.js must skip waiting on that message");
});

test("banner text is bilingual English/Nepali", () => {
  const src = read("static/sw-update.js");
  assert.ok(src.includes("A new version of VedicAstro is available."));
  assert.ok(src.includes("VedicAstro को नयाँ संस्करण उपलब्ध छ।"));
  assert.ok(src.includes("ताजा गर्नुहोस्"));
});

test("update module is loaded after app.js and the old bare registration is gone", () => {
  const html = read("static/index.html");
  assert.ok(html.includes('<script src="/static/sw-update.js" defer></script>'),
    "index.html must load sw-update.js");
  assert.ok(html.indexOf("/static/app.js") < html.indexOf("/static/sw-update.js"),
    "sw-update.js must load after app.js");
  assert.ok(!html.includes('navigator.serviceWorker.register("/sw.js")'),
    "the bare inline registration must be replaced by the module");
  const sw = read("static/sw.js");
  assert.ok(sw.includes('"/static/sw-update.js"'), "sw.js ASSETS must include sw-update.js");
  assert.ok(sw.includes("vedic-astro-static-v8"), "sw.js cache must be v8");
});
