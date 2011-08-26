from os.path import join

from django.contrib import admin
from django.contrib.sites.admin import SiteAdmin
from django.contrib.sites.models import Site
from django.conf import settings

from .models import SiteSettings
from .forms import SiteSettingsForm

class SiteSettingsInline(admin.StackedInline):
    model = SiteSettings
    form = SiteSettingsForm

class ExtendedSiteAdmin(SiteAdmin):
    inlines = [SiteSettingsInline]

    class Media:
        js = [join(settings.CMS_MEDIA_URL, path) for path in (
            'js/lib/jquery.js',
            'js/lib/jquery.query.js',

        )]

admin.site.unregister(Site)
admin.site.register(Site, ExtendedSiteAdmin)

