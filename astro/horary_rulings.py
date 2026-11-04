"""Full traditional horary rulings for the Life Questions library.

Each entry adds a ``ruling`` object to its question's API payload
(via :func:`astro.life_questions.to_public`). The ruling states HOW to
read a chart for the question — the KP method, what counts as a
favourable indication, what counts as an unfavourable one, and any
timing rule — in English and Nepali. It never answers a question on
its own: a ruling is a reading guide, and every entry keeps the
probability framing and disclaimers of the library.

SOURCES — documented per question, never mixed up:

- ``template:<Drive file id>`` — the ruling was read from the legacy
  Kundli Chakra "Subjects" template of that id (downloaded from the
  user's Drive folder and stripped of RTF markup). Where a template
  covers only part of a question, the source is
  ``template:<id>+classical`` and the classical part is the standard
  KP horary method (dasa-antardasa significators, star/sub lords,
  12th-from-prime negation), not a template quote.
- ``classical`` — no template for this exact question was read; the
  ruling follows the standard published KP horary method using the
  question's existing prime/supporting/negating houses (those houses
  themselves were already in the library; no new house numbers were
  invented here).
- ``pending`` — reserved for a question with no usable source; none
  of the 26 questions is pending at present, but ``to_public`` falls
  back to it if a ruling is ever missing, so the API never invents
  one silently.

Template ids actually read for this step (8 files):

- 1BA-FSO_O264rPw90nNVckSkEqtGRqv6i — "Timing of marriage"
- 1KSwPLdi3KL9hyea2FVEtRJpvWfkV_SBw — "Education"
- 1c2YlB2zZF_x3pCUhspvtVnYlIvinyeLu — "Business or Service"
- 1BkKEQ7Dhd9EEnA4XLHaxrZRYABACtVBE — "Purchase of Property"
- 1r2j4q95exlfFLHYhLulaiYqLGYbpiNG_ — "Sale-Purchase of Vehicle"
- 1F4-A-aowvw9ixguaqjtsvNvV1HTytjtj — "General sickness"
- 1Tr76-M1aCBaExg7AJDjppirinfMBBCS_ — "WINNING in LITIGATION"
- 1pY7NW7i2_hNdNgcogHQJIs3yMNWJBkIL — "Sex of the would be child"
  (this template notably states there is NO confirmed sutra for the
  subject and that an astrologer should not predict on it; its ruling
  below leads with that warning, and the male/female planet lore is
  labelled classical probability lore, explicitly unsatisfactory per
  the template itself).

Sensitive topics stay probability guidance only, never deterministic
fact, with clinician/lawyer pointers kept in the question text.
"""

from __future__ import annotations

# Short method shared by most KP rulings; individual entries add their
# own specifics on top of it.
KP_METHOD_EN = (
    "In KP horary, judge from the dasa and antardasa lords running at "
    "the time of the question: if their star lord and sub lord signify "
    "the prime houses, the matter is promised; the Moon's star and sub "
    "at the moment of the question confirm or weaken it."
)
KP_METHOD_NE = (
    "केपी प्रश्नमा प्रश्न सोधिएको समयमा चलिरहेको दशा र अन्तर्दशाका "
    "स्वामीबाट निर्णय गरिन्छ: तिनका नक्षत्र स्वामी र उपस्वामीले प्रमुख "
    "भावलाई सङ्केत गरे विषय पूरा हुने वाचा हुन्छ; प्रश्नको क्षणमा "
    "चन्द्रमाको नक्षत्र र उपले त्यसलाई पुष्टि वा कमजोर पार्छ।"
)

RULINGS = {
    # ---- Marriage -------------------------------------------------
    "marriage_timing": {
        "source": "template:1BA-FSO_O264rPw90nNVckSkEqtGRqv6i",
        "source_label_en": "Legacy template: Timing of marriage",
        "source_label_ne": "परम्परागत टेम्प्लेट: विवाहको समय",
        "method_en": (
            KP_METHOD_EN + " Venus is the natural significator of marriage "
            "for both partners, and the template gives it a special power: "
            "Venus can promise marriage in its own dasa or antardasa even "
            "if it does not itself signify the marriage combination."
        ),
        "method_ne": (
            KP_METHOD_NE + " शुक्र दुवै पक्षका लागि विवाहका प्राकृतिक कारक हुन्, "
            "र टेम्प्लेटले तिनलाई विशेष शक्ति दिन्छ: शुक्रले आफ्नै दशा वा "
            "अन्तर्दशामा विवाहको संयोजनलाई आफैँले सङ्केत नगरे पनि विवाहको वाचा "
            "गर्न सक्छन्।"
        ),
        "favourable_en": (
            "The running dasa/antardasa planets signify 7, 2 and 11 through "
            "their star/sub lords, with 5 (love) and 9 (fortune) supporting; "
            "or a Venus period is running."
        ),
        "favourable_ne": (
            "चलिरहेको दशा/अन्तर्दशाका ग्रहले आफ्ना नक्षत्र/उपस्वामीमार्फत ७, २ र "
            "११ लाई सङ्केत गर्छन्, ५ (प्रेम) र ९ (भाग्य) ले समर्थन गर्छन्; वा "
            "शुक्रको अवधि चलिरहेको हुन्छ।"
        ),
        "unfavourable_en": (
            "The significators point to 1, 6 and 10 instead. Each is the 12th "
            "house from a prime house — 1st is loss of family (2nd), 6th is "
            "loss of partnership (7th), 10th is loss of fulfilment (11th) — "
            "so they negate marriage rather than promise it."
        ),
        "unfavourable_ne": (
            "कारकहरूले १, ६ र १० तर्फ सङ्केत गर्छन्। प्रत्येक प्रमुख भावबाट "
            "बाह्रौँ भाव हो — पहिलो परिवार (दोस्रो) को हानि, छैटौँ साझेदारी "
            "(सातौँ) को हानि, दशौँ पूर्ति (एघारौँ) को हानि हो — त्यसैले तिनले "
            "विवाहको वाचा होइन, नकार गर्छन्।"
        ),
        "timing_en": (
            "Marriage is timed to the Venus period, or to the period whose "
            "lords activate 7, 2 and 11 together; check transits touching "
            "those houses for the finer date."
        ),
        "timing_ne": (
            "विवाहको समय शुक्रको अवधि, वा ७, २ र ११ लाई एकसाथ सक्रिय पार्ने "
            "अवधिबाट तोकिन्छ; सूक्ष्म मितिका लागि ती भावलाई छुने गोचर हेर्नुहोस्।"
        ),
    },
    "marriage_known_circle": {
        "source": "classical",
        "source_label_en": "Classical KP horary rule",
        "source_label_ne": "शास्त्रीय केपी प्रश्न नियम",
        "method_en": (
            KP_METHOD_EN + " For the 'known circle' flavour, the marriage "
            "houses must also connect with the 3rd house (neighbours, close "
            "circle) or the 5th (romance, acquaintance)."
        ),
        "method_ne": (
            KP_METHOD_NE + " 'चिनजानको घेरा' का लागि विवाहका भावहरू तेस्रो भाव "
            "(छिमेक, नजिकको घेरा) वा पाँचौँ (प्रेम, चिनजान) सँग पनि जोडिनुपर्छ।"
        ),
        "favourable_en": (
            "The significators link 7 to 3 or 5 along with 2 and 11: the "
            "partner is someone already known — a neighbour, colleague, or "
            "an acquaintance turned partner."
        ),
        "favourable_ne": (
            "कारकहरूले ७ लाई २ र ११ सँगै ३ वा ५ सँग जोड्छन्: जोडी पहिल्यै "
            "चिनेकै व्यक्ति हुन्छ — छिमेकी, सहकर्मी, वा चिनजानबाट जोडी बनेको।"
        ),
        "unfavourable_en": (
            "The significators point to 1, 6 and 10 (negation of marriage), "
            "or the links run only to 9 and 12, which point to a stranger or "
            "a foreign connection instead of the known circle."
        ),
        "unfavourable_ne": (
            "कारकहरूले १, ६ र १० (विवाहको नकार) तर्फ सङ्केत गर्छन्, वा सम्बन्ध "
            "९ र १२ मा मात्र चल्छ, जसले चिनजानको घेराभन्दा अपरिचित वा विदेशी "
            "सम्बन्धतर्फ देखाउँछ।"
        ),
    },
    "marriage_abroad": {
        "source": "classical",
        "source_label_en": "Classical KP horary rule",
        "source_label_ne": "शास्त्रीय केपी प्रश्न नियम",
        "method_en": (
            KP_METHOD_EN + " For a foreign marriage, the 7th house must link "
            "to the 9th (long journey, foreign land) and the 12th (foreign "
            "residence); the 2nd and 11th must still support the marriage "
            "itself, or there is travel without marriage."
        ),
        "method_ne": (
            KP_METHOD_NE + " विदेशी विवाहका लागि सातौँ भाव नवौँ (लामो यात्रा, विदेश) "
            "र बाह्रौँ (विदेश बसोबास) सँग जोडिनुपर्छ; दोस्रो र एघारौँले विवाहलाई "
            "नै समर्थन गर्नुपर्छ, नत्र यात्रा मात्र हुन्छ, विवाह हुँदैन।"
        ),
        "favourable_en": (
            "The significators join 7 to 9 and 12 while also signifying 2 and "
            "11: a partner from abroad, or marriage followed by settling "
            "abroad."
        ),
        "favourable_ne": (
            "कारकहरूले ७ लाई ९ र १२ सँग जोड्छन् र २ र ११ लाई पनि सङ्केत गर्छन्: "
            "विदेशी जोडी, वा विवाहपछि विदेशमा बसोबास।"
        ),
        "unfavourable_en": (
            "The significators point to 1, 6 and 10 (negation), or the 4th "
            "house of home dominates, which keeps the native rooted at home "
            "rather than marrying abroad."
        ),
        "unfavourable_ne": (
            "कारकहरूले १, ६ र १० (नकार) तर्फ सङ्केत गर्छन्, वा घरको चौथो भाव "
            "बलियो हुन्छ, जसले व्यक्तिलाई विदेशमा विवाह गर्नुभन्दा घरमै अड्याउँछ।"
        ),
    },
    "marriage_remarriage": {
        "source": "classical",
        "source_label_en": "Classical KP horary rule",
        "source_label_ne": "शास्त्रीय केपी प्रश्न नियम",
        "method_en": (
            KP_METHOD_EN + " A subsequent marriage is read as a fresh "
            "partnership from the usual houses 7, 2 and 11, with the 9th "
            "house — the 3rd from the 7th — also read for a second partner "
            "in several traditions."
        ),
        "method_ne": (
            KP_METHOD_NE + " पछिल्लो विवाहलाई सामान्य भाव ७, २ र ११ बाट नयाँ "
            "साझेदारीका रूपमा पढिन्छ, केही परम्परामा सातौँबाट तेस्रो पर्ने नवौँ "
            "भावलाई पनि दोस्रो जोडीका लागि हेरिन्छ।"
        ),
        "favourable_en": (
            "The significators promise 7, 2 and 11 with 9 and 5 supporting: "
            "a new partnership is indicated, judged on the current chart."
        ),
        "favourable_ne": (
            "कारकहरूले ९ र ५ को समर्थनसहित ७, २ र ११ को वाचा गर्छन्: वर्तमान "
            "कुण्डलीका आधारमा नयाँ साझेदारीको सङ्केत हुन्छ।"
        ),
        "unfavourable_en": (
            "The significators point to 1, 6 and 10 (negation of partnership). "
            "Separately, no timing should be read until the earlier "
            "separation is fully settled in real life."
        ),
        "unfavourable_ne": (
            "कारकहरूले १, ६ र १० (साझेदारीको नकार) तर्फ सङ्केत गर्छन्। यसबाहेक, "
            "अघिल्लो सम्बन्ध वास्तविक जीवनमा पूर्ण रूपमा नटुङ्गिएसम्म कुनै समय "
            "पढ्नु हुँदैन।"
        ),
    },
    "marriage_relationship_strain": {
        "source": "classical",
        "source_label_en": "Classical KP horary rule",
        "source_label_ne": "शास्त्रीय केपी प्रश्न नियम",
        "method_en": (
            KP_METHOD_EN + " Strain is read from the 7th (partnership) "
            "against the 5th (romance outside the partnership) and the 12th "
            "(secrecy, separation), with Venus as significator."
        ),
        "method_ne": (
            KP_METHOD_NE + " तनाव सातौँ (साझेदारी) लाई पाँचौँ (साझेदारीबाहिरको प्रेम) "
            "र बाह्रौँ (गोप्यता, अलगाव) सँग तुलना गरी, कारक शुक्रसहित पढिन्छ।"
        ),
        "favourable_en": (
            "The significators keep 7 strong with 11 and 3 supporting "
            "communication and fulfilment: the strain passes or is talked "
            "through. This is a probability pattern only."
        ),
        "favourable_ne": (
            "कारकहरूले ११ र ३ को संवाद र पूर्तिको समर्थनसहित ७ लाई बलियो राख्छन्: "
            "तनाव टर्छ वा कुराकानीले समाधान हुन्छ। यो सम्भावना ढाँचा मात्र हो।"
        ),
        "unfavourable_en": (
            "The significators link 7 heavily to 5 and 12, or to 1, 6 and 10: "
            "a period of secrecy, distance or third-party involvement is "
            "indicated as a probability pattern — never proof about any "
            "specific person, and never a reason for an accusation. It should "
            "prompt conversation and counselling."
        ),
        "unfavourable_ne": (
            "कारकहरूले ७ लाई ५ र १२, वा १, ६ र १० सँग बलियो गरी जोड्छन्: "
            "गोप्यता, दूरी वा तेस्रो पक्षको संलग्नताको अवधि सम्भावना ढाँचाका "
            "रूपमा देखिन्छ — कुनै विशेष व्यक्तिबारे प्रमाण कहिल्यै होइन, र "
            "आरोपको कारण पनि होइन। यसले संवाद र परामर्शतर्फ प्रेरणा दिनुपर्छ।"
        ),
    },
    # ---- Education ------------------------------------------------
    "education_exams": {
        "source": "template:1KSwPLdi3KL9hyea2FVEtRJpvWfkV_SBw+classical",
        "source_label_en": "Legacy template: Education, plus classical KP rule",
        "source_label_ne": "परम्परागत टेम्प्लेट: शिक्षा, साथै शास्त्रीय केपी नियम",
        "method_en": (
            "The template gives the houses of education as 2, 4, 9, 11 with "
            "5 and 3 in support: the 4th is the prime house of education "
            "(primary education, per some scholars), the 9th is secondary "
            "and higher study, the 11th is fulfilment and gains in "
            "education, the 2nd is knowledge acquired, the 5th is inclination "
            "and intelligence, and the 3rd is communication, confidence and "
            "written examination. Mercury (analytical power, logic, "
            "communication) and Jupiter (wisdom, natural knowledge) must "
            "both be analysed. " + KP_METHOD_EN
        ),
        "method_ne": (
            "टेम्प्लेटले शिक्षाका भाव २, ४, ९, ११ र समर्थनमा ५ र ३ दिन्छ: चौथो "
            "शिक्षाको प्रमुख भाव हो (केही विद्वानका अनुसार प्राथमिक शिक्षा), "
            "नवौँ माध्यमिक र उच्च अध्ययन, एघारौँ पूर्ति र शिक्षामा लाभ, दोस्रो "
            "आर्जित ज्ञान, पाँचौँ झुकाव र बुद्धि, तेस्रो संवाद, आत्मविश्वास र "
            "लिखित परीक्षा हो। बुध (विश्लेषण शक्ति, तर्क, संवाद) र गुरु (बुद्धि, "
            "प्राकृतिक ज्ञान) दुवैको विश्लेषण गर्नुपर्छ। " + KP_METHOD_NE
        ),
        "favourable_en": (
            "The running periods signify 4 and 9 with 11, supported by 2, 5 "
            "and 3, and Mercury and Jupiter are well placed: success in the "
            "exam or interview is indicated."
        ),
        "favourable_ne": (
            "चलिरहेको अवधिले २, ५ र ३ को समर्थनसहित ४ र ९ लाई एघारौँसँग सङ्केत "
            "गर्छ, र बुध र गुरु राम्रो स्थितिमा छन्: परीक्षा वा अन्तर्वार्तामा "
            "सफलताको सङ्केत हुन्छ।"
        ),
        "unfavourable_en": (
            "The significators point to 8 and 12 (obstacle, loss and "
            "distraction) instead of 4 and 9: preparation alone is not "
            "carrying the result, and the period points to delay or "
            "underperformance."
        ),
        "unfavourable_ne": (
            "कारकहरूले ४ र ९ को सट्टा ८ र १२ (बाधा, हानि र ध्यान भट्किने) तर्फ "
            "सङ्केत गर्छन्: तयारी मात्रले परिणाम धान्दैन, र अवधिले ढिलाइ वा "
            "कमजोर प्रदर्शनतर्फ देखाउँछ।"
        ),
        "timing_en": (
            "Judge the exam date itself: the dasa/bhukti then running, and "
            "Mercury's transit on that date, decide the day more than the "
            "general period does."
        ),
        "timing_ne": (
            "परीक्षाको मिति आफैँलाई हेर्नुहोस्: त्यस बेला चलिरहेको दशा/भुक्ति र "
            "त्यस मितिमा बुधको गोचरले सामान्य अवधिभन्दा दिन बढी निर्धारण गर्छ।"
        ),
    },
    "education_abroad": {
        "source": "classical",
        "source_label_en": "Classical KP horary rule",
        "source_label_ne": "शास्त्रीय केपी प्रश्न नियम",
        "method_en": (
            KP_METHOD_EN + " For study abroad, higher study (9th) must link "
            "to the 12th (foreign residence) while the 4th (home) is "
            "weakened, with the 11th supporting fulfilment and the 3rd "
            "supporting movement."
        ),
        "method_ne": (
            KP_METHOD_NE + " विदेश अध्ययनका लागि उच्च अध्ययन (नवौँ) बाह्रौँ (विदेश "
            "बसोबास) सँग जोडिनुपर्छ र चौथो (घर) कमजोर हुनुपर्छ, एघारौँले पूर्तिलाई "
            "र तेस्रोले गतिविधिलाई समर्थन गर्नुपर्छ।"
        ),
        "favourable_en": (
            "The significators join 9 to 12 with 11 and 3 supporting and the "
            "4th not binding the native home: admission and departure abroad "
            "are indicated."
        ),
        "favourable_ne": (
            "कारकहरूले ९ लाई ११ र ३ को समर्थनसहित १२ सँग जोड्छन् र चौथोले व्यक्तिलाई "
            "घरमा बाँध्दैन: विदेशमा भर्ना र प्रस्थानको सङ्केत हुन्छ।"
        ),
        "unfavourable_en": (
            "The significators point to 1 and 6 (negation), or the 4th house "
            "of home dominates: study stays local, or the foreign plan "
            "stalls."
        ),
        "unfavourable_ne": (
            "कारकहरूले १ र ६ (नकार) तर्फ सङ्केत गर्छन्, वा घरको चौथो भाव बलियो "
            "हुन्छ: अध्ययन स्थानीयमै रहन्छ, वा विदेशी योजना अड्किन्छ।"
        ),
    },
    "education_field": {
        "source": "template:1KSwPLdi3KL9hyea2FVEtRJpvWfkV_SBw+classical",
        "source_label_en": "Legacy template: Education, plus classical KP rule",
        "source_label_ne": "परम्परागत टेम्प्लेट: शिक्षा, साथै शास्त्रीय केपी नियम",
        "method_en": (
            "Compare the study houses (4th prime, 9th higher) with the 10th "
            "(vocation). The template names Mercury (analytical power, "
            "logic, communication) and Jupiter (wisdom, natural knowledge) "
            "as the planets to analyse; classically Mars adds engineering "
            "and technical skill and Venus adds arts and design. The "
            "strongest significator among them, linked to 4 and 9 and to "
            "the 10th, hints at the direction."
        ),
        "method_ne": (
            "अध्ययनका भाव (चौथो प्रमुख, नवौँ उच्च) लाई दशौँ (पेशा) सँग तुलना "
            "गर्नुहोस्। टेम्प्लेटले विश्लेषण गर्नुपर्ने ग्रह बुध (विश्लेषण शक्ति, "
            "तर्क, संवाद) र गुरु (बुद्धि, प्राकृतिक ज्ञान) भन्छ; शास्त्रीय रूपमा "
            "मङ्गलले इन्जिनियरिङ र प्राविधिक सीप, शुक्रले कला र डिजाइन थप्छन्। "
            "तिनमध्ये बलियो कारक ४ र ९ तथा दशौँसँग जोडिए दिशाको सङ्केत गर्छ।"
        ),
        "favourable_en": (
            "One planet's significators clearly dominate the 4th/9th-to-10th "
            "link with 2 and 11 supporting: that planet's field is the "
            "indicated direction, in general terms only."
        ),
        "favourable_ne": (
            "एउटा ग्रहका कारकहरूले २ र ११ को समर्थनसहित चौथो/नवौँबाट दशौँसम्मको "
            "सम्बन्धमा स्पष्ट वर्चस्व राख्छन्: त्यो ग्रहको क्षेत्र नै सामान्य "
            "रूपमा सङ्केत गरिएको दिशा हो।"
        ),
        "unfavourable_en": (
            "The significators scatter across 6 and 8 (obstacle, service "
            "pressure) with no planet dominating: the chart gives no clear "
            "direction, and interests, aptitude and real options should "
            "decide instead."
        ),
        "unfavourable_ne": (
            "कारकहरू ६ र ८ (बाधा, सेवाको दबाब) मा छरिन्छन् र कुनै ग्रहको वर्चस्व "
            "हुँदैन: कुण्डलीले स्पष्ट दिशा दिँदैन, र रुचि, क्षमता र वास्तविक "
            "विकल्पले नै निर्णय गर्नुपर्छ।"
        ),
    },
    # ---- Career ---------------------------------------------------
    "career_job_change": {
        "source": "classical",
        "source_label_en": "Classical KP horary rule",
        "source_label_ne": "शास्त्रीय केपी प्रश्न नियम",
        "method_en": (
            KP_METHOD_EN + " A change is supported when the running period "
            "links career (10th) to service (6th) and gain (11th), and to a "
            "new employer — the 7th house as 'the other party'."
        ),
        "method_ne": (
            KP_METHOD_NE + " चलिरहेको अवधिले पेशा (दशौँ) लाई सेवा (छैटौँ) र लाभ "
            "(एघारौँ) सँग, र नयाँ रोजगारदाता — सातौँ भाव 'अर्को पक्ष' का रूपमा — "
            "सँग जोड्दा परिवर्तनलाई समर्थन हुन्छ।"
        ),
        "favourable_en": (
            "The significators join 10 to 6 and 11, with 2 and 7 supporting: "
            "a move to a new post with better gain is indicated."
        ),
        "favourable_ne": (
            "कारकहरूले दशौँलाई ६ र ११ सँग, २ र ७ को समर्थनसहित जोड्छन्: राम्रो "
            "लाभसहित नयाँ पदमा सर्ने सङ्केत हुन्छ।"
        ),
        "unfavourable_en": (
            "The significators point to 5 and 12 (loss, break) instead of 6 "
            "and 11: the period points to a gap or a loss rather than a "
            "clean change — check notice periods and offers in real life "
            "first."
        ),
        "unfavourable_ne": (
            "कारकहरूले ६ र ११ को सट्टा ५ र १२ (हानि, अन्तराल) तर्फ सङ्केत गर्छन्: "
            "अवधिले सफा परिवर्तनभन्दा अन्तराल वा हानितर्फ देखाउँछ — वास्तविक "
            "जीवनमा सूचना अवधि र प्रस्ताव पहिले हेर्नुहोस्।"
        ),
    },
    "career_business_vs_service": {
        "source": "template:1c2YlB2zZF_x3pCUhspvtVnYlIvinyeLu+classical",
        "source_label_en": "Legacy template: Business or Service, plus classical KP rule",
        "source_label_ne": "परम्परागत टेम्प्लेट: व्यापार वा सेवा, साथै शास्त्रीय केपी नियम",
        "method_en": (
            "The template studies 2, 6, 7, 10 and 11 together. The financial "
            "triangle (Aarthic Trikon) is 2, 6 and 10 — assets, struggle and "
            "direction of karma — and for career and financial prospects "
            "the main concentration is 2, 10 and 11. If the 6th house "
            "connects with 2, 10 and 11, the native is generally inclined "
            "towards service (and if capable of business, chooses trading); "
            "but if the 7th house activates along with 2, 10 and 11, the "
            "native joins business. Saturn is the prime significator of "
            "service: if the dasa-antardasa subjects are signified through "
            "Saturn, service prospects are promoted; if Mercury is "
            "associated with the combination, it gives a trading and "
            "business attitude."
        ),
        "method_ne": (
            "टेम्प्लेटले २, ६, ७, १० र ११ लाई एकसाथ अध्ययन गर्छ। आर्थिक त्रिकोण "
            "(आर्थिक त्रिकोण) २, ६ र १० हो — सम्पत्ति, सङ्घर्ष र कर्मको दिशा — र "
            "पेशा तथा आर्थिक सम्भावनाका लागि मुख्य ध्यान २, १० र ११ मा हुन्छ। "
            "छैटौँ भाव २, १० र ११ सँग जोडिए व्यक्ति सामान्यतया सेवातर्फ झुक्छ "
            "(र व्यापार गर्न सक्षम भए व्यापार रोज्छ); तर सातौँ भाव २, १० र ११ "
            "सँगै सक्रिय भए व्यक्ति व्यापारमा लाग्छ। शनि सेवाका प्रमुख कारक हुन्: "
            "दशा–अन्तर्दशाका विषय शनिमार्फत सङ्केत भए सेवाको सम्भावना बढ्छ; बुध "
            "संयोजनसँग जोडिए व्यापारिक मनोवृत्ति दिन्छ।"
        ),
        "favourable_en": (
            "Service leaning: the significators join 6 to 2, 10 and 11, "
            "signified through Saturn. Business leaning: the significators "
            "join 7 to 2, 10 and 11, with Mercury associated — trading and "
            "business attitude."
        ),
        "favourable_ne": (
            "सेवातर्फ झुकाव: कारकहरूले शनिमार्फत सङ्केत हुँदै ६ लाई २, १० र ११ "
            "सँग जोड्छन्। व्यापारतर्फ झुकाव: कारकहरूले बुधको संलग्नतासहित ७ लाई "
            "२, १० र ११ सँग जोड्छन् — व्यापारिक मनोवृत्ति।"
        ),
        "unfavourable_en": (
            "Neither the 6th nor the 7th connects with 2, 10 and 11, or the "
            "significators point to 5 and 9 (the classical negation here): "
            "the chart gives no clear leaning, and capital, skills and "
            "market conditions matter as much as the chart."
        ),
        "unfavourable_ne": (
            "न छैटौँ न सातौँ २, १० र ११ सँग जोडिन्छ, वा कारकहरूले ५ र ९ "
            "(यहाँको शास्त्रीय नकार) तर्फ सङ्केत गर्छन्: कुण्डलीले स्पष्ट झुकाव "
            "दिँदैन, र पुँजी, सीप र बजारको अवस्था कुण्डलीजत्तिकै महत्त्वपूर्ण हुन्छ।"
        ),
    },
    "career_promotion_transfer": {
        "source": "classical",
        "source_label_en": "Classical KP horary rule",
        "source_label_ne": "शास्त्रीय केपी प्रश्न नियम",
        "method_en": (
            KP_METHOD_EN + " Promotion reads from status (10th) and gain "
            "(11th) with the service record (6th); transfer adds movement "
            "and change of place (3rd). The Sun, significator of status, "
            "should support rather than negate these houses."
        ),
        "method_ne": (
            KP_METHOD_NE + " पदोन्नति पद (दशौँ) र लाभ (एघारौँ) बाट सेवा अभिलेख "
            "(छैटौँ) सहित पढिन्छ; सरुवामा गतिविधि र ठाउँ परिवर्तन (तेस्रो) "
            "थपिन्छ। पदका कारक सूर्यले यी भावलाई नकार्नुभन्दा समर्थन गर्नुपर्छ।"
        ),
        "favourable_en": (
            "The significators join 10 to 11 and 6, with 2 and 3 supporting "
            "for a transfer: promotion, or promotion with a move, is "
            "indicated around the appraisal or transfer window."
        ),
        "favourable_ne": (
            "कारकहरूले दशौँलाई ११ र ६ सँग, सरुवाका लागि २ र ३ को समर्थनसहित "
            "जोड्छन्: मूल्याङ्कन वा सरुवाको समयमा पदोन्नति, वा सरुवासहितको "
            "पदोन्नतिको सङ्केत हुन्छ।"
        ),
        "unfavourable_en": (
            "The significators point to 5 and 8 (loss of position, obstacle) "
            "instead of 10 and 11: the period points to delay, a missed "
            "round, or a transfer without promotion."
        ),
        "unfavourable_ne": (
            "कारकहरूले दशौँ र एघारौँको सट्टा ५ र ८ (पदको हानि, बाधा) तर्फ सङ्केत "
            "गर्छन्: अवधिले ढिलाइ, छुटेको चरण, वा पदोन्नतिविनाको सरुवातर्फ देखाउँछ।"
        ),
    },
    "career_break": {
        "source": "classical",
        "source_label_en": "Classical KP horary rule",
        "source_label_ne": "शास्त्रीय केपी प्रश्न नियम",
        "method_en": (
            KP_METHOD_EN + " A break shows when the running period links "
            "career houses (10th, 6th) to the 12th (loss, separation) or "
            "the 8th (obstacle) and negates gain (11th, 2nd)."
        ),
        "method_ne": (
            KP_METHOD_NE + " चलिरहेको अवधिले पेशाका भाव (दशौँ, छैटौँ) लाई बाह्रौँ "
            "(हानि, अलगाव) वा आठौँ (बाधा) सँग जोड्दा र लाभ (एघारौँ, दोस्रो) "
            "नकार्दा अन्तराल देखिन्छ।"
        ),
        "favourable_en": (
            "The significators return to 10, 6 and 11 with 2 supporting: "
            "the interrupting period ends and a return — or a new direction "
            "— opens. Read it as a period to plan through, not a permanent "
            "verdict."
        ),
        "favourable_ne": (
            "कारकहरू २ को समर्थनसहित दशौँ, छैटौँ र एघारौँमा फर्किन्छन्: बाधा "
            "पुर्याउने अवधि सकिन्छ र फिर्ती — वा नयाँ दिशा — खुल्छ। यसलाई योजना "
            "बनाउने अवधि ठान्नुहोस्, स्थायी फैसला होइन।"
        ),
        "unfavourable_en": (
            "The significators stay linked to 12 and 8 while negating 11 and "
            "2: the break extends, and the chart points to planning and "
            "reskilling during the gap rather than forcing a return."
        ),
        "unfavourable_ne": (
            "कारकहरू ११ र २ लाई नकार्दै १२ र ८ सँग जोडिइरहन्छन्: अन्तराल लम्बिन्छ, "
            "र कुण्डलीले फिर्ती जबरजस्ती गर्नुभन्दा अन्तरालमा योजना र नयाँ सीपतर्फ "
            "देखाउँछ।"
        ),
    },
    # ---- Travel ---------------------------------------------------
    "travel_settling_abroad": {
        "source": "classical",
        "source_label_en": "Classical KP horary rule",
        "source_label_ne": "शास्त्रीय केपी प्रश्न नियम",
        "method_en": (
            KP_METHOD_EN + " Foreign residence (12th) with long travel (9th), "
            "away from home (4th), supported by fulfilment (11th) and "
            "movement (3rd), points to settling abroad. The Moon, "
            "significator of movement and residence, is also checked."
        ),
        "method_ne": (
            KP_METHOD_NE + " विदेश बसोबास (बाह्रौँ) सँग लामो यात्रा (नवौँ), घर "
            "(चौथो) बाट टाढा, पूर्ति (एघारौँ) र गतिविधि (तेस्रो) ले समर्थन गर्दा "
            "विदेशमा बसोबासको सङ्केत हुन्छ। गतिविधि र बसोबासका कारक चन्द्रमा "
            "पनि हेरिन्छ।"
        ),
        "favourable_en": (
            "The significators join 12 to 9 with 11 and 3 supporting, and "
            "the 4th does not bind the native home: settling abroad is "
            "indicated, alongside visas and practical plans."
        ),
        "favourable_ne": (
            "कारकहरूले बाह्रौँलाई ११ र ३ को समर्थनसहित नवौँसँग जोड्छन् र चौथोले "
            "व्यक्तिलाई घरमा बाँध्दैन: भिसा र व्यावहारिक योजनासँगै विदेशमा "
            "बसोबासको सङ्केत हुन्छ।"
        ),
        "unfavourable_en": (
            "The significators point to 1 and 6 (negation), or the 4th house "
            "of home dominates: the stay abroad remains temporary, or the "
            "move does not happen."
        ),
        "unfavourable_ne": (
            "कारकहरूले १ र ६ (नकार) तर्फ सङ्केत गर्छन्, वा घरको चौथो भाव बलियो "
            "हुन्छ: विदेश बसाइ अस्थायी नै रहन्छ, वा सर्ने काम हुँदैन।"
        ),
    },
    "travel_return_home": {
        "source": "classical",
        "source_label_en": "Classical KP horary rule",
        "source_label_ne": "शास्त्रीय केपी प्रश्न नियम",
        "method_en": (
            KP_METHOD_EN + " Return reads as home (4th) becoming strong again "
            "after a foreign period (12th, 9th), with the 11th and 2nd "
            "supporting a settled return rather than a forced one."
        ),
        "method_ne": (
            KP_METHOD_NE + " फिर्ती विदेशी अवधि (बाह्रौँ, नवौँ) पछि घर (चौथो) फेरि "
            "बलियो हुँदा पढिन्छ, एघारौँ र दोस्रोले बाध्यात्मक होइन, व्यवस्थित "
            "फिर्ती लाई समर्थन गर्नुपर्छ।"
        ),
        "favourable_en": (
            "The significators restore 4 with 11 and 2 supporting around the "
            "planned return dates: a settled return home is indicated."
        ),
        "favourable_ne": (
            "कारकहरूले योजनाबद्ध फिर्ती मितिमा ११ र २ को समर्थनसहित चौथोलाई "
            "पुनर्स्थापित गर्छन्: व्यवस्थित घर फिर्तीको सङ्केत हुन्छ।"
        ),
        "unfavourable_en": (
            "The significators point to 6 and 8 (obstacle, forced "
            "circumstance) or stay locked on 12 and 9: the return is delayed, "
            "or it happens under pressure rather than by choice."
        ),
        "unfavourable_ne": (
            "कारकहरूले ६ र ८ (बाधा, बाध्यात्मक परिस्थिति) तर्फ सङ्केत गर्छन्, वा "
            "बाह्रौँ र नवौँमै अड्किन्छन्: फिर्ती ढिलो हुन्छ, वा रोजाइले होइन, "
            "दबाबमा हुन्छ।"
        ),
    },
    # ---- Children -------------------------------------------------
    "children_timing_general": {
        "source": "classical",
        "source_label_en": "Classical KP horary rule",
        "source_label_ne": "शास्त्रीय केपी प्रश्न नियम",
        "method_en": (
            KP_METHOD_EN + " Children are read from the 5th (children), 2nd "
            "(family addition) and 11th (fulfilment), with Jupiter as "
            "significator. This entry covers timing and obstacles only, in "
            "general terms: it makes no claim about a child's sex or "
            "number."
        ),
        "method_ne": (
            KP_METHOD_NE + " सन्तान पाँचौँ (सन्तान), दोस्रो (परिवार थप) र एघारौँ "
            "(पूर्ति) बाट, कारक गुरुसहित पढिन्छ। यो प्रविष्टिले समय र बाधा मात्र, "
            "सामान्य रूपमा समेट्छ: सन्तानको सङ्ख्या वा लिङ्गबारे कुनै दाबी गर्दैन।"
        ),
        "favourable_en": (
            "The significators promise 5 with 2 and 11, supported by 9 and 7: "
            "the timing is indicated, with Jupiter well placed."
        ),
        "favourable_ne": (
            "कारकहरूले ९ र ७ को समर्थनसहित ५ लाई २ र ११ सँग वाचा गर्छन्: गुरु "
            "राम्रो स्थितिमा हुँदा समयको सङ्केत हुन्छ।"
        ),
        "unfavourable_en": (
            "The significators point to 1, 6 and 10 (negation of the 5th "
            "house promise): delays point to the negating houses to be "
            "worked through — including medical advice where relevant — not "
            "to a fixed outcome."
        ),
        "unfavourable_ne": (
            "कारकहरूले १, ६ र १० (पाँचौँ भावको वाचाको नकार) तर्फ सङ्केत गर्छन्: "
            "ढिलाइले नकार्ने भावलाई समाधान गर्नुपर्ने देखाउँछ — सान्दर्भिक भए "
            "चिकित्सकीय सल्लाहसहित — निश्चित परिणाम होइन।"
        ),
    },
    "children_sex_indication": {
        "source": "template:1pY7NW7i2_hNdNgcogHQJIs3yMNWJBkIL+classical",
        "source_label_en": (
            "Legacy template: Sex of the would be child, plus classical "
            "probability lore (labelled unsatisfactory by the template)"
        ),
        "source_label_ne": (
            "परम्परागत टेम्प्लेट: हुने सन्तानको लिङ्ग, साथै शास्त्रीय "
            "सम्भावना ज्ञान (टेम्प्लेटले नै असन्तोषजनक भनेको)"
        ),
        "method_en": (
            "The template's own position comes first, and it is a refusal, "
            "not a rule: there is NO confirmed sutra for this subject in "
            "astrological texts, an astrologer should not predict on such a "
            "subject, and the number of female children is already "
            "decreasing day by day. It adds that birth time can never be "
            "accurate enough — a small error changes the significations of "
            "houses and planets, so predictions built on them can never be "
            "accurate — and that the probability sutras that do exist give "
            "unsatisfactory results. The lore below is one such probability "
            "sutra, given only so the reader understands what tradition "
            "claims: male indications are traditionally counted from Sun, "
            "Mars and Jupiter, female from Moon and Venus, read from the "
            "5th house, its lord and the planets and signs involved, "
            "together with the 2nd and 11th. Treat it as play with "
            "probability, never as knowledge."
        ),
        "method_ne": (
            "टेम्प्लेटको आफ्नै अडान पहिले आउँछ, र त्यो नियम होइन, अस्वीकार हो: "
            "यस विषयमा ज्योतिष ग्रन्थमा कुनै पुष्टि भएको सूत्र छैन, ज्योतिषीले "
            "यस्तो विषयमा भविष्यवाणी गर्नु हुँदैन, र छोरीको सङ्ख्या दिनदिनै "
            "घट्दै गइरहेको छ। यसले थप्छ कि जन्म समय कहिल्यै पर्याप्त सही हुन "
            "सक्दैन — सानो त्रुटिले भाव र ग्रहका सङ्केत बदल्छ, त्यसैले तिनमा "
            "आधारित भविष्यवाणी कहिल्यै सही हुन सक्दैन — र भएका सम्भावना सूत्रले "
            "असन्तोषजनक परिणाम दिन्छन्। तलको ज्ञान त्यस्तै एउटा सम्भावना सूत्र हो, "
            "परम्पराले के दाबी गर्छ भन्ने बुझ्न मात्र दिइएको: पुरुष सङ्केत "
            "परम्परागत रूपमा सूर्य, मङ्गल र गुरुबाट, स्त्री सङ्केत चन्द्रमा र "
            "शुक्रबाट, पाँचौँ भाव, त्यसका स्वामी र संलग्न ग्रह/राशिबाट, दोस्रो र "
            "एघारौँसँगै गनिन्छ। यसलाई सम्भावनासँगको खेल ठान्नुहोस्, ज्ञान कहिल्यै होइन।"
        ),
        "favourable_en": (
            "Male leaning only: the 5th-house significators are predominantly "
            "Sun, Mars and Jupiter. Female leaning only: they are "
            "predominantly Moon and Venus. In both cases the template's "
            "warning stands — this is an unsatisfactory probability leaning, "
            "not a determination, and it must not be used for any medical "
            "decision."
        ),
        "favourable_ne": (
            "पुरुषतर्फ झुकाव मात्र: पाँचौँ भावका कारकहरू प्रायः सूर्य, मङ्गल र गुरु "
            "हुन्छन्। स्त्रीतर्फ झुकाव मात्र: तिनीहरू प्रायः चन्द्रमा र शुक्र "
            "हुन्छन्। दुवै अवस्थामा टेम्प्लेटको चेतावनी कायमै छ — यो असन्तोषजनक "
            "सम्भावना झुकाव मात्र हो, निर्धारण होइन, र कुनै चिकित्सकीय निर्णयका "
            "लागि प्रयोग गर्नु हुँदैन।"
        ),
        "unfavourable_en": (
            "No leaning can be read when the significators are mixed, or "
            "point to 1, 6 and 10 (negation of the 5th-house promise). The "
            "honest answer then is the template's own: do not predict on "
            "this subject."
        ),
        "unfavourable_ne": (
            "कारकहरू मिश्रित हुँदा, वा १, ६ र १० (पाँचौँ भावको वाचाको नकार) तर्फ "
            "सङ्केत गर्दा कुनै झुकाव पढ्न सकिँदैन। त्यस बेला इमानदार उत्तर "
            "टेम्प्लेटकै हो: यस विषयमा भविष्यवाणी नगर्नुहोस्।"
        ),
    },
    "children_pregnancy_difficulty": {
        "source": "classical",
        "source_label_en": "Classical KP horary rule",
        "source_label_ne": "शास्त्रीय केपी प्रश्न नियम",
        "method_en": (
            KP_METHOD_EN + " Difficulty is read from the 5th house against "
            "the 8th (sudden difficulty), 12th (loss) and 6th (health "
            "obstacle), with the Moon as significator of pregnancy."
        ),
        "method_ne": (
            KP_METHOD_NE + " कठिनाइ पाँचौँ भावलाई आठौँ (आकस्मिक कठिनाइ), बाह्रौँ "
            "(हानि) र छैटौँ (स्वास्थ्य बाधा) सँग तुलना गरी, गर्भावस्थाका कारक "
            "चन्द्रमासहित पढिन्छ।"
        ),
        "favourable_en": (
            "The significators keep 5 strong with 2 and 11, and 9 and 11 "
            "supporting: the period is indicated as manageable, with "
            "ordinary medical care."
        ),
        "favourable_ne": (
            "कारकहरूले २ र ११ सँग पाँचौँलाई बलियो राख्छन्, ९ र ११ ले समर्थन गर्छन्: "
            "अवधि सामान्य चिकित्सकीय हेरचाहसहित व्यवस्थापन गर्न सकिने रूपमा "
            "देखिन्छ।"
        ),
        "unfavourable_en": (
            "The significators link 5 heavily to 8, 12 and 6: a heavy "
            "indication is a probability prompt for extra medical care and "
            "rest — it is not a diagnosis, not a prediction of loss, and any "
            "pregnancy concern must go to a clinician promptly."
        ),
        "unfavourable_ne": (
            "कारकहरूले पाँचौँलाई ८, १२ र ६ सँग बलियो गरी जोड्छन्: भारी सङ्केत "
            "भनेको थप चिकित्सकीय हेरचाह र आरामका लागि सम्भावना प्रेरणा मात्र हो — "
            "निदान होइन, हानि हुन्छ भन्ने भविष्यवाणी होइन, र गर्भावस्थाको कुनै पनि "
            "चिन्ता तुरुन्त चिकित्सककहाँ लैजानुपर्छ।"
        ),
    },
    # ---- Property -------------------------------------------------
    "property_buying": {
        "source": "template:1BkKEQ7Dhd9EEnA4XLHaxrZRYABACtVBE+classical",
        "source_label_en": "Legacy template: Purchase of Property, plus classical KP rule",
        "source_label_ne": "परम्परागत टेम्प्लेट: सम्पत्ति खरिद, साथै शास्त्रीय केपी नियम",
        "method_en": (
            "The template gives the houses as 4 (prime house of property), "
            "11 (gain of property, fulfilment of desire) and 12 (expenses "
            "incurred during purchase). Mars and Saturn are the natural "
            "significators of property, and involvement of BOTH is an "
            "important condition: a native purchases a property when the "
            "dasa-antardasa planets activate 4, 11 and 12, with Mars and "
            "Saturn involved in the progressed dasa-antardasa. The template "
            "adds: check transit for the timing of any event."
        ),
        "method_ne": (
            "टेम्प्लेटले भाव ४ (सम्पत्तिको प्रमुख भाव), ११ (सम्पत्तिको लाभ, इच्छाको "
            "पूर्ति) र १२ (खरिदमा लाग्ने खर्च) दिन्छ। मङ्गल र शनि सम्पत्तिका "
            "प्राकृतिक कारक हुन्, र दुवैको संलग्नता महत्त्वपूर्ण सर्त हो: व्यक्ति "
            "तब सम्पत्ति किन्छ जब दशा–अन्तर्दशाका ग्रहले ४, ११ र १२ लाई सक्रिय "
            "पार्छन्, प्रगत दशा–अन्तर्दशामा मङ्गल र शनि संलग्न हुन्छन्। टेम्प्लेटले "
            "थप्छ: कुनै पनि घटनाको समयका लागि गोचर हेर्नुहोस्।"
        ),
        "favourable_en": (
            "The running dasa-antardasa activates 4, 11 and 12 together, "
            "with Mars and Saturn both involved in the progressed periods, "
            "and 2 and 9 supporting resources and fortune: purchase is "
            "indicated. Titles, loans and prices must still be verified in "
            "real life."
        ),
        "favourable_ne": (
            "चलिरहेको दशा–अन्तर्दशाले ४, ११ र १२ लाई एकसाथ सक्रिय पार्छ, प्रगत "
            "अवधिमा मङ्गल र शनि दुवै संलग्न हुन्छन्, र २ र ९ ले स्रोत र भाग्यलाई "
            "समर्थन गर्छन्: खरिदको सङ्केत हुन्छ। लालपुर्जा, ऋण र मूल्य वास्तविक "
            "जीवनमा नै जाँच्नुपर्छ।"
        ),
        "unfavourable_en": (
            "The significators point to 6 and 8 (dispute, obstacle — the "
            "classical negation here), or Mars or Saturn is absent from the "
            "running periods: the purchase stalls, or the property carries "
            "a dispute to be checked first."
        ),
        "unfavourable_ne": (
            "कारकहरूले ६ र ८ (विवाद, बाधा — यहाँको शास्त्रीय नकार) तर्फ सङ्केत "
            "गर्छन्, वा चलिरहेको अवधिमा मङ्गल वा शनि अनुपस्थित हुन्छ: खरिद अड्किन्छ, "
            "वा सम्पत्तिमा पहिले जाँच्नुपर्ने विवाद हुन्छ।"
        ),
        "timing_en": (
            "Time the purchase to the dasa-antardasa activating 4, 11 and "
            "12, confirmed by a transit touching those houses, and by a "
            "favourable Muhurta for registration if one is sought."
        ),
        "timing_ne": (
            "खरिदको समय ४, ११ र १२ लाई सक्रिय पार्ने दशा–अन्तर्दशाबाट, ती भावलाई "
            "छुने गोचरले पुष्टि गरी, र दर्ताका लागि अनुकूल मुहूर्त खोजिए त्यसबाट "
            "तोकिन्छ।"
        ),
    },
    "property_sale_timing": {
        "source": "classical",
        "source_label_en": "Classical KP horary rule",
        "source_label_ne": "शास्त्रीय केपी प्रश्न नियम",
        "method_en": (
            KP_METHOD_EN + " Sale reads from property (4th) through action "
            "(10th) and change (3rd — the 12th from the 4th, giving up the "
            "property), with gain (11th) and resources (2nd) supporting it. "
            "Rental income is a related check: the 4th with the 11th and "
            "2nd supporting steady gain, without promising any rent figure."
        ),
        "method_ne": (
            KP_METHOD_NE + " बिक्री सम्पत्ति (चौथो) बाट कार्य (दशौँ) र परिवर्तन "
            "(तेस्रो — चौथोबाट बाह्रौँ, सम्पत्ति त्याग) हुँदै, लाभ (एघारौँ) र स्रोत "
            "(दोस्रो) ले समर्थन गर्दा पढिन्छ। भाडा आम्दानी सम्बन्धित जाँच हो: "
            "चौथोसँग एघारौँ र दोस्रोले स्थिर लाभलाई समर्थन गर्ने, भाडा रकमको "
            "प्रतिज्ञा नगरी।"
        ),
        "favourable_en": (
            "The significators join 4 to 10 and 3 with 11 and 2 supporting: "
            "a sale at a gain is indicated; for rent, the same 4-11-2 link "
            "supports steady income."
        ),
        "favourable_ne": (
            "कारकहरूले चौथोलाई ११ र २ को समर्थनसहित दशौँ र तेस्रोसँग जोड्छन्: "
            "लाभमा बिक्रीको सङ्केत हुन्छ; भाडाका लागि त्यही ४-११-२ सम्बन्धले स्थिर "
            "आम्दानीलाई समर्थन गर्छ।"
        ),
        "unfavourable_en": (
            "The significators point to 6 and 12 (dispute, loss) instead of "
            "10 and 3: the sale stalls or goes at a loss, and market price "
            "and buyer readiness still decide the sale."
        ),
        "unfavourable_ne": (
            "कारकहरूले दशौँ र तेस्रोको सट्टा ६ र १२ (विवाद, हानि) तर्फ सङ्केत "
            "गर्छन्: बिक्री अड्किन्छ वा घाटामा हुन्छ, र बजार मूल्य र क्रेताको तयारीले "
            "नै बिक्री निर्धारण गर्छ।"
        ),
    },
    # ---- Vehicle --------------------------------------------------
    "vehicle_buying": {
        "source": "template:1r2j4q95exlfFLHYhLulaiYqLGYbpiNG_+classical",
        "source_label_en": "Legacy template: Sale-Purchase of Vehicle, plus classical KP rule",
        "source_label_ne": "परम्परागत टेम्प्लेट: सवारी बिक्री–खरिद, साथै शास्त्रीय केपी नियम",
        "method_en": (
            "The template gives the houses as 4, 11 and 12, noting some "
            "scholars also give importance to the 3rd house (travel, "
            "communication). Venus is the natural significator of the "
            "vehicle: a Venus dasa-antardasa may activate this subject "
            "whether or not Venus signifies the above combination, and "
            "otherwise Venus should still be present in the progressed "
            "dasa-antardasa."
        ),
        "method_ne": (
            "टेम्प्लेटले भाव ४, ११ र १२ दिन्छ, केही विद्वानले तेस्रो भाव (यात्रा, "
            "संवाद) लाई पनि महत्त्व दिन्छन् भन्ने उल्लेखसहित। शुक्र सवारीका "
            "प्राकृतिक कारक हुन्: शुक्रको दशा–अन्तर्दशाले माथिको संयोजनलाई सङ्केत "
            "गरे वा नगरे पनि यस विषयलाई सक्रिय पार्न सक्छ, र नत्र पनि प्रगत "
            "दशा–अन्तर्दशामा शुक्र उपस्थित हुनुपर्छ।"
        ),
        "favourable_en": (
            "The running periods activate 4, 11 and 12 with Venus present in "
            "the progressed dasa-antardasa (or a Venus period running), "
            "supported by 2 and 9: purchase is indicated. Condition, papers "
            "and loan terms must still be verified in real life."
        ),
        "favourable_ne": (
            "चलिरहेको अवधिले प्रगत दशा–अन्तर्दशामा शुक्र उपस्थित हुँदा (वा शुक्रको "
            "अवधि चल्दा) ४, ११ र १२ लाई सक्रिय पार्छ, २ र ९ ले समर्थन गर्छन्: "
            "खरिदको सङ्केत हुन्छ। अवस्था, कागजात र ऋणका सर्त वास्तविक जीवनमा नै "
            "जाँच्नुपर्छ।"
        ),
        "unfavourable_en": (
            "The significators point to 6 and 8 (loan trouble, obstacle — "
            "the classical negation here), or Venus is absent from the "
            "running periods: the purchase stalls or the vehicle disappoints."
        ),
        "unfavourable_ne": (
            "कारकहरूले ६ र ८ (ऋण समस्या, बाधा — यहाँको शास्त्रीय नकार) तर्फ सङ्केत "
            "गर्छन्, वा चलिरहेको अवधिमा शुक्र अनुपस्थित हुन्छ: खरिद अड्किन्छ वा "
            "सवारीले निराश पार्छ।"
        ),
    },
    "vehicle_sale_loan": {
        "source": "template:1r2j4q95exlfFLHYhLulaiYqLGYbpiNG_+classical",
        "source_label_en": "Legacy template: Sale-Purchase of Vehicle, plus classical KP rule",
        "source_label_ne": "परम्परागत टेम्प्लेट: सवारी बिक्री–खरिद, साथै शास्त्रीय केपी नियम",
        "method_en": (
            "The template's vehicle houses (4, 11, 12) are read together "
            "with the 6th house of loan and obligation for the repayment "
            "side: sale and loan-repayment both need the vehicle (4th) and "
            "gain (11th) supported, with the 6th showing the obligation being "
            "cleared. Venus (vehicle) and Mercury (papers, commerce) are "
            "checked as significators."
        ),
        "method_ne": (
            "टेम्प्लेटका सवारी भाव (४, ११, १२) लाई भुक्तानी पक्षका लागि ऋण र दायित्वको "
            "छैटौँ भावसँगै पढिन्छ: बिक्री र ऋण–भुक्तानी दुवैमा सवारी (चौथो) र लाभ "
            "(एघारौँ) लाई समर्थन चाहिन्छ, छैटौँले दायित्व चुक्ता भएको देखाउँछ। "
            "शुक्र (सवारी) र बुध (कागजात, व्यापार) कारकका रूपमा हेरिन्छन्।"
        ),
        "favourable_en": (
            "The significators join 4 to 6 and 11 with 2 and 10 supporting: "
            "a sale with a clean settlement, or repayment from available "
            "resources, is indicated. Confirm the loan statement and buyer "
            "papers in real life."
        ),
        "favourable_ne": (
            "कारकहरूले चौथोलाई २ र दशौँको समर्थनसहित छैटौँ र एघारौँसँग जोड्छन्: "
            "सफा फर्स्योटसहितको बिक्री, वा उपलब्ध स्रोतबाट भुक्तानीको सङ्केत हुन्छ। "
            "ऋण विवरण तथा क्रेता कागजात वास्तविक जीवनमा पुष्टि गर्नुहोस्।"
        ),
        "unfavourable_en": (
            "The significators point to 8 and 12 (loss, outlay without "
            "return) instead of 11: the sale goes at a loss or the loan "
            "lingers — the loan schedule itself sets the repayment dates."
        ),
        "unfavourable_ne": (
            "कारकहरूले एघारौँको सट्टा ८ र १२ (हानि, प्रतिफलविनाको खर्च) तर्फ सङ्केत "
            "गर्छन्: बिक्री घाटामा हुन्छ वा ऋण लम्बिन्छ — ऋण तालिकाले नै भुक्तानी "
            "मिति निर्धारण गर्छ।"
        ),
    },
    # ---- Health / general -----------------------------------------
    "health_general": {
        "source": "template:1F4-A-aowvw9ixguaqjtsvNvV1HTytjtj+classical",
        "source_label_en": "Legacy template: General sickness, plus classical KP rule",
        "source_label_ne": "परम्परागत टेम्प्लेट: सामान्य रोग, साथै शास्त्रीय केपी नियम",
        "method_en": (
            "The template is short and specific: the 1st and 6th houses mean "
            "a small disease or sickness — easily curable, of seasonal "
            "impact. So a 1st/6th indication on its own is a minor matter. "
            "Severity is judged classically: links to the 8th and 12th are "
            "what turn a minor indication into a serious one. This entry is "
            "a general wellbeing check only, never medical advice."
        ),
        "method_ne": (
            "टेम्प्लेट छोटो र स्पष्ट छ: पहिलो र छैटौँ भावको अर्थ सानो रोग वा बिरामी "
            "— सजिलै निको हुने, मौसमी प्रभावको हुन्छ। त्यसैले पहिलो/छैटौँको सङ्केत "
            "एक्लै सानो विषय हो। गम्भीरता शास्त्रीय रूपमा पढिन्छ: आठौँ र बाह्रौँसँगको "
            "सम्बन्धले नै सानो सङ्केतलाई गम्भीर बनाउँछ। यो प्रविष्टि सामान्य "
            "स्वास्थ्य जाँच मात्र हो, चिकित्सकीय सल्लाह कहिल्यै होइन।"
        ),
        "favourable_en": (
            "The significators stay on 1 and 6 with 2 and 9 supporting, and "
            "the Sun (vitality) well placed, without 8 or 12 links: a small, "
            "seasonal, easily curable matter — rest, routine and an "
            "ordinary check-up."
        ),
        "favourable_ne": (
            "कारकहरू २ र ९ को समर्थनसहित पहिलो र छैटौँमै रहन्छन्, सूर्य "
            "(जीवनशक्ति) राम्रो स्थितिमा हुन्छ, ८ वा १२ को सम्बन्ध हुँदैन: सानो, "
            "मौसमी, सजिलै निको हुने विषय — आराम, दिनचर्या र सामान्य जाँच।"
        ),
        "unfavourable_en": (
            "The significators link 1 and 6 heavily to 8 and 12: the "
            "indication is no longer 'small and curable' on the template's "
            "own terms, and any health concern must go to a clinician "
            "promptly. The chart never diagnoses, names a condition, or "
            "times treatment."
        ),
        "unfavourable_ne": (
            "कारकहरूले पहिलो र छैटौँलाई ८ र १२ सँग बलियो गरी जोड्छन्: टेम्प्लेटकै "
            "शब्दमा सङ्केत अब 'सानो र निको हुने' रहँदैन, र कुनै पनि स्वास्थ्य "
            "चिन्ता तुरुन्त चिकित्सककहाँ लैजानुपर्छ। कुण्डलीले कहिल्यै निदान गर्दैन, "
            "अवस्था तोक्दैन, वा उपचारको समय निर्धारण गर्दैन।"
        ),
    },
    "general_accident_caution": {
        "source": "classical",
        "source_label_en": "Classical KP horary rule",
        "source_label_ne": "शास्त्रीय केपी प्रश्न नियम",
        "method_en": (
            KP_METHOD_EN + " Traditionally the 8th (sudden events), 12th "
            "(loss) and 6th (injury, obstacle) are checked against vitality "
            "(1st) and support (11th), with Mars as significator of sudden "
            "force. This entry is general caution only, never a personal "
            "accident prediction."
        ),
        "method_ne": (
            KP_METHOD_NE + " परम्परागत रूपमा आठौँ (आकस्मिक घटना), बाह्रौँ (हानि) र "
            "छैटौँ (चोट, बाधा) लाई जीवनशक्ति (पहिलो) र समर्थन (एघारौँ) सँग तुलना "
            "गरिन्छ, आकस्मिक बलका कारक मङ्गलसहित। यो प्रविष्टि सामान्य सावधानी "
            "मात्र हो, व्यक्तिगत दुर्घटनाको भविष्यवाणी कहिल्यै होइन।"
        ),
        "favourable_en": (
            "The significators keep 1 and 11 strong against 8, 12 and 6: "
            "no special caution beyond ordinary care is indicated."
        ),
        "favourable_ne": (
            "कारकहरूले ८, १२ र ६ विरुद्ध पहिलो र एघारौँलाई बलियो राख्छन्: "
            "सामान्य हेरचाहभन्दा विशेष सावधानीको सङ्केत हुँदैन।"
        ),
        "unfavourable_en": (
            "The significators link 8, 12 and 6 heavily, or Mars transits "
            "are harsh in general terms: a heavy period is a prompt for "
            "extra care on the road and at work, nothing more. Safe "
            "behaviour, not the chart, prevents accidents."
        ),
        "unfavourable_ne": (
            "कारकहरूले ८, १२ र ६ लाई बलियो गरी जोड्छन्, वा मङ्गलको गोचर सामान्य "
            "रूपमा कठोर हुन्छ: भारी अवधिले सडक र काममा थप सावधानीको प्रेरणा मात्र "
            "दिन्छ, अरू केही होइन। दुर्घटना रोक्ने भनेको सुरक्षित व्यवहार हो, "
            "कुण्डली होइन।"
        ),
    },
    # ---- Litigation -----------------------------------------------
    "litigation_legal_trouble": {
        "source": "classical",
        "source_label_en": "Classical KP horary rule",
        "source_label_ne": "शास्त्रीय केपी प्रश्न नियम",
        "method_en": (
            KP_METHOD_EN + " Trouble is read from disputes (6th) linked to "
            "confinement and loss (12th) and sudden trouble (8th), with "
            "Saturn as significator of restriction."
        ),
        "method_ne": (
            KP_METHOD_NE + " समस्या विवाद (छैटौँ) लाई बन्दी र हानि (बाह्रौँ) र "
            "आकस्मिक समस्या (आठौँ) सँग जोडेर, प्रतिबन्धका कारक शनिसहित पढिन्छ।"
        ),
        "favourable_en": (
            "The significators keep 6 contained with 9 and 11 supporting "
            "lawful resolution and gain: disputes settle without escalation, "
            "as a probability leaning only."
        ),
        "favourable_ne": (
            "कारकहरूले ९ र ११ को कानुनसम्मत समाधान र लाभको समर्थनसहित छैटौँलाई "
            "नियन्त्रणमा राख्छन्: विवाद बढ्नुबिना टुङ्गिन्छ, सम्भावना झुकावका रूपमा मात्र।"
        ),
        "unfavourable_en": (
            "The significators link 6 heavily to 12 and 8, or negate 2 and "
            "10 (resources, standing): a heavy pattern is a probability "
            "caution to seek legal advice early and act lawfully — it is "
            "not a prediction of imprisonment, and it is not legal advice."
        ),
        "unfavourable_ne": (
            "कारकहरूले छैटौँलाई बाह्रौँ र आठौँसँग बलियो गरी जोड्छन्, वा २ र १० "
            "(स्रोत, प्रतिष्ठा) नकार्छन्: भारी ढाँचा भनेको चाँडै कानुनी सल्लाह "
            "लिने र कानुनसम्मत व्यवहार गर्ने सम्भावना सावधानी मात्र हो — कैद हुन्छ "
            "भन्ने भविष्यवाणी होइन, र कानुनी सल्लाह होइन।"
        ),
    },
    "litigation_court_outcome": {
        "source": "template:1Tr76-M1aCBaExg7AJDjppirinfMBBCS_+classical",
        "source_label_en": "Legacy template: WINNING in LITIGATION, plus classical KP rule",
        "source_label_ne": "परम्परागत टेम्प्लेट: मुद्दामा जित, साथै शास्त्रीय केपी नियम",
        "method_en": (
            "The template gives the winning combinations plainly: the 6th "
            "and 11th houses appearing together in the relevant "
            "dasa-antardasa periods. Other combinations signifying a win "
            "are 1, 6, 10 and 11 together; 10 and 11 together; and 1, 6 and "
            "10 together. Classically the opposing party (7th) and fortune "
            "and justice (9th) are read alongside, with Jupiter as "
            "significator of justice — the win is a probability leaning "
            "only, never a decision of the case."
        ),
        "method_ne": (
            "टेम्प्लेटले जित्ने संयोजन स्पष्ट दिन्छ: सम्बन्धित दशा–अन्तर्दशा "
            "अवधिमा छैटौँ र एघारौँ भाव एकसाथ देखा पर्ने। जित सङ्केत गर्ने अन्य "
            "संयोजन १, ६, १० र ११ एकसाथ; १० र ११ एकसाथ; र १, ६ र १० एकसाथ हुन्। "
            "शास्त्रीय रूपमा विपक्षी (सातौँ) र भाग्य र न्याय (नवौँ) सँगै पढिन्छ, "
            "न्यायका कारक गुरुसहित — जित सम्भावना झुकाव मात्र हो, मुद्दाको फैसला "
            "कहिल्यै होइन।"
        ),
        "favourable_en": (
            "The dasa-antardasa running over the hearing dates activates 6 "
            "and 11 together (or 1, 6, 10, 11; or 10 and 11), with 9 and 2 "
            "supporting: a favourable leaning. Evidence and procedure "
            "still decide the case, and a lawyer must be consulted."
        ),
        "favourable_ne": (
            "सुनुवाइ मितिमा चलिरहेको दशा–अन्तर्दशाले ६ र ११ लाई एकसाथ (वा १, ६, "
            "१०, ११; वा १० र ११) सक्रिय पार्छ, ९ र २ ले समर्थन गर्छन्: अनुकूल "
            "झुकाव हुन्छ। प्रमाण र प्रक्रियाले नै मुद्दा निर्धारण गर्छ, र वकिलसँग "
            "परामर्श गर्नुपर्छ।"
        ),
        "unfavourable_en": (
            "The significators point to 12 and 8 (loss, sudden reversal) "
            "instead of 11: the leaning runs against the querent, and the "
            "case needs its lawyer's strategy, not the chart's comfort."
        ),
        "unfavourable_ne": (
            "कारकहरूले एघारौँको सट्टा १२ र ८ (हानि, आकस्मिक उल्टो) तर्फ सङ्केत "
            "गर्छन्: झुकाव प्रश्नकर्ताको विपक्षमा चल्छ, र मुद्दालाई कुण्डलीको "
            "सात्वनाभन्दा वकिलको रणनीति चाहिन्छ।"
        ),
        "timing_en": (
            "Judge the hearing dates themselves: the dasa-antardasa then "
            "running must carry the 6-and-11 combination on those dates, "
            "not merely somewhere in the year."
        ),
        "timing_ne": (
            "सुनुवाइ मिति आफैँलाई हेर्नुहोस्: त्यस बेला चलिरहेको दशा–अन्तर्दशाले "
            "ती मितिमा ६ र ११ को संयोजन बोक्नुपर्छ, वर्षमा कतै मात्र होइन।"
        ),
    },
    "health_serious_periods": {
        "source": "classical",
        "source_label_en": "Classical KP horary rule",
        "source_label_ne": "शास्त्रीय केपी प्रश्न नियम",
        "method_en": (
            KP_METHOD_EN + " Serious strain is traditionally read from the "
            "6th (illness), 8th (sudden or chronic difficulty) and 12th "
            "(hospitalisation, loss) against vitality (1st) and support "
            "(11th), with Saturn as significator of chronic strain."
        ),
        "method_ne": (
            KP_METHOD_NE + " गम्भीर तनाव परम्परागत रूपमा छैटौँ (रोग), आठौँ "
            "(आकस्मिक वा दीर्घकालीन कठिनाइ) र बाह्रौँ (अस्पताल, हानि) लाई "
            "जीवनशक्ति (पहिलो) र समर्थन (एघारौँ) सँग तुलना गरी, दीर्घकालीन तनावका "
            "कारक शनिसहित पढिन्छ।"
        ),
        "favourable_en": (
            "The significators keep 1 and 11 strong against 6, 8 and 12: "
            "no serious-strain period is indicated; ordinary check-ups and "
            "care suffice."
        ),
        "favourable_ne": (
            "कारकहरूले ६, ८ र १२ विरुद्ध पहिलो र एघारौँलाई बलियो राख्छन्: "
            "गम्भीर तनावको अवधि सङ्केत हुँदैन; सामान्य जाँच र हेरचाह पर्याप्त हुन्छ।"
        ),
        "unfavourable_en": (
            "The significators link 6, 8 and 12 heavily while 1 and 11 "
            "weaken: a probability prompt for check-ups and care — it does "
            "not diagnose any disease, name a condition, or time treatment; "
            "any symptom needs a clinician."
        ),
        "unfavourable_ne": (
            "कारकहरूले ६, ८ र १२ लाई बलियो गरी जोड्छन् र पहिलो र एघारौँ कमजोर "
            "हुन्छन्: जाँच र हेरचाहका लागि सम्भावना प्रेरणा हुन्छ — यसले कुनै रोग "
            "निदान गर्दैन, अवस्था तोक्दैन, वा उपचारको समय निर्धारण गर्दैन; कुनै पनि "
            "लक्षण चिकित्सककै हो।"
        ),
    },
}


PENDING_RULING = {
    "source": "pending",
    "source_label_en": "Full ruling pending",
    "source_label_ne": "पूर्ण निर्णय बाँकी छ",
    "note_en": (
        "A full traditional ruling for this question has not been added "
        "yet; the summary above is all that is available for now."
    ),
    "note_ne": (
        "यस प्रश्नको पूर्ण परम्परागत निर्णय अझै थपिएको छैन; माथिको सारांश "
        "मात्र अहिले उपलब्ध छ।"
    ),
}


def get_ruling(question_id):
    """Ruling dict for a question id, or the pending marker if absent."""
    ruling = RULINGS.get(question_id)
    if ruling is None:
        return dict(PENDING_RULING)
    return ruling
