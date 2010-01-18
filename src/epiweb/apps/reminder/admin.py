from django.contrib import admin

from epiweb.apps.reminder.models import Reminder

class ReminderAdmin(admin.ModelAdmin):
    list_display = ('user', 'wday', 'active', 
                    'last_reminder', 'next_reminder')

admin.site.register(Reminder, ReminderAdmin)

