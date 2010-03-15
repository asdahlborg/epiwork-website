from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import redirect_to

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # (r'^$', 'django.views.generic.simple.direct_to_template', {'template': 'homepage.html'}),
    (r'^\+media/(?P<path>.*)$', 'django.views.static.serve', 
        {'document_root': settings.MEDIA_ROOT}),
    (r'^\+media-ggm/(?P<path>.*)$', 'django.views.static.serve', 
        {'document_root': settings.MEDIA_ROOT_GGM}),
    # Example:
    # (r'^epiweb/', include('epiweb.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^accounts/', include('epiweb.apps.accounts.urls')),
    (r'^survey/', include('epiweb.apps.survey.urls')),
    (r'^nieuws/', include('journal.urls'), {'categories': ('nieuws',),
                                            'template_name': 'news'}),
    url(r'^login/$', redirect_to, {'url': settings.LOGIN_URL}, 
                     name='loginurl-index'),
    (r'^login/', include('loginurl.urls')),
    url(r'^', include('cms.urls')),
)
