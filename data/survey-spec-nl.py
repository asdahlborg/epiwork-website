
class RepQ01(d.Question):
    question = 'Heeft u een van de volgende symptomen gehad afgelopen week?'
    type = 'options-multiple'
    blank = True
    options = (
        (0, 'Loopneus'),
        (1, 'Stuffy nose'),
        (2, 'Hacking cough'),
        (3, 'Dry cough'),
        (4, 'Sneezing'),
        (5, 'Sore throat'),
        (6, 'Muscle pain'),
        (7, 'Headache'),
        (8, 'Chest pain'),
        (9, 'Feeling exhausted'),
        (10, 'Feeling tired'),
        (11, 'Loss of appetite'),
        (12, 'Nausea'),
        (13, 'Vomiting'),
        (14, 'Diarrhoea'),
        (15, 'Watery, bloodshot eyes'),
        (16, 'Chills and feverish feeling'),
        (17, 'Coloured sputum'),
    )

class RepQ02(d.Question):
    question = 'When did these symptoms started?'
    type = 'date'

class RepQ03(d.Question):
    question = 'Did you have fever? If yes, what was the highest temperature measured? Please estimate if you had fever, but did not measure.'
    type = 'options-single'
    options = (
        (0, 'No'),
        (360, 'Less than 37°C'),
        (370, '37° - 37.5°C'),
        (375, '37.5° - 38°C'),
        (380, '38° - 38.5°C'),
        (385, '38.5° - 39°C'),
        (390, '39° - 39.5°C'),
        (395, '39.5° - 40°C'),
        (400, 'More than 40°C'),
    )

class RepQ04(d.Question):
    question = 'When was your temperature for the first time above 38°C?'
    type = 'date'

class RepQ05(d.Question):
    question = 'Did these symptoms develop abruptly with sudden high fever or chills?'
    type = 'options-single'
    options = (
        (0, 'No'),
        (1, 'Yes'),
        (2, "Don't know"),
    )

class RepQ06(d.Question):
    question = 'Did you consult a medical doctor for these symptoms?'
    type = 'options-single'
    options = (
        (0, 'No'),
        (1, 'Yes'),
    )

class RepQ07(d.Question):
    question = 'Did you take medication for these symptoms?'
    type = 'options-single'
    options = (
        (0, 'Tamiflu, Relenza, or another anti viral drug'),
        (1, 'Antibiotics'),
        (2, 'Antipyretics'),
        (3, 'Anti-inflammatory drugs'),
        (4, 'Vitamins'),
        (5, 'Other'),
    )

class RepQ08(d.Question):
    question = 'Did you change your occupations due to these symptoms?'
    type = 'options-single'
    options = (
        (0, 'No'),
        (1, 'Yes, I staid at home'),
        (2, 'Yes, but went to work/school as usual'),
        (3, 'I staid at home, but was able to work'),
    )

class RepQ09(d.Question):
    question = 'How long did you staid at home?'
    type = 'options-single'
    options = (
        (1, '1 day'),
        (2, '2 days'),
        (3, '3 days'),
        (4, '4 days'),
        (5, '5 days'),
        (6, '6 days'),
        (7, '1 week'),
        (14, 'Less than 2 weeks'),
        (21, 'Less than 3 weeks'),
        (22, 'More than 3 weeks'),
    )

class RepQ10(d.Question):
    question = 'Do other people from your family/home have/had comparable symptoms?'
    type = 'options-single'
    options = (
        (0, 'No'),
        (1, 'Yes'),
    )

class RepQ11(d.Question):
    question = 'According to our data you did not receive a seasonal flu vaccination?'
    type = 'options-single'
    options = (
        (1, 'Yes'),
        (0, 'No, meanwhile I have received a seasonal flu vaccination'),
    )

class RepQ12(d.Question):
    question = 'According to our data you did not receive a Mexican flu vaccination?'
    type = 'options-single'
    options = (
        (1, 'Yes'),
        (0, 'No, meanwhile I have received a Mexican flu vaccination'),
    )

class Survey(d.Survey):
    id = 'dev-survey-nl-0.0'
    rules = (
        RepQ01,
        { (RepQ01, 'is-not', d.Empty) : (
            RepQ02,
            RepQ03,
            RepQ04,
            RepQ05,
            RepQ06,
            RepQ07,
            RepQ08,
            { (RepQ08, 'is-in', d.Items(1, 3)) : (
                RepQ09
            ) },
            RepQ10,
            { (d.Profile('RegQ5'), 'is-not', 1) : (
                RepQ11
            ) },
            { (d.Profile('RegQ6'), 'is-not', 1) : (
                RepQ12
            ) },
        ) }
    )

