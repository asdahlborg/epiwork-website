from piston.handler import BaseHandler
from epiweb.apps.survey.models import ( Profile, SurveyUser, Survey, User, epoch)
from datetime import datetime
from re import sub
from utils import xmlify_spec

class EpiwebHandler(BaseHandler):
  allowed_methods = ('GET',)         

class GetUserProfile(EpiwebHandler):
  """Takes global_id
  Returns name, a_uids, code, report_ts
  """
  
  def read(self, request, uid=None):
    if 'uid':
      sus = SurveyUser.objects.filter(global_id=uid)
      if sus:
        su = sus[0]
      else:
        return {'error': 'uid %s not found' % uid}
      u = su.user.all()[0]
      name = u.get_full_name()
      a_uids = [su.global_id for s in SurveyUser.objects.filter(user=u)]

      # 5-digit code is generated from global_id:
      # divide by 1e5 and pad left with zeros
      code = '%05d' % (int(sub('-', '', su.global_id), 16) % 1e5)

      pd = su.last_participation_date
      if pd:
        # Report as time in milliseconds since 1970-01-01
        delta = pd - epoch()
        report_ts = (delta.days * 24 * 60 * 60 + delta.seconds) * 1000
      else:
        report_ts = 0

      return {'name': name, 'a_uids': a_uids,
              'code': code, 'report_ts': report_ts}
    else:
      return {'error': 'uid required'}

class GetReportSurvey(EpiwebHandler):
  """Takes language int
  Returns survey in XML format
  """

  def read(self, request, language=None):
    # Ignore language for now
    ss = Survey.objects.all()
    most_recently_added_survey = ss[len(ss)-1]
    print most_recently_added_survey.survey_id
    xml = xmlify_spec(most_recently_added_survey.specification)
    # print xml
    return {'survey': xml}

class GetImage(EpiwebHandler):
  """Takes type:int and uid:string
  Returns image:string of png encoded base64
  """
  def read(self, request, type=None, uid=None):
    return 42

class Report(EpiwebHandler):
  """
  """
  def read(self, request, uid=None, reports=None):
    return 42

class GetLanguage(EpiwebHandler):
  """
  """
  def read(self, request):
    return 42

class GetStatsHeaders(EpiwebHandler):
  """
  """
  def read(self, request, language=None):
    return 42

class GetStatistic(EpiwebHandler):
  """
  """
  def read(self, request, uid=None, id=None, lang=None):
    return 42

