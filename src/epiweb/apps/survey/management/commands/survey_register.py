from optparse import make_option
from django.core.management.base import CommandError, BaseCommand

class Command(BaseCommand):
    help = 'Register a survey specification.'
    args = '<survey_specification_file>'
    option_list = BaseCommand.option_list + (
        make_option('--replace', action='store_true',
                    dest='replace', default=False,
                    help='Replace existing survey.'),
    )

    def handle(self, *args, **options):
        try:
            fname = args[0]
        except ValueError:
            raise CommandError('Please enter survey_specification_file.')

        import codecs
        from epiweb.apps.survey import models, parser

        verbosity = int(options.get('verbosity', 1))
        replace = options.get('replace', False)

        try:
            content = codecs.open(fname, 'r', 'utf-8').read()
        except IOError, e:
            raise CommandError('Error while reading %s: %s' % (fname, e))

        try:
            survey = parser.parse(content)
        except Exception, e:
            raise CommandError('Error while reading survey specification: %s' % e)

        if verbosity > 0:
            print 'survey id: %s' % survey.id

        items = models.Survey.objects.filter(survey_id=survey.id)
        if len(items) > 0:
            if replace:
                data = items[0]
            else:
                raise CommandError('Duplicate survey_id: %s' % survey.id)
        else:
            data = models.Survey()

        data.survey_id = survey.id
        data.specification = content
        data.save()

        if verbosity > 0:
            print 'A new survey specification registered.'

