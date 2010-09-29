# -*- coding: utf-8 -*-

from django import forms
from django.template import Context, loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.db import transaction
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.conf import settings

from epiweb.apps.survey import utils, models

_ = lambda x: x

survey_form_helper = None
profile_form_helper = None

def get_active_survey_user(request):
    # FIXME one (Django) user can maintain more than one survey user
    #       so, there should be an identifier somewhere that points
    #       to the survey user that is filling the survey
    #       for now, just assume the (Django) user is one-to-one mapped
    #       to a survey user
    return request.user.surveyuser_set.get()

def profile_required(func):
    def redirect(request, *args, **kwargs):
        url_profile = reverse('epiweb.apps.survey.views.profile_index')
        url_survey = reverse('epiweb.apps.survey.views.index')
        url = '%s?next=%s' % (url_profile, url_survey)
        return HttpResponseRedirect(url)
    def _func(request, *args, **kwargs):
        survey_user = get_active_survey_user(request)
        profile = utils.get_user_profile(survey_user)
        if profile is None:
            request.user.message_set.create(
                message=_('You have to fill your profile data first.'))
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
    survey = utils.get_survey()
    form_class = utils.get_form_class(survey.id)
    survey_user = get_active_survey_user(request)

    if request.method == 'POST':
        form = form_class(survey_user, request.POST)
        if form.is_valid():
            participation = utils.add_survey_participation(survey_user,
                                                           survey._data)

            utils.add_response_queue(participation, survey, form.cleaned_data)
            data = utils.format_response_data(survey, form.cleaned_data)
            utils.save_last_response(survey_user, participation, data)

            return HttpResponseRedirect(reverse(
                                          'epiweb.apps.survey.views.thanks'))
        else:
            request.user.message_set.create(
                message=_('One or more questions have empty or invalid ' \
                          'answer. Please fix it first.'))
    else:
        form = form_class(survey_user)

    jsh = utils.JavascriptHelper(survey, survey_user)
    js = jsh.get_javascript()

    return render_to_response('survey/index.html', {
        'form': form,
        'js': js
    }, context_instance=RequestContext(request))

@login_required
def profile_index(request):
    survey = utils.get_profile()
    form_class = utils.get_form_class(survey.id)
    survey_user = get_active_survey_user(request)

    if request.method == 'POST':
        form = form_class(survey_user, request.POST)
        if form.is_valid():
            utils.add_profile_queue(survey_user, form._survey, form.cleaned_data)
            data = utils.format_profile_data(survey, form.cleaned_data)
            utils.save_profile(survey_user, survey._data, data)

            next = request.GET.get('next', None)
            if next is not None:
                url = next
            else:
                url = reverse('epiweb.apps.survey.views.profile_index')

            request.user.message_set.create(message=_('Profile saved.'))
            return HttpResponseRedirect(url)

        else:
            request.user.message_set.create(
                message=_('One or more questions have empty or invalid ' \
                          'answer. Please fix it first.'))
            
    else:
        form = form_class(survey_user,
                          utils.get_user_profile(survey_user))

    jsh = utils.JavascriptHelper(survey, survey_user)
    js = jsh.get_javascript()

    return render_to_response('survey/profile_index.html', {
        'form': form,
        'js': js
    }, context_instance=RequestContext(request))

