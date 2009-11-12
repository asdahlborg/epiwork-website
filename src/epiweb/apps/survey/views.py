# -*- coding: utf-8 -*-

from django import forms
from django.template import Context, loader
from django.http import HttpResponse

from epiweb.apps.survey.data import Survey, Section, Question
from epiweb.apps.survey import utils

_ = lambda x: x

survey_data = Survey()
section = Section()

q = Question('q10001', _('Did you have one or more of the following symptoms since your last visit?'))
q.type = 'option-multiple'
q.options = [
    _('Runnynose'),
    _('Stuffy nose'),
    _('Hacking cough'),
    _('Dry cough'),
    _('Sneezing'),
    _('Sorethroat'),
    _('Musclepain'),
    _('Headache'),
    _('Chestpain'),
    _('Feeling exhausted'),
    _('Feeling tired'),
    _('Lossofappetite'),
    _('Nausea'),
    _('Vomiting'),
    _('Diarrhoea'),
    _('Watery, bloodshot eyes'),
    _('Chillsandfeverishfeeling'),
    _('Colouredsputum'),
]
section.questions.append(q)

q = Question('q10002', _('When did these symptoms started?'))
q.type = 'date'
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
section.questions.append(q)

q = Question('q10004', _('When was your temperature for the first time above 38°C?'))
q.type = 'date'
section.questions.append(q)

q = Question('q10005', _('Did these symptoms develop abruptly with sudden high fever or chills?'))
q.type = 'option-single'
q.options = [
    _('No'),
    _('Yes'),
    _("Don't know"),
]
section.questions.append(q)

q = Question('q10006', _('Did you consult a medical doctor for these symptoms?'))
q.type = 'yes-no'
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
section.questions.append(q)

q = Question('q10008', _('Did you change your occupations due to these symptoms?'))
q.type = 'option-single'
q.options = [
    _('No'),
    _('Yes, I staid at home'),
    _('Yes, but went to work/school as usual'),
    _('I staid at home, but was able to work'),
]
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
section.questions.append(q)

q = Question('q10010', _('Do other people from your family/home have/had comparable symptoms?'))
q.type = 'yes-no'
section.questions.append(q)

q = Question('q10011', _('According to our data you did not receive a seasonal flu vaccination?'))
q.type = 'option-single'
q.options = [
    _('Yes'),
    _('No, meanwhile I have received a seasonal flu vaccination'),
]
section.questions.append(q)

q = Question('q10012', _('According to our data you did not receive a Mexican flu vaccination?'))
q.type = 'option-single'
q.options = [
    _('Yes'),
    _('No, meanwhile I have received a Mexican flu vaccination'),
]
section.questions.append(q)

survey_data.sections.append(section)

def create_field(item):
    if item['type'] == 'yes-no':
        field = forms.ChoiceField(widget=forms.RadioSelect,
                                  choices=[('yes', _('Yes')), ('no', _('No'))])

    elif item['type'] == 'option-multiple':
        field = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                          choices=zip(range(0, len(item['options'])), item['options']))

    elif item['type'] == 'option-single':
        field = forms.ChoiceField(widget=forms.RadioSelect,
                                  choices=zip(range(0, len(item['options'])), item['options']))

    elif item['type'] == 'date':
        field = forms.DateField(input_formats='%m/%d/%y')

    else:
        field = forms.CharField()

    field.label = item.get('label', None)
    field.required = False

    return field

def create_form(data, values=None):
    if values:
        f = forms.Form(values)
    else:
        f = forms.Form()

    for item in data:
        f.fields[item['id']] = create_field(item)
    return f

def index(request):

    if request.method == 'POST':
        form = utils.generate_form(survey_data.sections[0], request.POST)
    else:
        form = utils.generate_form(survey_data.sections[0])

    t = loader.get_template('survey/index.html')
    c = Context({
        'form': form
    })
    return HttpResponse(t.render(c))

def survey(request, survey_id, page=None):
    html = "survey_id=%s, page=%s" % (survey_id, page)
    return HttpResponse(html)

