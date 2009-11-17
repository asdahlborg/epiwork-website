
from epiweb.apps.profile import models

from django.conf import settings
from epidb_client import EpiDBClient

try:
    import json
except ImportError:
    import simplejson as json

def _create_profile_data(survey, cleaned_data):
    data = {}
    for question in survey.questions:
        id = question.id
        private = question.private
        if not private:
            data[id] = cleaned_data[id]
    
    return data

def send_profile(user, survey, cleaned_data):
    client = EpiDBClient(settings.EPIDB_API_KEY)
    client.server = settings.EPIDB_SERVER
    data = _create_profile_data(survey, cleaned_data)
    from epiweb.apps.survey import utils as survey_utils
    global_id = survey_utils.get_global_id(user)
    print "Global id:", global_id
    res = client.profile_update(global_id, data)
    return res

def get_profile(user):
    try:
        profile = models.Profile.objects.get(user=user)
        return json.loads(profile.data)
    except models.Profile.DoesNotExist:
        return None

def save_profile(user, data):
    try:
        profile = models.Profile.objects.get(user=user)
    except models.Profile.DoesNotExist:
        profile = models.Profile()
        profile.user = user

    profile.data = json.dumps(data)
    profile.save()

