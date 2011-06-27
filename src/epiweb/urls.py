from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import redirect_to

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^accounts/', include('epiweb.apps.accounts.urls')),
    (r'^survey/', include('epiweb.apps.survey.urls')),
    (r'^nieuws/', include('journal.urls'), {'categories': ('nieuws',),
                                            'template_name': 'news'}),
    url(r'^login/$', redirect_to, {'url': settings.LOGIN_URL}, 
                     name='loginurl-index'),
    (r'^login/', include('loginurl.urls')),
    (r'^contact/', include('contact_form.urls')),
)

if settings.DEBUG:
    urlpatterns = patterns('',
        (r'^' + settings.MEDIA_URL.lstrip('/'), include('appmedia.urls'), {'show_indexes': True}),
    ) + urlpatterns

if settings.MOBILE_INTERFACE_ACTIVE:
  urlpatterns += patterns('', (r'^ema/', include('epiweb.apps.survey.api.urls')))

if settings.EXTRA_SURVEY:
  urlpatterns += patterns('', (r'^extra-survey/',
                               include('epiweb.apps.survey.extra-urls')))

# Catchall
urlpatterns += patterns('', url(r'^', include('cms.urls')))

