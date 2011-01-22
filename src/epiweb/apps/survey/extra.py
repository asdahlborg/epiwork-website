### Django CMS setup for extra survey.

from django.core.exceptions import ObjectDoesNotExist 
from django.conf import settings
from cms.models.titlemodels import Title
from cms.models.pagemodel import Page
from .models import Survey
from .utils import UnknownSurveyError

# Switch on/off the extra survey functionality.
if settings.EXTRA_SURVEY:
  t = Title.objects.get(slug='extra-survey')
  p = t.page
  try:
    s = Survey.objects.get(survey_id=settings.EXTRA_SURVEY)
    t.title = s.title
  except ObjectDoesNotExist:
    raise UnknownSurveyError(settings.EXTRA_SURVEY)
  p.in_navigation = settings.EXTRA_SURVEY
  p.published = settings.EXTRA_SURVEY
  t.save()
  p.save()
