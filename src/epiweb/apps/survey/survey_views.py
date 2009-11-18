# -*- coding: utf-8 -*-

from django import forms
from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.db import transaction
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

from epiweb.apps.survey import utils
from epiweb.apps.survey import models
from epiweb.apps.survey import example

from epidb_client import EpiDBClient

from django.conf import settings

def _create_response_data():
    return {'test': 'dong'}

@transaction.commit_on_success
def _save_survey(request):
    client = EpiDBClient(settings.EPIDB_API_KEY)
    client.server = settings.EPIDB_SERVER
    data = _create_response_data() # TODO
    res = client.response_submit(data)

    try:
        s = models.Survey.objects.all()[0]
    except IndexError:
        s = models.Survey()
        s.description = 'desc'
        s.definition = 'def'
        s.survey_id = 'dudududu'
        s.created = '2009-11-16 03:20'
        s.save()

    hist = models.History()
    hist.user = request.user
    hist.epidb_id = res.get('id', None)
    hist.survey = s # request.session['survey_id']
    hist.save()
    print hist
    print res.get('id', None)

    try:
        profile = models.Profile.objects.get(user=request.user)
    except models.Profile.DoesNotExist:
        profile = models.Profile()
        profile.user = request.user
    profile.last_survey = hist
    profile.last_survey_date = hist.date
    profile.save()

    if res.get('id', None) is None:
        unsaved = models.Unsaved()
        unsaved.history = hist
        unsaved.date = hist.date
        unsaved.data = data
        unsaved.save()

sfh = None

@login_required
def thanks(request):
    return render_to_response('survey/thanks.html')

@login_required
def index(request):

    global sfh
    if sfh is None:
        survey = example.survey()
        sfh = utils.SurveyFormHelper(survey, request.user)

    if request.method == 'POST':
        form = sfh.create_form(request.POST)
        if form.is_valid():
            id = utils.send_survey_response(request.user, form._survey, form.cleaned_data)
            utils.save_survey_response(request.user, form._survey, id)
            return HttpResponseRedirect(reverse('epiweb.apps.survey.survey_views.thanks'))
    else:
        form = sfh.create_form()

    #js = utils.generate_js_helper(example.survey
    jsh = utils.JavascriptHelper(example.survey(), request.user)
    js = jsh.get_javascript()

    return render_to_response('survey/index.html', {
        'form': form,
        'js': js
    })

