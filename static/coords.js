"use strict";
/* Pure coordinate parsing for the manual-coordinates fallback.
 *
 * parseCoordinate(raw, kind, fallbackDir) resolves free-form user input
 * to ONE signed decimal value plus the hemisphere it implies, so the UI
 * (text field + N/S/E/W select) can never sit in a contradictory state.
 *
 *   kind        "lat" | "lon"
 *   fallbackDir the direction currently chosen in the select ("N"/"S"
 *               for latitude, "E"/"W" for longitude); used only when the
 *               typed text carries neither a letter nor a sign.
 *
 * Accepted forms:
 *   "27.7172"              signed/unsigned decimal degrees
 *   "-33.86"   "+85.324"   explicit sign
 *   "27.7172 N"  "N 27.7172"  "85.3240E"  "33.86 S"   direction letter
 *   "27° 43′ 2″"  "27°43'2\"N"  "27 43 02"           degrees/minutes/seconds
 *
 * Hemisphere precedence: typed letter > typed sign > select (fallbackDir).
 * S/W are negative. Minutes/seconds must be < 60. The magnitude must fit
 * the axis (lat <= 90, lon <= 180) — out-of-range is an error, never
 * silently clamped.
 *
 * Returns { ok: true, value, direction } or
 *         { ok: false, error: "empty" | "invalid" | "range" }.
 */
function parseCoordinate(raw, kind, fallbackDir) {
  const isLat = kind === "lat";
  const limit = isLat ? 90 : 180;
  const posDir = isLat ? "N" : "E";
  const negDir = isLat ? "S" : "W";

  let s = raw == null ? "" : String(raw);
  s = s.trim();
  if (!s) return { ok: false, error: "empty" };

  // --- direction letter (prefix or suffix, either case) ---
  let letter = null;
  const letters = s.match(/[NSEW]/gi) || [];
  if (letters.length > 0) {
    const uniq = [...new Set(letters.map((c) => c.toUpperCase()))];
    if (uniq.length > 1) return { ok: false, error: "invalid" };
    letter = uniq[0];
    if (letter !== posDir && letter !== negDir) {
      // A letter for the wrong axis, e.g. "E" in the latitude field.
      return { ok: false, error: "invalid" };
    }
    s = s.replace(/[NSEW]/gi, " ").trim();
  }

  // --- explicit sign ---
  let sign = null;
  if (s.startsWith("-") || s.startsWith("+")) {
    sign = s[0];
    s = s.slice(1).trim();
  }
  if (!s) return { ok: false, error: "invalid" };

  // --- numeric parts: decimal degrees, or degrees/minutes/seconds ---
  const parts = s
    .replace(/[°:]/g, " ")
    .replace(/[′'’]/g, " ")
    .replace(/[″"”]/g, " ")
    .split(/\s+/)
    .filter(Boolean);
  if (parts.length < 1 || parts.length > 3) return { ok: false, error: "invalid" };
  const nums = [];
  for (let i = 0; i < parts.length; i++) {
    if (!/^\d+(\.\d+)?$/.test(parts[i])) return { ok: false, error: "invalid" };
    // A fraction is only meaningful on the last (smallest) component.
    if (parts[i].includes(".") && i < parts.length - 1) {
      return { ok: false, error: "invalid" };
    }
    nums.push(parseFloat(parts[i]));
  }
  const deg = nums[0];
  const min = nums.length > 1 ? nums[1] : 0;
  const sec = nums.length > 2 ? nums[2] : 0;
  if (min >= 60 || sec >= 60) return { ok: false, error: "invalid" };
  const magnitude = deg + min / 60 + sec / 3600;
  if (magnitude > limit + 1e-9) return { ok: false, error: "range" };

  // --- resolve the one hemisphere this value lives in ---
  const direction =
    letter || (sign ? (sign === "-" ? negDir : posDir) : fallbackDir || posDir);
  let value = direction === negDir ? -magnitude : magnitude;
  if (value === 0) value = 0; // normalise -0
  return { ok: true, value, direction };
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { parseCoordinate };
}
