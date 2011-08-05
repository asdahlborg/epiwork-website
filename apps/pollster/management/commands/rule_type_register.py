from optparse import make_option
from django.core.management.base import CommandError, BaseCommand

class Command(BaseCommand):
    help = 'Register a rule type.'
    option_list = BaseCommand.option_list + (
        make_option('-t', '--title', action='store', type="string",
                    dest='title',
                    help='Rule title.'),
        make_option('-j', '--jsclass', action='store', type="string",
                    dest='jsclass',
                    help='JavaScript class.'),
    )

    def handle(self, *args, **options):
        from apps.pollster import models

        verbosity = int(options.get('verbosity'))

        rule = models.RuleType()
        rule.title = options.get('title')
        rule.js_class = options.get('jsclass', None)
        rule.save()

        if verbosity > 0:
            print 'Rule type "%s" registered' % (rule,)

