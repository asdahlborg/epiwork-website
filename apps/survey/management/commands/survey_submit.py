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
        from apps.survey import utils
        total_sent, total_error = utils.flush_profile_queue()

        verbosity = int(options.get('verbosity', 1))
        if total_error > 0 or verbosity > 0:
            print "Profiles: %d sent, %d error." % (total_sent, total_error)

    def send_responses(self, **options):
        from apps.survey import utils
        total_sent, total_error = utils.flush_response_queue()

        verbosity = int(options.get('verbosity', 1))
        if total_error > 0 or verbosity > 0:
            print "Responses: %d sent, %d error." % (total_sent, total_error)

