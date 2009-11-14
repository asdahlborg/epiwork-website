from django.db import models
from django.contrib.auth.models import User

class Survey(models.Model):
    created = models.DateTimeField()
    survey_id = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    definition = models.TextField()

class History(models.Model):
    user = models.ForeignKey(User, unique=True)
    date = models.DateTimeField(auto_now_add=True)
    survey = models.ForeignKey(Survey)
    epidb_id = models.CharField(max_length=36, null=True)

class Profile(models.Model):
    user = models.ForeignKey(User, unique=True)
    last_survey = models.ForeignKey(History)
    last_survey_date = models.DateTimeField()

class Unsaved(models.Model):
    history = models.ForeignKey(History)
    date = models.DateTimeField()
    data = models.TextField()
