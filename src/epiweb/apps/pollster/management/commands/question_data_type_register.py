from optparse import make_option
from django.core.management.base import CommandError, BaseCommand

class Command(BaseCommand):
    help = 'Register a question data type.'
    option_list = BaseCommand.option_list + (
        make_option('-t', '--title', action='store', type="string",
                    dest='title',
                    help='Data type title.'),
        make_option('-d', '--dbtype', action='store', type="string",
                    dest='dbtype',
                    help='JavaScript class.'),
    )

    def handle(self, *args, **options):
        from epiweb.apps.pollster import models

        verbosity = int(options.get('verbosity'))

        data = models.QuestionDataType()
        data.title = options.get('title')
        data.db_type = options.get('dbtype', None)
        data.save()

        if verbosity > 0:
            print 'Question data type "%s" registered' % (data,)

