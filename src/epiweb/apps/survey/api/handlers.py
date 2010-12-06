from piston.handler import BaseHandler
from epiweb.apps.survey.models import ( Profile, SurveyUser, Survey, User, epoch)
from epiweb.apps.survey.times import timedate_to_epochal
from utils import xmlify_spec, report_survey
from datetime import datetime
from re import sub
from base64 import b64encode

class EpiwebHandler(BaseHandler):
  allowed_methods = ('GET',)
  returnable = {'prot_v': '1.0', # EIP protocol version
                'serv': 99,      # Service type identifier
                'status': 0,     # Default status
                }

  # TODO Add code to restrict access to the api to certain users.
  # request.user must be in authorized_EIP_users
  authorized_EIP_users = ['ema']

  def check_args():
    "Each read should have a *args. Check against argslist."
    pass

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
          # Report timestamp as in milliseconds since 1970-01-01
          report_ts = timedate_to_epochal(pd)
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
    # TODO Ignore language for now
    ss = Survey.objects.all()
    most_recently_added_survey = ss[len(ss)-1]
    xml = xmlify_spec(most_recently_added_survey.specification)
    returnable.update({'survey': xml})
    return returnable

class GetImage(EpiwebHandler):
  """Takes type:int and uid:string. Returns image:string of png encoded base64
  """
  def read(self, request, type=None, uid=None):
    returnable = self.returnable.copy()
    print 'tu', type, uid
    if type:
      returnable.update({'type': type})
      if uid:
        sus = SurveyUser.objects.filter(global_id=uid)
        if sus:
          # TODO Put a real pic here!
          fd = open('src/epiweb/apps/survey/api/homer.png', 'r')
          raw = fd.read()
          enc = b64encode(raw)
          returnable.update({'image': enc})
        else:
          returnable.update({'status': 2,
                             'error_message': "uid '%s' not found" % uid})
      else:
        returnable.update({'status': 1,
                           'error_message': 'uid required'})
    else:
      returnable.update({'status': 3,
                         'error_message': 'type required'})
    return returnable

class Report(EpiwebHandler):
  """Post a report of completed surveys.
  """
  allowed_methods = ('POST',)

  def create(self, request):
    returnable = self.returnable.copy()
    if request.content_type:
      returnable.update(report_survey(request.data))
    else:
        returnable.update({'dummy': 'No statistics currently available'})
        # super(Report, self).create(request)
    return returnable

class GetLanguage(EpiwebHandler):
  """list of languages supported by the national IMS Server.
"""
  langs = { 'English': 1,
            'Italian': 2,
            'Portuguese': 3,
            'Dutch': 4,
            'German': 5,
            'French': 6,
            'Spanish': 7,
            'Swedish': 8 }
  # TODO Hard code the langs for the time being.
  supported_langs = ['Italian', 'Dutch']
  supported_lang_codes = [langs[c] for c in supported_langs]

  def read(self, request):
    returnable = self.returnable.copy()
    returnable.update({'lang': self.supported_lang_codes,
                       'languages': self.supported_langs})
    return returnable

class GetStatsHeaders(EpiwebHandler):
  """  """
  def read(self, request, language=None):
    returnable = self.returnable.copy()
    returnable.update({'dummy': 'No statistics currently available'})
    return returnable

class GetStatistic(EpiwebHandler):
  """  """
  def read(self, request, uid=None, id=None, lang=None):
    returnable = self.returnable.copy()
    returnable.update({'dummy': 'No statistics currently available'})
    return returnable