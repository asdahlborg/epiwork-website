from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'epiweb.apps.profile.views.index'),
)

