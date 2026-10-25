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
  assert.equal(chartKey({ dob: "2000-01-10", tob: "06:30", place_id: "kathmandu" }), "2000-01-10|06:30|kathmandu");
});

test("shareParams omits empty name", () => {
  assert.deepEqual(shareParams({ dob: "2000-01-01", tob: "06:30", place_id: "kathmandu" }),
    { dob: "2000-01-01", tob: "06:30", place_id: "kathmandu" });
});
