"""Curated Life Questions library (Phase 1).

A browsable guide to reading a chart for a life question: which houses
are prime, which support, which negate, and which planet is the natural
significator. House logic is adapted from traditional (legacy Subjects)
templates, but all prose here is rewritten for this app.

This is a guide, not a verdict: no question is answered without a
chart, and nothing here is a guaranteed outcome, medical advice, or
legal advice.

Probability framing (per Samir, 2026-11-04): astrology here is a
traditional probability indication, not a deterministic fact. Entries
on sensitive topics — child sex indication, pregnancy difficulty,
relationship strain involving a third party, legal trouble /
imprisonment risk, court outcomes, and serious health periods — are
included on that basis only, each with its own disclaimer. Pregnancy
and health entries are not medical advice (see a clinician); legal
entries are not legal advice (see a lawyer); and no entry should be
used to accuse a specific person or to decide a medical or legal
matter on its own.
"""

from __future__ import annotations

DISCLAIMER_EN = (
    "Guidance only, not a guaranteed outcome. "
    "Health entries are not medical advice — see a clinician. "
    "For legal or financial decisions, consult a qualified professional."
)
DISCLAIMER_NE = (
    "यो मार्गदर्शन मात्र हो, निश्चित परिणाम होइन। "
    "स्वास्थ्यसम्बन्धी प्रविष्टिहरू चिकित्सकीय सल्लाह होइनन् — चिकित्सकसँग परामर्श गर्नुहोस्। "
    "कानुनी वा आर्थिक निर्णयका लागि योग्य विशेषज्ञसँग परामर्श गर्नुहोस्।"
)

# Houses are 1-based, as in the legacy templates (7H = 7th house).
QUESTIONS = [
    {
        "id": "marriage_timing",
        "category": "marriage", "category_en": "Marriage", "category_ne": "विवाह",
        "question_en": "When may marriage take place?",
        "question_ne": "विवाह कहिले हुन सक्छ?",
        "prime_houses": [7, 2, 11], "supporting_houses": [5, 9], "negating_houses": [1, 6, 10],
        "significator_en": "Venus", "significator_ne": "शुक्र",
        "what_to_check_en": "Check the 7th house (partnership), 2nd (family addition) and 11th (fulfilment). Venus as natural significator, plus the 7th lord and its star/sub lords, should support rather than negate these houses.",
        "what_to_check_ne": "सातौँ भाव (साझेदारी), दोस्रो (परिवार थप) र एघारौँ (पूर्ति) हेर्नुहोस्। प्राकृतिक कारक शुक्र तथा सातौँ भावका स्वामी र तिनका नक्षत्र/उपस्वामीले यी भावलाई समर्थन गर्नुपर्छ, नकार्नु हुँदैन।",
        "timing_note_en": "Timing is usually read from the running dasha/bhukti and transits touching the prime houses, not from a single planet alone.",
        "timing_note_ne": "समय सामान्यतया चलिरहेको दशा/भुक्ति र प्रमुख भावलाई छुने गोचरबाट पढिन्छ, एउटा ग्रहबाट मात्र होइन।",
    },
    {
        "id": "marriage_known_circle",
        "category": "marriage", "category_en": "Marriage", "category_ne": "विवाह",
        "question_en": "Marriage within a known circle?",
        "question_ne": "चिनजानकै घेराभित्र विवाह?",
        "prime_houses": [7, 2, 11], "supporting_houses": [3, 5], "negating_houses": [1, 6, 10],
        "significator_en": "Venus", "significator_ne": "शुक्र",
        "what_to_check_en": "Start from the marriage houses (7, 2, 11) and look for a link to the 3rd house (neighbours, close circle) or 5th (romance, acquaintance). A strong 3rd/5th link points to someone already known.",
        "what_to_check_ne": "विवाहका भाव (७, २, ११) बाट सुरु गरी तेस्रो भाव (छिमेक, नजिकको घेरा) वा पाँचौँ (प्रेम, चिनजान) सँगको सम्बन्ध हेर्नुहोस्। तेस्रो/पाँचौँसँग बलियो सम्बन्ध भए चिनेकै व्यक्तितर्फ सङ्केत हुन्छ।",
        "timing_note_en": "Check the same dasha/transit picture as for marriage timing; the circle is a flavour of the match, not a separate timing rule.",
        "timing_note_ne": "विवाहको समयजस्तै दशा/गोचर हेर्नुहोस्; घेरा भनेको जोडीको विशेषता मात्र हो, छुट्टै समय-नियम होइन।",
    },
    {
        "id": "marriage_abroad",
        "category": "marriage", "category_en": "Marriage", "category_ne": "विवाह",
        "question_en": "Marriage abroad, or with a foreigner?",
        "question_ne": "विदेशमा वा विदेशीसँग विवाह?",
        "prime_houses": [7, 9, 12], "supporting_houses": [2, 11], "negating_houses": [1, 6, 10],
        "significator_en": "Venus", "significator_ne": "शुक्र",
        "what_to_check_en": "Marriage (7th) linked to the 9th (long journey, foreign land) and 12th (foreign residence) houses suggests a foreign connection. The 2nd and 11th should still support the marriage itself.",
        "what_to_check_ne": "विवाह (सातौँ) सँग नवौँ (लामो यात्रा, विदेश) र बाह्रौँ (विदेश बसोबास) भाव जोडिए विदेशी सम्बन्धको सङ्केत हुन्छ। दोस्रो र एघारौँले भने विवाहलाई नै समर्थन गर्नुपर्छ।",
        "timing_note_en": "Foreign links are read alongside dasha and transits to the 9th/12th houses, not from a foreign planet alone.",
        "timing_note_ne": "विदेशी सम्बन्ध दशा र नवौँ/बाह्रौँ भावका गोचरसँगै पढिन्छ, विदेशी ग्रहबाट मात्र होइन।",
    },
    {
        "id": "marriage_remarriage",
        "category": "marriage", "category_en": "Marriage", "category_ne": "विवाह",
        "question_en": "Planning a second marriage?",
        "question_ne": "दोस्रो विवाहको योजना?",
        "prime_houses": [7, 2, 11], "supporting_houses": [9, 5], "negating_houses": [1, 6, 10],
        "significator_en": "Venus", "significator_ne": "शुक्र",
        "what_to_check_en": "Read this respectfully, as a fresh partnership: the usual marriage houses (7, 2, 11), with some traditions also looking at the 9th house for a subsequent marriage. Check that the earlier separation is fully settled in real life before any timing is read.",
        "what_to_check_ne": "यसलाई नयाँ साझेदारीका रूपमा सम्मानपूर्वक पढ्नुहोस्: सामान्य विवाह भाव (७, २, ११), केही परम्परामा पछिल्लो विवाहका लागि नवौँ भाव पनि हेरिन्छ। समय पढ्नुअघि अघिल्लो सम्बन्ध वास्तविक जीवनमा पूर्ण रूपमा टुङ्गिएको छ भन्ने सुनिश्चित गर्नुहोस्।",
        "timing_note_en": "Timing follows the same dasha/transit rules as a first marriage, judged on the current chart, not on the past alone.",
        "timing_note_ne": "समय पहिलो विवाहकै दशा/गोचर नियमले, वर्तमान कुण्डलीका आधारमा पढिन्छ, विगतबाट मात्र होइन।",
    },
    {
        "id": "education_exams",
        "category": "education", "category_en": "Education", "category_ne": "शिक्षा",
        "question_en": "Success in exams or interviews?",
        "question_ne": "परीक्षा वा अन्तर्वार्तामा सफलता?",
        "prime_houses": [4, 9, 11], "supporting_houses": [3, 6], "negating_houses": [8, 12],
        "significator_en": "Mercury", "significator_ne": "बुध",
        "what_to_check_en": "Check the 4th (learning) and 9th (higher study) houses, with the 11th for success. Mercury, plus effort houses 3rd and 6th (competition), should support them; 8th/12th links point to obstacles or distraction.",
        "what_to_check_ne": "चौथो (सिकाइ) र नवौँ (उच्च अध्ययन) भाव, सफलताका लागि एघारौँ हेर्नुहोस्। बुध तथा प्रयासका भाव तेस्रो र छैटौँ (प्रतिस्पर्धा) ले समर्थन गर्नुपर्छ; आठौँ/बाह्रौँको सम्बन्धले बाधा वा ध्यान भट्किने सङ्केत गर्छ।",
        "timing_note_en": "Exam periods are best judged by dasha/bhukti and Mercury transits at the exam date, alongside preparation.",
        "timing_note_ne": "परीक्षाको समय दशा/भुक्ति र परीक्षा मितिमा बुधको गोचरसँगै, तयारीलाई पनि ध्यान दिई पढिन्छ।",
    },
    {
        "id": "education_abroad",
        "category": "education", "category_en": "Education", "category_ne": "शिक्षा",
        "question_en": "Study abroad, or far from home?",
        "question_ne": "विदेश वा घरबाट टाढा अध्ययन?",
        "prime_houses": [9, 12, 4], "supporting_houses": [11, 3], "negating_houses": [1, 6],
        "significator_en": "Jupiter", "significator_ne": "गुरु",
        "what_to_check_en": "Higher study (9th) linked to the 12th (foreign residence) and away from the 4th (home) suggests study far from home. The 11th should support the wish being fulfilled.",
        "what_to_check_ne": "उच्च अध्ययन (नवौँ) सँग बाह्रौँ (विदेश बसोबास) जोडिए र चौथो (घर) बाट टाढा भए घरबाट टाढा अध्ययनको सङ्केत हुन्छ। एघारौँले इच्छा पूरा हुनेतर्फ समर्थन गर्नुपर्छ।",
        "timing_note_en": "Look at dasha/bhukti and transits to the 9th/12th houses around application and departure dates.",
        "timing_note_ne": "आवेदन र प्रस्थानको समयमा दशा/भुक्ति र नवौँ/बाह्रौँ भावका गोचर हेर्नुहोस्।",
    },
    {
        "id": "education_field",
        "category": "education", "category_en": "Education", "category_ne": "शिक्षा",
        "question_en": "Which field of study suits me?",
        "question_ne": "कुन विषय मलाई उपयुक्त हुन्छ?",
        "prime_houses": [4, 9, 10], "supporting_houses": [2, 11], "negating_houses": [6, 8],
        "significator_en": "Mercury", "significator_ne": "बुध",
        "what_to_check_en": "Compare the 4th/9th (study) with the 10th (vocation): the strongest significators among Mercury (analysis, commerce), Jupiter (teaching, law), Mars (engineering, medicine-adjacent skills) and Venus (arts, design) hint at the direction, in general terms only.",
        "what_to_check_ne": "चौथो/नवौँ (अध्ययन) लाई दशौँ (पेशा) सँग तुलना गर्नुहोस्: बुध (विश्लेषण, वाणिज्य), गुरु (शिक्षण, कानुन), मङ्गल (इन्जिनियरिङ, प्राविधिक सीप) र शुक्र (कला, डिजाइन) मध्ये बलिया कारकले सामान्य दिशा सङ्केत गर्छन्।",
        "timing_note_en": "This is a direction guide, not a timing question; weigh it with interests, aptitude and real options.",
        "timing_note_ne": "यो दिशा-मार्गदर्शन मात्र हो, समयको प्रश्न होइन; रुचि, क्षमता र वास्तविक विकल्पसँगै तौलनुहोस्।",
    },
    {
        "id": "career_job_change",
        "category": "career", "category_en": "Career", "category_ne": "पेशा",
        "question_en": "Should I change jobs?",
        "question_ne": "नोकरी परिवर्तन गर्नु पर्छ?",
        "prime_houses": [10, 6, 11], "supporting_houses": [2, 7], "negating_houses": [5, 12],
        "significator_en": "Saturn", "significator_ne": "शनि",
        "what_to_check_en": "Check the 10th (career), 6th (service) and 11th (gain). A change is supported when the running period links 10th to 6th/11th and to a new employer (7th as 'the other party'); 5th/12th links suggest loss or a break instead.",
        "what_to_check_ne": "दशौँ (पेशा), छैटौँ (सेवा) र एघारौँ (लाभ) हेर्नुहोस्। चलिरहेको अवधिले दशौँलाई छैटौँ/एघारौँ र नयाँ रोजगारदाता (सातौँ, 'अर्को पक्ष') सँग जोड्दा परिवर्तनलाई समर्थन हुन्छ; पाँचौँ/बाह्रौँको सम्बन्धले हानि वा अन्तराल सङ्केत गर्छ।",
        "timing_note_en": "Judge timing by dasha/bhukti touching the 10th/6th houses, and check notice periods and offers in real life first.",
        "timing_note_ne": "समय दशा/भुक्तिले दशौँ/छैटौँ भावलाई छुँदा पढिन्छ, र वास्तविक जीवनमा सूचना अवधि र प्रस्ताव पहिले हेर्नुहोस्।",
    },
    {
        "id": "career_business_vs_service",
        "category": "career", "category_en": "Career", "category_ne": "पेशा",
        "question_en": "Business or service (employment)?",
        "question_ne": "व्यापार कि सेवा (नोकरी)?",
        "prime_houses": [10, 7, 11], "supporting_houses": [2, 6], "negating_houses": [5, 9],
        "significator_en": "Mercury", "significator_ne": "बुध",
        "what_to_check_en": "Service leans on the 6th (employment); independent business leans on the 7th (dealings with others) with the 10th and 11th supporting gain. Compare which set the running period and the 10th lord favour.",
        "what_to_check_ne": "सेवामा छैटौँ (रोजगारी) बलियो हुन्छ; स्वतन्त्र व्यापारमा सातौँ (अरूसँगको कारोबार) सँग दशौँ र एघारौँले लाभलाई समर्थन गर्छन्। चलिरहेको अवधि र दशौँका स्वामीले कुन पक्षलाई साथ दिन्छन्, तुलना गर्नुहोस्।",
        "timing_note_en": "This is a leaning, not a verdict; capital, skills and market conditions matter as much as the chart.",
        "timing_note_ne": "यो झुकाव मात्र हो, फैसला होइन; पुँजी, सीप र बजारको अवस्था पनि उत्तिकै महत्त्वपूर्ण हुन्छ।",
    },
    {
        "id": "career_promotion_transfer",
        "category": "career", "category_en": "Career", "category_ne": "पेशा",
        "question_en": "Promotion or transfer — when?",
        "question_ne": "पदोन्नति वा सरुवा — कहिले?",
        "prime_houses": [10, 11, 6], "supporting_houses": [2, 3], "negating_houses": [5, 8],
        "significator_en": "Sun", "significator_ne": "सूर्य",
        "what_to_check_en": "Promotion reads from the 10th (status) and 11th (gain) with the 6th (service record); transfer adds the 3rd (movement, change of place). The Sun as significator of status should support, not negate, these houses.",
        "what_to_check_ne": "पदोन्नति दशौँ (पद) र एघारौँ (लाभ) सँग छैटौँ (सेवा अभिलेख) बाट पढिन्छ; सरुवामा तेस्रो (गतिविधि, ठाउँ परिवर्तन) थपिन्छ। पदका कारक सूर्यले यी भावलाई समर्थन गर्नुपर्छ, नकार्नु हुँदैन।",
        "timing_note_en": "Look for dasha/bhukti and transits linking 10th/11th around appraisal or transfer windows.",
        "timing_note_ne": "मूल्याङ्कन वा सरुवाको समयमा दशा/भुक्ति र दशौँ/एघारौँ भावका गोचर हेर्नुहोस्।",
    },
    {
        "id": "career_break",
        "category": "career", "category_en": "Career", "category_ne": "पेशा",
        "question_en": "A break in career — what to check?",
        "question_ne": "पेशामा अन्तराल — के हेर्ने?",
        "prime_houses": [10, 6], "supporting_houses": [12, 8], "negating_houses": [11, 2],
        "significator_en": "Saturn", "significator_ne": "शनि",
        "what_to_check_en": "A break shows when the running period links career houses (10th, 6th) to the 12th (loss, separation) or 8th (obstacle) and negates gain (11th, 2nd). Read it as a period to plan through, not as a permanent verdict.",
        "what_to_check_ne": "पेशाका भाव (दशौँ, छैटौँ) चलिरहेको अवधिमा बाह्रौँ (हानि, अलगाव) वा आठौँ (बाधा) सँग जोडिए र लाभ (एघारौँ, दोस्रो) नकारिए अन्तराल देखिन्छ। यसलाई योजना बनाउने अवधि ठान्नुहोस्, स्थायी फैसला होइन।",
        "timing_note_en": "Note when the interrupting period ends and which house the next period supports, for a return or a new direction.",
        "timing_note_ne": "बाधा पुर्याउने अवधि कहिले सकिन्छ र अर्को अवधिले कुन भावलाई समर्थन गर्छ, फर्कने वा नयाँ दिशा लागि हेर्नुहोस्।",
    },
    {
        "id": "travel_settling_abroad",
        "category": "travel", "category_en": "Travel", "category_ne": "यात्रा",
        "question_en": "Settling abroad?",
        "question_ne": "विदेशमा बसोबास?",
        "prime_houses": [12, 9, 4], "supporting_houses": [11, 3], "negating_houses": [1, 6],
        "significator_en": "Moon", "significator_ne": "चन्द्रमा",
        "what_to_check_en": "Foreign residence (12th) with long travel (9th), away from home (4th), supported by fulfilment (11th) and movement (3rd), points to settling abroad. The Moon as significator of movement and residence is also checked.",
        "what_to_check_ne": "विदेश बसोबास (बाह्रौँ) सँग लामो यात्रा (नवौँ), घर (चौथो) बाट टाढा, पूर्ति (एघारौँ) र गतिविधि (तेस्रो) ले समर्थन गर्दा विदेशमा बसोबासको सङ्केत हुन्छ। गतिविधि र बसोबासका कारक चन्द्रमा पनि हेरिन्छ।",
        "timing_note_en": "Timing follows dasha/bhukti and transits to the 12th/9th houses, alongside visas and practical plans.",
        "timing_note_ne": "समय दशा/भुक्ति र बाह्रौँ/नवौँ भावका गोचरले, भिसा र व्यावहारिक योजनासँगै पढिन्छ।",
    },
    {
        "id": "travel_return_home",
        "category": "travel", "category_en": "Travel", "category_ne": "यात्रा",
        "question_en": "Returning home from abroad?",
        "question_ne": "विदेशबाट घर फर्कने?",
        "prime_houses": [4, 12, 9], "supporting_houses": [11, 2], "negating_houses": [6, 8],
        "significator_en": "Moon", "significator_ne": "चन्द्रमा",
        "what_to_check_en": "Return reads as home (4th) becoming strong again after a foreign period (12th, 9th), with the 11th and 2nd supporting a settled return rather than a forced one.",
        "what_to_check_ne": "फर्काइ विदेशी अवधि (बाह्रौँ, नवौँ) पछि घर (चौथो) फेरि बलियो हुँदा पढिन्छ, एघारौँ र दोस्रोले बाध्यात्मक होइन, व्यवस्थित फिर्ती लाई समर्थन गर्नुपर्छ।",
        "timing_note_en": "Check dasha/bhukti and transits to the 4th house around planned return dates.",
        "timing_note_ne": "योजनाबद्ध फिर्ती मितिमा दशा/भुक्ति र चौथो भावका गोचर हेर्नुहोस्।",
    },
    {
        "id": "children_timing_general",
        "category": "children", "category_en": "Children", "category_ne": "सन्तान",
        "question_en": "Children — timing and obstacles, in general terms?",
        "question_ne": "सन्तान — समय र बाधा, सामान्य रूपमा?",
        "prime_houses": [5, 2, 11], "supporting_houses": [9, 7], "negating_houses": [1, 6, 10],
        "significator_en": "Jupiter", "significator_ne": "गुरु",
        "what_to_check_en": "Check the 5th (children), 2nd (family addition) and 11th (fulfilment), with Jupiter as significator. This entry covers timing and obstacles only, in general terms; it makes no prediction about a child's sex or number, and medical questions belong to a clinician.",
        "what_to_check_ne": "पाँचौँ (सन्तान), दोस्रो (परिवार थप) र एघारौँ (पूर्ति) हेर्नुहोस्, कारक गुरु हुन्। यो प्रविष्टिले समय र बाधा मात्र, सामान्य रूपमा समेट्छ; सन्तानको सङ्ख्या वा लिङ्गबारे कुनै दाबी गर्दैन, र चिकित्सकीय प्रश्न चिकित्सककै हो।",
        "timing_note_en": "Timing is read from dasha/bhukti touching the 5th house; delays point to the negating houses to be worked through, not to a fixed outcome.",
        "timing_note_ne": "समय पाँचौँ भावलाई छुने दशा/भुक्तिबाट पढिन्छ; ढिलाइले नकार्ने भावलाई समाधान गर्नुपर्ने देखाउँछ, निश्चित परिणाम होइन।",
    },
    {
        "id": "property_buying",
        "category": "property", "category_en": "Property", "category_ne": "सम्पत्ति",
        "question_en": "Buying property — is the time favourable?",
        "question_ne": "सम्पत्ति किन्ने — समय अनुकूल छ?",
        "prime_houses": [4, 11, 12], "supporting_houses": [2, 9], "negating_houses": [6, 8],
        "significator_en": "Mars", "significator_ne": "मङ्गल",
        "what_to_check_en": "Property (4th) with gain (11th) and investment (12th), supported by resources (2nd) and fortune (9th), favours a purchase. Mars as significator of land/property is also checked; titles, loans and prices must still be verified in real life.",
        "what_to_check_ne": "सम्पत्ति (चौथो) सँग लाभ (एघारौँ) र लगानी (बाह्रौँ), स्रोत (दोस्रो) र भाग्य (नवौँ) ले समर्थन गर्दा खरिद अनुकूल हुन्छ। जग्गा/सम्पत्तिका कारक मङ्गल पनि हेरिन्छ; लालपुर्जा, ऋण र मूल्य वास्तविक जीवनमा नै जाँच्नुपर्छ।",
        "timing_note_en": "Read timing from dasha/bhukti to the 4th/11th houses, and from a favourable Muhurta for registration if one is sought.",
        "timing_note_ne": "समय चौथो/एघारौँ भावका दशा/भुक्तिबाट, र दर्ताका लागि अनुकूल मुहूर्त खोजिए त्यसबाट पनि पढिन्छ।",
    },
    {
        "id": "property_sale_timing",
        "category": "property", "category_en": "Property", "category_ne": "सम्पत्ति",
        "question_en": "Selling property — timing, and rental income?",
        "question_ne": "सम्पत्ति बेच्ने — समय, र भाडा आम्दानी?",
        "prime_houses": [4, 10, 3], "supporting_houses": [11, 2], "negating_houses": [6, 12],
        "significator_en": "Mars", "significator_ne": "मङ्गल",
        "what_to_check_en": "Sale reads from property (4th) through action (10th) and change (3rd), with gain (11th) and resources (2nd) supporting it. Rental income is a related general check: the 4th with the 11th and 2nd supporting steady gain, without promising a rent figure.",
        "what_to_check_ne": "बिक्री सम्पत्ति (चौथो) बाट कार्य (दशौँ) र परिवर्तन (तेस्रो) हुँदै, लाभ (एघारौँ) र स्रोत (दोस्रो) ले समर्थन गर्दा पढिन्छ। भाडा आम्दानी सम्बन्धित सामान्य जाँच हो: चौथोसँग एघारौँ र दोस्रोले स्थिर लाभलाई समर्थन गर्ने, भाडा रकमको प्रतिज्ञा नगरी।",
        "timing_note_en": "Timing follows dasha/bhukti to the 4th/10th houses; market price and buyer readiness still decide the sale.",
        "timing_note_ne": "समय चौथो/दशौँ भावका दशा/भुक्तिले पढिन्छ; बजार मूल्य र क्रेताको तयारीले नै बिक्री निर्धारण गर्छ।",
    },
    {
        "id": "vehicle_buying",
        "category": "vehicle", "category_en": "Vehicle", "category_ne": "सवारी",
        "question_en": "Buying a vehicle — what to check?",
        "question_ne": "सवारी किन्ने — के हेर्ने?",
        "prime_houses": [4, 11, 12], "supporting_houses": [2, 9], "negating_houses": [6, 8],
        "significator_en": "Venus", "significator_ne": "शुक्र",
        "what_to_check_en": "Vehicles are read from the 4th (conveyance) with gain (11th) and outlay (12th), supported by resources (2nd). Venus as significator of comfort/vehicles is checked; condition, papers and loan terms must still be verified in real life.",
        "what_to_check_ne": "सवारी चौथो (यातायात) बाट लाभ (एघारौँ) र खर्च (बाह्रौँ) सँग, स्रोत (दोस्रो) ले समर्थन गर्दा पढिन्छ। सुविधा/सवारीका कारक शुक्र हेरिन्छ; अवस्था, कागजात र ऋणका सर्त वास्तविक जीवनमा नै जाँच्नुपर्छ।",
        "timing_note_en": "Timing follows dasha/bhukti to the 4th/11th houses, and a vehicle Muhurta if one is sought.",
        "timing_note_ne": "समय चौथो/एघारौँ भावका दशा/भुक्तिबाट, र सवारी मुहूर्त खोजिए त्यसबाट पनि पढिन्छ।",
    },
    {
        "id": "vehicle_sale_loan",
        "category": "vehicle", "category_en": "Vehicle", "category_ne": "सवारी",
        "question_en": "Selling a vehicle, or repaying its loan?",
        "question_ne": "सवारी बेच्ने, वा त्यसको ऋण तिर्ने?",
        "prime_houses": [4, 6, 11], "supporting_houses": [2, 10], "negating_houses": [8, 12],
        "significator_en": "Mercury", "significator_ne": "बुध",
        "what_to_check_en": "Sale and loan-repayment both touch the 4th (vehicle) and 6th (loan/obligation) with gain (11th) supporting a clean settlement. Check the 2nd for resources to repay, and confirm the loan statement and buyer papers in real life.",
        "what_to_check_ne": "बिक्री र ऋण-भुक्तानी दुवैमा सवारी (चौथो) र छैटौँ (ऋण/दायित्व) सँग लाभ (एघारौँ) ले सफा फर्स्योटलाई समर्थन गर्नुपर्छ। भुक्तानीका लागि स्रोत (दोस्रो) हेर्नुहोस्, र ऋण विवरण तथा क्रेता कागजात वास्तविक जीवनमा पुष्टि गर्नुहोस्।",
        "timing_note_en": "Timing follows dasha/bhukti to the 4th/6th houses; the loan schedule itself sets the repayment dates.",
        "timing_note_ne": "समय चौथो/छैटौँ भावका दशा/भुक्तिले पढिन्छ; ऋण तालिकाले नै भुक्तानी मिति निर्धारण गर्छ।",
    },
    {
        "id": "health_general",
        "category": "health", "category_en": "Health", "category_ne": "स्वास्थ्य",
        "question_en": "General wellbeing — what to check?",
        "question_ne": "सामान्य स्वास्थ्य — के हेर्ने?",
        "prime_houses": [1, 6, 11], "supporting_houses": [2, 9], "negating_houses": [8, 12],
        "significator_en": "Sun", "significator_ne": "सूर्य",
        "what_to_check_en": "This is a general wellbeing check only, not medical advice: the 1st (body/vitality), 6th (health routines) and 11th (recovery/support), with the Sun as significator of vitality. It does not diagnose, predict disease, or time treatment — any health concern needs a clinician.",
        "what_to_check_ne": "यो सामान्य स्वास्थ्य जाँच मात्र हो: पहिलो (शरीर/जीवनशक्ति), छैटौँ (स्वास्थ्य दिनचर्या) र एघारौँ (सुधार/समर्थन), जीवनशक्तिका कारक सूर्यसहित। यसले रोग निदान गर्दैन, रोगको भविष्यवाणी गर्दैन, वा उपचारको समय तोक्दैन — कुनै पनि स्वास्थ्य चिन्ता चिकित्सककै हो।",
        "timing_note_en": "Read wellbeing periods from dasha/bhukti to the 1st/6th houses, as a prompt for rest, routine and check-ups — not as medical timing.",
        "timing_note_ne": "स्वास्थ्य अवधि पहिलो/छैटौँ भावका दशा/भुक्तिबाट, आराम, दिनचर्या र जाँचका लागि प्रेरणाका रूपमा पढिन्छ — चिकित्सकीय समयका रूपमा होइन।",
    },
    {
        "id": "general_accident_caution",
        "category": "general", "category_en": "General", "category_ne": "सामान्य",
        "question_en": "Accidents — general caution only?",
        "question_ne": "दुर्घटना — सामान्य सावधानी मात्र?",
        "prime_houses": [8, 12, 6], "supporting_houses": [1, 11], "negating_houses": [2, 9],
        "significator_en": "Mars", "significator_ne": "मङ्गल",
        "what_to_check_en": "This entry is general caution only, never a personal accident prediction. Traditionally, the 8th (sudden events), 12th (loss) and 6th (injury/obstacle) are checked against vitality (1st) and support (11th); a heavy period is a prompt for extra care on the road and at work, nothing more.",
        "what_to_check_ne": "यो प्रविष्टि सामान्य सावधानी मात्र हो, व्यक्तिगत दुर्घटनाको भविष्यवाणी कहिल्यै होइन। परम्परागत रूपमा आठौँ (आकस्मिक घटना), बाह्रौँ (हानि) र छैटौँ (चोट/बाधा) लाई जीवनशक्ति (पहिलो) र समर्थन (एघारौँ) सँग तुलना गरिन्छ; भारी अवधिले सडक र काममा थप सावधानीको प्रेरणा मात्र दिन्छ, अरू केही होइन।",
        "timing_note_en": "Caution periods are read from dasha/bhukti and Mars transits in general terms; safe behaviour, not the chart, prevents accidents.",
        "timing_note_ne": "सावधानी अवधि दशा/भुक्ति र मङ्गलको गोचरबाट सामान्य रूपमा पढिन्छ; दुर्घटना रोक्ने भनेको सुरक्षित व्यवहार हो, कुण्डली होइन।",
    },
    {
        "id": "children_sex_indication",
        "category": "children", "category_en": "Children", "category_ne": "सन्तान",
        "question_en": "Child — traditional sex indication, as probability only?",
        "question_ne": "सन्तान — परम्परागत लिङ्ग सङ्केत, सम्भावनाका रूपमा मात्र?",
        "prime_houses": [5, 2, 11], "supporting_houses": [9, 7], "negating_houses": [1, 6, 10],
        "significator_en": "Jupiter", "significator_ne": "गुरु",
        "what_to_check_en": "Traditional lore reads male/female indications from the 5th house, its lord, and the planets/signs involved (Sun, Mars and Jupiter traditionally counted as male; Moon and Venus as female), together with the 2nd and 11th. This is a probability indication from tradition only — it is not reliable, it is not a medical determination, and it must not be used on its own for any medical decision.",
        "what_to_check_ne": "परम्परागत ज्ञानले पाँचौँ भाव, त्यसका स्वामी र संलग्न ग्रह/राशिबाट पुरुष/स्त्री सङ्केत पढ्छ (सूर्य, मङ्गल र गुरु परम्परागत रूपमा पुरुष; चन्द्रमा र शुक्र स्त्री), दोस्रो र एघारौँसँगै। यो परम्परागत सम्भावना सङ्केत मात्र हो — भरपर्दो होइन, चिकित्सकीय निर्धारण होइन, र कुनै चिकित्सकीय निर्णयका लागि एक्लै प्रयोग गर्नु हुँदैन।",
        "timing_note_en": "Read only from dasha/bhukti touching the 5th house, and always as 'leaning, not certain'.",
        "timing_note_ne": "पाँचौँ भावलाई छुने दशा/भुक्तिबाट मात्र, र सधैँ 'झुकाव, निश्चित होइन' भनेर पढ्नुहोस्।",
    },
    {
        "id": "children_pregnancy_difficulty",
        "category": "children", "category_en": "Children", "category_ne": "सन्तान",
        "question_en": "Pregnancy — difficulty or loss risk, in traditional probability terms?",
        "question_ne": "गर्भावस्था — कठिनाइ वा हानिको जोखिम, परम्परागत सम्भावनाका रूपमा?",
        "prime_houses": [5, 2, 11], "supporting_houses": [9, 11], "negating_houses": [8, 12, 6],
        "significator_en": "Moon", "significator_ne": "चन्द्रमा",
        "what_to_check_en": "Traditional reading looks at the 5th house against the 8th (sudden difficulty), 12th (loss) and 6th (health obstacle), with the Moon as significator of pregnancy. A heavy indication is a probability prompt for extra medical care and rest — it is not a diagnosis, not a prediction of loss, and any pregnancy concern must go to a clinician promptly.",
        "what_to_check_ne": "परम्परागत पठनले पाँचौँ भावलाई आठौँ (आकस्मिक कठिनाइ), बाह्रौँ (हानि) र छैटौँ (स्वास्थ्य बाधा) सँग तुलना गर्छ, गर्भावस्थाका कारक चन्द्रमासहित। भारी सङ्केत भनेको थप चिकित्सकीय हेरचाह र आरामका लागि सम्भावना प्रेरणा मात्र हो — निदान होइन, हानि हुन्छ भन्ने भविष्यवाणी होइन, र गर्भावस्थाको कुनै पनि चिन्ता तुरुन्त चिकित्सककहाँ लैजानुपर्छ।",
        "timing_note_en": "Read difficulty periods from dasha/bhukti to the 5th/8th houses; medical timing and care always follow the clinician, not the chart.",
        "timing_note_ne": "कठिनाइ अवधि पाँचौँ/आठौँ भावका दशा/भुक्तिबाट पढिन्छ; चिकित्सकीय समय र हेरचाह सधैँ चिकित्सककै हुन्छ, कुण्डलीको होइन।",
    },
    {
        "id": "marriage_relationship_strain",
        "category": "marriage", "category_en": "Marriage", "category_ne": "विवाह",
        "question_en": "Relationship strain, including a third party?",
        "question_ne": "सम्बन्धमा तनाव, तेस्रो पक्षसहित?",
        "prime_houses": [7, 5, 12], "supporting_houses": [3, 11], "negating_houses": [1, 6, 10],
        "significator_en": "Venus", "significator_ne": "शुक्र",
        "what_to_check_en": "Strain is read from the 7th (partnership) against the 5th (romance) and 12th (secrecy, separation), with Venus as significator. A third-party indication is a probability pattern in the chart, in general terms — it is not proof about any specific person, and it should prompt conversation and counselling, not an accusation.",
        "what_to_check_ne": "तनाव सातौँ (साझेदारी) लाई पाँचौँ (प्रेम) र बाह्रौँ (गोप्यता, अलगाव) सँग तुलना गरी पढिन्छ, कारक शुक्रसहित। तेस्रो पक्षको सङ्केत कुण्डलीमा सामान्य सम्भावना ढाँचा मात्र हो — कुनै विशेष व्यक्तिबारे प्रमाण होइन, र यसले संवाद र परामर्शतर्फ प्रेरणा दिनुपर्छ, आरोप होइन।",
        "timing_note_en": "Strain periods follow dasha/bhukti to the 7th/12th houses; how a couple responds in real life matters more than the period itself.",
        "timing_note_ne": "तनाव अवधि सातौँ/बाह्रौँ भावका दशा/भुक्तिले पढिन्छ; दम्पतीले वास्तविक जीवनमा कसरी प्रतिक्रिया दिन्छन्, त्यो अवधिभन्दा महत्त्वपूर्ण हुन्छ।",
    },
    {
        "id": "litigation_legal_trouble",
        "category": "litigation", "category_en": "Litigation", "category_ne": "मुद्दा",
        "question_en": "Legal trouble or imprisonment risk, in traditional probability terms?",
        "question_ne": "कानुनी समस्या वा कैदको जोखिम, परम्परागत सम्भावनाका रूपमा?",
        "prime_houses": [6, 12, 8], "supporting_houses": [9, 11], "negating_houses": [2, 10],
        "significator_en": "Saturn", "significator_ne": "शनि",
        "what_to_check_en": "Traditional reading links disputes (6th) to confinement/loss (12th) and sudden trouble (8th), with Saturn as significator of restriction. A heavy pattern is a probability caution to seek legal advice early and act lawfully — it is not a prediction of imprisonment, and it is not legal advice.",
        "what_to_check_ne": "परम्परागत पठनले विवाद (छैटौँ) लाई बन्दी/हानि (बाह्रौँ) र आकस्मिक समस्या (आठौँ) सँग जोड्छ, प्रतिबन्धका कारक शनिसहित। भारी ढाँचा भनेको चाँडै कानुनी सल्लाह लिने र कानुनसम्मत व्यवहार गर्ने सम्भावना सावधानी मात्र हो — कैद हुन्छ भन्ने भविष्यवाणी होइन, र कानुनी सल्लाह होइन।",
        "timing_note_en": "Risk periods follow dasha/bhukti to the 6th/12th houses; the actual outcome depends on facts, law and counsel, not the chart alone.",
        "timing_note_ne": "जोखिम अवधि छैटौँ/बाह्रौँ भावका दशा/भुक्तिले पढिन्छ; वास्तविक परिणाम तथ्य, कानुन र वकिलमा निर्भर हुन्छ, कुण्डलीमा मात्र होइन।",
    },
    {
        "id": "litigation_court_outcome",
        "category": "litigation", "category_en": "Litigation", "category_ne": "मुद्दा",
        "question_en": "Court case — favourable outcome, as probability?",
        "question_ne": "अदालतको मुद्दा — अनुकूल परिणाम, सम्भावनाका रूपमा?",
        "prime_houses": [6, 7, 11], "supporting_houses": [9, 2], "negating_houses": [12, 8],
        "significator_en": "Jupiter", "significator_ne": "गुरु",
        "what_to_check_en": "A case is read from disputes (6th) and the opposing party (7th) with gain (11th) and fortune/justice (9th) supporting a favourable leaning, and Jupiter as significator of justice. This is a probability leaning only — it does not decide a case, and a lawyer must be consulted for the actual matter.",
        "what_to_check_ne": "मुद्दा विवाद (छैटौँ) र विपक्षी (सातौँ) बाट लाभ (एघारौँ) र भाग्य/न्याय (नवौँ) ले अनुकूल झुकावलाई समर्थन गर्दा पढिन्छ, न्यायका कारक गुरुसहित। यो सम्भावना झुकाव मात्र हो — यसले मुद्दा निर्धारण गर्दैन, र वास्तविक विषयका लागि वकिलसँग परामर्श गर्नुपर्छ।",
        "timing_note_en": "Favourable periods follow dasha/bhukti to the 6th/7th/11th houses around hearing dates; evidence and procedure still decide the case.",
        "timing_note_ne": "अनुकूल अवधि सुनुवाइ मितिमा छैटौँ/सातौँ/एघारौँ भावका दशा/भुक्तिले पढिन्छ; प्रमाण र प्रक्रियाले नै मुद्दा निर्धारण गर्छ।",
    },
    {
        "id": "health_serious_periods",
        "category": "health", "category_en": "Health", "category_ne": "स्वास्थ्य",
        "question_en": "Serious health periods, in traditional probability terms?",
        "question_ne": "गम्भीर स्वास्थ्य अवधि, परम्परागत सम्भावनाका रूपमा?",
        "prime_houses": [6, 8, 12], "supporting_houses": [1, 11], "negating_houses": [2, 9],
        "significator_en": "Saturn", "significator_ne": "शनि",
        "what_to_check_en": "Serious health strain is traditionally read from the 6th (illness), 8th (sudden/chronic difficulty) and 12th (hospitalisation/loss) against vitality (1st) and support (11th), with Saturn as significator of chronic strain. This is a probability prompt for check-ups and care — it does not diagnose any disease, name a condition, or time treatment; any symptom needs a clinician.",
        "what_to_check_ne": "गम्भीर स्वास्थ्य तनाव परम्परागत रूपमा छैटौँ (रोग), आठौँ (आकस्मिक/दीर्घकालीन कठिनाइ) र बाह्रौँ (अस्पताल/हानि) लाई जीवनशक्ति (पहिलो) र समर्थन (एघारौँ) सँग तुलना गरी पढिन्छ, दीर्घकालीन तनावका कारक शनिसहित। यो जाँच र हेरचाहका लागि सम्भावना प्रेरणा मात्र हो — यसले कुनै रोग निदान गर्दैन, अवस्था तोक्दैन, वा उपचारको समय निर्धारण गर्दैन; कुनै पनि लक्षण चिकित्सककै हो।",
        "timing_note_en": "Strain periods follow dasha/bhukti to the 6th/8th houses; medical decisions always follow the clinician, not the chart.",
        "timing_note_ne": "तनाव अवधि छैटौँ/आठौँ भावका दशा/भुक्तिले पढिन्छ; चिकित्सकीय निर्णय सधैँ चिकित्सककै हुन्छ, कुण्डलीको होइन।",
    },
]


def categories():
    """Category slugs in first-appearance order, with EN+NE labels."""
    seen = {}
    for q in QUESTIONS:
        seen.setdefault(q["category"], (q["category_en"], q["category_ne"]))
    return [
        {"slug": slug, "en": en, "ne": ne}
        for slug, (en, ne) in seen.items()
    ]


def list_questions(category=None):
    """All questions, optionally filtered by category slug."""
    if category is None:
        return list(QUESTIONS)
    wanted = str(category).strip().lower()
    return [q for q in QUESTIONS if q["category"] == wanted]


def get_question(question_id):
    for q in QUESTIONS:
        if q["id"] == question_id:
            return q
    return None


def to_public(q):
    """Public record shape: house lists + bilingual text + disclaimer."""
    return {
        "id": q["id"],
        "category": q["category"],
        "category_en": q["category_en"],
        "category_ne": q["category_ne"],
        "question_en": q["question_en"],
        "question_ne": q["question_ne"],
        "prime_houses": q["prime_houses"],
        "supporting_houses": q["supporting_houses"],
        "negating_houses": q["negating_houses"],
        "significator_en": q["significator_en"],
        "significator_ne": q["significator_ne"],
        "what_to_check_en": q["what_to_check_en"],
        "what_to_check_ne": q["what_to_check_ne"],
        "timing_note_en": q["timing_note_en"],
        "timing_note_ne": q["timing_note_ne"],
        "disclaimer_en": DISCLAIMER_EN,
        "disclaimer_ne": DISCLAIMER_NE,
    }
