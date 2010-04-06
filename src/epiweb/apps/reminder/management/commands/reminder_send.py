from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand):
    help = "Send reminders."

    def handle_noargs(self, **options):
        from epiweb.apps.reminder.send import send_reminder
        succeed, fail = send_reminder()

        if succeed + fail == 0:
            return u'No reminder sent.'
        elif fail == 0:
            return u'%d reminders sent.' % succeed
        else:
            return u'%d reminders sent, %d failed.' % (succeed, fail)

