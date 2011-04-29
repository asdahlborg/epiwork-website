import os
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
            fname = args[0]
        except IndexError:
            raise CommandError('Please enter specify a survey specification file')

        if not os.path.exists(fname):
            raise CommandError('File not found')

        from epiweb.apps.survey.sql import create_sql_create, create_table_name
        from epiweb.apps.survey.survey import parse_specification, Specification

        content = open(fname).read()
        data = parse_specification(content)
        spec = Specification(data)

        ddl, mapper_data = create_sql_create(spec)

        name = create_table_name(spec.survey.id)

        f = open('%s.sql' % name, 'w')
        f.write(ddl)
        f.close()

        f = open('%s.json' % name, 'w')
        f.write(json.dumps(mapper_data))
        f.close()

        print 'Two files created:'
        print '- SQL create table statements: %s.sql' % name
        print '- SQL data mapping information: %s.json' % name

