from django.conf.urls.defaults import *

from . import views

urlpatterns = patterns('',
    url(r'^profile/$', views.profile_index, name='survey_profile'),
    url(r'^thanks/$', views.thanks, name='survey_thanks'),
    url(r'^people/$', views.people, name='survey_people'),
    url(r'^people/add/$', views.people_add, name='survey_people_add'),
    url(r'^people/edit/$', views.people_edit, name='survey_people_edit'),
    url(r'^$', views.index, name='survey_index'),
)

