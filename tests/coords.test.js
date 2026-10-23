/* Parser tests for static/coords.js — run with: node --test tests/
 * Covers decimal, signed decimal, direction letters (prefix/suffix, both
 * hemispheres), DMS variants, letter-vs-select conflict resolution, and
 * out-of-range rejection. */
"use strict";
const { test } = require("node:test");
const assert = require("node:assert/strict");
const { parseCoordinate } = require("../static/coords.js");

const EPS = 1e-9;
function expectOk(res, value, direction) {
  assert.equal(res.ok, true, JSON.stringify(res));
  assert.ok(Math.abs(res.value - value) < EPS, `${res.value} != ${value}`);
  assert.equal(res.direction, direction);
}

/* ---- plain decimals ---- */
test("unsigned decimal uses the select fallback", () => {
  expectOk(parseCoordinate("27.7172", "lat", "N"), 27.7172, "N");
  expectOk(parseCoordinate("27.7172", "lat", "S"), -27.7172, "S");
  expectOk(parseCoordinate("85.3240", "lon", "E"), 85.324, "E");
  expectOk(parseCoordinate("85.3240", "lon", "W"), -85.324, "W");
});

test("signed decimal beats the select fallback", () => {
  expectOk(parseCoordinate("-33.86", "lat", "N"), -33.86, "S"); // minus + N selected -> S
  expectOk(parseCoordinate("-33.86", "lat", "S"), -33.86, "S");
  expectOk(parseCoordinate("+27.7", "lat", "S"), 27.7, "N");
  expectOk(parseCoordinate("-74.006", "lon", "E"), -74.006, "W");
  expectOk(parseCoordinate("+74.006", "lon", "W"), 74.006, "E");
});

/* ---- direction letters ---- */
test("letter as suffix", () => {
  expectOk(parseCoordinate("27.7172 N", "lat", "S"), 27.7172, "N"); // letter beats select
  expectOk(parseCoordinate("33.86 S", "lat", "N"), -33.86, "S"); // letter beats select
  expectOk(parseCoordinate("85.3240E", "lon", "W"), 85.324, "E");
  expectOk(parseCoordinate("74.0060 W", "lon", "E"), -74.006, "W");
});

test("letter as prefix, any case", () => {
  expectOk(parseCoordinate("N 27.7172", "lat", "S"), 27.7172, "N");
  expectOk(parseCoordinate("s 33.86", "lat", "N"), -33.86, "S");
  expectOk(parseCoordinate("W74.006", "lon", "E"), -74.006, "W");
});

test("letter for the wrong axis is invalid", () => {
  assert.equal(parseCoordinate("27.7 E", "lat", "N").ok, false);
  assert.equal(parseCoordinate("85.3 N", "lon", "E").ok, false);
  assert.equal(parseCoordinate("27.7 N S", "lat", "N").ok, false);
});

test("sign plus agreeing letter is fine; zero is not negative zero", () => {
  expectOk(parseCoordinate("-33.86 S", "lat", "N"), -33.86, "S");
  const z = parseCoordinate("0", "lat", "S");
  assert.equal(z.ok, true);
  assert.ok(Object.is(z.value, 0));
});

/* ---- degrees / minutes / seconds ---- */
const DMS = 27 + 43 / 60 + 2 / 3600; // 27.717222...
test("DMS with symbols and spaces", () => {
  expectOk(parseCoordinate("27° 43′ 2″", "lat", "N"), DMS, "N");
  expectOk(parseCoordinate("27°43'2\"N", "lat", "S"), DMS, "N"); // letter beats select
  expectOk(parseCoordinate("27 43 02", "lat", "N"), DMS, "N");
  expectOk(parseCoordinate("85°19'26\"E", "lon", "E"), 85 + 19 / 60 + 26 / 3600, "E");
});

test("DMS degrees+minutes only, fractional minutes", () => {
  expectOk(parseCoordinate("27°43′", "lat", "N"), 27 + 43 / 60, "N");
  expectOk(parseCoordinate("27 43.5", "lat", "N"), 27.725, "N");
  expectOk(parseCoordinate("-27 43 02", "lat", "N"), -DMS, "S"); // sign covers whole DMS
});

test("DMS rejects minutes/seconds >= 60 and stray fractions", () => {
  assert.equal(parseCoordinate("27° 75′", "lat", "N").error, "invalid");
  assert.equal(parseCoordinate("27 43 99", "lat", "N").error, "invalid");
  assert.equal(parseCoordinate("27.5 43", "lat", "N").error, "invalid");
});

/* ---- range validation: errors, never clamping ---- */
test("out of range is a range error", () => {
  assert.deepEqual(parseCoordinate("90.0001", "lat", "N"), { ok: false, error: "range" });
  assert.deepEqual(parseCoordinate("91", "lat", "N"), { ok: false, error: "range" });
  assert.deepEqual(parseCoordinate("90°0′1″", "lat", "N"), { ok: false, error: "range" });
  assert.deepEqual(parseCoordinate("180.5", "lon", "E"), { ok: false, error: "range" });
  assert.deepEqual(parseCoordinate("181 W", "lon", "E"), { ok: false, error: "range" });
});

test("axis limits themselves are valid", () => {
  expectOk(parseCoordinate("90", "lat", "N"), 90, "N");
  expectOk(parseCoordinate("90 S", "lat", "N"), -90, "S");
  expectOk(parseCoordinate("180", "lon", "W"), -180, "W");
});

/* ---- garbage in ---- */
test("empty and garbage inputs", () => {
  assert.deepEqual(parseCoordinate("", "lat", "N"), { ok: false, error: "empty" });
  assert.deepEqual(parseCoordinate("   ", "lon", "E"), { ok: false, error: "empty" });
  assert.equal(parseCoordinate("abc", "lat", "N").error, "invalid");
  assert.equal(parseCoordinate("27.7.1", "lat", "N").error, "invalid");
  assert.equal(parseCoordinate("-", "lat", "N").error, "invalid");
  assert.equal(parseCoordinate("N", "lat", "N").error, "invalid");
});

/* ---- the Sydney case from the bug report ---- */
test("Sydney entered with direction letters resolves signed", () => {
  expectOk(parseCoordinate("33.8688 S", "lat", "N"), -33.8688, "S");
  expectOk(parseCoordinate("151.2093 E", "lon", "W"), 151.2093, "E");
});
