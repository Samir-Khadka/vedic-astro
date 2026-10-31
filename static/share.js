"use strict";
/* Pure helpers for saved charts + shareable links (no DOM access, so
 * they are unit-testable in node exactly as the browser uses them).
 *
 * A share link carries the birth inputs as query params:
 *   ?dob=YYYY-MM-DD&tob=HH:MM&name=..&place_id=..   (gazetteer place)
 *   ?dob=..&tob=..&lat=..&lon=..&tz=..&place_name=.. (custom place)
 * On load, the app auto-fills the form from these params and generates.
 * Saved charts are the same payloads stored in localStorage (max 8,
 * deduplicated on dob+tob+place) — no account, no server storage.
 */

function shareParams(payload) {
  const q = {};
  if (payload.name) q.name = payload.name;
  q.dob = payload.dob;
  q.tob = payload.tob;
  if (payload.ayanamsa && payload.ayanamsa !== "lahiri") q.ayanamsa = payload.ayanamsa;
  if (payload.house_system && payload.house_system !== "placidus") q.house_system = payload.house_system;
  if (payload.place_id) {
    q.place_id = payload.place_id;
  } else {
    q.lat = String(payload.lat);
    q.lon = String(payload.lon);
    q.tz = payload.tz;
    if (payload.place_name) q.place_name = payload.place_name;
  }
  return q;
}

function buildShareUrl(origin, payload) {
  const q = new URLSearchParams(shareParams(payload));
  return origin + "/?" + q.toString();
}

function parseShareParams(search) {
  const q = new URLSearchParams(search);
  const dob = q.get("dob");
  const tob = q.get("tob");
  if (!dob || !tob) return null;
  if (!/^\d{4}-\d{2}-\d{2}$/.test(dob)) return null;
  if (!/^\d{2}:\d{2}(:\d{2})?$/.test(tob)) return null;
  const place_id = q.get("place_id");
  const extra = {};
  const aya = q.get("ayanamsa");
  if (aya && ["lahiri", "raman", "krishnamurti", "yukteshwar"].includes(aya)) extra.ayanamsa = aya;
  const hs = q.get("house_system");
  if (hs && ["placidus", "equal", "whole", "sripati"].includes(hs)) extra.house_system = hs;
  if (place_id) {
    return { name: q.get("name") || "", dob, tob, place_id, ...extra };
  }
  const lat = parseFloat(q.get("lat"));
  const lon = parseFloat(q.get("lon"));
  const tz = q.get("tz");
  if (!Number.isFinite(lat) || !Number.isFinite(lon) || !tz) return null;
  if (lat < -90 || lat > 90 || lon < -180 || lon > 180) return null;
  return { name: q.get("name") || "", dob, tob, lat, lon, tz,
           place_name: q.get("place_name") || "", ...extra };
}

function chartKey(payload) {
  // Saved-chart entries are wrappers ({..., payload}) while share links
  // and tests pass plain payloads — unwrap so both key the same chart.
  const p = (payload && payload.payload) || payload || {};
  const place = p.place_id || `${p.lat},${p.lon}`;
  const aya = p.ayanamsa || "lahiri";
  const hs = p.house_system || "placidus";
  return `${p.dob}|${p.tob}|${place}|${aya}|${hs}`;
}

function dedupeCharts(saved, payload, max) {
  const key = chartKey(payload);
  const next = saved.filter((c) => chartKey(c) !== key);
  next.unshift(payload);
  return next.slice(0, max || 8);
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { shareParams, buildShareUrl, parseShareParams, chartKey, dedupeCharts };
}
