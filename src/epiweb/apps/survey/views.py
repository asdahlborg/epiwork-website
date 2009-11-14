# -*- coding: utf-8 -*-

from django import forms
from django.template import Context, loader
from django.http import HttpResponse
from django.db import transaction

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

def index(request):

    if request.method == 'POST':
        form = utils.generate_form(example.survey, request.POST)
        _save_survey(request) # TODO
    else:
        form = utils.generate_form(example.survey)

    #js = utils.generate_js_helper(example.survey

    t = loader.get_template('survey/index.html')
    c = Context({
        'form': form,
        #'js': js
    })
    return HttpResponse(t.render(c))

def survey(request, survey_id, page=None):
    html = "survey_id=%s, page=%s" % (survey_id, page)
    return HttpResponse(html)

