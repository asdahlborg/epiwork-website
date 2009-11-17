from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^edit/$', 'epiweb.apps.profile.views.edit'),
    (r'^$', 'epiweb.apps.profile.views.index'),
)

