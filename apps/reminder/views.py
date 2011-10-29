from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings

from .models import UserReminderInfo, get_upcoming_dates, get_prev_reminder
from .send import create_message, send

@login_required
def unsubscribe(request):
    if request.method == "POST":
        info, _ = UserReminderInfo.objects.get_or_create(user=request.user, defaults={'active': True})
        info.active = False
        info.save()
        return render_to_response('reminder/unsubscribe_successful.html', locals(), context_instance=RequestContext(request))
    return render_to_response('reminder/unsubscribe.html', locals(), context_instance=RequestContext(request))
    
@staff_member_required
def overview(request):
    upcoming = [{
        'date': d,
        'description': description,
    } for d, description in get_upcoming_dates(datetime.now())]

    return render(request, 'reminder/overview.html', locals())

@staff_member_required
def manage(request, year, month, day, hour, minute):
    reminder_dict = get_prev_reminder(datetime(*map(int, [year, month, day, hour, minute, 59])))
    if not reminder_dict:
        return HttpResponse("There are no newsletters or reminders configured yet. Make sure to do so")
    reminder = _reminder(reminder_dict, request.user)
    if not reminder:
        return HttpResponse("There is no reminder in your current language configured. Make sure to add a translation")

    if request.method == "POST":
        sent = True
        send(None, request.user, reminder)
        
    return render(request, 'reminder/manage.html', locals())

@staff_member_required
def preview(request, year, month, day, hour, minute):
    reminder_dict = get_prev_reminder(datetime(*map(int, [year, month, day, hour, minute, 59])))
    if not reminder_dict:
        return HttpResponse("There are no newsletters or reminders configured yet. Make sure to do so")
    reminder = _reminder(reminder_dict, request.user)
    if not reminder:
        return HttpResponse("There is no reminder in your current language configured. Make sure to add a translation")

    text_base, html_content = create_message(request.user, reminder.message)
    return HttpResponse(html_content)

def _reminder(reminder_dict, user):
    info, _ = UserReminderInfo.objects.get_or_create(user=user, defaults={'active': True})
    language = info.get_language()

    if not language in reminder_dict:
        language = settings.LANGUAGE_CODE
    if not language in reminder_dict:
        return None
    
    reminder = reminder_dict[language]

    return reminder
