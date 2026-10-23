"""Numerology — Moolank (birth/root number, from the day of birth) and
Bhagyank (destiny/life-path number, from the full birth date), the pair
every premium Indian report prints. Each root number carries its ruling
planet and a short bilingual reading.
"""
from __future__ import annotations

from datetime import date

from .names import PLANET_NE

RULERS = {
    1: "Sun", 2: "Moon", 3: "Jupiter", 4: "Rahu", 5: "Mercury",
    6: "Venus", 7: "Ketu", 8: "Saturn", 9: "Mars",
}
_TRAITS = {
    1: ("Independent, self-driven and born to lead; success grows when you take initiative without waiting for permission.",
        "स्वतन्त्र, आत्मप्रेरित र नेतृत्वका लागि जन्मेका; अनुमति नपर्खी आफैँ पहल गर्दा सफलता बढ्छ।"),
    2: ("Sensitive, intuitive and diplomatic; partnerships and patience bring your best results.",
        "संवेदनशील, अन्तर्ज्ञानयुक्त र कूटनीतिक; साझेदारी र धैर्यले उत्कृष्ट फल दिन्छ।"),
    3: ("Expressive, optimistic and knowledge-loving; teaching, counsel and creative work suit you.",
        "अभिव्यक्तिशील, आशावादी र ज्ञानप्रेमी; शिक्षण, परामर्श र सिर्जनात्मक काम उपयुक्त हुन्छ।"),
    4: ("Practical, unconventional and sudden in change; discipline turns surprises into gains.",
        "व्यावहारिक, अपारम्परिक र परिवर्तनमा आकस्मिक; अनुशासनले आश्चर्यलाई लाभमा बदल्छ।"),
    5: ("Quick, versatile and freedom-loving; trade, communication and travel favour you.",
        "छिटो, बहुमुखी र स्वतन्त्रताप्रेमी; व्यापार, सञ्चार र यात्राले साथ दिन्छ।"),
    6: ("Warm, responsible and comfort-loving; family, art and service bring fulfilment.",
        "न्यानो, जिम्मेवार र सुखप्रेमी; परिवार, कला र सेवाले पूर्णता दिन्छ।"),
    7: ("Analytical, introspective and spiritually inclined; research and solitude sharpen you.",
        "विश्लेषणात्मक, आत्मचिन्तनशील र आध्यात्मिक झुकावयुक्त; अनुसन्धान र एकान्तले तपाईंलाई तीखो बनाउँछ।"),
    8: ("Disciplined, ambitious and karma-tested; slow, steady effort builds lasting authority.",
        "अनुशासित, महत्त्वाकाङ्क्षी र कर्मले परीक्षित; ढिलो तर स्थिर मेहनतले दीर्घकालीन अधिकार बनाउँछ।"),
    9: ("Courageous, compassionate and energetic; you finish what others abandon.",
        "साहसी, दयालु र ऊर्जावान्; अरूले छाडेको काम तपाईंले पूरा गर्नुहुन्छ।"),
}


def _root(n: int) -> int:
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n


def _entry(value: int) -> dict:
    ruler = RULERS[value]
    en, ne = _TRAITS[value]
    return {
        "value": value,
        "ruler": ruler,
        "ruler_ne": PLANET_NE[ruler],
        "trait": {"en": en, "ne": ne},
    }


def numerology(dob: date) -> dict:
    moolank = _root(dob.day)
    total = sum(int(d) for d in dob.strftime("%Y%m%d"))
    bhagyank = _root(total)
    return {"moolank": _entry(moolank), "bhagyank": _entry(bhagyank)}
