from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^thanks/$', 'epiweb.apps.survey.survey_views.thanks'),
    (r'^$', 'epiweb.apps.survey.survey_views.index'),
)

