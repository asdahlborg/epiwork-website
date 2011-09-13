from os.path import join

from django.contrib import admin
from django.contrib.sites.models import Site
from django.conf import settings

from .models import SiteSettings
from .forms import SiteSettingsForm

class SiteSettingsInline(admin.StackedInline):
    model = SiteSettings
    form = SiteSettingsForm

current_site_admin = type(admin.site._registry[Site])
class PartnerSiteAdmin(current_site_admin):
    inlines = current_site_admin.inlines + [SiteSettingsInline]

    class Media:
        js = [join(settings.CMS_MEDIA_URL, path) for path in (
            'js/lib/jquery.js',
            'js/lib/jquery.query.js',

        )]

admin.site.unregister(Site)
admin.site.register(Site, PartnerSiteAdmin)

