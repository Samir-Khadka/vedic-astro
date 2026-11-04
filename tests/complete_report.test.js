"use strict";
/* Complete Report frontend: loads the real static/app.js into a
   DOM-stubbed vm context (same pattern as render.test.js) and checks
   the report renderer helpers against a real /api/complete-report
   payload fixture: section order, bilingual titles, the unavailable
   Aaditya & Lagnam note (never invented numbers), Yantra without a
   magic-square grid, chart reuse, and the POST of the birth payload. */
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
  remove() {}
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

function loadApp({ lang = "en" } = {}) {
  const store = new Map();
  if (lang) store.set("vedic-astro-lang", lang);
  const localStorage = {
    getItem: (k) => (store.has(k) ? store.get(k) : null),
    setItem: (k, v) => { store.set(k, String(v)); },
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
    querySelector: (sel) => getEl("qs:" + sel),
    querySelectorAll: () => [],
    addEventListener() {},
    documentElement: new StubEl("html"),
    body: new StubEl("body"),
  };
  const fixture = JSON.parse(fs.readFileSync(
    path.join(__dirname, "fixtures", "complete_report_sample.json"), "utf8"));
  const calls = [];
  let rafCalls = 0; // cap like render.test.js: app animation loops via rAF would otherwise keep node alive forever
  const sandbox = {
    console, setTimeout, clearTimeout, URLSearchParams, Intl, Date, Math, JSON,
    AbortController,
    document,
    window: {
      innerWidth: 1280, innerHeight: 800, scrollY: 0,
      location: { origin: "https://x", search: "" },
      matchMedia: () => ({ matches: false, addListener() {}, addEventListener() {} }),
      addEventListener() {}, removeEventListener() {}, print() {},
    },
    navigator: { clipboard: { writeText: async () => {} } },
    localStorage,
    fetch: async (url, opts) => {
      calls.push({ url: String(url), body: opts && opts.body });
      if (String(url).includes("/api/complete-report")) {
        return { ok: true, json: async () => fixture };
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
  vm.runInContext(fs.readFileSync(path.join(ROOT, "static/coords.js"), "utf8"), sandbox);
  Object.assign(sandbox, sandbox.module.exports);
  const appSrc = fs.readFileSync(path.join(ROOT, "static/app.js"), "utf8") +
    "\n;globalThis.__harness = { STATE, crTitle, crSectionHTML, crReportHTML, crModelSections, CR_BASIC_SECTIONS, renderCompleteReport, loadCompleteReport, drawChartInto };";
  vm.runInContext(appSrc, sandbox);
  return { h: sandbox.__harness, elements, el: getEl, calls, fixture };
}

test("report HTML keeps fixture section order in TOC and body", () => {
  const { h, fixture } = loadApp();
  const { toc, body } = h.crReportHTML(fixture);
  const tocIds = [...toc.matchAll(/href="#cr-([a-z_0-9]+)"/g)].map((m) => m[1]);
  assert.deepEqual(tocIds, fixture.section_ids);
  const bodyIds = [...body.matchAll(/id="cr-([a-z_0-9]+)"/g)].map((m) => m[1]);
  assert.deepEqual(bodyIds, fixture.section_ids);
  assert.equal(bodyIds.length, 10);
});

test("section titles follow the current language", () => {
  const { h, fixture } = loadApp({ lang: "en" });
  assert.equal(h.crTitle(fixture.sections[0]), "Title Page");
  const ne = loadApp({ lang: "ne" });
  assert.equal(ne.h.crTitle(fixture.sections[0]), "शीर्षक पृष्ठ");
  assert.equal(ne.h.crTitle(fixture.sections[5]), "आदित्य र लग्नम् दशा");
});

test("unavailable Aaditya & Lagnam renders its honest note, no numbers", () => {
  const { h, fixture } = loadApp();
  const sec = fixture.sections.find((s) => s.id === "aaditya_lagnam");
  assert.equal(sec.available, false);
  const html = h.crSectionHTML(sec);
  assert.match(html, /Not yet computed/);
  assert.match(html, /not computed by the engine yet/);
  assert.doesNotMatch(html, /<td>/); // no fabricated table of dasha values
});

test("Yantra renders names, numbers, metal and mantra — and no grid", () => {
  const { h, fixture } = loadApp();
  const sec = fixture.sections.find((s) => s.id === "yantra");
  const html = h.crSectionHTML(sec);
  assert.match(html, /Sun Yantra/);
  assert.match(html, /Gold/);
  assert.match(html, /Suryaya Namah/);
  assert.doesNotMatch(html, /yantra-grid/);
  assert.doesNotMatch(html, /magic-square/);
});

test("renderCompleteReport draws D1/D9 and Varshphal charts with the existing renderer", () => {
  const { h, elements, fixture } = loadApp();
  h.STATE.bundle = { planets: [], lagna: { degree_in_sign: 0 }, charts: {} };
  assert.equal(h.renderCompleteReport(fixture, true), true);
  assert.equal(elements.get("complete-report").hidden, false);
  for (const id of ["cr-chart-d1", "cr-chart-d9", "cr-chart-v2026"]) {
    assert.match(elements.get(id).innerHTML, /<svg/, `${id} has an SVG chart`);
  }
  assert.match(elements.get("complete-report-body").innerHTML, /Complete Kundali Report|Title Page/);
});

test("section renderers never throw on empty or unknown data", () => {
  const { h } = loadApp();
  assert.doesNotThrow(() => h.crSectionHTML({ id: "planet_position", title_en: "x", title_ne: "x", available: true, data: {} }));
  assert.doesNotThrow(() => h.crSectionHTML({ id: "varshphal", title_en: "x", title_ne: "x", available: true, data: {} }));
  assert.doesNotThrow(() => h.crSectionHTML({ id: "no_such_section", title_en: "x", title_ne: "x", available: true, data: {} }));
  assert.doesNotThrow(() => h.crSectionHTML({ id: "sade_sati", title_en: "x", title_ne: "x", available: true, data: { current: {}, lifetime: {} } }));
  assert.doesNotThrow(() => h.crReportHTML({ sections: [] }));
  assert.doesNotThrow(() => h.crReportHTML(null));
});

test("loadCompleteReport POSTs the same birth payload to /api/complete-report", async () => {
  const { h, elements, calls } = loadApp();
  const payload = { name: "Sample", dob: "1990-05-15", tob: "08:30", place_id: "kathmandu" };
  h.STATE.birthPayload = payload;
  h.STATE.bundle = { planets: [], lagna: { degree_in_sign: 0 }, charts: {} };
  await h.loadCompleteReport();
  const call = calls.find((c) => c.url.includes("/api/complete-report"));
  assert.ok(call, "complete-report endpoint called");
  assert.deepEqual(JSON.parse(call.body), payload);
  assert.ok(h.STATE.completeReport, "report stored on STATE");
  assert.match(elements.get("complete-report-toc").innerHTML, /Title Page/);
  // Second click with the same payload just reveals, without a second POST.
  const before = calls.length;
  await h.loadCompleteReport();
  assert.equal(calls.length, before);
});

/* ---- Print models (step 2) ---- */

function fullReport(fixture) {
  // Every real section id, in API order, so Basic filtering can be
  // checked exactly even though the fixture is trimmed.
  const ids = ["title", "planet_position", "birth_details", "sayan_charts",
    "moon_navamsa", "chalit_bhava", "shodash_varga", "shodash_varga_table",
    "karaka_avastha_tara", "sudarshan", "aspects_planets", "aspects_bhava",
    "aspects_cusps", "upagrahas_arudha", "vimsopak_bala", "ashtakavarga",
    "shad_bhava_bala", "sarvato_bhadra", "vimshottari", "yogini",
    "aaditya_lagnam", "dasha_phala", "varshphal", "general_predictions",
    "effects_of_planets", "nakshatra_phal", "sade_sati", "manglik",
    "kaalsarp", "ratna_mantra", "yantra"];
  const byId = Object.fromEntries(fixture.sections.map((s) => [s.id, s]));
  return { sections: ids.map((id) => byId[id] || { id, title_en: id, title_ne: id, available: true, data: {} }) };
}

test("print models: Detailed and Book keep all sections, Basic keeps exactly its subset in order", () => {
  const { h, fixture } = loadApp();
  const report = fullReport(fixture);
  // Joined-string comparison: arrays cross the vm realm boundary, so
  // deepStrictEqual rejects them on prototype mismatch.
  const ids = (arr) => [...arr].join(",");
  assert.equal(ids(h.crModelSections(report, "detailed").map((s) => s.id)),
    ids(report.sections.map((s) => s.id)));
  assert.equal(ids(h.crModelSections(report, "book").map((s) => s.id)),
    ids(report.sections.map((s) => s.id)));
  assert.equal(ids(h.CR_BASIC_SECTIONS), ["title", "planet_position",
    "birth_details", "moon_navamsa", "vimshottari", "sade_sati", "manglik",
    "kaalsarp", "general_predictions"].join(","));
  assert.equal(ids(h.crModelSections(report, "basic").map((s) => s.id)),
    ids(h.CR_BASIC_SECTIONS));
  // Unknown ids in the subset are skipped, never rendered empty.
  const partial = { sections: report.sections.filter((s) => s.id !== "manglik") };
  assert.equal(
    ids(h.crModelSections(partial, "basic").map((s) => s.id)),
    ids([...h.CR_BASIC_SECTIONS].filter((id) => id !== "manglik")));
});

test("print models: Basic TOC/body show only the subset and condense Vimshottari to its current summary", () => {
  const { h, fixture } = loadApp();
  const report = fullReport(fixture);
  const { toc, body } = h.crReportHTML(report, "basic");
  const tocCount = (toc.match(/<li>/g) || []).length;
  assert.equal(tocCount, 9, "Basic TOC has 9 entries");
  assert.match(body, /General Predictions|general_predictions/);
  assert.doesNotMatch(body, /Ashtakavarga|ashtakavarga/);
  assert.doesNotMatch(body, /Yantra|yantra/);
  // Condensed Vimshottari: current summary present, full timeline table gone.
  const vim = body.split('id="cr-vimshottari"')[1].split("</article>")[0];
  assert.match(vim, /Current:/);
  assert.doesNotMatch(vim, /Antardashas/);
  // Detailed keeps everything, including the full Vimshottari timeline.
  const full = h.crReportHTML(report, "detailed");
  assert.equal((full.toc.match(/<li>/g) || []).length, 31);
  assert.match(full.body, /Antardashas/);
});

test("print models: renderCompleteReport applies the selected model and Book class, and re-render keeps it", () => {
  const { h, elements, fixture } = loadApp();
  const report = fullReport(fixture);
  h.STATE.completeReportModel = "basic";
  assert.equal(h.renderCompleteReport(report, true), true);
  assert.equal((elements.get("complete-report-toc").innerHTML.match(/<li>/g) || []).length, 9);
  h.STATE.completeReportModel = "book";
  assert.equal(h.renderCompleteReport(report, true), true);
  assert.equal((elements.get("complete-report-toc").innerHTML.match(/<li>/g) || []).length, 31);
  assert.ok(elements.get("complete-report").classList.contains("cr-model-book"));
  h.STATE.completeReportModel = "detailed";
  assert.equal(h.renderCompleteReport(report, true), true);
  assert.ok(!elements.get("complete-report").classList.contains("cr-model-book"));
});
