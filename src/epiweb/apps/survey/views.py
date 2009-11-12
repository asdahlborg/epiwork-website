# -*- coding: utf-8 -*-

from django import forms
from django.template import Context, loader
from django.http import HttpResponse

_ = lambda x: x

questions = []

section = []
section.append({
    'id': 'q10001', 
    'label': _('Did you have one or more of the following symptoms since your last visit?'),
    'type': 'option-multiple',
    'options': [
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
})
section.append({
    'id': 'q10002',
    'label': _('When did these symptoms started?'),
    'type': 'date'
})
section.append({
    'id': 'q10003',
    'label': _('Did you have fever? If yes, what was the highest temperature measured? Please estimate if you had fever, but did not measure.'),
    'type': 'option-single',
    'options': [
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
})
section.append({
    'id': 'q10004',
    'label': _('When was your temperature for the first time above 38°C?'),
    'type': 'date',
})
section.append({
    'id': 'q10005',
    'label': _('Did these symptoms develop abruptly with sudden high fever or chills?'),
    'type': 'option-single',
    'options': [
        _('No'),
        _('Yes'),
        _("Don't know"),
    ]
})
section.append({
    'id': 'q10006',
    'label': _('Did you consult a medical doctor for these symptoms?'),
    'type': 'yes-no',
})
section.append({
    'id': 'q10007',
    'label': _('Did you take medication for these symptoms?'),
    'type': 'option-single',
    'options': [
        _('Tamiflu, Relenza, or another anti viral drug'),
        _('Antibiotics'),
        _('Antipyretics'),
        _('Anti-inflammatory drugs'),
        _('Vitamins'),
        _('Other'),
    ]
})
section.append({
    'id': 'q10008',
    'label': _('Did you change your occupations due to these symptoms?'),
    'type': 'option-single',
    'options': [
        _('No'),
        _('Yes, I staid at home'),
        _('Yes, but went to work/school as usual'),
        _('I staid at home, but was able to work'),
    ]
})
section.append({
    'id': 'q10009',
    'label': _('How long did you staid at home?'),
    'type': 'option-single',
    'options': [
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
})
section.append({
    'id': 'q10010',
    'label': _('Do other people from your family/home have/had comparable symptoms?'),
    'type': 'yes-no'
})
section.append({
    'id': 'q10011',
    'label': _('According to our data you did not receive a seasonal flu vaccination?'),
    'type': 'option-single',
    'options': [
        _('Yes'),
        _('No, meanwhile I have received a seasonal flu vaccination'),
    ]
})
section.append({
    'id': 'q10012',
    'label': _('According to our data you did not receive a Mexican flu vaccination?'),
    'type': 'option-single',
    'options': [
        _('Yes'),
        _('No, meanwhile I have received a Mexican flu vaccination'),
    ]
})
questions.append(section)

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

    else:
        return forms.CharField(label=label)

def create_form(data):
    f = forms.Form()
    for item in data:
        f.fields[item['id']] = create_field(item)
    return f

def index(request):
    form = create_form(questions[0])

    t = loader.get_template('survey/index.html')
    c = Context({
        'form': form
    })
    return HttpResponse(t.render(c))

def survey(request, survey_id, page=None):
    html = "survey_id=%s, page=%s" % (survey_id, page)
    return HttpResponse(html)

