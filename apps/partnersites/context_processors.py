from django.contrib.sites.models import Site

from .models import SiteSettings

def customizations(request):
    site = Site.objects.get_current()
    settings = SiteSettings.get(site)

    return {
        'site_name': site.name,
        'site_logo': settings.logo.url if settings.logo else "",
    }
