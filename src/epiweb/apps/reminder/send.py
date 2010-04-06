import datetime
import smtplib

from django.db.models import Q
from django.core.mail import EmailMessage
from django.conf import settings
from django.template import Context, loader
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.conf import settings

from epiweb.apps.reminder.models import Reminder

def create_subject(user):
    t = loader.get_template('reminder/subject.txt')
    c = Context({'user': user})

    text = t.render(c)
    text = " ".join(text.split("\n"))
    text = text.strip()

    return text

def create_message(url, user):
    t = loader.get_template('reminder/message.txt')
    c = Context({'url': url,
                 'user': user})

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

def get_url(user):
    url = _get_url_survey()
    if settings.REMINDER_USE_LOGINURL:
        return _get_url_loginurl(user, url)
    return url

_loginurl_base = None
def _get_url_loginurl(user, next):
    from datetime import datetime, timedelta
    import loginurl.utils
    expires = datetime.now() + \
              timedelta(days=settings.REMINDER_LOGINURL_EXPIRES)
    usage_left = 0
    key = loginurl.utils.create(user, usage_left, expires, next)

    global _loginurl_base
    if _loginurl_base is None:
        domain = Site.objects.get_current()
        path = reverse('loginurl-index').strip('/')
        _loginurl_base = 'http://%s/%s' % (domain, path)

    url = '%s/%s' % (_loginurl_base, key.key)
    return url

_url = None
def _get_url_survey():
    global _url
    if _url is None:
        domain = Site.objects.get_current()
        path = reverse('epiweb.apps.survey.views.index')
        _url = 'http://%s%s' % (domain, path)
    return _url

def send_to(item):
    url = get_url(item.user)
    now = datetime.datetime.now()

    try:
        name = item.user.first_name, item.user.last_name

        email = item.user.email
        subject = create_subject(item.user)
        message = create_message(url, item.user)
        next = determine_next(now, item.wday)

        mail = EmailMessage(subject, message, settings.REMINDER_FROM, (email,))
        if hasattr(settings, 'REMINDER_HTML') and settings.REMINDER_HTML:
            mail.content_subtype = 'html'
        mail.send()

        item.last_reminder = datetime.datetime.now()
        item.next_reminder = next
        item.save()

        return True
    except smtplib.SMTPException:
        return False

