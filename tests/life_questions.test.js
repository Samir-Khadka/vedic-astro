"use strict";
/* Life Questions harness: loads the real static/life_questions.js into a
   DOM-stubbed vm context and drives the Prashna answer flow end to end
   (pick question -> number + place -> stubbed /api/places -> captured
   POST to /api/life-questions/{id}/answer). Guards the place payload
   the flow sends, which no test covered before. */
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
    this.children = []; this.scrollTop = 0; this.scrollHeight = 0;
    this._listeners = {};
    this._qsa = [];
    this._cls = new Set();
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
    this.options = [];
  }
  addEventListener(ev, fn) { (this._listeners[ev] ||= []).push(fn); }
  removeEventListener() {}
  fire(ev, arg) { for (const fn of this._listeners[ev] || []) fn(arg); }
  appendChild(c) { this.children.push(c); return c; }
  append(...cs) { this.children.push(...cs); }
  setAttribute() {}
  getAttribute() { return null; }
  querySelector() { return new StubEl(); }
  querySelectorAll() { return this._qsa; }
  remove() {}
  scrollIntoView() {}
}

const QUESTION = {
  id: "marriage_timing", category: "marriage",
  category_en: "Marriage", category_ne: "विवाह",
  question_en: "When may marriage take place?", question_ne: "विवाह कहिले हुन सक्छ?",
  prime_houses: [7], supporting_houses: [2, 11], negating_houses: [6],
  significator_en: "Venus", significator_ne: "शुक्र",
  what_to_check_en: "Check the 7th house.", what_to_check_ne: "सप्तम भाव हेर्नुहोस्।",
  timing_note_en: "Timing note.", timing_note_ne: "समय टिप्पणी।",
  disclaimer_en: "Guidance only.", disclaimer_ne: "मार्गदर्शन मात्र।",
  ruling: null,
};

const ANSWER = {
  band: "favourable", band_en: "Favourable indication", band_ne: "अनुकूल सङ्केत",
  explanation_en: "Supported.", explanation_ne: "सहयोग देखिन्छ।",
  score: 3, prime_hits: 1, supporting_hits: 1, negating_hits: 0,
  evidence: [], disclaimer_en: "Guidance only.", disclaimer_ne: "मार्गदर्शन मात्र।",
};

function loadLife({ places }) {
  const store = new Map([["vedic-astro-lang", "en"]]);
  const localStorage = {
    getItem: (k) => (store.has(k) ? store.get(k) : null),
    setItem: (k, v) => store.set(k, String(v)),
    removeItem: (k) => store.delete(k),
  };
  const elements = new Map();
  const getEl = (id) => {
    if (!elements.has(id)) elements.set(id, new StubEl());
    return elements.get(id);
  };
  const captured = { answerBody: null };
  const document = {
    getElementById: getEl,
    createElement: (tag) => new StubEl(tag),
    querySelector: () => new StubEl(),
    querySelectorAll: () => [],
    addEventListener() {},
    documentElement: new StubEl("html"),
    hidden: false,
    body: new StubEl("body"),
  };
  const sandbox = {
    console, setTimeout, clearTimeout, JSON, Math, Date,
    document,
    window: { addEventListener() {}, vedicLastBirthPayload: null },
    navigator: {},
    localStorage,
    fetch: async (url, opts) => {
      const u = String(url);
      if (u.startsWith("/api/life-questions/") && u.endsWith("/answer")) {
        captured.answerBody = JSON.parse(opts.body);
        return { ok: true, json: async () => ANSWER };
      }
      if (u.startsWith("/api/places")) {
        return { ok: true, json: async () => ({ places }) };
      }
      if (u === "/api/life-questions") {
        return {
          ok: true,
          json: async () => ({
            categories: [{ slug: "marriage", en: "Marriage", ne: "विवाह" }],
            questions: [QUESTION],
          }),
        };
      }
      return { ok: false, status: 404, json: async () => ({}) };
    },
  };
  sandbox.window.location = { reload() {} };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(fs.readFileSync(path.join(ROOT, "static/life_questions.js"), "utf8"), sandbox);
  return { sandbox, elements, el: getEl, captured };
}

async function drivePrashna({ places, placeText }) {
  const { el, captured } = loadLife({ places });
  // The list is rendered when the initial fetch resolves; the item
  // button must be in place before that render runs.
  const itemBtn = new StubEl("button");
  itemBtn.dataset = { id: "marriage_timing" };
  el("lq-list")._qsa = [itemBtn];
  await new Promise((r) => setTimeout(r, 50));
  itemBtn.fire("click");
  el("lq-answer-prashna-btn").fire("click");
  el("lq-p-number").value = "42";
  el("lq-p-place").value = placeText;
  el("lq-p-go").fire("click");
  await new Promise((r) => setTimeout(r, 50));
  return captured.answerBody;
}

/* ---- 2026-11-22: Prashna answer dropped worldwide places ----
   The flow took the first /api/places hit and sent only
   place_id: first.id — but worldwide (non-gazetteer) hits carry
   id null plus lat/lon/tz, so the answer request 400d with
   "provide place_id or lat/lon/tz" and the UI wrongly said the
   place was not found. Verified live before fixing. */
test("prashna answer sends lat/lon/tz for a worldwide (non-gazetteer) place", async () => {
  const body = await drivePrashna({
    placeText: "Lukla",
    places: [{ id: null, source: "global", name: "Lukla", country: "Nepal",
      label: "Lukla, Nepal", lat: 27.6875, lon: 86.7314, tz: "Asia/Kathmandu" }],
  });
  assert.ok(body, "the answer request must have been sent");
  assert.equal(body.prashna.number, 42);
  assert.equal(body.prashna.place_id, undefined, "no place_id for a global hit");
  assert.equal(body.prashna.lat, 27.6875);
  assert.equal(body.prashna.lon, 86.7314);
  assert.equal(body.prashna.tz, "Asia/Kathmandu");
});

test("prashna answer still sends place_id for a gazetteer place", async () => {
  const body = await drivePrashna({
    placeText: "Kathmandu",
    places: [{ id: "kathmandu", name: "Kathmandu", country: "Nepal",
      lat: 27.7172, lon: 85.324, tz: "Asia/Kathmandu", name_ne: "काठमाडौं" }],
  });
  assert.ok(body, "the answer request must have been sent");
  assert.equal(body.prashna.number, 42);
  assert.equal(body.prashna.place_id, "kathmandu");
  assert.equal(body.prashna.lat, undefined, "gazetteer hits need no coordinates");
});
