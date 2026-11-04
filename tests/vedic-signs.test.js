"use strict";
/* Vedic signs only: no Western astrological symbol may appear in the
   visible frontend files. The site uses Vedic sign numbers, full
   traditional sign names, and short planet abbreviations instead —
   the same convention as the printed patri charts. ॐ and ✦ are
   decorative and are explicitly allowed. */
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const BANNED = [
  "♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓",
  "☉", "☽", "☿", "♀", "♂", "♃", "♄",
];
const FILES = ["app.js", "scene3d.js", "index.html"];

for (const file of FILES) {
  test(`no Western astrological symbols in static/${file}`, () => {
    const src = fs.readFileSync(path.join(__dirname, "..", "static", file), "utf8");
    for (const ch of BANNED) {
      assert.ok(!src.includes(ch), `static/${file} still contains ${ch}`);
    }
  });
}

test("deleted symbol constants cannot creep back", () => {
  for (const file of ["app.js", "scene3d.js"]) {
    const src = fs.readFileSync(path.join(__dirname, "..", "static", file), "utf8");
    assert.ok(!src.includes("SIGN_GLYPHS"), `static/${file} still defines SIGN_GLYPHS`);
    assert.ok(!src.includes("PLANET_GLYPHS"), `static/${file} still defines PLANET_GLYPHS`);
    assert.ok(!src.includes("GLYPHS"), `static/${file} still references GLYPHS`);
  }
});

test("Vedic replacements are present", () => {
  const app = fs.readFileSync(path.join(__dirname, "..", "static", "app.js"), "utf8");
  assert.ok(app.includes("renderHeroRing"), "app.js must render the hero ring from numbers");
  assert.ok(app.includes("FOOTER_SIGNS_NE"), "app.js must carry Nepali footer sign names");
  assert.ok(app.includes("वृषभ"), "Nepali footer names must use वृषभ");
  assert.ok(app.includes("PLANET_ABBR"), "app.js must carry planet abbreviations");
  assert.ok(app.includes("rebuildHeroWheel"), "language toggle must rebuild the 3D wheel");
  const scene = fs.readFileSync(path.join(__dirname, "..", "static", "scene3d.js"), "utf8");
  assert.ok(scene.includes("Noto Sans Devanagari"), "3D wheel font must support Devanagari digits");
  assert.ok(scene.includes("rebuildHeroWheel"), "scene3d.js must expose rebuildHeroWheel");
  const html = fs.readFileSync(path.join(__dirname, "..", "static", "index.html"), "utf8");
  assert.ok(html.includes("Mesha ✦ Vrishabha"), "footer band must list traditional sign names");
  assert.ok(html.includes("✦"), "✦ separators must be kept");
});

test("service-worker cache bumped so returning visitors get the new files", () => {
  const sw = fs.readFileSync(path.join(__dirname, "..", "static", "sw.js"), "utf8");
  assert.ok(sw.includes("vedic-astro-static-v4"), "sw.js cache must be v4");
});
