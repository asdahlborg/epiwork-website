# -*- coding: utf-8 -*-

from django.core.urlresolvers import get_resolver, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.utils.safestring import mark_safe
from apps.survey.models import SurveyUser
from . import models, forms, parser, json
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
    if not survey.is_editable:
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
def survey_unpublish(request, id):
    survey = get_object_or_404(models.Survey, pk=id)
    if (request.method == 'POST'):
        survey.unpublish()
        return redirect(survey)
    return redirect(survey)

@login_required
def survey_test(request, id, language=None):
    survey = get_object_or_404(models.Survey, pk=id)
    if language:
        translation = get_object_or_404(models.TranslationSurvey, survey=survey, language=language)
        survey.set_translation_survey(translation)
    survey_user = _get_active_survey_user(request)
    user = _get_active_survey_user(request)
    form = None
    user_id = request.user.id
    global_id = survey_user and survey_user.global_id
    last_partecipation_data = None
    if request.method == 'POST':
        form = survey.as_form()(request.POST)
        if form.is_valid():
            form.cleaned_data['user'] = user_id
            form.cleaned_data['global_id'] = global_id
            form.cleaned_data['timestamp'] = datetime.datetime.now()
            destination = reverse(survey_test, kwargs={'id':id, 'language': language})
            if user:
                destination += '?gid='+user.global_id
            return HttpResponseRedirect(destination)
        else:
            survey.set_form(form)
    encoder = json.JSONEncoder(ensure_ascii=False, indent=2)
    last_partecipation_data_json = encoder.encode(last_partecipation_data)

    return render_to_response('pollster/survey_test.html', {
        "survey": survey,
        "last_partecipation_data_json": last_partecipation_data_json,
        "language": language,
        "form": form
    })

@login_required
def survey_run(request, id):
    survey = get_object_or_404(models.Survey, pk=id, status='PUBLISHED')
    survey_user = _get_active_survey_user(request)
    form = None
    user_id = request.user.id
    global_id = survey_user and survey_user.global_id
    last_partecipation_data = survey.get_last_partecipation_data(user_id, global_id)
    if request.method == 'POST':
        form = survey.as_form()(request.POST)
        if form.is_valid():
            form.cleaned_data['user'] = user_id
            form.cleaned_data['global_id'] = global_id
            form.cleaned_data['timestamp'] = datetime.datetime.now()
            form.save()
            return HttpResponseRedirect('/survey/thanks')
        else:
            survey.set_form(form)
    encoder = json.JSONEncoder(ensure_ascii=False, indent=2)
    last_partecipation_data_json = encoder.encode(last_partecipation_data)

    return render_to_response('pollster/survey_test.html', {
        "survey": survey,
        "last_partecipation_data_json": last_partecipation_data_json,
        "form": form
    })

@login_required
def survey_translation_list_or_add(request, id):
    survey = get_object_or_404(models.Survey, pk=id)
    form_add = forms.SurveyTranslationAddForm()
    if request.method == 'POST':
        form_add = forms.SurveyTranslationAddForm(request.POST)
        if form_add.is_valid():
            language = form_add.cleaned_data['language']
            if survey.translationsurvey_set.all().filter(language=language)[0:1]:
                translation = translations[0]
            else:
                translation = models.TranslationSurvey(survey=survey, language=language)
                translation.save()
            return redirect(translation)
    return render_to_response('pollster/survey_translation_list.html', {
        "survey": survey,
        "form_add": form_add
    })


@login_required
def survey_translation_edit(request, id, language):
    survey = get_object_or_404(models.Survey, pk=id)
    translation = get_object_or_404(models.TranslationSurvey, survey=survey, language=language)
    survey.set_translation_survey(translation)
    if request.method == 'POST':
        forms = []
        forms.append( survey.translation.as_form(request.POST) )
        for question in survey.questions:
            forms.append( question.translation.as_form(request.POST) )
            for row in question.rows:
                forms.append( row.translation.as_form(request.POST) )
            for column in question.columns:
                forms.append( column.translation.as_form(request.POST) )
            for option in question.options:
                forms.append( option.translation.as_form(request.POST) )
        if all(f.is_valid() for f in forms):
            for form in forms:
                form.save()
            return redirect(translation)
    return render_to_response('pollster/survey_translation_edit.html', {
        "survey": survey,
        "translation": translation
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
