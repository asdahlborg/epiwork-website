# -*- coding: utf-8 -*-

from epiweb.apps.survey import definitions as d
_ = lambda x: x

class RepQ01(d.Question):
    question = _('Did you have one or more of the following symptoms since your last visit?')
    type = 'option-multiple'
    options = (
        _('Runny nose'),
        _('Stuffy nose'),
        _('Hacking cough'),
        _('Dry cough'),
        _('Sneezing'),
        _('Sore throat'),
        _('Muscle pain'),
        _('Headache'),
        _('Chest pain'),
        _('Feeling exhausted'),
        _('Feeling tired'),
        _('Loss of appetite'),
        _('Nausea'),
        _('Vomiting'),
        _('Diarrhoea'),
        _('Watery, bloodshot eyes'),
        _('Chills and feverish feeling'),
        _('Coloured sputum'),
    )

class RepQ02(d.Question):
    question = _('When did these symptoms started?')
    type = 'date'

class RepQ03(d.Question):
    question = _('Did you have fever? If yes, what was the highest temperature measured? Please estimate if you had fever, but did not measure.')
    type = 'option-single'
    options = (
        _('No'),
        _('Less than 37°C'),
        _('37°C'),
        _('37° - 37.5°C'),
        _('37.5° - 38°C'),
        _('38°'),
        _('38.5°C'),
        _('38.5° - 39°C'),
        _('39° - 39.5°C'),
        _('39.5° - 40°C'),
        _('More than 40°C'),
    )

class RepQ04(d.Question):
    question = _('When was your temperature for the first time above 38°C?')
    type = 'date'

class RepQ05(d.Question):
    question = _('Did these symptoms develop abruptly with sudden high fever or chills?')
    type = 'option-single'
    options = (
        _('No'),
        _('Yes'),
        _("Don't know"),
    )

class RepQ06(d.Question):
    question = _('Did you consult a medical doctor for these symptoms?')
    type = 'option-single'
    options = ('No', 'Yes')

class RepQ07(d.Question):
    question = _('Did you take medication for these symptoms?')
    type = 'option-single'
    options = (
        _('Tamiflu, Relenza, or another anti viral drug'),
        _('Antibiotics'),
        _('Antipyretics'),
        _('Anti-inflammatory drugs'),
        _('Vitamins'),
        _('Other'),
    )

class RepQ08(d.Question):
    question = _('Did you change your occupations due to these symptoms?')
    type = 'option-single'
    options = (
        _('No'),
        _('Yes, I staid at home'),
        _('Yes, but went to work/school as usual'),
        _('I staid at home, but was able to work'),
    )

class RepQ09(d.Question):
    question = _('How long did you staid at home?')
    type = 'option-single'
    options = (
        _('1 day'),
        _('2 days'),
        _('3 days'),
        _('4 days'),
        _('5 days'),
        _('6 days'),
        _('1 week'),
        _('Less than 2 weeks'),
        _('Less than 3 weeks'),
        _('More than 3 weeks'),
    )

class RepQ10(d.Question):
    question = _('Do other people from your family/home have/had comparable symptoms?')
    type = 'option-single'
    options = ('No', 'Yes')

class RepQ11(d.Question):
    question = _('According to our data you did not receive a seasonal flu vaccination?')
    type = 'option-single'
    options = (
        _('Yes'),
        _('No, meanwhile I have received a seasonal flu vaccination'),
    )

class RepQ12(d.Question):
    question = _('According to our data you did not receive a Mexican flu vaccination?')
    type = 'option-single'
    options = (
        _('Yes'),
        _('No, meanwhile I have received a Mexican flu vaccination'),
    )

class Survey(d.Survey):
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
            { (RepQ08, 'is-in', (1, 3)) : (
                RepQ09
            ) },
            RepQ10,
            { (d.Profile('seasonal-flu-vaccine'), 'is-not', 'Yes') : (
                RepQ11
            ) },
            { (d.Profile('mexican-flu-vaccine'), 'is-not', 'Yes') : (
                RepQ12
            ) },
        ) }
    )

survey = Survey

