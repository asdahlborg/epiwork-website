import datetime
import smtplib

from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from django.template import Context, loader

from epiweb.apps.reminder.models import Reminder

def create_subject(first_name, last_name=None):
    t = loader.get_template('reminder/subject.txt')
    c = Context({'first_name': first_name,
                 'last_name': last_name})

    text = t.render(c)
    text = " ".join(text.split("\n"))
    text = text.strip()

    return text

def create_message(url, email, first_name, last_name=None):
    t = loader.get_template('reminder/message.txt')
    c = Context({'url': url,
                 'first_name': first_name,
                 'last_name': last_name,
                 'email': email})

    return t.render(c)

def determine_next(now, wday):
    year, week = map(lambda x: int(x), 
                     now.strftime('%Y %W').split())

    # Input's wday uses 0 = Monday (comes from weekday())
    # but strptime's uses 0 = Sunday
    # so, shifting is needed
    wday = (wday + 1) % 7
    next = datetime.datetime.strptime('%d %d %d' % (year, week+1, wday),
                                      '%Y %W %w')
    return next

def send_reminder():
    now = datetime.datetime.now()
    last = now - datetime.timedelta(days=7)

    items = Reminder.objects.filter(active=True, 
                                    next_reminder__lte=now,
                                    last_reminder__lte=last)

    url = None

    fail = []
    succeed = []
    for item in items:
        res = send_to(item)
        if res:
            succeed.append(item)
        else:
            fail.append(item)

    return len(succeed), len(fail)

def send_to(item):
    url = 'http://example.com/survey/'
    now = datetime.datetime.now()

    try:
        name = item.user.first_name, item.user.last_name

        email = item.user.email
        subject = create_subject(*name)
        message = create_message(url, email, *name)
        next = determine_next(now, item.wday)

        send_mail(subject, message, settings.REMINDER_FROM, (email,))

        item.last_reminder = datetime.datetime.now()
        item.next_reminder = next
        item.save()

        return True
    except smtplib.SMTPException:
        return False

