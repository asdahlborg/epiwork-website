from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^thanks/$', 'epiweb.apps.survey.views.thanks'),
    (r'^$', 'epiweb.apps.survey.views.index'),
)

