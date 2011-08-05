from django.conf.urls.defaults import *

from . import views

urlpatterns = patterns('',
    url(r'^urls.js$', views.urls, kwargs={'prefix': 'pollster_'}, name='pollster_urls'),
    url(r'^pollster/$', views.survey_add, name='pollster_survey_add'),
    url(r'^pollster/(?P<id>\d+)/$', views.survey_edit, name='pollster_survey_edit'),
    url(r'^pollster/(?P<id>\d+)/export$', views.survey_export, name='pollster_survey_export'),
    url(r'^pollster/(?P<id>\d+)/publish$', views.survey_publish, name='pollster_survey_publish'),
    url(r'^pollster/(?P<id>\d+)/unpublish$', views.survey_unpublish, name='pollster_survey_unpublish'),
    url(r'^pollster/(?P<id>\d+)/translations$', views.survey_translation_list_or_add, name='pollster_survey_translation_list'),
    url(r'^pollster/(?P<id>\d+)/translations$', views.survey_translation_list_or_add, name='pollster_survey_translation_add'),
    url(r'^pollster/(?P<id>\d+)/translations/(?P<language>.+)$', views.survey_translation_edit, name='pollster_survey_translation_edit'),
    url(r'^surveys/(?P<id>\d+)/$', views.survey_test, name='pollster_survey_test'),
    url(r'^surveys/(?P<id>\d+)/(?P<language>.+)/$', views.survey_test, name='pollster_survey_test'),
    url(r'^$', views.survey_list, name='pollster_survey_list'),
)

