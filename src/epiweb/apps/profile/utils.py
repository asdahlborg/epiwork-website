
from epiweb.apps.profile import models

try:
    import json
except ImportError:
    import simplejson as json

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

