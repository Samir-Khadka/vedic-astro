"use strict";
/* AI Astrologer harness: loads the real static/ai_astrologer.js into a
   DOM-stubbed vm context and drives the ask flow end to end (input ->
   stubbed /api/ask-astrologer -> rendered chat HTML). Guards the
   user-visible text the file renders, which no test covered before. */
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
  }
  addEventListener(ev, fn) { (this._listeners[ev] ||= []).push(fn); }
  removeEventListener() {}
  fire(ev, arg) { for (const fn of this._listeners[ev] || []) fn(arg); }
  appendChild(c) { this.children.push(c); return c; }
  append(...cs) { this.children.push(...cs); }
  setAttribute() {}
  getAttribute() { return null; }
  querySelector() { return new StubEl(); }
  querySelectorAll() { return []; }
  remove() {}
  scrollIntoView() {}
}

function loadAi({ lang = "en", answer = null } = {}) {
  const store = new Map();
  if (lang) store.set("vedic-astro-lang", lang);
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
    window: {
      addEventListener() {},
      vedicLastBirthPayload: { dob: "1998-05-14", tob: "06:30", place_id: "kathmandu" },
    },
    navigator: {},
    localStorage,
    fetch: async (url) => {
      if (String(url).includes("/api/ask-astrologer")) {
        return { ok: true, json: async () => answer };
      }
      return { ok: false, status: 404, json: async () => ({}) };
    },
  };
  sandbox.window.location = { reload() {} };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(fs.readFileSync(path.join(ROOT, "static/ai_astrologer.js"), "utf8"), sandbox);
  return { sandbox, elements, el: getEl };
}

const ANSWER = {
  area_title_en: "Career", area_title_ne: "करियर",
  direct_answer_en: "Career looks supported.", direct_answer_ne: "करियरमा सहयोग देखिन्छ।",
  band: "Favourable",
  planet_table: [
    { planet: "Sun", sign_en: "Aries", sign_ne: "मेष", house: 1, effect_en: "Sun in the 1st house.", effect_ne: "सूर्य 1st भावमा।" },
    { planet: "Moon", sign_en: "Scorpio", sign_ne: "वृश्चिक", house: 2, effect_en: "Moon in the 2nd house.", effect_ne: "चन्द्र 2nd भावमा।" },
    { planet: "Mars", sign_en: "Aries", sign_ne: "मेष", house: 3, effect_en: "Mars in the 3rd house.", effect_ne: "मङ्गल 3rd भावमा।" },
    { planet: "Jupiter", sign_en: "Aquarius", sign_ne: "कुम्भ", house: 11, effect_en: "Jupiter in the 11th house.", effect_ne: "बृहस्पति 11th भावमा।" },
  ],
  supporting: [], challenging: [], timing_en: "", disclaimer_en: "",
};

async function askAndReadHtml({ lang }) {
  const { el } = loadAi({ lang, answer: ANSWER });
  el("ai-input").value = "Will my career grow?";
  el("ai-send").fire("click");
  await new Promise((r) => setTimeout(r, 50));
  return el("ai-chat").children.map((c) => c.innerHTML).join("\n");
}

/* ---- 2026-11-11: ordinal fix ----
   planetTableHTML built the house label as `${house}th house`, so a
   planet in the 1st/2nd/3rd house printed "1th house"/"2th house"/
   "3th house" — the same bug class as the 2026-11-09 backend/app.js
   ordinal sweep, missed because ai_astrologer.js was not in it. */
test("planet table prints 1st/2nd/3rd house, never 1th/2th/3th", async () => {
  const html = await askAndReadHtml({ lang: "en" });
  for (const want of ["1st house", "2nd house", "3rd house", "11th house"]) {
    assert.ok(html.includes(want), `expected "${want}" in:\n${html}`);
  }
  for (const bad of [/\b1th house/, /\b2th house/, /\b3th house/]) {
    assert.ok(!bad.test(html), `must not print "${bad}":\n${html}`);
  }
});

test("planet table in Nepali uses औँ भाव, never the English ordinal", async () => {
  const html = await askAndReadHtml({ lang: "ne" });
  assert.ok(html.includes("1औँ भाव"), `expected Nepali ordinal in:\n${html}`);
  assert.ok(!html.includes("th house"), `no English ordinal in Nepali output:\n${html}`);
});
