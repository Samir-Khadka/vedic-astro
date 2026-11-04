"use strict";
/* Nepali festivals in the month calendar: the frontend renders the
   backend's additive `festivals` list per day (violet festival chips,
   deep-red public-holiday chips, distinct from the gold astronomical
   markers), a bilingual legend, and a Festivals & holidays section
   in the day-detail panel. These tests pin the wiring strings so a
   refactor cannot silently drop the feature. */
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const appJs = fs.readFileSync(path.join(__dirname, "..", "static", "app.js"), "utf8");
const css = fs.readFileSync(path.join(__dirname, "..", "static", "styles.css"), "utf8");
const html = fs.readFileSync(path.join(__dirname, "..", "static", "index.html"), "utf8");
const sw = fs.readFileSync(path.join(__dirname, "..", "static", "sw.js"), "utf8");

test("calendar cells render festival/holiday badges from d.festivals", () => {
  assert.ok(appJs.includes("function calFestivals(festivals)"));
  assert.ok(appJs.includes("calFestivals(d.festivals)"));
  assert.ok(appJs.includes("cal-holiday"));
  assert.ok(appJs.includes("cal-festival"));
});

test("day-detail panel has a Festivals & holidays section", () => {
  assert.ok(appJs.includes("cal_fest_title"));
  assert.ok(appJs.includes("d.festivals"));
  assert.ok(appJs.includes("cal_holiday_flag"));
  assert.ok(appJs.includes("cal_no_fest"));
});

test("legend element exists and is rendered bilingually", () => {
  assert.ok(html.includes('id="cal-legend"'));
  assert.ok(appJs.includes("function renderCalLegend()"));
  assert.ok(appJs.includes("cal_legend_marker"));
  assert.ok(appJs.includes("cal_legend_festival"));
  assert.ok(appJs.includes("cal_legend_holiday"));
});

test("the old false hint text is gone", () => {
  assert.ok(!appJs.includes("regional festival dates are not guessed"));
  assert.ok(!appJs.includes("क्षेत्रीय पर्व मितिहरू अनुमान गरिँदैनन्"));
  assert.ok(appJs.includes("cal_hint:\"Gold chips are astronomical markers"));
});

test("clicked day gets a selected state", () => {
  assert.ok(appJs.includes("cal-selected"));
  assert.ok(appJs.includes("selectedCalDate"));
  assert.ok(css.includes(".cal-cell.cal-selected"));
});

test("holiday chips are deep red, festival chips violet", () => {
  assert.ok(css.includes(".cal-holiday"));
  assert.ok(css.includes("#a31621"));
  assert.ok(css.includes(".cal-festival"));
});

test("service worker cache is v7", () => {
  assert.ok(sw.includes('vedic-astro-static-v7'));
  assert.ok(!sw.includes('vedic-astro-static-v6'));
});
