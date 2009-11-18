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
    
    msurvey = request.session.get('survey_msurvey', None)
    if msurvey is None:
        msurvey = utils.get_current_survey()

    survey = utils.get_survey_object(msurvey)
    helper = utils.get_survey_form_helper(survey)

    if request.method == 'POST':
        form = helper.create_form(request.user, request.POST)
        if form.is_valid():
            res = utils.send_survey_response(request.user, form._survey, form.cleaned_data)
            id = res.get('id', None)
            utils.save_survey_response(request.user, msurvey, id)
            return HttpResponseRedirect(reverse('epiweb.apps.survey.views.thanks'))
        else:
            request.user.message_set.create(message=_('One or more questions have empty or invalid answer. Please fix it first.'))
    else:
        form = helper.create_form(request.user)

    jsh = utils.JavascriptHelper(survey, request.user)
    js = jsh.get_javascript()

    return render_to_response('survey/index.html', {
        'form': form,
        'js': js
    }, context_instance=RequestContext(request))

@login_required
def profile_index(request):
    profile = utils.get_profile_object()
    helper = utils.get_survey_form_helper(profile)

    if request.method == 'POST':
        form = helper.create_form(request.user, request.POST)
        if form.is_valid():
            utils.send_profile(request.user, form._survey, form.cleaned_data)
            utils.save_profile(request.user, form.cleaned_data)
            return HttpResponseRedirect(reverse('epiweb.apps.survey.views.profile_index'))
        else:
            request.user.message_set.create(message=_('One or more questions have empty or invalid answer. Please fix it first.'))
            
    else:
        form = helper.create_form(request.user, utils.get_profile(request.user))

    jsh = utils.JavascriptHelper(profile, request.user)
    js = jsh.get_javascript()

    return render_to_response('survey/profile_index.html', {
        'form': form,
        'js': js
    }, context_instance=RequestContext(request))

