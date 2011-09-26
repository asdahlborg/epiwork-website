from piston.handler import BaseHandler
from piston.utils import rc
from apps.survey.models import Profile, SurveyUser, Survey, User
from apps.survey.times import timedate_to_epochal
from utils import xmlify_spec, report_survey, code_hash, code_unhash, GetError
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
    # for clarity: the line below is not implemented in any way.
    authorized_EIP_users = ['ema']

    csrf_exempt = True # this is the default, but it's provided here for explicity
    # this depends on Django-piston with at least the following changeset
    # https://bitbucket.org/jespern/django-piston/changeset/adeef486579b

    def check_args():
        "Each read should have a *args. Check against argslist."
        pass

class GetUserProfile(EpiwebHandler):
    """Takes uid (which is an activation code)
    Returns name, activation_codes, code, report_ts

    The EIP client refers to a 'uid'.    We call it an activation code or 'acode'.
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
            name = su.name
            if su.user is None:
                raise GetError(2, "no django-users for activation code '%s'" % acode)
            u = su.user
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
        # language parameter is ignored, but kept for backwards compatability
        ss = Survey.objects.all()
        most_recently_added_survey = ss[len(ss)-1]
        xml = xmlify_spec(most_recently_added_survey.specification)
        returnable.update({'survey': xml})
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
                return returnable
            else:
                returnable.update(reported)
        else:
            returnable.update({'status': 5, 'error_message': 'incorrect content_type'})
        return returnable

