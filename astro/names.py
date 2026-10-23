"""Shared constants for the Vedic astrology engine.

All name tables are bilingual (English + Nepali in Devanagari). Astronomical
and classical-rule constants (sign lords, exaltations, combustion orbs,
natural friendships) follow Brihat Parashara Hora Shastra conventions.
"""

# ---------------------------------------------------------------------------
# Signs (Rashi) 0..11
# ---------------------------------------------------------------------------
SIGNS_EN = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]
SIGNS_NE = [
    "मेष", "वृष", "मिथुन", "कर्कट", "सिंह", "कन्या",
    "तुला", "वृश्चिक", "धनु", "मकर", "कुम्भ", "मीन",
]
# Ruling planet of each sign (index-aligned with SIGNS_EN)
SIGN_LORDS = [
    "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
    "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter",
]

# ---------------------------------------------------------------------------
# Planets (Grahas)
# ---------------------------------------------------------------------------
PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
PLANETS_7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
PLANET_EN = {p: p for p in PLANETS}
PLANET_NE = {
    "Sun": "सूर्य", "Moon": "चन्द्र", "Mars": "मङ्गल", "Mercury": "बुध",
    "Jupiter": "बृहस्पति", "Venus": "शुक्र", "Saturn": "शनि",
    "Rahu": "राहु", "Ketu": "केतु",
}
PLANET_ABBR = {
    "Sun": "Su", "Moon": "Mo", "Mars": "Ma", "Mercury": "Me",
    "Jupiter": "Ju", "Venus": "Ve", "Saturn": "Sa", "Rahu": "Ra", "Ketu": "Ke",
}

# ---------------------------------------------------------------------------
# Nakshatras 0..26, each 13 deg 20 min
# ---------------------------------------------------------------------------
NAKSHATRAS_EN = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha",
    "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana",
    "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]
NAKSHATRAS_NE = [
    "अश्विनी", "भरणी", "कृत्तिका", "रोहिणी", "मृगशिरा", "आर्द्रा",
    "पुनर्वसु", "पुष्य", "अश्लेषा", "मघा", "पूर्व फाल्गुनी",
    "उत्तर फाल्गुनी", "हस्त", "चित्रा", "स्वाती", "विशाखा", "अनुराधा",
    "ज्येष्ठा", "मूल", "पूर्वाषाढा", "उत्तराषाढा", "श्रवण",
    "धनिष्ठा", "शतभिषा", "पूर्व भाद्रपदा", "उत्तर भाद्रपदा", "रेवती",
]
# Vimshottari lord cycle, starting from Ketu (Ashwini's lord)
DASHA_SEQUENCE = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
DASHA_YEARS = {
    "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
    "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17,
}
# Nakshatra i is ruled by DASHA_SEQUENCE[i % 9]
NAKSHATRA_LORDS = [DASHA_SEQUENCE[i % 9] for i in range(27)]

NAKSHATRA_SPAN = 360.0 / 27.0  # 13.333... degrees

# ---------------------------------------------------------------------------
# Dignity: exaltation sign (and peak degree within the sign), own signs,
# debilitation sign (= opposite of exaltation).
# ---------------------------------------------------------------------------
EXALTATION = {  # planet: (sign index, peak degree in sign)
    "Sun": (0, 10), "Moon": (1, 3), "Mars": (9, 28), "Mercury": (5, 15),
    "Jupiter": (3, 5), "Venus": (11, 27), "Saturn": (6, 20),
}
OWN_SIGNS = {
    "Sun": [4], "Moon": [3], "Mars": [0, 7], "Mercury": [2, 5],
    "Jupiter": [8, 11], "Venus": [1, 6], "Saturn": [9, 10],
}
# Combustion orbs in degrees (planet combust when within this of the Sun)
COMBUSTION_ORB = {
    "Moon": 12, "Mars": 17, "Mercury": 14, "Jupiter": 11,
    "Venus": 10, "Saturn": 15,
}
# Moolatrikona: planet -> (sign index, start degree-in-sign, end degree).
# (The Moon's first 3 degrees of Taurus are its exaltation zone; the rest
# of Taurus is moolatrikona.)
MOOLATRIKONA = {
    "Sun": (4, 0.0, 20.0), "Moon": (1, 3.0, 30.0), "Mars": (0, 0.0, 12.0),
    "Mercury": (5, 15.0, 20.0), "Jupiter": (8, 0.0, 10.0),
    "Venus": (6, 0.0, 15.0), "Saturn": (10, 0.0, 20.0),
}

# Natural (naisargika) friendships: planet -> (friends, neutral, enemies)
FRIENDSHIP = {
    "Sun": ({"Moon", "Mars", "Jupiter"}, {"Mercury"}, {"Venus", "Saturn"}),
    "Moon": ({"Sun", "Mercury"}, {"Mars", "Jupiter", "Venus", "Saturn"}, set()),
    "Mars": ({"Sun", "Moon", "Jupiter"}, {"Venus", "Saturn"}, {"Mercury"}),
    "Mercury": ({"Sun", "Venus"}, {"Mars", "Jupiter", "Saturn"}, {"Moon"}),
    "Jupiter": ({"Sun", "Moon", "Mars"}, {"Saturn"}, {"Mercury", "Venus"}),
    "Venus": ({"Mercury", "Saturn"}, {"Mars", "Jupiter"}, {"Sun", "Moon"}),
    "Saturn": ({"Mercury", "Venus"}, {"Jupiter"}, {"Sun", "Moon", "Mars"}),
}
NATURAL_BENEFICS = {"Jupiter", "Venus", "Mercury", "Moon"}
NATURAL_MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}

# ---------------------------------------------------------------------------
# Panchang vocabularies
# ---------------------------------------------------------------------------
TITHIS_EN = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi",
    "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi",
    "Trayodashi", "Chaturdashi", "Purnima",
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi",
    "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi",
    "Trayodashi", "Chaturdashi", "Amavasya",
]
TITHIS_NE = [
    "प्रतिपदा", "द्वितीया", "तृतीया", "चतुर्थी", "पञ्चमी", "षष्ठी",
    "सप्तमी", "अष्टमी", "नवमी", "दशमी", "एकादशी", "द्वादशी",
    "त्रयोदशी", "चतुर्दशी", "पूर्णिमा",
    "प्रतिपदा", "द्वितीया", "तृतीया", "चतुर्थी", "पञ्चमी", "षष्ठी",
    "सप्तमी", "अष्टमी", "नवमी", "दशमी", "एकादशी", "द्वादशी",
    "त्रयोदशी", "चतुर्दशी", "औंसी",
]
YOGAS_EN = [
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda",
    "Sukarma", "Dhriti", "Shoola", "Ganda", "Vriddhi", "Dhruva", "Vyaghata",
    "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyan", "Parigha", "Shiva",
    "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti",
]
YOGAS_NE = [
    "विष्कम्भ", "प्रीति", "आयुष्मान्", "सौभाग्य", "शोभन", "अतिगण्ड",
    "सुकर्मा", "धृति", "शूल", "गण्ड", "वृद्धि", "ध्रुव", "व्याघात",
    "हर्षण", "वज्र", "सिद्धि", "व्यतीपात", "वरीयान्", "परिघ", "शिव",
    "सिद्ध", "साध्य", "शुभ", "शुक्ल", "ब्रह्मा", "इन्द्र", "वैधृति",
]
# Karana: 7 movable karanas cycle; 4 fixed ones occur at set half-tithis
KARANAS_MOVABLE_EN = ["Bava", "Balava", "Kaulava", "Taitila", "Garaja", "Vanija", "Vishti"]
KARANAS_MOVABLE_NE = ["बव", "बालव", "कौलव", "तैतिल", "गरज", "वणिज", "विष्टि"]
KARANAS_FIXED_EN = {"Kimstughna": "Kimstughna", "Shakuni": "Shakuni", "Chatushpada": "Chatushpada", "Naga": "Naga"}
KARANAS_FIXED_NE = {"Kimstughna": "किंस्तुघ्न", "Shakuni": "शकुनि", "Chatushpada": "चतुष्पाद", "Naga": "नाग"}
# Weekday names indexed by Python date.weekday() (Mon=0)
WEEKDAYS_EN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
WEEKDAYS_NE = ["सोमबार", "मङ्गलबार", "बुधबार", "बिहीबार", "शुक्रबार", "शनिबार", "आइतबार"]
VAARA_LORDS = ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Sun"]  # by weekday Mon..Sun

HOUSE_NAMES_EN = [
    "1st", "2nd", "3rd", "4th", "5th", "6th",
    "7th", "8th", "9th", "10th", "11th", "12th",
]
HOUSE_NAMES_NE = [
    "पहिलो", "दोस्रो", "तेसो", "चौथो", "पाँचौँ", "छैटौँ",
    "सातौँ", "आठौँ", "नवौँ", "दशौँ", "एघारौँ", "बाह्रौँ",
]
HOUSE_THEMES_EN = {
    1: "self and personality", 2: "wealth and family", 3: "courage and siblings",
    4: "home and mother", 5: "children and creativity", 6: "health and competition",
    7: "marriage and partnerships", 8: "longevity and transformation",
    9: "fortune and dharma", 10: "career and status", 11: "gains and networks",
    12: "foreign lands and liberation",
}
HOUSE_THEMES_NE = {
    1: "आत्म र व्यक्तित्व", 2: "धन र परिवार", 3: "साहस र दाजुभाइ-दिदीबहिनी",
    4: "घर र आमा", 5: "सन्तान र सृजनशीलता", 6: "स्वास्थ्य र प्रतिस्पर्धा",
    7: "विवाह र साझेदारी", 8: "आयु र रूपान्तरण",
    9: "भाग्य र धर्म", 10: "पेशा र प्रतिष्ठा", 11: "लाभ र सम्पर्क सञ्जाल",
    12: "विदेश र मुक्ति",
}
