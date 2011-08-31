import datetime
import smtplib
from traceback import format_exc

from django.db.models import Q
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template import Context, loader, Template
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.html import strip_tags
from django.contrib.sites.models import Site
from django.contrib.auth.models import User

import loginurl.utils

from .models import get_reminders_for_users, UserReminderInfo, ReminderError

def create_message(user, message):
    t = Template(message)
    c = Context({
        'url': get_url(user),
        'first_name': user.first_name,
        'last_name': user.last_name,
    })
    inner = t.render(c)

    t = loader.get_template('reminder/message.html')
    return inner, t.render(Context({
        'inner': inner,
        'MEDIA_URL': get_media_url(),
    }))

def send_reminders():
    now = datetime.datetime.now()

    i = -1
    for i, (user, message) in enumerate(get_reminders_for_users(now, User.objects.all())):
        send(now, user, message)

    return i + 1

def get_media_url():
    site = Site.objects.get_current()
    return 'http://%s%s' % (site.domain, settings.MEDIA_URL)

def get_url(user):
    return get_login_url(user, get_survey_url())

def get_login_url(user, next):
    expires = datetime.datetime.now() + datetime.timedelta(days=7)

    usage_left = 0
    key = loginurl.utils.create(user, usage_left, expires, next)

    domain = Site.objects.get_current()
    path = reverse('loginurl-index').strip('/')
    loginurl_base = 'http://%s/%s' % (domain, path)

    return '%s/%s' % (loginurl_base, key.key)

def get_survey_url():
    domain = Site.objects.get_current()
    path = reverse('apps.survey.views.index')
    return 'http://%s%s' % (domain, path)

def send(now, user, message):
    text_base, html_content = create_message(user, message.message)
    text_content = strip_tags(text_base)

    msg = EmailMultiAlternatives(
        message.subject,
        text_content,
        "%s <%s>" % (message.sender_name, message.sender_email),
        [user.email],
    )

    msg.attach_alternative(html_content, "text/html")

    try:
        msg.send()
    except Exception, e:
        ReminderError.objects.create(
            user=user,
            message=unicode(e),
            traceback=format_exc(),
        )

    info = UserReminderInfo.objects.get(user=user)
    info.last_reminder = now
    info.save()
