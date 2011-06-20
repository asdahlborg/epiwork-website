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

from epiweb.apps.survey import utils, models, forms
from .survey import ( Specification,
                      FormBuilder,
                      JavascriptBuilder,
                      get_survey_context, )
import extra

_ = lambda x: x

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
    return render_to_response('survey/thanks.html',
        context_instance=RequestContext(request))

@login_required
def select_user(request, template='survey/select_user.html'):
    next = request.GET.get('next', None)
    if next is None:
        next = reverse(index)

    users = models.SurveyUser.objects.filter(user=request.user)
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
        request.user.message_set.create(
            message=_('You have to fill your profile data first.'))
        url = reverse('epiweb.apps.survey.views.profile_index')
        url_next = reverse('epiweb.apps.survey.views.index')
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
            request.user.message_set.create(
                message=_('One or more questions have empty or invalid ' \
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

    spec = utils.load_specification(settings.SURVEY_PROFILE_ID)
    context = get_survey_context(survey_user)
    builder = FormBuilder(spec)

    if request.method == 'POST':
        form = builder.get_form(context, request.POST)
        if form.is_valid():
            utils.add_profile_queue(survey_user, spec, form.cleaned_data)
            data = utils.format_profile_data(spec, form.cleaned_data)
            utils.save_profile(survey_user, spec.survey.id, data)
            utils.save_local_profile(survey_user, data)
            utils.save_response_locally(survey_user.name,
                                        spec.survey.id,
                                        data,
                                        None)

            next = request.GET.get('next', None)
            if next is not None:
                url = next
            else:
                url = reverse('epiweb.apps.survey.views.profile_index')
            url = '%s?gid=%s' % (url, survey_user.global_id)

            request.user.message_set.create(message=_('Profile saved.'))
            return HttpResponseRedirect(url)

        else:
            request.user.message_set.create(
                message=_('One or more questions have empty or invalid ' \
                          'answer. Please fix it first.'))

    else:
        initial = utils.get_user_profile(survey_user)
        form = builder.get_form(context, initial=initial)

    js_builder = JavascriptBuilder(spec)
    js = mark_safe(js_builder.get_javascript(context))

    return render_to_response('survey/profile_index.html', {
        'form': form,
        'js': js
    }, context_instance=RequestContext(request))


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
                url = reverse('epiweb.apps.survey.views.extra_index')
            url = '%s?gid=%s' % (url, survey_user.global_id)

            return HttpResponseRedirect(reverse(thanks))

        else:
            request.user.message_set.create(
                message=_('One or more questions have empty or invalid ' \
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
def people_add(request):
    if request.method == 'POST':
        form = forms.AddPeople(request.POST)
        if form.is_valid():
            survey_user = models.SurveyUser()
            survey_user.name = form.cleaned_data['name']
            survey_user.save()
            survey_user.user.add(request.user)

            request.user.message_set.create(
                message=_('A new person has been added.'))

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
    users = models.SurveyUser.objects.filter(user=request.user)
    return render_to_response('survey/people.html', {'people': users},
                              context_instance=RequestContext(request))

