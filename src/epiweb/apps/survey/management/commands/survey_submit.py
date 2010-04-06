from django.core.management.base import NoArgsCommand

try:
    import cPickle as pickle
except ImportError:
    import pickle

class Command(NoArgsCommand):
    help = 'Send all survey responses and user profiles waiting in queue.'

    def handle_noargs(self, **options):
        self.send_profiles(**options)
        self.send_responses(**options)

    def send_profiles(self, **options):
        from django.conf import settings
        from epiweb.apps.survey.models import ProfileSendQueue
        from epidb_client import EpiDBClient, ResponseError, \
                                 InvalidResponseError
        
        client = EpiDBClient(settings.EPIDB_API_KEY)
        if hasattr(settings, 'EPIDB_SERVER') and settings.EPIDB_SERVER is not None:
            client.server = settings.EPIDB_SERVER

        total = 0
        total_sent = 0
        total_error = 0

        surveys = ProfileSendQueue.objects.order_by('date')
        for survey in surveys:
            date = survey.date
            profile_survey_id = survey.survey_id
            user_id = survey.user_id
            answers = pickle.loads(str(survey.answers))

            try:
                res = client.profile_update(user_id, profile_survey_id, 
                                            answers, date)
                survey.set_sent(res['id'])
                total_sent += 1
            except InvalidResponseError, e:
                total_error += 1
                print e
            except ResponseError, e:
                total_error += 1
                print e

            total += 1

        verbosity = int(options.get('verbosity', 1))
        if total_error > 0 or verbosity > 0:
            print "Profiles: %d sent, %d error." % (total_sent, total_error)

    def send_responses(self, **options):
        from django.conf import settings
        from epiweb.apps.survey.models import ResponseSendQueue
        from epidb_client import EpiDBClient, ResponseError, \
                                 InvalidResponseError
        
        client = EpiDBClient(settings.EPIDB_API_KEY)
        if hasattr(settings, 'EPIDB_SERVER') and settings.EPIDB_SERVER is not None:
            client.server = settings.EPIDB_SERVER

        total = 0
        total_sent = 0
        total_error = 0

        surveys = ResponseSendQueue.objects.order_by('date')
        for survey in surveys:
            date = survey.date
            survey_id = survey.survey_id
            user_id = survey.user_id
            answers = pickle.loads(str(survey.answers))

            try:
                res = client.response_submit(user_id, survey_id, 
                                             answers, date)
                survey.set_sent(res['id'])
                total_sent += 1
            except InvalidResponseError, e:
                total_error += 1
            except ResponseError, e:
                total_error += 1

            total += 1

        verbosity = int(options.get('verbosity', 1))
        if total_error > 0 or verbosity > 0:
            print "Responses: %d sent, %d error." % (total_sent, total_error)

