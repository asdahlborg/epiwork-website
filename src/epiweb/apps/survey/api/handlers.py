from piston.handler import BaseHandler
from epiweb.apps.survey.models import ( Profile, SurveyUser, Survey, User, epoch)
from datetime import datetime
from re import sub
from utils import xmlify_spec

class EpiwebHandler(BaseHandler):
  allowed_methods = ('GET',)         
  returnable = {'status': 0, 'prot_v': "1.0", 'serv': 99}
  
class GetUserProfile(EpiwebHandler):
  """Takes global_id
  Returns name, a_uids, code, report_ts
  """
  
  def read(self, request, uid=None):
    returnable = self.returnable.copy()
    if uid:
      sus = SurveyUser.objects.filter(global_id=uid)
      if sus:
        su = sus[0]
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
        returnable.update({'name': name, 'a_uids': a_uids,
                                'code': code, 'report_ts': report_ts})
      else:
        returnable.update({'status': 2,
                                'error_message': "uid '%s' not found" % uid})
    else:
      returnable.update({'status': 1,
                              'error_message': 'uid required'})
    return returnable

class GetReportSurvey(EpiwebHandler):
  """Takes language int
  Returns survey in XML format
  """

  def read(self, request, language=None):
    returnable = self.returnable.copy()
    # Ignore language for now
    ss = Survey.objects.all()
    most_recently_added_survey = ss[len(ss)-1]
    print most_recently_added_survey.survey_id
    xml = xmlify_spec(most_recently_added_survey.specification)
    print xml
    returnable.update({'survey': xml})
    return returnable

class GetImage(EpiwebHandler):
  """Takes type:int and uid:string
  Returns image:string of png encoded base64
  """
  def read(self, request, type=None, uid=None):
    returnable = self.returnable.copy()
    returnable.update({'dummy': 42})
    return returnable

class Report(EpiwebHandler):
  """ """
  allowed_methods = ('POST',)         

  def read(self, request, uid=None, reports=None):
    returnable = self.returnable.copy()
    returnable.update({'dummy': 42})
    return returnable

class GetLanguage(EpiwebHandler):
  """  """
  def read(self, request):
    returnable = self.returnable.copy()
    returnable.update({'dummy': 42})
    return returnable

class GetStatsHeaders(EpiwebHandler):
  """  """
  def read(self, request, language=None):
    returnable = self.returnable.copy()
    returnable.update({'dummy': 42})
    return returnable

class GetStatistic(EpiwebHandler):
  """  """
  def read(self, request, uid=None, id=None, lang=None):
    returnable = self.returnable.copy()
    returnable.update({'dummy': 42})
    return returnable
