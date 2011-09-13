from django.core.management.base import NoArgsCommand

from ...send import send_reminders

class Command(NoArgsCommand):
    help = "Send reminders."

    def handle_noargs(self, **options):
        return u'%d reminders sent.\n' % send_reminders()
