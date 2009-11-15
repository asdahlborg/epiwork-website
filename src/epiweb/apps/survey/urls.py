from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^\+(?P<survey_id>\w+)/(?P<page>(\+final|\d+))/$', 'epiweb.apps.survey.views.survey'),
    (r'^\+(?P<survey_id>\w+)/$', 'epiweb.apps.survey.views.survey'),
    (r'^thanks/$', 'epiweb.apps.survey.views.thanks'),
    (r'^$', 'epiweb.apps.survey.views.index'),
)

