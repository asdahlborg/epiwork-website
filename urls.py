from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import redirect_to

from haystack.views import SearchView, search_view_factory
from haystack.forms import SearchForm

from apps.ew_contact_form.forms import ContactForm

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/surveys-editor/', include('apps.pollster.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^surveys/(?P<id>\d+)/$', 'apps.pollster.views.survey_run'),
    (r'^survey/', include('apps.survey.urls')),
    (r'^influenzanet/', 'django.views.generic.simple.direct_to_template', {'template': 'influenzanet.html'}),
    (r'^googlec96088c11ef7e5c4.html$', 'django.views.generic.simple.direct_to_template', {'template': 'googlec96088c11ef7e5c4.html'}),

    url(r'^search/$', search_view_factory(
        view_class=SearchView,
        form_class=SearchForm
    ), name='haystack_search'),

    (r'^test-search/$', 'views.test_search'),
    (r'^accounts/', include('apps.accounts.urls')),
    (r'^nieuws/', include('journal.urls'), {'categories': ('nieuws',),
                                            'template_name': 'news'}),
    url(r'^login/$', redirect_to, {'url': settings.LOGIN_URL}, 
                     name='loginurl-index'),
    (r'^login/', include('loginurl.urls')),
    (r'^count/', include('apps.count.urls')),

    url(r'^contact/$', 'contact_form.views.contact_form', {'form_class': ContactForm}, name='contact_form'),
    url(r'^contact/sent/$', 'django.views.generic.simple.direct_to_template', {'template': 'contact_form/contact_form_sent.html'}, name='contact_form_sent'),

    (r'^colors.css$', 'apps.partnersites.views.colors_css'),
)

if settings.DEBUG:
    urlpatterns = patterns('',
        (r'^404/$', 'django.views.defaults.page_not_found'),
        (r'^500/$', 'views.server_error'),
        (r'^' + settings.MEDIA_URL.lstrip('/'), include('appmedia.urls'), {'show_indexes': True}),
    ) + urlpatterns

# Catchall
urlpatterns += patterns('', url(r'^', include('cms.urls')))

handler500 = 'views.server_error'
