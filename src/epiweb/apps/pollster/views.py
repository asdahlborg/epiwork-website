# -*- coding: utf-8 -*-

from django.core.urlresolvers import get_resolver, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.utils import simplejson
from epiweb.apps.survey.models import SurveyUser
from . import models, forms, parser
import re, datetime

@login_required
def survey_list(request):
    surveys = models.Survey.objects.all()
    return render_to_response('pollster/survey_list.html', {
        "surveys": surveys
    })

@login_required
def survey_add(request):
    survey = models.Survey()
    if (request.method == 'POST'):
        form = forms.SurveyXmlForm(request.POST)
        if form.is_valid():
            # create and redirect
            parser.survey_update_from_xml(survey, form.cleaned_data['surveyxml'])
            return redirect(survey)
    # return an empty survey structure
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
    survey = get_object_or_404(models.Survey, pk=id)
    if not survey.is_draft:
        return redirect(survey_test, id=id)
    if request.method == 'POST':
        form = forms.SurveyXmlForm(request.POST)
        if form.is_valid():
            parser.survey_update_from_xml(survey, form.cleaned_data['surveyxml'])
            return redirect(survey)
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
def survey_publish(request, id):
    survey = get_object_or_404(models.Survey, pk=id)
    if (request.method == 'POST'):
        survey.publish()
        return redirect(survey)
    return redirect(survey)

@login_required
def survey_test(request, id):
    survey = get_object_or_404(models.Survey, pk=id)
    user = _get_active_survey_user(request)
    if request.method == 'POST':
        form = survey.as_form()(request.POST)
        if form.is_valid():
            form.cleaned_data['user'] = request.user.id
            if user:
                form.cleaned_data['global_id'] = user.global_id
            form.cleaned_data['timestamp'] = datetime.datetime.now()
            if survey.is_published:
                form.save()
            destination = reverse(survey_test, kwargs={'id':id})
            if user:
                destination += '?gid='+user.global_id
            return HttpResponseRedirect(destination)
        else:
            print form.errors
    return render_to_response('pollster/survey_test.html', {
        "survey": survey
    })

@login_required
def survey_export(request, id):
    survey = get_object_or_404(models.Survey, pk=id)
    return render_to_response('pollster/survey_export.json', {
        "survey": survey
    }, mimetype='application/json')

# based on http://djangosnippets.org/snippets/2059/
def urls(request, prefix=''):
    """
        Returns javascript for mapping service endpoint names to urls.

        For this view to work properly, all urls that are to be made
        available and are using regular expressions for defining
        parameters must use named parameters.

        The view uses Django internal url resolver to iterate over a list
        of all currently defined url patterns.  It looks for named patterns
        and replaces each named regex group definition the group name enclosed
        in curley braces.  Url pattern names will be translated into
        javascript variable names by converting all letters to the upper
        case and replacing '-' with '_'.
    """
    resolver = get_resolver(None)

    urls = {}

    for name in resolver.reverse_dict:
        if isinstance(name, str) and name.startswith(prefix):
            url_regex = resolver.reverse_dict.get(name)[1]
            param_names = resolver.reverse_dict.get(name)[0][0][1]
            arg_pattern = r'\(\?P\<[^\)]+\)'  #matches named groups in the form of (?P<name>pattern)

            i = 0
            for match in re.findall(arg_pattern, url_regex):
                url_regex = url_regex.replace(match, "{%s}"%param_names[i])
                i += 1

            urls[name] = "/" + url_regex[:-1]

    return render_to_response("pollster/urls.js", {'urls':urls}, mimetype="application/javascript")

def _get_active_survey_user(request):
    gid = request.GET.get('gid', None)
    if gid is None:
        return None
    else:
        return SurveyUser.objects.get(global_id=gid, user=request.user)
