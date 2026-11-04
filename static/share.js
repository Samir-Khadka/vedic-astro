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


/* Open-JSON export/import for saved charts (Phase 2).
 * Format: {format: "vedic-astro-saved-charts", version: 1,
 *          exported_at: ISO string, charts: [saved entries]}
 * A bare array of entries is also accepted on import, so a hand-edited
 * or older file still loads. Invalid entries are skipped, never fatal,
 * and the merged list keeps the existing 8-chart cap. */

function isValidChartPayload(p) {
  if (!p || typeof p !== "object") return false;
  if (!/^\d{4}-\d{2}-\d{2}$/.test(p.dob || "")) return false;
  if (!/^\d{2}:\d{2}(:\d{2})?$/.test(p.tob || "")) return false;
  if (typeof p.place_id === "string" && p.place_id) return true;
  const lat = Number(p.lat), lon = Number(p.lon);
  return Number.isFinite(lat) && Number.isFinite(lon) && typeof p.tz === "string" && !!p.tz
    && lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180;
}

function normalizeSavedEntry(entry) {
  if (!entry || typeof entry !== "object") return null;
  const payload = entry.payload || entry;
  if (!isValidChartPayload(payload)) return null;
  if (entry.payload) return entry; // already a wrapper entry
  return { name: payload.name || "", dob: payload.dob, tob: payload.tob,
           place_name: payload.place_name || "", payload };
}

function exportSavedCharts(saved) {
  const charts = (Array.isArray(saved) ? saved : [])
    .map(normalizeSavedEntry).filter(Boolean);
  return JSON.stringify({ format: "vedic-astro-saved-charts", version: 1,
    exported_at: new Date().toISOString(), charts }, null, 2);
}

function importSavedCharts(text, existing, max) {
  let data;
  try { data = JSON.parse(text); } catch { return { charts: existing || [], skipped: 0, error: "invalid-json" }; }
  const list = Array.isArray(data) ? data : data.charts;
  if (!Array.isArray(list)) return { charts: existing || [], skipped: 0, error: "bad-format" };
  if (data.format && data.format !== "vedic-astro-saved-charts") {
    return { charts: existing || [], skipped: 0, error: "bad-format" };
  }
  let merged = Array.isArray(existing) ? existing.slice() : [];
  let skipped = 0;
  for (const raw of list) {
    const entry = normalizeSavedEntry(raw);
    if (!entry) { skipped++; continue; }
    const next = dedupeCharts(merged, entry, max || 8);
    if (next.length === merged.length && !next.some((c) => chartKey(c) === chartKey(entry))) skipped++;
    merged = next;
  }
  return { charts: merged, skipped, error: null };
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { shareParams, buildShareUrl, parseShareParams, chartKey, dedupeCharts, isValidChartPayload, normalizeSavedEntry, exportSavedCharts, importSavedCharts };
}
