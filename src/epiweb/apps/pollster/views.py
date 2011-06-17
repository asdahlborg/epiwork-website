# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from . import models

@login_required
def survey_list(request):
    surveys = models.Survey.objects.all()
    return render_to_response('pollster/survey_list.html', {
        "surveys": surveys
    })

@login_required
def survey_add(request):
    survey = models.Survey()
    virtual_option_types = models.VirtualOptionType.objects.all()
    question_data_types = models.QuestionDataType.objects.all()
    rule_types = models.RuleType.objects.all()
    return render_to_response('pollster/survey_edit.html', {
        "survey": survey,
        "virtual_option_types": virtual_option_types,
        "question_data_types": question_data_types,
        "rule_types": rule_types
    })

@login_required
def survey_edit(request, id):
    survey = models.Survey.objects.get(id=id)
    virtual_option_types = models.VirtualOptionType.objects.all()
    question_data_types = models.QuestionDataType.objects.all()
    rule_types = models.RuleType.objects.all()
    return render_to_response('pollster/survey_edit.html', {
        "survey": survey,
        "virtual_option_types": virtual_option_types,
        "question_data_types": question_data_types,
        "rule_types": rule_types
    })

@login_required
def survey_test(request, id):
    survey = models.Survey.objects.get(id=id)
    return render_to_response('pollster/survey.html', {
        "survey": survey
    })
