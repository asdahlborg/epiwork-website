from . import models
from django.conf import settings

def get_user_profile(user_id, global_id):
    try:
        shortname = settings.POLLSTER_USER_PROFILE_SURVEY
        survey = models.Survey.get_by_shortname(shortname)
        profile = survey.get_last_participation_data(user_id, global_id)
        return profile
    except models.Survey.DoesNotExist:
        return None
    except StandardError, e:
        return None
