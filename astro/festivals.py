"""Nepali festivals and public holidays for the patro calendar.

Two tiers, both computed here — nothing is looked up from another
calendar app, and no other app's wording, descriptions or branding is
used. Only facts (a festival falls on a given tithi, a public holiday
falls on a given date) are taken from the sources below.

SOURCES (what each one established):
- Government of Nepal, Ministry of Home Affairs, "List of Public
  Holidays, 2082 B.S. (2025/26 A.D.)", Nepal Gazette Part 5 notice
  dated 2081/11/15 (summarised in the Pradhan Law P&A Alert of
  6 March 2025 and in edusanjal/collegenp's republications of the
  same notice): the national and scoped public-holiday list used for
  Tier 2 and for every `holiday` flag below, including the Dashain
  holiday block (Ashwin 13-18, 2082) and the Tihar holiday block
  (Kartik 3-7, 2082), and the 2082 BS dates of Ghatasthapana,
  Vijaya Dashami, Bhai Tika, Chhath, Fagu/Terai Holi, Maha
  Shivaratri, Ram Navami, Teej, Indra Jatra, Gai Jatra and the
  fixed-date holidays.
- Nepal Panchanga Nirnayak Bikas Samiti (calendar committee) tika
  announcements as reported in Nepali press for 2082/2083: Dashain
  2082 (Ghatasthapana 22 Sep 2025, Vijaya Dashami 2 Oct 2025,
  Kojagrat Purnima 6 Oct 2025), Tihar 2082 (Kag 19 Oct, Kukur +
  Laxmi Puja 20 Oct, Gai 21 Oct, Govardhan 22 Oct, Bhai Tika
  23 Oct 2025), Dashain 2083 (Ghatasthapana 11 Oct, Vijaya
  Dashami 21 Oct 2026) and Tihar 2083 (Kag 7 Nov, Kukur + Laxmi
  8 Nov, Bhai Tika 11 Nov 2026, MOHA 2083 Tihar holiday
  Kartik 22-26).
- Hamro Patro's own date pages for 2083, verified 2026-11-10:
  Phulpati 17 Oct 2026 (Ashwin 31, 2083), Maha Ashtami
  18 Oct 2026 (Kartik 1, 2083); and the Samiti's Dashain 2082
  dates via The Himalayan Times (16 Sep 2025): Phulpati
  29 Sep 2025, Maha Ashtami 30 Sep 2025, Maha Navami 1 Oct
  2025, Vijaya Dashami 2 Oct 2025.
- Getty Images news captions for Indra Jatra 2025: the festival
  starts from Bhadra Shukla Chaturdashi, procession 6 Sep 2025.
- The classical tithi rules themselves (e.g. Teej = Bhadra Shukla
  Tritiya, Shivaratri = Phalguna Krishna Chaturdashi, Holi =
  Phalguna Purnima with the Terai a day later, Chhath = Kartik
  Shukla Shashthi) are the standard published rules, cross-checked
  against the gazette dates above — every rule below reproduces
  its gazette/press date for 2082 and, where published, for 2083
  (see tests/test_festivals.py).

CONVENTIONS (documented, not hidden):
- Tithi festivals use the sunrise tithi, the same convention as the
  rest of this app (daily_panchang is evaluated at sunrise).
  Exceptions, each fixed by the festival's own classical
  prevailing time and each verified against gazette/press dates:
  Laxmi Puja, Chhath Sandhya Arghya, Kojagrat Purnima, Dhanya
  Purnima / Udhauli / Yomari Punhi and Maha Shivaratri use the
  SUNSET tithi (evening/night rituals — e.g. Shivaratri 2026 is
  15 Feb by sunset Chaturdashi, while its sunrise tithi is still
  Trayodashi; Kojagrat 2025 is 6 Oct by sunset Purnima, while its
  sunrise tithi is still Chaturdashi); Fagu Purnima uses the
  PRADOSH tithi (sunset + 2 hours, the Holika Dahan hour — the
  only rule that gives both Fagu 2025 = 13 Mar and Fagu 2026 =
  2 Mar, where the sunrise tithi is still Chaturdashi on both
  days). Counter-checks that fixed these choices: Buddha Jayanti
  and Janai Purnima must stay on the SUNRISE rule, because on
  their eves the sunset/pradosh tithi is already Purnima
  (11 May 2025 pradosh, 8 Aug 2025 sunset) while the gazette
  dates are the next days (12 May, 9 Aug).
  Phulpati and Maha Ashtami use the MORNING tithi (the tithi
  three hours after sunrise — the first prahar of the day).
  That is the only rule that gives both years' Samiti dates:
  in 2083 Saptami begins 06:09 on 17 Oct and Ashtami 08:43
  on 18 Oct, both inside the morning, so the festivals fall
  those days; in 2082 Saptami begins 14:42 on 28 Sep and
  Ashtami 16:47 on 29 Sep, both in the afternoon, so the
  festivals fall on the next (sunrise) days, 29 and 30 Sep.
  Neither the pure sunrise rule (wrong in 2083: Phulpati
  18 Oct, Ashtami 19 Oct) nor the pure sunset rule (wrong in
  2082: Phulpati 28 Sep, Ashtami 29 Sep) reproduces both
  years. Maha Navami and Vijaya Dashami stay on sunrise:
  their 2083 starts (Navami 11:07 on 19 Oct, Dashami 13:05
  on 20 Oct) are after the morning window, and their 2082
  starts are in the evening, so sunrise gives the Samiti
  dates in both years (Navami 1 Oct 2025 / 20 Oct 2026,
  Dashami 2 Oct 2025 / 21 Oct 2026).
  Gai Tihar is the civil day after Laxmi Puja, Chhath Usha
  Arghya the civil day after Chhath Sandhya Arghya, and Terai
  Holi the civil day after Fagu Purnima, matching the published
  2082/2083 sequences.
- When Maha Ashtami is long enough that the sunrise tithi is
  still Ashtami the day after it (19 Oct 2026, Kartik 2),
  that day is a Dashain Holiday: it sits inside the MOHA
  Dashain holiday block (Kartik 1-6, 2083) and the (7,10)/(7,11)
  Ekadashi/Dwadashi rules alone would leave it unbadged.
- A tithi can occasionally repeat at sunrise (long tithi) or be
  skipped at sunrise (short tithi). When it repeats, only the
  FIRST day in the sequence carries the festival; when it is
  skipped, no day carries it. This is the honest consequence of
  the sunrise convention, not a correction.
- Festival lunar month (the "Ashwin" in "Ashwin Shukla
  Pratipada"): Nepal names festival months Purnimanta-style.
  For a date D, take the lunar cycle (Amavasya to Amavasya)
  containing D. For Shukla days the festival month is the BS
  solar month of the cycle's first civil day; for Krishna days it
  is the BS solar month of the NEXT cycle's first civil day.
  BS month m maps to lunar month (m % 12) + 1 (Baisakh ->
  Vaishakha, ..., Chaitra -> Chaitra). This rule reproduces all
  21 gazette/press anchor dates checked during development
  (Ghatasthapana, Vijaya Dashami, Kag/Kukur/Laxmi/Bhai Tika,
  Janai Purnima, Gai Jatra, Janmashtami, Teej, Indra Jatra,
  Buddha Jayanti, Shivaratri, Fagu Purnima, Ram Navami,
  Basanta Panchami, Dhanya Purnima, Jitiya, in both 2082 and
  2083 where published). The engine's own lunar_month_at naming
  is deliberately NOT used here: it names months from the Sun
  sign at Purnima, which disagrees with the festival tradition
  whenever a Purnima falls before that month's Sankranti.
- Tithi festivals need the BS calendar, so they are available
  only inside the BS table's range (BS 2000-2090, AD
  1943-04-14..2034-04-13). Outside it, only AD-fixed holidays
  are returned. Adhik Maas (leap lunar month) is not
  distinguished, as elsewhere in this app.
- Maghe Sankranti is the day the Sun's noon sign changes to
  Makara (9); other Sankrantis stay astronomical markers only.

DELIBERATELY OMITTED (not guessed):
- Eid al-Fitr, Eid al-Adha, Bhoto Jatra, Muhammad Jayanti, Guru
  Nanak Jayanti, Saruwa Pawani: the 2082 gazette itself lists
  them as "to be determined" by later notice.
- Sonam Lhosar and Gyalpo Lhosar: dates vary by community
  announcement (the gazette's Sonam Lhosar date does not follow
  a stable tithi rule).
- Ghode Jatra: its 2082 gazette date matches two different
  tithi anchors (Chaitra Krishna Chaturdashi at sunrise and
  Amavasya at sunset), so no single rule could be verified.
- Falgunanda Jayanti: no tithi rule verified.
- Saturdays: Nepal's weekly holiday is Saturday, but it is not
  a dated festival/holiday entry; marking every seventh cell
  would drown the festival badges. (Possible follow-up.)
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from .bs_calendar import ad_to_bs
from .ephemeris import sun_moon_longitudes, sunrise_sunset, to_julian_day

# Lunar month indices, 1-based: 1 Chaitra ... 12 Phalguna.
LUNAR_EN = ["Chaitra", "Vaishakha", "Jyeshtha", "Ashadha", "Shravana",
            "Bhadrapada", "Ashwin", "Kartika", "Margashirsha", "Pausha",
            "Magha", "Phalguna"]
LUNAR_NE = ["चैत्र", "वैशाख", "ज्येष्ठ", "आषाढ", "श्रावण",
            "भाद्र", "आश्विन", "कार्तिक", "मार्गशीर्ष", "पौष",
            "माघ", "फाल्गुन"]

# tithi_index: 0..14 Shukla Pratipada..Purnima, 15..29 Krishna
# Pratipada..Amavasya (same numbering as panchang.py).


def _e(key, en, ne, holiday, scope_en=None, scope_ne=None, kind="festival",
       prevailing="sunrise"):
    """One festival/holiday entry. `prevailing` is the time of day
    whose tithi decides the date: "sunrise" (default), "morning"
    (sunrise + 3 hours, the first prahar — Phulpati and Maha
    Ashtami), "sunset" or "pradosh" (sunset + 2 hours). See the
    module docstring."""
    return {"key": key, "name_en": en, "name_ne": ne, "kind": kind,
            "holiday": holiday, "scope_en": scope_en, "scope_ne": scope_ne,
            "prevailing": prevailing}


# (lunar_month_index, tithi_index) -> entry. Sunrise-tithi rules.
_TITHI_RULES = [
    ((2, 14), _e("buddha_jayanti", "Buddha Jayanti", "बुद्ध जयन्ती", True)),
    ((2, 14), _e("ubhauli", "Ubhauli Parwa", "उभौली पर्व", True)),
    ((4, 14), _e("guru_purnima", "Guru Purnima", "गुरु पूर्णिमा", False)),
    ((5, 4), _e("nag_panchami", "Nag Panchami", "नाग पञ्चमी", False)),
    ((5, 14), _e("janai_purnima", "Janai Purnima (Rakshya Bandhan)",
                 "जनै पूर्णिमा (रक्षा बन्धन)", True)),
    ((6, 15), _e("gai_jatra", "Gai Jatra", "गाई जात्रा", True,
                 "Kathmandu Valley and Newar community",
                 "काठमाडौं उपत्यका तथा नेवार समुदाय")),
    ((6, 2), _e("teej", "Haritalika Teej", "हरितालिका तीज", True,
                "Women only", "महिला मात्र")),
    ((6, 4), _e("rishi_panchami", "Rishi Panchami", "ऋषि पञ्चमी", False)),
    ((6, 7), _e("gaura_parwa", "Gaura Parwa", "गौरा पर्व", True,
                "Sudurpashchim and related communities",
                "सुदूरपश्चिम तथा सम्बन्धित समुदाय")),
    ((6, 13), _e("indra_jatra", "Indra Jatra", "इन्द्र जात्रा", True,
                 "Kathmandu Valley only", "काठमाडौं उपत्यका मात्र")),
    ((6, 22), _e("krishna_janmashtami", "Krishna Janmashtami",
                 "श्रीकृष्ण जन्माष्टमी", True)),
    ((7, 0), _e("ghatasthapana", "Ghatasthapana", "घटस्थापना", True)),
    ((7, 6), _e("phulpati", "Phulpati", "फूलपाती", True,
                prevailing="morning")),
    ((7, 7), _e("maha_ashtami", "Maha Ashtami", "महा अष्टमी", True,
                prevailing="morning")),
    ((7, 8), _e("maha_navami", "Maha Navami", "महा नवमी", True)),
    ((7, 9), _e("vijaya_dashami", "Vijaya Dashami", "विजया दशमी", True)),
    ((7, 10), _e("dashain_holiday", "Dashain Holiday", "दशैं बिदा", True,
                 kind="holiday")),
    ((7, 11), _e("dashain_holiday", "Dashain Holiday", "दशैं बिदा", True,
                 kind="holiday")),
    ((7, 14), _e("kojagrat_purnima", "Kojagrat Purnima",
                 "कोजाग्रत पूर्णिमा", False, prevailing="sunset")),
    ((7, 23), _e("jitiya", "Jitiya Parwa", "जितिया पर्व", True,
                 "Women celebrating Jitiya only",
                 "जितिया मनाउने महिला मात्र")),
    ((8, 27), _e("kag_tihar", "Kag Tihar", "काग तिहार", False)),
    ((8, 28), _e("kukur_tihar", "Kukur Tihar", "कुकुर तिहार", True)),
    ((8, 3), _e("chhath_nahay", "Chhath (Nahay Khay)",
                "छठ (नहाय खाय)", False)),
    ((8, 4), _e("chhath_kharna", "Chhath (Kharna)", "छठ (खरना)", False)),
    ((9, 14), _e("dhanya_purnima", "Dhanya Purnima", "धान्य पूर्णिमा",
                 True, prevailing="sunset")),
    ((9, 14), _e("udhauli", "Udhauli Parwa", "उधौली पर्व", True,
                 prevailing="sunset")),
    ((9, 14), _e("yomari_punhi", "Yomari Punhi", "योमरी पुन्हि", True,
                 prevailing="sunset")),
    ((11, 4), _e("basanta_panchami", "Basanta Panchami (Saraswati Puja)",
                 "वसन्त पञ्चमी (सरस्वती पूजा)", True,
                 "Educational institutions only",
                 "शैक्षिक संस्था मात्र")),
    ((12, 28), _e("maha_shivaratri", "Maha Shivaratri",
                  "महा शिवरात्रि", True, prevailing="sunset")),
    ((12, 14), _e("fagu_purnima", "Fagu Purnima (Holi)",
                  "फागु पूर्णिमा (होली)", True,
                  "Hilly and Himalayan districts",
                  "पहाडी तथा हिमाली जिल्ला", prevailing="pradosh")),
    ((1, 8), _e("ram_navami", "Ram Navami", "राम नवमी", True)),
    ((1, 14), _e("hanuman_jayanti", "Hanuman Jayanti",
                 "हनुमान जयन्ती", False)),
]

# (BS month, BS day) -> entry. Stable, gazette-verified fixed dates.
_BS_FIXED = {
    (1, 1): _e("nepali_new_year", "Nepali New Year", "नयाँ वर्ष", True),
    (2, 15): _e("republic_day", "Republic Day", "गणतन्त्र दिवस", True),
    (6, 3): _e("constitution_day", "Constitution Day",
               "संविधान दिवस", True),
    (9, 27): _e("prithvi_jayanti", "Prithvi Jayanti (National Unity Day)",
                 "पृथ्वी जयन्ती (राष्ट्रिय एकता दिवस)", True),
    (9, 15): _e("tamu_lhosar", "Tamu Lhosar", "तमु ल्होसार", True),
    (10, 16): _e("martyrs_day", "Martyrs' Day", "सहिद दिवस", True),
    (11, 7): _e("democracy_day", "National Democracy Day",
                "राष्ट्रिय प्रजातन्त्र दिवस", True),
}

# (AD month, AD day) -> entry. Stable, gazette-verified fixed dates.
_AD_FIXED = {
    (5, 1): _e("labour_day", "International Labour Day",
               "अन्तर्राष्ट्रिय श्रमिक दिवस", True),
    (12, 25): _e("christmas", "Christmas Day", "क्रिसमस", True),
    (3, 8): _e("womens_day", "International Women's Day",
               "अन्तर्राष्ट्रिय महिला दिवस", True,
               "Women employees only", "महिला कर्मचारी मात्र"),
    (12, 3): _e("disability_day", "Intl. Day of Persons with Disabilities",
                 "अपाङ्गता भएका व्यक्तिहरूको अन्तर्राष्ट्रिय दिवस", True),
}

_LAXMI = _e("laxmi_puja", "Laxmi Puja", "लक्ष्मी पूजा", True)
_GAI_TIHAR = _e("gai_tihar", "Gai Tihar", "गाई तिहार", True)
_GOVARDHAN = _e("govardhan_puja", "Govardhan Puja (Mha Puja)",
                "गोवर्धन पूजा (म्ह पूजा)", True)
_BHAI_TIKA = _e("bhai_tika", "Bhai Tika", "भाइटीका", True)
_TIHAR_HOLIDAY = _e("tihar_holiday", "Tihar Holiday", "तिहार बिदा",
                    True, kind="holiday")
_CHHATH_MAIN = _e("chhath_parwa", "Chhath Parwa (Sandhya Arghya)",
                  "छठ पर्व (सन्ध्या अर्घ्य)", True)
_CHHATH_USHA = _e("chhath_usha", "Chhath (Usha Arghya)",
                  "छठ (उषा अर्घ्य)", False)
_TERAI_HOLI = _e("terai_holi", "Terai Holi", "तराई होली", True,
                 "Terai districts", "तराई जिल्ला")
_MAGHE = _e("maghe_sankranti", "Maghe Sankranti", "माघे सङ्क्रान्ति", True)


def _noon_tithi(day: date, tz_name: str) -> int:
    tz = ZoneInfo(tz_name)
    sun, moon = sun_moon_longitudes(
        to_julian_day(datetime.combine(day, time(12, 0), tzinfo=tz)))
    return int(((moon - sun) % 360.0) // 12.0)


def _is_cycle_start(day: date, tz_name: str) -> bool:
    """First civil day of a lunar cycle: noon tithi 0 after a day whose
    noon tithi was 28 or 29 (same test as panchang.lunar_month_at)."""
    return (_noon_tithi(day, tz_name) == 0
            and _noon_tithi(day - timedelta(days=1), tz_name) >= 28)


class _CycleTracker:
    """Walks consecutive days, tracking the current lunar cycle's
    first day (S) and the next cycle's first day (N)."""

    def __init__(self, first_day: date, tz_name: str):
        self.tz = tz_name
        self.s = None
        for k in range(0, 35):
            cand = first_day - timedelta(days=k)
            if _is_cycle_start(cand, tz_name):
                self.s = cand
                break
        if self.s is None:
            raise ValueError("could not bracket the lunar cycle")
        self.n = self._next_start(self.s)

    def _next_start(self, start: date) -> date:
        for k in range(1, 35):
            cand = start + timedelta(days=k)
            if _is_cycle_start(cand, self.tz):
                return cand
        raise ValueError("could not bracket the lunar cycle")

    def festival_month(self, day: date, sunrise_tithi: int) -> int | None:
        """Festival lunar month index (1..12) for `day`, or None when
        the BS table cannot name it (outside BS 2000-2090)."""
        while day >= self.n:
            self.s, self.n = self.n, self._next_start(self.n)
        anchor = self.s if sunrise_tithi < 15 else self.n
        try:
            bs = ad_to_bs(anchor)
        except ValueError:
            return None
        return bs["month"] % 12 + 1


def _day_tithis(day: date, lat: float, lon: float, tz_name: str):
    """(morning tithi, sunset tithi, pradosh tithi) for a civil
    date. Morning is sunrise + 3 hours (the first prahar);
    pradosh is sunset + 2 hours, the classical evening worship
    hour. Any may be None when no sunrise/sunset exists
    (polar fallback)."""
    rise, set_ = sunrise_sunset(day, lat, lon, tz_name)

    def _tithi(moment):
        sun, moon = sun_moon_longitudes(to_julian_day(moment))
        return int(((moon - sun) % 360.0) // 12.0)

    morning = (_tithi(rise + timedelta(hours=3))
               if rise is not None else None)
    if set_ is None:
        return morning, None, None
    return morning, _tithi(set_), _tithi(set_ + timedelta(hours=2))


def _noon_sun_sign(day: date, tz_name: str) -> int:
    tz = ZoneInfo(tz_name)
    sun, _moon = sun_moon_longitudes(
        to_julian_day(datetime.combine(day, time(12, 0), tzinfo=tz)))
    return int(sun // 30.0)


def _public(entry):
    """API shape for one festival/holiday entry: internal fields
    (the prevailing-time flag) are not exposed."""
    return {"key": entry["key"], "name_en": entry["name_en"],
            "name_ne": entry["name_ne"], "kind": entry["kind"],
            "holiday": entry["holiday"],
            "scope_en": entry["scope_en"], "scope_ne": entry["scope_ne"]}


def festivals_for_days(day_infos, lat, lon, tz_name):
    """Festivals/holidays for an ordered list of day dicts.

    Each day dict needs: `date` (a date), `tithi_index` (sunrise
    tithi, as computed by daily_panchang) and `sun_sign` (noon Sun
    sign). `prev_sun_sign` may be supplied per day; otherwise the
    previous day's noon sign is computed once for the first day
    and carried forward. Returns a list of entry lists, aligned
    with `day_infos`. Days must be consecutive and in order, and
    callers should include a few lookback days before the range
    they care about (see attach_festivals) so first-occurrence
    and day-after rules resolve correctly at the range's start.
    """
    out = []
    tracker = None
    prev = None  # previous day's info dict + its emitted entries
    for info in day_infos:
        day = info["date"]
        if tracker is None:
            tracker = _CycleTracker(day, tz_name)
        fest_month = tracker.festival_month(day, info["tithi_index"])
        morning, sunset, pradosh = _day_tithis(day, lat, lon, tz_name)
        prev_sun = info.get("prev_sun_sign")
        if prev_sun is None:
            prev_sun = (_noon_sun_sign(day - timedelta(days=1), tz_name)
                        if prev is None else prev["info"]["sun_sign"])
        entries = []
        seen_keys = set()
        seen_pairs = set()
        if fest_month is not None:
            for (month, tithi), entry in _TITHI_RULES:
                if month != fest_month:
                    continue
                prevailing = entry.get("prevailing", "sunrise")
                active = {"sunrise": info["tithi_index"] == tithi,
                          "morning": morning == tithi,
                          "sunset": sunset == tithi,
                          "pradosh": pradosh == tithi}[prevailing]
                if not active:
                    continue
                # First occurrence wins when a tithi repeats at the
                # prevailing time: skip if the previous day had the
                # SAME (month, tithi) rule. The key alone is not
                # enough — Dashain Holiday is one key carried by
                # two rules (Ekadashi (7,10) and Dwadashi (7,11)),
                # and a key check would wrongly suppress the
                # Dwadashi day every year.
                if prev and (month, tithi) in prev["rule_pairs"]:
                    continue
                entries.append(entry)
                seen_keys.add(entry["key"])
                seen_pairs.add((month, tithi))
            # Dashain Holiday gap day: when Maha Ashtami is long
            # enough that the sunrise tithi is still Ashtami the
            # day after it (19 Oct 2026), that day is inside the
            # MOHA Dashain holiday block but no tithi rule badges
            # it — the Ekadashi/Dwadashi rules only cover the
            # block's tail. Fires once: the next day's previous
            # day is this gap day, not Maha Ashtami.
            if (fest_month == 7 and info["tithi_index"] == 7
                    and prev and "maha_ashtami" in prev["keys"]
                    and "dashain_holiday" not in seen_keys):
                entries.append(_e("dashain_holiday", "Dashain Holiday",
                                  "दशैं बिदा", True, kind="holiday"))
                seen_keys.add("dashain_holiday")
            # Evening rituals whose tithi has no sunrise rule of
            # its own: first day the tithi prevails at sunset, in
            # the Kartik span.
            if fest_month == 8 and sunset == 29:
                if not (prev and prev["sunset"] == 29
                        and prev["fest_month"] == 8):
                    entries.append(_LAXMI)
                    seen_keys.add("laxmi_puja")
            if fest_month == 8 and sunset == 5:
                if not (prev and prev["sunset"] == 5
                        and prev["fest_month"] == 8):
                    entries.append(_CHHATH_MAIN)
                    seen_keys.add("chhath_parwa")
            # Day-after rules, driven by the previous day.
            if prev and "laxmi_puja" in prev["keys"]:
                entries.append(_GAI_TIHAR)
                seen_keys.add("gai_tihar")
            if prev and "fagu_purnima" in prev["keys"]:
                entries.append(_TERAI_HOLI)
                seen_keys.add("terai_holi")
            if prev and "chhath_parwa" in prev["keys"]:
                entries.append(_CHHATH_USHA)
                seen_keys.add("chhath_usha")
            # Govardhan / Bhai Tika / Tihar holiday are sunrise
            # rules, handled like _TITHI_RULES but kept separate
            # for readability (they complete the Tihar sequence).
            for entry, tithi in ((_GOVARDHAN, 0), (_BHAI_TIKA, 1),
                                 (_TIHAR_HOLIDAY, 2)):
                if fest_month != 8 or info["tithi_index"] != tithi:
                    continue
                if prev and entry["key"] in prev["keys"]:
                    continue  # repeat tithi: first day already had it
                entries.append(entry)
                seen_keys.add(entry["key"])
        # Maghe Sankranti: the Sun's noon sign changes to Makara.
        if info["sun_sign"] == 9 and prev_sun != 9:
            entries.append(_MAGHE)
            seen_keys.add("maghe_sankranti")
        # Fixed-date holidays.
        try:
            bs = ad_to_bs(day)
            fixed = _BS_FIXED.get((bs["month"], bs["day"]))
            if fixed is not None:
                entries.append(fixed)
                seen_keys.add(fixed["key"])
        except ValueError:
            pass
        fixed_ad = _AD_FIXED.get((day.month, day.day))
        if fixed_ad is not None:
            entries.append(fixed_ad)
            seen_keys.add(fixed_ad["key"])
        out.append(entries)
        prev = {"info": info, "keys": seen_keys, "sunset": sunset,
                "fest_month": fest_month, "rule_pairs": seen_pairs}
    return [[_public(e) for e in entries] for entries in out]


def attach_festivals(day_dicts, lat, lon, tz_name, lookback=4):
    """Add a `festivals` list to each month-response day dict in
    place (additive only — no existing field is touched). Each
    dict needs `date` (AD ISO string), `tithi_index` and
    `sun_sign`. A few lookback days before the range are walked
    through the same rules so first-occurrence and day-after
    rules resolve correctly on the range's first days.
    """
    from .panchang import daily_panchang

    if not day_dicts:
        return day_dicts
    first = date.fromisoformat(day_dicts[0]["date"])
    infos = []
    for k in range(lookback, 0, -1):
        d = first - timedelta(days=k)
        p = daily_panchang(d, lat, lon, tz_name)
        infos.append({"date": d, "tithi_index": p["tithi_index"],
                      "sun_sign": _noon_sun_sign(d, tz_name)})
    for d in day_dicts:
        infos.append({"date": date.fromisoformat(d["date"]),
                      "tithi_index": d["tithi_index"],
                      "sun_sign": d["sun_sign"]})
    results = festivals_for_days(infos, lat, lon, tz_name)
    for d, festivals in zip(day_dicts, results[lookback:]):
        d["festivals"] = festivals
    return day_dicts


def festivals_for_day(day: date, lat: float, lon: float, tz_name: str,
                      sunrise_tithi: int | None = None,
                      sun_sign: int | None = None):
    """Festivals/holidays for a single date (day-detail panel).

    Builds a five-day window so first-occurrence and day-after
    rules resolve exactly as they do inside a month grid.
    """
    from .panchang import daily_panchang

    infos = []
    for k in range(4, -1, -1):
        d = day - timedelta(days=k)
        p = daily_panchang(d, lat, lon, tz_name)
        infos.append({"date": d, "tithi_index": p["tithi_index"],
                      "sun_sign": _noon_sun_sign(d, tz_name)})
    if sunrise_tithi is not None:
        infos[-1]["tithi_index"] = sunrise_tithi
    if sun_sign is not None:
        infos[-1]["sun_sign"] = sun_sign
    return festivals_for_days(infos, lat, lon, tz_name)[-1]
