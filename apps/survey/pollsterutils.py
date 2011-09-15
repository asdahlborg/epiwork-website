from apps.pollster import models

def get_user_profile(user_id, global_id):
    try:
        intake = models.Survey.get_by_shortname('intake')
        profile = intake.get_last_participation_data(user_id, global_id)
        return profile
    except models.Survey.DoesNotExist:
        return None
    except StandardError, e:
        return None
