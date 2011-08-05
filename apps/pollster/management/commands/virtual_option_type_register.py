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
        make_option('-j', '--jsclass', action='store', type="string",
                    dest='jsclass',
                    help='JavaScript class.'),
    )

    def handle(self, *args, **options):
        from apps.pollster import models

        verbosity = int(options.get('verbosity'))

        question_data_type_title = options.get('question_data_type_title')
        question_data_type = models.QuestionDataType.objects.get(title = question_data_type_title)

        data = models.VirtualOptionType()
        data.question_data_type = question_data_type
        data.title = options.get('title')
        data.js_class = options.get('jsclass', None)
        data.save()

        if verbosity > 0:
            print 'Rule type "%s" registered' % (data,)
