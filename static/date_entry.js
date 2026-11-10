"use strict";
/* BS/AD date entry with validation — one widget reused by the birth form
   (#f-dob) and both matching forms (#m1-dob, #m2-dob).

   AD mode keeps the native date input (the AD calendar picker). BS mode
   offers year (2000–2090) / month (Nepali names) / day selects, with the
   day list limited to that BS month's real length from /api/bs-month-length
   (single source of truth: the backend lookup table, never a copy here).
   The submitted payload still sends an AD `dob` — BS is entry/display only.

   Pure helpers are exported for Node tests (UMD guard); the widget itself
   runs only in the browser and reuses app.js globals (LANG, t, locNum)
   because this file loads after static/app.js. */
function isLeapYear(y) { return (y % 4 === 0 && y % 100 !== 0) || y % 400 === 0; }
function daysInAdMonth(y, m) {
  return [31, isLeapYear(y) ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1];
}
function parseAd(iso) {
  const mt = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso || "");
  if (!mt) return null;
  const y = +mt[1], m = +mt[2], d = +mt[3];
  if (m < 1 || m > 12 || d < 1 || d > daysInAdMonth(y, m)) return null;
  return { y, m, d };
}
function isValidTime(s) {
  const mt = /^(\d{2}):(\d{2})$/.exec(s || "");
  return !!mt && +mt[1] <= 23 && +mt[2] <= 59;
}
function todayIso() {
  const n = new Date();
  return `${n.getFullYear()}-${String(n.getMonth() + 1).padStart(2, "0")}-${String(n.getDate()).padStart(2, "0")}`;
}
/* Date+time validation. Returns an i18n error key, or null when valid.
   `today` is injectable so tests can pin it. */
function validateDateTime(adIso, timeStr, today) {
  if (!adIso) return "err_missing_date";
  if (!parseAd(adIso)) return "err_bad_date";
  if (adIso > (today || todayIso())) return "err_future_date";
  if (!timeStr) return "err_fields";
  if (!isValidTime(timeStr)) return "err_bad_time";
  return null;
}
function isValidBsDate(y, m, d, monthLength) {
  return Number.isInteger(y) && y >= 2000 && y <= 2090 &&
    Number.isInteger(m) && m >= 1 && m <= 12 &&
    Number.isInteger(d) && d >= 1 && d <= monthLength;
}

const DE_BS_MONTHS_EN = ["Baisakh", "Jestha", "Ashadh", "Shrawan", "Bhadra", "Ashwin",
  "Kartik", "Mangsir", "Poush", "Magh", "Falgun", "Chaitra"];
const DE_BS_MONTHS_NE = ["बैशाख", "जेठ", "असार", "श्रावण", "भदौ", "आश्विन",
  "कार्तिक", "मंसिर", "पौष", "माघ", "फाल्गुन", "चैत्र"];
const BS_MIN_YEAR = 2000, BS_MAX_YEAR = 2090;

if (typeof module !== "undefined" && module.exports) {
  module.exports = { isLeapYear, daysInAdMonth, parseAd, isValidTime, todayIso,
    validateDateTime, isValidBsDate, DE_BS_MONTHS_EN, DE_BS_MONTHS_NE, BS_MIN_YEAR, BS_MAX_YEAR };
}

if (typeof document !== "undefined") {
  const T = (k) => (typeof t === "function" ? t(k) : k);
  const LN = (n) => (typeof locNum === "function" ? locNum(n) : String(n));
  const isNe = () => (typeof LANG !== "undefined" && LANG === "ne");
  const $ = (id) => document.getElementById(id);
  const PREFIXES = ["f", "m1", "m2"];
  const S = {}; // prefix -> widget state

  function els(p) {
    return {
      ad: $(`${p}-dob`),
      fields: $(`${p}-bs-fields`),
      year: $(`${p}-bs-year`),
      month: $(`${p}-bs-month`),
      day: $(`${p}-bs-day`),
      equiv: $(`${p}-date-equiv`),
      err: $(`${p}-date-error`),
      modeBtns: document.querySelectorAll(`[data-date-prefix="${p}"][data-date-mode]`),
    };
  }
  function bsParts(p) {
    const e = els(p);
    const y = parseInt(e.year.value, 10), m = parseInt(e.month.value, 10), d = parseInt(e.day.value, 10);
    return { y: Number.isNaN(y) ? null : y, m: Number.isNaN(m) ? null : m, d: Number.isNaN(d) ? null : d };
  }
  function buildOptions(sel, items, placeholder) {
    const cur = sel.value;
    sel.innerHTML = "";
    const ph = document.createElement("option");
    ph.value = ""; ph.textContent = placeholder; sel.appendChild(ph);
    for (const [value, text] of items) {
      const o = document.createElement("option");
      o.value = value; o.textContent = text; sel.appendChild(o);
    }
    if ([...sel.options].some((o) => o.value === cur)) sel.value = cur;
  }
  function buildYearOptions(p) {
    const items = [];
    for (let y = BS_MIN_YEAR; y <= BS_MAX_YEAR; y++) items.push([y, LN(y)]);
    buildOptions(els(p).year, items, T("date_year_ph"));
  }
  function buildMonthOptions(p) {
    const names = isNe() ? DE_BS_MONTHS_NE : DE_BS_MONTHS_EN;
    buildOptions(els(p).month, names.map((n, i) => [i + 1, n]), T("date_month_ph"));
  }
  function buildDayOptions(p, len) {
    const items = [];
    for (let d = 1; d <= len; d++) items.push([d, LN(d)]);
    buildOptions(els(p).day, items, T("date_day_ph"));
  }
  function showError(p, key) {
    const e = els(p).err;
    if (!e) return;
    e.textContent = T(key); e.hidden = false;
  }
  function clearError(p) {
    const e = els(p).err;
    if (e) { e.textContent = ""; e.hidden = true; }
  }
  function setEquiv(p, text) {
    const e = els(p).equiv;
    if (!e) return;
    if (text) { e.textContent = text; e.hidden = false; }
    else { e.textContent = ""; e.hidden = true; }
  }
  async function fetchMonthLength(p, y, m) {
    const st = S[p];
    const key = `${y}-${m}`;
    if (st.lenCache[key]) return st.lenCache[key];
    const res = await fetch(`/api/bs-month-length?bs_year=${y}&bs_month=${m}`);
    if (!res.ok) throw new Error("bad");
    const body = await res.json();
    st.lenCache[key] = body.month_length;
    return body.month_length;
  }
  async function refreshDayLimit(p) {
    const st = S[p];
    const { y, m, d } = bsParts(p);
    if (y == null || m == null) return;
    let len;
    try { len = await fetchMonthLength(p, y, m); } catch { return; }
    const prevDay = d;
    buildDayOptions(p, len);
    if (prevDay != null && prevDay > len) {
      // Day no longer exists in this month: leave the day unpicked and
      // show the error immediately instead of silently changing the date.
      els(p).day.value = "";
      st.lastAd = "";
      showError(p, "err_bad_date");
      setEquiv(p, null);
    }
  }
  async function refreshEquiv(p) {
    const st = S[p];
    const seq = ++st.seq;
    if (st.mode === "ad") {
      const iso = els(p).ad.value;
      const parsed = parseAd(iso);
      if (!parsed) { setEquiv(p, null); return; }
      try {
        const res = await fetch(`/api/bs?date=${iso}`);
        if (!res.ok) throw new Error("bad");
        const body = await res.json();
        if (seq !== st.seq) return;
        st.lastBs = body;
        setEquiv(p, `${T("equiv_bs")}: ${isNe() ? body.formatted_ne : body.formatted_en}`);
      } catch { if (seq === st.seq) setEquiv(p, null); }
    } else {
      const { y, m, d } = bsParts(p);
      if (y == null || m == null || d == null) { setEquiv(p, null); return; }
      try {
        const res = await fetch(`/api/bs?bs=${y}-${String(m).padStart(2, "0")}-${String(d).padStart(2, "0")}`);
        if (!res.ok) throw new Error("bad");
        const body = await res.json();
        if (seq !== st.seq) return;
        st.lastAd = body.ad; st.lastBs = body;
        setEquiv(p, `${T("equiv_ad")}: ${body.ad}`);
      } catch { if (seq === st.seq) { st.lastAd = ""; setEquiv(p, null); } }
    }
  }
  function validate(p) {
    const st = S[p];
    if (st.mode === "ad") {
      return validateDateTime(els(p).ad.value, "00:00", todayIso());
    }
    const { y, m, d } = bsParts(p);
    if (y == null || m == null || d == null) return "err_missing_date";
    const len = st.lenCache[`${y}-${m}`];
    if (len != null && !isValidBsDate(y, m, d, len)) return "err_bad_date";
    if (st.lastAd && st.lastAd > todayIso()) return "err_future_date";
    if (st.lastAd && !parseAd(st.lastAd)) return "err_bad_date";
    return null;
  }
  function getAdDate(p) {
    const st = S[p];
    if (!st) return $(`${p}-dob`) ? $(`${p}-dob`).value : "";
    if (st.mode === "ad") return els(p).ad.value || "";
    const { y, m, d } = bsParts(p);
    if (y == null || m == null || d == null) return "";
    return st.lastAdFor === `${y}-${m}-${d}` ? st.lastAd : "";
  }
  async function resolveAdDate(p) {
    const st = S[p];
    if (!st || st.mode === "ad") return getAdDate(p);
    const { y, m, d } = bsParts(p);
    if (y == null || m == null || d == null) return "";
    const key = `${y}-${m}-${d}`;
    if (st.lastAdFor === key) return st.lastAd;
    try {
      const res = await fetch(`/api/bs?bs=${y}-${String(m).padStart(2, "0")}-${String(d).padStart(2, "0")}`);
      if (!res.ok) return "";
      const body = await res.json();
      st.lastAd = body.ad; st.lastAdFor = key; st.lastBs = body;
      return body.ad;
    } catch { return ""; }
  }
  function setMode(p, mode) {
    const st = S[p];
    if (!st) return;
    st.mode = mode;
    const e = els(p);
    e.modeBtns.forEach((b) => b.classList.toggle("is-active", b.getAttribute("data-date-mode") === mode));
    e.ad.hidden = mode !== "ad";
    e.fields.hidden = mode !== "bs";
    if (mode === "bs" && e.ad.value && parseAd(e.ad.value)) {
      // Preselect the BS equivalent of the current AD date.
      fetch(`/api/bs?date=${e.ad.value}`).then((r) => (r.ok ? r.json() : null)).then((body) => {
        if (!body) return;
        e.year.value = body.year; buildMonthOptions(p); e.month.value = body.month;
        fetchMonthLength(p, body.year, body.month).then((len) => {
          buildDayOptions(p, len); e.day.value = body.day;
          st.lastAd = e.ad.value; st.lastAdFor = `${body.year}-${body.month}-${body.day}`; st.lastBs = body;
        }).catch(() => {});
      }).catch(() => {});
    }
    if (mode === "ad" && st.lastAd) e.ad.value = st.lastAd;
    clearError(p);
    refreshEquiv(p);
  }
  async function setAdDate(p, iso) {
    const st = S[p];
    if (!st) {
      const el = $(`${p}-dob`);
      if (el) el.value = iso || "";
      return;
    }
    els(p).ad.value = iso || "";
    st.lastAd = ""; st.lastAdFor = ""; st.lastBs = null;
    clearError(p);
    if (!parseAd(iso)) { buildDayOptions(p, 32); els(p).year.value = ""; els(p).month.value = ""; els(p).day.value = ""; setEquiv(p, null); return; }
    try {
      const res = await fetch(`/api/bs?date=${iso}`);
      if (!res.ok) throw new Error("bad");
      const body = await res.json();
      els(p).year.value = body.year; buildMonthOptions(p); els(p).month.value = body.month;
      const len = await fetchMonthLength(p, body.year, body.month);
      buildDayOptions(p, len); els(p).day.value = body.day;
      st.lastAd = iso; st.lastAdFor = `${body.year}-${body.month}-${body.day}`; st.lastBs = body;
      setEquiv(p, `${T("equiv_bs")}: ${isNe() ? body.formatted_ne : body.formatted_en}`);
    } catch { setEquiv(p, null); }
  }
  function refreshLanguage() {
    for (const p of PREFIXES) {
      if (!S[p]) continue;
      buildYearOptions(p); buildMonthOptions(p);
      const { d } = bsParts(p);
      const e = els(p);
      const len = Math.max(32, 1);
      buildDayOptions(p, e.day.options.length > 1 ? e.day.options.length - 1 : len);
      if (d != null) e.day.value = d;
      const st = S[p];
      if (st.lastBs) {
        setEquiv(p, st.mode === "ad"
          ? `${T("equiv_bs")}: ${isNe() ? st.lastBs.formatted_ne : st.lastBs.formatted_en}`
          : `${T("equiv_ad")}: ${st.lastAd}`);
      }
    }
  }
  function initOne(p) {
    const e = els(p);
    if (!e.ad || !e.year || !e.month || !e.day) return;
    S[p] = { mode: "ad", lenCache: {}, seq: 0, lastAd: "", lastAdFor: "", lastBs: null };
    buildYearOptions(p); buildMonthOptions(p); buildDayOptions(p, 32);
    e.modeBtns.forEach((b) => b.addEventListener("click", () => setMode(p, b.getAttribute("data-date-mode"))));
    e.ad.addEventListener("change", () => { clearError(p); refreshEquiv(p); });
    e.year.addEventListener("change", () => { clearError(p); refreshDayLimit(p).then(() => refreshEquiv(p)); });
    e.month.addEventListener("change", () => { clearError(p); refreshDayLimit(p).then(() => refreshEquiv(p)); });
    e.day.addEventListener("change", () => {
      const k = validate(p);
      if (k) showError(p, k); else clearError(p);
      refreshEquiv(p);
    });
    // Sync the BS selects with any AD value already present (share links,
    // restored charts) so switching to BS shows the same date.
    if (e.ad.value && parseAd(e.ad.value)) setAdDate(p, e.ad.value);
  }
  function initDateEntries() {
    for (const p of PREFIXES) initOne(p);
  }
  initDateEntries();

  window.VedicDateEntry = { initDateEntries, getMode: (p) => (S[p] ? S[p].mode : "ad"),
    setMode, getAdDate, resolveAdDate, validate, showError, clearError, setAdDate,
    refreshLanguage, isValidTime, validateDateTime, parseAd };
}
