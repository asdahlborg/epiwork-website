# -*- coding: utf-8 -*-

from epiweb.apps.survey.data.conditions import *
from epiweb.apps.survey.data import Survey, Section, Question
_ = lambda x: x

data = Survey()
section = Section()

q = Question('q10001', _('Did you have one or more of the following symptoms since your last visit?'))
q.type = 'option-multiple'
q.options = [
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
]
section.questions.append(q)

q = Question('q10002', _('When did these symptoms started?'))
q.type = 'date'
q.condition = NotEmpty(Q("q10001"))
section.questions.append(q)

q = Question('q10003', _('Did you have fever? If yes, what was the highest temperature measured? Please estimate if you had fever, but did not measure.'))
q.type = 'option-single'
q.options = [
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
]
q.condition = NotEmpty(Q("q10001"))
section.questions.append(q)

q = Question('q10004', _('When was your temperature for the first time above 38°C?'))
q.type = 'date'
q.condition = NotEmpty(Q("q10001"))
section.questions.append(q)

q = Question('q10005', _('Did these symptoms develop abruptly with sudden high fever or chills?'))
q.type = 'option-single'
q.options = [
    _('No'),
    _('Yes'),
    _("Don't know"),
]
q.condition = NotEmpty(Q("q10001"))
section.questions.append(q)

q = Question('q10006', _('Did you consult a medical doctor for these symptoms?'))
q.type = 'yes-no'
q.condition = NotEmpty(Q("q10001"))
section.questions.append(q)

q = Question('q10007', _('Did you take medication for these symptoms?'))
q.type = 'option-single'
q.options = [
    _('Tamiflu, Relenza, or another anti viral drug'),
    _('Antibiotics'),
    _('Antipyretics'),
    _('Anti-inflammatory drugs'),
    _('Vitamins'),
    _('Other'),
]
q.condition = NotEmpty(Q("q10001"))
section.questions.append(q)

q = Question('q10008', _('Did you change your occupations due to these symptoms?'))
q.type = 'option-single'
q.options = [
    _('No'),
    _('Yes, I staid at home'),
    _('Yes, but went to work/school as usual'),
    _('I staid at home, but was able to work'),
]
q.condition = NotEmpty(Q("q10001"))
section.questions.append(q)

q = Question('q10009', _('How long did you staid at home?'))
q.type = 'option-single'
q.options = [
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
]
q.condition = NotEmpty(Q("q10001")) & OneOf(Q("q10008"), [1, 2])
section.questions.append(q)

q = Question('q10010', _('Do other people from your family/home have/had comparable symptoms?'))
q.type = 'yes-no'
q.condition = NotEmpty(Q("q10001"))
section.questions.append(q)

q = Question('q10011', _('According to our data you did not receive a seasonal flu vaccination?'))
q.type = 'option-single'
q.options = [
    _('Yes'),
    _('No, meanwhile I have received a seasonal flu vaccination'),
]
q.condition = Intake("q20005") == False
section.questions.append(q)

q = Question('q10012', _('According to our data you did not receive a Mexican flu vaccination?'))
q.type = 'option-single'
q.options = [
    _('Yes'),
    _('No, meanwhile I have received a Mexican flu vaccination'),
]
q.condition = Intake("q20006") == False
section.questions.append(q)

data.sections.append(section)

