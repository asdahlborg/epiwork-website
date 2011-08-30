from os.path import join

from django.contrib import admin
from django.contrib.sites.models import Site
from django.conf import settings

from nani.admin import TranslatableAdmin

from .models import UserReminderInfo, ReminderSettings, NewsLetterTemplate, NewsLetter
from .forms import ReminderSettingsForm, NewsLetterTemplateForm, NewsLetterForm

def make_active(modeladmin, request, queryset):
    queryset.update(active=True)
make_active.short_description = 'Make selected reminders active'

def make_inactive(modeladmin, request, queryset):
    queryset.update(active=False)
make_inactive.short_description = 'Make selected reminders inactive'

class UserReminderInfoAdmin(admin.ModelAdmin):
    list_display = ('user', 'active', 'last_reminder',)
    ordering = ('user__username',)
    actions = (make_active, make_inactive,)
    list_editable = ('active',)
    list_filter = ('active',)
    search_fields = ('user__username',)

    def get_actions(self, request):
        actions = super(UserReminderInfoAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

admin.site.register(UserReminderInfo, UserReminderInfoAdmin)

class SiteSettingsInline(admin.StackedInline):
    model = ReminderSettings
    form = ReminderSettingsForm

current_site_admin = type(admin.site._registry[Site])
class ReminderSiteAdmin(current_site_admin):
    inlines = current_site_admin.inlines + [SiteSettingsInline]

admin.site.unregister(Site)
admin.site.register(Site, ReminderSiteAdmin)

class NewsLetterTemplateAdmin(TranslatableAdmin):
    form = NewsLetterTemplateForm

    class Media:
        js = [join(settings.CMS_MEDIA_URL, path) for path in (
            'js/lib/jquery.js',
            'js/lib/jquery.query.js',

        )]

admin.site.register(NewsLetterTemplate, NewsLetterTemplateAdmin)

class NewsLetterAdmin(TranslatableAdmin):
    form = NewsLetterForm
    list_display = ("__unicode__", "date")

    class Media:
        js = [join(settings.CMS_MEDIA_URL, path) for path in (
            'js/lib/jquery.js',
            'js/lib/jquery.query.js',

        )]

admin.site.register(NewsLetter, NewsLetterAdmin)
