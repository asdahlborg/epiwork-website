from piston.handler import BaseHandler
from epiweb.apps.survey.models import ( Profile, SurveyUser, Survey, User, epoch)
from datetime import datetime
from re import sub

class GetUserProfile(BaseHandler):
  """Takes global_id
  Returns name, a_uids, code, report_ts
  """
  allowed_methods = ('GET',)         
  
  def read(self, request, uid=None):
    print request.GET, uid
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

class GetReportSurvey(BaseHandler):
  """Takes language int
  Returns survey in XML format
  """
  allowed_methods = ('GET',)         

  def read(self, request, uid=None):
    pass
