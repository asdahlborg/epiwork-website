from optparse import make_option
from django.core.management.base import CommandError, BaseCommand

class Command(BaseCommand):
    help = 'Prints the CREATE TABLE SQL statements for the given survey id'
    args = '<survey_id>'

    def handle(self, *args, **options):
        try:
            survey_id = args[0]
        except ValueError:
            raise CommandError('Please enter a survey_id')

        from epiweb.apps.survey.models import Survey
        from epiweb.apps.survey.sql import create_ddl

        try:
            survey = Survey.objects.get(survey_id=survey_id)
        except Survey.DoesNotExist:
            raise CommandError('Invalid survey_id: %s' % survey_id)

        ddl = create_ddl(survey)
        print ddl

