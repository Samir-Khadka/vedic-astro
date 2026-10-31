"use strict";
/* Renderer harness: loads the real static/app.js + static/share.js into a
   DOM-stubbed vm context and runs renderBundle()/saveCurrentChart() against
   real /api/kundali bundles. Guards the user-visible failure mode where one
   throwing section killed the whole chart behind a generic error. */
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const ROOT = path.join(__dirname, "..");

class StubEl {
  constructor(tag = "div") {
    this.tagName = tag.toUpperCase();
    this.innerHTML = ""; this.textContent = ""; this.value = "";
    this.hidden = false; this.dataset = {}; this.type = ""; this.className = "";
    this.children = []; this.options = []; this.open = false; this.checked = false;
    this._cls = new Set(); this._attrs = {};
    const self = this;
    this.classList = {
      add: (...c) => c.forEach((x) => self._cls.add(x)),
      remove: (...c) => c.forEach((x) => self._cls.delete(x)),
      toggle: (c, force) => {
        const on = force !== undefined ? !!force : !self._cls.has(c);
        if (on) self._cls.add(c); else self._cls.delete(c);
        return on;
      },
      contains: (c) => self._cls.has(c),
    };
    this.style = { setProperty: () => {}, removeProperty: () => {} };
  }
  addEventListener() {}
  removeEventListener() {}
  remove() {} // intro auto-hide calls intro.remove() after a timeout
  appendChild(c) { this.children.push(c); return c; }
  append(...cs) { this.children.push(...cs); }
  setAttribute(k, v) { this._attrs[k] = v; }
  getAttribute(k) { return this._attrs[k]; }
  closest() { return null; }
  querySelector() { return new StubEl(); }
  querySelectorAll() { return []; }
  getContext() {
    return new Proxy({}, {
      get: (t, p) => (typeof p === "string" ? () => {} : undefined),
      set: () => true,
    });
  }
  scrollIntoView() {}
  requestSubmit() {}
  get childElementCount() { return this.children.length; }
}

function loadApp({ lang = "en", throwOnSave = false, fetchScript = null } = {}) {
  const store = new Map();
  if (lang) store.set("vedic-astro-lang", lang);
  const localStorage = {
    getItem: (k) => (store.has(k) ? store.get(k) : null),
    setItem: (k, v) => {
      if (throwOnSave && k === "vedic-astro-charts") throw new Error("quota");
      store.set(k, String(v));
    },
    removeItem: (k) => store.delete(k),
  };
  const elements = new Map();
  const getEl = (id) => {
    if (!elements.has(id)) elements.set(id, new StubEl());
    return elements.get(id);
  };
  const document = {
    getElementById: getEl,
    createElement: (tag) => new StubEl(tag),
    createElementNS: () => new StubEl("text"),
    // Cache querySelector results so tests can read what renderers wrote
    // into "#planet-table tbody" etc. (app code never uses querySelectorAll
    // for render targets, only for button groups).
    querySelector: (sel) => getEl("qs:" + sel),
    querySelectorAll: () => [],
    addEventListener() {},
    documentElement: new StubEl("html"),
  };
  let rafCalls = 0;
  const fetchQueue = fetchScript ? [...fetchScript] : null;
  const sandbox = {
    console, setTimeout, clearTimeout, URLSearchParams, Intl, Date, Math, JSON,
    AbortController,
    document,
    window: {
      innerWidth: 1280, innerHeight: 800, scrollY: 0,
      location: { origin: "https://x", search: "" },
      matchMedia: () => ({ matches: false, addListener() {}, addEventListener() {} }),
      addEventListener() {},
    },
    navigator: { clipboard: { writeText: async () => {} } },
    localStorage,
    fetch: async (url) => {
      // Scripted entries apply ONLY to /api/kundali: app load itself calls
      // loadPanchang(), which would otherwise eat the first scripted entry.
      if (fetchQueue && fetchQueue.length && String(url).includes("/api/kundali")) {
        const next = fetchQueue.shift();
        if (next.throw) throw next.throw;
        return next;
      }
      if (String(url).includes("/api/tz")) {
        return { ok: true, json: async () => ({ tz: "Asia/Kathmandu" }) };
      }
      return {
        ok: true,
        json: async () => ({
          paksha: "Shukla", tithi_index: 0, nakshatra_index: 0, yoga_index: 0,
          karana: "Bava", weekday: 0, sunrise: "1998-05-14T05:16:32+05:45",
          sunset: "1998-05-14T18:43:51+05:45",
        }),
      };
    },
    requestAnimationFrame: (cb) => {
      if (rafCalls++ < 3) setTimeout(() => cb(Date.now()), 0);
      return 0;
    },
    cancelAnimationFrame: () => {},
    performance: { now: () => Date.now() },
    IntersectionObserver: class { observe() {} unobserve() {} disconnect() {} },
  };
  sandbox.window.requestAnimationFrame = sandbox.requestAnimationFrame;
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  sandbox.module = { exports: {} };
  sandbox.exports = sandbox.module.exports;
  vm.runInContext(fs.readFileSync(path.join(ROOT, "static/share.js"), "utf8"), sandbox);
  Object.assign(sandbox, sandbox.module.exports);
  // coords.js loads before app.js in production (pure helpers, no DOM);
  // the vm context needs it for the same reason.
  vm.runInContext(fs.readFileSync(path.join(ROOT, "static/coords.js"), "utf8"), sandbox);
  Object.assign(sandbox, sandbox.module.exports);
  const appSrc = fs.readFileSync(path.join(ROOT, "static/app.js"), "utf8") +
    "\n;globalThis.__harness = { STATE, renderBundle, saveCurrentChart, drawChart, renderMatch, renderPrashna, fetchKundaliWithRetry, isRetryableKundaliError, signColHeader, settlePlaceTz, PLACE_TZ_PENDING, ensureManualTz };";
  vm.runInContext(appSrc, sandbox);
  // el(id) mirrors document.getElementById (creating the stub on demand);
  // the raw Map only holds ids the app code actually touched.
  return { h: sandbox.__harness, elements, document, store, el: getEl };
}

function loadBundles() {
  const out = {};
  for (const n of ["sample", "london", "sydney", "urlabari", "retro"]) {
    out[n] = JSON.parse(fs.readFileSync(path.join(__dirname, "fixtures", `b_${n}.json`), "utf8"));
  }
  return out;
}

const SECTION_IDS = ["results-title", "glance-strip", "chart-svg-wrap", "planet-table",
  "current-dasha", "kp-table", "dosha-cards", "av-table", "prediction-sections",
  "strength-summary", "transit-table", "numerology-body", "lalkitab-body",
  "premium-chapters", "deep-planets", "chalit-table", "argala-table"];

test("renderBundle renders all real bundles in EN and NE without throwing", () => {
  const bundles = loadBundles();
  for (const [name, bundle] of Object.entries(bundles)) {
    for (const lang of ["en", "ne"]) {
      const { h, elements } = loadApp({ lang });
      h.STATE.bundle = bundle;
      h.STATE.birthPayload = { dob: "1998-05-14", tob: "06:30", place_id: "kathmandu" };
      h.renderBundle(); // must not throw
      const title = elements.get("results-title").textContent;
      assert.ok(title.length > 0, `${name}/${lang}: results-title set`);
      assert.ok(elements.get("chart-svg-wrap").innerHTML.includes("<svg"),
        `${name}/${lang}: chart SVG rendered`);
      assert.ok(elements.get("glance-strip").innerHTML.length > 0,
        `${name}/${lang}: glance strip rendered`);
    }
  }
});

test("renderBundle renders every section for the sample bundle", () => {
  const { h, elements } = loadApp({ lang: "en" });
  h.STATE.bundle = JSON.parse(fs.readFileSync(path.join(__dirname, "fixtures", "b_sample.json"), "utf8"));
  h.STATE.birthPayload = { dob: "1998-05-14", tob: "06:30", place_id: "kathmandu" };
  h.renderBundle();
  const elFor = (id) => elements.get(id) || elements.get("qs:#" + id + " tbody");
  for (const id of SECTION_IDS) {
    const el = elFor(id);
    const content = (el && (el.innerHTML || el.textContent)) || "";
    assert.ok(content.length > 0, `section element ${id} rendered`);
  }
});

test("saveCurrentChart stores, dedupes, and never throws on storage failure", () => {
  const { h, store } = loadApp({ lang: "en" });
  h.STATE.bundle = JSON.parse(fs.readFileSync(path.join(__dirname, "fixtures", "b_sample.json"), "utf8"));
  h.STATE.birthPayload = { dob: "1998-05-14", tob: "06:30", place_id: "kathmandu" };
  h.saveCurrentChart();
  h.saveCurrentChart(); // same chart twice -> still one entry
  let saved = JSON.parse(store.get("vedic-astro-charts"));
  assert.equal(saved.length, 1, "duplicate chart deduped");
  h.STATE.birthPayload = { dob: "1998-05-14", tob: "06:30", place_id: "london" };
  h.saveCurrentChart();
  saved = JSON.parse(store.get("vedic-astro-charts"));
  assert.equal(saved.length, 2, "different chart added");
  // Storage failure must never throw (it once hid every chart behind the
  // generic error, because save ran inside the submit handler's try).
  const bad = loadApp({ throwOnSave: true });
  bad.h.STATE.bundle = JSON.parse(fs.readFileSync(path.join(__dirname, "fixtures", "b_sample.json"), "utf8"));
  bad.h.STATE.birthPayload = { dob: "1998-05-14", tob: "06:30", place_id: "kathmandu" };
  bad.h.saveCurrentChart(); // must not throw
});

test("one missing bundle section never kills the whole render", () => {
  const base = JSON.parse(fs.readFileSync(path.join(__dirname, "fixtures", "b_sample.json"), "utf8"));
  const CORE = new Set(["birth", "lagna", "planets", "charts"]);
  const failures = [];
  for (const key of Object.keys(base)) {
    const { h, el } = loadApp({ lang: "en" });
    const bundle = JSON.parse(JSON.stringify(base));
    delete bundle[key];
    h.STATE.bundle = bundle;
    h.STATE.birthPayload = { dob: "1998-05-14", tob: "06:30", place_id: "kathmandu" };
    let coreOk;
    try {
      coreOk = h.renderBundle();
    } catch (e) {
      failures.push(`${key}: ${e.message}`);
      continue;
    }
    if (CORE.has(key)) {
      assert.equal(coreOk, false, `core correctly reports failure without ${key}`);
    } else {
      assert.equal(coreOk, true, `core still renders without ${key}`);
      assert.ok(el("chart-svg-wrap").innerHTML.includes("<svg"),
        `chart still renders without ${key}`);
    }
  }
  assert.deepEqual(failures, [], `renderBundle threw for missing keys: ${failures.join("; ")}`);
});

test("renderBundle with a corrupted section still renders the rest", () => {
  const { h, elements, el } = loadApp({ lang: "en" });
  const bundle = JSON.parse(fs.readFileSync(path.join(__dirname, "fixtures", "b_sample.json"), "utf8"));
  bundle.strength = { shadbala: null }; // corrupted strength section
  bundle.lal_kitab = null;
  h.STATE.bundle = bundle;
  h.STATE.birthPayload = { dob: "1998-05-14", tob: "06:30", place_id: "kathmandu" };
  assert.equal(h.renderBundle(), true, "core chart still renders");
  assert.ok(el("chart-svg-wrap").innerHTML.includes("<svg"));
  assert.ok(el("glance-strip").innerHTML.length > 0);
  const notes = elements.get("section-notes");
  assert.ok(notes && notes.children.length >= 2,
    "each failed section gets a named per-section note");
  assert.ok(notes.children.every((c) => (c.textContent || "").includes("could not be shown")),
    "notes name the failure in plain language");
});

test("kundali fetch retries once on a wake-up failure, then succeeds", async () => {
  const { h } = loadApp({
    fetchScript: [
      { throw: new TypeError("network down") },
      { ok: true, json: async () => ({ marker: 1 }) },
    ],
  });
  let retries = 0;
  const data = await h.fetchKundaliWithRetry({ dob: "1998-05-14" }, () => retries++);
  assert.equal(data.marker, 1);
  assert.equal(retries, 1, "retried exactly once");
});

test("kundali fetch does not retry a 4xx input error", async () => {
  const { h } = loadApp({ fetchScript: [{ ok: false, status: 400 }] });
  let retries = 0;
  await assert.rejects(
    h.fetchKundaliWithRetry({ dob: "x" }, () => retries++),
    (e) => e.status === 400);
  assert.equal(retries, 0, "input errors are not retried");
});

/* ---- 2026-10-31: frontend fixes ----
   signColHeader: bindu-table sign headers previously did signName(i).slice(0, 4),
   which slices UTF-16 code units — in Nepali this printed broken Devanagari
   ("वृश्", "कन्य", "कुम्") instead of whole names ("वृश्चिक", "कन्या", "कुम्भ").
   settlePlaceTz / ensureManualTz: a submit landing before the async /api/tz
   lookup (place without tz, or the 400ms manual-coords debounce) resolved
   used to fail with "no place picked" even though the place was selected. */

const SIGNS_NE_FULL = ["मेष","वृष","मिथुन","कर्कट","सिंह","कन्या","तुला","वृश्चिक","धनु","मकर","कुम्भ","मीन"];

test("bindu-table headers show whole Nepali sign names, truncated English", () => {
  const { h } = loadApp({ lang: "ne" });
  for (let i = 0; i < 12; i++) {
    assert.equal(h.signColHeader(i), SIGNS_NE_FULL[i],
      `sign ${i}: Nepali header must be the whole name, got ${h.signColHeader(i)}`);
  }
  const { h: hen } = loadApp({ lang: "en" });
  assert.equal(hen.signColHeader(7), "Scor", "English keeps the 4-letter form");
  for (let i = 0; i < 12; i++) {
    assert.ok(hen.signColHeader(i).length <= 4, `en header ${i} fits the column`);
  }
});

test("Ashtakavarga headers render whole Nepali names end to end", () => {
  const { h, elements } = loadApp({ lang: "ne" });
  h.STATE.bundle = JSON.parse(fs.readFileSync(path.join(__dirname, "fixtures", "b_sample.json"), "utf8"));
  h.STATE.birthPayload = { dob: "1998-05-14", tob: "06:30", place_id: "kathmandu" };
  h.renderBundle();
  const head = elements.get("av-head").innerHTML;
  assert.ok(head.includes("<th>वृश्चिक</th>"), `AV header keeps the whole name: ${head.slice(0, 160)}`);
  assert.ok(!head.includes("वृश्<") && !head.includes("कन्य<") && !head.includes("कुम्<"),
    "no truncated Devanagari fragments in AV headers");
});

test("settlePlaceTz waits for a pending lookup, then resolves at once", async () => {
  const { h } = loadApp({ lang: "en" });
  let resolved = false;
  let release;
  h.PLACE_TZ_PENDING["f-place"] = new Promise((res) => { release = res; }).then(() => { resolved = true; });
  const settling = h.settlePlaceTz("f-place", 500);
  await new Promise((r) => setTimeout(r, 30));
  assert.equal(resolved, false, "still waiting while the lookup is in flight");
  release();
  await settling;
  assert.equal(resolved, true, "submit proceeds once the lookup lands");
  await h.settlePlaceTz("f-place", 50); // entry consumed: resolves immediately
});

test("settlePlaceTz gives up after its timeout instead of hanging", async () => {
  const { h } = loadApp({ lang: "en" });
  h.PLACE_TZ_PENDING["f-place"] = new Promise(() => {}); // never resolves
  const t0 = Date.now();
  await h.settlePlaceTz("f-place", 50);
  assert.ok(Date.now() - t0 < 5000, "timed out instead of hanging the submit");
});

test("ensureManualTz fills an empty timezone, keeps a hand-entered one", async () => {
  const { h, el } = loadApp({ lang: "en" });
  el("f-lat").value = "27.7172";
  el("f-lon").value = "85.324";
  el("f-tz").value = "";
  await h.ensureManualTz();
  assert.equal(el("f-tz").value, "Asia/Kathmandu", "debounce-window submit still gets the lookup result");
  el("f-tz").value = "Pacific/Auckland";
  await h.ensureManualTz();
  assert.equal(el("f-tz").value, "Pacific/Auckland", "a hand-entered timezone always wins");
});
