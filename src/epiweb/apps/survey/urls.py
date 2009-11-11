from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^\+(?P<survey_id>\w+)/(?P<page>(\+final|\d+))/$', 'epiweb.apps.survey.views.survey'),
    (r'^\+(?P<survey_id>\w+)/$', 'epiweb.apps.survey.views.survey'),
    (r'^$', 'epiweb.apps.survey.views.index'),
)

