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
                    help='Database type.'),
        make_option('-j', '--jsclass', action='store', type="string",
                    dest='jsclass',
                    help='JavaScript class.'),
        make_option('-c', '--cssclass', action='store', type="string",
                    dest='cssclass',
                    help='CSS class.'),
    )

    def handle(self, *args, **options):
        from apps.pollster import models

        verbosity = int(options.get('verbosity'))

        data = models.QuestionDataType()
        data.title = options.get('title')
        data.db_type = options.get('dbtype', None)
        data.js_class = options.get('jsclass', None)
        data.css_class = options.get('cssclass', None)
        data.save()

        if verbosity > 0:
            print 'Question data type "%s" registered' % (data,)

