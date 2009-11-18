# -*- coding: utf-8 -*-

from django import forms
from django.template import Context, loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.db import transaction
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

from epiweb.apps.survey import utils
from epiweb.apps.survey import models
from epiweb.apps.survey import example
from epiweb.apps.survey import profile_data

from epidb_client import EpiDBClient

from django.conf import settings

_ = lambda x: x

survey_form_helper = None
profile_form_helper = None

def profile_required(func):
    def redirect(request, *args, **kwargs):
        url = reverse('epiweb.apps.survey.views.profile_index')
        return HttpResponseRedirect(url)
    def _func(request, *args, **kwargs):
        profile = utils.get_profile(request.user)
        if profile is None:
            request.user.message_set.create(message=_('You have to fill your profile data first.'))
            return redirect(request)
        else:
            return func(request, *args, **kwargs)
    return _func
        

@login_required
def thanks(request):
    return render_to_response('survey/thanks.html',
        context_instance=RequestContext(request))

@login_required
@profile_required
def index(request):

    global survey_form_helper
    if survey_form_helper is None:
        survey = example.survey()
        survey_form_helper = utils.SurveyFormHelper(survey)

    if request.method == 'POST':
        form = survey_form_helper.create_form(request.user, request.POST)
        if form.is_valid():
            id = utils.send_survey_response(request.user, form._survey, form.cleaned_data)
            utils.save_survey_response(request.user, form._survey, id)
            return HttpResponseRedirect(reverse('epiweb.apps.survey.views.thanks'))
        else:
            request.user.message_set.create(message=_('One or more questions have empty or invalid answer. Please fix it first.'))
    else:
        form = survey_form_helper.create_form(request.user)

    #js = utils.generate_js_helper(example.survey
    jsh = utils.JavascriptHelper(example.survey(), request.user)
    js = jsh.get_javascript()

    return render_to_response('survey/index.html', {
        'form': form,
        'js': js
    }, context_instance=RequestContext(request))

@login_required
def profile_index(request):
    global profile_form_helper
    if profile_form_helper is None:
        survey = profile_data.UserProfile()
        profile_form_helper = utils.SurveyFormHelper(survey)

    if request.method == 'POST':
        form = profile_form_helper.create_form(request.user, request.POST)
        if form.is_valid():
            utils.send_profile(request.user, form._survey, form.cleaned_data)
            utils.save_profile(request.user, form.cleaned_data)
            return HttpResponseRedirect(reverse('epiweb.apps.survey.views.profile_index'))
        else:
            request.user.message_set.create(message=_('One or more questions have empty or invalid answer. Please fix it first.'))
            
    else:
        form = profile_form_helper.create_form(request.user, utils.get_profile(request.user))

    jsh = utils.JavascriptHelper(profile_data.UserProfile(), request.user)
    js = jsh.get_javascript()

    return render_to_response('survey/profile_index.html', {
        'form': form,
        'js': js
    }, context_instance=RequestContext(request))

