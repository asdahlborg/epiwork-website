from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

import uuid

class Survey(models.Model):
    survey_id = models.CharField(max_length=50, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    definition = models.TextField()
    hash = models.CharField(max_length=40)
    active = models.BooleanField()

    def __unicode__(self):
        return '%s - %s' % (self.survey_id, self.title)

class Participation(models.Model):
    user = models.ForeignKey(User)
    survey = models.ForeignKey(Survey)
    date = models.DateTimeField(auto_now_add=True)
    epidb_id = models.CharField(max_length=36, null=True)
    previous_participation = models.ForeignKey('self', null=True)
    previous_participation_date = models.DateTimeField(null=True)

    def __unicode__(self):
        return '%s (%s)' % (self.user.username, self.date)

    class Meta:
        verbose_name_plural = 'Survey participation log'

class UnsentResponse(models.Model):
    participation = models.ForeignKey(Participation)
    date = models.DateTimeField()
    data = models.TextField()

class SurveyUser(models.Model):
    user = models.ForeignKey(User, unique=True)
    global_id = models.CharField(max_length=36)
    last_participation = models.ForeignKey(Participation, null=True)
    last_participation_date = models.DateTimeField(null=True)

class Profile(models.Model):
    user = models.ForeignKey(User, unique=True)
    created = models.DateTimeField(null=True)
    updated = models.DateTimeField(null=True)
    valid = models.BooleanField(default=False)
    data = models.TextField(null=True, blank=True)

    def save(self):
        if self.valid:
            self.updated = datetime.now()
            if self.created is None:
                self.created = self.updated

        super(Profile, self).save()

    class Meta:
        verbose_name_plural = 'User profile'

def add_global_id(sender, **kwargs):
    instance = kwargs.get('instance', None)
    try:
        user = SurveyUser.objects.get(user=instance)
    except SurveyUser.DoesNotExist:
        user = SurveyUser()
        user.user = instance
        user.global_id = str(uuid.uuid4())
        user.save()

def add_empty_profile(sender, **kwargs):
    instance = kwargs.get('instance', None)
    try:
        profile = Profile.objects.get(user=instance)
    except Profile.DoesNotExist:
        profile = Profile()
        profile.user = instance
        profile.valid = False
        profile.created = None
        profile.updated = None
        profile.data = None
        profile.save()

post_save.connect(add_global_id, sender=User)
post_save.connect(add_empty_profile, sender=User)

