
from django import forms
from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.db import transaction
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

from epiweb.apps.survey import utils as survey_utils

from epiweb.apps.profile import models
from epiweb.apps.profile import data
from epiweb.apps.profile import utils


sfh = None

@login_required
def index(request):
    global sfh
    if sfh is None:
        survey = data.UserProfile()
        sfh = survey_utils.SurveyFormHelper(survey, request.user)

    if request.method == 'POST':
        form = sfh.create_form(request.POST)
        if form.is_valid():
            utils.send_profile(request.user, form._survey, form.cleaned_data)
            utils.save_profile(request.user, form.cleaned_data)
            return HttpResponseRedirect(reverse('epiweb.apps.profile.views.index'))
            
    else:
        form = sfh.create_form(utils.get_profile(request.user))

    jsh = survey_utils.JavascriptHelper(data.UserProfile(), request.user)
    js = jsh.get_javascript()

    return render_to_response('profile/index.html', {
        'form': form,
        'js': js
    })

