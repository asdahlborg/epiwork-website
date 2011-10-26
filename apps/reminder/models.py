import datetime

from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _
from django.conf import settings

from nani.models import TranslatableModel, TranslatedFields

# A short word on terminology:
# "Reminder" may refer to a NewsLetter object, or simply a placeholder
# that's based on the is_default_reminder NewsLetterTemplate

NO_INTERVAL = -1

class UserReminderInfo(models.Model):
    user = models.ForeignKey(User, unique=True)
    last_reminder = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField()
    language = models.CharField(max_length=5, blank=True, null=True)

    def __unicode__(self):
        return self.user.username

    def get_language(self):
        if not self.language:
            return settings.LANGUAGE_CODE
        return self.language

class ReminderSettings(models.Model):
    site = models.OneToOneField(Site)
    send_reminders = models.BooleanField(_("Send reminders"), help_text=_("Check this box to send reminders"))
    interval = models.IntegerField(_("Interval"), choices=((7 ,_("Weekly")), (14,_("Bi-weekly")), (NO_INTERVAL, _("Don't send reminders at a fixed interval"))), null=True, blank=True)
    begin_date = models.DateTimeField(_("Begin date"), help_text=_("Date & time of the first reminder and point of reference for subsequent reminders; (Time zone: MET)"), null=True, blank=True)

    def __unicode__(self):
        return _(u"Reminder settings")

class NewsLetterTemplate(TranslatableModel):
    is_default_reminder = models.BooleanField(_("Is default reminder"), help_text=_("If this option is checked this template is the standard template for reminder emails."))
    is_default_newsitem = models.BooleanField(_("Is default newsitem"), help_text=_("If this option is checked this template is the standard template for new news items."))
    sender_email = models.EmailField(_("Sender email"), help_text="Only use email addresses for your main domain to ensure deliverability")
    sender_name = models.CharField(_("Sender name"), max_length=255)

    translations = TranslatedFields(
        subject = models.CharField(max_length=255),
        message = models.TextField(help_text="The strings {{ url }} and {{ unsubscribe_url }} may be used to refer to the profile url and unsubscribe url."),
    )

    def __unicode__(self):
        return self.subject

class NewsLetter(TranslatableModel):
    date = models.DateTimeField(_("Date"), unique=True, choices=[])

    sender_email = models.EmailField(_("Sender email"), help_text="Only use email addresses for your main domain to ensure deliverability")
    sender_name = models.CharField(_("Sender name"), max_length=255)

    translations = TranslatedFields(
        subject = models.CharField(max_length=255),
        message = models.TextField(help_text="The strings {{ url }} and {{ unsubscribe_url }} may be used to refer to the profile url and unsubscribe url."),
    )

    def __unicode__(self):
        return self.subject

    class Meta:
        ordering = ("-date",)

class MockNewsLetter(object):
    def __init__(self):
        self.date = self.sender_email= self.sender_name = self.subject = self.message = None

class ReminderError(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User)
    message = models.CharField(max_length=255)
    traceback = models.TextField()

    def __unicode__(self):
        return self.message

    class Meta:
        ordering = ("-timestamp",)

    def email(self):
        return self.user.email

def get_settings():
    if ReminderSettings.objects.count() == 0:
        return None
    return ReminderSettings.objects.all()[0] 

def get_upcoming_dates(now):
    settings = get_settings()
    if not settings or not settings.send_reminders or not settings.begin_date:
        raise StopIteration()

    to_yield = 5
    current = settings.begin_date

    while to_yield > 0:
        if current >= now:
            diff = current - now
            days = diff.days % 7
            weeks = diff.days / 7 
            if weeks == 0:
                yield current, _("%(current)s (in %(days)s days)") % locals()
            else:
                yield current, _("%(current)s (in %(weeks)s weeks)") % locals()
            to_yield -= 1
        current += datetime.timedelta(settings.interval)

def get_default_for_reminder(language):
    if NewsLetterTemplate.objects.language(language).filter(is_default_reminder=True).count() == 0:
        return None
    return NewsLetterTemplate.objects.language(language).filter(is_default_reminder=True)[0]

def get_default_for_newsitem(language):
    if NewsLetterTemplate.objects.language(language).filter(is_default_newsitem=True).count() == 0:
        return None
    return NewsLetterTemplate.objects.language(language).filter(is_default_newsitem=True)[0]

def get_prev_reminder_date(now):
    """Returns the date of the previous reminder or None if there's no
    such date"""

    settings = get_settings()

    if not settings or not settings.send_reminders or not settings.begin_date or now < settings.begin_date:
        return None

    if settings.interval == NO_INTERVAL:
        qs = NewsLetter.objects.filter(date__lte=now).exclude(date__gt=now).order_by("-date")
        if qs.count() == 0:
            return None
        return qs[0].date

    current = settings.begin_date
    prev = settings.begin_date

    while True:
        if current >= now:
            return prev
        prev = current
        current += datetime.timedelta(settings.interval)

def get_prev_reminder(now):
    """Returns the reminder (newsletter/tempate) to send at a given moment
    as a dict with languages as keys, or None if there is no such reminder"""

    prev_date = get_prev_reminder_date(now)
    if prev_date is None:
        return None

    if NewsLetter.objects.filter(date=prev_date).count():
        result = {}
        for language, name in settings.LANGUAGES:
            if NewsLetter.objects.language(language).filter(date=prev_date):
                result[language] = NewsLetter.objects.language(language).get(date=prev_date)
        return result

    result = {}
    for language, name in settings.LANGUAGES:
        template = get_default_for_reminder(language)
        if template is None:
            continue

        newsletter = MockNewsLetter()
        newsletter.date = prev_date
        newsletter.sender_email = template.sender_email
        newsletter.sender_name = template.sender_name
        newsletter.subject = template.subject
        newsletter.message = template.message
        result[language] = newsletter

    return result

def get_reminders_for_users(now, users):
    reminder_dict = get_prev_reminder(now)
    if not reminder_dict:
        raise StopIteration()

    for user in users:
        info, _ = UserReminderInfo.objects.get_or_create(user=user, defaults={'active': True})
        if not info.active:
            continue

        language = info.get_language()
        if not language in reminder_dict:
            language = settings.LANGUAGE_CODE
        
        reminder = reminder_dict[language]
        if info.last_reminder is None or info.last_reminder < reminder.date:
            yield user, reminder

