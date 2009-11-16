# -*- coding: utf-8 -*-

from django import forms
from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.db import transaction
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response

from epiweb.apps.survey import utils
from epiweb.apps.survey import models
from epiweb.apps.survey import example

from epidb_client import EpiDBClient

from django.conf import settings

def _create_response_data():
    return ""

@transaction.commit_on_success
def _save_survey(request):
    client = EpiDBClient(settings.EPIDB_API_KEY)
    client.server = settings.EPIDB_SERVER
    data = _create_response_data() # TODO
    res = client.response_submit(data)

    hist = models.History()
    hist.user = request.user
    hist.epidb_id = res.get('id', None)
    hist.survey = request.session['survey_id']
    hist.save()

    profile = models.Profile.objects.get(user=request.user)
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

def thanks(request):
    return render_to_response('survey/thanks.html')

def index(request):

    global sfh
    if sfh is None:
        survey = example.survey()
        sfh = utils.SurveyFormHelper(survey)

    if request.method == 'POST':
        form = sfh.create_form(request.POST)
        if form.is_valid():
            # _save_survey(request) # TODO
            return HttpResponseRedirect(reverse('epiweb.apps.survey.views.thanks'))
    else:
        form = sfh.create_form()

    #js = utils.generate_js_helper(example.survey
    jsh = utils.JavascriptHelper(example.survey())
    js = jsh.get_javascript()

    return render_to_response('survey/index.html', {
        'form': form,
        'js': js
    })

def survey(request, survey_id, page=None):
    html = "survey_id=%s, page=%s" % (survey_id, page)
    return HttpResponse(html)

