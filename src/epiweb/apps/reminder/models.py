import datetime

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class Reminder(models.Model):
    user = models.ForeignKey(User, unique=True)
    last_reminder = models.DateTimeField()
    next_reminder = models.DateField()
    wday = models.IntegerField()
    active = models.BooleanField()

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

