try:
    import simplejson as json
except ImportError:
    import json

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
        from epiweb.apps.survey.sql import create_sql_create, create_table_name

        try:
            survey = Survey.objects.get(survey_id=survey_id)
        except Survey.DoesNotExist:
            raise CommandError('Invalid survey_id: %s' % survey_id)

        name = create_table_name(survey_id)

        ddl, mapper_data = create_sql_create(survey)

        f = open('%s.sql' % name, 'w')
        f.write(ddl)
        f.close()

        f = open('%s.json' % name, 'w')
        f.write(json.dumps(mapper_data))
        f.close()

        print 'Two files created:'
        print '- SQL create table statements: %s.sql' % name
        print '- SQL data mapping information: %s.json' % name

