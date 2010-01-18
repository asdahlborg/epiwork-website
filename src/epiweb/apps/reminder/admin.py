from django.contrib import admin

from epiweb.apps.reminder.models import Reminder

def make_active(modeladmin, request, queryset):
    queryset.update(active=True)
make_active.short_description = 'Make selected reminders active'

def make_inactive(modeladmin, request, queryset):
    queryset.update(active=False)
make_inactive.short_description = 'Make selected reminders inactive'

class ReminderAdmin(admin.ModelAdmin):
    list_display = ('user', 'wday', 'active', 
                    'last_reminder', 'next_reminder')
    ordering = ('user__username',)
    actions = (make_active, make_inactive,)
    list_editable = ('active',)
    list_filter = ('wday', 'active',)
    search_fields = ('user__username',)

admin.site.register(Reminder, ReminderAdmin)

