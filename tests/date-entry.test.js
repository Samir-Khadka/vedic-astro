"use strict";
/* Date-entry validation logic: real dates, BS day limits, future rejection. */
const test = require("node:test");
const assert = require("node:assert/strict");
const de = require("../static/date_entry.js");

test("AD month lengths incl. leap years", () => {
  assert.equal(de.daysInAdMonth(2026, 2), 28);
  assert.equal(de.daysInAdMonth(2024, 2), 29);
  assert.equal(de.daysInAdMonth(2000, 2), 29);
  assert.equal(de.daysInAdMonth(1900, 2), 28);
  assert.equal(de.daysInAdMonth(2026, 4), 30);
});

test("parseAd rejects impossible dates", () => {
  assert.equal(de.parseAd("2026-02-30"), null);
  assert.equal(de.parseAd("2026-13-01"), null);
  assert.equal(de.parseAd("2026-00-10"), null);
  assert.equal(de.parseAd("not-a-date"), null);
  assert.deepEqual(de.parseAd("2024-02-29"), { y: 2024, m: 2, d: 29 });
});

test("validateDateTime: missing, bad, future, bad time", () => {
  const today = "2026-11-04";
  assert.equal(de.validateDateTime("", "06:30", today), "err_missing_date");
  assert.equal(de.validateDateTime("2026-02-30", "06:30", today), "err_bad_date");
  assert.equal(de.validateDateTime("2026-11-05", "06:30", today), "err_future_date");
  assert.equal(de.validateDateTime("2026-11-04", "06:30", today), null);
  assert.equal(de.validateDateTime("2026-11-04", "", today), "err_fields");
  assert.equal(de.validateDateTime("2026-11-04", "25:00", today), "err_bad_time");
  assert.equal(de.validateDateTime("2026-11-04", "6:30", today), "err_bad_time");
});

test("isValidTime accepts HH:MM only", () => {
  assert.equal(de.isValidTime("00:00"), true);
  assert.equal(de.isValidTime("23:59"), true);
  assert.equal(de.isValidTime("24:00"), false);
  assert.equal(de.isValidTime("12:60"), false);
});

test("BS day limit: day beyond the month length is invalid", () => {
  // 2083 Kartik has 30 days; 2083 Ashadh has 32.
  assert.equal(de.isValidBsDate(2083, 7, 30, 30), true);
  assert.equal(de.isValidBsDate(2083, 7, 31, 30), false);
  assert.equal(de.isValidBsDate(2083, 3, 32, 32), true);
  assert.equal(de.isValidBsDate(2083, 3, 33, 32), false);
  assert.equal(de.isValidBsDate(1999, 1, 1, 30), false);
  assert.equal(de.isValidBsDate(2091, 1, 1, 30), false);
  assert.equal(de.isValidBsDate(2083, 13, 1, 30), false);
});

test("BS month names mirror the backend lists", () => {
  assert.equal(de.DE_BS_MONTHS_EN.length, 12);
  assert.equal(de.DE_BS_MONTHS_NE.length, 12);
  assert.equal(de.DE_BS_MONTHS_EN[0], "Baisakh");
  assert.equal(de.DE_BS_MONTHS_NE[6], "कार्तिक");
  assert.equal(de.BS_MIN_YEAR, 2000);
  assert.equal(de.BS_MAX_YEAR, 2090);
});
