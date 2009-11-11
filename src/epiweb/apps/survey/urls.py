from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'epiweb.apps.survey.views.index')
)

