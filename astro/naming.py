"""Nakshatra name letters (naam akshar) — the classical syllable table.

Each nakshatra pada carries a prescribed starting syllable for the
child's name; a Nepali janma patri prints it prominently. The table is
the standard published one (108 syllables), in transliteration and
Devanagari.
"""
from __future__ import annotations

# (transliteration, Devanagari) per pada 1..4, per nakshatra 0..26
SYLLABLES = [
    [("Chu", "चु"), ("Che", "चे"), ("Cho", "चो"), ("La", "ला")],          # Ashwini
    [("Li", "ली"), ("Lu", "लू"), ("Le", "ले"), ("Lo", "लो")],          # Bharani
    [("A", "अ"), ("E", "ई"), ("U", "उ"), ("Ae", "ए")],                 # Krittika
    [("O", "ओ"), ("Va", "वा"), ("Vi", "वी"), ("Vu", "वू")],            # Rohini
    [("Ve", "वे"), ("Vo", "वो"), ("Ka", "का"), ("Khi", "खी")],         # Mrigashira
    [("Ku", "कु"), ("Gha", "घ"), ("Jha", "झ"), ("Chha", "छ")],         # Ardra
    [("Ke", "के"), ("Ko", "को"), ("Ha", "हा"), ("Hi", "ही")],          # Punarvasu
    [("Hu", "हु"), ("He", "हे"), ("Ho", "हो"), ("Da", "ड")],           # Pushya
    [("Di", "डी"), ("Du", "डू"), ("De", "दे"), ("Do", "डो")],          # Ashlesha
    [("Ma", "मा"), ("Mi", "मी"), ("Mu", "मू"), ("Me", "मे")],          # Magha
    [("Mo", "मो"), ("Ta", "टा"), ("Ti", "टी"), ("Tu", "टू")],          # Purva Phalguni
    [("Te", "ते"), ("To", "टो"), ("Pa", "पा"), ("Pi", "पी")],          # Uttara Phalguni
    [("Pu", "पू"), ("Sha", "ष"), ("Na", "ण"), ("Tha", "ठ")],           # Hasta
    [("Pe", "पे"), ("Po", "पो"), ("Ra", "रा"), ("Ri", "री")],          # Chitra
    [("Ru", "रू"), ("Re", "रे"), ("Ro", "रो"), ("Ta", "ता")],          # Swati
    [("Ti", "ती"), ("Tu", "तू"), ("Te", "ते"), ("To", "तो")],          # Vishakha
    [("Na", "ना"), ("Ni", "नी"), ("Nu", "नू"), ("Ne", "ने")],          # Anuradha
    [("No", "नो"), ("Ya", "या"), ("Yi", "यी"), ("Yu", "यू")],          # Jyeshtha
    [("Ye", "ये"), ("Yo", "यो"), ("Bha", "भा"), ("Bhi", "भी")],        # Mula
    [("Bhu", "भू"), ("Dha", "धा"), ("Pha", "फा"), ("Dha", "ढा")],      # Purva Ashadha
    [("Bhe", "भे"), ("Bho", "भो"), ("Ja", "जा"), ("Ji", "जी")],        # Uttara Ashadha
    [("Khi", "खी"), ("Khu", "खू"), ("Khe", "खे"), ("Kho", "खो")],      # Shravana
    [("Ga", "गा"), ("Gi", "गी"), ("Gu", "गू"), ("Ge", "गे")],          # Dhanishta
    [("Go", "गो"), ("Sa", "सा"), ("Si", "सी"), ("Su", "सू")],          # Shatabhisha
    [("Se", "से"), ("So", "सो"), ("Da", "दा"), ("Di", "दी")],          # Purva Bhadrapada
    [("Du", "दू"), ("Tha", "थ"), ("Jha", "झ"), ("Na", "ञ")],          # Uttara Bhadrapada
    [("De", "दे"), ("Do", "दो"), ("Cha", "चा"), ("Chi", "ची")],        # Revati
]


def name_letters(moon_nakshatra: int, moon_pada: int) -> dict:
    options = [
        {"pada": i + 1, "en": en, "ne": ne}
        for i, (en, ne) in enumerate(SYLLABLES[moon_nakshatra])
    ]
    chosen = options[moon_pada - 1]
    return {
        "nakshatra_index": moon_nakshatra,
        "pada": moon_pada,
        "syllable_en": chosen["en"],
        "syllable_ne": chosen["ne"],
        "options": options,
    }
