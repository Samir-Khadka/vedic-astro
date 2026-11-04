"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const { shareParams, buildShareUrl, parseShareParams, chartKey, dedupeCharts } = require("../static/share.js");

test("share round-trip for gazetteer and custom places", () => {
  const a = { name: "A", dob: "1998-05-14", tob: "06:30", place_id: "kathmandu" };
  const back = parseShareParams(new URL(buildShareUrl("https://x", a)).search);
  assert.deepEqual(back, a);
  const b = { name: "", dob: "2000-01-01", tob: "12:00", lat: 35.01, lon: 135.76, tz: "Asia/Tokyo", place_name: "Kyoto" };
  assert.deepEqual(parseShareParams(new URL(buildShareUrl("https://x", b)).search), b);
});

test("parse rejects bad input", () => {
  assert.equal(parseShareParams("?dob=1998-05-14"), null);
  assert.equal(parseShareParams("?dob=14-05-1998&tob=06:30"), null);
  assert.equal(parseShareParams("?dob=1998-05-14&tob=06:30&lat=999&lon=0&tz=Asia/Kathmandu"), null);
  assert.equal(parseShareParams("?dob=1998-05-14&tob=06:30&lat=27&lon=85"), null);
});

test("dedupe keeps newest first, max 8", () => {
  let saved = [];
  for (let i = 0; i < 10; i++) {
    saved = dedupeCharts(saved, { dob: `2000-01-${String(i + 1).padStart(2, "0")}`, tob: "06:30", place_id: "kathmandu" });
  }
  assert.equal(saved.length, 8);
  assert.equal(saved[0].dob, "2000-01-10");
  const again = dedupeCharts(saved, { dob: "2000-01-10", tob: "06:30", place_id: "kathmandu" });
  assert.equal(again.length, 8);
  assert.equal(again[0].dob, "2000-01-10");
  assert.equal(chartKey({ dob: "2000-01-10", tob: "06:30", place_id: "kathmandu" }), "2000-01-10|06:30|kathmandu|lahiri|placidus");
  assert.equal(chartKey({ dob: "2000-01-10", tob: "06:30", place_id: "kathmandu", ayanamsa: "raman" }),
    "2000-01-10|06:30|kathmandu|raman|placidus");
});

test("shareParams omits empty name", () => {
  assert.deepEqual(shareParams({ dob: "2000-01-01", tob: "06:30", place_id: "kathmandu" }),
    { dob: "2000-01-01", tob: "06:30", place_id: "kathmandu" });
});

test("saved-chart export/import round-trip, with bad entries skipped", () => {
  const { exportSavedCharts, importSavedCharts } = require("../static/share.js");
  const entry = { name: "A", dob: "1998-05-14", tob: "06:30", place_name: "Kathmandu",
    payload: { name: "A", dob: "1998-05-14", tob: "06:30", place_id: "kathmandu" } };
  const text = exportSavedCharts([entry, { dob: "bad", tob: "06:30", place_id: "kathmandu" }]);
  const doc = JSON.parse(text);
  assert.equal(doc.format, "vedic-astro-saved-charts");
  assert.equal(doc.charts.length, 1);
  const res = importSavedCharts(text, []);
  assert.equal(res.error, null);
  assert.equal(res.charts.length, 1);
  assert.equal(res.charts[0].dob, "1998-05-14");
  // Bare array and broken JSON both behave safely.
  assert.equal(importSavedCharts(JSON.stringify([entry]), []).charts.length, 1);
  const bad = importSavedCharts("not json", [entry]);
  assert.equal(bad.error, "invalid-json");
  assert.equal(bad.charts.length, 1);
  const wrong = importSavedCharts(JSON.stringify({ format: "other", charts: [] }), []);
  assert.equal(wrong.error, "bad-format");
});

test("chartComparisonRows: lagna, planets, dasha, same-sign flags", () => {
  const { chartComparisonRows } = require("../static/share.js");
  const mk = (lagnaSign, moonSign, md, ad) => ({
    lagna: { sign: lagnaSign, sign_en: "Sagittarius", sign_ne: "धनु", nakshatra_en: "Mula", nakshatra_ne: "मूल", house: null },
    planets: [
      { planet: "Sun", sign: 8, sign_en: "Sagittarius", sign_ne: "धनु", nakshatra_en: "Mula", nakshatra_ne: "मूल", house: 1 },
      { planet: "Moon", sign: moonSign, sign_en: "Libra", sign_ne: "तुला", nakshatra_en: "Swati", nakshatra_ne: "स्वाती", house: 11 },
    ],
    dasha: { current: { mahadasha: { lord: md }, antardasha: { lord: ad } } },
  });
  const rows = chartComparisonRows(mk(8, 6, "Saturn", "Saturn"), mk(8, 3, "Saturn", "Jupiter"), "en");
  const byLabel = Object.fromEntries(rows.map((r) => [r.label, r]));
  assert.equal(byLabel.Lagna.same, true);
  assert.equal(byLabel.Moon.same, false);
  assert.equal(byLabel.Sun.same, true);
  assert.equal(byLabel.Mars.a, "—"); // missing planet never crashes
  assert.equal(byLabel.Mahadasha.same, true);
  assert.equal(byLabel.Antardasha.same, false);
  assert.equal(rows.length, 12); // Lagna + 9 planets + 2 dasha
  const neRows = chartComparisonRows(mk(8, 6, "Saturn", "Saturn"), mk(8, 6, "Saturn", "Saturn"), "ne");
  assert.match(neRows[0].a, /धनु/);
});
