from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import redirect_to

from epiweb.apps.ew_contact_form.forms import ContactForm

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^search/', include('haystack.urls')),
    (r'^accounts/', include('epiweb.apps.accounts.urls')),
    (r'^survey/', include('epiweb.apps.survey.urls')),
    (r'^nieuws/', include('journal.urls'), {'categories': ('nieuws',),
                                            'template_name': 'news'}),
    url(r'^login/$', redirect_to, {'url': settings.LOGIN_URL}, 
                     name='loginurl-index'),
    (r'^login/', include('loginurl.urls')),

    url(r'^contact/$', 'contact_form.views.contact_form', {'form_class': ContactForm}, name='contact_form'),
    url(r'^contact/sent/$', 'django.views.generic.simple.direct_to_template', {'template': 'contact_form/contact_form_sent.html'}, name='contact_form_sent'),
)

if settings.DEBUG:
    urlpatterns = patterns('',
        (r'^404/$', 'django.views.defaults.page_not_found'),
        (r'^500/$', 'epiweb.views.server_error'),
        (r'^' + settings.MEDIA_URL.lstrip('/'), include('appmedia.urls'), {'show_indexes': True}),
    ) + urlpatterns

if settings.MOBILE_INTERFACE_ACTIVE:
  urlpatterns += patterns('', (r'^ema/', include('epiweb.apps.survey.api.urls')))

if settings.EXTRA_SURVEY:
  urlpatterns += patterns('', (r'^extra-survey/',
                               include('epiweb.apps.survey.extra-urls')))

# Catchall
urlpatterns += patterns('', url(r'^', include('cms.urls')))

handler500 = 'epiweb.views.server_error'
