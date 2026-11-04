"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const { ROUTER_PAGES, pageFromHash } = require("../static/router.js");

test("every page in the brief has exactly one hash", () => {
  const ids = ROUTER_PAGES.map((p) => p.id);
  assert.deepEqual(ids, [
    "home",
    "kundali",
    "complete-report",
    "premium",
    "prashna",
    "matching",
    "panchang",
    "horoscope",
    "muhurta",
    "life-questions",
    "ai-astrologer",
  ]);
  const hashes = ROUTER_PAGES.map((p) => p.hash);
  assert.equal(new Set(hashes).size, hashes.length);
  assert.equal(new Set(ids).size, ids.length);
});

test("pageFromHash maps hashes with and without '#'", () => {
  assert.equal(pageFromHash("#kundali"), "kundali");
  assert.equal(pageFromHash("kundali"), "kundali");
  assert.equal(pageFromHash("#ai-astrologer"), "ai-astrologer");
  assert.equal(pageFromHash("#complete-report"), "complete-report");
  assert.equal(pageFromHash("#muhurta"), "muhurta");
  assert.equal(pageFromHash("#life-questions"), "life-questions");
});

test("pageFromHash: empty hash is Home, unknown hash is null (router falls back)", () => {
  assert.equal(pageFromHash(""), "home");
  assert.equal(pageFromHash("#"), "home");
  assert.equal(pageFromHash(null), "home");
  assert.equal(pageFromHash("#no-such-page"), null);
  /* In-page anchors (e.g. Complete Report contents links) must NOT
     resolve to a page, so the router leaves them alone. */
  assert.equal(pageFromHash("#cr-section-title"), null);
});
