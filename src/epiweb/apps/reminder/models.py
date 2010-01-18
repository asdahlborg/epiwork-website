import datetime

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

_ = lambda x: x

# Reference: http://docs.python.org/library/time.html
# - tm_wday => range [0,6], Monday is 0
MONDAY = 0
TUESDAY = 1
WEDNESDAY = 2
THURSDAY = 3
FRIDAY = 4
SATURDAY = 5
SUNDAY = 6

DAYS = (
    (MONDAY, _('Monday')),
    (TUESDAY, _('Tuesday')),
    (WEDNESDAY, _('Wednesday')),
    (THURSDAY, _('Thursday')),
    (FRIDAY, _('Friday')),
    (SATURDAY, _('Saturday')),
    (SUNDAY, _('Sunday'))
)

class Reminder(models.Model):
    user = models.ForeignKey(User, unique=True)
    last_reminder = models.DateTimeField()
    next_reminder = models.DateField()
    wday = models.IntegerField(choices=DAYS, verbose_name="Day",
                               default=MONDAY)
    active = models.BooleanField()

    def __unicode__(self):
        return self.user.username

def add_reminder(sender, **kwargs):
    instance = kwargs.get('instance', None)
    try:
        reminder = Reminder.objects.get(user=instance)
    except Reminder.DoesNotExist:
        now = datetime.datetime.now()
        next = now + datetime.timedelta(days=7)

        reminder = Reminder()
        reminder.user = instance
        reminder.last_reminder = now
        reminder.next_reminder = next
        reminder.wday = now.timetuple().tm_wday
        reminder.active = True
        reminder.save()

post_save.connect(add_reminder, sender=User)

