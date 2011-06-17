from optparse import make_option
from django.core.management.base import CommandError, BaseCommand

class Command(BaseCommand):
    help = 'Register a virtual option type.'
    option_list = BaseCommand.option_list + (
        make_option('-t', '--title', action='store', type="string",
                    dest='title',
                    help='Rule title.'),
        make_option('-q', '--question-data-type-title', action='store', type="string",
                    dest='question_data_type_title',
                    help='Question data type title'),
        make_option('-p', '--pyclass', action='store', type="string",
                    dest='pyclass',
                    help='Python class.'),
    )

    def handle(self, *args, **options):
        from epiweb.apps.pollster import models

        verbosity = int(options.get('verbosity'))

        question_data_type_title = options.get('question_data_type_title')
        question_data_type = models.QuestionDataType.objects.get(title = question_data_type_title)

        data = models.VirtualOptionDataType()
        data.question_data_type = question_data_type
        data.title = options.get('title')
        data.python_class = options.get('pyclass', None)
        data.save()

        if verbosity > 0:
            print 'Rule type "%s" registered' % (data,)

