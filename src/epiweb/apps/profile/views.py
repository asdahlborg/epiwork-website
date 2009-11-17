
from django import forms
from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.db import transaction
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response

from epiweb.apps.profile import models
from epiweb.apps.profile import data

from epiweb.apps.survey import utils

try:
    import json
except ImportError:
    import simplejson as json

def _get_profile(user):
    try:
        profile = models.Profile.objects.get(user=user)
        return json.loads(profile.data)
    except models.Profile.DoesNotExist:
        return None

def _save_profile(user, data):
    try:
        profile = models.Profile.objects.get(user=user)
    except models.Profile.DoesNotExist:
        profile = models.Profile()
        profile.user = user

    profile.data = json.dumps(data)
    profile.save()

sfh = None

def index(request):
    global sfh
    if sfh is None:
        survey = data.UserProfile()
        sfh = utils.SurveyFormHelper(survey)

    if request.method == 'POST':
        form = sfh.create_form(request.POST)
        if form.is_valid():
            _save_profile(request.user, form.cleaned_data)
            return HttpResponseRedirect(reverse('epiweb.apps.profile.views.index'))
            
    else:
        form = sfh.create_form(_get_profile(request.user))

    jsh = utils.JavascriptHelper(data.UserProfile())
    js = jsh.get_javascript()

    return render_to_response('profile/index.html', {
        'form': form,
        'js': js
    })

