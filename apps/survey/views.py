# -*- coding: utf-8 -*-

from django import forms
from django.template import Context, loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.db import transaction
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from apps.survey import utils, models, forms
from .survey import ( Specification,
                      FormBuilder,
                      JavascriptBuilder,
                      get_survey_context, )
import apps.pollster as pollster
import extra
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

@login_required
def thanks(request):
    persons = models.SurveyUser.objects.filter(user=request.user)
    for person in persons:
        responses = list(models.LastResponse.objects.filter(user=person))
        if responses[0].data:
            response_dict = pickle.loads(str(responses[0].data))
            wq1 = set(response_dict['WeeklyQ1'])
            wq1b = response_dict['WeeklyQ1b']
            if wq1==set([0]):
                person.diag = _('No symptoms')
            elif (wq1b == 0) and wq1.intersection([1,17,11,8,9]) and wq1.intersection([6,5,18]):
                person.diag = _('Flu symptoms')
            elif wq1.intersection([2,3,4,5,6]):
               person.diag = _('Cold / allergy')
            elif len(wq1.intersection([15,19,14,12,13]))>1:
               person.diag = _('Gastrointestinal symptoms')
            else:
               person.diag = _('Other non-influenza symptons')
        else: 
           person.diag = _('Next status')
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
        url = '%s?next=%s' % (reverse(people_add), next)
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
    if utils.get_user_profile(survey_user) is None:
        messages.add_message(request, messages.INFO, 
            _('You have to fill your profile data first.'))
        url = reverse('apps.survey.views.profile_index')
        url_next = reverse('apps.survey.views.index')
        url = '%s?gid=%s&next=%s' % (url, survey_user.global_id, url_next)
        return HttpResponseRedirect(url)

    spec = utils.load_specification(settings.SURVEY_ID)
    context = get_survey_context(survey_user)
    builder = FormBuilder(spec)

    if request.method == 'POST':
        form = builder.get_form(context, request.POST)
        if form.is_valid():
            participation = utils.add_survey_participation(survey_user,
                                                           spec.survey.id)

            utils.add_response_queue(participation, spec, form.cleaned_data)
            data = utils.format_response_data(spec, form.cleaned_data)
            utils.save_last_response(survey_user, participation, data)
            utils.save_local_flu_survey(survey_user, spec.survey.id, data)
            utils.update_local_profile(survey_user)
            utils.save_response_locally(survey_user.name,
                                        spec.survey.id,
                                        data,
                                        participation.date)

            return HttpResponseRedirect(reverse(thanks))
        else:
            messages.add_message(request, messages.INFO, 
                _('One or more questions have empty or invalid ' \
                          'answer. Please fix it first.'))
    else:
        form = builder.get_form(context)

    js_builder = JavascriptBuilder(spec)
    js = mark_safe(js_builder.get_javascript(context))

    return render_to_response('survey/index.html', {
        'form': form,
        'js': js
    }, context_instance=RequestContext(request))

@login_required
def profile_index(request):
    try:
        survey_user = get_active_survey_user(request)
    except ValueError:
        raise Http404()
    if survey_user is None:
        url = '%s?next=%s' % (reverse(select_user), reverse(profile_index))
        return HttpResponseRedirect(url)

    survey = pollster.models.Survey.get_by_shortname('intake')
    return pollster.views.survey_run(request, survey.id)

@login_required
def extra_index(request):
    try:
        survey_user = get_active_survey_user(request)
    except ValueError:
        raise Http404()
    if survey_user is None:
        url = '%s?next=%s' % (reverse(select_user), reverse(extra_index))
        return HttpResponseRedirect(url)
    spec = utils.load_specification(settings.EXTRA_SURVEY)
    context = get_survey_context(survey_user)
    builder = FormBuilder(spec)

    if request.method == 'POST':
        form = builder.get_form(context, request.POST)
        if form.is_valid():
            participation = utils.add_extra_survey_participation(survey_user,
                                                                 spec.survey.id)
            utils.add_response_queue(participation, spec, form.cleaned_data)
            data = utils.format_response_data(spec, form.cleaned_data)
            utils.save_extra_response(survey_user, participation, data)
            utils.save_response_locally(survey_user.name,
                                        spec.survey.id,
                                        data,
                                        None)

            next = request.GET.get('next', None)
            if next:
                url = next
            else:
                url = reverse('apps.survey.views.extra_index')
            url = '%s?gid=%s' % (url, survey_user.global_id)

            return HttpResponseRedirect(reverse(thanks))

        else:
            messages.add_message(request, messages.INFO, 
                _('One or more questions have empty or invalid ' \
                          'answer. Please fix it first.'))

    else:
        initial = utils.get_user_profile(survey_user)
        form = builder.get_form(context, initial=initial)

    js_builder = JavascriptBuilder(spec)
    js = mark_safe(js_builder.get_javascript(context))

    return render_to_response('survey/extra_index.html', {
        'form': form,
        'js': js,
        'title': spec.survey.title
    }, context_instance=RequestContext(request))


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

    if confirmed == 'T':
        survey_user.deleted = True
        survey_user.save()
        
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
            survey_user.name = form.cleaned_data['name']
            survey_user.save()
            survey_user.user.add(request.user)

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

