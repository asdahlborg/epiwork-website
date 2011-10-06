# -*- coding: utf-8 -*-

from django import forms
from django.template import Context, loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.db import connection, transaction, DatabaseError
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.db import connection

from apps.survey import utils, models, forms
from apps.pollster import views as pollster_views
from apps.pollster import utils as pollster_utils
from .survey import ( Specification,
                      FormBuilder,
                      JavascriptBuilder,
                      get_survey_context, )
import apps.pollster as pollster
import pickle

survey_form_helper = None
profile_form_helper = None

def get_active_survey_user(request):
    gid = request.GET.get('gid', None)
    if gid is None:
        return None
    else:
        try:
            return models.SurveyUser.objects.get(global_id=gid,
                                                 user=request.user)
        except models.SurveyUser.DoesNotExist:
            raise ValueError()

def _decode_person_health_status(status):
    if status == "NO-SYMPTOMS":
        diag = _('No symptoms')
    elif status == "ILI":
        diag = _('Flu symptoms')
    elif status == "COMMON-COLD":
       diag = _('Cold / allergy')
    elif status == "GASTROINTESTINAL":
       diag = _('Gastrointestinal symptoms')
    elif status == "NON-INFLUENZA":
       diag = _('Other non-influenza symptons')
    else:
       diag = _('Next status')
    return diag

def _db_table_exists(table):
    cursor = connection.cursor()
    table_names = connection.introspection.get_table_list(cursor)
    return table in table_names

def _get_person_health_status(request, survey, global_id):
    if not _db_table_exists("pollster_health_status"):
        return (None, _decode_person_health_status(None))

    data = survey.get_last_participation_data(request.user.id, global_id)
    status = None
    if data:
        cursor = connection.cursor()
        params = { 'weekly_id': data["id"] }
        cursor.execute("""
            SELECT S.status
              FROM pollster_health_status S
             WHERE S.pollster_results_weekly_id = :weekly_id""", params)
        status = cursor.fetchone()[0]
    return (status, _decode_person_health_status(status))

def _get_person_health_history(request, survey, global_id):
    if not _db_table_exists("pollster_health_status"):
        raise StopIteration

    results = []
    cursor = connection.cursor()
    params = { 'user_id': request.user.id, 'global_id': global_id }
    cursor.execute("""
        SELECT W.timestamp, S.status
          FROM pollster_health_status S, pollster_results_weekly W
         WHERE S.pollster_results_weekly_id = W.id
           AND W.user = :user_id
           AND W.global_id = :global_id
         ORDER BY W.timestamp""", params)
    results = cursor.fetchall()
    for ret in results:
        timestamp, status = ret
        yield {'timestamp': timestamp, 'status': status, 'diag':_decode_person_health_status(status)}

@login_required
def thanks(request):
    try:
        survey = pollster.models.Survey.get_by_shortname('weekly')
    except:
        raise Exception("The survey application requires a published survey with the shortname 'weekly'")
    Weekly = survey.as_model()

    persons = models.SurveyUser.objects.filter(user=request.user, deleted=False)
    for person in persons:
        person.health_status, person.diag = _get_person_health_status(request, survey, person.global_id)
        person.health_history = list(_get_person_health_history(request, survey, person.global_id))[-7:]
    return render_to_response('survey/thanks.html', {'persons': persons}, 
                              context_instance=RequestContext(request))

@login_required
def thanks_profile(request):
    return render_to_response('survey/thanks_profile.html',
        context_instance=RequestContext(request))

@login_required
def select_user(request, template='survey/select_user.html'):
    next = request.GET.get('next', None)
    if next is None:
        next = reverse(index)

    users = models.SurveyUser.objects.filter(user=request.user, deleted=False)
    total = len(users)
    if total == 0:
        survey_user = models.SurveyUser.objects.create(
            user=request.user,
            name=request.user.username,
        )
        url = '%s?gid=%s' % (next, survey_user.global_id)
        return HttpResponseRedirect(url)
        
    elif total == 1:
        survey_user = users[0]
        url = '%s?gid=%s' % (next, survey_user.global_id)
        return HttpResponseRedirect(url)

    return render_to_response(template, {
        'users': users,
        'next': next,
    }, context_instance=RequestContext(request))

@login_required
def index(request):
    try:
        survey_user = get_active_survey_user(request)
    except ValueError:
        raise Http404()
    if survey_user is None:
        url = '%s?next=%s' % (reverse(select_user), reverse(index))
        return HttpResponseRedirect(url)

    # Check if the user has filled user profile
    profile = pollster_utils.get_user_profile(request.user.id, survey_user.global_id)
    if profile is None:
        messages.add_message(request, messages.INFO, 
            _('You have to fill your profile data first.'))
        url = reverse('apps.survey.views.profile_index')
        url_next = reverse('apps.survey.views.index')
        url = '%s?gid=%s&next=%s' % (url, survey_user.global_id, url_next)
        return HttpResponseRedirect(url)

    try:
        survey = pollster.models.Survey.get_by_shortname('weekly')
    except:
        raise Exception("The survey application requires a published survey with the shortname 'weekly'")

    next = None
    if 'next' not in request.GET:
        next = reverse(thanks)

    return pollster_views.survey_run(request, survey.shortname, next=next)

@login_required
def profile_index(request):
    try:
        survey_user = get_active_survey_user(request)
    except ValueError:
        raise Http404()
    if survey_user is None:
        url = '%s?next=%s' % (reverse(select_user), reverse(profile_index))
        return HttpResponseRedirect(url)

    try:
        survey = pollster.models.Survey.get_by_shortname('intake')
    except:
        raise Exception("The survey application requires a published survey with the shortname 'intake'")

    next = None
    if 'next' not in request.GET:
        next = reverse(thanks_profile)

    return pollster_views.survey_run(request, survey.shortname, next=next)

@login_required
def people_edit(request):
    try:
        survey_user = get_active_survey_user(request)
    except ValueError:
        raise Http404()
    if survey_user is None:
        url = '%s?next=%s' % (reverse(select_user), reverse(people_edit))
        return HttpResponseRedirect(url)
    elif survey_user.deleted == True:
        raise Http404()

    if request.method == 'POST':
        form = forms.AddPeople(request.POST)
        if form.is_valid():
            survey_user.name = form.cleaned_data['name']
            survey_user.save()

            return HttpResponseRedirect(reverse(people))

    else:
        form = forms.AddPeople(initial={'name': survey_user.name})

    return render_to_response('survey/people_edit.html', {'form': form},
                              context_instance=RequestContext(request))

@login_required
def people_remove(request):
    try:
        survey_user = get_active_survey_user(request)
    except ValueError:
        raise Http404()

    if survey_user is None:
        url = reverse(people)
        return HttpResponseRedirect(url)
    elif survey_user.deleted == True:
        raise Http404()

    confirmed = request.POST.get('confirmed', None)

    if confirmed == 'Y':
        survey_user.deleted = True
        survey_user.save()
   
        url = reverse(people)
        return HttpResponseRedirect(url)

    elif confirmed == 'N':
        url = reverse(people)
        return HttpResponseRedirect(url)

    else:
        return render_to_response('survey/people_remove.html', {'person': survey_user},
                              context_instance=RequestContext(request))

@login_required
def people_add(request):
    if request.method == 'POST':
        form = forms.AddPeople(request.POST)
        if form.is_valid():
            survey_user = models.SurveyUser()
            survey_user.user = request.user
            survey_user.name = form.cleaned_data['name']
            survey_user.save()

            messages.add_message(request, messages.INFO, 
                _('A new person has been added.'))

            next = request.GET.get('next', None)
            if next is None:
                url = reverse(people)
            else:
                url = '%s?gid=%s' % (next, survey_user.global_id)
            return HttpResponseRedirect(url)

    else:
        form = forms.AddPeople()

    return render_to_response('survey/people_add.html', {'form': form},
                              context_instance=RequestContext(request))

@login_required
def people(request):
    users = models.SurveyUser.objects.filter(user=request.user, deleted=False)
    return render_to_response('survey/people.html', {'people': users},
                              context_instance=RequestContext(request))

