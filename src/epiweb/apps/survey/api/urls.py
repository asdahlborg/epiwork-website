from django.conf.urls.defaults import *
from epiweb.apps.survey.api.handlers import GetUserProfile
from piston.resource import Resource

urlpatterns = patterns('',                                          
   url(r'^GetUserProfile', Resource(GetUserProfile),
       { 'emitter_format': 'json' }),
)                                                                   
