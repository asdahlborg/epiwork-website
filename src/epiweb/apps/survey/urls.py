from django.conf.urls.defaults import *

from . import views

urlpatterns = patterns('',
    (r'^profile/$', views.profile_index),
    (r'^thanks/$', views.thanks),
    url(r'^people/$', views.people, name='survey_people'),
    url(r'^people/add/$', views.people_add, name='survey_people_add'),
    (r'^$', views.index),
)

