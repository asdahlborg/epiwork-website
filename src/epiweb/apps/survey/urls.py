from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^profile/$', 'epiweb.apps.survey.views.profile_index'),
    (r'^thanks/$', 'epiweb.apps.survey.views.thanks'),
    (r'^$', 'epiweb.apps.survey.views.index'),
)

