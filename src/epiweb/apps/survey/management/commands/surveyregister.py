from optparse import make_option
from django.core.management.base import CommandError, BaseCommand

class Command(BaseCommand):
    help = 'Register a survey specification.'
    args = '<survey_id> <survey_specification_file>'
    option_list = BaseCommand.option_list + (
        make_option('--replace', action='store_true',
                    dest='replace', default=False,
                    help='Replace existing survey.'),
    )

    def handle(self, *args, **options):
        try:
            survey_id, fname = args
        except ValueError:
            raise CommandError('Please enter survey_id and survey_specification_file.')

        from epiweb.apps.survey import models
        verbosity = int(options.get('verbosity', 1))
        replace = options.get('replace', False)

        try:
            content = open(fname).read()
        except IOError:
            raise CommandError('Error while reading %s' % fname)

        items = models.Survey.objects.filter(survey_id=survey_id)
        if len(items) > 0:
            if replace:
                for item in items:
                    item.delete()
            else:
                raise CommandError('Duplicate survey_id: %s' % survey_id)

        survey = models.Survey()
        survey.survey_id = survey_id
        survey.specification = content
        survey.save()

        if verbosity > 0:
            print "A new survey specification registered: %s" % survey_id

