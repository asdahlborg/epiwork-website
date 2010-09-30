from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^profile/$', 'epiweb.apps.survey.views.profile_index'),
    (r'^thanks/$', 'epiweb.apps.survey.views.thanks'),
    url(r'^people/$', 'epiweb.apps.survey.views.people', name='survey_people'),
    url(r'^people/add/$', 'epiweb.apps.survey.views.people_add', name='survey_people_add'),
    (r'^$', 'epiweb.apps.survey.views.index'),
)

