from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'epiweb.apps.survey.profile_views.index'),
)

