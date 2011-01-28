from piston.handler import BaseHandler
from piston.utils import rc
from epiweb.apps.survey.models import Profile, SurveyUser, Survey, User
from epiweb.apps.survey.times import timedate_to_epochal
from utils import ( xmlify_spec, report_survey,
                    code_hash, code_unhash,
                    GetError, )
from datetime import datetime
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
  """Takes uid (which is an activation code)
  Returns name, activation_codes, code, report_ts

  The EIP client refers to a 'uid'.  We call it an activation code or 'acode'.
  """

  def read(self, request, uid=None):
    returnable = self.returnable.copy()
    acode = uid
    try:
      if not acode:
        raise GetError(1, 'activation_code required')
      sus = SurveyUser.objects.filter(global_id=code_unhash(acode))
      if len(sus) == 0:
        raise GetError(2, "activation code '%s' not found" % acode)
      if len(sus) > 1:
        raise GetError(4, "activation code '%s' ambiguous" % acode)
      su = sus[0]
      sua = su.user.all()
      if len(sua) == 0:
        raise GetError(2, "activation code '%s' not found" % acode)
      if len(sua) > 1:
        raise GetError(4, "activation code '%s' ambiguous" % acode)
      u = sua[0]
      name = u.get_full_name()
      acodes = [code_hash(s.global_id)
                for s in SurveyUser.objects.filter(user=u)]
      pd = su.last_participation_date
      if pd:
        # Timestamp as in milliseconds since 1970-01-01
        report_ts = timedate_to_epochal(pd)
      else:
        report_ts = 0
      returnable.update({'name': name, 'a_uids': acodes,
                         'uid': acode, 'report_ts': report_ts})
    except GetError as inst:
      returnable.update(inst.dict)
    finally:
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
  """Takes image type and activation code.
  Returns image as a string of png encoded base64.
  """
  def read(self, request, image_type=None, uid=None):
    returnable = self.returnable.copy()
    acode = uid
    try:
      if not image_type:
        raise GetError(3, 'image type required')
      returnable.update({'type': image_type})
      if not acode:
        raise GetError(1, 'activation code required')
      sus = SurveyUser.objects.filter(global_id=code_unhash(acode))
      if len(sus) == 0:
        raise GetError(2, "activation code '%s' not found" % acode)
      if len(sus) > 1:
        raise GetError(4, "activation code '%s' ambiguous" % acode)
      # TODO Put a real pic here!
      fd = open('src/epiweb/apps/survey/api/homer.png', 'r')
      raw = fd.read()
      enc = b64encode(raw)
      returnable.update({'image': enc})
    except GetError as inst:
      returnable.update(inst.dict)
    finally:
      return returnable

class Report(EpiwebHandler):
  """Post a report of completed surveys.
  """
  allowed_methods = ('POST',)

  def create(self, request):
    returnable = self.returnable.copy()
    if request.content_type:
      reported = report_survey(request.data)
      if reported['status'] == 0:
        r = rc.CREATED
        r.write(reported)
        return r
      else:
        returnable.update(reported)
    else:
      returnable.update({'status': 5,
                         'error_message': 'incorrect content_type'})
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
