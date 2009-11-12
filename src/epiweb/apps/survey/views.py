# -*- coding: utf-8 -*-

from django import forms
from django.template import Context, loader
from django.http import HttpResponse

from epiweb.apps.survey import utils
from epiweb.apps.survey.data import example

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
        form = utils.generate_form(example.data.sections[0], request.POST)
    else:
        form = utils.generate_form(example.data.sections[0])

    t = loader.get_template('survey/index.html')
    c = Context({
        'form': form
    })
    return HttpResponse(t.render(c))

def survey(request, survey_id, page=None):
    html = "survey_id=%s, page=%s" % (survey_id, page)
    return HttpResponse(html)

