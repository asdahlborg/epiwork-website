from django.contrib.sites.models import Site
from django.shortcuts import render_to_response

from .models import SiteSettings

def colors_css(request):
    site = Site.objects.get_current()
    settings = SiteSettings.get(site=site)
    return render_to_response('colors.css', locals(), mimetype='text/css')
    
