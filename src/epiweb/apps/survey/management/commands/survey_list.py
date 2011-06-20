from django.core.management.base import CommandError, BaseCommand

class Command(BaseCommand):
    help = 'Print registered surveys'

    def handle(self, *args, **options):
        from epiweb.apps.survey import models

        surveys = models.Survey.objects.all()
        if len(surveys) > 0:
            print 'Registered surveys:'
            for index, survey in enumerate(surveys):
                print '%3d. %s' % (index+1, survey.survey_id)
        else:
            print 'No survey is registered.'

