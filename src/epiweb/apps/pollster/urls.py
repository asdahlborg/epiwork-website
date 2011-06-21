from django.conf.urls.defaults import *

from . import views

urlpatterns = patterns('',
    url(r'^urls.js$', views.urls, kwargs={'prefix': 'pollster_'}, name='pollster_urls'),
    url(r'^pollster/$', views.survey_add, name='pollster_survey_add'),
    url(r'^pollster/(?P<id>\d+)/$', views.survey_edit, name='pollster_survey_edit'),
    url(r'^surveys/(?P<id>\d+)/$', views.survey_test, name='pollster_survey_test'),
    url(r'^$', views.survey_list, name='pollster_survey_list'),
)

