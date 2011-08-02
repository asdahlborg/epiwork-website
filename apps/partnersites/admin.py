from django.contrib import admin
from django.contrib.sites.admin import SiteAdmin
from django.contrib.sites.models import Site

from .models import SiteSettings
from .forms import SiteSettingsForm

class SiteSettingsInline(admin.StackedInline):
    model = SiteSettings
    form = SiteSettingsForm

class ExtendedSiteAdmin(SiteAdmin):
    inlines = [SiteSettingsInline]

admin.site.unregister(Site)
admin.site.register(Site, ExtendedSiteAdmin)

