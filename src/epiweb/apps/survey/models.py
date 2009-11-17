from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

import uuid

class Survey(models.Model):
    created = models.DateTimeField()
    survey_id = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    definition = models.TextField()

class History(models.Model):
    user = models.ForeignKey(User)
    date = models.DateTimeField(auto_now_add=True)
    survey = models.ForeignKey(Survey)
    epidb_id = models.CharField(max_length=36, null=True)

class Info(models.Model):
    user = models.ForeignKey(User, unique=True)
    last_survey = models.ForeignKey(History)
    last_survey_date = models.DateTimeField()

class Unsaved(models.Model):
    history = models.ForeignKey(History)
    date = models.DateTimeField()
    data = models.TextField()

class EpiDBUser(models.Model):
    user = models.ForeignKey(User, unique=True)
    global_id = models.CharField(max_length=36)

def add_global_id(sender, **kwargs):
    instance = kwargs.get('instance', None)
    print repr(instance)
    try:
        user = EpiDBUser.objects.get(user=instance)
    except EpiDBUser.DoesNotExist:
        user = EpiDBUser()
        user.user = instance
        user.global_id = str(uuid.uuid4())
        print "Global id:", user.global_id
        user.save()
        
post_save.connect(add_global_id, sender=User)
