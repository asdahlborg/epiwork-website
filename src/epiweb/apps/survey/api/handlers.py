from piston.handler import BaseHandler
from epiweb.apps.survey.models import ( Profile, SurveyUser, Survey, User, epoch)
from datetime import datetime
from re import sub
from utils import xmlify_spec

class EpiwebHandler(BaseHandler):
  allowed_methods = ('GET',)
  returnable = {'prot_v': '1.0', # EIP protocol version
                'serv': 99,      # Service type identifier
                'status': 0,     # Default status
                }

  # Add code to restrict access to the api to certain users.
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
  """
  {
  "prot_v"      : <<string>>,
  "serv"        : <<int>>,
  "uid"         : <<string>>,
  "reports" [{ "uid"           : <<string>>,
               "surv_v"        : <<string>>,
               "ts"            : <<long>>,
               "data"  [{ "id"        : <<int>>,
                          "value"     : [<<<string>>]
                       }]
            }]
       }
"""
  allowed_methods = ('POST',)
  fields =('prot_v', 'serv', 'uid',
           'reports', ('uid', 'surv_v', 'ts', 'data', ('id', 'value')))

  def create(self, request):
    print 'POSTting'
    print 1, request.POST
    print 2, request.content_type
    print 3, dir(request)
    print 4, dir(request.POST)
    print 5, request.POST.keys(), len(request.POST.keys())
    print 'rpd', request.raw_post_data
    # print request.POST.data
    # print help(request.parse_file_upload)

    if request.content_type:
      data = request.data
      print data
#        print 'dsm', data, self.model

#        em = self.model(title=data['title'], content=data['content'])
#        em.save()
#
#        for comment in data['comments']:
#            Comment(parent=em, content=comment['content']).save()

      returnable = self.returnable.copy()
      returnable.update({'dummy': 'No statistics currently available'})
      return returnable
    else:
        super(GetStatistic, self).create(request)

    if request.content_type == 'application/json':
      print 'got json, json parse this', request.raw_post_data
    elif not request.content_type:
      print 'got parameter list, parse from request.POST', request.POST
    print 'done'

    # self.check_args()
    returnable = self.returnable.copy()
    returnable.update({'dummy': 'No statistics currently available'})
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
  # Hard code the langs for the time being.
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
